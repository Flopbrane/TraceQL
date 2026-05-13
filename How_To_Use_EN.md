# Query Engine DSL How To Use

Query Engine is a small search DSL for plain text, JSON-like documents, browser pages, logs, and SQL-backed data.

## Basic Queries

```text
error
"disk full"
level:ERROR
context.cpu>=80
message~/timeout|failed/
level:ERROR AND disk
level:ERROR OR level:WARN
NOT debug
(level:ERROR OR level:WARN) disk
```

## Reserved Words

Do not use these words as special command-like words at the beginning of a query unless you mean the DSL or SQL meaning.

Query Engine DSL reserved words:

```text
AND OR NOT
```

Common SQL reserved words to avoid as field names or command-like query words:

```text
ADD ALL ALTER AND ANY AS ASC BETWEEN BY CASE CHECK COLUMN CREATE DELETE DESC
DISTINCT DROP ELSE END EXISTS FROM GROUP HAVING IN INDEX INSERT INTO IS JOIN
KEY LIKE LIMIT NOT NULL ON OR ORDER PRIMARY REGEXP SELECT SET TABLE THEN UNION
UPDATE VALUES WHEN WHERE
```

## Special Symbols

These symbols have meaning in the DSL:

```text
: < <= > >= == != ~ /.../ "..." ( ) -term
```

## Writing Literal Words

If a document starts with a reserved word such as `AND`, `OR`, or `NOT`, search it as a phrase:

```text
"AND then the process restarted"
"OR condition"
"NOT available"
```

For exact text, prefer double quotes. For field search, use `field:value`.

## Field Names

Use simple ASCII field names:

```text
title
text
url
metadata.domain
context.cpu
```

Avoid SQL reserved words as field names. Prefer `created_at` over `time`, `record_type` over `type`, and `body_text` over `text` when designing database tables.

## Plain Text Files

Supported extraction targets:

- `.txt`, `.md`, `.rst`, `.csv`, `.json`, `.jsonl`, `.log`
- `.html`, `.htm`, `.xhtml`
- `.pdf`
- `.docx`

Example:

```python
from query_engine import extract_text_file, search

document = extract_text_file("manual.pdf").to_document()
results = search("install AND error", [document])
```
