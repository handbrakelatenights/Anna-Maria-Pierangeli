# Complete NFT Minting Guide for Public Domain Movies

## Overview

This system processes **EVERY FRAME** and **EVERY AUDIO ASSET** from public domain movies and mints them as NFTs on the blockchain. It's a complete, automated pipeline that handles:

- **Frame Extraction**: Extract all frames from a video (100,000+ for a feature film)
- **Audio Extraction**: Extract full audio track + time-based segments
- **IPFS Upload**: Decentralized storage for all assets
- **NFT Minting**: Mint an NFT for every single asset
- **Batch Processing**: Gas-optimized batch minting
- **Multi-chain Support**: Ethereum, Polygon, BSC, and testnets

## Why Mint Every Frame?

Each frame of a public domain movie is unique content that can be:
- **Collected**: Build complete sets of iconic films
- **Traded**: Each frame has its own rarity and value
- **Displayed**: Digital art galleries and NFT platforms
- **Archived**: Blockchain-verified film preservation
- **Analyzed**: Frame-by-frame ownership and provenance

## System Architecture

```
Video File
    │
    ├──> Frame Extractor ──> IPFS ──> NFT Minter ──> Blockchain
    │        (Every frame)
    │
    └──> Audio Extractor ──> IPFS ──> NFT Minter ──> Blockchain
             (Full + segments)
```

## Prerequisites

### 1. Software Requirements

```bash
# Python 3.8+
python --version

# FFmpeg (for audio extraction)
ffmpeg -version

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 2. Blockchain Setup

You need:
- **Wallet with private key**
- **RPC endpoint** (Infura, Alchemy, or public RPC)
- **Native tokens** for gas (ETH, MATIC, BNB)
- **NFT Smart Contract** (ERC-721 or ERC-1155)

### 3. IPFS Setup

For decentralized storage:
- **Pinata Account** (https://pinata.cloud) - Free tier available
- API Key and Secret Key

### 4. Environment Configuration

Create `.env` file:

```bash
# Wallet
WALLET_PRIVATE_KEY=your_private_key_here

# RPC Endpoints
INFURA_PROJECT_ID=your_infura_project_id

# IPFS (Pinata)
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_KEY=your_pinata_secret_key

# Database (optional)
MONGO_URL=mongodb://localhost:27017
DB_NAME=newsdb
```

**SECURITY**: Never commit `.env` file to git!

## Smart Contract Requirements

Your NFT contract must support:

### ERC-721 Standard

```solidity
function mint(address to, string memory tokenURI) public returns (uint256);
```

### Example Contract

Use OpenZeppelin's ERC-721URIStorage:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract PublicDomainMovieNFT is ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    constructor() ERC721("Public Domain Movie Frames", "PDMF") {}

    function mint(address to, string memory tokenURI)
        public
        onlyOwner
        returns (uint256)
    {
        _tokenIds.increment();
        uint256 newTokenId = _tokenIds.current();
        _mint(to, newTokenId);
        _setTokenURI(newTokenId, tokenURI);
        return newTokenId;
    }
}
```

Deploy this to your chosen network and note the contract address.

## Usage

### Complete Pipeline (Everything)

Process a movie, extract EVERY frame and audio, and mint ALL NFTs:

```bash
python complete_nft_pipeline.py \
  --video path/to/night_of_living_dead.mp4 \
  --movie "Night of the Living Dead" \
  --year 1968 \
  --director "George A. Romero" \
  --reason "Copyright notice omission" \
  --contract 0xYourContractAddress \
  --abi-file contract_abi.json \
  --network polygon_mumbai
```

**Warning**: This will mint **100,000+** NFTs for a feature film! Make sure you have enough gas.

### Step-by-Step Process

#### Step 1: Extract Assets Only (No Minting)

Test extraction first:

```bash
python complete_nft_pipeline.py \
  --video movie.mp4 \
  --movie "Movie Title" \
  --year 1968 \
  --director "Director" \
  --contract 0x... \
  --abi-file abi.json \
  --no-mint
```

This will:
- Extract all frames
- Extract all audio
- Calculate gas estimates
- **NOT** mint any NFTs

Check the output in `nft_pipeline_output/`:
- `frames/` - All extracted frames
- `audio/` - All audio assets
- `reports/` - Extraction statistics

#### Step 2: Frames Only (Skip Audio)

Mint only frame NFTs:

```bash
python complete_nft_pipeline.py \
  --video movie.mp4 \
  --movie "Movie Title" \
  --year 1968 \
  --director "Director" \
  --contract 0x... \
  --abi-file abi.json \
  --frames-only
```

#### Step 3: Check Costs

Before minting, the system will show:

```
COST ESTIMATE
------------------------------------------------------------
Frame NFTs: 129,600
Audio NFTs: 241
Total NFTs: 129,841
Gas per NFT: ~150,000
Total gas: ~19,476,150,000
Gas price: 30.00 Gwei
Estimated cost: 0.584285 MATIC
------------------------------------------------------------

This will mint 129841 NFTs.
Continue? (yes/no):
```

### Individual Components

#### Extract Frames Only

```bash
python movie_frame_extractor.py movie.mp4 \
  --title "Movie Title" \
  --mode all \
  --format jpg \
  --quality 95
```

#### Extract Audio Only

```bash
# Full audio track
python audio_extractor.py movie.mp4 \
  --title "Movie Title" \
  --mode full \
  --format mp3

# Audio segments (30s each)
python audio_extractor.py movie.mp4 \
  --title "Movie Title" \
  --mode segments \
  --segment-duration 30
```

#### Manual NFT Minting

```bash
# Check balance
python nft_minting_system.py --network polygon_mumbai --check-balance

# Estimate costs
python nft_minting_system.py --network polygon_mumbai --estimate-cost 100000

# Test IPFS upload
python nft_minting_system.py --upload-test frame_00000000.jpg
```

## Supported Networks

### Testnets (Recommended for Testing)

| Network | Chain ID | Currency | Free Faucet |
|---------|----------|----------|-------------|
| Polygon Mumbai | 80001 | MATIC | https://faucet.polygon.technology/ |
| Ethereum Sepolia | 11155111 | SepoliaETH | https://sepoliafaucet.com/ |

### Mainnets (Production)

| Network | Chain ID | Currency | Gas Cost (typical) |
|---------|----------|----------|-------------------|
| Polygon | 137 | MATIC | ~$0.001 per NFT |
| Ethereum | 1 | ETH | ~$5-50 per NFT |
| BSC | 56 | BNB | ~$0.10 per NFT |

**Recommendation**: Use Polygon Mainnet for cost-effective minting.

## Gas Optimization

### Batch Minting

The system automatically batches minting to optimize gas:

```python
config = PipelineConfig(
    ...
    batch_size=10,           # Mint 10 NFTs per batch
    delay_between_batches=3.0  # Wait 3 seconds between batches
)
```

### Cost Calculations

For a 90-minute movie at 24fps:

```
Total frames: 90 × 60 × 24 = 129,600 frames
Gas per mint: ~150,000 gas
Total gas: 19,440,000,000 gas

On Polygon (30 Gwei gas price):
Cost = 19,440,000,000 × 30 / 1e9 = 583.2 MATIC
At $0.80/MATIC = $466.56

On Ethereum (30 Gwei):
Cost = 0.5832 ETH
At $2,000/ETH = $1,166.40
```

### Reducing Costs

**Option 1: Sample Frames**
Instead of every frame, mint 1000 representative frames:

```bash
python movie_frame_extractor.py movie.mp4 \
  --title "Movie" \
  --mode sample \
  --samples 1000
```

Cost: ~$3.60 on Polygon, $9 on Ethereum

**Option 2: ERC-1155 Batch Minting**
Use ERC-1155 for true batch minting (requires different contract).

**Option 3: Layer 2 Solutions**
Use Arbitrum, Optimism, or zkSync for even cheaper minting.

## NFT Metadata Format

Each NFT includes comprehensive metadata:

```json
{
  "name": "Night of the Living Dead - Frame #12450",
  "description": "Frame #12450 from the 1968 public domain film...",
  "image": "ipfs://QmXxx.../frame_12450.jpg",
  "external_url": "https://wikipedia.org/wiki/Night_of_the_Living_Dead",
  "attributes": [
    {"trait_type": "Movie Title", "value": "Night of the Living Dead"},
    {"trait_type": "Year", "value": 1968},
    {"trait_type": "Director", "value": "George A. Romero"},
    {"trait_type": "Frame Number", "value": 12450},
    {"trait_type": "Timestamp", "value": "00:08:37.500"},
    {"trait_type": "Asset Type", "value": "Frame"},
    {"trait_type": "Public Domain Reason", "value": "Copyright notice omission"}
  ],
  "properties": {
    "category": "Public Domain Cinema",
    "type": "Frame",
    "source": "Public Domain"
  }
}
```

## Output Structure

After running the pipeline:

```
nft_pipeline_output/
├── frames/
│   └── Night_of_the_Living_Dead/
│       ├── frame_00000000.jpg
│       ├── frame_00000001.jpg
│       ├── ...
│       ├── frame_00129599.jpg
│       ├── metadata.json
│       └── summary.txt
│
├── audio/
│   └── Night_of_the_Living_Dead/
│       ├── full_audio.mp3
│       ├── segment_00000.mp3
│       ├── segment_00001.mp3
│       └── ...
│
└── reports/
    ├── final_report.json
    ├── summary.txt
    ├── frames_minting_report.json
    └── audio_minting_report.json
```

### Reports

**final_report.json**: Complete pipeline statistics
**summary.txt**: Human-readable summary
**frames_minting_report.json**: All frame minting transactions
**audio_minting_report.json**: All audio minting transactions

## Real-World Example

### Processing "Night of the Living Dead"

```bash
# 1. Download from Internet Archive
wget "https://archive.org/download/night_of_the_living_dead/night_of_the_living_dead_512kb.mp4"

# 2. Deploy NFT contract to Polygon Mumbai
# (Use Remix IDE or Hardhat)
# Contract address: 0x1234...

# 3. Get Mumbai MATIC from faucet
# Visit: https://faucet.polygon.technology/

# 4. Run complete pipeline
python complete_nft_pipeline.py \
  --video night_of_the_living_dead_512kb.mp4 \
  --movie "Night of the Living Dead" \
  --year 1968 \
  --director "George A. Romero" \
  --reason "Copyright notice omission" \
  --contract 0x1234567890abcdef... \
  --abi-file NotLD_ABI.json \
  --network polygon_mumbai

# Expected output:
# - 129,600 frame NFTs
# - 241 audio segment NFTs (30s each)
# - Total: 129,841 NFTs
# - Time: ~24-48 hours (with delays)
# - Cost: ~600 MATIC (testnet is free!)
```

## Monitoring

### Check Progress

The pipeline provides real-time updates:

```
[STEP 1/5] Extracting frames...
Total frames to extract: 129,600
Estimated time: 129.6 minutes (at 1000 frames/min)
Progress: 1,000/129,600 frames (0.8%)
Progress: 2,000/129,600 frames (1.5%)
...

[STEP 4/5] Minting 129,600 frame NFTs...
Processing batch 1/12960...
  ✓ Frame #0 minted
  ✓ Frame #1 minted
...
```

### View on Blockchain

After minting, view your NFTs:

- **Polygon Mumbai**: https://mumbai.polygonscan.com/address/YOUR_CONTRACT
- **OpenSea Testnet**: https://testnets.opensea.io/collection/YOUR_COLLECTION
- **Polygon Mainnet**: https://polygonscan.com/address/YOUR_CONTRACT
- **OpenSea**: https://opensea.io/collection/YOUR_COLLECTION

## Best Practices

### 1. Start Small

Test with a short clip first:

```bash
# Extract first 10 seconds
ffmpeg -i movie.mp4 -t 10 test_clip.mp4

# Process test clip
python complete_nft_pipeline.py --video test_clip.mp4 ...
```

### 2. Use Testnets

Always test on Mumbai or Sepolia first:
- Free gas (faucets)
- No real money at risk
- Same functionality as mainnet

### 3. Verify Public Domain

Before minting:
- Confirm public domain status
- Document the reason
- Check your jurisdiction
- Save proof/evidence

### 4. Storage Planning

For a feature film:
- Frames: 15-35 GB
- Audio: 100-300 MB
- IPFS storage: Paid plans may be needed for large collections

### 5. Gas Management

- Monitor gas prices (use https://polygonscan.com/gastracker)
- Mint during low-traffic times
- Consider pausing/resuming for better gas prices
- Budget extra for failed transactions

## Troubleshooting

### Common Issues

**"Insufficient funds for gas"**
```bash
# Check balance
python nft_minting_system.py --check-balance

# Get testnet tokens from faucet
# Mainnet: Buy crypto on exchange
```

**"Transaction underpriced"**
- Gas price too low
- Wait and retry
- Increase gas price in config

**"IPFS upload failed"**
- Check Pinata API keys
- Verify file size limits
- Check internet connection

**"FFmpeg not found"**
```bash
# Linux
sudo apt-get install ffmpeg

# Mac
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/
```

**"Out of disk space"**
- Feature films need 20-40 GB
- Use external drive
- Process in batches

## Advanced Usage

### Custom Attributes

Add custom traits to NFTs:

```python
additional_attributes = [
    {"trait_type": "Scene", "value": "Opening Credits"},
    {"trait_type": "Character", "value": "Ben"},
    {"trait_type": "Location", "value": "Farmhouse"}
]
```

### Collection Management

Create themed collections:
- "Opening Scene" - First 1000 frames
- "Key Moments" - Scene changes only
- "Character Frames" - Frames with specific characters

### Rarity Tiers

Assign rarity based on:
- Frame number (key moments)
- Audio quality (special segments)
- Historical significance
- Scene importance

## Legal Considerations

**Public Domain Verification**:
- Check copyright status in your country
- US: Generally pre-1928 or failed copyright
- EU: Different rules may apply
- Some works may have restored copyright

**Transparency**:
- Clearly state public domain status in metadata
- Don't claim original authorship
- Include source information
- Document public domain reason

**Commercial Use**:
- Public domain works can be used commercially
- Including NFT sales
- No royalties owed
- Anyone can create NFTs from same work

**NOT Public Domain**:
- Modern films (generally post-1928 with valid copyright)
- Films with renewed copyright
- Restored or colorized versions (new copyright)
- Foreign films may have different status

## Support & Resources

### Documentation
- Full guide: `PUBLIC_DOMAIN_MOVIE_PROCESSING.md`
- Quick start: `QUICKSTART_MOVIE_PROCESSING.md`
- This guide: `NFT_MINTING_GUIDE.md`

### Tools
- OpenZeppelin Contracts: https://openzeppelin.com/contracts/
- Remix IDE: https://remix.ethereum.org/
- Hardhat: https://hardhat.org/
- Infura: https://infura.io/
- Pinata: https://pinata.cloud/

### Marketplaces
- OpenSea: https://opensea.io/
- Rarible: https://rarible.com/
- LooksRare: https://looksrare.org/

### Public Domain Resources
- Internet Archive: https://archive.org/details/movies
- Public Domain Review: https://publicdomainreview.org/
- Copyright Guide: https://copyright.cornell.edu/publicdomain

## Future Enhancements

Potential additions:
- [ ] ERC-1155 batch minting support
- [ ] Automated rarity calculation
- [ ] Character detection (AI/ML)
- [ ] Scene classification
- [ ] Marketplace integration
- [ ] Collection website generator
- [ ] Royalty splitting
- [ ] DAO governance for collections

---

**Created**: 2025-11-09
**Version**: 1.0
**License**: For public domain content processing only

**READY TO MINT YOUR MOVIE COLLECTION!** 🎬🖼️🎵
