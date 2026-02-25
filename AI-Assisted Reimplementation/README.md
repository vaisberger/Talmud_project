# Talmud Citation Analysis Project

A pipeline for analyzing Talmud text to extract mishnayot and citations, match citations to their referenced mishnayot, detect consecutive repeated citations, and produce structured JSON output for further analysis.

---

## Project Structure

| File | Description |
|------|-------------|
| `extractor.py` | Extracts mishnayot and citations from raw Talmud HTML text |
| `match_consecutive.py` | Matches extracted citations to mishnayot using Hebrew normalization and similarity scoring |
| `extractor_pipeline.py` | Main pipeline: fetches text from URLs, extracts mishnayot and citations, matches them, and saves JSON |
| `test_extractor.py` | Unit tests for extraction logic |
| `requirements.txt` | Python dependencies (`requests`, `pytest`, etc.) |
| `all_extracted.json` | JSON file storing all extracted mishnayot, citations, and matches |

---

## Current Status

- **Step 1 — Extraction:** Mishnayot and citations are extracted and stored in JSON.
- **Step 2 — Citation Matching:** Each citation is matched to the best-fitting mishna using normalized token similarity.
- **Step 3 — Consecutive Detection:** Consecutive highly similar citations linked to the same mishna are grouped.
- **Step 4 — Reporting:** Unmatched citations are tracked, and JSON can be used for further analysis.

---

## Running the Pipeline

```bash
python extractor_pipeline.py
```

This generates or updates `all_extracted.json`.

---

## Talmud Structure Rules

| Element | Rule |
|---------|------|
| **Mishnayot** | Start with `מתני׳` (or variants), typically end with `:` |
| **Gemara** | Starts with `גמ׳`, ends with `:` |
| **Citations** | Found in Gemara sections, usually between colons `:` |
| **Chapter End** | `הדרן עלך` followed by `:` — indicates chapter end; not treated as a citation |

---

## Hebrew Text Normalization

Matching is performed only on normalized Hebrew text. Normalization includes:

- Removing HTML tags
- Removing niqqud
- Converting final letters: `ך → כ`, `ם → מ`, `ן → נ`, `ף → פ`, `ץ → צ`
- Removing punctuation
- Removing the suffix `וכו`
- Collapsing multiple spaces

This ensures matching is formatting-independent and consistent across tractates.

---

## Citation Matching Logic

Each citation is matched only against mishnayot from the same masechet. The similarity score combines multiple signals:

### 1. Containment Check

If one normalized text is fully contained inside the other:

```
normalize(a) in normalize(b)
```

The similarity score is set to `1.0`. This handles shortened or partially quoted citations.

### 2. Token Window Overlap

The citation is treated as a fragment of the mishna. The algorithm searches for the best matching window of equal token length inside the mishna and measures token overlap.

### 3. Longest Consecutive Token Match

The algorithm measures the longest uninterrupted sequence of matching tokens between citation and mishna. The final similarity score is calculated as:

```
similarity = 1 - (1 - overlap) * (1 - longest_run)
```

This acts as a probabilistic OR between local overlap and phrase continuity.

---

## Logical Order Conflict Detection

Some citations may contain almost identical words but represent reversed logical meaning, for example:

```
שכח מה שאמר לו רבו
שכח רבו מה שאמר לו
```

or:

```
בפני נכתב חציו ובפני נחתם כולו
בפני נכתב כולו ובפני נחתם חציו
```

To prevent false grouping, consecutive citations are compared using **token order analysis**. The algorithm measures inversion in the ordering of shared tokens — high inversion indicates semantic reversal. Such citations are not grouped together even if their similarity score is high.

---

## Output

The pipeline produces a structured JSON file (`all_extracted.json`) containing:

- Mishnayot
- Citations
- Citation-to-mishna matches
- Unmatched citations
- Consecutive similar citation groups
