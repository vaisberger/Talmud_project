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
Using a **40% similarity threshold**, we found **7 instances** across Shas where Mishnayot are cited consecutively:

1. **Bava Batra 42a** - cited on 49a and 50b 
2. **Bava Batra 68b** - cited on 69a (twice consecutively)
3. **Berakhot 51b** - cited on 52a and 52b 
4. **Ketubot 22a** - cited on 23a 
5. **Sanhedrin 40a** - cited on 42a
6. **Shabbat 142b** - cited on same page 
7. **Yevamot 25a** - cited on 119a and 119b

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

### Step 1: Extract Citations and Mishnayot
* Parse Talmud text files from Sefaria
* Extract Mishna texts (marked with `<big><strong>מתני׳</strong></big>`)
* Extract citation texts (text between colons in the Gemara)
* Store in SQLite database

### Step 2: Match Citations to Mishnayot
The matching algorithm uses a **hybrid approach** combining two metrics to identify which Mishna a citation is quoting from:

1. **Longest Common Substring**: Finds the longest sequence of consecutive matching words
   * Minimum threshold: **2 consecutive matching words**
   
2. **Token Overlap Score**: Measures how many words from the citation appear in the Mishna
   ```python
   token_overlap_score = (shared_words) / (total_citation_words)
   ```
   * Minimum threshold: **50% overlap**

**Matching Criteria**:
A citation is matched to a source Mishna if:
* Longest common substring ≥ 2 words **AND**
* Token overlap score > 0.5 (50% of citation words appear in Mishna)
* Both texts are from the same tractate (masechet)

This hybrid approach ensures citations are matched only when they have both:
- Consecutive word sequences (meaningful phrases from the Mishna)
- Sufficient overall word overlap (not just a short coincidental match)

### Step 3: Find Consecutive Citations
1. Query all Mishnayot that have 2+ citations
2. For each Mishna with multiple citations:
   * Check if citation IDs are consecutive (differ by 1)
   * Apply similarity check using `check_similar_citations()`
3. Group consecutive similar citations together

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

[('Bava Batra', '68b', '(ולא את חרוב המורכב ולא סדן השקמה\n', '69a'), 
 ('Bava Batra', '68b', "ולא את חרוב המורכב ולא סדן השקמה וכו'\n", '69a')]

found 7 instances where a Mishna is cited consecutively in the shas
```

## Development History

### Matching Algorithm Evolution (Step 2: Citations → Mishnayot)
1. **Initial approach**: Longest common substring only
   * Simple but sometimes matched unrelated texts with short common phrases
   
2. **Current approach**: Hybrid token overlap + longest common substring
   * Combines phrase-level matching with overall word coverage
   * More accurate matching of citations to source Mishnayot

### Citation Comparison Evolution (Step 4: Comparing Citations)
1. **Initial approach**: Simple substring matching with length threshold
   * Used 40% similarity threshold
   
2. **Levenshtein distance attempt**: Measured character-level edit distance between citations
   * **Conclusion**: Not suitable for this purpose
   * Character-level differences don't capture semantic similarity well for citation comparison
   
3. **Back to refined substring approach**: 
   * Kept the substring + length threshold method (40%)
   * Proved more effective than Levenshtein for comparing similar citations

## Current Status
-  Completed analysis of Bava Batra
-  Expanded analysis to entire Shas
-  Tested Levenshtein distance (determined unsuitable)
-  Implemented token overlap scoring for improved matching citation to mishna accuracy
-  Final results validation in progress

## Next Step: AI-Assisted Reimplementation

The next phase of this project is to reimplement the system using Cursor (AI-assisted development).

Since the expected results and validation criteria are already known, this phase focuses on:
- Evaluating AI-assisted development workflows in a controlled setting
- Comparing AI-generated code with the original implementation
- Improving structure, readability, and maintainability
- Strengthening unit tests and validation logic

This allows direct comparison between the original and AI-assisted implementations while maintaining result correctness.

## Requirements
```
Python 3.x
sqlite3
```

## Data Source
Talmud text from Sefaria:
`https://raw.githubusercontent.com/Sefaria/Sefaria-Export/master/txt/Talmud/Bavli/`

## Author
Yael Novick
December 2024
