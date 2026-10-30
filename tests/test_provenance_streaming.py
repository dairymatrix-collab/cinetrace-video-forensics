from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import provenance_probe  # noqa: E402


class ProvenanceStreamingTests(unittest.TestCase):
    def scan_bytes(self, data: bytes, needles: tuple[bytes, ...], chunk_size: int, context_bytes: int = 4):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "synthetic authorized sample.bin"
            source.write_bytes(data)
            return provenance_probe.scan_byte_signatures(
                source,
                needles=needles,
                chunk_size=chunk_size,
                context_bytes=context_bytes,
            )

    def test_chunk_boundaries_case_and_context_match_legacy_order(self):
        data = b"prefix-NEeDLe-middle-TaG-suffix"
        needles = (b"needle", b"tag")
        expected = []
        for needle in needles:
            position = 0
            while True:
                position = data.lower().find(needle, position)
                if position < 0:
                    break
                start = max(0, position - 4)
                context = data[start:position + len(needle) + 4].decode("utf-8", "replace")
                expected.append({"needle": needle.decode(), "offset": position, "context": context})
                position += len(needle)

        for chunk_size in (1, 2, 5, 6, 7, 13):
            with self.subTest(chunk_size=chunk_size):
                self.assertEqual(self.scan_bytes(data, needles, chunk_size), expected)

    def test_overlapping_signatures_keep_legacy_nonoverlap_semantics(self):
        hits = self.scan_bytes(b"aaaaa", (b"aa",), chunk_size=1, context_bytes=1)
        self.assertEqual([hit["offset"] for hit in hits], [0, 2])

    def test_empty_file_and_empty_needle_list(self):
        self.assertEqual(self.scan_bytes(b"", (b"x",), chunk_size=3), [])
        self.assertEqual(self.scan_bytes(b"some bytes", (), chunk_size=3), [])

    def test_invalid_bounds_fail_explicitly(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "sample.bin"
            source.write_bytes(b"sample")
            with self.assertRaises(ValueError):
                provenance_probe.scan_byte_signatures(source, (b"x",), chunk_size=0)
            with self.assertRaises(ValueError):
                provenance_probe.scan_byte_signatures(source, (b"x",), context_bytes=-1)
            with self.assertRaises(ValueError):
                provenance_probe.scan_byte_signatures(source, (b"",))

    def test_large_synthetic_file_hash_and_scan_do_not_use_read_bytes(self):
        data = (b"A" * (2 * 1024 * 1024)) + b"xmp" + (b"B" * 4096)
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "large synthetic sample.bin"
            source.write_bytes(data)
            with patch.object(Path, "read_bytes", side_effect=AssertionError("whole-file read is forbidden")):
                self.assertEqual(
                    provenance_probe.sha256_file(source, chunk_size=4096),
                    hashlib.sha256(data).hexdigest(),
                )
                hits = provenance_probe.scan_byte_signatures(
                    source, needles=(b"xmp",), chunk_size=4096, context_bytes=8
                )
            self.assertEqual([hit["offset"] for hit in hits], [2 * 1024 * 1024])
            self.assertEqual(hits[0]["context"], "A" * 8 + "xmp" + "B" * 8)


if __name__ == "__main__":
    unittest.main()
