# Query Engine

Query Engine is a small dependency-free DSL for searching JSON-like documents.
The current goal is to keep the grammar stable enough to translate to
JavaScript or TypeScript for browser use.

## Grammar v0.1

- `disk` searches all text in a document.
- `"disk full"` searches an exact phrase.
- `level:ERROR` searches a field value.
- `context.cpu >= 80` performs a numeric comparison.
- `message~/timeout|failed/` performs a regular expression search.
- `AND`, `OR`, `NOT`, `-term`, and parentheses compose expressions.
- Adjacent expressions mean `AND`: `level:ERROR disk`.

## Example

```python
from query_engine import search

documents = [
    {"level": "ERROR", "message": "Disk full", "context": {"cpu": 91}},
    {"level": "INFO", "message": "Heartbeat ok", "context": {"cpu": 12}},
]

results = search("level:ERROR context.cpu>=80", documents)
```

## Development Order

1. Fix the grammar in `query_engine/parser.py`.
2. Keep the public AST and data types in `query_engine/ast.py` and `query_engine/models.py`.
3. Add parser and matcher tests in `tests/`.
4. Keep runtime code dependency-free.
5. Split AI or application-specific integrations into separate packages.
