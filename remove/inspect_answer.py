#!/usr/bin/env python3
"""Inspect how answers are stored"""

import requests
from bs4 import BeautifulSoup
import re

url = "https://j-archive.com/showgame.php?game_id=9302"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

round_table = soup.find('table', class_='round')
all_rows = round_table.find_all('tr', recursive=False)
first_clue_row = all_rows[1]
clue_cells = first_clue_row.find_all('td', class_='clue', recursive=False)

print("=== First Clue Cell ===")
first_clue = clue_cells[0]
print(f"\nFull HTML (first 1500 chars):\n{str(first_clue)[:1500]}")

print("\n\n=== Looking for answer ===")
div_with_mouseover = first_clue.find('div', onmouseover=True)
if div_with_mouseover:
    print("✓ Found div with onmouseover")
    mouseover = div_with_mouseover.get('onmouseover')
    print(f"\nMouseover attribute:\n{mouseover}")

    print("\n\nTrying regex patterns:")
    patterns = [
        r'correct_response[^>]*>([^<]+)<',
        r'correct_response">([^<]+)<',
        r'em class="correct_response">([^<]+)</em>',
    ]

    for pattern in patterns:
        match = re.search(pattern, mouseover)
        if match:
            print(f"✓ Pattern '{pattern}' matched: {match.group(1)}")
        else:
            print(f"✗ Pattern '{pattern}' did not match")
else:
    print("✗ No div with onmouseover found")

    # Try other ways to find answer
    print("\nLooking for other elements with mouseover:")
    all_mouseover = first_clue.find_all(attrs={'onmouseover': True})
    print(f"Found {len(all_mouseover)} elements with onmouseover")
    if all_mouseover:
        print(f"First element: {str(all_mouseover[0])[:500]}")
