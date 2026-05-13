import tempfile
import unittest
from pathlib import Path

from query_engine.adapters.extractors import extract_text_file
from query_engine.reserved_words import DSL_RESERVED_WORDS, RESERVED_WORDS, SQL_RESERVED_WORDS


class ExtractorAndReservedWordTests(unittest.TestCase):
    def test_extract_plain_text_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "note.txt"
            path.write_text("alpha\n\nbeta", encoding="utf-8")

            document = extract_text_file(path)

        self.assertEqual(document.text, "alpha beta")
        self.assertEqual(document.title, "note")

    def test_extract_html_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "page.html"
            path.write_text("<html><title>Hello</title><script>x()</script><body>alpha beta</body></html>", encoding="utf-8")

            document = extract_text_file(path)

        self.assertEqual(document.title, "Hello")
        self.assertIn("alpha beta", document.text)
        self.assertNotIn("x()", document.text)

    def test_reserved_words_include_dsl_and_sql_words(self) -> None:
        self.assertIn("AND", DSL_RESERVED_WORDS)
        self.assertIn("SELECT", SQL_RESERVED_WORDS)
        self.assertIn("WHERE", RESERVED_WORDS)


if __name__ == "__main__":
    unittest.main()
