#!/usr/bin/env python3
"""Quick script to inspect J-Archive HTML structure"""

import requests
from bs4 import BeautifulSoup

url = "https://j-archive.com/showgame.php?game_id=9302"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

print("=== Looking for round tables ===")
# Try different ways to find round tables
tables = soup.find_all('table')
print(f"Total tables found: {len(tables)}")

for i, table in enumerate(tables[:5]):  # First 5 tables
    classes = table.get('class', [])
    id_attr = table.get('id', '')
    print(f"\nTable {i}: class={classes}, id={id_attr}")

    # Look at first row
    first_tr = table.find('tr')
    if first_tr:
        print(f"  First <tr> content preview: {str(first_tr)[:200]}")

print("\n\n=== Looking for categories ===")
# Try to find category elements
for selector in ['td.category', 'td.category_name', '.category', '.category_name']:
    elements = soup.select(selector)
    if elements:
        print(f"\nFound {len(elements)} elements with selector '{selector}'")
        print(f"  First element: {elements[0].text.strip()[:100] if elements else 'N/A'}")

print("\n\n=== Looking for clues ===")
for selector in ['td.clue', '.clue_text', 'td.clue_text']:
    elements = soup.select(selector)
    if elements:
        print(f"\nFound {len(elements)} elements with selector '{selector}'")
        if elements:
            print(f"  First element: {str(elements[0])[:200]}")
