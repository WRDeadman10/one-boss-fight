"""S171 fixtures for preserving valid outputs across failed atomic writes."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from atomic_io import atomic_create_text, atomic_write_text


class AtomicIOS171Tests(unittest.TestCase):
    def test_failed_replace_preserves_previous_manifest_and_cleans_temp(self):
        with tempfile.TemporaryDirectory(prefix="OneBossFight atomic output ") as temporary:
            target = Path(temporary) / "manifest with spaces 雪.json"
            target.write_text('{"schema":1,"valid":true}\n', encoding="utf-8")

            with patch("atomic_io.os.replace", side_effect=OSError("simulated publish interruption")):
                with self.assertRaises(OSError):
                    atomic_write_text(target, '{"schema":1,"valid":false}\n')

            self.assertEqual(target.read_text(encoding="utf-8"), '{"schema":1,"valid":true}\n')
            self.assertEqual(list(Path(temporary).glob(f".{target.name}.*.tmp")), [])

    def test_atomic_create_refuses_to_replace_existing_valid_manifest(self):
        with tempfile.TemporaryDirectory(prefix="OneBossFight atomic create ") as temporary:
            target = Path(temporary) / "profile 雪.json"
            original = '{"enabled":true}\n'
            target.write_text(original, encoding="utf-8")

            with self.assertRaises(FileExistsError):
                atomic_create_text(target, '{"enabled":false}\n')

            self.assertEqual(target.read_text(encoding="utf-8"), original)
            self.assertEqual(list(Path(temporary).glob(f".{target.name}.*.tmp")), [])

    def test_permission_error_during_replace_preserves_old_output_and_cleans_temp(self):
        with tempfile.TemporaryDirectory(prefix="OneBossFight locked output ") as temporary:
            target = Path(temporary) / "report.json"
            target.write_text("old complete report\n", encoding="utf-8")
            with patch("atomic_io.os.replace", side_effect=PermissionError("locked by another process")):
                with self.assertRaises(PermissionError):
                    atomic_write_text(target, "new report\n")
            self.assertEqual(target.read_text(encoding="utf-8"), "old complete report\n")
            self.assertEqual(list(Path(temporary).glob(f".{target.name}.*.tmp")), [])

    def test_permission_error_during_create_does_not_publish_or_leave_temp(self):
        with tempfile.TemporaryDirectory(prefix="OneBossFight denied create ") as temporary:
            target = Path(temporary) / "report.json"
            with patch("atomic_io.os.link", side_effect=PermissionError("publish denied")):
                with self.assertRaises(PermissionError):
                    atomic_create_text(target, "complete report\n")
            self.assertFalse(target.exists())
            self.assertEqual(list(Path(temporary).glob(f".{target.name}.*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
