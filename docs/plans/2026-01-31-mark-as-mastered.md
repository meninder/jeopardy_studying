# Mark as Mastered Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add ability to mark flashcards as "mastered" so they don't appear until reset.

**Architecture:** Store mastered card IDs in localStorage. Filter them from the active deck. Add checkmark button to both card faces. Add reset functionality to settings modal.

**Tech Stack:** Vanilla JavaScript, localStorage, existing HTML/CSS patterns

---

## Task 1: Add localStorage Helper Functions

**Files:**
- Modify: `docs/static/app-standalone.js:249-262` (after existing localStorage code)

**Step 1: Add the mastered cards storage functions**

Add after line 262 (after `clearAPIKey` function):

```javascript
// ============================================
// MASTERED CARDS FUNCTIONALITY
// ============================================

const MASTERED_CARDS_STORAGE_KEY = 'jeopardy-mastered-cards';

function getMasteredCards() {
    const stored = localStorage.getItem(MASTERED_CARDS_STORAGE_KEY);
    if (!stored) return { cardIds: [], lastReset: null };
    try {
        return JSON.parse(stored);
    } catch {
        return { cardIds: [], lastReset: null };
    }
}

function saveMasteredCard(cardId) {
    const data = getMasteredCards();
    if (!data.cardIds.includes(cardId)) {
        data.cardIds.push(cardId);
        localStorage.setItem(MASTERED_CARDS_STORAGE_KEY, JSON.stringify(data));
    }
}

function resetMasteredCards() {
    localStorage.setItem(MASTERED_CARDS_STORAGE_KEY, JSON.stringify({
        cardIds: [],
        lastReset: new Date().toISOString()
    }));
}

function generateCardId(card) {
    // Simple hash from question + answer for stable ID
    const str = card.question + '|' + card.answer;
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return 'card-' + Math.abs(hash).toString(36);
}

function getMasteredCount() {
    return getMasteredCards().cardIds.length;
}
```

**Step 2: Verify syntax is correct**

Open browser console on `docs/static/flashcards.html`, check for JavaScript errors.

**Step 3: Commit**

```bash
git add docs/static/app-standalone.js
git commit -m "feat: add localStorage helpers for mastered cards"
```

---

## Task 2: Add Card ID to Each Flashcard

**Files:**
- Modify: `docs/static/app-standalone.js:63-75` (loadAllFlashcards function)
- Modify: `docs/static/app-standalone.js:78-85` (loadCategoryFlashcards function)

**Step 1: Update loadAllFlashcards to add cardId**

Replace the `loadAllFlashcards` function:

```javascript
// Load all flashcards (mixed mode)
function loadAllFlashcards() {
    allFlashcards = [];
    flashcardsData.categories.forEach(category => {
        category.flashcards.forEach(card => {
            const cardWithMeta = {
                ...card,
                category: category.name
            };
            cardWithMeta.cardId = generateCardId(cardWithMeta);
            allFlashcards.push(cardWithMeta);
        });
    });
    currentFlashcards = filterMasteredCards([...allFlashcards]);
    updateProgressDisplay();
}
```

**Step 2: Update loadCategoryFlashcards to add cardId**

Replace the `loadCategoryFlashcards` function:

```javascript
// Load flashcards for specific category
function loadCategoryFlashcards(categoryIndex) {
    const category = flashcardsData.categories[categoryIndex];
    const cardsWithMeta = category.flashcards.map(card => {
        const cardWithMeta = {
            ...card,
            category: category.name
        };
        cardWithMeta.cardId = generateCardId(cardWithMeta);
        return cardWithMeta;
    });
    currentFlashcards = filterMasteredCards(cardsWithMeta);
    updateProgressDisplay();
}
```

**Step 3: Add the filter function and progress display function**

Add after the mastered cards storage functions:

```javascript
function filterMasteredCards(cards) {
    const mastered = getMasteredCards();
    return cards.filter(card => !mastered.cardIds.includes(card.cardId));
}

function updateProgressDisplay() {
    const masteredCount = getMasteredCount();
    totalEl.textContent = currentFlashcards.length;

    // Update or create mastered count display
    let masteredSpan = document.getElementById('mastered-count');
    if (!masteredSpan) {
        masteredSpan = document.createElement('span');
        masteredSpan.id = 'mastered-count';
        masteredSpan.style.opacity = '0.7';
        masteredSpan.style.marginLeft = '8px';
        document.getElementById('progress').appendChild(masteredSpan);
    }

    if (masteredCount > 0) {
        masteredSpan.textContent = `(${masteredCount} mastered)`;
    } else {
        masteredSpan.textContent = '';
    }
}
```

**Step 4: Verify cards still load correctly**

Refresh the page, verify flashcards display normally.

**Step 5: Commit**

```bash
git add docs/static/app-standalone.js
git commit -m "feat: add card IDs and filter mastered cards from deck"
```

---

## Task 3: Add Checkmark Button HTML and CSS

**Files:**
- Modify: `docs/static/flashcards.html:684-698` (flashcard-front and flashcard-back divs)
- Modify: `docs/static/flashcards.html:8-668` (add CSS styles)

**Step 1: Add CSS for checkmark button**

Add before the closing `</style>` tag (around line 668):

```css
.mastered-btn {
    position: absolute;
    bottom: 15px;
    right: 15px;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    border: none;
    background: rgba(102, 126, 234, 0.2);
    color: #667eea;
    font-size: 1.5rem;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
}

.mastered-btn:hover {
    background: rgba(102, 126, 234, 0.4);
    transform: scale(1.1);
}

.mastered-btn.clicked {
    background: #28a745;
    color: white;
}

.flashcard-back .mastered-btn {
    background: rgba(255, 255, 255, 0.2);
    color: white;
}

.flashcard-back .mastered-btn:hover {
    background: rgba(255, 255, 255, 0.4);
}

.flashcard-back .mastered-btn.clicked {
    background: #28a745;
    color: white;
}

.toast {
    position: fixed;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    background: #333;
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 1rem;
    z-index: 2000;
    animation: toastFadeIn 0.3s ease-out;
}

@keyframes toastFadeIn {
    from {
        opacity: 0;
        transform: translateX(-50%) translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateX(-50%) translateY(0);
    }
}
```

**Step 2: Add checkmark button to front of card**

Find the `flashcard-front` div (around line 684) and add the button inside it, after the hint:

```html
<div class="flashcard-front">
    <div class="card-content">
        <div>
            <p id="question">Loading...</p>
            <div id="jeopardy-category" class="jeopardy-category-label"></div>
        </div>
    </div>
    <div class="hint">Click card to reveal answer</div>
    <button class="mastered-btn" id="mastered-btn-front" title="Mark as mastered">✓</button>
</div>
```

**Step 3: Add checkmark button to back of card**

Find the `flashcard-back` div (around line 693) and add the button inside it, after the hint:

```html
<div class="flashcard-back">
    <div class="card-content">
        <div id="answer">Answer</div>
    </div>
    <div class="hint">Click card to see question</div>
    <button class="mastered-btn" id="mastered-btn-back" title="Mark as mastered">✓</button>
</div>
```

**Step 4: Verify buttons appear on card**

Refresh page, verify checkmark buttons appear on both sides of card.

**Step 5: Commit**

```bash
git add docs/static/flashcards.html
git commit -m "feat: add checkmark button HTML and CSS to flashcard"
```

---

## Task 4: Add Checkmark Click Handler

**Files:**
- Modify: `docs/static/app-standalone.js:10-21` (add DOM element references)
- Modify: `docs/static/app-standalone.js` (add click handler after existing event listeners)

**Step 1: Add DOM element references**

Add after line 21 (after `categoryNameEl`):

```javascript
const masteredBtnFront = document.getElementById('mastered-btn-front');
const masteredBtnBack = document.getElementById('mastered-btn-back');
```

**Step 2: Add the mark as mastered function**

Add after the `filterMasteredCards` function:

```javascript
function markCurrentCardAsMastered(event) {
    event.stopPropagation(); // Prevent card flip

    if (currentFlashcards.length === 0) return;

    const card = currentFlashcards[currentIndex];

    // Visual feedback
    const btn = event.currentTarget;
    btn.classList.add('clicked');

    setTimeout(() => {
        // Save to localStorage
        saveMasteredCard(card.cardId);

        // Remove from current deck
        currentFlashcards.splice(currentIndex, 1);

        // Check if deck is now empty
        if (currentFlashcards.length === 0) {
            handleAllCardsMastered();
            return;
        }

        // Adjust index if we were at the end
        if (currentIndex >= currentFlashcards.length) {
            currentIndex = currentFlashcards.length - 1;
        }

        // Update display
        updateProgressDisplay();
        displayCard();

        // Reset button state
        btn.classList.remove('clicked');
    }, 200);
}

function handleAllCardsMastered() {
    showToast('All mastered! Deck reset.');
    resetMasteredCards();

    // Reload based on current category selection
    const selectedValue = categorySelect.value;
    if (selectedValue === 'all') {
        loadAllFlashcards();
    } else {
        loadCategoryFlashcards(parseInt(selectedValue));
    }

    currentIndex = 0;
    shuffleCards();
}

function showToast(message) {
    // Remove existing toast if any
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 2000);
}
```

**Step 3: Add event listeners for mastered buttons**

Add after line 216 (after `categorySelect.addEventListener`):

```javascript
masteredBtnFront.addEventListener('click', markCurrentCardAsMastered);
masteredBtnBack.addEventListener('click', markCurrentCardAsMastered);
```

**Step 4: Test the mastered functionality**

1. Click checkmark on a card
2. Verify green flash, card advances
3. Verify progress shows "(1 mastered)"
4. Refresh page, verify the card is still hidden

**Step 5: Commit**

```bash
git add docs/static/app-standalone.js
git commit -m "feat: add click handler for marking cards as mastered"
```

---

## Task 5: Add M Keyboard Shortcut

**Files:**
- Modify: `docs/static/app-standalone.js:219-239` (keyboard event listener)

**Step 1: Add M key to keyboard handler**

Replace the keyboard event listener switch statement:

```javascript
// Keyboard navigation
document.addEventListener('keydown', (e) => {
    // Don't trigger shortcuts if user is typing in an input or textarea
    const isTyping = e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA';

    if (isTyping) {
        return; // Allow normal typing behavior
    }

    switch(e.key) {
        case 'ArrowLeft':
            prevCard();
            break;
        case 'ArrowRight':
            nextCard();
            break;
        case ' ':
            e.preventDefault();
            flipCard();
            break;
        case 'm':
        case 'M':
            // Simulate click on front button (works regardless of flip state)
            masteredBtnFront.click();
            break;
    }
});
```

**Step 2: Update keyboard hint in HTML**

In `flashcards.html`, find the keyboard-hint div (around line 719) and update it:

```html
<div class="keyboard-hint">
    Use ← → arrow keys to navigate • Space to flip card • M to mark mastered
</div>
```

**Step 3: Test keyboard shortcut**

Press M key, verify card is marked as mastered.

**Step 4: Commit**

```bash
git add docs/static/app-standalone.js docs/static/flashcards.html
git commit -m "feat: add M keyboard shortcut for marking cards mastered"
```

---

## Task 6: Add Reset Button to Settings Modal

**Files:**
- Modify: `docs/static/flashcards.html:724-746` (settings modal)
- Modify: `docs/static/app-standalone.js` (add reset handler)

**Step 1: Add Study Progress section to settings modal HTML**

In `flashcards.html`, find the settings modal body (around line 731) and add after the API key status div:

```html
<div id="api-key-status" class="api-key-status"></div>

<hr style="margin: 20px 0; border: none; border-top: 1px solid #e0e0e0;">

<div class="form-group">
    <label>Study Progress</label>
    <p id="mastered-status" style="color: #666; margin-bottom: 10px;">You've mastered 0 cards across all categories</p>
    <button id="reset-progress-btn" class="btn btn-secondary" style="width: 100%;">Reset Progress</button>
</div>
```

**Step 2: Add DOM reference and handler in JS**

Add after the other AI-related DOM elements (around line 38):

```javascript
const masteredStatusEl = document.getElementById('mastered-status');
const resetProgressBtn = document.getElementById('reset-progress-btn');
```

**Step 3: Update openSettingsModal to show mastered count**

Find `openSettingsModal` function and add at the end, before `settingsModal.classList.add('show')`:

```javascript
// Update mastered count display
const masteredCount = getMasteredCount();
masteredStatusEl.textContent = `You've mastered ${masteredCount} card${masteredCount !== 1 ? 's' : ''} across all categories`;
```

**Step 4: Add reset handler**

Add after the `handleClearAPIKey` function:

```javascript
function handleResetProgress() {
    const masteredCount = getMasteredCount();
    if (masteredCount === 0) {
        showToast('No mastered cards to reset');
        return;
    }

    if (confirm(`Are you sure? This will bring back all ${masteredCount} mastered cards.`)) {
        resetMasteredCards();

        // Reload current deck
        const selectedValue = categorySelect.value;
        if (selectedValue === 'all') {
            loadAllFlashcards();
        } else {
            loadCategoryFlashcards(parseInt(selectedValue));
        }

        currentIndex = 0;
        shuffleCards();

        // Update modal display
        masteredStatusEl.textContent = "You've mastered 0 cards across all categories";

        showToast('Progress reset!');
        closeSettingsModal();
    }
}
```

**Step 5: Add event listener for reset button**

Add after line 448 (after `submitAIQuestionBtn` event listener):

```javascript
resetProgressBtn.addEventListener('click', handleResetProgress);
```

**Step 6: Test reset functionality**

1. Mark a few cards as mastered
2. Open settings, verify count shows correctly
3. Click Reset Progress, confirm
4. Verify all cards are back

**Step 7: Commit**

```bash
git add docs/static/flashcards.html docs/static/app-standalone.js
git commit -m "feat: add reset progress button to settings modal"
```

---

## Task 7: Handle Edge Case - Empty Category on Load

**Files:**
- Modify: `docs/static/app-standalone.js` (handleCategoryChange and loadAllFlashcards)

**Step 1: Add auto-reset check to handleCategoryChange**

Replace the `handleCategoryChange` function:

```javascript
// Handle category change
function handleCategoryChange() {
    const selectedValue = categorySelect.value;
    currentIndex = 0;

    if (selectedValue === 'all') {
        loadAllFlashcards();
    } else {
        loadCategoryFlashcards(parseInt(selectedValue));
    }

    // Check if all cards in this category are mastered
    if (currentFlashcards.length === 0) {
        handleAllCardsMastered();
        return;
    }

    displayCard();
}
```

**Step 2: Add same check to initApp**

Update `initApp` function:

```javascript
// Initialize the app
function initApp() {
    // Populate category dropdown
    populateCategories();

    // Load all flashcards
    loadAllFlashcards();

    // Check if all cards are mastered on load
    if (currentFlashcards.length === 0) {
        handleAllCardsMastered();
        return;
    }

    // Shuffle on startup so you don't see the same card first every time
    shuffleCards();
}
```

**Step 3: Test edge case**

1. Mark all cards as mastered (or all in a category)
2. Refresh page (or switch to that category)
3. Verify auto-reset happens with toast message

**Step 4: Commit**

```bash
git add docs/static/app-standalone.js
git commit -m "feat: auto-reset when all cards in deck are mastered"
```

---

## Task 8: Final Integration Test

**Files:**
- None (testing only)

**Step 1: Full feature test**

Test the complete flow:

1. Load page fresh - verify cards display, progress shows "Card 1 of N"
2. Click checkmark on front of card - verify green flash, card advances, "(1 mastered)" appears
3. Flip card, click checkmark on back - verify same behavior
4. Press M key - verify card marked as mastered
5. Refresh page - verify mastered cards stay hidden
6. Open settings - verify "You've mastered X cards" shows correct count
7. Click Reset Progress - verify confirmation dialog
8. Confirm reset - verify all cards are back, toast shows
9. Mark all cards as mastered - verify auto-reset and shuffle happens

**Step 2: Cross-browser test (optional)**

If available, test in Safari and Firefox to verify localStorage works.

**Step 3: Commit any fixes if needed**

If any issues found, fix and commit with appropriate message.

---

## Summary

After completing all tasks, the feature includes:

- Checkmark button on both sides of flashcard
- localStorage persistence of mastered cards
- Progress display showing "(X mastered)"
- M keyboard shortcut
- Reset button in settings modal with confirmation
- Auto-reset when all cards in deck are mastered
- Toast notifications for feedback
