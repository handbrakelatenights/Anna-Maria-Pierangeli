# Anna Maria Pierangeli - Public Domain Movie NFT System

> Complete end-to-end system for processing public domain movies and minting NFTs for every frame and audio asset.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Overview

This project combines historical tribute with cutting-edge blockchain technology. Named after **Anna Maria Pierangeli** (Pier Angeli), the Italian actress who became a Hollywood star in the 1950s, this system preserves and immortalizes public domain cinema through NFT technology.

### What It Does

🎬 **Processes entire public domain movies**
- Extracts EVERY frame (100,000+ for feature films)
- Extracts ALL audio assets (full track + segments)
- Uploads to IPFS (decentralized storage)
- Mints an NFT for every single asset
- Generates comprehensive metadata

🖼️ **Creates massive NFT collections**
- 129,600 frame NFTs for a 90-minute film
- 241+ audio segment NFTs
- Blockchain-verified provenance
- Public domain documentation
- Multi-chain support

📚 **Includes curated public domain catalog**
- 10 classic films pre-configured
- Metropolis (1927)
- Night of the Living Dead (1968)
- Nosferatu (1922)
- And more...

## Demo

Watch how the system processes public domain movie frames:

https://github.com/handbrakelatenights/Anna-Maria-Pierangeli/assets/1762688975395.mov

*Example demonstration of frame extraction and processing from a public domain film.*

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/handbrakelatenights/Anna-Maria-Pierangeli.git
cd Anna-Maria-Pierangeli

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (required for audio extraction)
# Linux
sudo apt-get install ffmpeg

# Mac
brew install ffmpeg
```

### Setup

1. **Create `.env` file**:

```bash
cp .env.example .env
# Edit .env with your credentials
```

2. **Get required credentials**:
   - Wallet private key (MetaMask, etc.)
   - Infura/Alchemy RPC endpoint
   - Pinata API keys (for IPFS)

3. **Deploy NFT contract** (or use existing):
   - See `examples/example_contract.sol`
   - Deploy to testnet first (Polygon Mumbai)
   - Note the contract address

### Process Your First Movie

```bash
# Extract and mint all frames and audio
python complete_nft_pipeline.py \
  --video path/to/public_domain_movie.mp4 \
  --movie "Night of the Living Dead" \
  --year 1968 \
  --director "George A. Romero" \
  --contract 0xYourContractAddress \
  --abi-file examples/contract_abi.json \
  --network polygon_mumbai
```

**That's it!** The system will:
1. Extract all frames
2. Extract all audio
3. Upload to IPFS
4. Mint NFTs for everything
5. Generate reports

## Features

### 🎥 Frame Extraction
- Extract every frame from any video
- Multiple modes: all frames, samples, key scenes
- High-quality output (JPG, PNG)
- SHA-256 hashing for verification
- Comprehensive metadata

### 🎵 Audio Extraction
- Full audio track extraction
- Time-based segments (configurable)
- Multiple formats (MP3, WAV, FLAC, OGG)
- Frame-specific audio clips
- Professional FFmpeg integration

### 🌐 IPFS Storage
- Decentralized asset hosting
- Pinata cloud pinning
- Automatic URL generation
- Permanent storage
- Gateway access

### ⛓️ Multi-Chain NFT Minting
- **Ethereum** (Mainnet & Sepolia)
- **Polygon** (Mainnet & Mumbai)
- **Binance Smart Chain**
- ERC-721 standard
- Batch minting optimization
- Gas cost estimation

### 📊 Analytics & Reporting
- Real-time progress tracking
- Comprehensive statistics
- Gas usage monitoring
- Error logging
- Success/failure reports

## System Components

| Component | Purpose | Lines of Code |
|-----------|---------|---------------|
| `complete_nft_pipeline.py` | End-to-end orchestration | 600+ |
| `nft_minting_system.py` | Blockchain integration | 700+ |
| `movie_frame_extractor.py` | Frame extraction | 500+ |
| `audio_extractor.py` | Audio processing | 400+ |
| `public_domain_movie_catalog.py` | Movie database | 600+ |
| `movie_processing_workflow.py` | Workflow automation | 400+ |

**Total**: 3,200+ lines of production code

## Documentation

📖 **Comprehensive Guides**:
- [NFT Minting Guide](NFT_MINTING_GUIDE.md) - Complete NFT creation walkthrough
- [Movie Processing Guide](PUBLIC_DOMAIN_MOVIE_PROCESSING.md) - Frame & audio extraction
- [Quick Start Guide](QUICKSTART_MOVIE_PROCESSING.md) - 5-minute setup
- [Anna Maria Pierangeli Project](ANNA_MARIA_PIERANGELI_PROJECT.md) - Original project overview

## Use Cases

### 🎨 NFT Collections
Create complete collections from iconic films:
- Every frame as a unique NFT
- Rarity based on scene importance
- Collector sets with verifiable scarcity
- Marketplace integration

### 🏛️ Film Preservation
Blockchain-verified archival:
- Immutable historical record
- Decentralized storage
- Frame-by-frame documentation
- Public domain verification

### 📚 Educational
Teaching and research:
- Film analysis tools
- Frame-by-frame study
- Audio segmentation
- Metadata generation

### 💰 Commercial
Legal revenue generation:
- NFT sales
- Collection licensing
- Derivative works
- Public domain monetization

## Cost Estimates

### 90-Minute Feature Film

| Network | Frames | Audio | Total NFTs | Cost |
|---------|--------|-------|------------|------|
| Polygon Mumbai | 129,600 | 241 | 129,841 | **FREE** (testnet) |
| Polygon Mainnet | 129,600 | 241 | 129,841 | ~$400-500 |
| Ethereum Mainnet | 129,600 | 241 | 129,841 | ~$1,000-2,000+ |

**Recommendation**: Start with Polygon Mumbai (free testnet), then deploy to Polygon Mainnet for production.

### Short Film (10 minutes)

| Network | Frames | Audio | Total NFTs | Cost |
|---------|--------|-------|------------|------|
| Polygon Mainnet | 14,400 | 27 | 14,427 | ~$40-50 |
| Ethereum Mainnet | 14,400 | 27 | 14,427 | ~$110-220 |

## Example Usage

### Extract Frames Only
```bash
python movie_frame_extractor.py video.mp4 \
  --title "Metropolis" \
  --mode sample \
  --samples 1000
```

### Extract Audio Only
```bash
python audio_extractor.py video.mp4 \
  --title "Nosferatu" \
  --mode segments \
  --segment-duration 30
```

### Process Without Minting
```bash
python complete_nft_pipeline.py \
  --video movie.mp4 \
  --movie "Title" \
  --year 1927 \
  --director "Director" \
  --contract 0x... \
  --abi-file abi.json \
  --no-mint
```

### Estimate Costs
```bash
python nft_minting_system.py \
  --network polygon_mumbai \
  --estimate-cost 129600
```

### Add Movie to Catalog
```bash
python public_domain_movie_catalog.py --seed
```

## Public Domain Catalog

Pre-configured with 10 classic films:

1. **Metropolis** (1927) - Fritz Lang
2. **Night of the Living Dead** (1968) - George A. Romero
3. **The Great Train Robbery** (1903) - Edwin S. Porter
4. **His Girl Friday** (1940) - Howard Hawks
5. **Plan 9 from Outer Space** (1959) - Ed Wood
6. **The Cabinet of Dr. Caligari** (1920) - Robert Wiene
7. **A Trip to the Moon** (1902) - Georges Méliès
8. **Reefer Madness** (1936) - Louis J. Gasnier
9. **Nosferatu** (1922) - F. W. Murnau
10. **Charade** (1963) - Stanley Donen

All films include:
- Full metadata
- Public domain documentation
- Download links (Internet Archive)
- Wikipedia references

## Legal Framework

### Public Domain Verification

This system is designed for **confirmed public domain content only**.

Works may be public domain due to:
- Published before 1928 (US)
- Copyright not renewed (1928-1963)
- Copyright notice omission
- Expired copyright

**Important**:
- Verify public domain status in your jurisdiction
- Document the reason in NFT metadata
- Include source attribution
- Respect international copyright laws

### NFT Considerations

✅ **You CAN**:
- Mint NFTs from public domain frames
- Sell NFTs commercially
- Create derivative works
- Use for educational purposes

❌ **You CANNOT**:
- Claim original authorship
- Prevent others from using same content
- Ignore jurisdiction-specific laws
- Mint copyrighted content

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Input: Video File                        │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
        ▼                    ▼
┌──────────────┐    ┌──────────────┐
│    Frame     │    │    Audio     │
│  Extraction  │    │  Extraction  │
└──────┬───────┘    └──────┬───────┘
       │                   │
       │  ┌────────────────┘
       │  │
       ▼  ▼
┌─────────────────┐
│  IPFS Upload    │
│   (Pinata)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  NFT Minting    │
│  (Blockchain)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Reports &     │
│   Metadata      │
└─────────────────┘
```

## Performance

### Frame Extraction
- Speed: ~1,000 frames/minute
- 90-min movie: ~130 minutes extraction
- Storage: 15-35 GB per feature film

### Audio Extraction
- Speed: Near real-time
- 90-min movie: ~5 minutes extraction
- Storage: 100-300 MB per feature film

### NFT Minting
- Speed: ~10 NFTs/batch (configurable)
- 129,600 NFTs: ~24-48 hours
- Includes delays to avoid rate limits

## System Requirements

### Minimum
- Python 3.8+
- 4GB RAM
- 50GB disk space
- FFmpeg
- Internet connection

### Recommended
- Python 3.10+
- 16GB RAM
- 500GB SSD
- Fast internet
- GPU (for large-scale processing)

## Troubleshooting

### Common Issues

**"FFmpeg not found"**
```bash
# Install FFmpeg first
sudo apt-get install ffmpeg  # Linux
brew install ffmpeg          # Mac
```

**"Insufficient funds"**
```bash
# Get testnet tokens
# Polygon Mumbai: https://faucet.polygon.technology/
# Ethereum Sepolia: https://sepoliafaucet.com/
```

**"IPFS upload failed"**
- Check Pinata API keys in `.env`
- Verify file size limits
- Check internet connection

**"Transaction failed"**
- Increase gas price
- Check wallet balance
- Verify contract address

See [NFT_MINTING_GUIDE.md](NFT_MINTING_GUIDE.md#troubleshooting) for more solutions.

## Roadmap

### Current (v1.0)
- ✅ Complete frame extraction
- ✅ Audio extraction
- ✅ IPFS integration
- ✅ Multi-chain NFT minting
- ✅ Batch processing
- ✅ Comprehensive documentation

### Planned (v1.1)
- [ ] ERC-1155 batch minting
- [ ] Automated rarity calculation
- [ ] Web UI for processing
- [ ] Marketplace integration
- [ ] Collection analytics

### Future (v2.0)
- [ ] AI scene classification
- [ ] Character detection
- [ ] Automated metadata enhancement
- [ ] DAO governance
- [ ] Multi-language support

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

Areas for contribution:
- Additional public domain films
- Performance optimizations
- UI/UX improvements
- Documentation updates
- Bug fixes

## Anna Maria Pierangeli

This project is named in honor of **Anna Maria Pierangeli** (1932-1971), known professionally as **Pier Angeli**. She was an Italian actress who became one of Hollywood's brightest stars in the 1950s, starring in films like "Teresa" (1951), "Somebody Up There Likes Me" (1956), and many others.

Her story represents:
- The golden age of cinema
- International artistic collaboration
- The preservation of film history
- The cultural impact of classic Hollywood

By using blockchain technology to preserve and celebrate public domain cinema, we honor the legacy of artists like Anna Maria Pierangeli who helped shape the film industry.

## Resources

### External Links
- [Internet Archive Movies](https://archive.org/details/movies)
- [Public Domain Review](https://publicdomainreview.org/)
- [Copyright Guide](https://copyright.cornell.edu/publicdomain)
- [OpenZeppelin Contracts](https://openzeppelin.com/contracts/)
- [Pinata IPFS](https://pinata.cloud/)

### Blockchain Networks
- [Polygon Mumbai Faucet](https://faucet.polygon.technology/)
- [Ethereum Sepolia Faucet](https://sepoliafaucet.com/)
- [OpenSea](https://opensea.io/)
- [Polygonscan](https://polygonscan.com/)

### Development Tools
- [Remix IDE](https://remix.ethereum.org/)
- [Hardhat](https://hardhat.org/)
- [Web3.py Docs](https://web3py.readthedocs.io/)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)

## License

MIT License - See LICENSE file for details

**Note**: The license applies to the code in this repository. Public domain films processed by this system have their own individual public domain status.

## Support

- **Issues**: [GitHub Issues](https://github.com/handbrakelatenights/Anna-Maria-Pierangeli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/handbrakelatenights/Anna-Maria-Pierangeli/discussions)
- **Documentation**: See `docs/` directory

## Acknowledgments

- Anna Maria Pierangeli (Pier Angeli) - Inspiration
- Internet Archive - Public domain film source
- OpenZeppelin - Smart contract framework
- Pinata - IPFS infrastructure
- The public domain community

---

**Made with ❤️ for film preservation and blockchain innovation**

**Start minting your movie collection today!** 🎬→🖼️→⛓️
