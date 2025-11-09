"""
Complete NFT Pipeline for Public Domain Movies

End-to-end system that:
1. Extracts EVERY frame from a movie
2. Extracts audio assets (full track + segments)
3. Uploads all assets to IPFS
4. Mints NFTs for every frame
5. Mints NFTs for audio assets
6. Generates comprehensive reports

This is the COMPLETE system for processing a public domain movie
and creating an NFT for every single asset.

Usage:
    python complete_nft_pipeline.py \
        --video path/to/movie.mp4 \
        --contract 0x... \
        --movie "Night of the Living Dead" \
        --year 1968 \
        --director "George A. Romero"
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
import cv2

from movie_frame_extractor import PublicDomainMovieProcessor
from audio_extractor import AudioExtractor
from nft_minting_system import NFTMinter, MintingResult
from public_domain_movie_catalog import PUBLIC_DOMAIN_MOVIES

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Configuration for the complete pipeline."""
    video_path: str
    movie_title: str
    movie_year: int
    director: str
    public_domain_reason: str
    nft_contract_address: str
    contract_abi: List[Dict]
    network: str = "polygon_mumbai"
    working_dir: str = "nft_pipeline_output"

    # Frame extraction settings
    extract_all_frames: bool = True
    frame_interval: int = 1  # 1 = every frame
    frame_format: str = "jpg"
    frame_quality: int = 95

    # Audio extraction settings
    extract_full_audio: bool = True
    extract_audio_segments: bool = True
    audio_segment_duration: float = 30.0  # 30 second segments
    audio_format: str = "mp3"

    # Minting settings
    mint_frames: bool = True
    mint_audio: bool = True
    batch_size: int = 10  # NFTs per batch
    delay_between_batches: float = 3.0  # seconds

    # Output settings
    save_reports: bool = True


@dataclass
class PipelineStats:
    """Statistics from pipeline execution."""
    start_time: str
    end_time: str
    duration_seconds: float
    total_frames_extracted: int
    total_audio_assets_extracted: int
    frames_minted: int
    frames_failed: int
    audio_minted: int
    audio_failed: int
    total_gas_used: int
    total_cost_eth: float
    ipfs_uploads: int
    errors: List[str]


class CompleteNFTPipeline:
    """Complete end-to-end NFT creation pipeline."""

    def __init__(self, config: PipelineConfig):
        """
        Initialize pipeline.

        Args:
            config: PipelineConfig object
        """
        self.config = config
        self.working_dir = Path(config.working_dir)
        self.working_dir.mkdir(exist_ok=True)

        # Create subdirectories
        self.frames_dir = self.working_dir / "frames"
        self.audio_dir = self.working_dir / "audio"
        self.reports_dir = self.working_dir / "reports"

        for d in [self.frames_dir, self.audio_dir, self.reports_dir]:
            d.mkdir(exist_ok=True)

        # Initialize components
        self.frame_extractor = PublicDomainMovieProcessor(
            output_dir=str(self.frames_dir)
        )
        self.audio_extractor = AudioExtractor(
            output_dir=str(self.audio_dir)
        )
        self.nft_minter = NFTMinter(network=config.network)

        # Stats
        self.stats = {
            'frames_extracted': 0,
            'audio_extracted': 0,
            'frames_minted': 0,
            'audio_minted': 0,
            'total_gas': 0,
            'errors': []
        }

    async def run_complete_pipeline(self) -> PipelineStats:
        """
        Execute the complete pipeline.

        Returns:
            PipelineStats object
        """
        start_time = datetime.utcnow()
        logger.info("=" * 80)
        logger.info("STARTING COMPLETE NFT PIPELINE")
        logger.info("=" * 80)
        logger.info(f"Movie: {self.config.movie_title} ({self.config.movie_year})")
        logger.info(f"Director: {self.config.director}")
        logger.info(f"Network: {self.config.network}")
        logger.info(f"Contract: {self.config.nft_contract_address}")
        logger.info("=" * 80)

        # Step 1: Extract ALL frames
        logger.info("\n[STEP 1/5] Extracting frames...")
        frames_data = await self.extract_all_frames()

        # Step 2: Extract audio assets
        logger.info("\n[STEP 2/5] Extracting audio assets...")
        audio_data = await self.extract_audio()

        # Step 3: Estimate costs
        logger.info("\n[STEP 3/5] Estimating minting costs...")
        self.estimate_costs(len(frames_data), len(audio_data))

        # Step 4: Mint frame NFTs
        if self.config.mint_frames and frames_data:
            logger.info(f"\n[STEP 4/5] Minting {len(frames_data)} frame NFTs...")
            await self.mint_frame_nfts(frames_data)
        else:
            logger.info("\n[STEP 4/5] Skipping frame minting")

        # Step 5: Mint audio NFTs
        if self.config.mint_audio and audio_data:
            logger.info(f"\n[STEP 5/5] Minting {len(audio_data)} audio NFTs...")
            await self.mint_audio_nfts(audio_data)
        else:
            logger.info("\n[STEP 5/5] Skipping audio minting")

        # Generate final report
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        pipeline_stats = PipelineStats(
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            duration_seconds=duration,
            total_frames_extracted=self.stats['frames_extracted'],
            total_audio_assets_extracted=self.stats['audio_extracted'],
            frames_minted=self.stats['frames_minted'],
            frames_failed=self.stats['frames_extracted'] - self.stats['frames_minted'],
            audio_minted=self.stats['audio_minted'],
            audio_failed=self.stats['audio_extracted'] - self.stats['audio_minted'],
            total_gas_used=self.stats['total_gas'],
            total_cost_eth=0.0,  # Calculate from gas
            ipfs_uploads=self.stats['frames_minted'] + self.stats['audio_minted'],
            errors=self.stats['errors']
        )

        # Save report
        if self.config.save_reports:
            self.save_final_report(pipeline_stats, frames_data, audio_data)

        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE COMPLETE!")
        logger.info("=" * 80)
        logger.info(f"Duration: {duration/60:.2f} minutes")
        logger.info(f"Frames: {pipeline_stats.frames_minted}/{pipeline_stats.total_frames_extracted} minted")
        logger.info(f"Audio: {pipeline_stats.audio_minted}/{pipeline_stats.total_audio_assets_extracted} minted")
        logger.info(f"Total NFTs created: {pipeline_stats.frames_minted + pipeline_stats.audio_minted}")
        logger.info("=" * 80)

        return pipeline_stats

    async def extract_all_frames(self) -> List[Dict]:
        """Extract all frames from the movie."""
        logger.info(f"Extracting frames from: {self.config.video_path}")

        # Open video to get info
        cap = cv2.VideoCapture(self.config.video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        logger.info(f"Total frames to extract: {total_frames:,}")
        logger.info(f"Estimated time: {total_frames/1000:.1f} minutes (at 1000 frames/min)")

        # Extract frames
        result = self.frame_extractor.extract_frames(
            video_path=self.config.video_path,
            movie_title=self.config.movie_title,
            frame_interval=self.config.frame_interval,
            frame_format=self.config.frame_format,
            quality=self.config.frame_quality,
            progress_callback=self._frame_progress_callback
        )

        self.stats['frames_extracted'] = result['frames_extracted']

        # Load frame metadata
        metadata_file = Path(result['frame_metadata_file'])
        with open(metadata_file) as f:
            metadata = json.load(f)

        frames_data = []
        for frame in metadata['frames']:
            frames_data.append({
                'path': frame['file_path'],
                'frame_number': frame['frame_number'],
                'timestamp': frame['timestamp_formatted'],
                'file_hash': frame['file_hash']
            })

        logger.info(f"✓ Extracted {len(frames_data)} frames")
        return frames_data

    async def extract_audio(self) -> List[Dict]:
        """Extract audio assets."""
        audio_data = []

        # Full audio track
        if self.config.extract_full_audio:
            logger.info("Extracting full audio track...")
            full_audio = self.audio_extractor.extract_full_audio(
                video_path=self.config.video_path,
                movie_title=self.config.movie_title,
                audio_format=self.config.audio_format
            )
            audio_data.append({
                'path': full_audio.file_path,
                'type': 'full',
                'duration': full_audio.duration_seconds,
                'start_time': full_audio.start_time,
                'file_hash': full_audio.file_hash
            })

        # Audio segments
        if self.config.extract_audio_segments:
            logger.info("Extracting audio segments...")
            segments = self.audio_extractor.extract_audio_segments(
                video_path=self.config.video_path,
                movie_title=self.config.movie_title,
                segment_duration=self.config.audio_segment_duration,
                audio_format=self.config.audio_format
            )

            for seg in segments:
                audio_data.append({
                    'path': seg.file_path,
                    'type': 'segment',
                    'duration': seg.duration_seconds,
                    'start_time': seg.start_time,
                    'file_hash': seg.file_hash
                })

        self.stats['audio_extracted'] = len(audio_data)
        logger.info(f"✓ Extracted {len(audio_data)} audio assets")
        return audio_data

    def estimate_costs(self, num_frames: int, num_audio: int):
        """Estimate and display minting costs."""
        total_nfts = 0
        if self.config.mint_frames:
            total_nfts += num_frames
        if self.config.mint_audio:
            total_nfts += num_audio

        estimate = self.nft_minter.estimate_gas_cost(total_nfts)

        logger.info("\n" + "-" * 60)
        logger.info("COST ESTIMATE")
        logger.info("-" * 60)
        logger.info(f"Frame NFTs: {num_frames if self.config.mint_frames else 0}")
        logger.info(f"Audio NFTs: {num_audio if self.config.mint_audio else 0}")
        logger.info(f"Total NFTs: {total_nfts}")
        logger.info(f"Gas per NFT: ~{estimate['gas_per_mint']:,}")
        logger.info(f"Total gas: ~{estimate['total_gas']:,}")
        logger.info(f"Gas price: {estimate['gas_price_gwei']:.2f} Gwei")
        logger.info(f"Estimated cost: {estimate['total_cost_eth']:.6f} {estimate['currency']}")
        logger.info("-" * 60)

        # Confirm
        print("\nThis will mint", total_nfts, "NFTs.")
        response = input("Continue? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Aborted by user")
            exit(0)

    async def mint_frame_nfts(self, frames_data: List[Dict]):
        """Mint NFTs for all frames."""
        movie_info = {
            'title': self.config.movie_title,
            'year': self.config.movie_year,
            'director': self.config.director,
            'public_domain_reason': self.config.public_domain_reason
        }

        results = self.nft_minter.batch_mint_frames(
            contract_address=self.config.nft_contract_address,
            contract_abi=self.config.contract_abi,
            frames_data=frames_data,
            movie_info=movie_info,
            batch_size=self.config.batch_size,
            delay_between_batches=self.config.delay_between_batches
        )

        # Update stats
        for result in results:
            if result.success:
                self.stats['frames_minted'] += 1
                if result.gas_used:
                    self.stats['total_gas'] += result.gas_used
            else:
                self.stats['errors'].append(f"Frame minting failed: {result.error}")

        # Save minting report
        self._save_minting_report(results, "frames_minting_report.json")

    async def mint_audio_nfts(self, audio_data: List[Dict]):
        """Mint NFTs for audio assets."""
        results = []

        for idx, audio in enumerate(audio_data):
            logger.info(f"Minting audio NFT {idx + 1}/{len(audio_data)}...")

            # Prepare metadata
            metadata = self.nft_minter.prepare_audio_nft_metadata(
                audio_path=audio['path'],
                movie_title=self.config.movie_title,
                movie_year=self.config.movie_year,
                director=self.config.director,
                duration=audio['duration'],
                start_time=audio['start_time'],
                public_domain_reason=self.config.public_domain_reason,
                asset_type=audio['type']
            )

            # Mint
            result = self.nft_minter.mint_erc721_with_metadata(
                contract_address=self.config.nft_contract_address,
                contract_abi=self.config.contract_abi,
                metadata=metadata
            )

            results.append(result)

            if result.success:
                self.stats['audio_minted'] += 1
                if result.gas_used:
                    self.stats['total_gas'] += result.gas_used
                logger.info(f"  ✓ Audio NFT minted")
            else:
                self.stats['errors'].append(f"Audio minting failed: {result.error}")
                logger.error(f"  ✗ Failed: {result.error}")

            # Delay between mints
            if idx < len(audio_data) - 1:
                await asyncio.sleep(self.config.delay_between_batches)

        # Save report
        self._save_minting_report(results, "audio_minting_report.json")

    def save_final_report(
        self,
        stats: PipelineStats,
        frames_data: List[Dict],
        audio_data: List[Dict]
    ):
        """Save comprehensive final report."""
        report = {
            "movie": {
                "title": self.config.movie_title,
                "year": self.config.movie_year,
                "director": self.config.director,
                "public_domain_reason": self.config.public_domain_reason
            },
            "pipeline_config": asdict(self.config),
            "statistics": asdict(stats),
            "extraction": {
                "total_frames": len(frames_data),
                "total_audio_assets": len(audio_data)
            },
            "minting": {
                "frames_minted": stats.frames_minted,
                "frames_failed": stats.frames_failed,
                "audio_minted": stats.audio_minted,
                "audio_failed": stats.audio_failed,
                "total_nfts_created": stats.frames_minted + stats.audio_minted,
                "total_gas_used": stats.total_gas_used
            }
        }

        report_file = self.reports_dir / "final_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Final report saved: {report_file}")

        # Also save human-readable summary
        summary_file = self.reports_dir / "summary.txt"
        with open(summary_file, 'w') as f:
            f.write(f"NFT Pipeline Report\n")
            f.write(f"{'='*60}\n\n")
            f.write(f"Movie: {self.config.movie_title} ({self.config.movie_year})\n")
            f.write(f"Director: {self.config.director}\n")
            f.write(f"Public Domain: {self.config.public_domain_reason}\n\n")
            f.write(f"Execution Time: {stats.duration_seconds/60:.2f} minutes\n\n")
            f.write(f"Assets Extracted:\n")
            f.write(f"  - Frames: {stats.total_frames_extracted:,}\n")
            f.write(f"  - Audio: {stats.total_audio_assets_extracted}\n\n")
            f.write(f"NFTs Minted:\n")
            f.write(f"  - Frame NFTs: {stats.frames_minted:,}\n")
            f.write(f"  - Audio NFTs: {stats.audio_minted}\n")
            f.write(f"  - Total: {stats.frames_minted + stats.audio_minted:,}\n\n")
            f.write(f"Blockchain:\n")
            f.write(f"  - Network: {self.config.network}\n")
            f.write(f"  - Contract: {self.config.nft_contract_address}\n")
            f.write(f"  - Total Gas: {stats.total_gas_used:,}\n\n")
            if stats.errors:
                f.write(f"Errors ({len(stats.errors)}):\n")
                for error in stats.errors[:10]:
                    f.write(f"  - {error}\n")

        logger.info(f"Summary saved: {summary_file}")

    def _save_minting_report(self, results: List[MintingResult], filename: str):
        """Save minting results to file."""
        report_file = self.reports_dir / filename
        with open(report_file, 'w') as f:
            json.dump({
                "total": len(results),
                "successful": sum(1 for r in results if r.success),
                "failed": sum(1 for r in results if not r.success),
                "results": [asdict(r) for r in results]
            }, f, indent=2)

    def _frame_progress_callback(self, current: int, total: int):
        """Callback for frame extraction progress."""
        if current % 1000 == 0:
            logger.info(f"Progress: {current:,}/{total:,} frames ({current/total*100:.1f}%)")


async def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Complete NFT Pipeline")
    parser.add_argument("--video", required=True, help="Path to video file")
    parser.add_argument("--movie", required=True, help="Movie title")
    parser.add_argument("--year", type=int, required=True, help="Movie year")
    parser.add_argument("--director", required=True, help="Director name")
    parser.add_argument("--reason", default="Copyright expired",
                        help="Public domain reason")
    parser.add_argument("--contract", required=True, help="NFT contract address")
    parser.add_argument("--abi-file", required=True, help="Path to contract ABI JSON")
    parser.add_argument("--network", default="polygon_mumbai", help="Blockchain network")
    parser.add_argument("--no-mint", action="store_true",
                        help="Extract only, don't mint")
    parser.add_argument("--frames-only", action="store_true",
                        help="Process frames only (skip audio)")

    args = parser.parse_args()

    # Load contract ABI
    with open(args.abi_file) as f:
        contract_abi = json.load(f)

    # Create config
    config = PipelineConfig(
        video_path=args.video,
        movie_title=args.movie,
        movie_year=args.year,
        director=args.director,
        public_domain_reason=args.reason,
        nft_contract_address=args.contract,
        contract_abi=contract_abi,
        network=args.network,
        mint_frames=not args.no_mint,
        mint_audio=not args.no_mint and not args.frames_only,
        extract_audio_segments=not args.frames_only
    )

    # Run pipeline
    pipeline = CompleteNFTPipeline(config)
    stats = await pipeline.run_complete_pipeline()

    print("\n✓ Pipeline complete! Check the reports directory for details.")


if __name__ == "__main__":
    asyncio.run(main())
