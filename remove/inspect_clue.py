#!/usr/bin/env python3
"""Inspect detailed clue structure"""

import requests
from bs4 import BeautifulSoup

url = "https://j-archive.com/showgame.php?game_id=9302"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find first round table
round_table = soup.find('table', class_='round')
print("=== ROUND TABLE STRUCTURE ===\n")

# Get all rows
all_rows = round_table.find_all('tr')
print(f"Total rows in round table: {len(all_rows)}")

# First row (categories)
print("\n=== FIRST ROW (Categories) ===")
first_row = all_rows[0]
category_cells = first_row.find_all('td', class_='category')
print(f"Number of category cells: {len(category_cells)}")
if category_cells:
    print(f"First category: {category_cells[0].find('td', class_='category_name').text}")

# Second row (first clue row)
print("\n=== SECOND ROW (First Clue Row) ===")
if len(all_rows) > 1:
    second_row = all_rows[1]
    print(f"Second row HTML (first 500 chars):\n{str(second_row)[:500]}")

    clue_cells = second_row.find_all('td', class_='clue')
    print(f"\nNumber of clue cells in row: {len(clue_cells)}")

    if clue_cells:
        first_clue = clue_cells[0]
        print("\n=== FIRST CLUE CELL ===")
        print(f"Full HTML:\n{str(first_clue)[:800]}")

        # Try to find clue_text
        clue_text = first_clue.find('td', class_='clue_text')
        if clue_text:
            print(f"\n✓ Found clue_text: {clue_text.text[:100]}")
        else:
            print("\n✗ No clue_text found!")

        # Try to find answer
        div_with_mouseover = first_clue.find('div', onmouseover=True)
        if div_with_mouseover:
            print(f"\n✓ Found div with onmouseover")
            mouseover = div_with_mouseover.get('onmouseover')
            print(f"Mouseover content (first 200 chars): {mouseover[:200]}")
