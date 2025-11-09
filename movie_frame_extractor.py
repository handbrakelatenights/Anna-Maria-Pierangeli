"""
Public Domain Movie Frame Extractor

This module provides utilities to extract frames from public domain movies
and prepare them for various uses including NFT creation, archival, and analysis.

Legal Note: This tool is designed for use with movies that are confirmed to be
in the public domain. Users are responsible for verifying the public domain
status of any content they process.
"""

import cv2
import os
from pathlib import Path
from typing import Optional, Callable, Dict, List
import json
from datetime import datetime
import hashlib
from dataclasses import dataclass, asdict
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class FrameMetadata:
    """Metadata for an extracted frame."""
    frame_number: int
    timestamp_ms: float
    timestamp_formatted: str
    file_path: str
    file_hash: str
    resolution: tuple
    file_size: int
    extracted_at: str


@dataclass
class MovieMetadata:
    """Metadata for the source movie."""
    title: str
    source_file: str
    total_frames: int
    fps: float
    duration_seconds: float
    resolution: tuple
    codec: str
    public_domain_year: Optional[int] = None
    source_url: Optional[str] = None
    notes: Optional[str] = None


class PublicDomainMovieProcessor:
    """Process public domain movies and extract frames."""

    def __init__(self, output_dir: str = "extracted_frames"):
        """
        Initialize the movie processor.

        Args:
            output_dir: Directory to save extracted frames
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def extract_frames(
        self,
        video_path: str,
        movie_title: str,
        frame_interval: int = 1,
        max_frames: Optional[int] = None,
        frame_format: str = "jpg",
        quality: int = 95,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict:
        """
        Extract frames from a video file.

        Args:
            video_path: Path to the video file
            movie_title: Title of the movie for organization
            frame_interval: Extract every Nth frame (1 = all frames)
            max_frames: Maximum number of frames to extract (None = all)
            frame_format: Output format (jpg, png, etc.)
            quality: JPEG quality (0-100, only for jpg format)
            progress_callback: Optional callback function(current, total)

        Returns:
            Dictionary with extraction results and metadata
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Create output directory for this movie
        movie_dir = self.output_dir / self._sanitize_filename(movie_title)
        movie_dir.mkdir(exist_ok=True)

        # Open video
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Failed to open video: {video_path}")

        try:
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            codec = int(cap.get(cv2.CAP_PROP_FOURCC))
            codec_str = "".join([chr((codec >> 8 * i) & 0xFF) for i in range(4)])

            duration = total_frames / fps if fps > 0 else 0

            logger.info(f"Processing: {movie_title}")
            logger.info(f"Total frames: {total_frames}, FPS: {fps}, Duration: {duration:.2f}s")
            logger.info(f"Resolution: {width}x{height}")

            # Create movie metadata
            movie_metadata = MovieMetadata(
                title=movie_title,
                source_file=str(video_path),
                total_frames=total_frames,
                fps=fps,
                duration_seconds=duration,
                resolution=(width, height),
                codec=codec_str
            )

            # Extract frames
            frame_metadata_list = []
            frames_extracted = 0
            frame_count = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Check if we should extract this frame
                if frame_count % frame_interval == 0:
                    # Check max_frames limit
                    if max_frames and frames_extracted >= max_frames:
                        break

                    # Save frame
                    frame_file = movie_dir / f"frame_{frame_count:08d}.{frame_format}"

                    # Set quality parameters
                    if frame_format.lower() in ['jpg', 'jpeg']:
                        params = [cv2.IMWRITE_JPEG_QUALITY, quality]
                    elif frame_format.lower() == 'png':
                        params = [cv2.IMWRITE_PNG_COMPRESSION, 9]
                    else:
                        params = []

                    cv2.imwrite(str(frame_file), frame, params)

                    # Calculate file hash
                    file_hash = self._calculate_file_hash(frame_file)

                    # Create frame metadata
                    timestamp_ms = (frame_count / fps) * 1000 if fps > 0 else 0
                    timestamp_formatted = self._format_timestamp(timestamp_ms / 1000)

                    frame_meta = FrameMetadata(
                        frame_number=frame_count,
                        timestamp_ms=timestamp_ms,
                        timestamp_formatted=timestamp_formatted,
                        file_path=str(frame_file),
                        file_hash=file_hash,
                        resolution=(width, height),
                        file_size=frame_file.stat().st_size,
                        extracted_at=datetime.utcnow().isoformat()
                    )
                    frame_metadata_list.append(frame_meta)

                    frames_extracted += 1

                    # Progress callback
                    if progress_callback and frames_extracted % 100 == 0:
                        progress_callback(frames_extracted, total_frames // frame_interval)

                frame_count += 1

            # Save metadata
            self._save_metadata(movie_dir, movie_metadata, frame_metadata_list)

            logger.info(f"Extraction complete: {frames_extracted} frames saved to {movie_dir}")

            return {
                "success": True,
                "frames_extracted": frames_extracted,
                "output_directory": str(movie_dir),
                "movie_metadata": asdict(movie_metadata),
                "frame_metadata_file": str(movie_dir / "metadata.json")
            }

        finally:
            cap.release()

    def batch_extract_sample_frames(
        self,
        video_path: str,
        movie_title: str,
        num_samples: int = 100,
        **kwargs
    ) -> Dict:
        """
        Extract a representative sample of frames from a movie.

        Args:
            video_path: Path to the video file
            movie_title: Title of the movie
            num_samples: Number of frames to extract
            **kwargs: Additional arguments for extract_frames

        Returns:
            Dictionary with extraction results
        """
        # Calculate interval to get desired number of samples
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        interval = max(1, total_frames // num_samples)

        return self.extract_frames(
            video_path=video_path,
            movie_title=movie_title,
            frame_interval=interval,
            max_frames=num_samples,
            **kwargs
        )

    def extract_key_scenes(
        self,
        video_path: str,
        movie_title: str,
        scene_change_threshold: float = 30.0,
        **kwargs
    ) -> Dict:
        """
        Extract frames at scene changes (key moments).

        Args:
            video_path: Path to the video file
            movie_title: Title of the movie
            scene_change_threshold: Threshold for detecting scene changes
            **kwargs: Additional arguments for saving frames

        Returns:
            Dictionary with extraction results
        """
        video_path = Path(video_path)
        movie_dir = self.output_dir / self._sanitize_filename(movie_title)
        movie_dir.mkdir(exist_ok=True)

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Failed to open video: {video_path}")

        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            prev_frame = None
            frame_count = 0
            scenes_detected = 0
            frame_metadata_list = []

            logger.info(f"Detecting key scenes in: {movie_title}")

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if prev_frame is not None:
                    # Calculate difference between frames
                    diff = cv2.absdiff(frame, prev_frame)
                    mean_diff = diff.mean()

                    # If difference exceeds threshold, it's likely a scene change
                    if mean_diff > scene_change_threshold:
                        frame_file = movie_dir / f"scene_{scenes_detected:05d}_frame_{frame_count:08d}.jpg"
                        cv2.imwrite(str(frame_file), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])

                        file_hash = self._calculate_file_hash(frame_file)
                        timestamp_ms = (frame_count / fps) * 1000 if fps > 0 else 0

                        frame_meta = FrameMetadata(
                            frame_number=frame_count,
                            timestamp_ms=timestamp_ms,
                            timestamp_formatted=self._format_timestamp(timestamp_ms / 1000),
                            file_path=str(frame_file),
                            file_hash=file_hash,
                            resolution=(frame.shape[1], frame.shape[0]),
                            file_size=frame_file.stat().st_size,
                            extracted_at=datetime.utcnow().isoformat()
                        )
                        frame_metadata_list.append(frame_meta)
                        scenes_detected += 1

                prev_frame = frame.copy()
                frame_count += 1

                if frame_count % 1000 == 0:
                    logger.info(f"Processed {frame_count}/{total_frames} frames, {scenes_detected} scenes detected")

            # Save metadata
            metadata_file = movie_dir / "key_scenes_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump({
                    "movie_title": movie_title,
                    "total_scenes": scenes_detected,
                    "frames": [asdict(fm) for fm in frame_metadata_list]
                }, f, indent=2)

            logger.info(f"Scene detection complete: {scenes_detected} key scenes saved")

            return {
                "success": True,
                "scenes_detected": scenes_detected,
                "output_directory": str(movie_dir),
                "metadata_file": str(metadata_file)
            }

        finally:
            cap.release()

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Remove or replace characters that are invalid in filenames."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()

    @staticmethod
    def _calculate_file_hash(file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Format seconds as HH:MM:SS.mmm"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

    def _save_metadata(
        self,
        output_dir: Path,
        movie_metadata: MovieMetadata,
        frame_metadata_list: List[FrameMetadata]
    ):
        """Save metadata to JSON file."""
        metadata = {
            "movie": asdict(movie_metadata),
            "extraction_info": {
                "total_frames_extracted": len(frame_metadata_list),
                "extraction_date": datetime.utcnow().isoformat()
            },
            "frames": [asdict(fm) for fm in frame_metadata_list]
        }

        metadata_file = output_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Also save a summary file
        summary_file = output_dir / "summary.txt"
        with open(summary_file, 'w') as f:
            f.write(f"Movie: {movie_metadata.title}\n")
            f.write(f"Source: {movie_metadata.source_file}\n")
            f.write(f"Total Original Frames: {movie_metadata.total_frames}\n")
            f.write(f"FPS: {movie_metadata.fps}\n")
            f.write(f"Duration: {movie_metadata.duration_seconds:.2f} seconds\n")
            f.write(f"Resolution: {movie_metadata.resolution[0]}x{movie_metadata.resolution[1]}\n")
            f.write(f"Frames Extracted: {len(frame_metadata_list)}\n")
            f.write(f"Extraction Date: {datetime.utcnow().isoformat()}\n")


def main():
    """Example usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Extract frames from public domain movies")
    parser.add_argument("video_path", help="Path to the video file")
    parser.add_argument("--title", required=True, help="Movie title")
    parser.add_argument("--output", default="extracted_frames", help="Output directory")
    parser.add_argument("--interval", type=int, default=1, help="Extract every Nth frame")
    parser.add_argument("--max-frames", type=int, help="Maximum frames to extract")
    parser.add_argument("--format", default="jpg", help="Output format (jpg, png)")
    parser.add_argument("--quality", type=int, default=95, help="JPEG quality (0-100)")
    parser.add_argument("--mode", default="all", choices=["all", "sample", "scenes"],
                        help="Extraction mode")
    parser.add_argument("--samples", type=int, default=100, help="Number of samples (for sample mode)")

    args = parser.parse_args()

    processor = PublicDomainMovieProcessor(output_dir=args.output)

    def progress(current, total):
        print(f"Progress: {current}/{total} frames extracted", end='\r')

    try:
        if args.mode == "sample":
            result = processor.batch_extract_sample_frames(
                video_path=args.video_path,
                movie_title=args.title,
                num_samples=args.samples,
                frame_format=args.format,
                quality=args.quality,
                progress_callback=progress
            )
        elif args.mode == "scenes":
            result = processor.extract_key_scenes(
                video_path=args.video_path,
                movie_title=args.title
            )
        else:
            result = processor.extract_frames(
                video_path=args.video_path,
                movie_title=args.title,
                frame_interval=args.interval,
                max_frames=args.max_frames,
                frame_format=args.format,
                quality=args.quality,
                progress_callback=progress
            )

        print(f"\n✓ Success! {result['frames_extracted' if args.mode != 'scenes' else 'scenes_detected']} frames extracted")
        print(f"  Output: {result['output_directory']}")

    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
