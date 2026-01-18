# Talmud Citation Analysis Project

This project analyzes Talmud text to find cases where mishna citations are consecutively repeated.

## Project Structure

- `extractor.py` - Main extraction logic for mishnayot and citations
- `test_extractor.py` - Comprehensive unit tests for extraction
- `requirements.txt` - Python dependencies

## Current Status

**Step 1: Unit Tests** - Writing comprehensive unit tests for extraction logic.

## Talmud Structure

- **Mishnayot**: Start with `<big><strong>מתני׳</strong></big>`, `מתני׳ <big><strong>`, or `<big><strong>מתני'</strong></big>` and end with `:`
- **Gemara**: Starts with `<big><strong>גמ׳</strong></big>` and ends with `:`
- **Citations**: Found only in gemara sections, between 2 `:` markers
- **Chapter End**: `<strong>הדרן עלך` followed by `:` indicates chapter end (not connected to colons)

## Running Tests

```bash
python -m pytest test_extractor.py -v
```

Or:

```bash
python test_extractor.py
```
