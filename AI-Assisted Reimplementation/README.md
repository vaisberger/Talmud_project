# Talmud Citation Analysis Project

This project analyzes Talmud text to extract mishnayot and citations, and matches citations to the mishnayot they reference. It can identify cases where citations are repeated consecutively and provides a structured JSON output.

---

## Project Structure

- `extractor.py` – Extracts mishnayot and citations from raw Talmud text.
- `match_consecutive.py` – Matches extracted citations to mishnayot using Hebrew text normalization and similarity scoring.
- `extractor_pipeline.py` – Main pipeline: fetches text from URLs, extracts mishnayot and citations, matches them, and saves JSON.
- `test_extractor.py` – Comprehensive unit tests for extraction logic.
- `requirements.txt` – Python dependencies (`requests`, `pytest`, etc.).
- `all_extracted.json` – JSON file storing all extracted mishnayot, citations, and matches.

---

## Current Status

- **Step 1: Extraction** – Mishnayot and citations are extracted and stored in JSON.  
- **Step 2: Citation Matching** – Each citation is matched to the best-fitting mishna using `similarity_score`.  
- **Step 3: Reporting** – Unmatched citations are tracked, and JSON can be used for further analysis.

---

## Talmud Structure Rules

- **Mishnayot**: Start with `<big><strong>מתני׳</strong></big>` (or variants) and typically end with `:`.  
- **Gemara**: Starts with `<big><strong>גמ׳</strong></big>` and ends with `:`.  
- **Citations**: Found in Gemara sections, usually between colons `:`.  
- **Chapter End**: `<strong>הדרן עלך` followed by `:` indicates chapter end, not a citation.

---

## Hebrew Text Normalization

- Removes HTML tags, niqqud, and punctuation.
- Converts final letters (`ך, ם, ן, ף, ץ`) to standard forms.
- Removes common suffixes like `וכו`.
- Collapses multiple spaces.

---

## Running the Pipeline

```bash
python extractor_pipeline.py
