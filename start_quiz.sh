#!/bin/bash

# Start the Jeopardy Quiz App

echo "=========================================="
echo "   JEOPARDY QUIZ APP - Quick Start"
echo "=========================================="
echo ""

# Check if database exists
if [ ! -f "data/jeopardy.db" ]; then
    echo "⚠️  Database not found!"
    echo ""
    echo "Would you like to scrape some games first? (y/n)"
    read -r response

    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo ""
        echo "Scraping games 9302-9310..."
        python scraper/run_scraper.py 9302-9310 --stats
    else
        echo ""
        echo "Please run the scraper first:"
        echo "  python scraper/run_scraper.py 9302-9310"
        exit 1
    fi
fi

echo ""
echo "Starting quiz app..."
echo "Open your browser to: http://localhost:8001"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python quiz-app/api.py
