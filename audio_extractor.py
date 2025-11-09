"""
Audio Asset Extractor for Public Domain Movies

Extracts and processes audio from public domain movies for NFT creation.
Supports multiple extraction modes:
- Full audio track
- Audio segments (by time interval)
- Scene-based audio clips
- Individual sound effects/moments

Legal Note: For use with confirmed public domain content only.
"""

import subprocess
import json
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class AudioAssetMetadata:
    """Metadata for an extracted audio asset."""
    asset_id: str
    asset_type: str  # 'full', 'segment', 'scene', 'effect'
    file_path: str
    file_hash: str
    duration_seconds: float
    start_time: float
    end_time: float
    sample_rate: int
    channels: int
    bitrate: str
    file_size: int
    format: str
    extracted_at: str
    source_movie: str


class AudioExtractor:
    """Extract audio assets from video files."""

    def __init__(self, output_dir: str = "extracted_audio"):
        """
        Initialize audio extractor.

        Args:
            output_dir: Directory for audio output
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def check_ffmpeg_installed(self) -> bool:
        """Check if FFmpeg is installed."""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def get_video_info(self, video_path: str) -> Dict:
        """
        Get video/audio information using ffprobe.

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video/audio information
        """
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(video_path)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {}

    def extract_full_audio(
        self,
        video_path: str,
        movie_title: str,
        audio_format: str = 'mp3',
        quality: str = '320k'
    ) -> AudioAssetMetadata:
        """
        Extract complete audio track from video.

        Args:
            video_path: Path to video file
            movie_title: Movie title for naming
            audio_format: Output format (mp3, wav, flac, ogg)
            quality: Audio bitrate (320k, 256k, 192k, etc.)

        Returns:
            AudioAssetMetadata object
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        # Create output directory for this movie
        movie_dir = self.output_dir / self._sanitize_filename(movie_title)
        movie_dir.mkdir(exist_ok=True)

        # Output file
        output_file = movie_dir / f"full_audio.{audio_format}"

        logger.info(f"Extracting full audio from {movie_title}...")

        # FFmpeg command
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-vn',  # No video
            '-acodec', self._get_codec(audio_format),
            '-ab', quality,
            '-y',  # Overwrite
            str(output_file)
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"✓ Audio extracted to {output_file}")

            # Get audio info
            info = self.get_video_info(output_file)
            audio_stream = next(
                (s for s in info.get('streams', []) if s['codec_type'] == 'audio'),
                {}
            )

            # Calculate file hash
            file_hash = self._calculate_file_hash(output_file)

            # Create metadata
            duration = float(info.get('format', {}).get('duration', 0))

            metadata = AudioAssetMetadata(
                asset_id=file_hash[:16],
                asset_type='full',
                file_path=str(output_file),
                file_hash=file_hash,
                duration_seconds=duration,
                start_time=0.0,
                end_time=duration,
                sample_rate=int(audio_stream.get('sample_rate', 0)),
                channels=int(audio_stream.get('channels', 0)),
                bitrate=audio_stream.get('bit_rate', quality),
                file_size=output_file.stat().st_size,
                format=audio_format,
                extracted_at=datetime.utcnow().isoformat(),
                source_movie=movie_title
            )

            # Save metadata
            self._save_metadata(movie_dir, [metadata], "full_audio_metadata.json")

            return metadata

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
            raise

    def extract_audio_segments(
        self,
        video_path: str,
        movie_title: str,
        segment_duration: float = 30.0,
        audio_format: str = 'mp3',
        quality: str = '192k',
        max_segments: Optional[int] = None
    ) -> List[AudioAssetMetadata]:
        """
        Extract audio in time-based segments.

        Args:
            video_path: Path to video file
            movie_title: Movie title
            segment_duration: Duration of each segment in seconds
            audio_format: Output format
            quality: Audio bitrate
            max_segments: Maximum number of segments to extract

        Returns:
            List of AudioAssetMetadata objects
        """
        video_path = Path(video_path)
        movie_dir = self.output_dir / self._sanitize_filename(movie_title)
        movie_dir.mkdir(exist_ok=True)

        # Get total duration
        info = self.get_video_info(video_path)
        total_duration = float(info.get('format', {}).get('duration', 0))

        logger.info(f"Extracting audio segments from {movie_title}")
        logger.info(f"Total duration: {total_duration:.2f}s, Segment size: {segment_duration}s")

        segments_metadata = []
        segment_count = 0
        start_time = 0.0

        while start_time < total_duration:
            if max_segments and segment_count >= max_segments:
                break

            end_time = min(start_time + segment_duration, total_duration)
            actual_duration = end_time - start_time

            # Output file
            output_file = movie_dir / f"segment_{segment_count:05d}.{audio_format}"

            # FFmpeg command for segment
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-ss', str(start_time),
                '-t', str(actual_duration),
                '-vn',
                '-acodec', self._get_codec(audio_format),
                '-ab', quality,
                '-y',
                str(output_file)
            ]

            try:
                subprocess.run(cmd, check=True, capture_output=True)

                # Get audio info
                seg_info = self.get_video_info(output_file)
                audio_stream = next(
                    (s for s in seg_info.get('streams', []) if s['codec_type'] == 'audio'),
                    {}
                )

                file_hash = self._calculate_file_hash(output_file)

                metadata = AudioAssetMetadata(
                    asset_id=file_hash[:16],
                    asset_type='segment',
                    file_path=str(output_file),
                    file_hash=file_hash,
                    duration_seconds=actual_duration,
                    start_time=start_time,
                    end_time=end_time,
                    sample_rate=int(audio_stream.get('sample_rate', 0)),
                    channels=int(audio_stream.get('channels', 0)),
                    bitrate=audio_stream.get('bit_rate', quality),
                    file_size=output_file.stat().st_size,
                    format=audio_format,
                    extracted_at=datetime.utcnow().isoformat(),
                    source_movie=movie_title
                )

                segments_metadata.append(metadata)
                segment_count += 1

                if segment_count % 10 == 0:
                    logger.info(f"Extracted {segment_count} segments...")

            except subprocess.CalledProcessError as e:
                logger.error(f"Error extracting segment {segment_count}: {e}")

            start_time = end_time

        # Save metadata
        self._save_metadata(movie_dir, segments_metadata, "segments_metadata.json")

        logger.info(f"✓ Extracted {len(segments_metadata)} audio segments")
        return segments_metadata

    def extract_audio_for_frames(
        self,
        video_path: str,
        movie_title: str,
        frame_timestamps: List[float],
        audio_duration: float = 5.0,
        audio_format: str = 'mp3'
    ) -> List[AudioAssetMetadata]:
        """
        Extract audio clips corresponding to specific frame timestamps.

        Args:
            video_path: Path to video file
            movie_title: Movie title
            frame_timestamps: List of timestamps (in seconds) for each frame
            audio_duration: Duration of audio clip for each frame
            audio_format: Output format

        Returns:
            List of AudioAssetMetadata objects
        """
        video_path = Path(video_path)
        movie_dir = self.output_dir / self._sanitize_filename(movie_title) / "frame_audio"
        movie_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Extracting {len(frame_timestamps)} audio clips for frames...")

        audio_metadata = []

        for idx, timestamp in enumerate(frame_timestamps):
            output_file = movie_dir / f"frame_{idx:08d}_audio.{audio_format}"

            # Extract audio around the frame timestamp
            start_time = max(0, timestamp - audio_duration / 2)

            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-ss', str(start_time),
                '-t', str(audio_duration),
                '-vn',
                '-acodec', self._get_codec(audio_format),
                '-y',
                str(output_file)
            ]

            try:
                subprocess.run(cmd, check=True, capture_output=True)

                file_hash = self._calculate_file_hash(output_file)

                metadata = AudioAssetMetadata(
                    asset_id=file_hash[:16],
                    asset_type='frame_audio',
                    file_path=str(output_file),
                    file_hash=file_hash,
                    duration_seconds=audio_duration,
                    start_time=start_time,
                    end_time=start_time + audio_duration,
                    sample_rate=44100,  # Default, could probe
                    channels=2,
                    bitrate='192k',
                    file_size=output_file.stat().st_size,
                    format=audio_format,
                    extracted_at=datetime.utcnow().isoformat(),
                    source_movie=movie_title
                )

                audio_metadata.append(metadata)

                if (idx + 1) % 100 == 0:
                    logger.info(f"Extracted audio for {idx + 1} frames...")

            except subprocess.CalledProcessError as e:
                logger.error(f"Error extracting audio for frame {idx}: {e}")

        # Save metadata
        self._save_metadata(movie_dir.parent, audio_metadata, "frame_audio_metadata.json")

        logger.info(f"✓ Extracted audio for {len(audio_metadata)} frames")
        return audio_metadata

    @staticmethod
    def _get_codec(audio_format: str) -> str:
        """Get FFmpeg codec for audio format."""
        codecs = {
            'mp3': 'libmp3lame',
            'wav': 'pcm_s16le',
            'flac': 'flac',
            'ogg': 'libvorbis',
            'aac': 'aac',
            'm4a': 'aac'
        }
        return codecs.get(audio_format.lower(), 'libmp3lame')

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Remove invalid characters from filename."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()

    @staticmethod
    def _calculate_file_hash(file_path: Path) -> str:
        """Calculate SHA-256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _save_metadata(
        self,
        output_dir: Path,
        metadata_list: List[AudioAssetMetadata],
        filename: str
    ):
        """Save metadata to JSON file."""
        metadata_file = output_dir / filename
        with open(metadata_file, 'w') as f:
            json.dump({
                "total_assets": len(metadata_list),
                "extraction_date": datetime.utcnow().isoformat(),
                "assets": [asdict(m) for m in metadata_list]
            }, f, indent=2)

        logger.info(f"Metadata saved to {metadata_file}")


def main():
    """Command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Extract audio assets from public domain movies")
    parser.add_argument("video_path", help="Path to video file")
    parser.add_argument("--title", required=True, help="Movie title")
    parser.add_argument("--mode", choices=["full", "segments"], default="full",
                        help="Extraction mode")
    parser.add_argument("--segment-duration", type=float, default=30.0,
                        help="Segment duration in seconds (for segments mode)")
    parser.add_argument("--format", default="mp3", choices=["mp3", "wav", "flac", "ogg"],
                        help="Audio output format")
    parser.add_argument("--quality", default="320k", help="Audio bitrate (e.g., 320k, 192k)")
    parser.add_argument("--max-segments", type=int, help="Maximum segments to extract")
    parser.add_argument("--output", default="extracted_audio", help="Output directory")

    args = parser.parse_args()

    extractor = AudioExtractor(output_dir=args.output)

    # Check FFmpeg
    if not extractor.check_ffmpeg_installed():
        logger.error("FFmpeg not found! Please install FFmpeg first.")
        logger.error("  Linux: sudo apt-get install ffmpeg")
        logger.error("  Mac: brew install ffmpeg")
        return

    try:
        if args.mode == "full":
            metadata = extractor.extract_full_audio(
                video_path=args.video_path,
                movie_title=args.title,
                audio_format=args.format,
                quality=args.quality
            )
            print(f"\n✓ Extracted full audio track")
            print(f"  Duration: {metadata.duration_seconds:.2f}s")
            print(f"  File: {metadata.file_path}")
            print(f"  Hash: {metadata.file_hash}")

        elif args.mode == "segments":
            metadata_list = extractor.extract_audio_segments(
                video_path=args.video_path,
                movie_title=args.title,
                segment_duration=args.segment_duration,
                audio_format=args.format,
                quality=args.quality,
                max_segments=args.max_segments
            )
            print(f"\n✓ Extracted {len(metadata_list)} audio segments")
            print(f"  Segment duration: {args.segment_duration}s")
            print(f"  Output directory: {extractor.output_dir / extractor._sanitize_filename(args.title)}")

    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
