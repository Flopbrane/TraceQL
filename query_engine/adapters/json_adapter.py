# -*- coding: utf-8 -*-
"""JSON or JSONL 形式の文書をロードするアダプター。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

Record = dict[str, Any]


class JsonAdapter:
    def __init__(
        self,
        load_file_path: str | Path,
    ) -> None:

        self.load_file_path = Path(load_file_path)

    def load(self) -> list[Record]:

        suffix: str = self.load_file_path.suffix.lower()

        if suffix == ".jsonl":
            return self._load_jsonl()

        if suffix == ".json":
            return self._load_json()

        raise ValueError(f"Unsupported file: {suffix}")

    def _load_json(self) -> list[Record]:

        with open(
            self.load_file_path,
            "r",
            encoding="utf-8",
        ) as f:
            data: dict[str, Any] = cast(dict[str, Any], json.load(f))

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            return [data]

        raise ValueError("Invalid JSON structure")

    def _load_jsonl(self) -> list[Record]:

        rows: list[Record] = []

        with open(
            self.load_file_path,
            "r",
            encoding="utf-8",
        ) as f:
            for line in f:
                line: str = line.strip()

                if not line:
                    continue

                rows.append(json.loads(line))

        return rows