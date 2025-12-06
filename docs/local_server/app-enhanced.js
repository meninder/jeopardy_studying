// Enhanced Flashcard App
// Loads from flashcards-enhanced.json with enriched answers

let flashcardsData = {};
let allFlashcards = [];
let currentFlashcards = [];
let currentIndex = 0;
let isFlipped = false;

// DOM Elements
const flashcard = document.getElementById('flashcard');
const questionEl = document.getElementById('question');
const answerEl = document.getElementById('answer');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const shuffleBtn = document.getElementById('shuffle-btn');
const flipBtn = document.getElementById('flip-btn');
const categorySelect = document.getElementById('category-select');
const currentEl = document.getElementById('current');
const totalEl = document.getElementById('total');
const categoryNameEl = document.getElementById('category-name');

// Load flashcards from JSON file
async function loadFlashcards() {
    try {
        const response = await fetch('flashcards-enhanced.json');
        const data = await response.json();
        flashcardsData = data;

        // Populate category dropdown
        populateCategories();

        // Load all flashcards
        loadAllFlashcards();

        // Shuffle on startup so you don't see the same card first every time
        shuffleCards();
    } catch (error) {
        console.error('Error loading flashcards:', error);
        questionEl.textContent = 'Error loading flashcards. Make sure flashcards-enhanced.json is in the same folder.';
    }
}

// Populate category dropdown
function populateCategories() {
    flashcardsData.categories.forEach((category, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = `${category.name} (${category.flashcards.length} cards)`;
        categorySelect.appendChild(option);
    });
}

// Load all flashcards (mixed mode)
function loadAllFlashcards() {
    allFlashcards = [];
    flashcardsData.categories.forEach(category => {
        category.flashcards.forEach(card => {
            allFlashcards.push({
                ...card,
                category: category.name
            });
        });
    });
    currentFlashcards = [...allFlashcards];
    totalEl.textContent = currentFlashcards.length;
}

// Load flashcards for specific category
function loadCategoryFlashcards(categoryIndex) {
    const category = flashcardsData.categories[categoryIndex];
    currentFlashcards = category.flashcards.map(card => ({
        ...card,
        category: category.name
    }));
    totalEl.textContent = currentFlashcards.length;
}

// Display current card
function displayCard() {
    if (currentFlashcards.length === 0) {
        questionEl.textContent = 'No flashcards available';
        answerEl.innerHTML = '';
        return;
    }

    const card = currentFlashcards[currentIndex];
    questionEl.textContent = card.question;

    // Format answer with line breaks and bullets preserved
    answerEl.innerHTML = formatAnswer(card.answer);

    currentEl.textContent = currentIndex + 1;
    categoryNameEl.textContent = card.category;

    // Reset flip state
    if (isFlipped) {
        flashcard.classList.remove('flipped');
        isFlipped = false;
    }

    // Update button states
    prevBtn.disabled = currentIndex === 0;
    nextBtn.disabled = currentIndex === currentFlashcards.length - 1;
}

// Format answer text with proper line breaks and styling
function formatAnswer(answer) {
    // Split by newlines and process
    const lines = answer.split('\n');
    let html = '';

    lines.forEach(line => {
        if (line.trim() === '') {
            html += '<br>';
        } else if (line.trim().startsWith('•')) {
            // Bullet point - make it a styled list item
            html += `<div class="bullet-point">${line.trim()}</div>`;
        } else {
            // Main answer or regular text
            html += `<div class="answer-line">${line}</div>`;
        }
    });

    return html;
}

// Flip card
function flipCard() {
    flashcard.classList.toggle('flipped');
    isFlipped = !isFlipped;
}

// Navigate to previous card
function prevCard() {
    if (currentIndex > 0) {
        currentIndex--;
        displayCard();
    }
}

// Navigate to next card
function nextCard() {
    if (currentIndex < currentFlashcards.length - 1) {
        currentIndex++;
        displayCard();
    }
}

// Shuffle cards
function shuffleCards() {
    // Fisher-Yates shuffle algorithm
    for (let i = currentFlashcards.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [currentFlashcards[i], currentFlashcards[j]] = [currentFlashcards[j], currentFlashcards[i]];
    }
    currentIndex = 0;
    displayCard();
}

// Handle category change
function handleCategoryChange() {
    const selectedValue = categorySelect.value;
    currentIndex = 0;

    if (selectedValue === 'all') {
        loadAllFlashcards();
    } else {
        loadCategoryFlashcards(parseInt(selectedValue));
    }

    displayCard();
}

// Event Listeners
flashcard.addEventListener('click', flipCard);
prevBtn.addEventListener('click', prevCard);
nextBtn.addEventListener('click', nextCard);
shuffleBtn.addEventListener('click', shuffleCards);
flipBtn.addEventListener('click', flipCard);
categorySelect.addEventListener('change', handleCategoryChange);

// Keyboard navigation
document.addEventListener('keydown', (e) => {
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
    }
});

// Initialize app
loadFlashcards();
