import sys
import unittest
from pathlib import Path

LOGGER_WINDOW = Path(__file__).resolve().parents[1] / "logger_window"
if str(LOGGER_WINDOW) not in sys.path:
    sys.path.insert(0, str(LOGGER_WINDOW))

from logs.log_types import LogDict  # noqa: E402
from logs.search_matcher import match_search_query  # noqa: E402


def sample_log() -> LogDict:
    return {
        "level": "ERROR",
        "time": "2026-04-23T05:49:31+00:00",
        "trace_id": "trace-001",
        "where": {
            "file": "system_monitor.py",
            "function": "run_test",
            "line": 42,
        },
        "what": {
            "message": "system_gpu_status",
            "status": "failed",
        },
        "context": {
            "cpu_percent": 21.9,
            "gpu_mem_total_mb": 2048,
        },
        "output": "file",
    }


class LoggerWindowTraceQLBridgeTests(unittest.TestCase):
    def test_search_window_uses_traceql_field_aliases(self) -> None:
        log = sample_log()

        self.assertTrue(match_search_query(log, "message:system_gpu_status", "Asia/Tokyo"))
        self.assertTrue(match_search_query(log, "function:run_test file:system_monitor.py", "Asia/Tokyo"))
        self.assertTrue(match_search_query(log, "context.cpu_percent>=20", "Asia/Tokyo"))
        self.assertFalse(match_search_query(log, "level:INFO", "Asia/Tokyo"))

    def test_search_window_uses_traceql_boolean_and_sort_body(self) -> None:
        log = sample_log()

        self.assertTrue(match_search_query(log, "gpu AND level:ERROR sort by time desc", "Asia/Tokyo"))
        self.assertFalse(match_search_query(log, "gpu AND NOT level:ERROR", "Asia/Tokyo"))

    def test_search_window_keeps_date_term_search_working(self) -> None:
        log = sample_log()

        self.assertTrue(match_search_query(log, "2026-04-23", "Asia/Tokyo"))
        self.assertTrue(match_search_query(log, "14:49", "Asia/Tokyo"))


if __name__ == "__main__":
    unittest.main()
