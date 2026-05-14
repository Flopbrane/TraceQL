import tempfile
import unittest
from pathlib import Path

from query_engine import similarity
from query_engine.similarity import cached_document_vector, similarity_score, vectorize_text
from query_engine.utils import flatten_text, get_path


class SimilarityAndUtilsTests(unittest.TestCase):
    def test_get_path_reads_nested_mapping_and_sequence(self) -> None:
        document = {
            "context": {
                "devices": [
                    {"name": "cpu", "usage": 42},
                    {"name": "gpu", "usage": 88},
                ]
            }
        }

        self.assertEqual(get_path(document, "context.devices.1.name"), "gpu")
        self.assertEqual(get_path(document, "context.devices.1.usage"), 88)
        self.assertIsNone(get_path(document, "context.devices.gpu.name"))
        self.assertIsNone(get_path(document, "context.devices.99.name"))

    def test_flatten_text_keeps_nested_keys_and_values(self) -> None:
        text = flatten_text({"level": "ERROR", "context": {"gpu": ["high", 88]}})

        self.assertIn("level", text)
        self.assertIn("ERROR", text)
        self.assertIn("gpu", text)
        self.assertIn("high", text)
        self.assertIn("88", text)

    def test_similarity_query_synonyms_raise_related_document_score(self) -> None:
        related = similarity_score("gpu memory pressure", "graphics vram usage is high")
        unrelated = similarity_score("gpu memory pressure", "daily backup completed")

        self.assertGreater(related, unrelated)

    def test_cached_document_vector_round_trips_through_cache_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cache_path: Path = similarity.CACHE_PATH
            original_cache = getattr(similarity, "_cache")
            similarity.CACHE_PATH = Path(temp_dir) / "cache.jsonl"
            setattr(similarity, "_cache", None)
            try:
                first = cached_document_vector("GPU VRAM usage is high")
                setattr(similarity, "_cache", None)
                second = cached_document_vector("GPU VRAM usage is high")
            finally:
                similarity.CACHE_PATH = original_cache_path
                setattr(similarity, "_cache", original_cache)

        self.assertEqual(first, second)
        self.assertEqual(first, vectorize_text("GPU VRAM usage is high"))


if __name__ == "__main__":
    unittest.main()
