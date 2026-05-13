import unittest

from query_engine.documents import from_text, normalize_text
from query_engine.matcher import match_query


class DocumentTests(unittest.TestCase):
    def test_normalize_text_collapses_whitespace(self) -> None:
        self.assertEqual(normalize_text("alpha\n\n beta\tgamma"), "alpha beta gamma")

    def test_text_document_can_be_searched(self) -> None:
        document = from_text("Disk full on worker 1", title="incident").to_document()

        self.assertTrue(match_query("title:incident disk", document))


if __name__ == "__main__":
    unittest.main()
