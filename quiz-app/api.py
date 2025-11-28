#!/usr/bin/env python3
"""
Flask API to serve Jeopardy clues from SQLite database
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import sys
from pathlib import Path

# Add parent directory to path to import scraper module
sys.path.insert(0, str(Path(__file__).parent.parent))
from scraper.database import JeopardyDatabase

app = Flask(__name__, static_folder='public')
CORS(app)  # Enable CORS for development

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "jeopardy.db"


@app.route('/')
def serve_app():
    """Serve the quiz application"""
    return send_from_directory('public', 'index.html')


@app.route('/api/clue/random', methods=['GET'])
def get_random_clue():
    """Get a random clue from the database, optionally filtered by date"""
    try:
        # Get optional date filter parameters from query string
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        with JeopardyDatabase(str(DB_PATH)) as db:
            # If date filters provided, use date-filtered method
            if start_date or end_date:
                clue = db.get_random_clue_by_date(
                    start_date=start_date,
                    end_date=end_date,
                    exclude_final=True
                )
            else:
                clue = db.get_random_clue(exclude_final=True)

            if clue is None:
                return jsonify({'error': 'No clues found in database'}), 404

            return jsonify(clue)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        with JeopardyDatabase(str(DB_PATH)) as db:
            stats = db.get_stats()
            return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/show/<int:show_number>', methods=['GET'])
def get_show_clues(show_number):
    """Get all clues from a specific show number"""
    try:
        with JeopardyDatabase(str(DB_PATH)) as db:
            clues = db.get_clues_by_show_number(show_number)

            if not clues:
                return jsonify({'error': f'Show #{show_number} not found in database'}), 404

            return jsonify({
                'show_number': show_number,
                'clue_count': len(clues),
                'clues': clues
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'database': str(DB_PATH)})


if __name__ == '__main__':
    print("=" * 80)
    print("JEOPARDY QUIZ APP - Starting Server")
    print("=" * 80)
    print(f"Database: {DB_PATH}")
    print(f"Quiz app: http://localhost:8001")
    print(f"API: http://localhost:8001/api")
    print("=" * 80)

    # Check if database exists
    if not DB_PATH.exists():
        print(f"\nWARNING: Database not found at {DB_PATH}")
        print("Run the scraper first to populate the database:")
        print("  python scraper/run_scraper.py 9302")
        print()

    app.run(debug=True, port=8001)
