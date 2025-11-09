"""
Public Domain Movie Catalog System

This module manages a catalog of public domain movies and integrates
with the News application database to create articles and video entries
for public domain films.

Features:
- Movie metadata management
- Integration with Internet Archive
- Automatic article generation
- Frame extraction coordination
- NFT metadata preparation
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path
from datetime import datetime
import uuid
from typing import List, Dict, Optional
import json
import aiohttp
import logging
from dataclasses import dataclass, asdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')


@dataclass
class PublicDomainMovie:
    """Represents a public domain movie."""
    title: str
    year: int
    director: str
    description: str
    public_domain_reason: str
    duration_minutes: Optional[int] = None
    genre: Optional[str] = None
    cast: Optional[List[str]] = None
    source_url: Optional[str] = None
    archive_url: Optional[str] = None
    wikipedia_url: Optional[str] = None
    imdb_id: Optional[str] = None
    country: Optional[str] = "USA"
    language: Optional[str] = "English"


# Curated list of notable public domain movies
PUBLIC_DOMAIN_MOVIES = [
    PublicDomainMovie(
        title="Metropolis",
        year=1927,
        director="Fritz Lang",
        genre="Science Fiction",
        duration_minutes=153,
        country="Germany",
        description="A visionary science fiction masterpiece set in a futuristic urban dystopia. Directed by Fritz Lang, this German expressionist film depicts a divided society where wealthy industrialists rule from high-rise towers while workers toil underground. The story follows Freder, the son of the city's ruler, who discovers the harsh reality of the workers' lives and falls in love with Maria, a prophet figure who preaches peace between classes.",
        public_domain_reason="Copyright expired; published before 1928",
        cast=["Alfred Abel", "Gustav Fröhlich", "Brigitte Helm"],
        archive_url="https://archive.org/details/Metropolis_1927",
        wikipedia_url="https://en.wikipedia.org/wiki/Metropolis_(1927_film)"
    ),
    PublicDomainMovie(
        title="Night of the Living Dead",
        year=1968,
        director="George A. Romero",
        genre="Horror",
        duration_minutes=96,
        description="The film that defined the modern zombie genre. A group of people barricade themselves in an old farmhouse to remain safe from flesh-eating zombies. George Romero's groundbreaking horror film introduced the concept of the modern zombie and featured revolutionary social commentary for its time.",
        public_domain_reason="Copyright notice omission",
        cast=["Duane Jones", "Judith O'Dea", "Karl Hardman"],
        archive_url="https://archive.org/details/night_of_the_living_dead",
        wikipedia_url="https://en.wikipedia.org/wiki/Night_of_the_Living_Dead"
    ),
    PublicDomainMovie(
        title="The Great Train Robbery",
        year=1903,
        director="Edwin S. Porter",
        genre="Western/Action",
        duration_minutes=12,
        description="One of the first narrative films and a landmark in cinema history. This Western silent film depicts a dramatic train robbery and the subsequent pursuit of the outlaws. Its innovative use of cross-cutting, location shooting, and camera movement influenced the development of narrative filmmaking.",
        public_domain_reason="Published before 1928",
        cast=["Gilbert M. Anderson", "George Barnes", "Justus D. Barnes"],
        archive_url="https://archive.org/details/TheGreatTrainRobbery",
        wikipedia_url="https://en.wikipedia.org/wiki/The_Great_Train_Robbery_(1903_film)"
    ),
    PublicDomainMovie(
        title="His Girl Friday",
        year=1940,
        director="Howard Hawks",
        genre="Comedy/Romance",
        duration_minutes=92,
        description="A fast-paced screwball comedy featuring rapid-fire dialogue and stellar performances. Starring Cary Grant and Rosalind Russell, the film follows a newspaper editor trying to lure his ex-wife and former star reporter away from her planned marriage. Known for its sophisticated wit and overlapping dialogue.",
        public_domain_reason="Copyright not renewed",
        cast=["Cary Grant", "Rosalind Russell", "Ralph Bellamy"],
        archive_url="https://archive.org/details/HisGirlFriday",
        wikipedia_url="https://en.wikipedia.org/wiki/His_Girl_Friday"
    ),
    PublicDomainMovie(
        title="Plan 9 from Outer Space",
        year=1959,
        director="Ed Wood",
        genre="Science Fiction/Horror",
        duration_minutes=79,
        description="Often called 'the worst movie ever made,' this cult classic has gained a devoted following. Aliens implement 'Plan 9,' a scheme to resurrect Earth's dead to prevent humanity from creating a doomsday weapon. Despite its numerous flaws, the film has become a beloved piece of camp cinema history.",
        public_domain_reason="Copyright not renewed",
        cast=["Bela Lugosi", "Vampira", "Tor Johnson"],
        archive_url="https://archive.org/details/Plan9FromOuterSpace",
        wikipedia_url="https://en.wikipedia.org/wiki/Plan_9_from_Outer_Space"
    ),
    PublicDomainMovie(
        title="The Cabinet of Dr. Caligari",
        year=1920,
        director="Robert Wiene",
        genre="Horror/Thriller",
        duration_minutes=76,
        country="Germany",
        description="A landmark of German Expressionist cinema featuring twisted sets and dramatic shadows. The film tells the story of a mysterious hypnotist who uses a somnambulist to commit murders. Its unique visual style and twist ending have influenced filmmakers for over a century.",
        public_domain_reason="Published before 1928",
        cast=["Werner Krauss", "Conrad Veidt", "Friedrich Feher"],
        archive_url="https://archive.org/details/TheCabinetOfDr.Caligari",
        wikipedia_url="https://en.wikipedia.org/wiki/The_Cabinet_of_Dr._Caligari"
    ),
    PublicDomainMovie(
        title="A Trip to the Moon",
        year=1902,
        director="Georges Méliès",
        genre="Science Fiction/Fantasy",
        duration_minutes=14,
        country="France",
        description="One of the first science fiction films and a masterpiece of early cinema. A group of astronomers travel to the moon in a cannon-propelled capsule. Famous for the iconic image of the rocket landing in the moon's eye, this hand-colored film demonstrated the potential of cinema for fantasy and spectacle.",
        public_domain_reason="Published before 1928",
        cast=["Georges Méliès", "Victor André", "Bleuette Bernon"],
        archive_url="https://archive.org/details/TheTripToTheMoon",
        wikipedia_url="https://en.wikipedia.org/wiki/A_Trip_to_the_Moon"
    ),
    PublicDomainMovie(
        title="Reefer Madness",
        year=1936,
        director="Louis J. Gasnier",
        genre="Drama/Propaganda",
        duration_minutes=66,
        description="Originally intended as a morality tale warning about the dangers of marijuana, this film has become a cult classic for its over-the-top portrayal of cannabis use. The melodramatic plot shows teenagers descending into madness, violence, and death after trying marijuana. Now viewed as unintentional comedy.",
        public_domain_reason="Copyright not renewed",
        cast=["Dorothy Short", "Kenneth Craig", "Lillian Miles"],
        archive_url="https://archive.org/details/ReeferMadness",
        wikipedia_url="https://en.wikipedia.org/wiki/Reefer_Madness"
    ),
    PublicDomainMovie(
        title="Nosferatu",
        year=1922,
        director="F. W. Murnau",
        genre="Horror",
        duration_minutes=94,
        country="Germany",
        description="An unauthorized adaptation of Bram Stoker's Dracula that became a masterpiece in its own right. This German Expressionist film tells the story of Count Orlok, a vampire who brings terror to a German town. Max Schreck's iconic portrayal of the vampire has influenced countless horror films.",
        public_domain_reason="Published before 1928",
        cast=["Max Schreck", "Gustav von Wangenheim", "Greta Schröder"],
        archive_url="https://archive.org/details/nosferatu_1922",
        wikipedia_url="https://en.wikipedia.org/wiki/Nosferatu"
    ),
    PublicDomainMovie(
        title="Charade",
        year=1963,
        director="Stanley Donen",
        genre="Romance/Thriller",
        duration_minutes=113,
        description="A sophisticated romantic thriller starring Cary Grant and Audrey Hepburn. After her husband is murdered, a woman finds herself pursued by several men who believe she has a fortune in stolen gold. Combining romance, mystery, and comedy, it's often called 'the best Hitchcock movie that Hitchcock never made.'",
        public_domain_reason="Copyright notice omission",
        cast=["Cary Grant", "Audrey Hepburn", "Walter Matthau"],
        archive_url="https://archive.org/details/Charade_1963",
        wikipedia_url="https://en.wikipedia.org/wiki/Charade_(1963_film)"
    )
]


class PublicDomainMovieCatalog:
    """Manages the catalog of public domain movies."""

    def __init__(self, db_client=None):
        """Initialize the catalog."""
        self.db_client = db_client
        self.movies = PUBLIC_DOMAIN_MOVIES

    async def generate_article_from_movie(self, movie: PublicDomainMovie) -> Dict:
        """
        Generate a news article about a public domain movie.

        Args:
            movie: PublicDomainMovie object

        Returns:
            Article dictionary ready for database insertion
        """
        # Generate comprehensive article content
        content = f"""**{movie.title}** ({movie.year}) is a {movie.genre} film directed by {movie.director}. """

        if movie.duration_minutes:
            content += f"Running {movie.duration_minutes} minutes, "

        content += f"this {movie.country} production "

        if movie.language and movie.language != "English":
            content += f"in {movie.language} "

        content += "has entered the public domain and is freely available for viewing and use.\n\n"

        content += f"**Synopsis**\n\n{movie.description}\n\n"

        if movie.cast:
            content += f"**Cast**\n\n"
            content += ", ".join(movie.cast) + "\n\n"

        content += f"**Public Domain Status**\n\n"
        content += f"This film is in the public domain due to: {movie.public_domain_reason}. "
        content += "This means anyone can freely view, download, share, and even create derivative works from this film without needing permission or paying royalties.\n\n"

        content += "**Cultural Significance**\n\n"
        content += f"{movie.title} represents an important piece of cinema history. "

        # Add genre-specific cultural notes
        if "Horror" in movie.genre:
            content += "Horror films from this era helped establish many of the genre conventions we recognize today. "
        elif "Science Fiction" in movie.genre or "Fantasy" in movie.genre:
            content += "Early science fiction films like this one demonstrated the creative potential of cinema to transport audiences to fantastic worlds. "
        elif "Comedy" in movie.genre:
            content += "Classic comedies from this period showcase timeless humor and sophisticated filmmaking techniques. "

        content += "The film's availability in the public domain ensures that future generations can study, enjoy, and build upon this cultural artifact.\n\n"

        if movie.archive_url:
            content += f"**Where to Watch**\n\n"
            content += f"The complete film is available for free viewing and download at the Internet Archive: {movie.archive_url}\n\n"

        content += "**Uses and Applications**\n\n"
        content += "As a public domain work, this film can be:\n"
        content += "- Streamed or downloaded for personal viewing\n"
        content += "- Used in educational settings\n"
        content += "- Remixed or incorporated into new creative works\n"
        content += "- Restored and preserved by archivists\n"
        content += "- Analyzed frame-by-frame for film studies\n"
        content += "- Used for commercial purposes including NFT creation\n\n"

        if movie.wikipedia_url:
            content += f"**Learn More**\n\n"
            content += f"For more information about {movie.title}, visit: {movie.wikipedia_url}"

        # Create article object
        article = {
            "id": str(uuid.uuid4()),
            "title": f"{movie.title} ({movie.year}) - Public Domain Classic",
            "author": "Public Domain Film Archive",
            "category": "Public Domain Cinema",
            "summary": f"{movie.title}, a {movie.year} {movie.genre} film directed by {movie.director}, is now in the public domain and freely available. {movie.description[:200]}...",
            "content": content,
            "image_base64": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "metadata": {
                "movie_year": movie.year,
                "director": movie.director,
                "genre": movie.genre,
                "duration_minutes": movie.duration_minutes,
                "public_domain_reason": movie.public_domain_reason,
                "archive_url": movie.archive_url,
                "wikipedia_url": movie.wikipedia_url
            }
        }

        return article

    async def seed_all_movies(self):
        """Add all public domain movies to the database."""
        if not self.db_client:
            mongo_url = os.environ.get('MONGO_URL')
            db_name = os.environ.get('DB_NAME', 'newsdb')
            self.db_client = AsyncIOMotorClient(mongo_url)
            db = self.db_client[db_name]
        else:
            db_name = os.environ.get('DB_NAME', 'newsdb')
            db = self.db_client[db_name]

        articles_added = 0
        articles_skipped = 0

        logger.info(f"Seeding {len(self.movies)} public domain movies...")

        for movie in self.movies:
            # Check if article already exists
            existing = await db.articles.find_one({"title": f"{movie.title} ({movie.year}) - Public Domain Classic"})

            if existing:
                logger.info(f"Skipping {movie.title} - already exists")
                articles_skipped += 1
                continue

            # Generate and insert article
            article = await self.generate_article_from_movie(movie)
            await db.articles.insert_one(article)
            articles_added += 1
            logger.info(f"Added article for {movie.title}")

        logger.info(f"Complete! Added {articles_added} articles, skipped {articles_skipped}")

        return {
            "articles_added": articles_added,
            "articles_skipped": articles_skipped,
            "total_movies": len(self.movies)
        }

    def export_nft_metadata(self, movie: PublicDomainMovie, output_dir: str = "nft_metadata") -> str:
        """
        Export NFT-ready metadata for a movie.

        Args:
            movie: PublicDomainMovie object
            output_dir: Directory to save metadata

        Returns:
            Path to the metadata file
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Create NFT metadata following common standards
        nft_metadata = {
            "name": f"{movie.title} ({movie.year})",
            "description": movie.description,
            "external_url": movie.wikipedia_url or movie.archive_url,
            "attributes": [
                {"trait_type": "Year", "value": movie.year},
                {"trait_type": "Director", "value": movie.director},
                {"trait_type": "Genre", "value": movie.genre},
                {"trait_type": "Country", "value": movie.country},
                {"trait_type": "Public Domain Reason", "value": movie.public_domain_reason}
            ]
        }

        if movie.duration_minutes:
            nft_metadata["attributes"].append({
                "trait_type": "Duration (minutes)",
                "value": movie.duration_minutes
            })

        if movie.cast:
            nft_metadata["attributes"].append({
                "trait_type": "Cast",
                "value": ", ".join(movie.cast)
            })

        # Save metadata
        filename = f"{movie.title.replace(' ', '_')}_{movie.year}_metadata.json"
        filepath = output_path / filename

        with open(filepath, 'w') as f:
            json.dump(nft_metadata, f, indent=2)

        logger.info(f"NFT metadata saved to {filepath}")
        return str(filepath)

    def list_movies_by_genre(self, genre: str) -> List[PublicDomainMovie]:
        """Get all movies of a specific genre."""
        return [m for m in self.movies if genre.lower() in m.genre.lower()]

    def list_movies_by_year_range(self, start_year: int, end_year: int) -> List[PublicDomainMovie]:
        """Get movies within a year range."""
        return [m for m in self.movies if start_year <= m.year <= end_year]


async def main():
    """Main entry point for catalog operations."""
    import argparse

    parser = argparse.ArgumentParser(description="Public Domain Movie Catalog")
    parser.add_argument("--seed", action="store_true", help="Seed database with all movies")
    parser.add_argument("--export-nft", help="Export NFT metadata for a movie (by title)")
    parser.add_argument("--list-genres", action="store_true", help="List all genres")
    parser.add_argument("--genre", help="List movies by genre")

    args = parser.parse_args()

    catalog = PublicDomainMovieCatalog()

    if args.seed:
        result = await catalog.seed_all_movies()
        print(f"✓ Seeded {result['articles_added']} articles")
        print(f"  Skipped {result['articles_skipped']} existing articles")

    elif args.export_nft:
        movie = next((m for m in catalog.movies if m.title.lower() == args.export_nft.lower()), None)
        if movie:
            filepath = catalog.export_nft_metadata(movie)
            print(f"✓ NFT metadata exported to {filepath}")
        else:
            print(f"Movie '{args.export_nft}' not found in catalog")

    elif args.list_genres:
        genres = set(m.genre for m in catalog.movies)
        print("Available genres:")
        for genre in sorted(genres):
            print(f"  - {genre}")

    elif args.genre:
        movies = catalog.list_movies_by_genre(args.genre)
        print(f"Movies in genre '{args.genre}':")
        for movie in movies:
            print(f"  - {movie.title} ({movie.year}) by {movie.director}")

    else:
        print(f"Public Domain Movie Catalog ({len(catalog.movies)} movies)")
        print("\nAvailable movies:")
        for movie in catalog.movies:
            print(f"  • {movie.title} ({movie.year}) - {movie.genre}")


if __name__ == "__main__":
    asyncio.run(main())
