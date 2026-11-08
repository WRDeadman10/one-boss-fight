from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from process_test_support import run_test_subprocess


TOOLS = Path(__file__).resolve().parent


class IsolatedParityImportTests(unittest.TestCase):
    def test_receipt_writer_help_works_under_isolated_python(self) -> None:
        result = run_test_subprocess(self,
            [sys.executable, "-I", str(TOOLS / "write_a4_parity_receipt.py"), "--help"],
            timeout=15, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_comparator_help_works_under_isolated_python(self) -> None:
        result = run_test_subprocess(self,
            [sys.executable, "-I", str(TOOLS / "compare_encounter_parity.py"), "--help"],
            timeout=15, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
