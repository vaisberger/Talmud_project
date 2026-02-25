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

def longest_ratio(a, b):
    raw = longest_consecutive_match(a, b)
    return raw / min(len(a), len(b)) if min(len(a), len(b)) else 0

def difference_penalty(a, b):
    set_a = set(a)
    set_b = set(b)

    missing = set_a - set_b
    return len(missing) / len(set_a) if set_a else 1


#spliting the mishna into windows the len of the citation and finding the best window 
def window_overlap_score(tokens_a, tokens_b, assume_a_shorter=False):
    """
    Computes maximal token overlap of the shorter sequence inside the longer one.

    If assume_a_shorter=True:
        tokens_a is treated as the fragment (citation → mishna)
        returns 0 if tokens_a > tokens_b

    If assume_a_shorter=False:
        function is symmetric (citation ↔ citation)
    """

    if assume_a_shorter:
        short, long = tokens_a, tokens_b
        if len(short) > len(long):
            return 0
    else:
        short, long = (tokens_a, tokens_b) if len(tokens_a) <= len(tokens_b) else (tokens_b, tokens_a)

    if not short:
        return 0

    best = 0
    short_set = set(short)

    for i in range(len(long) - len(short) + 1):
        window = long[i:i + len(short)]
        common = len(short_set & set(window))
        best = max(best, common / len(short))

    return best

def is_contained(a_text, b_text):
    """
    True if one normalized string is fully inside the other
    (after removing וכו, punctuation, finals, html, niqqud).
    """
    a = normalize_hebrew(a_text)
    b = normalize_hebrew(b_text)

    if not a or not b:
        return False

    return a in b or b in a


#combin both algorithems and calculates probabilistic OR
def similarity_score(a_text, b_text, directional=False):
    if is_contained(a_text, b_text):
        return 1.0
    a = normalize_hebrew(a_text).split()
    b = normalize_hebrew(b_text).split()

    overlap = window_overlap_score(a, b, assume_a_shorter=directional)

    if directional:
        # citation -> mishna
        longest = longest_consecutive_match(a, b)
        longest = longest / len(a) if len(a) else 0
        return 1 - (1 - overlap) * (1 - longest)

    else:
          # ----- citation ↔ citation -----
       longest = longest_ratio(a, b)
       penalty = difference_penalty(a, b)

       base = 1 - (1 - overlap) * (1 - longest)

      
       return base * (1 - penalty)

def order_conflict(a, b):
    """
    a, b = token lists
    Returns value in [0,1]
    0 = the same order
    1 = completely reversed order
    """

    common = [w for w in a if w in b]
    if len(common) < 3:
        return 0  # Very little information

    pos_a = [a.index(w) for w in common]
    pos_b = [b.index(w) for w in common]

    inversions = 0
    total = 0

    for i in range(len(common)):
        for j in range(i+1, len(common)):
            total += 1
            if (pos_a[i] - pos_a[j]) * (pos_b[i] - pos_b[j]) < 0:
                inversions += 1

    return inversions / total if total else 0


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
             score = similarity_score(citation["text"], mishna["text"],True)
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

        # 3. similar text
        a = normalize_hebrew(citation["text"]).split()
        b = normalize_hebrew(prev["text"]).split()

        base_sim = similarity_score(citation["text"], prev["text"], directional=False)

        conflict = order_conflict(a, b)

        if conflict > 0.6:
          similar = False
        else:
         similar = base_sim >= threshold


        if same_mishna and consecutive and similar:
            current_group.append(citation)
        else:
            if len(current_group) >= 2:
                consecutive_groups.append([c["id"] for c in current_group])
            current_group = [citation]

    if len(current_group) >= 2:
        consecutive_groups.append([c["id"] for c in current_group])

    return consecutive_groups


