# 🎯 Jeopardy Study Flashcards

**206 flashcards with enriched answers** - Double the content, 10x the context!

Each answer includes 2-4 bullet points with historical context, dates, statistics, and related facts.

---

## 📂 Folder Structure

```
study_guide/
├── local_server/              ← EDIT HERE (source files)
│   ├── flashcards-enhanced.json   ← Edit this to update flashcards
│   ├── index.html
│   ├── app-enhanced.js
│   └── styles.css
│
├── static/                    ← DEPLOY HERE (auto-generated)
│   ├── flashcards.html        ← Push this to GitHub Pages
│   ├── flashcards-data.js     ← Auto-built by build_static.py
│   └── app-standalone.js
│
├── build_static.py            ← Run this to rebuild static version
└── README.md                  ← You are here
```

---

## 🚀 Quick Start

### Option 1: GitHub Pages (Static)

**Just open it:**
```bash
open static/flashcards.html
```

Works without any server! Perfect for GitHub Pages.

### Option 2: Local Development

**With server:**
```bash
cd local_server/
python3 -m http.server 8000
# Open: http://localhost:8000
```

Better for editing and testing.

---

## 🔄 Workflow: Making Updates

### Step 1: Edit the JSON
```bash
vim local_server/flashcards-enhanced.json
```

The JSON structure:
```json
{
  "categories": [
    {
      "name": "Category Name",
      "flashcards": [
        {
          "question": "What is...?",
          "answer": "The answer\n\n• Additional fact 1\n• Additional fact 2\n• Additional fact 3"
        }
      ]
    }
  ]
}
```

### Step 2: Build Static Version
```bash
python3 build_static.py
```

This converts `local_server/flashcards-enhanced.json` → `static/flashcards-data.js`

### Step 3: Test
```bash
open static/flashcards.html
```

### Step 4: Deploy to GitHub Pages
```bash
git add .
git commit -m "Update flashcards"
git push
```

---

## 🌐 GitHub Pages Setup

### One-Time Setup

1. **Push to GitHub:**
   ```bash
   git add study_guide/
   git commit -m "Add flashcard app"
   git push
   ```

2. **Enable GitHub Pages:**
   - Go to repo Settings → Pages
   - Source: Deploy from branch `main`
   - Folder: `/` or `/study_guide` (depending on your setup)
   - Save

3. **Your URL will be:**
   ```
   https://[username].github.io/[repo]/study_guide/static/flashcards.html
   ```

### Every Update

```bash
python3 build_static.py  # Rebuild
git add static/          # Stage changes
git commit -m "Update"   # Commit
git push                 # Deploy!
```

GitHub Pages will automatically update within a minute.

---

## 🛠️ Why Two Folders?

### `local_server/` (Source - Edit This!)
- **Purpose:** Development, editing, source control
- **Format:** Clean JSON, separate CSS/JS files
- **Pros:** Easy to edit, clean structure, version control friendly
- **Cons:** Requires HTTP server (CORS restrictions)

### `static/` (Built - Deploy This!)
- **Purpose:** GitHub Pages deployment
- **Format:** Embedded data as JavaScript variable
- **Pros:** Works without server, GitHub Pages compatible
- **Cons:** Harder to edit directly (but you don't need to!)

### `build_static.py` (The Bridge!)
- Reads clean JSON from `local_server/`
- Wraps it as `const FLASHCARD_DATA = {...};`
- Writes to `static/flashcards-data.js`
- Solves CORS issue for GitHub Pages

---

## 📚 Features

- **206 flashcards** across 15 categories
- **Enriched answers** with 2-4 bullet points each
- **Click to flip** cards and reveal answers
- **Keyboard shortcuts:** ← → arrows, Space to flip
- **Shuffle mode** to randomize order
- **Category filter** to focus on specific topics
- **Progress tracking** shows current card
- **Scrollable answers** for longer content
- **Responsive design** works on mobile

---

## 📖 Categories

1. Brain Anatomy & Medicine (8 cards)
2. American History (10 cards)
3. World Geography (12 cards)
4. Literature & Authors (12 cards)
5. Arts & Museums (8 cards)
6. Food, Drink & Cuisine (11 cards)
7. Music, Film & Television (9 cards)
8. Science & Nature (10 cards)
9. Language, Etymology & Wordplay (8 cards)
10. Sports & Athletics (9 cards)
11. Royalty & Historical Figures (9 cards)
12. Broadway & Theater (5 cards)
13. Ancient History & Mythology (8 cards)
14. Costumes, Fashion & Culture (5 cards)
15. Miscellaneous Facts & Trivia (7+ cards)

---

## 💡 Example: Enriched Answer

**Before (Basic):**
```
Q: What is the cerebellum?
A: The cerebellum
```

**After (Enriched):**
```
Q: What is the 'little brain' about the size of a fist located at the back of the head?
A: The cerebellum

   • Coordinates voluntary movements like balance and posture
   • Contains more neurons than the rest of the brain combined
   • Damage causes ataxia (loss of coordination) and tremors
   • Latin name means 'little brain'
```

Every flashcard follows this format!

---

## 🎓 Study Tips

1. **Start with one category** to focus your learning
2. **Try to answer before flipping** - say it out loud!
3. **Use shuffle mode** to test yourself randomly
4. **Read the bullet points** - context helps retention
5. **Review struggling categories** more frequently
6. **Mix all categories** once comfortable with individual topics

---

## ✅ Update Checklist

Before deploying to GitHub Pages:

- [ ] Edited `local_server/flashcards-enhanced.json`
- [ ] Ran `python3 build_static.py`
- [ ] Tested `static/flashcards.html` works
- [ ] Committed both `local_server/` and `static/` folders
- [ ] Pushed to GitHub

---

## 🚫 Important: Don't Edit These Files

These are **auto-generated** by `build_static.py`:
- `static/flashcards-data.js` (has "DO NOT EDIT" comment)

Always edit the source in `local_server/` and rebuild!

---

## 🐛 Troubleshooting

### "Error loading flashcards" in static version
- Make sure you ran `python3 build_static.py`
- Check that `static/flashcards-data.js` exists
- Try opening directly: `open static/flashcards.html`

### Changes not showing on GitHub Pages
- Did you run `build_static.py`?
- Did you commit and push `static/` folder?
- Wait 1-2 minutes for GitHub Pages to update
- Hard refresh browser (Cmd+Shift+R)

### Can't run local server version
- Make sure you're in `local_server/` directory
- Run: `python3 -m http.server 8000`
- Open: `http://localhost:8000` (not file://)

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Edit flashcards | `vim local_server/flashcards-enhanced.json` |
| Rebuild static | `python3 build_static.py` |
| Test static | `open static/flashcards.html` |
| Test with server | `cd local_server && python3 -m http.server 8000` |
| Deploy | `git add . && git commit -m "Update" && git push` |

---

## 📊 Stats

- **Total Cards:** 206
- **Total Categories:** 15
- **Average Facts per Card:** 3-4 bullet points
- **Total Content:** ~52KB of enriched learning material
- **Source:** Extracted from actual Jeopardy database

---

**Happy studying!** 📚🎓

Need help? Check the comments in `build_static.py` or open an issue.
