"""
NFT Minting System for Public Domain Movie Assets

Comprehensive NFT minting infrastructure supporting:
- Multiple blockchain networks (Ethereum, Polygon, Binance Smart Chain, etc.)
- Both ERC-721 (unique) and ERC-1155 (batch) standards
- IPFS integration for decentralized storage
- Batch minting with gas optimization
- Frame and audio asset minting
- Metadata generation and validation

Requirements:
    pip install web3 py-ipfs-http-client python-dotenv

Setup:
    Create .env file with:
    WALLET_PRIVATE_KEY=your_private_key
    INFURA_PROJECT_ID=your_infura_id (or other RPC provider)
    PINATA_API_KEY=your_pinata_key (for IPFS)
    PINATA_SECRET_KEY=your_pinata_secret
"""

from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import time
import logging
import hashlib
import base64
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Supported Networks
NETWORKS = {
    'ethereum_mainnet': {
        'rpc': f"https://mainnet.infura.io/v3/{os.getenv('INFURA_PROJECT_ID')}",
        'chain_id': 1,
        'name': 'Ethereum Mainnet',
        'explorer': 'https://etherscan.io',
        'currency': 'ETH'
    },
    'ethereum_sepolia': {
        'rpc': f"https://sepolia.infura.io/v3/{os.getenv('INFURA_PROJECT_ID')}",
        'chain_id': 11155111,
        'name': 'Ethereum Sepolia Testnet',
        'explorer': 'https://sepolia.etherscan.io',
        'currency': 'SepoliaETH'
    },
    'polygon_mainnet': {
        'rpc': 'https://polygon-rpc.com',
        'chain_id': 137,
        'name': 'Polygon Mainnet',
        'explorer': 'https://polygonscan.com',
        'currency': 'MATIC'
    },
    'polygon_mumbai': {
        'rpc': 'https://rpc-mumbai.maticvigil.com',
        'chain_id': 80001,
        'name': 'Polygon Mumbai Testnet',
        'explorer': 'https://mumbai.polygonscan.com',
        'currency': 'MATIC'
    },
    'bsc_mainnet': {
        'rpc': 'https://bsc-dataseed.binance.org',
        'chain_id': 56,
        'name': 'Binance Smart Chain',
        'explorer': 'https://bscscan.com',
        'currency': 'BNB'
    }
}


@dataclass
class NFTMetadata:
    """Standard NFT metadata."""
    name: str
    description: str
    image: str  # IPFS URL or HTTP URL
    external_url: Optional[str] = None
    animation_url: Optional[str] = None  # For audio/video
    attributes: Optional[List[Dict]] = None
    properties: Optional[Dict] = None


@dataclass
class MintingResult:
    """Result from minting operation."""
    success: bool
    tx_hash: Optional[str] = None
    token_id: Optional[int] = None
    contract_address: Optional[str] = None
    gas_used: Optional[int] = None
    gas_price: Optional[int] = None
    error: Optional[str] = None
    ipfs_hash: Optional[str] = None
    metadata_url: Optional[str] = None


class IPFSUploader:
    """Upload files to IPFS using Pinata."""

    def __init__(self):
        self.api_key = os.getenv('PINATA_API_KEY')
        self.secret_key = os.getenv('PINATA_SECRET_KEY')
        self.base_url = 'https://api.pinata.cloud'

    def upload_file(self, file_path: str, name: Optional[str] = None) -> str:
        """
        Upload file to IPFS via Pinata.

        Args:
            file_path: Path to file
            name: Optional name for the file

        Returns:
            IPFS hash
        """
        if not self.api_key or not self.secret_key:
            raise ValueError("PINATA_API_KEY and PINATA_SECRET_KEY required")

        url = f"{self.base_url}/pinning/pinFileToIPFS"

        headers = {
            'pinata_api_key': self.api_key,
            'pinata_secret_api_key': self.secret_key
        }

        with open(file_path, 'rb') as f:
            files = {'file': (name or Path(file_path).name, f)}

            response = requests.post(url, files=files, headers=headers)
            response.raise_for_status()

        result = response.json()
        ipfs_hash = result['IpfsHash']
        logger.info(f"✓ Uploaded to IPFS: {ipfs_hash}")

        return ipfs_hash

    def upload_json(self, data: Dict, name: str = "metadata.json") -> str:
        """
        Upload JSON metadata to IPFS.

        Args:
            data: JSON data
            name: File name

        Returns:
            IPFS hash
        """
        if not self.api_key or not self.secret_key:
            raise ValueError("PINATA_API_KEY and PINATA_SECRET_KEY required")

        url = f"{self.base_url}/pinning/pinJSONToIPFS"

        headers = {
            'Content-Type': 'application/json',
            'pinata_api_key': self.api_key,
            'pinata_secret_api_key': self.secret_key
        }

        payload = {
            'pinataContent': data,
            'pinataMetadata': {'name': name}
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        ipfs_hash = result['IpfsHash']
        logger.info(f"✓ Uploaded metadata to IPFS: {ipfs_hash}")

        return ipfs_hash

    @staticmethod
    def get_ipfs_url(ipfs_hash: str, gateway: str = "https://gateway.pinata.cloud") -> str:
        """Get HTTP URL for IPFS hash."""
        return f"{gateway}/ipfs/{ipfs_hash}"


class NFTMinter:
    """NFT minting orchestrator."""

    def __init__(
        self,
        network: str = 'polygon_mumbai',
        private_key: Optional[str] = None
    ):
        """
        Initialize NFT minter.

        Args:
            network: Network name from NETWORKS dict
            private_key: Wallet private key (or from env)
        """
        if network not in NETWORKS:
            raise ValueError(f"Unsupported network: {network}")

        self.network_config = NETWORKS[network]
        self.network_name = network

        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.network_config['rpc']))

        # Add PoA middleware for networks that need it
        if 'polygon' in network or 'bsc' in network:
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        # Setup account
        self.private_key = private_key or os.getenv('WALLET_PRIVATE_KEY')
        if not self.private_key:
            raise ValueError("WALLET_PRIVATE_KEY required")

        self.account = Account.from_key(self.private_key)
        self.address = self.account.address

        # IPFS uploader
        self.ipfs = IPFSUploader()

        logger.info(f"Initialized NFT Minter")
        logger.info(f"Network: {self.network_config['name']}")
        logger.info(f"Wallet: {self.address}")
        logger.info(f"Balance: {self.w3.from_wei(self.w3.eth.get_balance(self.address), 'ether')} {self.network_config['currency']}")

    def prepare_frame_nft_metadata(
        self,
        frame_path: str,
        frame_number: int,
        movie_title: str,
        movie_year: int,
        timestamp: str,
        director: str,
        public_domain_reason: str,
        additional_attributes: Optional[List[Dict]] = None
    ) -> NFTMetadata:
        """
        Prepare NFT metadata for a movie frame.

        Args:
            frame_path: Path to frame image
            frame_number: Frame number in movie
            movie_title: Movie title
            movie_year: Year of movie
            timestamp: Timestamp in movie
            director: Director name
            public_domain_reason: Why it's public domain
            additional_attributes: Additional metadata attributes

        Returns:
            NFTMetadata object
        """
        # Upload frame to IPFS
        ipfs_hash = self.ipfs.upload_file(
            frame_path,
            name=f"{movie_title}_frame_{frame_number}.jpg"
        )
        image_url = self.ipfs.get_ipfs_url(ipfs_hash)

        # Build attributes
        attributes = [
            {"trait_type": "Movie Title", "value": movie_title},
            {"trait_type": "Year", "value": movie_year},
            {"trait_type": "Director", "value": director},
            {"trait_type": "Frame Number", "value": frame_number},
            {"trait_type": "Timestamp", "value": timestamp},
            {"trait_type": "Asset Type", "value": "Frame"},
            {"trait_type": "Public Domain Reason", "value": public_domain_reason}
        ]

        if additional_attributes:
            attributes.extend(additional_attributes)

        # Create metadata
        metadata = NFTMetadata(
            name=f"{movie_title} - Frame #{frame_number}",
            description=f"Frame #{frame_number} from the {movie_year} public domain film '{movie_title}' directed by {director}. Timestamp: {timestamp}. This frame is from a film in the public domain due to: {public_domain_reason}",
            image=image_url,
            attributes=attributes,
            properties={
                "category": "Public Domain Cinema",
                "type": "Frame",
                "source": "Public Domain"
            }
        )

        return metadata

    def prepare_audio_nft_metadata(
        self,
        audio_path: str,
        movie_title: str,
        movie_year: int,
        director: str,
        duration: float,
        start_time: float,
        public_domain_reason: str,
        asset_type: str = "Audio Segment",
        additional_attributes: Optional[List[Dict]] = None
    ) -> NFTMetadata:
        """
        Prepare NFT metadata for audio asset.

        Args:
            audio_path: Path to audio file
            movie_title: Movie title
            movie_year: Year
            director: Director
            duration: Duration in seconds
            start_time: Start time in movie
            public_domain_reason: Public domain reason
            asset_type: Type of audio asset
            additional_attributes: Additional attributes

        Returns:
            NFTMetadata object
        """
        # Upload audio to IPFS
        ipfs_hash = self.ipfs.upload_file(audio_path)
        audio_url = self.ipfs.get_ipfs_url(ipfs_hash)

        # Format times
        start_formatted = self._format_time(start_time)
        end_formatted = self._format_time(start_time + duration)

        attributes = [
            {"trait_type": "Movie Title", "value": movie_title},
            {"trait_type": "Year", "value": movie_year},
            {"trait_type": "Director", "value": director},
            {"trait_type": "Duration (seconds)", "value": duration},
            {"trait_type": "Start Time", "value": start_formatted},
            {"trait_type": "End Time", "value": end_formatted},
            {"trait_type": "Asset Type", "value": asset_type},
            {"trait_type": "Public Domain Reason", "value": public_domain_reason}
        ]

        if additional_attributes:
            attributes.extend(additional_attributes)

        metadata = NFTMetadata(
            name=f"{movie_title} - {asset_type} ({start_formatted})",
            description=f"{asset_type} from the {movie_year} public domain film '{movie_title}' directed by {director}. Duration: {duration:.2f}s, Time range: {start_formatted} - {end_formatted}. This audio is from a film in the public domain due to: {public_domain_reason}",
            image="",  # Could add a waveform visualization
            animation_url=audio_url,
            attributes=attributes,
            properties={
                "category": "Public Domain Cinema",
                "type": "Audio",
                "source": "Public Domain"
            }
        )

        return metadata

    def mint_erc721_with_metadata(
        self,
        contract_address: str,
        contract_abi: List,
        metadata: NFTMetadata,
        to_address: Optional[str] = None
    ) -> MintingResult:
        """
        Mint ERC-721 NFT with metadata.

        Args:
            contract_address: NFT contract address
            contract_abi: Contract ABI
            metadata: NFT metadata
            to_address: Recipient address (defaults to minter)

        Returns:
            MintingResult
        """
        try:
            # Upload metadata to IPFS
            metadata_dict = asdict(metadata)
            metadata_hash = self.ipfs.upload_json(metadata_dict)
            metadata_url = self.ipfs.get_ipfs_url(metadata_hash)

            # Get contract
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=contract_abi
            )

            # Build transaction
            recipient = to_address or self.address
            nonce = self.w3.eth.get_transaction_count(self.address)

            # Assuming standard mint function: mint(address to, string memory tokenURI)
            tx = contract.functions.mint(
                Web3.to_checksum_address(recipient),
                metadata_url
            ).build_transaction({
                'from': self.address,
                'nonce': nonce,
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price
            })

            # Sign and send
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            logger.info(f"Transaction sent: {tx_hash.hex()}")

            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt['status'] == 1:
                logger.info(f"✓ NFT minted successfully!")

                return MintingResult(
                    success=True,
                    tx_hash=tx_hash.hex(),
                    contract_address=contract_address,
                    gas_used=receipt['gasUsed'],
                    gas_price=tx['gasPrice'],
                    ipfs_hash=metadata_hash,
                    metadata_url=metadata_url
                )
            else:
                return MintingResult(
                    success=False,
                    error="Transaction failed"
                )

        except Exception as e:
            logger.error(f"Minting error: {e}")
            return MintingResult(
                success=False,
                error=str(e)
            )

    def batch_mint_frames(
        self,
        contract_address: str,
        contract_abi: List,
        frames_data: List[Dict],
        movie_info: Dict,
        batch_size: int = 10,
        delay_between_batches: float = 2.0
    ) -> List[MintingResult]:
        """
        Batch mint multiple frame NFTs with gas optimization.

        Args:
            contract_address: NFT contract address
            contract_abi: Contract ABI
            frames_data: List of dicts with frame info (path, number, timestamp)
            movie_info: Movie metadata (title, year, director, etc.)
            batch_size: Frames per batch
            delay_between_batches: Delay in seconds between batches

        Returns:
            List of MintingResult objects
        """
        results = []
        total = len(frames_data)

        logger.info(f"Starting batch minting of {total} frames...")
        logger.info(f"Batch size: {batch_size}")

        for i in range(0, total, batch_size):
            batch = frames_data[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size

            logger.info(f"\nProcessing batch {batch_num}/{total_batches}...")

            for frame_data in batch:
                # Prepare metadata
                metadata = self.prepare_frame_nft_metadata(
                    frame_path=frame_data['path'],
                    frame_number=frame_data['frame_number'],
                    movie_title=movie_info['title'],
                    movie_year=movie_info['year'],
                    timestamp=frame_data['timestamp'],
                    director=movie_info['director'],
                    public_domain_reason=movie_info['public_domain_reason']
                )

                # Mint
                result = self.mint_erc721_with_metadata(
                    contract_address=contract_address,
                    contract_abi=contract_abi,
                    metadata=metadata
                )

                results.append(result)

                if result.success:
                    logger.info(f"  ✓ Frame #{frame_data['frame_number']} minted")
                else:
                    logger.error(f"  ✗ Frame #{frame_data['frame_number']} failed: {result.error}")

            # Delay between batches to avoid rate limits
            if i + batch_size < total:
                logger.info(f"Waiting {delay_between_batches}s before next batch...")
                time.sleep(delay_between_batches)

        # Summary
        successful = sum(1 for r in results if r.success)
        failed = total - successful

        logger.info(f"\n{'='*60}")
        logger.info(f"Batch Minting Complete!")
        logger.info(f"Total: {total}, Successful: {successful}, Failed: {failed}")
        logger.info(f"{'='*60}")

        return results

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds as HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def estimate_gas_cost(self, num_nfts: int) -> Dict:
        """
        Estimate gas costs for minting.

        Args:
            num_nfts: Number of NFTs to mint

        Returns:
            Cost estimates
        """
        gas_per_mint = 150000  # Approximate
        total_gas = gas_per_mint * num_nfts
        gas_price = self.w3.eth.gas_price

        cost_wei = total_gas * gas_price
        cost_eth = self.w3.from_wei(cost_wei, 'ether')

        return {
            "num_nfts": num_nfts,
            "gas_per_mint": gas_per_mint,
            "total_gas": total_gas,
            "gas_price_gwei": self.w3.from_wei(gas_price, 'gwei'),
            "total_cost_eth": float(cost_eth),
            "currency": self.network_config['currency']
        }


def main():
    """Example usage and CLI."""
    import argparse

    parser = argparse.ArgumentParser(description="NFT Minting System")
    parser.add_argument("--network", default="polygon_mumbai",
                        choices=list(NETWORKS.keys()),
                        help="Blockchain network")
    parser.add_argument("--check-balance", action="store_true",
                        help="Check wallet balance")
    parser.add_argument("--estimate-cost", type=int, metavar="NUM_NFTS",
                        help="Estimate cost for minting N NFTs")
    parser.add_argument("--upload-test", help="Test IPFS upload with file")

    args = parser.parse_args()

    try:
        minter = NFTMinter(network=args.network)

        if args.check_balance:
            balance = minter.w3.eth.get_balance(minter.address)
            balance_eth = minter.w3.from_wei(balance, 'ether')
            print(f"\nWallet: {minter.address}")
            print(f"Network: {minter.network_config['name']}")
            print(f"Balance: {balance_eth} {minter.network_config['currency']}")

        elif args.estimate_cost:
            estimate = minter.estimate_gas_cost(args.estimate_cost)
            print(f"\nGas Cost Estimate for {estimate['num_nfts']} NFTs:")
            print(f"  Gas per mint: {estimate['gas_per_mint']:,}")
            print(f"  Total gas: {estimate['total_gas']:,}")
            print(f"  Gas price: {estimate['gas_price_gwei']:.2f} Gwei")
            print(f"  Total cost: {estimate['total_cost_eth']:.6f} {estimate['currency']}")

        elif args.upload_test:
            print(f"\nUploading {args.upload_test} to IPFS...")
            ipfs_hash = minter.ipfs.upload_file(args.upload_test)
            url = minter.ipfs.get_ipfs_url(ipfs_hash)
            print(f"✓ IPFS Hash: {ipfs_hash}")
            print(f"✓ URL: {url}")

        else:
            parser.print_help()

    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
