from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from process_test_support import run_test_subprocess


class BoundedTestSubprocessTests(unittest.TestCase):
    def test_timeout_fails_with_command_and_captured_output_and_cleans_temp_root(self) -> None:
        temporary_path: Path | None = None
        with self.assertRaisesRegex(AssertionError, "exceeded 0.05s timeout") as caught:
            with tempfile.TemporaryDirectory() as temporary:
                temporary_path = Path(temporary)
                run_test_subprocess(
                    self,
                    [sys.executable, "-c", "import time; print('started', flush=True); time.sleep(5)"],
                    timeout=0.05,
                    cwd=temporary_path,
                    capture_output=True,
                    text=True,
                    check=False,
                )
        self.assertIn("command=", str(caught.exception))
        self.assertIn("started", str(caught.exception))
        self.assertIsNotNone(temporary_path)
        self.assertFalse(temporary_path.exists())


if __name__ == "__main__":
    unittest.main()
