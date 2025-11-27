#!/usr/bin/env python3
"""Understand the exact table structure"""

import requests
from bs4 import BeautifulSoup

url = "https://j-archive.com/showgame.php?game_id=9302"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

round_table = soup.find('table', class_='round')

print("=== Analyzing first 10 rows ===\n")
all_rows = round_table.find_all('tr', recursive=False)  # Only direct children
print(f"Direct TR children: {len(all_rows)}")

for i, row in enumerate(all_rows[:10]):
    tds = row.find_all('td', recursive=False)
    print(f"\nRow {i}: {len(tds)} direct TD children")

    for j, td in enumerate(tds[:3]):  # First 3 TDs
        classes = td.get('class', [])
        print(f"  TD {j}: class={classes}")

        # Show content preview
        text = td.get_text(strip=True)[:50]
        print(f"    Text preview: {text}")

        # Check for nested tables
        nested_tables = td.find_all('table')
        if nested_tables:
            print(f"    Contains {len(nested_tables)} nested table(s)")
