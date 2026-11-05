"""S170 path fixture: spaces, mixed Windows separators, and Unicode stay inside temp roots."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from evidence_pack import safe_output_path
from verify_evidence_manifest import verify


class PathNormalizationS170Tests(unittest.TestCase):
    def test_evidence_paths_with_spaces_mixed_separators_and_unicode(self):
        with tempfile.TemporaryDirectory(prefix="OneBossFight path fixture 雪 ") as temporary:
            root = Path(temporary).resolve()
            source_dir = root / "source files 雪"
            output = root / "evidence bundle é 雪"
            source_dir.mkdir()
            output.mkdir()

            # Build the input spelling with forward slashes in the root and a
            # backslash separator before the Unicode filename (Windows case).
            if os.name == "nt":
                source_text = str(source_dir).replace("\\", "/") + "\\raw evidence 雪.log"
            else:
                source_text = str(source_dir / "raw evidence 雪.log")
            source = Path(source_text)
            source.write_text("evidence with spaces and 雪", encoding="utf-8")

            destination = safe_output_path(output, "raw evidence 雪.log")
            self.assertEqual(destination.parent, output)
            self.assertTrue(destination.resolve().is_relative_to(output))
            destination.write_bytes(source.read_bytes())

            manifest = output / "evidence_manifest.json"
            manifest.write_text(json.dumps({
                "schema": 1,
                "files": [{
                    "file": destination.name,
                    "bytes": destination.stat().st_size,
                    "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
                }],
            }, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(verify(manifest), [])

            traversal = "..\\outside 雪.log" if os.name == "nt" else "../outside 雪.log"
            with self.assertRaises(ValueError):
                safe_output_path(output, traversal)
            self.assertFalse((root / "outside 雪.log").exists())


if __name__ == "__main__":
    unittest.main()
