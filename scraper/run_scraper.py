#!/usr/bin/env python3
"""
CLI tool to scrape multiple Jeopardy games and store them in the database
"""

import argparse
import time
from typing import List, Tuple
from pathlib import Path

from jarchive_scraper import scrape_jarchive_game, save_to_json
from database import JeopardyDatabase


def scrape_game(game_id: int, db: JeopardyDatabase, save_json: bool = True) -> Tuple[bool, str]:
    """
    Scrape a single game and store it

    Args:
        game_id: Game ID to scrape
        db: Database instance
        save_json: Whether to save JSON debug file

    Returns:
        Tuple of (success, message)
    """
    try:
        # Check if already exists
        if db.game_exists(game_id):
            return False, f"Game {game_id} already exists in database"

        # Scrape the game
        game_data = scrape_jarchive_game(game_id)

        # Save to database
        db.insert_game(game_data)

        # Save JSON for debugging
        if save_json:
            json_path = save_to_json(game_data)
            print(f"  JSON saved: {json_path}")

        # Print summary
        total_clues = (
            len(game_data['jeopardy_round']) +
            len(game_data['double_jeopardy_round']) +
            (1 if game_data['final_jeopardy'] else 0)
        )

        return True, f"Successfully scraped {total_clues} clues"

    except Exception as e:
        return False, f"Error: {str(e)}"


def scrape_games_batch(
    game_ids: List[int],
    delay: float = 1.0,
    save_json: bool = True
) -> dict:
    """
    Scrape multiple games with delay between requests

    Args:
        game_ids: List of game IDs to scrape
        delay: Delay in seconds between requests (be respectful!)
        save_json: Whether to save JSON debug files

    Returns:
        Dictionary with statistics
    """
    stats = {
        'total': len(game_ids),
        'success': 0,
        'failed': 0,
        'skipped': 0
    }

    with JeopardyDatabase() as db:
        for i, game_id in enumerate(game_ids, 1):
            print(f"\n[{i}/{len(game_ids)}] Processing game {game_id}...")

            success, message = scrape_game(game_id, db, save_json)

            if success:
                stats['success'] += 1
            elif "already exists" in message:
                stats['skipped'] += 1
            else:
                stats['failed'] += 1

            print(f"  {message}")

            # Be respectful with delays between requests
            if i < len(game_ids):
                time.sleep(delay)

    return stats


def parse_game_range(range_str: str) -> List[int]:
    """
    Parse game range string into list of game IDs

    Examples:
        "9302" -> [9302]
        "9300-9305" -> [9300, 9301, 9302, 9303, 9304, 9305]
        "9300,9302,9304" -> [9300, 9302, 9304]
    """
    game_ids = []

    for part in range_str.split(','):
        part = part.strip()

        if '-' in part:
            # Range like "9300-9305"
            start, end = part.split('-')
            game_ids.extend(range(int(start), int(end) + 1))
        else:
            # Single ID
            game_ids.append(int(part))

    return game_ids


def main():
    parser = argparse.ArgumentParser(
        description='Scrape Jeopardy games from J-Archive',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape a single game
  python run_scraper.py 9302

  # Scrape a range of games
  python run_scraper.py 9300-9310

  # Scrape specific games
  python run_scraper.py 9300,9302,9304

  # Scrape with custom delay
  python run_scraper.py 9300-9305 --delay 2.0

  # Skip JSON files (database only)
  python run_scraper.py 9302 --no-json
        """
    )

    parser.add_argument(
        'games',
        type=str,
        help='Game ID(s) to scrape. Can be single (9302), range (9300-9305), or comma-separated (9300,9302,9304)'
    )

    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between requests in seconds (default: 1.0)'
    )

    parser.add_argument(
        '--no-json',
        action='store_true',
        help='Skip saving JSON debug files'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics after scraping'
    )

    args = parser.parse_args()

    # Parse game IDs
    try:
        game_ids = parse_game_range(args.games)
    except ValueError as e:
        print(f"Error parsing game IDs: {e}")
        return

    print(f"Planning to scrape {len(game_ids)} game(s)")
    print(f"Delay between requests: {args.delay}s")
    print(f"Save JSON files: {not args.no_json}")
    print("=" * 80)

    # Scrape games
    stats = scrape_games_batch(
        game_ids,
        delay=args.delay,
        save_json=not args.no_json
    )

    # Print summary
    print("\n" + "=" * 80)
    print("SCRAPING COMPLETE")
    print(f"  Total games processed: {stats['total']}")
    print(f"  Successfully scraped: {stats['success']}")
    print(f"  Skipped (already exists): {stats['skipped']}")
    print(f"  Failed: {stats['failed']}")

    # Show database stats if requested
    if args.stats:
        print("\n" + "=" * 80)
        print("DATABASE STATISTICS")
        with JeopardyDatabase() as db:
            db_stats = db.get_stats()
            print(f"  Total Games: {db_stats['total_games']}")
            print(f"  Total Clues: {db_stats['total_clues']}")
            print(f"  Unique Categories: {db_stats['unique_categories']}")


if __name__ == "__main__":
    main()
