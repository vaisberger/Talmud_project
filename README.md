# Talmud Consecutive Citation Finder

## Project Overview
This project analyzes the Talmud to find instances where a Mishna citation is consecutively repeated in the Gemara text.

## Goal
Answer the question: "How often is a Mishna citation consecutively repeated in the Talmud?"

## What counts as "consecutively repeated"?
- Two or more citations that appear one after another in the Gemara (sequential citation IDs)
- All citations reference the same Mishna
- The citation texts are nearly identical (with minor differences like the suffix "וכו")

### Current Results 
Using a **40% similarity threshold**, we found **6 instances** across Shas where Mishnayot are cited consecutively:

1. **Bava Batra 42a** - cited on 49a and 50b 
2. **Berakhot 51b** - cited on 52a and 52b 
3. **Ketubot 22a** - cited on 23a 
4. **Sanhedrin 40a** - cited on 42a
5. **Shabbat 142b** - cited on same page 
6. **Yevamot 25a** - cited on 119a and 119b

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
   * `id`: Primary key
   * `masechet`: Tractate name
   * `daf`: Location reference (e.g., "2a", "42a")
   * `mishna`: Full text of the Mishna

2. **citations**: Contains citation texts extracted from the Gemara
   * `id`: Primary key (sequential order in the text)
   * `masechet`: Tractate name
   * `daf`: Location reference
   * `citation`: Text of the citation

3. **matched**: Links citations to their source Mishnayot
   * `id`: Primary key
   * `masechet`: Tractate name
   * `mishna_daf`: Reference to the Mishna location
   * `citation_id`: Reference to the citation ID
   * `citation_daf`: Location of the citation in Gemara

## How It Works
### Step 1: Extract Citations
* Parse Talmud text files from Sefaria
* Extract Mishna texts (marked with `<big><strong>מתני׳</strong></big>`)
* Extract citation texts (text between colons in the Gemara)
* Store in SQLite database

### Step 2: Match Citations to Mishnayot
* Use **longest common substring algorithm** to match citations to source Mishnayot
* Minimum threshold: **2 consecutive matching words**
* Only matches within the same tractate (masechet)

### Step 3: Find Consecutive Citations
1. Query all Mishnayot that have 2+ citations
2. For each Mishna with multiple citations:
   * Check if citation IDs are consecutive (differ by 1)
   * Check if citations are on consecutive or nearby pages
   * Apply similarity check using `check_similar_citations()`
3. Group consecutive similar citations together

### Step 4: Similarity Algorithm
Citations are considered similar if:

1. **Exact match**: Texts are identical after stripping whitespace
2. **"וכו'" handling**: After removing the "וכו'" suffix, texts match
3. **Substring with length threshold**: 
   * One text contains the other (full vs. partial quotation)
   * Length difference is within **40%** (configurable threshold)
   * Formula: `shorter_length / longer_length >= 0.6`

**Example**: 
* Text 1: "ולא לאיש חזקה בנכסי אשתו" (6 words)
* Text 2: "ולא לאיש חזקה בנכסי אשתו וכו'" (7 words)
* Ratio: 6/7 = 0.857 - **Similar** 

### Threshold Tuning
* **40% threshold**: More conservative, giving very similar citations (6 instances)
* **45% threshold**: More relaxed, giving slightly less similar results (10 instances)
* Currently using 40% 

### Output Format
```
[('Bava Batra', '42a', "ולא לאיש חזקה בנכסי אשתו וכו'\n", '49a'), 
 ('Bava Batra', '42a', 'ולא לאיש חזקה בנכסי אשתו\n', '50b')]

found 6 instances where a Mishna is cited consecutively in the shas
```

## Current Status
-  Completed analysis of Bava Batra
-  Currently expanding analysis to entire Shas
-  Next: Implement fuzzy matching using Levenshtein distance
-  Future: Complete analysis of all shas with Levenshtein distance

## Requirements
```
Python 3.x
sqlite3
```

## Data Source
Talmud text from: https://raw.githubusercontent.com/Sefaria/Sefaria-Export/master/txt/Talmud/Bavli/Seder%20Nezikin/Bava%20Batra/Hebrew/Wikisource%20Talmud%20Bavli.txt

## Author
Yael Novick
December 2024
