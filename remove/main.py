#!/usr/bin/env python3
"""
J-Archive Jeopardy Game Scraper
Extracts all clues, answers, and metadata from a J-Archive game page
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_jarchive_game(game_id):
    """
    Scrape a complete Jeopardy game from J-Archive
    
    Args:
        game_id: The game ID from J-Archive URL
        
    Returns:
        Dictionary containing all game data
    """
    url = f"https://j-archive.com/showgame.php?game_id={game_id}"
    
    print(f"Fetching game {game_id}...")
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract game metadata
    game_title = soup.find('title').text.strip() if soup.find('title') else "Unknown Game"
    
    game_data = {
        'game_id': game_id,
        'title': game_title,
        'url': url,
        'jeopardy_round': [],
        'double_jeopardy_round': [],
        'final_jeopardy': None
    }
    
    # Find all rounds
    rounds = soup.find_all('table', class_='round')

    for round_idx, round_table in enumerate(rounds):
        round_name = 'jeopardy_round' if round_idx == 0 else 'double_jeopardy_round'

        # Extract categories - use find_all with recursive=False to get only direct children
        all_rows = round_table.find_all('tr', recursive=False)
        categories = []
        if all_rows:
            category_row = all_rows[0]
            category_cells = category_row.find_all('td', class_='category', recursive=False)
            categories = [cat.find('td', class_='category_name').text.strip()
                         for cat in category_cells if cat.find('td', class_='category_name')]

        print(f"\nRound {round_idx + 1}: {len(categories)} categories found")

        # Extract clues - skip first row (categories)
        clue_rows = all_rows[1:]
        
        for row_idx, row in enumerate(clue_rows):
            value = ['$200', '$400', '$600', '$800', '$1000'][row_idx] if row_idx < 5 else 'Unknown'
            clue_cells = row.find_all('td', class_='clue', recursive=False)

            for cat_idx, cell in enumerate(clue_cells):
                if cat_idx >= len(categories):
                    continue

                # Find clue text - it's a nested <td> with class clue_text
                clue_text_td = cell.find('td', class_='clue_text')
                if not clue_text_td:
                    continue

                clue_text = clue_text_td.text.strip()

                # Find answer - it's in a hidden <td> element with the correct_response class
                answer = None
                correct_response_em = cell.find('em', class_='correct_response')
                if correct_response_em:
                    answer = correct_response_em.get_text(strip=True)

                # Check if it's a Daily Double
                daily_double = 'clue_value_daily_double' in str(cell)

                clue_data = {
                    'category': categories[cat_idx],
                    'value': value,
                    'clue': clue_text,
                    'answer': answer,
                    'daily_double': daily_double
                }

                game_data[round_name].append(clue_data)
    
    # Extract Final Jeopardy
    final_round = soup.find('table', class_='final_round')
    if final_round:
        category_div = final_round.find('div', class_='category_name')
        clue_text_td = final_round.find('td', class_='clue_text')
        
        if category_div and clue_text_td:
            final_category = category_div.text.strip()
            final_clue = clue_text_td.text.strip()
            
            # Find Final Jeopardy answer
            final_answer = None
            onmouseover = final_round.find('div', onmouseover=True)
            if onmouseover:
                mouseover = onmouseover.get('onmouseover')
                answer_match = re.search(r'correct_response[^>]*>([^<]+)<', mouseover)
                if answer_match:
                    final_answer = answer_match.group(1).strip()
            
            game_data['final_jeopardy'] = {
                'category': final_category,
                'clue': final_clue,
                'answer': final_answer
            }
    
    return game_data


def print_game_data(game_data):
    """Print game data in a readable format"""
    print("\n" + "="*80)
    print(f"GAME: {game_data['title']}")
    print(f"URL: {game_data['url']}")
    print("="*80)
    
    # Print Jeopardy Round
    print("\n### JEOPARDY! ROUND ###\n")
    for clue in game_data['jeopardy_round']:
        dd_marker = " [DAILY DOUBLE]" if clue['daily_double'] else ""
        print(f"Category: {clue['category']}")
        print(f"Value: {clue['value']}{dd_marker}")
        print(f"Clue: {clue['clue']}")
        print(f"Answer: {clue['answer']}")
        print()
    
    # Print Double Jeopardy Round
    print("\n### DOUBLE JEOPARDY! ROUND ###\n")
    for clue in game_data['double_jeopardy_round']:
        dd_marker = " [DAILY DOUBLE]" if clue['daily_double'] else ""
        print(f"Category: {clue['category']}")
        print(f"Value: {clue['value']}{dd_marker}")
        print(f"Clue: {clue['clue']}")
        print(f"Answer: {clue['answer']}")
        print()
    
    # Print Final Jeopardy
    if game_data['final_jeopardy']:
        print("\n### FINAL JEOPARDY! ###\n")
        fj = game_data['final_jeopardy']
        print(f"Category: {fj['category']}")
        print(f"Clue: {fj['clue']}")
        print(f"Answer: {fj['answer']}")
        print()


def save_to_json(game_data, filename=None):
    """Save game data to JSON file"""
    if filename is None:
        filename = f"jeopardy_game_{game_data['game_id']}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(game_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nGame data saved to: {filename}")


if __name__ == "__main__":
    # Example usage
    game_id = 9302
    
    try:
        game_data = scrape_jarchive_game(game_id)
        
        # Print summary
        print(f"\n✓ Successfully scraped game {game_id}")
        print(f"  - Jeopardy Round: {len(game_data['jeopardy_round'])} clues")
        print(f"  - Double Jeopardy Round: {len(game_data['double_jeopardy_round'])} clues")
        print(f"  - Final Jeopardy: {'Yes' if game_data['final_jeopardy'] else 'No'}")
        
        # Print all data
        print_game_data(game_data)
        
        # Save to JSON
        save_to_json(game_data)
        
    except Exception as e:
        print(f"Error scraping game: {e}")
        import traceback
        traceback.print_exc()