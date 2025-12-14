# ============================================
# FLASHCARD GENERATOR
# ============================================

# ============================================
# IMPORTS & SETUP
# ============================================

import sqlite3
import random
import json
import os
import asyncio
import argparse
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY environment variable is not set.")
    print("Please set it by running:")
    print('  export OPENAI_API_KEY="your-api-key-here"')
    print("\nOr add it to your shell profile (~/.zshrc or ~/.bashrc)")
    exit(1)

client = AsyncOpenAI(api_key=api_key)

# PATHS
JEOPARDY_DB = "./data/jeopardy.db"
FLASHCARD_DB = "./data/flashcards.db"

STARTER_CATEGORIES = [
    "Life Sciences",
    "Physical Sciences",
    "Ancient & Medieval History",
    "Modern History",
    "World Geography",
    "Literature & Language",
    "Visual Arts & Music",
    "Mathematics",
    "Sports & Games",
    "Entertainment & Media"
]

# ============================================
# DATABASE INITIALIZATION
# ============================================

def initialize_flashcard_db():
    """
    Creates flashcards.db with three tables:

    categories:
      - id INTEGER PRIMARY KEY AUTOINCREMENT
      - name TEXT UNIQUE NOT NULL
      - created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    flashcards:
      - id INTEGER PRIMARY KEY AUTOINCREMENT
      - category_id INTEGER
      - question TEXT NOT NULL
      - answer TEXT NOT NULL
      - original_clue_id INTEGER NOT NULL
      - created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      - FOREIGN KEY (category_id) REFERENCES categories(id)

    processed_clues:
      - clue_id INTEGER PRIMARY KEY
      - processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    """

    conn = sqlite3.connect(FLASHCARD_DB)
    cursor = conn.cursor()

    # Create categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create flashcards table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            original_clue_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)

    # Create processed_clues table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_clues (
            clue_id INTEGER PRIMARY KEY,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert starter categories (ignore if already exist)
    for category in STARTER_CATEGORIES:
        try:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (category,))
        except sqlite3.IntegrityError:
            # Category already exists, skip
            pass

    conn.commit()
    conn.close()
    print(f"✓ Flashcard database initialized at {FLASHCARD_DB}")

# ============================================
# CATEGORY MANAGEMENT
# ============================================

def get_all_categories():
    """
    Returns list of all category names

    Returns:
        list of str: ['Life Sciences', 'Physical Sciences', ...]
    """

    conn = sqlite3.connect(FLASHCARD_DB)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM categories ORDER BY name")
    categories = [row[0] for row in cursor.fetchall()]

    conn.close()
    return categories

def add_category(category_name):
    """
    Adds new category to database if it doesn't exist

    Args:
        category_name (str): Name of category to add

    Returns:
        int: category_id
    """

    conn = sqlite3.connect(FLASHCARD_DB)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
        conn.commit()
        category_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        # Category already exists, get its id
        cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
        category_id = cursor.fetchone()[0]

    conn.close()
    return category_id

def get_category_id(category_name):
    """
    Get the id for a category name

    Args:
        category_name (str): Name of category

    Returns:
        int: category_id or None if not found
    """

    conn = sqlite3.connect(FLASHCARD_DB)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else None

# ============================================
# CLUE PROCESSING
# ============================================

def get_random_unprocessed_clue():
    """
    Gets a random clue from jeopardy.db that hasn't been processed

    Returns:
        dict: {
            'clue_id': int,
            'jeopardy_category': str,  # Original Jeopardy category
            'clue': str,
            'answer': str,
            'value': str
        }
        or None if no unprocessed clues remain
    """

    # Connect to jeopardy.db
    jeopardy_conn = sqlite3.connect(JEOPARDY_DB)
    jeopardy_cursor = jeopardy_conn.cursor()

    # Connect to flashcard.db to check processed clues
    flashcard_conn = sqlite3.connect(FLASHCARD_DB)
    flashcard_cursor = flashcard_conn.cursor()

    # Get all processed clue ids
    flashcard_cursor.execute("SELECT clue_id FROM processed_clues")
    processed_ids = {row[0] for row in flashcard_cursor.fetchall()}

    # Get all clue ids from jeopardy.db
    jeopardy_cursor.execute("SELECT id FROM clues")
    all_ids = [row[0] for row in jeopardy_cursor.fetchall()]

    # Find unprocessed ids
    unprocessed_ids = [clue_id for clue_id in all_ids if clue_id not in processed_ids]

    if not unprocessed_ids:
        jeopardy_conn.close()
        flashcard_conn.close()
        return None

    # Randomly select one
    selected_id = random.choice(unprocessed_ids)

    # Fetch full clue data
    jeopardy_cursor.execute(
        "SELECT id, category, clue, answer, value FROM clues WHERE id = ?",
        (selected_id,)
    )
    row = jeopardy_cursor.fetchone()

    jeopardy_conn.close()
    flashcard_conn.close()

    return {
        'clue_id': row[0],
        'jeopardy_category': row[1],
        'clue': row[2],
        'answer': row[3],
        'value': row[4]
    }

def is_clue_processed(clue_id):
    """
    Check if a clue has already been processed

    Args:
        clue_id (int): ID from jeopardy.db

    Returns:
        bool: True if already processed
    """

    conn = sqlite3.connect(FLASHCARD_DB)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM processed_clues WHERE clue_id = ?", (clue_id,))
    count = cursor.fetchone()[0]

    conn.close()
    return count > 0

def get_batch_unprocessed_clues(batch_size):
    """
    Gets a batch of random unprocessed clues from jeopardy.db

    Args:
        batch_size (int): Number of clues to fetch

    Returns:
        list of dict: List of clue data dictionaries, each containing:
            {
                'clue_id': int,
                'jeopardy_category': str,
                'clue': str,
                'answer': str,
                'value': str
            }
    """

    # Connect to jeopardy.db
    jeopardy_conn = sqlite3.connect(JEOPARDY_DB)
    jeopardy_cursor = jeopardy_conn.cursor()

    # Connect to flashcard.db to check processed clues
    flashcard_conn = sqlite3.connect(FLASHCARD_DB)
    flashcard_cursor = flashcard_conn.cursor()

    # Get all processed clue ids
    flashcard_cursor.execute("SELECT clue_id FROM processed_clues")
    processed_ids = {row[0] for row in flashcard_cursor.fetchall()}

    # Get all clue ids from jeopardy.db
    jeopardy_cursor.execute("SELECT id FROM clues")
    all_ids = [row[0] for row in jeopardy_cursor.fetchall()]

    # Find unprocessed ids
    unprocessed_ids = [clue_id for clue_id in all_ids if clue_id not in processed_ids]

    if not unprocessed_ids:
        jeopardy_conn.close()
        flashcard_conn.close()
        return []

    # Randomly select batch
    selected_ids = random.sample(unprocessed_ids, min(batch_size, len(unprocessed_ids)))

    # Fetch full clue data for selected ids
    clues = []
    for clue_id in selected_ids:
        jeopardy_cursor.execute(
            "SELECT id, category, clue, answer, value FROM clues WHERE id = ?",
            (clue_id,)
        )
        row = jeopardy_cursor.fetchone()
        clues.append({
            'clue_id': row[0],
            'jeopardy_category': row[1],
            'clue': row[2],
            'answer': row[3],
            'value': row[4]
        })

    jeopardy_conn.close()
    flashcard_conn.close()

    return clues

# ============================================
# LLM FLASHCARD GENERATION
# ============================================

async def generate_flashcard(clue_data, existing_categories):
    """
    Uses OpenAI API to generate enriched flashcard content

    Args:
        clue_data (dict): {
            'jeopardy_category': str,
            'clue': str,
            'answer': str,
            'value': str
        }
        existing_categories (list): List of existing category names

    Returns:
        dict: {
            'question': str,
            'answer': str,  # Answer with bullet points
            'category': str  # Existing category or new one
        }
    """

    system_message = f"""You are a flashcard generator for Jeopardy-style trivia questions.
Your job is to:
1. Create a clear, standalone jeopardy style question based on the Jeopardy clue. The question should be specific and informative.
2. Provide the answer followed by 3-5 related educational bullet points
3. Assign the flashcard to an existing category OR create a new medium-specificity category

IMPORTANT - Avoid vague questions:
- DO NOT create simple "What is X?" questions that just identify a name or term (e.g., "What is Park Avenue?")
- DO NOT create ambiguous questions where the answer could refer to multiple things without context (e.g., "What is spurs?" - team vs. riding equipment)
- DO ensure questions include enough context from the original clue to make them educational and specific
- DO make questions that test knowledge of facts, events, or concepts, not just definitions
- GOOD example: "What New York street, originally called 4th Avenue, was renamed in 1860 and became known for affluent residences?"
- BAD example: "What is Park Avenue?"

Format your response as JSON:
{{
  "question": "What is...",
  "answer": "The answer\\n\\n• Bullet point 1\\n• Bullet point 2\\n• Bullet point 3",
  "category": "Life Sciences"  // or "NEW: Mythology"
}}

Existing categories: {', '.join(existing_categories)}

Only create a NEW category if the clue doesn't fit well in existing ones.
New categories should be medium specificity (e.g., "American Politics", "Classical Music", "Mythology")
not too broad (e.g., "History") or too narrow (e.g., "17th Century French Literature")."""

    user_message = f"""Original Jeopardy Category: {clue_data['jeopardy_category']}
Clue: {clue_data['clue']}
Answer: {clue_data['answer']}
Value: {clue_data['value']}"""

    response = await client.chat.completions.create(
        model="gpt-5.2",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        response_format={"type": "json_object"},
        temperature=0.7
    )

    result = json.loads(response.choices[0].message.content)
    return result

# ============================================
# FLASHCARD STORAGE
# ============================================

def add_flashcard(question, answer, category_name, original_clue_id):
    """
    Adds flashcard to database and marks clue as processed

    Args:
        question (str): The flashcard question
        answer (str): The answer with bullet points
        category_name (str): Category name (may start with "NEW: ")
        original_clue_id (int): ID from jeopardy.db
    """

    # Handle new category
    if category_name.startswith("NEW: "):
        category_name = category_name[5:]  # Strip "NEW: " prefix

    # Get or create category
    category_id = get_category_id(category_name)
    if category_id is None:
        category_id = add_category(category_name)

    # Add flashcard and mark as processed
    conn = sqlite3.connect(FLASHCARD_DB)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO flashcards (category_id, question, answer, original_clue_id) VALUES (?, ?, ?, ?)",
        (category_id, question, answer, original_clue_id)
    )

    cursor.execute(
        "INSERT INTO processed_clues (clue_id) VALUES (?)",
        (original_clue_id,)
    )

    conn.commit()
    conn.close()

# ============================================
# STATISTICS & REPORTING
# ============================================

def get_stats():
    """
    Returns statistics about the flashcard database

    Returns:
        dict: {
            'total_flashcards': int,
            'total_categories': int,
            'processed_clues': int,
            'remaining_clues': int,
            'flashcards_per_category': list of (category, count)
        }
    """

    # Connect to flashcard db
    flashcard_conn = sqlite3.connect(FLASHCARD_DB)
    flashcard_cursor = flashcard_conn.cursor()

    # Count flashcards
    flashcard_cursor.execute("SELECT COUNT(*) FROM flashcards")
    total_flashcards = flashcard_cursor.fetchone()[0]

    # Count categories
    flashcard_cursor.execute("SELECT COUNT(*) FROM categories")
    total_categories = flashcard_cursor.fetchone()[0]

    # Count processed clues
    flashcard_cursor.execute("SELECT COUNT(*) FROM processed_clues")
    processed_clues = flashcard_cursor.fetchone()[0]

    # Get flashcards per category
    flashcard_cursor.execute("""
        SELECT c.name, COUNT(f.id)
        FROM categories c
        LEFT JOIN flashcards f ON c.id = f.category_id
        GROUP BY c.name
        ORDER BY COUNT(f.id) DESC, c.name
    """)
    flashcards_per_category = flashcard_cursor.fetchall()

    flashcard_conn.close()

    # Connect to jeopardy db to count total clues
    jeopardy_conn = sqlite3.connect(JEOPARDY_DB)
    jeopardy_cursor = jeopardy_conn.cursor()

    jeopardy_cursor.execute("SELECT COUNT(*) FROM clues")
    total_clues = jeopardy_cursor.fetchone()[0]

    jeopardy_conn.close()

    remaining_clues = total_clues - processed_clues

    return {
        'total_flashcards': total_flashcards,
        'total_categories': total_categories,
        'processed_clues': processed_clues,
        'remaining_clues': remaining_clues,
        'flashcards_per_category': flashcards_per_category
    }

# ============================================
# MAIN PIPELINE
# ============================================

def generate_batch(batch_size=20, max_concurrent=10):
    """
    Main function to generate a batch of flashcards

    Args:
        batch_size (int): Number of flashcards to generate
        max_concurrent (int): Maximum number of concurrent API calls (default: 10)
    """

    print(f"\n{'='*50}")
    print(f"FLASHCARD GENERATION - Batch Size: {batch_size}")
    print(f"{'='*50}\n")

    # Print starting stats
    stats = get_stats()
    print(f"Starting Statistics:")
    print(f"  Total flashcards: {stats['total_flashcards']}")
    print(f"  Total categories: {stats['total_categories']}")
    print(f"  Processed clues: {stats['processed_clues']}")
    print(f"  Remaining clues: {stats['remaining_clues']}")
    print()

    # Fetch batch of unprocessed clues
    clues = get_batch_unprocessed_clues(batch_size)

    if not clues:
        print(f"\n⚠ No more unprocessed clues available!")
        return

    print(f"Fetched {len(clues)} clues to process")
    print(f"Using up to {max_concurrent} concurrent API calls\n")

    # Get existing categories once (shared across all generations)
    existing_categories = get_all_categories()

    # Run async generation
    flashcards = asyncio.run(_generate_flashcards_parallel(clues, existing_categories, max_concurrent))

    # Write results to database sequentially
    generated_count = 0
    for i, (clue_data, flashcard) in enumerate(zip(clues, flashcards)):
        print(f"[{i+1}/{len(clues)}] Processing clue #{clue_data['clue_id']}...")
        print(f"  Original category: {clue_data['jeopardy_category']}")
        print(f"  Clue: {clue_data['clue'][:80]}...")

        if flashcard is None:
            print(f"  ✗ Error generating flashcard")
            print()
            continue

        try:
            # Add to database
            add_flashcard(
                flashcard['question'],
                flashcard['answer'],
                flashcard['category'],
                clue_data['clue_id']
            )

            generated_count += 1
            print(f"  ✓ Generated flashcard")
            print(f"    Question: {flashcard['question'][:80]}...")
            print(f"    Category: {flashcard['category']}")
            print()

        except Exception as e:
            print(f"  ✗ Error saving flashcard: {e}")
            print()
            continue

    # Print completion message
    print(f"\n{'='*50}")
    print(f"BATCH COMPLETE - Generated {generated_count} flashcards")
    print(f"{'='*50}\n")

    # Print final stats
    stats = get_stats()
    print(f"Final Statistics:")
    print(f"  Total flashcards: {stats['total_flashcards']}")
    print(f"  Total categories: {stats['total_categories']}")
    print(f"  Processed clues: {stats['processed_clues']}")
    print(f"  Remaining clues: {stats['remaining_clues']}")
    print()
    print(f"Flashcards per category:")
    for cat, count in stats['flashcards_per_category']:
        if count > 0:
            print(f"  {cat}: {count}")

async def _generate_flashcards_parallel(clues, existing_categories, max_concurrent):
    """
    Helper function to generate flashcards in parallel using async/await

    Args:
        clues (list): List of clue data dictionaries
        existing_categories (list): List of existing category names
        max_concurrent (int): Maximum number of concurrent API calls

    Returns:
        list: List of flashcard dicts (or None for errors)
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def generate_with_semaphore(clue_data):
        async with semaphore:
            try:
                return await generate_flashcard(clue_data, existing_categories)
            except Exception as e:
                print(f"  ✗ Error generating flashcard for clue #{clue_data['clue_id']}: {e}")
                return None

    # Generate all flashcards in parallel (limited by semaphore)
    print(f"Generating {len(clues)} flashcards in parallel...\n")
    flashcards = await asyncio.gather(*[generate_with_semaphore(clue) for clue in clues])

    return flashcards

# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate Jeopardy flashcards using OpenAI API')
    parser.add_argument(
        '--batch-size',
        type=int,
        default=200,
        help='Number of flashcards to generate (default: 200)'
    )
    parser.add_argument(
        '--max-concurrent',
        type=int,
        default=10,
        help='Maximum number of concurrent API calls (default: 10)'
    )
    args = parser.parse_args()

    # Initialize database (safe to run multiple times)
    initialize_flashcard_db()

    # Generate batch of flashcards
    generate_batch(batch_size=args.batch_size, max_concurrent=args.max_concurrent)

    # Final statistics already printed by generate_batch
