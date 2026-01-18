"""
Unit tests for Talmud text extraction.
Tests cover edge cases for mishna and citation extraction.
"""

import unittest
import textwrap
from extractor import extract_mishnayot_and_citations


class TestMishnaExtraction(unittest.TestCase):
    """Test cases for mishna extraction."""

    def test_simple_mishna_extraction(self):
        text = "<big><strong>מתני׳</strong></big>\nThe mishna text ends here:"
        mishnayot, _ = extract_mishnayot_and_citations(text)
        self.assertEqual(len(mishnayot), 1)
        self.assertIn("The mishna text ends here", mishnayot[0])

    def test_multiple_mishnayot(self):
        text = textwrap.dedent("""\
            <big><strong>מתני׳</strong></big>
            First mishna:
            <big><strong>גמ׳</strong></big>
            Some gemara
            <big><strong>מתני׳</strong></big>
            Second mishna:
            <big><strong>גמ׳</strong></big>""")
        mishnayot, _ = extract_mishnayot_and_citations(text)
        self.assertEqual(len(mishnayot), 2)
        self.assertIn("First mishna", mishnayot[0])
        self.assertIn("Second mishna", mishnayot[1])

    def test_mishna_multiline(self):
        text = textwrap.dedent("""\
            <big><strong>מתני׳</strong></big>
            Line one of mishna
            Line two of mishna:
            <big><strong>גמ׳</strong></big>""")
        mishnayot, _ = extract_mishnayot_and_citations(text)
        self.assertEqual(len(mishnayot), 1)
        self.assertIn("Line one", mishnayot[0])
        self.assertIn("Line two", mishnayot[0])


class TestCitationExtractionEdgeCases(unittest.TestCase):
    """Citation extraction edge case tests."""

    def test_single_line_middle(self):
        text = "<big><strong>גמ׳</strong></big>\nSome text :citation: more text"
        _, citations = extract_mishnayot_and_citations(text)
        self.assertEqual(citations, ["citation"])

    def test_single_line_start(self):
        text = "<big><strong>גמ׳</strong></big>\n:citation: more text"
        _, citations = extract_mishnayot_and_citations(text)
        self.assertEqual(citations, ["citation"])

    def test_single_line_end(self):
        text = "<big><strong>גמ׳</strong></big>\nSome text :citation:"
        _, citations = extract_mishnayot_and_citations(text)
        self.assertEqual(citations, ["citation"])

    def test_single_line_exact(self):
        text = "<big><strong>גמ׳</strong></big>\n:citation:"
        _, citations = extract_mishnayot_and_citations(text)
        self.assertEqual(citations, ["citation"])

    def test_multiline_middle_to_next_line_start(self):
        text = "<big><strong>גמ׳</strong></big>\nSome text :citation\ncontinues here:"
        _, citations = extract_mishnayot_and_citations(text)
        self.assertEqual(citations, ["citation\ncontinues here"])

    def test_multiline_start_colon_new_line(self):
        text = "<big><strong>גמ׳</strong></big>\n:citation continues\nand ends midline: more text"
        _, citations = extract_mishnayot_and_citations(text)
        self.assertEqual(citations, ["citation continues\nand ends midline"])

    def test_multiple_citations_one_line(self):
        text = "<big><strong>גמ׳</strong></big>\n:citation1: middle :citation2: end"
        _, citations = extract_mishnayot_and_citations(text)
        self.assertEqual(citations, ["citation1", "citation2"])

    def test_multiple_citations_multiline(self):
        text = "<big><strong>גמ׳</strong></big>\n:citation1: text\n:citation2 spanning\nmultiple lines:"
        _, citations = extract_mishnayot_and_citations(text)
        self.assertEqual(
            citations,
            ["citation1", "citation2 spanning\nmultiple lines"]
        )

    def test_structural_colons_not_detected(self):
        text = (
            "<big><strong>מתני׳</strong></big>\nMishna ends:\n"
            "<big><strong>גמ׳</strong></big>\nGemara ends:\n"
            "<strong>הדרן עלך:"
        )
        _, citations = extract_mishnayot_and_citations(text)
        self.assertEqual(citations, [])

    def test_structural_colons_ignored_but_citation_detected(self):
        text = textwrap.dedent("""\
            <big><strong>מתני׳</strong></big>
            Mishna ends:
            <big><strong>גמ׳</strong></big>
            Some gemara text :Valid citation: continues
            <strong>הדרן עלך:""")
        _, citations = extract_mishnayot_and_citations(text)
        self.assertEqual(citations, ["Valid citation"])

    def test_colon_after_chapter_end_ignored(self):
        text = "<big><strong>גמ׳</strong></big>\n<strong>הדרן עלך: Some text :Valid citation:"
        _, citations = extract_mishnayot_and_citations(text)
        self.assertEqual(citations, ["Valid citation"])

    def test_real_world_example(self):
        text = textwrap.dedent("""\
            <big><strong>גמ׳</strong></big>\nText:First citation
            spans lines:Text:Second citation
            also spans:More text""")
        _, citations = extract_mishnayot_and_citations(text)
        self.assertEqual(
            citations,
            ["First citation\nspans lines", "Second citation\nalso spans"]
        )
       
    def test_citation_not_across_daf(self):
      text = (
        "<big><strong>גמ׳</strong></big>\n"
        "Text:This is citation part 1\n"
        "Daf 160a\n"
        "Text:This is not a citation"
       )

      _, citations = extract_mishnayot_and_citations(text)
      self.assertEqual(citations, [])



class TestIntegration(unittest.TestCase):
    """Integration tests for full extraction."""

    def test_full_text_multiple_mishnayot_and_citations(self):
        text = textwrap.dedent("""\
            <big><strong>מתני׳</strong></big>
            Mishna text 1:
            <big><strong>גמ׳</strong></big>
            Gemara text :Citation 1: and :Citation 2: more gemara
            <big><strong>מתני׳</strong></big>
            Mishna text 2:
            <strong>הדרן עלך:""")
        mishnayot, citations = extract_mishnayot_and_citations(text)
        self.assertEqual(len(mishnayot), 2)
        self.assertEqual(citations, ["Citation 1", "Citation 2"])


if __name__ == "__main__":
    unittest.main()
