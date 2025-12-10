# Flashcards Data Management

This directory contains scripts to expand the flashcards in `docs/static/flashcards-data.js` using questions from the Jeopardy database.

## Files

- **`jeopardy.db`** - SQLite database containing Jeopardy questions and answers
- **`smart_double_flashcards.py`** - Extracts relevant questions from the database
- **`merge_flashcards.py`** - Merges extracted questions into flashcards-data.js
- **`smart_flashcards.json`** - Temporary output from extraction (auto-generated)

## How to Expand Flashcards

### Step 1: Extract Questions from Database

Run the extraction script to pull new questions from the database:

```bash
python3 data/smart_double_flashcards.py
```

This will:
- Query the `jeopardy.db` database for questions matching each flashcard category
- Use smart keyword searches (database categories don't map 1:1 with flashcard categories)
- Filter out visual clues (questions with "seen here", "picture", etc.)
- Generate `data/smart_flashcards.json` with the extracted questions

**Note:** The script uses `ORDER BY RANDOM()` so you'll get different questions each time you run it.

### Step 2: Merge into Flashcards File

Run the merge script to add the extracted questions to the flashcards:

```bash
python3 data/merge_flashcards.py
```

This will:
- Read the extracted questions from `data/smart_flashcards.json`
- Add them to each category in `docs/static/flashcards-data.js`
- Update the metadata (total card count, etc.)
- Preserve the JavaScript format

### Complete Workflow

```bash
# From the project root directory
cd /path/to/jeopardy

# Extract new questions
python3 data/smart_double_flashcards.py

# Merge into flashcards
python3 data/merge_flashcards.py
```

## Customizing the Extraction

To modify which questions are extracted, edit `data/smart_double_flashcards.py`:

1. **Adjust target counts** - Change how many questions to add per category:
   ```python
   target_counts = {
       "Brain Anatomy & Medicine": 7,  # Change this number
       "American History": 10,
       # ...
   }
   ```

2. **Modify search keywords** - Update the keyword lists for each category:
   ```python
   new_flashcards["Brain Anatomy & Medicine"] = get_questions([
       ['BRAIN', 'ANATOMY', 'ORGAN', 'BODY PART'],  # Add/remove keywords
       ['MEDICINE', 'MEDICAL', 'DOCTOR', 'DISEASE'],
       # ...
   ], target_counts["Brain Anatomy & Medicine"])
   ```

3. **Add exclusion keywords** - Filter out unwanted categories:
   ```python
   get_questions([...], target, exclude_keywords=['CIVIL WAR', 'POLITICS'])
   ```

## Database Schema

The `jeopardy.db` database has this structure:

```sql
-- Table: clues
- id (INTEGER PRIMARY KEY)
- game_id (INTEGER)
- round (TEXT)
- category (TEXT)
- value (TEXT)
- clue (TEXT)
- answer (TEXT)
- daily_double (BOOLEAN)
```

## Tips

- Run the extraction multiple times to get different random questions
- Review `smart_flashcards.json` before merging if you want to manually curate
- The merge script appends to existing flashcards (doesn't replace them)
- Backup `docs/static/flashcards-data.js` before merging if you want to revert
