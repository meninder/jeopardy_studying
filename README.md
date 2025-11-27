# Jeopardy Game Scraper & Quiz App

A complete system to scrape Jeopardy games from J-Archive and quiz yourself with a beautiful web interface.

## Project Structure

```
jeopardy/
├── data/                          # All data files
│   ├── jeopardy.db               # SQLite database
│   └── json/                     # Debug JSON files
├── scraper/                      # Scraping module
│   ├── __init__.py
│   ├── jarchive_scraper.py      # Core scraping logic
│   ├── database.py               # SQLite operations
│   └── run_scraper.py            # CLI to scrape games
├── quiz-app/                     # Quiz application
│   ├── api.py                    # Flask API server
│   └── public/
│       └── index.html            # Quiz web interface
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Scrape Jeopardy Games

The scraper is agnostic to game IDs and can scrape single games, ranges, or specific games.

**Scrape a single game:**
```bash
python scraper/run_scraper.py 9302
```

**Scrape a range of games:**
```bash
python scraper/run_scraper.py 9300-9310
```

**Scrape specific games:**
```bash
python scraper/run_scraper.py 9300,9302,9304
```

**Advanced options:**
```bash
# Custom delay between requests (be respectful!)
python scraper/run_scraper.py 9300-9305 --delay 2.0

# Skip JSON files (database only)
python scraper/run_scraper.py 9302 --no-json

# Show database statistics after scraping
python scraper/run_scraper.py 9302 --stats
```

### 2. Run the Quiz App

Start the Flask server:
```bash
python quiz-app/api.py
```

Then open your browser to:
```
http://localhost:8001
```

## Features

### Scraper
- ✅ Scrape single or multiple Jeopardy games
- ✅ Store data in SQLite database
- ✅ Save JSON files for debugging
- ✅ Batch scraping with configurable delays
- ✅ Skip already-scraped games
- ✅ Extract categories, clues, answers, and Daily Doubles

### Quiz App
- ✅ Random clue selection from database
- ✅ Click-to-reveal answer functionality
- ✅ Beautiful Jeopardy-themed interface
- ✅ Display category, value, and round information
- ✅ Track database statistics
- ✅ Daily Double indicators

## Database Schema

### Games Table
- `game_id` (PRIMARY KEY)
- `title`
- `url`
- `air_date`
- `scraped_at`

### Clues Table
- `id` (PRIMARY KEY)
- `game_id` (FOREIGN KEY)
- `round` (Jeopardy, Double Jeopardy, Final Jeopardy)
- `category`
- `value`
- `clue`
- `answer`
- `daily_double`

## API Endpoints

### Get Random Clue
```
GET /api/clue/random
```
Returns a random clue from the database (excludes Final Jeopardy by default)

### Get Statistics
```
GET /api/stats
```
Returns database statistics (total games, clues, categories)

### Health Check
```
GET /api/health
```
Returns API health status

## Development

### Using the Database Programmatically

```python
from scraper.database import JeopardyDatabase

# Get a random clue
with JeopardyDatabase() as db:
    clue = db.get_random_clue()
    print(f"Category: {clue['category']}")
    print(f"Clue: {clue['clue']}")
    print(f"Answer: {clue['answer']}")

# Get database stats
with JeopardyDatabase() as db:
    stats = db.get_stats()
    print(f"Total games: {stats['total_games']}")
```

### Scraping Programmatically

```python
from scraper import scrape_jarchive_game, JeopardyDatabase

# Scrape a game
game_data = scrape_jarchive_game(9302)

# Save to database
with JeopardyDatabase() as db:
    db.insert_game(game_data)
```

## Notes

- The scraper includes a default 1-second delay between requests to be respectful to J-Archive
- JSON files are saved in `data/json/` for debugging purposes
- The database will automatically create the schema on first run
- Already-scraped games are automatically skipped

## License

This project is for educational purposes only. Please respect J-Archive's terms of service and use reasonable delays when scraping.
