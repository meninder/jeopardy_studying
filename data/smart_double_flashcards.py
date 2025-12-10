#!/usr/bin/env python3
import sqlite3
import json
import random

# Connect to database
conn = sqlite3.connect('data/jeopardy.db')
cursor = conn.cursor()

# Current counts per category (we need to double these)
target_counts = {
    "Brain Anatomy & Medicine": 7,
    "American History": 10,
    "World Geography": 12,
    "Literature & Authors": 12,
    "Arts & Museums": 8,
    "Food, Drink & Cuisine": 11,
    "Music, Film & Television": 9,
    "Science & Nature": 10,
    "Language, Etymology & Wordplay": 8,
    "Sports & Athletics": 9,
    "Royalty & Historical Figures": 9,
    "Broadway & Theater": 5,
    "Ancient History & Mythology": 8,
    "Costumes, Fashion & Culture": 5,
    "Mountains, Geography & Landmarks": 6,
    "Miscellaneous Facts & Trivia": 7,
    "Poetry & Poets": 5,
    "Civil War & 19th Century America": 3
}

new_flashcards = {}

def get_questions(keywords_list, limit, exclude_keywords=None):
    """Get questions matching any of the keyword lists"""
    all_questions = []

    for keywords in keywords_list:
        where_clause = " OR ".join([f"category LIKE '%{kw}%'" for kw in keywords])
        if exclude_keywords:
            exclude_clause = " AND " + " AND ".join([f"category NOT LIKE '%{kw}%'" for kw in exclude_keywords])
        else:
            exclude_clause = ""

        query = f"""
        SELECT DISTINCT clue, answer FROM clues
        WHERE ({where_clause}){exclude_clause}
        AND answer IS NOT NULL
        AND length(clue) > 40
        AND clue NOT LIKE '%seen here%'
        AND clue NOT LIKE '%picture%'
        AND clue NOT LIKE '%shown here%'
        ORDER BY RANDOM() LIMIT {limit * 3}
        """

        cursor.execute(query)
        questions = [{"question": row[0], "answer": row[1]} for row in cursor.fetchall()]
        all_questions.extend(questions)

    # Remove duplicates and return up to limit
    seen = set()
    unique = []
    for q in all_questions:
        key = q['question']
        if key not in seen:
            seen.add(key)
            unique.append(q)
        if len(unique) >= limit:
            break

    return unique[:limit]

# Brain Anatomy & Medicine
new_flashcards["Brain Anatomy & Medicine"] = get_questions([
    ['BRAIN', 'ANATOMY', 'ORGAN', 'BODY PART'],
    ['MEDICINE', 'MEDICAL', 'DOCTOR', 'DISEASE', 'HEALTH'],
    ['HEART', 'BLOOD', 'NERVE', 'CELL']
], target_counts["Brain Anatomy & Medicine"])

# American History
new_flashcards["American History"] = get_questions([
    ['U.S. HISTORY', 'AMERICAN HISTORY'],
    ['PRESIDENT', 'WASHINGTON', 'LINCOLN', 'JEFFERSON'],
    ['AMERICAN', 'U.S.', 'AMERICA'],
    ['REVOLUTIONARY WAR', 'INDEPENDENCE']
], target_counts["American History"], exclude_keywords=['CIVIL WAR'])

# World Geography
new_flashcards["World Geography"] = get_questions([
    ['GEOGRAPHY', 'COUNTRIES', 'CAPITALS'],
    ['RIVER', 'LAKE', 'OCEAN', 'SEA'],
    ['CITY', 'NATION', 'BORDER']
], target_counts["World Geography"], exclude_keywords=['AMERICAN', 'U.S.'])

# Literature & Authors
new_flashcards["Literature & Authors"] = get_questions([
    ['LITERATURE', 'NOVEL', 'FICTION'],
    ['AUTHOR', 'WRITER', 'POET'],
    ['BOOK', 'CLASSIC']
], target_counts["Literature & Authors"], exclude_keywords=['POET'])

# Arts & Museums
new_flashcards["Arts & Museums"] = get_questions([
    ['ART', 'ARTIST', 'PAINTING', 'PAINTER'],
    ['MUSEUM', 'SCULPTURE', 'GALLERY'],
    ['PICASSO', 'VAN GOGH', 'MONET']
], target_counts["Arts & Museums"])

# Food, Drink & Cuisine
new_flashcards["Food, Drink & Cuisine"] = get_questions([
    ['FOOD', 'CUISINE', 'RECIPE', 'DISH'],
    ['DRINK', 'COCKTAIL', 'WINE', 'BEER', 'BEVERAGE'],
    ['COOK', 'CHEF', 'RESTAURANT'],
    ['CAKE', 'DESSERT', 'BREAD']
], target_counts["Food, Drink & Cuisine"])

# Music, Film & Television
new_flashcards["Music, Film & Television"] = get_questions([
    ['MUSIC', 'SONG', 'BAND', 'SINGER'],
    ['FILM', 'MOVIE', 'CINEMA', 'DIRECTOR'],
    ['TELEVISION', 'TV', 'SITCOM', 'SHOW'],
    ['ROCK', 'POP', 'JAZZ']
], target_counts["Music, Film & Television"], exclude_keywords=['BROADWAY', 'MUSICAL', 'THEATER'])

# Science & Nature
new_flashcards["Science & Nature"] = get_questions([
    ['SCIENCE', 'PHYSICS', 'CHEMISTRY', 'BIOLOGY'],
    ['ANIMAL', 'NATURE', 'WILDLIFE', 'CREATURE'],
    ['PLANET', 'SPACE', 'STAR'],
    ['ELEMENT', 'ATOM', 'MOLECULE']
], target_counts["Science & Nature"])

# Language, Etymology & Wordplay
new_flashcards["Language, Etymology & Wordplay"] = get_questions([
    ['WORD', 'LANGUAGE', 'ETYMOLOGY'],
    ['PHRASE', 'IDIOM', 'SAYING'],
    ['LETTER', 'ALPHABET', 'SPELLING'],
    ['PREFIX', 'SUFFIX', 'ROOT']
], target_counts["Language, Etymology & Wordplay"])

# Sports & Athletics
new_flashcards["Sports & Athletics"] = get_questions([
    ['SPORTS', 'SPORT', 'ATHLETIC'],
    ['FOOTBALL', 'BASEBALL', 'BASKETBALL', 'HOCKEY'],
    ['OLYMPIC', 'CHAMPION', 'ATHLETE'],
    ['SOCCER', 'TENNIS', 'GOLF']
], target_counts["Sports & Athletics"])

# Royalty & Historical Figures
new_flashcards["Royalty & Historical Figures"] = get_questions([
    ['ROYAL', 'KING', 'QUEEN', 'MONARCH'],
    ['PRINCE', 'PRINCESS', 'EMPEROR', 'EMPRESS'],
    ['DYNASTY', 'THRONE', 'CROWN'],
    ['HISTORICAL FIGURE', 'LEADER']
], target_counts["Royalty & Historical Figures"])

# Broadway & Theater
new_flashcards["Broadway & Theater"] = get_questions([
    ['BROADWAY', 'MUSICAL', 'THEATER', 'THEATRE'],
    ['PLAY', 'STAGE', 'DRAMA'],
    ['SHOW TUNE', 'RODGERS', 'HAMMERSTEIN']
], target_counts["Broadway & Theater"])

# Ancient History & Mythology
new_flashcards["Ancient History & Mythology"] = get_questions([
    ['ANCIENT', 'MYTHOLOGY', 'MYTH', 'LEGEND'],
    ['GREEK', 'ROMAN', 'EGYPT'],
    ['ZEUS', 'APOLLO', 'ATHENA'],
    ['PHARAOH', 'CAESAR', 'EMPIRE']
], target_counts["Ancient History & Mythology"])

# Costumes, Fashion & Culture
new_flashcards["Costumes, Fashion & Culture"] = get_questions([
    ['FASHION', 'COSTUME', 'CLOTHING', 'DRESS'],
    ['STYLE', 'WEAR', 'GARMENT'],
    ['DESIGNER', 'FABRIC']
], target_counts["Costumes, Fashion & Culture"])

# Mountains, Geography & Landmarks
new_flashcards["Mountains, Geography & Landmarks"] = get_questions([
    ['MOUNTAIN', 'PEAK', 'SUMMIT', 'RANGE'],
    ['LANDMARK', 'MONUMENT', 'MEMORIAL'],
    ['EVEREST', 'ALPS', 'ANDES']
], target_counts["Mountains, Geography & Landmarks"])

# Miscellaneous Facts & Trivia
cursor.execute("""
SELECT DISTINCT clue, answer FROM clues
WHERE answer IS NOT NULL
AND length(clue) > 40
AND clue NOT LIKE '%seen here%'
AND clue NOT LIKE '%picture%'
AND clue NOT LIKE '%shown here%'
ORDER BY RANDOM() LIMIT ?
""", (target_counts["Miscellaneous Facts & Trivia"],))
new_flashcards["Miscellaneous Facts & Trivia"] = [{"question": row[0], "answer": row[1]} for row in cursor.fetchall()]

# Poetry & Poets
new_flashcards["Poetry & Poets"] = get_questions([
    ['POET', 'POETRY', 'POEM', 'VERSE'],
    ['SHAKESPEARE', 'FROST', 'DICKINSON'],
    ['SONNET', 'HAIKU', 'RHYME']
], target_counts["Poetry & Poets"])

# Civil War & 19th Century America
new_flashcards["Civil War & 19th Century America"] = get_questions([
    ['CIVIL WAR', '19TH CENTURY'],
    ['LINCOLN', 'GRANT', 'LEE'],
    ['CONFEDERATE', 'UNION', 'SLAVERY']
], target_counts["Civil War & 19th Century America"])

# Save to JSON
with open('smart_flashcards.json', 'w') as f:
    json.dump(new_flashcards, f, indent=2)

print(f"\nExtracted new flashcards for {len(new_flashcards)} categories:")
total_new = 0
for cat in target_counts.keys():
    count = len(new_flashcards.get(cat, []))
    total_new += count
    target = target_counts.get(cat, 0)
    print(f"{cat}: {count}/{target} questions (total will be {target + count})")

print(f"\nTotal new flashcards: {total_new}")
print(f"Current total: 206")
print(f"New total: {206 + total_new}")

conn.close()
