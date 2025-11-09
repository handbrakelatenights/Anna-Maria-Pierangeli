# Public Domain Movie Processing System

## Overview

This comprehensive system provides tools for processing public domain movies, including:

- **Frame Extraction**: Extract individual frames from video files
- **Movie Cataloging**: Manage a database of public domain films
- **Metadata Generation**: Create NFT-ready metadata
- **Database Integration**: Add movie content to the News application
- **Workflow Automation**: Complete end-to-end processing pipeline

## Legal Note

This system is designed for use with films that are **confirmed to be in the public domain**. Public domain status varies by jurisdiction and users are responsible for verifying the public domain status of any content they process.

### Public Domain Criteria

Works may be in the public domain because:

- **Published before 1928** (in the United States)
- **Copyright not renewed** (for works published 1928-1963)
- **Copyright notice omission** (for pre-1989 works)
- **Expired copyright** (varies by country and publication date)

Always verify public domain status before commercial use.

## System Components

### 1. Frame Extractor (`movie_frame_extractor.py`)

Extracts frames from video files with multiple extraction modes.

**Features:**
- Extract all frames from a movie
- Sample-based extraction (extract N evenly-spaced frames)
- Scene detection (extract frames at scene changes)
- Comprehensive metadata generation
- SHA-256 hash calculation for each frame
- Progress tracking

**Usage:**

```bash
# Extract all frames (WARNING: This creates 100,000+ files for a feature film!)
python movie_frame_extractor.py video.mp4 --title "Movie Title" --mode all

# Extract 100 sample frames (recommended for most uses)
python movie_frame_extractor.py video.mp4 --title "Movie Title" --mode sample --samples 100

# Extract key scenes only
python movie_frame_extractor.py video.mp4 --title "Movie Title" --mode scenes

# Custom options
python movie_frame_extractor.py video.mp4 --title "Movie Title" \
  --mode sample \
  --samples 500 \
  --format png \
  --quality 100 \
  --output my_frames
```

**Extraction Modes:**

| Mode | Description | Use Case | Typical Output |
|------|-------------|----------|----------------|
| `all` | Every frame | Complete archival, frame-by-frame analysis | 170,000+ frames for 2-hour film @ 24fps |
| `sample` | Evenly-spaced frames | NFT collections, previews, representative samples | 100-1000 frames |
| `scenes` | Scene changes only | Key moments, highlights, scene analysis | 50-500 frames |

### 2. Movie Catalog (`public_domain_movie_catalog.py`)

Manages a curated catalog of notable public domain films.

**Features:**
- Pre-populated with 10 classic public domain movies
- Automatic article generation for News application
- NFT metadata export
- Genre and year-based filtering
- Integration with Internet Archive links

**Included Movies:**

1. **Metropolis** (1927) - German expressionist sci-fi masterpiece
2. **Night of the Living Dead** (1968) - Zombie genre foundation
3. **The Great Train Robbery** (1903) - Early narrative cinema
4. **His Girl Friday** (1940) - Screwball comedy classic
5. **Plan 9 from Outer Space** (1959) - Cult classic
6. **The Cabinet of Dr. Caligari** (1920) - German expressionist horror
7. **A Trip to the Moon** (1902) - Early sci-fi fantasy
8. **Reefer Madness** (1936) - Propaganda turned cult classic
9. **Nosferatu** (1922) - Iconic vampire film
10. **Charade** (1963) - Romantic thriller

**Usage:**

```bash
# List all movies in catalog
python public_domain_movie_catalog.py

# Seed database with all movie articles
python public_domain_movie_catalog.py --seed

# Export NFT metadata for a specific movie
python public_domain_movie_catalog.py --export-nft "Metropolis"

# List movies by genre
python public_domain_movie_catalog.py --genre "Horror"

# List all available genres
python public_domain_movie_catalog.py --list-genres
```

**Programmatic Usage:**

```python
from public_domain_movie_catalog import PublicDomainMovieCatalog

catalog = PublicDomainMovieCatalog()

# Get movies by genre
horror_movies = catalog.list_movies_by_genre("Horror")

# Get movies from a specific era
silent_era = catalog.list_movies_by_year_range(1900, 1929)

# Generate article for database
movie = catalog.movies[0]
article = await catalog.generate_article_from_movie(movie)

# Export NFT metadata
nft_file = catalog.export_nft_metadata(movie)
```

### 3. Workflow Coordinator (`movie_processing_workflow.py`)

Orchestrates the complete processing pipeline.

**Features:**
- Automated download from Internet Archive
- Frame extraction with multiple modes
- Database article creation
- NFT metadata generation
- Batch processing for entire catalog
- Collection manifest generation

**Usage:**

```bash
# List available movies
python movie_processing_workflow.py --list

# Process a single movie (all steps)
python movie_processing_workflow.py --movie "Night of the Living Dead"

# Process with specific options
python movie_processing_workflow.py --movie "Metropolis" \
  --extract-mode sample \
  --samples 200

# Process all movies in catalog
python movie_processing_workflow.py --all --extract-mode sample --samples 100

# Generate collection manifest
python movie_processing_workflow.py --manifest

# Process without certain steps
python movie_processing_workflow.py --movie "Nosferatu" \
  --no-download \
  --no-database \
  --extract-mode scenes
```

**Workflow Steps:**

1. **Download**: Fetch movie from Internet Archive (if URL available)
2. **Frame Extraction**: Extract frames based on selected mode
3. **Database**: Add article to News application database
4. **NFT Metadata**: Generate NFT-ready metadata files

## Installation

### Prerequisites

- Python 3.8+
- MongoDB (for database integration)
- FFmpeg (for advanced video processing)

### Setup

1. **Install Python dependencies:**

```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment:**

Create or update `backend/.env`:

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=newsdb
```

3. **Verify installation:**

```bash
# Test frame extractor
python movie_frame_extractor.py --help

# Test catalog
python public_domain_movie_catalog.py --list-genres

# Test workflow
python movie_processing_workflow.py --list
```

## Use Cases

### NFT Creation

Extract frames from public domain movies to create NFT collections:

```bash
# Extract 1000 representative frames
python movie_frame_extractor.py path/to/movie.mp4 \
  --title "Metropolis" \
  --mode sample \
  --samples 1000 \
  --format png \
  --quality 100

# Generate NFT metadata
python public_domain_movie_catalog.py --export-nft "Metropolis"
```

Each frame will have:
- Unique SHA-256 hash
- Timestamp metadata
- Frame number
- Source movie information
- NFT-standard metadata format

### Educational Content

Create educational articles about classic films:

```bash
# Add all movies to News database
python public_domain_movie_catalog.py --seed

# Process specific movie for article + frames
python movie_processing_workflow.py --movie "The Cabinet of Dr. Caligari"
```

### Film Archival

Preserve and catalog public domain films:

```bash
# Extract key scenes for archival
python movie_processing_workflow.py --movie "Nosferatu" \
  --extract-mode scenes

# Generate complete collection manifest
python movie_processing_workflow.py --manifest
```

### Content Analysis

Extract frames for machine learning or analysis:

```bash
# Sample frames for ML training
python movie_frame_extractor.py movie.mp4 \
  --title "Training Data" \
  --mode sample \
  --samples 5000

# Extract scene changes for analysis
python movie_frame_extractor.py movie.mp4 \
  --title "Scene Analysis" \
  --mode scenes
```

## Output Structure

### Frame Extraction Output

```
extracted_frames/
└── Movie_Title/
    ├── frame_00000000.jpg
    ├── frame_00000024.jpg
    ├── frame_00000048.jpg
    ├── ...
    ├── metadata.json          # Complete extraction metadata
    └── summary.txt            # Human-readable summary
```

### Metadata Format

**metadata.json** contains:

```json
{
  "movie": {
    "title": "Movie Title",
    "source_file": "/path/to/video.mp4",
    "total_frames": 172800,
    "fps": 24.0,
    "duration_seconds": 7200.0,
    "resolution": [1920, 1080],
    "codec": "h264"
  },
  "extraction_info": {
    "total_frames_extracted": 100,
    "extraction_date": "2025-11-09T12:00:00"
  },
  "frames": [
    {
      "frame_number": 0,
      "timestamp_ms": 0.0,
      "timestamp_formatted": "00:00:00.000",
      "file_path": "extracted_frames/Movie_Title/frame_00000000.jpg",
      "file_hash": "abc123...",
      "resolution": [1920, 1080],
      "file_size": 245678,
      "extracted_at": "2025-11-09T12:00:00"
    }
  ]
}
```

### NFT Metadata Format

```json
{
  "name": "Metropolis (1927)",
  "description": "A visionary science fiction masterpiece...",
  "external_url": "https://en.wikipedia.org/wiki/Metropolis_(1927_film)",
  "attributes": [
    {"trait_type": "Year", "value": 1927},
    {"trait_type": "Director", "value": "Fritz Lang"},
    {"trait_type": "Genre", "value": "Science Fiction"},
    {"trait_type": "Country", "value": "Germany"},
    {"trait_type": "Public Domain Reason", "value": "Copyright expired; published before 1928"}
  ]
}
```

## Best Practices

### Frame Extraction

**For NFT Collections:**
- Use `sample` mode with 100-1000 frames
- Use PNG format for highest quality
- Set quality to 100
- Extract from highest quality source available

**For Archival:**
- Use `scenes` mode for key moments
- Use JPG format (quality 95) for storage efficiency
- Include comprehensive metadata

**For Analysis:**
- Consider your specific needs (sample vs. all frames)
- Balance quantity vs. storage requirements
- Use appropriate interval for time-series analysis

### Storage Considerations

**Frame Count Estimates:**

| Movie Length | FPS | Total Frames | Storage (JPG @ 95%) | Storage (PNG) |
|--------------|-----|--------------|---------------------|---------------|
| 90 min       | 24  | 129,600      | ~15-25 GB          | ~50-80 GB    |
| 120 min      | 24  | 172,800      | ~20-35 GB          | ~65-105 GB   |
| 100 samples  | -   | 100          | ~10-50 MB          | ~30-100 MB   |
| 1000 samples | -   | 1000         | ~100-500 MB        | ~300 MB-1 GB |

**Recommendations:**
- Use `sample` mode unless you need every frame
- Start with 100 samples, increase if needed
- Monitor disk space when processing multiple movies
- Consider cloud storage for large collections

### NFT Considerations

**Legal:**
- Verify public domain status in your jurisdiction
- Be transparent about public domain source
- Don't claim original authorship
- Anyone can create NFTs from the same frames

**Technical:**
- Consider blockchain gas fees for large collections
- Batch mint when possible
- Use IPFS for decentralized storage
- Include comprehensive metadata

**Marketing:**
- Highlight historical significance
- Provide context about the film
- Create themed collections (era, genre, director)
- Consider rarity tiers (key scenes vs. random frames)

## Extending the System

### Adding New Movies

Edit `public_domain_movie_catalog.py` and add to `PUBLIC_DOMAIN_MOVIES`:

```python
PublicDomainMovie(
    title="Your Movie Title",
    year=1950,
    director="Director Name",
    genre="Genre",
    duration_minutes=90,
    country="USA",
    description="Film description...",
    public_domain_reason="Reason for public domain status",
    cast=["Actor 1", "Actor 2"],
    archive_url="https://archive.org/details/identifier",
    wikipedia_url="https://en.wikipedia.org/wiki/..."
)
```

### Custom Processing

Create custom processing scripts:

```python
from movie_frame_extractor import PublicDomainMovieProcessor
from public_domain_movie_catalog import PublicDomainMovieCatalog

processor = PublicDomainMovieProcessor()
catalog = PublicDomainMovieCatalog()

# Custom frame extraction with callback
def my_progress(current, total):
    print(f"Processing: {current}/{total}")

result = processor.extract_frames(
    video_path="my_movie.mp4",
    movie_title="My Movie",
    frame_interval=10,  # Every 10th frame
    progress_callback=my_progress
)
```

## Troubleshooting

### Common Issues

**"Failed to open video"**
- Ensure file path is correct
- Check video codec support (install FFmpeg if needed)
- Try converting to MP4 with standard codec

**"No MONGO_URL configured"**
- Set up `.env` file in backend directory
- Ensure MongoDB is running
- Check connection string format

**Download failures**
- Verify Internet Archive URL
- Check network connection
- Some archives may have different file formats (try .avi, .ogv)

**Out of disk space**
- Use `sample` mode instead of `all`
- Reduce number of samples
- Clean up previous extractions

## Performance Tips

- Use `sample` mode for initial testing
- Process movies in batches during off-hours
- Use SSD storage for frame extraction
- Monitor system resources during processing
- Consider distributed processing for large catalogs

## Future Enhancements

Potential additions:

- [ ] Audio extraction and analysis
- [ ] Subtitle/intertitle OCR
- [ ] Automated scene classification (ML)
- [ ] Color palette extraction
- [ ] Character detection and tracking
- [ ] Integration with blockchain APIs
- [ ] Web interface for processing
- [ ] Distributed processing support
- [ ] Cloud storage integration (S3, GCS)
- [ ] Advanced quality enhancement
- [ ] Format conversion tools

## Resources

### Public Domain Film Sources

- [Internet Archive](https://archive.org/details/movies) - Largest collection
- [Public Domain Review](https://publicdomainreview.org/) - Curated content
- [Wikimedia Commons](https://commons.wikimedia.org/) - Free media repository
- [Open Culture](https://www.openculture.com/freemoviesonline) - Educational focus

### Legal Information

- [Copyright Term and the Public Domain](https://copyright.cornell.edu/publicdomain)
- [Public Domain Sherpa](http://publicdomainsherpa.com/) - Public domain status guide
- [Creative Commons Public Domain Tools](https://creativecommons.org/publicdomain/)

### Technical Resources

- [OpenCV Documentation](https://docs.opencv.org/) - Computer vision library
- [Internet Archive Docs](https://archive.org/developers/) - API documentation
- [NFT Metadata Standards](https://docs.opensea.io/docs/metadata-standards)

## License

This processing system is provided as-is for processing public domain content. The code itself is part of the News1 application. The public domain films processed by this system have their own individual public domain status.

## Support

For issues or questions:
- Review this documentation
- Check the troubleshooting section
- Examine example code in each module
- Refer to source code comments

---

**Last Updated**: 2025-11-09
**Version**: 1.0
**Maintainer**: NewsHub Development Team
