import unittest

from query_engine.matcher import match_query, search

DOCUMENTS = [
    {
        "level": "ERROR",
        "message": "Disk full on worker 1",
        "context": {"cpu": 91, "tags": ["storage", "urgent"]},
    },
    {
        "level": "INFO",
        "message": "Heartbeat ok",
        "context": {"cpu": 12, "tags": ["health"]},
    },
]


class MatcherTests(unittest.TestCase):
    def test_field_and_term_match(self) -> None:
        self.assertTrue(match_query("level:ERROR disk", DOCUMENTS[0]))
        self.assertFalse(match_query("level:ERROR heartbeat", DOCUMENTS[0]))

    def test_comparison_match(self) -> None:
        self.assertTrue(match_query("context.cpu >= 80", DOCUMENTS[0]))
        self.assertFalse(match_query("context.cpu >= 80", DOCUMENTS[1]))

    def test_regex_and_not_match(self) -> None:
        self.assertTrue(match_query("message~/disk|timeout/ NOT heartbeat", DOCUMENTS[0]))
        self.assertFalse(match_query("NOT heartbeat", DOCUMENTS[1]))

    def test_search_returns_matching_documents(self) -> None:
        results = search("level:ERROR OR context.cpu<20", DOCUMENTS)

        self.assertEqual([result.document["level"] for result in results], ["ERROR", "INFO"])


if __name__ == "__main__":
    unittest.main()
