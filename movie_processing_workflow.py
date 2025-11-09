"""
Public Domain Movie Processing Workflow

This module coordinates the complete workflow for processing public domain movies:
1. Download from Internet Archive
2. Extract frames
3. Generate metadata
4. Create database articles
5. Prepare NFT metadata

Usage:
    python movie_processing_workflow.py --movie "Night of the Living Dead" --all
"""

import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import Optional, Dict
import logging
from movie_frame_extractor import PublicDomainMovieProcessor
from public_domain_movie_catalog import PublicDomainMovieCatalog, PUBLIC_DOMAIN_MOVIES
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MovieProcessingWorkflow:
    """Coordinates the complete public domain movie processing workflow."""

    def __init__(self, working_dir: str = "public_domain_movies"):
        """
        Initialize the workflow.

        Args:
            working_dir: Root directory for all processing
        """
        self.working_dir = Path(working_dir)
        self.working_dir.mkdir(exist_ok=True)

        self.downloads_dir = self.working_dir / "downloads"
        self.frames_dir = self.working_dir / "extracted_frames"
        self.nft_metadata_dir = self.working_dir / "nft_metadata"

        for directory in [self.downloads_dir, self.frames_dir, self.nft_metadata_dir]:
            directory.mkdir(exist_ok=True)

        self.frame_processor = PublicDomainMovieProcessor(output_dir=str(self.frames_dir))
        self.catalog = PublicDomainMovieCatalog()

    async def download_from_archive(
        self,
        archive_identifier: str,
        movie_title: str,
        file_format: str = "mp4"
    ) -> Optional[Path]:
        """
        Download a movie from Internet Archive.

        Args:
            archive_identifier: Archive.org identifier (from URL)
            movie_title: Movie title for file naming
            file_format: Preferred format (mp4, avi, etc.)

        Returns:
            Path to downloaded file or None if failed
        """
        # Extract identifier from URL if full URL provided
        if "archive.org" in archive_identifier:
            archive_identifier = archive_identifier.split("/")[-1]

        # Internet Archive download URL pattern
        download_url = f"https://archive.org/download/{archive_identifier}/{archive_identifier}.{file_format}"

        output_file = self.downloads_dir / f"{movie_title.replace(' ', '_')}.{file_format}"

        if output_file.exists():
            logger.info(f"File already exists: {output_file}")
            return output_file

        logger.info(f"Downloading {movie_title} from Internet Archive...")
        logger.info(f"URL: {download_url}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(download_url) as response:
                    if response.status == 200:
                        total_size = int(response.headers.get('content-length', 0))
                        downloaded = 0

                        async with aiofiles.open(output_file, 'wb') as f:
                            async for chunk in response.content.iter_chunked(1024 * 1024):  # 1MB chunks
                                await f.write(chunk)
                                downloaded += len(chunk)
                                if total_size:
                                    progress = (downloaded / total_size) * 100
                                    logger.info(f"Download progress: {progress:.1f}%")

                        logger.info(f"✓ Downloaded to {output_file}")
                        return output_file
                    else:
                        logger.error(f"Download failed with status {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error downloading: {e}")
            return None

    async def process_movie(
        self,
        movie_title: str,
        extract_mode: str = "sample",
        num_samples: int = 100,
        add_to_database: bool = True,
        generate_nft_metadata: bool = True
    ) -> Dict:
        """
        Complete processing workflow for a public domain movie.

        Args:
            movie_title: Title of the movie
            extract_mode: Frame extraction mode (all, sample, scenes)
            num_samples: Number of sample frames (for sample mode)
            add_to_database: Whether to add article to database
            generate_nft_metadata: Whether to generate NFT metadata

        Returns:
            Dictionary with processing results
        """
        logger.info(f"=" * 80)
        logger.info(f"Processing: {movie_title}")
        logger.info(f"=" * 80)

        # Find movie in catalog
        movie = next((m for m in PUBLIC_DOMAIN_MOVIES if m.title.lower() == movie_title.lower()), None)
        if not movie:
            logger.error(f"Movie '{movie_title}' not found in catalog")
            return {"success": False, "error": "Movie not found in catalog"}

        results = {
            "movie_title": movie.title,
            "success": True,
            "steps": {}
        }

        # Step 1: Download movie (if archive URL available)
        video_file = None
        if movie.archive_url:
            logger.info("\n[1/4] Downloading movie...")
            # Extract archive identifier from URL
            archive_id = movie.archive_url.split("/")[-1]
            video_file = await self.download_from_archive(
                archive_identifier=archive_id,
                movie_title=movie.title
            )
            results["steps"]["download"] = {
                "success": video_file is not None,
                "file_path": str(video_file) if video_file else None
            }
        else:
            logger.info("\n[1/4] Skipping download - no archive URL")
            results["steps"]["download"] = {
                "success": False,
                "reason": "No archive URL available"
            }

        # Step 2: Extract frames (if video downloaded)
        if video_file and video_file.exists():
            logger.info("\n[2/4] Extracting frames...")

            if extract_mode == "sample":
                extract_result = self.frame_processor.batch_extract_sample_frames(
                    video_path=str(video_file),
                    movie_title=movie.title,
                    num_samples=num_samples
                )
            elif extract_mode == "scenes":
                extract_result = self.frame_processor.extract_key_scenes(
                    video_path=str(video_file),
                    movie_title=movie.title
                )
            else:  # all frames
                extract_result = self.frame_processor.extract_frames(
                    video_path=str(video_file),
                    movie_title=movie.title,
                    frame_interval=1
                )

            results["steps"]["frame_extraction"] = extract_result
            logger.info(f"✓ Extracted frames: {extract_result.get('frames_extracted', extract_result.get('scenes_detected', 0))}")
        else:
            logger.info("\n[2/4] Skipping frame extraction - no video file")
            results["steps"]["frame_extraction"] = {
                "success": False,
                "reason": "No video file available"
            }

        # Step 3: Add to database
        if add_to_database:
            logger.info("\n[3/4] Adding to database...")
            article = await self.catalog.generate_article_from_movie(movie)

            # Connect to database and insert
            from motor.motor_asyncio import AsyncIOMotorClient
            import os
            mongo_url = os.environ.get('MONGO_URL')
            db_name = os.environ.get('DB_NAME', 'newsdb')

            if mongo_url:
                client = AsyncIOMotorClient(mongo_url)
                db = client[db_name]

                # Check if exists
                existing = await db.articles.find_one({"title": article["title"]})
                if not existing:
                    await db.articles.insert_one(article)
                    logger.info(f"✓ Article added to database")
                    results["steps"]["database"] = {
                        "success": True,
                        "article_id": article["id"]
                    }
                else:
                    logger.info(f"Article already exists in database")
                    results["steps"]["database"] = {
                        "success": True,
                        "article_id": existing["id"],
                        "already_existed": True
                    }
                client.close()
            else:
                logger.warning("No database connection - skipping")
                results["steps"]["database"] = {
                    "success": False,
                    "reason": "No MONGO_URL configured"
                }
        else:
            logger.info("\n[3/4] Skipping database - disabled")
            results["steps"]["database"] = {"success": False, "reason": "Disabled"}

        # Step 4: Generate NFT metadata
        if generate_nft_metadata:
            logger.info("\n[4/4] Generating NFT metadata...")
            nft_metadata_file = self.catalog.export_nft_metadata(
                movie=movie,
                output_dir=str(self.nft_metadata_dir)
            )
            logger.info(f"✓ NFT metadata saved")
            results["steps"]["nft_metadata"] = {
                "success": True,
                "file_path": nft_metadata_file
            }
        else:
            logger.info("\n[4/4] Skipping NFT metadata - disabled")
            results["steps"]["nft_metadata"] = {"success": False, "reason": "Disabled"}

        logger.info(f"\n" + "=" * 80)
        logger.info(f"Processing complete for {movie.title}")
        logger.info(f"=" * 80)

        return results

    async def batch_process_all_movies(self, **kwargs) -> Dict:
        """
        Process all movies in the catalog.

        Args:
            **kwargs: Arguments to pass to process_movie

        Returns:
            Summary of all processing
        """
        results = {
            "total_movies": len(PUBLIC_DOMAIN_MOVIES),
            "processed": 0,
            "failed": 0,
            "movies": []
        }

        for movie in PUBLIC_DOMAIN_MOVIES:
            try:
                result = await self.process_movie(movie.title, **kwargs)
                if result.get("success"):
                    results["processed"] += 1
                else:
                    results["failed"] += 1
                results["movies"].append(result)
            except Exception as e:
                logger.error(f"Error processing {movie.title}: {e}")
                results["failed"] += 1
                results["movies"].append({
                    "movie_title": movie.title,
                    "success": False,
                    "error": str(e)
                })

        return results

    def generate_collection_manifest(self) -> Dict:
        """
        Generate a manifest file for the entire collection.

        Returns:
            Collection manifest dictionary
        """
        manifest = {
            "collection_name": "Public Domain Cinema Collection",
            "description": "A curated collection of classic public domain films",
            "total_movies": len(PUBLIC_DOMAIN_MOVIES),
            "movies": []
        }

        for movie in PUBLIC_DOMAIN_MOVIES:
            movie_info = {
                "title": movie.title,
                "year": movie.year,
                "director": movie.director,
                "genre": movie.genre,
                "duration_minutes": movie.duration_minutes,
                "public_domain_reason": movie.public_domain_reason,
                "archive_url": movie.archive_url,
                "wikipedia_url": movie.wikipedia_url
            }
            manifest["movies"].append(movie_info)

        # Save manifest
        manifest_file = self.working_dir / "collection_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Collection manifest saved to {manifest_file}")
        return manifest


async def main():
    """Command-line interface for the workflow."""
    import argparse

    parser = argparse.ArgumentParser(description="Public Domain Movie Processing Workflow")
    parser.add_argument("--movie", help="Movie title to process")
    parser.add_argument("--all", action="store_true", help="Process all movies in catalog")
    parser.add_argument("--list", action="store_true", help="List available movies")
    parser.add_argument("--extract-mode", choices=["all", "sample", "scenes"], default="sample",
                        help="Frame extraction mode")
    parser.add_argument("--samples", type=int, default=100,
                        help="Number of sample frames (for sample mode)")
    parser.add_argument("--no-download", action="store_true", help="Skip download step")
    parser.add_argument("--no-database", action="store_true", help="Skip database insertion")
    parser.add_argument("--no-nft", action="store_true", help="Skip NFT metadata generation")
    parser.add_argument("--manifest", action="store_true", help="Generate collection manifest")
    parser.add_argument("--working-dir", default="public_domain_movies",
                        help="Working directory for processing")

    args = parser.parse_args()

    workflow = MovieProcessingWorkflow(working_dir=args.working_dir)

    if args.list:
        print(f"\nAvailable Public Domain Movies ({len(PUBLIC_DOMAIN_MOVIES)}):\n")
        for i, movie in enumerate(PUBLIC_DOMAIN_MOVIES, 1):
            print(f"{i:2d}. {movie.title} ({movie.year}) - {movie.genre}")
            print(f"     Director: {movie.director}")
            if movie.archive_url:
                print(f"     Available at: {movie.archive_url}")
            print()

    elif args.manifest:
        manifest = workflow.generate_collection_manifest()
        print(f"\n✓ Generated manifest for {manifest['total_movies']} movies")
        print(f"  Saved to: {workflow.working_dir / 'collection_manifest.json'}")

    elif args.all:
        print("\n" + "=" * 80)
        print("BATCH PROCESSING ALL MOVIES")
        print("=" * 80 + "\n")

        results = await workflow.batch_process_all_movies(
            extract_mode=args.extract_mode,
            num_samples=args.samples,
            add_to_database=not args.no_database,
            generate_nft_metadata=not args.no_nft
        )

        print("\n" + "=" * 80)
        print("BATCH PROCESSING SUMMARY")
        print("=" * 80)
        print(f"Total movies: {results['total_movies']}")
        print(f"Successfully processed: {results['processed']}")
        print(f"Failed: {results['failed']}")

    elif args.movie:
        result = await workflow.process_movie(
            movie_title=args.movie,
            extract_mode=args.extract_mode,
            num_samples=args.samples,
            add_to_database=not args.no_database,
            generate_nft_metadata=not args.no_nft
        )

        if result.get("success"):
            print(f"\n✓ Successfully processed {args.movie}")
        else:
            print(f"\n✗ Failed to process {args.movie}")
            if "error" in result:
                print(f"  Error: {result['error']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
