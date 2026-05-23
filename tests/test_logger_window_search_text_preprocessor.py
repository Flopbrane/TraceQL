# -*- coding: utf-8 -*-
"""Tests for LogViewer search text preprocessing."""
from __future__ import annotations

import unittest
from typing import Any, Mapping

from logger_window.logs.search_text_preprocessor import (
    build_search_text_datetime,
    collect_log_dates,
)


class SearchTextPreprocessorTests(unittest.TestCase):
    def test_single_day_time_query_uses_loaded_log_date(self) -> None:
        rows: list[Mapping[str, Any]] = [
            {"time": "2026-04-24T01:15:00+00:00"},
            {"time": "2026-04-24T01:16:00+00:00"},
        ]

        self.assertEqual(
            build_search_text_datetime("10:15", rows, "Asia/Tokyo"),
            "2026-04-24 10:15",
        )

    def test_multi_day_time_query_remains_time_only(self) -> None:
        rows: list[Mapping[str, Any]] = [
            {"time": "2026-04-23T01:15:00+00:00"},
            {"time": "2026-04-24T01:15:00+00:00"},
        ]

        self.assertEqual(
            build_search_text_datetime("10:15", rows, "Asia/Tokyo"),
            "10:15",
        )

    def test_time_range_uses_loaded_log_date(self) -> None:
        rows: list[Mapping[str, Any]] = [
            {"time": "2026-04-24T01:15:00+00:00"},
        ]

        self.assertEqual(
            build_search_text_datetime("10:15..10:16", rows, "Asia/Tokyo"),
            "2026-04-24 10:15..2026-04-24 10:16",
        )

    def test_collect_log_dates_ignores_rows_without_valid_time(self) -> None:
        rows: list[Mapping[str, Any]] = [
            {"time": "2026-04-24T01:15:00+00:00"},
            {"time": None},
            {"message": "missing time"},
        ]

        self.assertEqual(
            [item.isoformat() for item in collect_log_dates(rows, "Asia/Tokyo")],
            ["2026-04-24"],
        )


if __name__ == "__main__":
    unittest.main()
