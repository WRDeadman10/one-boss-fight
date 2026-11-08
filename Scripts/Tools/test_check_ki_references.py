"""Regression checks for the KI reference checker's exit status."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from Scripts.Tools.check_ki_references import main


class CheckKIReferencesTests(unittest.TestCase):
    def test_missing_reference_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "Documentation").mkdir()
            (root / "Source").mkdir()
            (root / "Documentation/KNOWN_ISSUES.md").write_text("KI-001 documented\n", encoding="utf-8")
            (root / "Source/missing.cpp").write_text("// KI-999 missing\n", encoding="utf-8")
            output = StringIO()
            with patch("sys.argv", ["check_ki_references.py", "--root", str(root)]), redirect_stdout(output):
                self.assertEqual(main(), 1)
            self.assertIn("KI-999 missing from KNOWN_ISSUES.md", output.getvalue())

    def test_documented_reference_passes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "Documentation").mkdir()
            (root / "Source").mkdir()
            (root / "Documentation/KNOWN_ISSUES.md").write_text("KI-001 documented\n", encoding="utf-8")
            (root / "Source/known.cpp").write_text("// KI-001 documented\n", encoding="utf-8")
            with patch("sys.argv", ["check_ki_references.py", "--root", str(root)]), redirect_stdout(StringIO()):
                self.assertEqual(main(), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
