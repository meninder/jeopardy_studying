# Quick Start Guide

## 🎯 Your Jeopardy project has been refactored!

### What's New?

1. **Modular Scraper** - Scrape any number of games
2. **SQLite Database** - Fast, queryable storage
3. **Quiz Web App** - Beautiful interface to test yourself
4. **JSON Debugging** - All data saved as JSON too

---

## 🚀 Getting Started (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Scrape Some Games (Optional - 4 games already loaded!)
```bash
# You already have 4 games with 240 clues!
# But if you want more:
python scraper/run_scraper.py 9310-9320 --stats
```

### Step 3: Start the Quiz App
```bash
# Easy way:
./start_quiz.sh

# Or manually:
python quiz-app/api.py
```

Then open your browser to: **http://localhost:8001**

---

## 📊 Current Database Status

- ✅ **4 games** imported
- ✅ **240 clues** ready to quiz
- ✅ **48 categories**

---

## 🎮 How to Use

### Scraping Games

```bash
# Single game
python scraper/run_scraper.py 9302

# Range of games
python scraper/run_scraper.py 9300-9310

# Specific games
python scraper/run_scraper.py 9300,9305,9310

# With custom delay (be respectful!)
python scraper/run_scraper.py 9300-9305 --delay 2.0

# Show stats after scraping
python scraper/run_scraper.py 9302 --stats
```

### Using the Quiz

1. Start the server: `python quiz-app/api.py`
2. Open browser to: `http://localhost:8001`
3. Click anywhere on the card to reveal the answer
4. Click "Next Question" for a new random clue

---

## 📁 New Directory Structure

```
jeopardy/
├── data/
│   ├── jeopardy.db          ← SQLite database
│   └── json/                ← Debug JSON files
├── scraper/
│   ├── jarchive_scraper.py  ← Core scraping logic
│   ├── database.py          ← SQLite operations
│   └── run_scraper.py       ← CLI tool
├── quiz-app/
│   ├── api.py               ← Flask API server
│   └── public/
│       └── index.html       ← Quiz interface
├── README.md                ← Full documentation
├── MIGRATION.md             ← What changed
└── requirements.txt         ← Python dependencies
```

---

## 🔧 API Endpoints

The quiz app uses these endpoints:

- `GET /api/clue/random` - Get random clue
- `GET /api/stats` - Database statistics
- `GET /api/health` - Health check

---

## 💡 Pro Tips

1. **Scrape Responsibly**: Use `--delay` to add pauses between requests
2. **JSON Debugging**: All games are saved as JSON in `data/json/`
3. **Database Queries**: Import `JeopardyDatabase` for custom queries
4. **Old Files**: `main.py` and `inspect_*.py` are kept for reference

---

## 🎉 You're Ready!

Everything is set up and tested. Just run:

```bash
python quiz-app/api.py
```

And start quizzing yourself! 🧠
