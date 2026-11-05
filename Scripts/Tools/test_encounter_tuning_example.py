from __future__ import annotations

import copy
import unittest

import compare_encounter_parity as parity
from test_validate_encounter_manifest import receipt, resign
from validate_encounter_manifest import validate


def parity_receipt(route: str, run_id: str, max_health: int) -> dict[str, object]:
    return {
        "schema": "onebossfight.encounter-parity/v1",
        "route": route,
        "run_id": run_id,
        "identity": {
            "map": "/Game/Maps/Arena", "build_id": "fixture-build",
            "content_sha256": "a" * 64, "settings_sha256": "b" * 64,
            "seed": 1, "driver": "fixture_tuning", "driver_args": [],
            "input_sha256": "c" * 64,
        },
        "final_marker": {"kind": "R", "passed": 1, "total": 1},
        "checks": {"passed": 1, "minimum": 1},
        "terminal": {"clean": True, "result": "Complete"},
        "activation": {"outcome": "LegacyAttached" if route == "legacy" else "Activated"},
        "components": {"boss": ["BossCore"], "player": ["PlayerCore"]},
        "observables": {"boss_max_health": max_health},
    }


class EncounterTuningExampleTests(unittest.TestCase):
    def test_one_field_tuning_validates_and_reports_one_expected_parity_difference(self):
        baseline = receipt()
        baseline["definitions"]["boss"]["stats"]["max_health"] = 2000
        baseline = resign(baseline)
        tuned = copy.deepcopy(baseline)
        tuned["definitions"]["boss"]["stats"]["max_health"] = 1999
        tuned = resign(tuned)
        self.assertEqual(validate(baseline), [])
        self.assertEqual(validate(tuned), [])

        issues = parity.compare(
            parity_receipt("legacy", "baseline", 2000),
            parity_receipt("data", "tuned", 1999),
        )
        self.assertEqual(issues, ["parity mismatch observables"])

        # Receipt identity hashing is deterministic after the single field edit.
        self.assertEqual(tuned["manifest_sha256"], resign(copy.deepcopy(tuned))["manifest_sha256"])


if __name__ == "__main__":
    unittest.main()
