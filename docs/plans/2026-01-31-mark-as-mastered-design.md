# Mark as Mastered Feature Design

## Overview

Add ability to mark flashcards as "mastered" so they don't appear until reset.

## Decisions

| Decision | Choice |
|----------|--------|
| Checkmark location | Both sides of card (bottom-right corner) |
| Reset location | Settings modal |
| Progress display | "Card 3 of 42 (8 mastered)" |
| Un-mark behavior | Reset only (no toggle) |
| All cards mastered | Auto-reset and reshuffle |
| Storage mechanism | localStorage |
| Keyboard shortcut | `M` key |

## Data Storage

**localStorage key:** `jeopardy-mastered-cards`

```javascript
{
  "cardIds": ["card-123", "card-456", ...],
  "lastReset": "2026-01-31T..."
}
```

Card IDs are stable hashes generated from question + answer text.

Mastered status is global across all categories.

## UI Elements

### Checkmark Button (on card)
- Position: Bottom-right corner of both front and back faces
- Size: 44x44px circular button
- Appearance: "✓" icon, semi-transparent purple background
- On click: Green flash, then auto-advance to next card

### Progress Display (header)
- Format: `Card 3 of 42 (8 mastered)`
- "(8 mastered)" in muted color

### Settings Modal Additions
- New section: "Study Progress"
- Text: "You've mastered X cards across all categories"
- Button: "Reset Progress" with confirmation dialog

## Interaction Flow

1. User clicks checkmark (or presses `M`)
2. Green flash animation (200ms)
3. Card ID saved to localStorage
4. Deck refiltered to exclude mastered cards
5. Auto-advance to next card
6. Progress counter updates

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Mark last card in deck | "All mastered!" flash, auto-reset, reshuffle |
| Category has 0 remaining on load | Auto-reset that category, show toast |
| Switch to fully mastered category | Auto-reset, reshuffle |
| Reset while viewing a card | Reload full deck, go to card 1, reshuffle |

## Files to Modify

- `docs/static/flashcards.html` - Add checkmark button HTML, settings modal section
- `docs/static/app-standalone.js` - localStorage logic, filtering, UI updates

## Implementation Tasks

1. Add localStorage helper functions (save, load, reset mastered cards)
2. Add card ID generation (hash from question + answer)
3. Add checkmark button to card HTML (both sides)
4. Add checkmark button styles
5. Add click handler for checkmark (save + advance)
6. Add `M` keyboard shortcut
7. Update progress display to show mastered count
8. Filter mastered cards from deck on load and category change
9. Add "Study Progress" section to settings modal
10. Add reset button with confirmation
11. Handle auto-reset when all cards mastered
12. Add toast notification for auto-reset
