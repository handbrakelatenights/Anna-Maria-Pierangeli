# Quick Start: Public Domain Movie Processing

## 5-Minute Setup

### 1. Install Dependencies

```bash
cd backend
pip install opencv-python aiohttp aiofiles
```

### 2. List Available Movies

```bash
cd ..
python public_domain_movie_catalog.py
```

You'll see 10 classic public domain movies ready to process.

### 3. Process Your First Movie

```bash
# Process "Night of the Living Dead" - extract 100 sample frames
python movie_processing_workflow.py --movie "Night of the Living Dead" \
  --extract-mode sample \
  --samples 100 \
  --no-download
```

Note: Using `--no-download` because you'll need to provide your own video file.

## Common Tasks

### Extract Frames from Your Own Video

```bash
# Simple extraction - 100 frames
python movie_frame_extractor.py path/to/video.mp4 \
  --title "My Public Domain Movie" \
  --mode sample \
  --samples 100

# High quality for NFTs
python movie_frame_extractor.py path/to/video.mp4 \
  --title "My Public Domain Movie" \
  --mode sample \
  --samples 1000 \
  --format png \
  --quality 100
```

### Add Movies to News Database

```bash
# Add all 10 movies as articles
python public_domain_movie_catalog.py --seed
```

### Generate NFT Metadata

```bash
# Create NFT metadata for Metropolis
python public_domain_movie_catalog.py --export-nft "Metropolis"

# Check the output
cat nft_metadata/Metropolis_1927_metadata.json
```

### Browse by Genre

```bash
# List all genres
python public_domain_movie_catalog.py --list-genres

# Get horror movies
python public_domain_movie_catalog.py --genre "Horror"
```

## Example: Complete NFT Collection Workflow

```bash
# 1. Download a public domain movie from archive.org
# Visit: https://archive.org/details/night_of_the_living_dead
# Download the MP4 file

# 2. Extract 500 high-quality frames
python movie_frame_extractor.py Downloads/night_of_the_living_dead.mp4 \
  --title "Night of the Living Dead" \
  --mode sample \
  --samples 500 \
  --format png \
  --quality 100

# 3. Generate NFT metadata
python public_domain_movie_catalog.py --export-nft "Night of the Living Dead"

# 4. Check the output
ls -lh extracted_frames/Night_of_the_Living_Dead/
cat nft_metadata/Night_of_the_Living_Dead_1968_metadata.json
```

## What You Get

After processing, you'll have:

**In `extracted_frames/Movie_Name/`:**
- Individual frame images (frame_00000000.jpg, etc.)
- metadata.json with complete extraction info
- summary.txt with human-readable details

**In `nft_metadata/`:**
- Movie_Name_YEAR_metadata.json with NFT-standard metadata

**In the database (if enabled):**
- Comprehensive article about the movie
- Links to source material
- Public domain information

## Next Steps

1. **Process More Movies**: Try other films from the catalog
2. **Customize Extraction**: Adjust samples, quality, format
3. **Add Your Own**: Add more public domain movies to the catalog
4. **Create NFTs**: Use the frames and metadata for blockchain minting
5. **Build Content**: Use articles in your News application

## Tips

- Start with `--samples 10` to test before extracting hundreds of frames
- Use `--no-database` if you don't have MongoDB configured
- Check disk space before extracting (1000 PNG frames ≈ 300MB-1GB)
- Verify public domain status before commercial use

## Troubleshooting

**"Failed to open video"**
```bash
# Install ffmpeg if needed
sudo apt-get install ffmpeg  # Linux
brew install ffmpeg          # Mac
```

**"No MONGO_URL configured"**
```bash
# Either set up MongoDB, or use --no-database flag
python movie_processing_workflow.py --movie "Metropolis" --no-database
```

**Need more help?**
- Read full documentation: `PUBLIC_DOMAIN_MOVIE_PROCESSING.md`
- Check module help: `python movie_frame_extractor.py --help`

## Legal Reminder

**Always verify public domain status in your jurisdiction before commercial use.**

This system is designed for confirmed public domain works. The included movies are believed to be in the U.S. public domain, but users should verify status for their specific use case and location.

---

Happy processing! 🎬
