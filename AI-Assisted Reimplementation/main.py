# extractor_pipeline.py
import requests
import json
from extractor import extract_mishnayot_and_citations

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

    def add(self, source, mishnayot_list, citations_list):
        """Add extracted items from a source (URL/file) with indexed order."""
        start_index_m = len(self.mishnayot) + 1
        for i, m in enumerate(mishnayot_list, start=start_index_m):
            self.mishnayot.append({"id": i, "text": m})

        start_index_c = len(self.citations) + 1
        for i, c in enumerate(citations_list, start=start_index_c):
            self.citations.append({"id": i,"text": c})

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

        mishnayot, citations = extract_mishnayot_and_citations(text)
        manager.add(url, mishnayot, citations)
        print(f"Processed {url}: {len(mishnayot)} mishnayot, {len(citations)} citations")

    manager.save()
    return manager


if __name__ == "__main__":
    urls = [
        "https://raw.githubusercontent.com/Sefaria/Sefaria-Export/master/txt/Talmud/Bavli/Seder%20Nezikin/Bava%20Batra/Hebrew/Wikisource%20Talmud%20Bavli.txt",
      
    ]

    manager = process_urls(urls)

    # Example: access all citations
    all_citations = manager.get_all_citations()
    print(f"Total citations collected: {len(all_citations)}")
