# extractor_pipeline.py
import requests
import json
from extractor import extract_mishnayot_and_citations
from match_consecutive import (match_citations,find_consecutive_similar_citations)


EXTRACTION_FILE = "all_extracted.json"


class ExtractionManager:
    """Manages all extracted mishnayot and citations across multiple sources."""
    def __init__(self, filename=EXTRACTION_FILE):
        self.filename = filename
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.mishnayot = data.get("mishnayot", [])
                self.citations = data.get("citations", [])
        except FileNotFoundError:
            self.mishnayot = []
            self.citations = []

    def add(self, mishnayot_list, citations_list,masechet):
        """Add extracted items from a source (URL/file) with indexed order."""
        start_index_m = len(self.mishnayot) + 1
        for i, m in enumerate(mishnayot_list, start=start_index_m):
          self.mishnayot.append({
            "id": i,
            "text": m["text"],
            "daf": m["daf"],
            "masechet": masechet
         })

        start_index_c = len(self.citations) + 1
        for i, c in enumerate(citations_list, start=start_index_c):
          self.citations.append({
             "id": i,
             "text": c["text"],
             "daf": c["daf"],
             "masechet": masechet
         })

    def save(self):
        """Save all extractions to JSON file."""
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump({
                "mishnayot": self.mishnayot,
                "citations": self.citations
            }, f, ensure_ascii=False, indent=2)

    def get_all_mishnayot(self):
        return self.mishnayot

    def get_all_citations(self):
        return self.citations

    def filter_mishnayot_by_source(self, source):
        return [x for x in self.mishnayot if x["source"] == source]

    def filter_citations_by_source(self, source):
        return [x for x in self.citations if x["source"] == source]


def fetch_text_from_url(url):
    """Fetches raw text from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""


def process_urls(url_list):
    manager = ExtractionManager()

    for url in url_list:
        text = fetch_text_from_url(url)
        if not text:
            continue

        mishnayot, citations, masechet = extract_mishnayot_and_citations(text)
        manager.add( mishnayot, citations,masechet)
        print(f"Processed {url}: {len(mishnayot)} mishnayot, {len(citations)} citations")

    manager.save()
    return manager


if __name__ == "__main__":
    urls = [
        "https://raw.githubusercontent.com/Sefaria/Sefaria-Export/master/txt/Talmud/Bavli/Seder%20Nezikin/Bava%20Batra/Hebrew/Wikisource%20Talmud%20Bavli.txt",
        "https://raw.githubusercontent.com/Sefaria/Sefaria-Export/refs/heads/master/txt/Talmud/Bavli/Seder%20Kodashim/Arakhin/Hebrew/Wikisource%20Talmud%20Bavli.txt",
        "https://raw.githubusercontent.com/Sefaria/Sefaria-Export/refs/heads/master/txt/Talmud/Bavli/Seder%20Kodashim/Bekhorot/Hebrew/Wikisource%20Talmud%20Bavli.txt",
        
    ]

    manager = process_urls(urls)

    # MATCH citations to mishnayot
    match_citations(manager)

    # Save updated structure
    manager.save()

    print(f"Unmatched citations: {len(manager.unmatched_citations)}")
    
# אחרי match_citations(manager)
    groups = find_consecutive_similar_citations(manager)

# lookup מהיר
    mishna_by_id = {m["id"]: m for m in manager.mishnayot}
    citation_by_id = {c["id"]: c for c in manager.citations}

    for group in groups[:5]:
       first = citation_by_id[group[0]]
       mishna_id = first["matched_mishna_id"]
       m = mishna_by_id[mishna_id]

       print("\n" + "="*60)
       print(f"Masechet: {m['masechet']}")
       print("Mishna:")
       print(f"Daf {m['daf']}")
       print(m["text"])

       for i, cid in enumerate(group, start=1):
         c = citation_by_id[cid]
         print(f"\nCitation {i}:")
         print(f"{c['text']}   Daf {c['daf']}")


