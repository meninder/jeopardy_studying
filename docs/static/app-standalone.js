// Standalone Flashcard App - Works without server (GitHub Pages compatible)
// Data loaded from flashcards-data.js

let flashcardsData = FLASHCARD_DATA; // Loaded from flashcards-data.js
let allFlashcards = [];
let currentFlashcards = [];
let currentIndex = 0;
let isFlipped = false;

// DOM Elements
const flashcard = document.getElementById('flashcard');
const questionEl = document.getElementById('question');
const answerEl = document.getElementById('answer');
const jeopardyCategoryEl = document.getElementById('jeopardy-category');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const shuffleBtn = document.getElementById('shuffle-btn');
const categorySelect = document.getElementById('category-select');
const currentEl = document.getElementById('current');
const totalEl = document.getElementById('total');
const categoryNameEl = document.getElementById('category-name');

// AI-related DOM Elements
const settingsBtn = document.getElementById('settings-btn');
const askAIBtn = document.getElementById('ask-ai-btn');
const settingsModal = document.getElementById('settings-modal');
const askAIModal = document.getElementById('ask-ai-modal');
const apiKeyInput = document.getElementById('api-key-input');
const saveApiKeyBtn = document.getElementById('save-api-key-btn');
const clearApiKeyBtn = document.getElementById('clear-api-key-btn');
const toggleKeyVisibilityBtn = document.getElementById('toggle-key-visibility');
const apiKeyStatus = document.getElementById('api-key-status');
const aiContextQuestion = document.getElementById('ai-context-question');
const aiQuestionInput = document.getElementById('ai-question-input');
const submitAIQuestionBtn = document.getElementById('submit-ai-question-btn');
const aiLoading = document.getElementById('ai-loading');
const aiResponse = document.getElementById('ai-response');
const aiError = document.getElementById('ai-error');

// Initialize the app
function initApp() {
    // Populate category dropdown
    populateCategories();

    // Load all flashcards
    loadAllFlashcards();

    // Shuffle on startup so you don't see the same card first every time
    shuffleCards();
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
        jeopardyCategoryEl.textContent = '';
        return;
    }

    // Reset flip state FIRST, before updating content
    if (isFlipped) {
        flashcard.classList.remove('flipped');
        isFlipped = false;
    }

    const card = currentFlashcards[currentIndex];
    questionEl.textContent = card.question;

    // Display jeopardy category if available
    if (card.jeopardyCategory) {
        jeopardyCategoryEl.textContent = `Jeopardy Category: ${card.jeopardyCategory}`;
        jeopardyCategoryEl.style.display = 'inline-block';
    } else {
        jeopardyCategoryEl.textContent = '';
        jeopardyCategoryEl.style.display = 'none';
    }

    // Format answer with line breaks and bullets preserved
    answerEl.innerHTML = formatAnswer(card.answer);

    currentEl.textContent = currentIndex + 1;
    categoryNameEl.textContent = card.category;

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
        // If card is flipped, flip it back first, then navigate after animation
        if (isFlipped) {
            flipCard();
            setTimeout(() => {
                currentIndex--;
                displayCard();
            }, 600); // Wait for flip animation (0.6s)
        } else {
            currentIndex--;
            displayCard();
        }
    }
}

// Navigate to next card
function nextCard() {
    if (currentIndex < currentFlashcards.length - 1) {
        // If card is flipped, flip it back first, then navigate after animation
        if (isFlipped) {
            flipCard();
            setTimeout(() => {
                currentIndex++;
                displayCard();
            }, 600); // Wait for flip animation (0.6s)
        } else {
            currentIndex++;
            displayCard();
        }
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
categorySelect.addEventListener('change', handleCategoryChange);

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
    }
});

// Start the app when page loads
initApp();

// ============================================
// AI FUNCTIONALITY
// ============================================

const OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions';
const API_KEY_STORAGE_KEY = 'jeopardy_openai_api_key';

// API Key Management
function getStoredAPIKey() {
    return localStorage.getItem(API_KEY_STORAGE_KEY);
}

function saveAPIKey(apiKey) {
    localStorage.setItem(API_KEY_STORAGE_KEY, apiKey);
}

function clearAPIKey() {
    localStorage.removeItem(API_KEY_STORAGE_KEY);
}

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

// Modal Management
function openSettingsModal() {
    const storedKey = getStoredAPIKey();
    if (storedKey) {
        apiKeyInput.value = storedKey;
        showAPIKeyStatus('API key is saved', 'success');
    } else {
        apiKeyInput.value = '';
        apiKeyStatus.textContent = '';
        apiKeyStatus.className = 'api-key-status';
    }
    settingsModal.classList.add('show');
}

function closeSettingsModal() {
    settingsModal.classList.remove('show');
    apiKeyStatus.textContent = '';
    apiKeyStatus.className = 'api-key-status';
}

function openAskAIModal() {
    // Check if API key exists
    const apiKey = getStoredAPIKey();
    if (!apiKey) {
        openSettingsModal();
        showAPIKeyStatus('Please enter your OpenAI API key first', 'error');
        return;
    }

    // Set the current question as context
    const currentCard = currentFlashcards[currentIndex];
    aiContextQuestion.textContent = currentCard.question;

    // Clear previous responses
    aiQuestionInput.value = '';
    aiResponse.textContent = '';
    aiError.textContent = '';
    aiLoading.style.display = 'none';

    askAIModal.classList.add('show');
    aiQuestionInput.focus();
}

function closeAskAIModal() {
    askAIModal.classList.remove('show');
}

function showAPIKeyStatus(message, type) {
    apiKeyStatus.textContent = message;
    apiKeyStatus.className = `api-key-status ${type}`;
}

// Toggle API Key Visibility
function toggleAPIKeyVisibility() {
    if (apiKeyInput.type === 'password') {
        apiKeyInput.type = 'text';
        toggleKeyVisibilityBtn.textContent = '🙈 Hide';
    } else {
        apiKeyInput.type = 'password';
        toggleKeyVisibilityBtn.textContent = '👁️ Show';
    }
}

// Save API Key
function handleSaveAPIKey() {
    const apiKey = apiKeyInput.value.trim();
    if (!apiKey) {
        showAPIKeyStatus('Please enter an API key', 'error');
        return;
    }

    if (!apiKey.startsWith('sk-')) {
        showAPIKeyStatus('Invalid API key format. OpenAI keys start with "sk-"', 'error');
        return;
    }

    saveAPIKey(apiKey);
    showAPIKeyStatus('API key saved successfully!', 'success');
    setTimeout(() => {
        closeSettingsModal();
    }, 1500);
}

// Clear API Key
function handleClearAPIKey() {
    if (confirm('Are you sure you want to clear your saved API key?')) {
        clearAPIKey();
        apiKeyInput.value = '';
        showAPIKeyStatus('API key cleared', 'success');
    }
}

// Submit AI Question
async function handleSubmitAIQuestion() {
    const userQuestion = aiQuestionInput.value.trim();

    if (!userQuestion) {
        showAIError('Please enter a question');
        return;
    }

    const apiKey = getStoredAPIKey();
    if (!apiKey) {
        showAIError('No API key found. Please set your API key in settings.');
        return;
    }

    // Get current card info
    const currentCard = currentFlashcards[currentIndex];

    // Show loading state
    aiLoading.style.display = 'block';
    aiResponse.textContent = '';
    aiError.textContent = '';
    submitAIQuestionBtn.disabled = true;

    try {
        const response = await fetch(OPENAI_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: 'gpt-5.2',
                messages: [
                    {
                        role: 'system',
                        content: 'You are a helpful Jeopardy study assistant. Help users understand Jeopardy clues and answers in a clear and educational way. The goal is to make the person asking the question better at answering trivia questions.'
                    },
                    {
                        role: 'user',
                        content: `Here is the current Jeopardy clue I'm studying:\n\nQuestion: ${currentCard.question}\nAnswer: ${currentCard.answer}\nCategory: ${currentCard.category}\n\nMy question: ${userQuestion}`
                    }
                ],
                temperature: 0.7
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));

            if (response.status === 401) {
                throw new Error('Invalid API key. Please check your settings.');
            } else if (response.status === 429) {
                throw new Error('Rate limit exceeded. Please try again later.');
            } else if (response.status === 500) {
                throw new Error('OpenAI server error. Please try again later.');
            } else {
                throw new Error(errorData.error?.message || `API error: ${response.status}`);
            }
        }

        const data = await response.json();
        const aiAnswer = data.choices[0].message.content;

        // Parse markdown and show response
        if (typeof marked !== 'undefined') {
            aiResponse.innerHTML = marked.parse(aiAnswer);
        } else {
            // Fallback if marked.js fails to load
            aiResponse.textContent = aiAnswer;
        }

    } catch (error) {
        console.error('AI Error:', error);
        showAIError(error.message || 'Failed to get AI response. Please try again.');
    } finally {
        aiLoading.style.display = 'none';
        submitAIQuestionBtn.disabled = false;
    }
}

function showAIError(message) {
    aiError.textContent = message;
    aiResponse.textContent = '';
}

// Event Listeners for AI functionality
settingsBtn.addEventListener('click', openSettingsModal);
askAIBtn.addEventListener('click', openAskAIModal);
saveApiKeyBtn.addEventListener('click', handleSaveAPIKey);
clearApiKeyBtn.addEventListener('click', handleClearAPIKey);
toggleKeyVisibilityBtn.addEventListener('click', toggleAPIKeyVisibility);
submitAIQuestionBtn.addEventListener('click', handleSubmitAIQuestion);

// Allow Enter key to submit in question input
aiQuestionInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmitAIQuestion();
    }
});

// Allow Enter key to save API key
apiKeyInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        handleSaveAPIKey();
    }
});

// Close modals when clicking outside
settingsModal.addEventListener('click', (e) => {
    if (e.target === settingsModal) {
        closeSettingsModal();
    }
});

askAIModal.addEventListener('click', (e) => {
    if (e.target === askAIModal) {
        closeAskAIModal();
    }
});

// Close modals with ESC key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        if (settingsModal.classList.contains('show')) {
            closeSettingsModal();
        }
        if (askAIModal.classList.contains('show')) {
            closeAskAIModal();
        }
    }
});

// Make modal close functions globally accessible for onclick handlers
window.closeSettingsModal = closeSettingsModal;
window.closeAskAIModal = closeAskAIModal;
