from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import encounter_parity_receipt as receipt


def capture(route: str = "data") -> dict[str, object]:
    selected = route == "data"
    return {
        "route": route,
        "run_id": f"run-{route}",
        "identity": {
            "map": "/Game/Maps/Arena", "build_id": "editor-build",
            "content_sha256": "a" * 64, "settings_sha256": "b" * 64,
            "seed": 41, "driver": "pie_a4_low_sweep",
            "driver_args": [], "input_sha256": "c" * 64,
        },
        "selection": ({
            "selected": True, "definition": "/Game/Test/DA_Encounter",
            "manifest_sha256": "e" * 64,
            "encounter_instance": "11111111-22222222-33333333-44444444",
            "boss_slot": "Boss", "player_slot": "Player", "initial_boss_phase": "PhaseOne",
        } if selected else {
            "selected": False, "definition": None, "manifest_sha256": None,
            "encounter_instance": None, "boss_slot": None, "player_slot": None,
            "initial_boss_phase": None,
        }),
        "participants": [
            {"role": "boss", "actor_class": "Boss_C", "actor_id": "boss-slot",
             "participant_generation": "1" if selected else "0", "reset_count": 0},
            {"role": "player", "actor_class": "Player_C", "actor_id": "player-slot",
             "participant_generation": "1" if selected else "0", "reset_count": 0},
        ],
        "final_marker": {"kind": "R", "passed": 14, "total": 14},
        "checks": {"passed": 14, "minimum": 14},
        "terminal": {"clean": True, "result": "Completed"},
        "activation": {"outcome": "Activated"},
        "components": {"boss": ["Sweep"], "player": ["Combat"]},
        "observables": {
            "S2_grounded_front_250": {
                "value": {"hits": 1, "health_delta": 20},
                "source_log": "capture.log", "source_log_sha256": "f" * 64,
                "trial_id": "S2-01",
            },
        },
    }


class EncounterParityReceiptTests(unittest.TestCase):
    def test_rate_ratio_comparison_is_typed_and_bounded(self) -> None:
        value = capture()
        value["observables"] = {
            "T2b pack A1b slows before active": {
                "value": 0.396, "source_log": "capture.log", "source_log_sha256": "f" * 64,
                "trial_id": "T2b", "comparison": {"type": "rate_ratio", "range": [0.0, 1.0]},
            },
        }
        result = receipt.build_receipt(value)
        self.assertEqual(result["observables"]["T2b pack A1b slows before active"]["comparison"],
                         {"type": "rate_ratio", "range": [0.0, 1.0]})
        value["observables"]["T2b pack A1b slows before active"]["comparison"] = {
            "type": "rate_ratio", "range_seconds": [0.0, 1.0]}
        with self.assertRaises(receipt.ReceiptError):
            receipt.build_receipt(value)

    def test_failed_driver_run_is_retained_as_a_valid_receipt(self) -> None:
        value = capture()
        value["checks"] = {"passed": 13, "minimum": 14}
        value["final_marker"] = {"kind": "R", "passed": 13, "total": 14}
        value["terminal"] = {"clean": False, "result": "Failed"}
        result = receipt.build_receipt(value)
        self.assertEqual(result["checks"], {"passed": 13, "minimum": 14})
        self.assertEqual(result["terminal"], {"clean": False, "result": "Failed"})

    def test_passed_may_exceed_minimum_but_not_captured_total(self) -> None:
        value = capture()
        value["checks"] = {"passed": 26, "minimum": 25}
        value["final_marker"] = {"kind": "R", "passed": 26, "total": 26}
        result = receipt.build_receipt(value)
        self.assertEqual(result["checks"], {"passed": 26, "minimum": 25})
        value["checks"]["passed"] = 27  # type: ignore[index]
        with self.assertRaisesRegex(receipt.ReceiptError, "exceeds captured total"):
            receipt.build_receipt(value)

    def test_builder_emits_versioned_selection_and_participant_identity(self) -> None:
        result = receipt.build_receipt(capture())
        self.assertEqual(result["schema"], "onebossfight.encounter-parity/v2")
        self.assertTrue(result["selection"]["selected"])  # type: ignore[index]
        self.assertEqual(result["participants"][0]["participant_generation"], "1")  # type: ignore[index]

    def test_uint64_generation_uses_exact_decimal_string(self) -> None:
        value = capture()
        maximum_minus_one = "18446744073709551614"
        value["participants"][0]["participant_generation"] = maximum_minus_one  # type: ignore[index]
        result = receipt.build_receipt(value)
        self.assertEqual(result["participants"][0]["participant_generation"], maximum_minus_one)  # type: ignore[index]
        value["participants"][0]["participant_generation"] = "18446744073709551616"  # type: ignore[index]
        with self.assertRaisesRegex(receipt.ReceiptError, "uint64"):
            receipt.build_receipt(value)

    def test_malformed_digest_and_missing_participant_are_rejected(self) -> None:
        bad_digest = capture()
        bad_digest["identity"]["input_sha256"] = "not-a-digest"  # type: ignore[index]
        with self.assertRaisesRegex(receipt.ReceiptError, "input_sha256"):
            receipt.build_receipt(bad_digest)
        missing = capture()
        missing["participants"] = [missing["participants"][0]]  # type: ignore[index]
        with self.assertRaisesRegex(receipt.ReceiptError, "exactly one boss and one player"):
            receipt.build_receipt(missing)

    def test_selection_identity_drift_is_retained_for_comparator(self) -> None:
        left, right = receipt.build_receipt(capture("legacy")), capture("data")
        right["selection"]["manifest_sha256"] = "9" * 64  # type: ignore[index]
        self.assertNotEqual(left["selection"], right["selection"])

    def test_exact_typed_json_observable_is_accepted(self) -> None:
        value = capture()
        value["observables"]["S2_grounded_front_250"]["comparison"] = {"type": "exact"}  # type: ignore[index]
        value["observables"]["S2_grounded_front_250"]["value"] = [  # type: ignore[index]
            {"trial": "side roll at heal+1.30", "hits": 0, "iframe_passes": 0, "world_hits": 1}
        ]
        parsed = receipt.build_receipt(value)
        self.assertEqual(parsed["observables"]["S2_grounded_front_250"]["comparison"], {"type": "exact"})  # type: ignore[index]

    def test_stochastic_contract_requires_run_and_declared_threshold_fields(self) -> None:
        value = capture()
        value["observables"]["S2_grounded_front_250"].update({  # type: ignore[index]
            "value": {"scenario_ran": True, "hits": 2, "trials": 5},
            "comparison": {
                "type": "stochastic", "scenario_ran_field": "scenario_ran",
                "threshold": {"left_field": "hits", "op": "gte", "right_value": 1},
            },
        })
        parsed = receipt.build_receipt(value)
        self.assertEqual(parsed["observables"]["S2_grounded_front_250"]["comparison"]["type"], "stochastic")  # type: ignore[index]
        value["observables"]["S2_grounded_front_250"]["value"] = {"hits": 2, "trials": 5}  # type: ignore[index]
        with self.assertRaisesRegex(receipt.ReceiptError, "run/threshold fields"):
            receipt.build_receipt(value)

    def test_atomic_receipt_write_keeps_log_input_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            log = root / "capture.log"
            log.write_bytes(b"raw evidence\n")
            before = hashlib.sha256(log.read_bytes()).hexdigest()
            facts = copy.deepcopy(capture())
            facts["observables"]["S2_grounded_front_250"]["source_log_sha256"] = before  # type: ignore[index]
            target = root / "out" / "receipt.json"
            receipt.write_receipt(target, facts)
            self.assertEqual(hashlib.sha256(log.read_bytes()).hexdigest(), before)
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["schema"], receipt.SCHEMA)
            self.assertEqual(list(target.parent.glob("*.tmp")), [])

    def test_snapshot_join_preserves_selected_runtime_identity(self) -> None:
        facts = capture()
        snapshot = {
            "schema": "onebossfight.encounter-runtime-snapshot/v1", "route": "data",
            "selection": facts["selection"], "participants": facts["participants"],
            "activation": {"outcome": "ActivatedRegisteredSubset"},
            "components": facts["components"],
        }
        joined = receipt.build_receipt_from_snapshot(snapshot, facts)
        self.assertEqual(joined["route"], "data")
        self.assertEqual(joined["selection"], facts["selection"])
        self.assertEqual(joined["participants"], facts["participants"])

    def test_legacy_snapshot_uses_zero_for_unavailable_binding_generation(self) -> None:
        facts = capture("legacy")
        snapshot = {
            "schema": "onebossfight.encounter-runtime-snapshot/v1", "route": "legacy",
            "selection": {"selected": False, "definition": "", "manifest_sha256": "",
                          "encounter_instance": "", "boss_slot": "", "player_slot": "",
                          "initial_boss_phase": ""},
            "participants": [
                {"role": role, "actor_class": role + "_C", "actor_id": role,
                 "participant_generation": "", "reset_count": 0}
                for role in ("boss", "player")
            ],
            "activation": {"outcome": "LegacyAttached"},
            "components": {"boss": ["Sweep"], "player": ["Dodge"]},
        }
        joined = receipt.build_receipt_from_snapshot(snapshot, facts)
        self.assertEqual(joined["selection"], {
            "selected": False, "definition": None, "manifest_sha256": None,
            "encounter_instance": None, "boss_slot": None, "player_slot": None,
            "initial_boss_phase": None,
        })
        self.assertEqual([row["participant_generation"] for row in joined["participants"]], ["0", "0"])


if __name__ == "__main__":
    unittest.main()
