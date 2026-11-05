from __future__ import annotations

import json
import contextlib
import copy
import hashlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import compare_encounter_parity as parity
import encounter_parity_receipt


def receipt(route: str, run_id: str) -> dict[str, object]:
    return {
        "schema": "onebossfight.encounter-parity/v1",
        "route": route,
        "run_id": run_id,
        "identity": {
            "map": "/Game/Maps/Arena",
            "build_id": "Editor-abcdef",
            "content_sha256": "a" * 64,
            "settings_sha256": "b" * 64,
            "seed": 12345,
            "driver": "pie_example",
            "driver_args": ["--seed", "12345"],
            "input_sha256": "c" * 64,
        },
        "final_marker": {"kind": "R", "passed": 14, "total": 14},
        "checks": {"passed": 14, "minimum": 14},
        "terminal": {"clean": True, "result": "CompletedWithDamage"},
        "activation": {"outcome": "LegacyAttached" if route == "legacy" else "Activated"},
        "components": {"boss": ["A", "B"], "player": ["P"]},
        "observables": {"result": "CompletedWithDamage", "player_hp": 80},
    }


class EncounterParityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, name: str, value: object) -> Path:
        path = self.root / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def timing_receipt(self, route: str, run_id: str, seconds: float, *, bounds: list[float] | None = None) -> dict[str, object]:
        selected = route == "data"
        capture: dict[str, object] = {
            "route": route, "run_id": run_id,
            "identity": {"map": "/Game/Arena", "build_id": "b", "content_sha256": "a" * 64,
                         "settings_sha256": "b" * 64, "seed": 1, "driver": "timing_test",
                         "driver_args": [], "input_sha256": "c" * 64},
            "selection": ({"selected": True, "definition": "/Game/Test/Encounter", "manifest_sha256": "e" * 64,
                           "encounter_instance": "guid", "boss_slot": "Boss", "player_slot": "Player",
                           "initial_boss_phase": "PhaseOne"} if selected else
                          {"selected": False, "definition": None, "manifest_sha256": None,
                           "encounter_instance": None, "boss_slot": None, "player_slot": None,
                           "initial_boss_phase": None}),
            "participants": [{"role": role, "actor_class": role + "_C", "actor_id": role,
                              "participant_generation": "1" if selected else "0", "reset_count": 0}
                             for role in ("boss", "player")],
            "final_marker": {"kind": "R", "passed": 1, "total": 1},
            "checks": {"passed": 1, "minimum": 1}, "terminal": {"clean": True, "result": "Complete"},
            "activation": {"outcome": "Attached" if not selected else "Activated"},
            "components": {"boss": [], "player": []},
            "observables": {"windup": {"value": seconds, "source_log": f"{route}.log",
                                          "source_log_sha256": "f" * 64, "trial_id": "windup-1",
                                          "comparison": {"type": "timing_seconds",
                                                          "range_seconds": bounds or [0.0, 1.0]}}},
        }
        return encounter_parity_receipt.build_receipt(capture)

    def test_typed_timing_tolerance_passes_at_010_seconds(self) -> None:
        left = self.timing_receipt("legacy", "one", 0.400)
        right = self.timing_receipt("data", "two", 0.410)
        self.assertEqual(parity.compare(left, right), [])
        self.assertEqual(parity._observable_status(left, right, "windup"), "MATCH")

    def test_typed_timing_tolerance_passes_at_027_seconds(self) -> None:
        left = self.timing_receipt("legacy", "one", 0.400)
        right = self.timing_receipt("data", "two", 0.427)
        self.assertEqual(parity.compare(left, right), [])

    def test_typed_timing_tolerance_fails_at_040_seconds(self) -> None:
        left = self.timing_receipt("legacy", "one", 0.400)
        right = self.timing_receipt("data", "two", 0.440)
        self.assertTrue(any("parity mismatch observable windup" in issue
                            for issue in parity.compare(left, right)))

    def test_typed_timing_out_of_authored_range_fails(self) -> None:
        left = self.timing_receipt("legacy", "one", 0.400, bounds=[0.3, 0.5])
        right = self.timing_receipt("data", "two", 0.510, bounds=[0.3, 0.5])
        self.assertTrue(any("parity mismatch observable windup" in issue
                            for issue in parity.compare(left, right)))

    def test_typed_rate_ratio_uses_point_zero_one_and_authored_range(self) -> None:
        left = {"value": 0.396, "comparison": {"type": "rate_ratio", "range": [0.0, 1.0]}}
        right = {"value": 0.398, "comparison": {"type": "rate_ratio", "range": [0.0, 1.0]}}
        self.assertTrue(parity._observable_value_matches(left, right))
        self.assertFalse(parity._observable_value_matches(left, {**right, "value": 0.407}))
        self.assertFalse(parity._observable_value_matches(
            left, {"value": 1.01, "comparison": {"type": "rate_ratio", "range": [0.0, 1.0]}}))

    def test_undeclared_timing_like_observables_remain_exact(self) -> None:
        left = self.timing_receipt("legacy", "one", 0.400)
        right = self.timing_receipt("data", "two", 0.410)
        del left["observables"]["windup"]["comparison"]  # type: ignore[index]
        del right["observables"]["windup"]["comparison"]  # type: ignore[index]
        self.assertTrue(any("parity mismatch observable windup" in issue
                            for issue in parity.compare(left, right)))

    def test_v2_route_specific_selection_and_generation_are_not_gameplay_mismatches(self) -> None:
        def capture_v2(route: str, run_id: str) -> dict[str, object]:
            selected = route == "data"
            value: dict[str, object] = {
                "route": route, "run_id": run_id,
                "identity": {"map": "/Game/Arena", "build_id": "b", "content_sha256": "a" * 64,
                             "settings_sha256": "b" * 64, "seed": 1, "driver": "pie_a4_low_sweep",
                             "driver_args": [], "input_sha256": "c" * 64},
                "selection": ({"selected": True, "definition": "/Game/Test/Encounter", "manifest_sha256": "e" * 64,
                               "encounter_instance": "guid", "boss_slot": "Boss", "player_slot": "Player",
                               "initial_boss_phase": "PhaseOne"} if selected else
                              {"selected": False, "definition": None, "manifest_sha256": None,
                               "encounter_instance": None, "boss_slot": None, "player_slot": None,
                               "initial_boss_phase": None}),
                "participants": [
                    {"role": role, "actor_class": role + "_C", "actor_id": role,
                     "participant_generation": "1" if selected else "0", "reset_count": 0}
                    for role in ("boss", "player")],
                "final_marker": {"kind": "R", "passed": 14, "total": 14},
                "checks": {"passed": 14, "minimum": 14},
                "terminal": {"clean": True, "result": "Completed"},
                "activation": {"outcome": "LegacyAttached" if not selected else "Activated"},
                "components": {"boss": ["Sweep"], "player": ["Dodge"]},
                "observables": {"S2": {"value": {"hits": 1}, "source_log": "run.log",
                                         "source_log_sha256": "f" * 64, "trial_id": "S2"}},
            }
            return value
        control = encounter_parity_receipt.build_receipt(capture_v2("legacy", "one"))
        candidate = encounter_parity_receipt.build_receipt(capture_v2("data", "two"))
        issues = parity.compare(control, candidate)
        self.assertEqual(issues, [])

    def test_v2_check_parity_uses_status_and_trial_identity_not_message(self) -> None:
        control = self.timing_receipt("legacy", "one", 0.4)
        candidate = self.timing_receipt("data", "two", 0.4)
        del control["observables"]["windup"]["comparison"]  # type: ignore[index]
        del candidate["observables"]["windup"]["comparison"]  # type: ignore[index]
        control["observables"]["windup"]["value"] = {  # type: ignore[index]
            "status": "PASS", "message": "A3a windup 0.426 s (pointer 0x00001234)"}
        candidate["observables"]["windup"]["value"] = {  # type: ignore[index]
            "status": "PASS", "message": "A3a windup 0.422 s (pointer 0x00005678)"}
        self.assertEqual(parity.compare(control, candidate), [])
        candidate["observables"]["windup"]["value"]["status"] = "FAIL"  # type: ignore[index]
        self.assertTrue(any("parity mismatch observable windup" in issue
                            for issue in parity.compare(control, candidate)))
        candidate["observables"]["windup"]["value"]["status"] = "PASS"  # type: ignore[index]
        candidate["observables"]["windup"]["trial_id"] = "other-trial"  # type: ignore[index]
        self.assertTrue(any("unmatched trial for observable windup" in issue
                            for issue in parity.compare(control, candidate)))

    def test_typed_measurement_compares_attached_check_status(self) -> None:
        control = self.timing_receipt("legacy", "one", 0.400)
        candidate = self.timing_receipt("data", "two", 0.400)
        control["observables"]["windup"]["check_status"] = "PASS"  # type: ignore[index]
        candidate["observables"]["windup"]["check_status"] = "FAIL"  # type: ignore[index]
        self.assertTrue(any("parity mismatch observable windup" in issue
                            for issue in parity.compare(control, candidate)))

    def test_message_numeric_tokens_use_absolute_or_relative_tolerance(self) -> None:
        def compare_messages(left_message: str, right_message: str) -> list[str]:
            control = self.timing_receipt("legacy", "one", 0.4)
            candidate = self.timing_receipt("data", "two", 0.4)
            for receipt, message in ((control, left_message), (candidate, right_message)):
                observable = receipt["observables"]["windup"]  # type: ignore[index]
                observable.pop("comparison")
                observable["value"] = {"status": "PASS", "message": message}
            return parity.compare(control, candidate)

        self.assertEqual(compare_messages("windup 0.26 s", "windup 0.27 s"), [])
        self.assertEqual(compare_messages("first at 4.4 seconds", "first at 4.5 seconds"), [])
        self.assertEqual(compare_messages("13 samples", "12 samples"), [])
        self.assertEqual(compare_messages("series [1, 2, 3]", "series [1, 2, 4]"), [])
        self.assertEqual(compare_messages("samples [('side roll', 0, 0)]",
                                          "samples [('side roll', 0, 1)]"), [])
        self.assertEqual(compare_messages("object BP_Boss_C_3 at 0x000008AB", "object BP_Boss_C_1 at 0x000005FE"), [])
        large_delta = compare_messages("boss max health 2000.0", "boss max health 1500.0")
        self.assertTrue(any("numeric token 1 differs" in issue and "control=2000" in issue and "data=1500" in issue
                            for issue in large_delta))
        bracketed_health = compare_messages("boss [health 2000.0/2000.0]", "boss [health 1500.0/1500.0]")
        self.assertTrue(any("numeric token" in issue and "control=2000" in issue
                            for issue in bracketed_health))
        changed_text = compare_messages("state Dormant", "state Fighting")
        self.assertTrue(any("message text differs" in issue for issue in changed_text))
        changed_count = compare_messages("observed 1.0 sample", "observed sample")
        self.assertTrue(any("numeric token 1 count differs" in issue for issue in changed_count))

    def test_build_231_l1d_camera_sample_noise_is_volatile_but_ratio_is_not(self) -> None:
        # Values copied from the retained pie_legend_t1 comparison. Sample counts
        # vary while the reported high-pass ratio agrees across routes.
        left = "L1d ratio 0.22 scales [('600 cm', 0.982, 523), ('1500 cm', 0.174, 1877)]"
        right = "L1d ratio 0.22 scales [('600 cm', 0.661, 983), ('1500 cm', 0.174, 1877)]"
        self.assertIsNone(parity._message_mismatch(left, right))
        self.assertTrue(parity._volatile_message_differs(left, right))
        self.assertIsNotNone(parity._message_mismatch(left.replace("ratio 0.22", "ratio 0.72"), right))

    def test_health_diagnostic_tokens_remain_semantic(self) -> None:
        # Shape and values copied from both retained pie_riposte_lethal_d5 logs.
        left = "L1 the riposte took the boss from 60.0 health to zero (health 0.0, dead tag True, montage AN_Boss01_DeathLegend)"
        same = "L1 the riposte took the boss from 60 health to zero (health 0, dead tag True, montage AN_Boss01_DeathLegend)"
        changed = left.replace("60.0", "50.0")
        self.assertIsNone(parity._message_mismatch(left, same))
        self.assertIsNotNone(parity._message_mismatch(left, changed))

    def test_d6c_warns_for_sample_count_and_bracketed_series_without_failing(self) -> None:
        control = self.timing_receipt("legacy", "one", 0.4)
        candidate = self.timing_receipt("data", "two", 0.4)
        for receipt, message in (
            (control, "4 samples pelvis [140,133,123,112]"),
            (candidate, "5 samples pelvis [140,133,123,98,81]"),
        ):
            observable = receipt["observables"].pop("windup")  # type: ignore[index]
            observable.pop("comparison")
            observable["value"] = {"status": "PASS", "message": message}
            receipt["observables"]["check-0001"] = observable  # type: ignore[index]
        self.assertEqual(parity.compare(control, candidate), [])
        warnings = parity._message_warnings(control, candidate)
        self.assertEqual(len(warnings), 1)
        self.assertIn("check-0001", warnings[0])
        self.assertIn("4 samples pelvis [140,133,123,112]", warnings[0])
        self.assertIn("5 samples pelvis [140,133,123,98,81]", warnings[0])

    def test_d6c_bracketed_state_values_fail_without_sample_warning(self) -> None:
        control = self.timing_receipt("legacy", "one", 0.4)
        candidate = self.timing_receipt("data", "two", 0.4)
        for receipt, message in ((control, "state [health 2000/2000]"),
                                 (candidate, "state [health 1500/1500]")):
            observable = receipt["observables"]["windup"]  # type: ignore[index]
            observable.pop("comparison")
            observable["value"] = {"status": "PASS", "message": message}
        self.assertTrue(any("numeric token" in issue and "control=2000" in issue
                            for issue in parity.compare(control, candidate)))
        self.assertEqual(parity._message_warnings(control, candidate), [])

    def test_bracketed_state_metric_keywords_are_never_downgraded_to_sample_warnings(self) -> None:
        for keyword in ("health", "posture", "poise", "damage", "stamina", "hp"):
            with self.subTest(keyword=keyword):
                left, right = f"state [{keyword} 2000]", f"state [{keyword} 1500]"
                mismatch = parity._message_mismatch(left, right)
                self.assertIsNotNone(mismatch)
                self.assertIn("control=2000", mismatch or "")
                self.assertFalse(parity._volatile_message_differs(left, right))

    def test_d6c_exact_typed_per_trial_counts_fail_on_one_boundary_trial(self) -> None:
        control = self.timing_receipt("legacy", "one", 0.4)
        candidate = self.timing_receipt("data", "two", 0.4)
        for receipt, world_hits in ((control, 0), (candidate, 1)):
            observable = receipt["observables"]["windup"]  # type: ignore[index]
            observable["value"] = [{"trial": "side roll at heal+1.30", "hits": 0,
                                    "iframe_passes": 0, "world_hits": world_hits}]
            observable["comparison"] = {"type": "exact"}
        self.assertTrue(any("parity mismatch observable windup" in issue
                            for issue in parity.compare(control, candidate)))
        self.assertEqual(parity._message_warnings(control, candidate), [])

    def test_stochastic_observables_pass_threshold_and_report_both_values_as_warn(self) -> None:
        control = self.timing_receipt("legacy", "one", 0.4)
        candidate = self.timing_receipt("data", "two", 0.4)
        comparison = {
            "type": "stochastic", "scenario_ran_field": "scenario_ran",
            "threshold": {"left_field": "hits", "op": "gte", "right_value": 1},
        }
        for receipt, hits in ((control, 2), (candidate, 1)):
            observable = receipt["observables"]["windup"]  # type: ignore[index]
            observable["comparison"] = comparison
            observable["check_status"] = "PASS"
            observable["value"] = {"scenario_ran": True, "hits": hits, "trials": 5}
        self.assertEqual(parity.compare(control, candidate), [])
        warnings = parity._message_warnings(control, candidate)
        self.assertEqual(len(warnings), 1)
        self.assertIn('"hits": 2', warnings[0])
        self.assertIn('"hits": 1', warnings[0])

    def test_stochastic_observables_fail_when_a_scenario_or_threshold_fails(self) -> None:
        control = self.timing_receipt("legacy", "one", 0.4)
        candidate = self.timing_receipt("data", "two", 0.4)
        comparison = {
            "type": "stochastic", "scenario_ran_field": "scenario_ran",
            "threshold": {"left_field": "attacks", "op": "gte", "right_value": 1},
        }
        for receipt, ran, attacks in ((control, True, 1), (candidate, True, 3)):
            observable = receipt["observables"]["windup"]  # type: ignore[index]
            observable["comparison"] = comparison
            observable["check_status"] = "PASS"
            observable["value"] = {"scenario_ran": ran, "attacks": attacks}
        self.assertEqual(parity.compare(control, candidate), [])
        candidate["observables"]["windup"]["value"]["attacks"] = 0  # type: ignore[index]
        self.assertTrue(any("parity mismatch observable windup" in issue
                            for issue in parity.compare(control, candidate)))
        candidate["observables"]["windup"]["value"] = {"scenario_ran": False, "attacks": 3}  # type: ignore[index]
        self.assertTrue(any("parity mismatch observable windup" in issue
                            for issue in parity.compare(control, candidate)))

    def test_typed_timing_masks_only_time_values_and_checks_other_message_numbers(self) -> None:
        control = self.timing_receipt("legacy", "one", 0.400)
        candidate = self.timing_receipt("data", "two", 0.427)
        control["observables"]["windup"]["check_status"] = "PASS"  # type: ignore[index]
        candidate["observables"]["windup"]["check_status"] = "PASS"  # type: ignore[index]
        control["observables"]["windup"]["check_message"] = "windup 0.400s health 2000 hits 3"  # type: ignore[index]
        candidate["observables"]["windup"]["check_message"] = "windup 0.427s health 2000 hits 3"  # type: ignore[index]
        self.assertEqual(parity.compare(control, candidate), [])
        candidate["observables"]["windup"]["check_message"] = "windup 0.427s health 1500 hits 3"  # type: ignore[index]
        self.assertTrue(any("parity mismatch observable windup" in issue
                            for issue in parity.compare(control, candidate)))
        candidate["observables"]["windup"]["check_message"] = "windup 0.427s health 2000 hits 2"  # type: ignore[index]
        self.assertTrue(any("parity mismatch observable windup" in issue
                            for issue in parity.compare(control, candidate)))

    def test_retained_legend_t1c_passes_but_mutated_health_token_fails(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        pair = repo_root / "Docs/BossCombatReview/Execution/Claude/B_C835_PARITY/pie_legend_t1c"
        control = parity.read_receipt(pair / "receipt_legacy.json", "legacy")
        candidate = parity.read_receipt(pair / "receipt_data.json", "data")
        self.assertEqual(parity.compare(control, candidate), [])

        mutated_control = copy.deepcopy(control)
        mutated_candidate = copy.deepcopy(candidate)
        mutated_control["observables"]["check-0021"]["check_message"] += " health 2000"
        mutated_candidate["observables"]["check-0021"]["check_message"] += " health 1500"
        self.assertTrue(any("parity mismatch observable check-0021" in issue
                            for issue in parity.compare(mutated_control, mutated_candidate)))

    def test_v2_pair_compares_captured_values_and_retains_source_hashes(self) -> None:
        def capture(route: str, run_id: str) -> dict[str, object]:
            value = {
                "route": route, "run_id": run_id,
                "identity": {
                    "map": "/Game/Maps/Arena", "build_id": "build",
                    "content_sha256": "a" * 64, "settings_sha256": "b" * 64,
                    "seed": 7, "driver": "pie_a4_low_sweep",
                    "driver_args": [], "input_sha256": "c" * 64,
                },
                "selection": ({
                    "selected": True, "definition": "/Game/Test/Encounter",
                    "manifest_sha256": "e" * 64,
                    "encounter_instance": "11111111-22222222-33333333-44444444",
                    "boss_slot": "Boss", "player_slot": "Player", "initial_boss_phase": "PhaseOne",
                } if route == "data" else {
                    "selected": False, "definition": None, "manifest_sha256": None,
                    "encounter_instance": None, "boss_slot": None, "player_slot": None,
                    "initial_boss_phase": None,
                }),
                "participants": [
                    {"role": "boss", "actor_class": "Boss_C", "actor_id": "boss",
                     "participant_generation": "1" if route == "data" else "0", "reset_count": 0},
                    {"role": "player", "actor_class": "Player_C", "actor_id": "player",
                     "participant_generation": "1" if route == "data" else "0", "reset_count": 0},
                ],
                "final_marker": {"kind": "R", "passed": 14, "total": 14},
                "checks": {"passed": 14, "minimum": 14},
                "terminal": {"clean": True, "result": "Complete"},
                "activation": {"outcome": "Attached" if route == "legacy" else "Activated"},
                "components": {"boss": ["Sweep"], "player": ["Dodge"]},
                "observables": {
                    "S2": {"value": {"hits": 1}, "source_log": f"{route}.log",
                           "source_log_sha256": "f" * 64, "trial_id": "S2-1"},
                },
            }
            return encounter_parity_receipt.build_receipt(value)

        control_path = self.write("v2-control.json", capture("legacy", "one"))
        data_path = self.write("v2-data.json", capture("data", "two"))
        report_path = self.root / "v2-report.json"
        argv = ["compare_encounter_parity.py", str(control_path), str(data_path), "--report-json", str(report_path)]
        with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(parity.main(), 0)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["sources"]["control"]["receipt_sha256"], parity.sha256_file(control_path))
        self.assertEqual(report["observable_sources"]["S2"]["control"]["source_log_sha256"], "f" * 64)

        data = json.loads(data_path.read_text(encoding="utf-8"))
        control_receipt = parity.read_receipt(control_path, "legacy")
        data["identity"]["input_sha256"] = "9" * 64
        data_path.write_text(json.dumps(data), encoding="utf-8")
        changed_receipt = parity.read_receipt(data_path, "data")
        self.assertTrue(any("identity mismatch input_sha256" in issue for issue in parity.compare(control_receipt, changed_receipt)))
        data["identity"]["input_sha256"] = "c" * 64
        data["observables"]["S2"]["trial_id"] = "S2-skipped"
        data_path.write_text(json.dumps(data), encoding="utf-8")
        with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(parity.main(), 2)
        self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["status"], "INCONCLUSIVE")

    def test_valid_legacy_data_pair_passes_declared_observables(self) -> None:
        control = parity.read_receipt(self.write("control.json", receipt("legacy", "run-a")), "legacy")
        data = parity.read_receipt(self.write("data.json", receipt("data", "run-b")), "data")
        self.assertEqual(parity.compare(control, data), [])

    def test_build_identity_drift_fails_pair(self) -> None:
        left, right = receipt("legacy", "run-a"), receipt("data", "run-b")
        right["identity"]["build_id"] = "other-build"  # type: ignore[index]
        issues = parity.compare(left, right)  # type: ignore[arg-type]
        self.assertTrue(any("identity mismatch build_id" in issue for issue in issues))

    def test_negative_control_input_identity_drift_fails_pair(self) -> None:
        left, right = receipt("legacy", "run-a"), receipt("data", "run-b")
        right["identity"]["input_sha256"] = "d" * 64  # type: ignore[index]
        issues = parity.compare(left, right)  # type: ignore[arg-type]
        self.assertTrue(any("identity mismatch input_sha256" in issue for issue in issues))

    def test_v2_source_log_verification_checks_bytes(self) -> None:
        log = self.root / "raw.log"
        log.write_bytes(b"captured evidence\n")
        digest = hashlib.sha256(log.read_bytes()).hexdigest()
        value = {
            "schema": "onebossfight.encounter-parity/v2",
            "observables": {"trial": {"source_log": "raw.log", "source_log_sha256": digest}},
        }
        receipt_path = self.root / "receipt.json"
        parity.verify_source_logs(value, receipt_path)
        log.write_bytes(b"changed evidence\n")
        with self.assertRaisesRegex(parity.ReceiptError, "SHA-256 mismatch"):
            parity.verify_source_logs(value, receipt_path)

    def test_observable_mismatch_fails_pair(self) -> None:
        left, right = receipt("legacy", "run-a"), receipt("data", "run-b")
        right["observables"]["player_hp"] = 79  # type: ignore[index]
        issues = parity.compare(left, right)  # type: ignore[arg-type]
        self.assertTrue(any("parity mismatch observables" in issue for issue in issues))

    def test_missing_and_extra_observables_fail_pair(self) -> None:
        left, missing = receipt("legacy", "run-a"), receipt("data", "run-b")
        del missing["observables"]["player_hp"]
        issues = parity.compare(left, missing)
        self.assertTrue(any("parity mismatch observables" in issue for issue in issues))
        self.assertTrue(any("observable field sets differ" in issue for issue in issues))

        extra = receipt("data", "run-c")
        extra["observables"]["extra_metric"] = 1
        issues = parity.compare(left, extra)
        self.assertTrue(any("observable field sets differ" in issue for issue in issues))

    def test_missing_identity_refuses_inconclusive(self) -> None:
        value = receipt("legacy", "run-a")
        del value["identity"]["input_sha256"]  # type: ignore[index]
        with self.assertRaisesRegex(parity.ReceiptError, "incomplete identity"):
            parity.read_receipt(self.write("missing.json", value), "legacy")

    def test_wrong_route_refuses_but_failed_run_is_readable_for_comparison(self) -> None:
        value = receipt("data", "run-a")
        with self.assertRaisesRegex(parity.ReceiptError, "route must"):
            parity.read_receipt(self.write("route.json", value), "legacy")
        value["checks"]["passed"] = 13  # type: ignore[index]
        value["terminal"] = {"clean": False, "result": "Failed"}
        failed = parity.read_receipt(self.write("failed.json", value), "data")
        issues = parity.compare(receipt("legacy", "run-control"), failed)
        self.assertTrue(any("candidate run failed checks: 13/14" in issue for issue in issues))

    def test_report_json_is_deterministic_atomic_and_does_not_mutate_inputs(self) -> None:
        control, data = receipt("legacy", "run-a"), receipt("data", "run-b")
        control_path = self.write("control.json", control)
        data_path = self.write("data.json", data)
        before = (control_path.read_bytes(), data_path.read_bytes())
        report_path = self.root / "nested" / "report.json"
        argv = ["compare_encounter_parity.py", str(control_path), str(data_path), "--report-json", str(report_path)]
        with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(parity.main(), 0)
        first = report_path.read_bytes()
        report = json.loads(first)
        self.assertEqual(report["schema"], "onebossfight.encounter-parity-report/v1")
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["exit_code"], 0)
        self.assertEqual(list(report_path.parent.glob("*.tmp")), [])
        with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(parity.main(), 0)
        self.assertEqual(report_path.read_bytes(), first)
        self.assertEqual((control_path.read_bytes(), data_path.read_bytes()), before)

    def test_report_json_records_fail_and_inconclusive_status(self) -> None:
        control = receipt("legacy", "run-a")
        data = receipt("data", "run-b")
        data["identity"]["build_id"] = "different"  # type: ignore[index]
        cp, dp, report = self.write("c.json", control), self.write("d.json", data), self.root / "report.json"
        argv = ["compare_encounter_parity.py", str(cp), str(dp), "--report-json", str(report)]
        with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(parity.main(), 1)
        self.assertEqual(json.loads(report.read_text(encoding="utf-8"))["status"], "FAIL")

        broken = receipt("legacy", "run-c")
        del broken["identity"]["input_sha256"]  # type: ignore[index]
        bp = self.write("broken.json", broken)
        argv = ["compare_encounter_parity.py", str(bp), str(dp), "--report-json", str(report)]
        with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(parity.main(), 2)
        result = json.loads(report.read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "INCONCLUSIVE")
        self.assertEqual(result["exit_code"], 2)
        self.assertTrue(result["issues"])


if __name__ == "__main__":
    unittest.main()
