from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from query_engine import search

documents = [
    {"level": "ERROR", "message": "Disk full on worker 1", "context": {"cpu": 91}},
    {"level": "INFO", "message": "Heartbeat ok", "context": {"cpu": 12}},
]

results = search("level:ERROR context.cpu>=80", documents)

for result in results:
    print(result.document)
