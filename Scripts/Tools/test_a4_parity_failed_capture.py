from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from write_a4_parity_receipt import read_driver_capture


class A4FailedCaptureTests(unittest.TestCase):
    def test_13_of_14_capture_is_preserved_for_comparator(self) -> None:
        snapshot = {
            "schema": "onebossfight.encounter-runtime-snapshot/v1", "route": "legacy",
            "selection": {"selected": False},
            "participants": [], "activation": {}, "components": {},
        }
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "closed.log"
            log.write_text(
                "[A5ParityRunner] SNAPSHOT_JSON " + json.dumps(snapshot) + "\n"
                "[A4] FAIL S6 backward roll\n[A4] RESULT 13/14 passed\n",
                encoding="utf-8",
            )
            facts = read_driver_capture(log, "pie_a4_low_sweep")["run_facts"]
        self.assertEqual(facts["checks"], {"passed": 13, "minimum": 14})
        self.assertEqual(facts["terminal"], {"clean": False, "result": "Failed"})
        self.assertEqual(facts["observables"]["check-0001"]["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
