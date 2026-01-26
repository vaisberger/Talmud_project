"""
Matches extracted citations to Mishnayot.
Designed to be called from extractor_pipeline.py
"""

import re

# ---------------------------
# Hebrew normalization
# ---------------------------

FINAL_LETTERS = {
    "ך": "כ",
    "ם": "מ",
    "ן": "נ",
    "ף": "פ",
    "ץ": "צ",
}

def clean_text_for_matching(text):
    return re.sub(r"^[^\u05D0-\u05EA]*|[^\u05D0-\u05EA]*$", "", text)

def normalize_hebrew(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)              # HTML
    text = re.sub(r"[\u0591-\u05C7]", "", text)       # niqqud

    for f, r in FINAL_LETTERS.items():
        text = text.replace(f, r)

    text = re.sub(r"[^\u05D0-\u05EA\s]", " ", text)   # punctuation
    text = text.replace("וכו", "")
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ---------------------------
# Matching logic
# ---------------------------
#longest common string with the text being tokenized
def longest_consecutive_match(c_tokens, m_tokens) -> int:
    max_run = 0
    for i in range(len(c_tokens)):
        for j in range(len(m_tokens)):
            k = 0
            while (
                i + k < len(c_tokens)
                and j + k < len(m_tokens)
                and c_tokens[i + k] == m_tokens[j + k]
            ):
                k += 1
            max_run = max(max_run, k)
    return max_run
#spliting the mishna into windows the len of the citation and finding the best window 
def window_overlap_score(c_tokens, m_tokens):
    if len(c_tokens) > len(m_tokens):
        return 0

    best = 0
    for i in range(len(m_tokens) - len(c_tokens) + 1):
        window = m_tokens[i:i+len(c_tokens)]
        common = len(set(window) & set(c_tokens))
        score = common / len(c_tokens)
        best = max(best, score)

    return best


#combin both algorithems and calculates probabilistic OR
def similarity_score(citation_text, mishna_text):
    c_tokens = normalize_hebrew(clean_text_for_matching(citation_text)).split()
    m_tokens = normalize_hebrew(clean_text_for_matching(mishna_text)).split()

    if len(c_tokens) < 2:
        return 0.0

    overlap = window_overlap_score(c_tokens, m_tokens)
    longest = longest_consecutive_match(c_tokens, m_tokens) / len(c_tokens)

    return 1 - (1-overlap)*(1-longest)






# ---------------------------
# Public API
# ---------------------------

def match_citations(manager, threshold = 0.55):
    """
    Mutates manager.mishnayot and manager.citations in-place.
    """

    # init
    for m in manager.mishnayot:
        m["citations"] = []

    unmatched = []

    for citation in manager.citations:
        best_score = 0.0
        best_mishna = None

        for mishna in manager.mishnayot:
            if mishna["masechet"]==citation["masechet"]:
             score = similarity_score(citation["text"], mishna["text"])
             if score > best_score:
                best_score = score
                best_mishna = mishna

        if best_mishna and best_score >= threshold:
            best_mishna["citations"].append(citation["id"])
            citation["matched_mishna_id"] = best_mishna["id"]
        else:
            citation["matched_mishna_id"] = None
            unmatched.append(citation["id"])

    manager.unmatched_citations = unmatched

def find_consecutive_similar_citations(manager, threshold: float = 0.8):
    """
    Finds sequences of consecutive citations that are very similar and linked to the same mishna.
    """

    consecutive_groups = []

    # Only matched citations, sorted by ID
    matched = sorted(
        [c for c in manager.citations if c.get("matched_mishna_id")],
        key=lambda x: x["id"]
    )

    current_group = []

    for citation in matched:
        if not current_group:
            current_group.append(citation)
            continue

        prev = current_group[-1]

        # 1. same mishna
        same_mishna = citation["matched_mishna_id"] == prev["matched_mishna_id"]

        # 2. consecutive in index
        consecutive = citation["id"] == prev["id"] + 1

        if citation["id"]==3461:
                print("hi")
        # 3. similar text
        similar = similarity_score(citation["text"], prev["text"]) >= threshold

        if same_mishna and consecutive and similar:
            current_group.append(citation)
        else:
            if len(current_group) >= 2:
                consecutive_groups.append([c["id"] for c in current_group])
            current_group = [citation]

    if len(current_group) >= 2:
        consecutive_groups.append([c["id"] for c in current_group])

    return consecutive_groups


