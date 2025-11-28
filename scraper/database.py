#!/usr/bin/env python3
"""
Database module for storing Jeopardy game data in SQLite
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional


class JeopardyDatabase:
    """Handles all database operations for Jeopardy data"""

    def __init__(self, db_path: str = None):
        """
        Initialize database connection

        Args:
            db_path: Path to SQLite database file. Defaults to data/jeopardy.db
        """
        if db_path is None:
            # Default to data/jeopardy.db relative to project root
            project_root = Path(__file__).parent.parent
            db_path = project_root / "data" / "jeopardy.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        self.cursor = self.conn.cursor()

        self._create_tables()

    def _create_tables(self):
        """Create database schema if it doesn't exist"""

        # Games table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                game_id INTEGER PRIMARY KEY,
                show_number INTEGER,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                air_date TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Add show_number column if it doesn't exist (for existing databases)
        try:
            self.cursor.execute("SELECT show_number FROM games LIMIT 1")
        except sqlite3.OperationalError:
            print("Adding show_number column to existing database...")
            self.cursor.execute("ALTER TABLE games ADD COLUMN show_number INTEGER")
            self.conn.commit()

        # Clues table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS clues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                round TEXT NOT NULL,
                category TEXT NOT NULL,
                value TEXT NOT NULL,
                clue TEXT NOT NULL,
                answer TEXT,
                daily_double BOOLEAN DEFAULT 0,
                FOREIGN KEY (game_id) REFERENCES games(game_id)
            )
        """)

        # Create indices for better query performance
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_clues_game_id
            ON clues(game_id)
        """)

        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_clues_round
            ON clues(round)
        """)

        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_clues_category
            ON clues(category)
        """)

        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_games_show_number
            ON games(show_number)
        """)

        self.conn.commit()

    def game_exists(self, game_id: int) -> bool:
        """Check if a game already exists in the database"""
        self.cursor.execute(
            "SELECT 1 FROM games WHERE game_id = ?",
            (game_id,)
        )
        return self.cursor.fetchone() is not None

    def insert_game(self, game_data: Dict) -> bool:
        """
        Insert a complete game into the database

        Args:
            game_data: Dictionary containing game data from scraper

        Returns:
            True if successful, False if game already exists
        """
        game_id = game_data['game_id']

        # Check if game already exists
        if self.game_exists(game_id):
            print(f"Game {game_id} already exists in database. Skipping.")
            return False

        # Insert game metadata
        self.cursor.execute("""
            INSERT INTO games (game_id, show_number, title, url, air_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            game_id,
            game_data.get('show_number'),
            game_data['title'],
            game_data['url'],
            game_data.get('air_date')
        ))

        # Insert Jeopardy Round clues
        for clue in game_data.get('jeopardy_round', []):
            self._insert_clue(game_id, 'Jeopardy', clue)

        # Insert Double Jeopardy Round clues
        for clue in game_data.get('double_jeopardy_round', []):
            self._insert_clue(game_id, 'Double Jeopardy', clue)

        # Insert Final Jeopardy
        if game_data.get('final_jeopardy'):
            self._insert_clue(game_id, 'Final Jeopardy', game_data['final_jeopardy'])

        self.conn.commit()
        print(f"✓ Game {game_id} inserted into database")
        return True

    def _insert_clue(self, game_id: int, round_name: str, clue: Dict):
        """Insert a single clue into the database"""
        self.cursor.execute("""
            INSERT INTO clues (game_id, round, category, value, clue, answer, daily_double)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            game_id,
            round_name,
            clue.get('category', ''),
            clue.get('value', ''),
            clue.get('clue', ''),
            clue.get('answer'),
            clue.get('daily_double', False)
        ))

    def get_random_clue(self, exclude_final: bool = True) -> Optional[Dict]:
        """
        Get a random clue from the database

        Args:
            exclude_final: If True, exclude Final Jeopardy clues

        Returns:
            Dictionary with clue data or None if no clues found
        """
        query = """
            SELECT
                c.id,
                c.game_id,
                g.show_number,
                g.air_date,
                c.round,
                c.category,
                c.value,
                c.clue,
                c.answer,
                c.daily_double,
                g.title as game_title
            FROM clues c
            JOIN games g ON c.game_id = g.game_id
        """

        if exclude_final:
            query += " WHERE c.round != 'Final Jeopardy'"

        query += " ORDER BY RANDOM() LIMIT 1"

        self.cursor.execute(query)
        row = self.cursor.fetchone()

        if row:
            return dict(row)
        return None

    def get_clues_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """Get clues from a specific category"""
        self.cursor.execute("""
            SELECT
                c.id,
                c.game_id,
                g.show_number,
                g.air_date,
                c.round,
                c.category,
                c.value,
                c.clue,
                c.answer,
                c.daily_double,
                g.title as game_title
            FROM clues c
            JOIN games g ON c.game_id = g.game_id
            WHERE c.category LIKE ?
            ORDER BY RANDOM()
            LIMIT ?
        """, (f"%{category}%", limit))

        return [dict(row) for row in self.cursor.fetchall()]

    def get_clues_by_show_number(self, show_number: int) -> List[Dict]:
        """
        Get all clues from a specific show number

        Args:
            show_number: The Jeopardy show number (e.g., 9426)

        Returns:
            List of clue dictionaries, or empty list if show not found
        """
        self.cursor.execute("""
            SELECT
                c.id,
                c.game_id,
                g.show_number,
                g.air_date,
                c.round,
                c.category,
                c.value,
                c.clue,
                c.answer,
                c.daily_double,
                g.title as game_title
            FROM clues c
            JOIN games g ON c.game_id = g.game_id
            WHERE g.show_number = ?
            ORDER BY c.round, c.category
        """, (show_number,))

        return [dict(row) for row in self.cursor.fetchall()]

    def get_random_clue_by_date(self, start_date: str = None, end_date: str = None, exclude_final: bool = True) -> Optional[Dict]:
        """
        Get a random clue from the database filtered by date range

        Args:
            start_date: Start date in YYYY-MM-DD format (inclusive)
            end_date: End date in YYYY-MM-DD format (inclusive)
            exclude_final: If True, exclude Final Jeopardy clues

        Returns:
            Dictionary with clue data or None if no clues found
        """
        query = """
            SELECT
                c.id,
                c.game_id,
                g.show_number,
                g.air_date,
                c.round,
                c.category,
                c.value,
                c.clue,
                c.answer,
                c.daily_double,
                g.title as game_title
            FROM clues c
            JOIN games g ON c.game_id = g.game_id
            WHERE 1=1
        """
        params = []

        if start_date:
            query += " AND g.air_date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND g.air_date <= ?"
            params.append(end_date)

        if exclude_final:
            query += " AND c.round != 'Final Jeopardy'"

        query += " ORDER BY RANDOM() LIMIT 1"

        self.cursor.execute(query, params)
        row = self.cursor.fetchone()

        if row:
            return dict(row)
        return None

    def get_stats(self) -> Dict:
        """Get database statistics"""
        self.cursor.execute("SELECT COUNT(*) FROM games")
        game_count = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM clues")
        clue_count = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(DISTINCT category) FROM clues")
        category_count = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT MIN(show_number), MAX(show_number) FROM games WHERE show_number IS NOT NULL")
        show_range = self.cursor.fetchone()

        self.cursor.execute("SELECT MIN(air_date), MAX(air_date) FROM games WHERE air_date IS NOT NULL")
        date_range = self.cursor.fetchone()

        return {
            'total_games': game_count,
            'total_clues': clue_count,
            'unique_categories': category_count,
            'show_number_range': {
                'min': show_range[0],
                'max': show_range[1]
            } if show_range[0] else None,
            'date_range': {
                'min': date_range[0],
                'max': date_range[1]
            } if date_range[0] else None
        }

    def close(self):
        """Close database connection"""
        self.conn.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


if __name__ == "__main__":
    # Test the database
    with JeopardyDatabase() as db:
        stats = db.get_stats()
        print("Database Statistics:")
        print(f"  Total Games: {stats['total_games']}")
        print(f"  Total Clues: {stats['total_clues']}")
        print(f"  Unique Categories: {stats['unique_categories']}")
