import unittest

from query_engine.adapters.browser import BrowserPage, browser_page_to_document
from query_engine.adapters.logs import log_to_document
from query_engine.evaluators.memory import match_query
from query_engine.evaluators.sql import compile_sql_where


class AdapterAndSqlTests(unittest.TestCase):
    def test_browser_page_adapter_creates_searchable_document(self) -> None:
        page = BrowserPage(
            title="OpenAI Docs",
            url="https://platform.openai.com/docs",
            text="Agents and responses documentation",
            metadata={"domain": "platform.openai.com"},
        )
        document = browser_page_to_document(page)

        self.assertTrue(match_query("title:OpenAI metadata.domain:openai.com", document))

    def test_log_adapter_keeps_level_and_text(self) -> None:
        document = log_to_document({"level": "ERROR", "message": "Disk full", "code": 507})

        self.assertTrue(match_query("level:ERROR disk", document))

    def test_sql_compiler_builds_where_and_params(self) -> None:
        result = compile_sql_where("level:ERROR AND count>=3")

        self.assertEqual(result.where_sql, '("level" LIKE ?) AND ("count" >= ?)')
        self.assertEqual(result.params, ("%ERROR%", 3.0))


if __name__ == "__main__":
    unittest.main()
