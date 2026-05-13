# Query Engine DSL 使い方

Query Engine は、平文、JSON風の文書、ブラウザページ、ログ、SQL backed data に使うための小さな検索DSLです。

## 基本の検索

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

## 予約語

次の言葉は、DSLやSQLのコマンドとして使うため、文章の冒頭やフィールド名として使うときは注意してください。

Query Engine DSL の予約語:

```text
AND OR NOT
```

フィールド名やコマンド風の検索語として避けたいSQL予約語:

```text
ADD ALL ALTER AND ANY AS ASC BETWEEN BY CASE CHECK COLUMN CREATE DELETE DESC
DISTINCT DROP ELSE END EXISTS FROM GROUP HAVING IN INDEX INSERT INTO IS JOIN
KEY LIKE LIMIT NOT NULL ON OR ORDER PRIMARY REGEXP SELECT SET TABLE THEN UNION
UPDATE VALUES WHEN WHERE
```

## 特別な記号

次の記号はDSL内で特別な意味を持ちます。

```text
: < <= > >= == != ~ /.../ "..." ( ) -term
```

## 文章として検索したい場合

文書が `AND`、`OR`、`NOT` のような予約語で始まる場合は、ダブルクォートで囲んでください。

```text
"AND then the process restarted"
"OR condition"
"NOT available"
```

完全一致に近い検索をしたい場合も、ダブルクォートを使うのがおすすめです。フィールド検索は `field:value` を使います。

## フィールド名

フィールド名は、シンプルなASCII名がおすすめです。

```text
title
text
url
metadata.domain
context.cpu
```

DB設計ではSQL予約語をフィールド名にしないでください。たとえば `time` より `created_at`、`type` より `record_type`、汎用本文なら `text` より `body_text` の方が安全です。

## 平文ファイル

現在の抽出対象:

- `.txt`, `.md`, `.rst`, `.csv`, `.json`, `.jsonl`, `.log`
- `.html`, `.htm`, `.xhtml`
- `.pdf`
- `.docx`

例:

```python
from query_engine import extract_text_file, search

document = extract_text_file("manual.pdf").to_document()
results = search("install AND error", [document])
```
