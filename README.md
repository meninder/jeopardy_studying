# Jeopardy Game Scraper & Quiz App

A complete system to scrape Jeopardy games from [J-Archive](https://j-archive.com/) and quiz yourself with a beautiful web interface.

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
# Install with uv (recommended):
uv sync

# Or with pip:
pip install -r requirements.txt
```

### Step 2: Scrape Some Games (Optional - 4 games already loaded!)
```bash
# You already have 4 games with 240 clues!
# But if you want more games from J-Archive:
uv run python scraper/run_scraper.py 9310-9320 --stats
```

### Step 3: Open the Quiz App
```bash
# Open the HTML file directly in your browser:
open quiz-app/public/index.html

# Or start the Flask server and browse to http://localhost:8001:
./start_quiz.sh
```

---

## Features

### Scraper
- ✅ Scrape single or multiple Jeopardy games from J-Archive
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

### Static Flashcards
- ✅ Works without any server (perfect for GitHub Pages)
- ✅ Edit flashcards in JSON format
- ✅ Auto-generate static JavaScript bundle
- ✅ Category filtering and shuffle mode
- ✅ AI-powered question assistance (optional OpenAI integration)
- ✅ Keyboard navigation support

---

## Project Structure

```
jeopardy/
├── data/                          # All data files
│   ├── jeopardy.db               # Raw scraped clues from J-Archive
│   ├── flashcards.db             # AI-enhanced flashcards
│   └── json/                     # Debug JSON files
├── scraper/                      # Scraping module
│   ├── __init__.py
│   ├── jarchive_scraper.py      # Core scraping logic
│   ├── database.py               # SQLite operations
│   └── run_scraper.py            # CLI to scrape games
├── generate_flashcard_data/      # AI flashcard generation
│   ├── generate_flashcard_data.py   # Converts clues to flashcards via OpenAI
│   └── generate_flashcards_js.py    # Exports flashcards.db to JavaScript
├── quiz-app/                     # Quiz application
│   ├── api.py                    # Flask API server
│   └── public/
│       └── index.html            # Quiz web interface
├── docs/                         # Static flashcards for GitHub Pages
│   ├── build_static.py           # Converts JSON to JS
│   ├── local_server/
│   │   └── flashcards-enhanced.json  # Edit your flashcards here
│   └── static/
│       ├── flashcards.html       # Static flashcard app
│       └── flashcards-data.js    # Auto-generated (don't edit)
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## Usage

### Scraping Games from J-Archive

**Scrape a single game:**
```bash
uv run python scraper/run_scraper.py 9302
```

**Scrape a range of games:**
```bash
uv run python scraper/run_scraper.py 9300-9310
```

**Scrape specific games:**
```bash
uv run python scraper/run_scraper.py 9300,9302,9304
```

**Advanced options:**
```bash
# Custom delay between requests (be respectful to J-Archive!)
uv run python scraper/run_scraper.py 9300-9305 --delay 2.0

# Skip JSON files (database only)
uv run python scraper/run_scraper.py 9302 --no-json

# Show database statistics after scraping
uv run python scraper/run_scraper.py 9302 --stats
```

### Using the Quiz

1. Open the HTML file directly: `open quiz-app/public/index.html`
2. Click anywhere on the card to reveal the answer
3. Click "Next Question" for a new random clue

**Alternative (with server):**
1. Start the server: `uv run python quiz-app/api.py`
2. Open browser to: `http://localhost:8001`

### Adding Questions to the Flashcard App (Full Pipeline)

This is the complete 3-step process to add new AI-enhanced flashcards:

**Step 1: Scrape games from J-Archive**
```bash
# Scrape a range of games (e.g., 9331-9350)
uv run python scraper/run_scraper.py 9331-9350 --stats
```
This saves raw Jeopardy clues to `data/jeopardy.db`.

**Step 2: Generate flashcards using OpenAI**
```bash
# Process unprocessed clues into enriched flashcards
uv run python generate_flashcard_data/generate_flashcard_data.py --batch-size 200
```
This:
- Samples unprocessed clues from `jeopardy.db`
- Sends them to OpenAI to create better questions with educational bullet points
- Categorizes them into topics (Life Sciences, History, etc.)
- Saves to `data/flashcards.db`
- Tracks processed clues (won't reprocess the same clue twice)

Requires `OPENAI_API_KEY` environment variable.

**Step 3: Export to JavaScript for the static app**
```bash
uv run python generate_flashcard_data/generate_flashcards_js.py
```
This exports `flashcards.db` to a JavaScript file for the static flashcard app.

---

### Building Static Flashcards for GitHub Pages (Manual)

For manually editing flashcards without the AI pipeline:

**Step 1: Edit your flashcards**
```bash
# Edit the JSON file with your study questions:
# docs/local_server/flashcards-enhanced.json
```

**Step 2: Build the static version**
```bash
cd docs
uv run python build_static.py
```

**Step 3: View locally**
```bash
open static/flashcards.html
```

**Step 4: Deploy to GitHub Pages (optional)**
```bash
git add docs/static/
git commit -m "Update flashcards"
git push
```

The build script converts your JSON flashcards into a JavaScript file that gets embedded in the static HTML, making it work without any backend server. Perfect for GitHub Pages hosting!

---

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

---

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

---

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

---

## Pro Tips

1. **Use uv**: `uv sync` and `uv run` are faster and more reliable than pip
2. **Scrape Responsibly**: Use `--delay` to add pauses between requests to J-Archive (default is 1 second)
3. **JSON Debugging**: All games are saved as JSON in `data/json/` for debugging purposes
4. **Database Queries**: Import `JeopardyDatabase` for custom queries
5. **Already Scraped**: The scraper automatically skips already-scraped games
6. **Old Files**: `main.py` and `inspect_*.py` are kept for reference

---

## Notes

- All Jeopardy game data is scraped from [J-Archive](https://j-archive.com/), a fan-created archive of Jeopardy! games
- The scraper includes a default 1-second delay between requests to be respectful to J-Archive
- The database will automatically create the schema on first run
- All data is stored locally in `data/jeopardy.db`

## License

This project is for educational purposes only. Please respect J-Archive's terms of service and use reasonable delays when scraping.
