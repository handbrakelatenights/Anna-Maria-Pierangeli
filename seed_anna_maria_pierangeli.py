"""
Seed script to add Anna Maria Pierangeli article to the News database.

Anna Maria Pierangeli (1932-1971), known professionally as Pier Angeli,
was an Italian actress who became a Hollywood star in the 1950s.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path
from datetime import datetime
import uuid

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

# Article data about Anna Maria Pierangeli
ANNA_MARIA_ARTICLE = {
    "id": str(uuid.uuid4()),
    "title": "Anna Maria Pierangeli: The Italian Star Who Captivated Hollywood",
    "author": "NewsHub Editorial Team",
    "category": "Cinema History",
    "summary": "Exploring the life and legacy of Anna Maria Pierangeli, better known as Pier Angeli, the Italian actress who became one of Hollywood's brightest stars in the 1950s.",
    "content": """Anna Maria Pierangeli, born on June 19, 1932, in Cagliari, Sardinia, Italy, became one of the most celebrated actresses of Hollywood's Golden Age under her stage name, Pier Angeli.

EARLY LIFE AND CAREER BEGINNINGS

Born into a family that would later escape to Rome during World War II, Anna Maria showed an early talent for performance. Her breakthrough came when she was discovered by director Léonide Moguy, who cast her in the Italian film "Tomorrow Is Too Late" (1950). Her natural beauty and emotional depth caught the attention of Hollywood scouts.

HOLLYWOOD STARDOM

MGM Studios signed Pierangeli in 1950, giving her the stage name "Pier Angeli." Her American debut came in "Teresa" (1951), a performance that earned her the Golden Globe Award for New Star of the Year. This role showcased her ability to convey deep emotion and vulnerability, traits that would define her career.

Throughout the 1950s, Angeli starred in numerous prestigious productions including:
- "The Devil Makes Three" (1952)
- "The Story of Three Loves" (1953)
- "The Silver Chalice" (1954) alongside Paul Newman
- "Somebody Up There Likes Me" (1956) with Paul Newman
- "The Vintage" (1957)

PERSONAL LIFE AND CHALLENGES

Angeli's personal life was marked by both romance and tragedy. Her relationship with James Dean in the early 1950s became legendary in Hollywood lore, though family pressure led her to marry singer Vic Damone instead in 1954. The marriage ended in divorce in 1959.

Despite her professional success, Angeli struggled with the pressures of Hollywood and personal relationships. She married Italian composer Armando Trovajoli in 1962, but this marriage also ended in divorce.

LATER CAREER AND LEGACY

During the 1960s, Angeli continued to work in both American and European cinema, though the roles became less prominent. She appeared in various television shows and international productions, demonstrating her versatility as an actress.

Tragically, Anna Maria Pierangeli died on September 10, 1971, at the age of 39 in Beverly Hills, California. Her death was ruled as accidental due to a barbiturate overdose.

CULTURAL IMPACT

Pier Angeli remains a symbol of the international appeal of 1950s Hollywood cinema. Her performances brought a European sensibility to American films, and her natural beauty and talent made her one of the era's most memorable actresses.

Film historians often cite her work as exemplifying the transition period in Hollywood when international stars began to reshape American cinema. Her relationship with James Dean has become part of Hollywood mythology, symbolizing the era's romantic idealism.

REMEMBERING A STAR

Today, Anna Maria Pierangeli is remembered not only for her beauty but for her genuine talent and the emotional authenticity she brought to every role. Her films continue to be studied and appreciated by new generations of cinema enthusiasts, ensuring that her legacy endures.

Her story serves as both inspiration and cautionary tale about the pressures of fame in Hollywood's Golden Age, making her one of the most compelling figures in cinema history.""",
    "image_base64": None,  # Can be added if an image is available
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}


async def seed_database():
    """Seed the database with Anna Maria Pierangeli article."""
    try:
        # Connect to MongoDB
        mongo_url = os.environ.get('MONGO_URL')
        if not mongo_url:
            raise ValueError("MONGO_URL environment variable not set")

        db_name = os.environ.get('DB_NAME', 'newsdb')

        print(f"Connecting to MongoDB...")
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]

        # Check if article already exists
        existing = await db.articles.find_one({"title": ANNA_MARIA_ARTICLE["title"]})

        if existing:
            print("Article about Anna Maria Pierangeli already exists in database.")
            print(f"Article ID: {existing['id']}")
        else:
            # Insert the article
            await db.articles.insert_one(ANNA_MARIA_ARTICLE)
            print("Successfully added Anna Maria Pierangeli article to database!")
            print(f"Article ID: {ANNA_MARIA_ARTICLE['id']}")
            print(f"Title: {ANNA_MARIA_ARTICLE['title']}")
            print(f"Category: {ANNA_MARIA_ARTICLE['category']}")

        # Close connection
        client.close()
        print("\nDatabase connection closed.")

    except Exception as e:
        print(f"Error seeding database: {e}")
        raise


def main():
    """Main entry point."""
    print("=" * 80)
    print("Anna Maria Pierangeli Article Seed Script")
    print("=" * 80)
    print()

    asyncio.run(seed_database())

    print()
    print("=" * 80)
    print("Seed process completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
