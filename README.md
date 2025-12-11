# Talmud Consecutive Citation Finder

## Project Overview
This project analyzes the Talmud to find instances where a Mishna citation is consecutively repeated in the Gemara text.

## Goal
Answer the question: "How often is a Mishna citation consecutively repeated in the Talmud?"

## What counts as "consecutively repeated"?
- Two or more citations that appear one after another in the Gemara (sequential citation IDs)
- All citations reference the same Mishna
- The citation texts are nearly identical (with minor differences like the suffix "וכו")

## Project Structure
```
TALMUD_PROJECT/
├── mishnayot.db              # SQLite database with Mishnayot, citations, and matches
├── db.py                     # Database setup and connection
├── Data_processing.py        # Extracts and processes Talmud text data
├── matching_process.py       # Matches citations to Mishnayot using text similarity
├── consecutive_analysis.py   # Main script to find consecutive repeated citations
└── README.md               
```

## Database Schema

### Tables
1. **mishnayot**: Contains the Mishna texts
   - `id`: Primary key
   - `daf`: Location reference (e.g., "2a", "42a")
   - `mishna`: Full text of the Mishna

2. **citations**: Contains citation texts extracted from the Gemara
   - `id`: Primary key (also serves as sequential order in the text)
   - `daf`: Location reference
   - `citation`: Text of the citation

3. **matched**: Links citations to their source Mishnayot
   - `id`: Primary key
   - `mishna_daf`: Reference to the Mishna
   - `citation_id`: Reference to the citation ID
   - `citation_daf`: Location of the citation

## How It Works

### Step 1: Extract Citations
1. Extract Mishna texts from the Talmud
2. Extract citation texts (text between colons in the Gemara)
   
### Step 2: Match citations to mishnayot
1. Match citations to Mishnayot using longest common substring algorithm
   - Minimum threshold: 2 words in common

### Step 3: Find Consecutive Citations
1. Filter out Mishnayot that are only cited once
2. For each Mishna with multiple citations:
   - Check if citation IDs are consecutive (differ by 1)
   - Check if the citation texts are similar using `are_similar_citations()`
3. Group consecutive similar citations together

### Step 4: Similarity Check
Citations are considered similar if:
- They are exactly the same, OR
- They differ only by the "וכו" suffix, OR
- One text contains the other AND the length difference is within 20%

## Output
The script outputs groups of consecutive citations, showing:
- Mishna reference (daf)
- Citation text
- Citation locations (daf)
- Number instances in total found where a Mishna citation is consecutively repeated

## Current Status
-  Working on Bava Batra tractate
-  Next: Implement fuzzy matching using Levenshtein distance
-  Future: Expand to all of Shas

## Requirements
```
Python 3.x
sqlite3
```

## Example
```
Mishna 42a has consecutive citations:

  Citation 49a: "ולא לאיש חזקה בנכסי אשתו וכו"
  Citation 50b: "ולא לאיש חזקה בנכסי אשתו"

- Classified as a repeated citation
```

## Data Source
Talmud text from: https://raw.githubusercontent.com/Sefaria/Sefaria-Export/master/txt/Talmud/Bavli/Seder%20Nezikin/Bava%20Batra/Hebrew/Wikisource%20Talmud%20Bavli.txt

## Author
Yael Novick
December 2024
