"""Offline contracts for the AR C-971 R2 hold receipt parser."""
import unittest
from pathlib import Path

from Scripts.Tools import ar_charge_receipt as receipt


def sample(case, montage="Ability_E_Anim_Montage", observed="393.00", tick="0.02780"):
    return ("[2026.11.07-07.34.52:658][449] LogPython: [ERControlLatency] "
            f"sample case={case} montage={montage} position=0.029 observed_ms={observed} tick_s={tick}")


def log(route="data"):
    rows = [f"LogPython: [EncounterActivation] route={route}", f"LogPython: [ERControlLatency] route={route}"]
    for case in receipt.EXPECTED_CASES:
        rows.append(sample(case))
    return "\n".join(rows)


class ChargeReceiptTests(unittest.TestCase):
    def test_retained_c971_filtered_log_uses_same_run_activation_witness(self):
        root = Path(__file__).resolve().parents[2]
        evidence = root / "Docs" / "BossCombatReview" / "Execution" / "Claude" / "P_C971_ERLATENCY"
        data_value = receipt.parse_file(evidence / "probe_data_lines.txt", build_id="TEST-FIXTURE-ONLY",
                                        route_witness_file=evidence / "probe_data.log")
        self.assertEqual(data_value["route"], "data")
        self.assertEqual(len(data_value["samples"]), 4)
        with self.assertRaisesRegex(ValueError, "route witness=data disagrees with probe route=legacy"):
            receipt.parse_file(evidence / "probe_legacy_lines.txt", build_id="TEST-FIXTURE-ONLY",
                               route_witness_file=evidence / "probe_legacy.log")

    def test_unreal_p_log_prefixes_and_unrelated_pack_rows(self):
        raw = ("[2026.11.07-07.32.20:353][  5]LogTemp: Display: [EncounterActivation] default data startup: selected DA route=data\n"
               "[2026.11.07-07.32.20:354][  6]LogTemp: Display: [EncounterActivation] route=data reason=StoredDefinition\n"
               "[2026.11.07-07.32.20:355][  7]LogPython: [ERControlLatency] route=legacy RPG_LEGACY_STARTUP=1\n")
        for index, case in enumerate(receipt.EXPECTED_CASES):
            prefix = "[ERControlLatency]" if index % 2 == 0 else "[ERControlLatency]"
            raw += "[2026.11.07-07.32.56:242][984]LogPython: %s sample %s\n" % (prefix, sample(case).split("sample ", 1)[1])
        raw += "\n[2026.11.07-07.32.56:243][985]LogRPGDodge: first_dodge_activation_trace active=0"
        with self.assertRaisesRegex(ValueError, "route witness=data disagrees with probe route=legacy"):
            receipt.parse_text(raw, build_id="TEST-ONLY")
        raw = raw.replace("[ERControlLatency] route=legacy", "[ERControlLatency] route=data")
        result = receipt.parse_text(raw, build_id="TEST-ONLY")
        self.assertEqual(result["route"], "data")
        self.assertEqual(len(result["samples"]), 4)
        self.assertIn("EncounterActivation", result["parser_scope"])

    def test_reads_route_cases_and_tick_bounded_fields(self):
        result = receipt.parse_text(log("legacy"), build_id="BUILD-269", input_sha256="a" * 64)
        self.assertEqual(result["route"], "legacy")
        self.assertEqual(result["build_id"], "BUILD-269")
        self.assertEqual(len(result["samples"]), 4)
        self.assertEqual(result["samples"][2]["case"], "R2_hold_0.36s")
        self.assertEqual(result["samples"][2]["nominal_requested_hold_s"], 0.36)
        self.assertTrue(result["observations_are_game_tick_bounded_not_device_latency"])

    def test_requires_explicit_operator_build_identity(self):
        with self.assertRaisesRegex(ValueError, "build_id is required"):
            receipt.parse_text(log(), build_id="")

    def test_requires_one_explicit_route(self):
        with self.assertRaisesRegex(ValueError, "EncounterActivation.*route witness"):
            receipt.parse_text("\n".join(sample(case) for case in receipt.EXPECTED_CASES), build_id="B1")
        with self.assertRaisesRegex(ValueError, "conflicting probe route values"):
            receipt.parse_text(log() + "\nLogPython: [Showcase] route=legacy", build_id="B1")

    def test_lead_mislabelled_legacy_fixture_is_rejected_by_activation_witness(self):
        root = Path(__file__).resolve().parents[2]
        log_path = (root / "Docs/BossCombatReview/Execution/Claude/P_C1095_KI192REPEAT"
                    / "mislabelled_legacy_is_data/probe_legacy_r1.log")
        with self.assertRaisesRegex(ValueError, "route witness=data disagrees with probe route=legacy"):
            receipt.parse_file(log_path, build_id="BUILD-269")

    def test_lead_truelegacy_and_data_fixtures_follow_activation_witness(self):
        root = Path(__file__).resolve().parents[2] / "Docs/BossCombatReview/Execution/Claude/P_C1095_KI192REPEAT"
        expected = {"probe_truelegacy_r1.log": "legacy", "probe_data_r1.log": "data"}
        for filename, route in expected.items():
            with self.subTest(filename=filename):
                value = receipt.parse_file(root / filename, build_id="BUILD-269")
                self.assertEqual(value["route"], route)
                self.assertEqual(len(value["samples"]), 4)

    def test_full_editor_startup_route_does_not_conflict_with_driver_route(self):
        raw = ("[EncounterActivation] default data startup: selected DA_Sevarog route=data\n"
               "[EncounterActivation] route=legacy reason=NoSelectionAndConfigEnabled\n"
               "LogPython: [ERControlLatency] route=legacy RPG_LEGACY_STARTUP=1\n")
        raw += "\n".join(sample(case) for case in receipt.EXPECTED_CASES)
        self.assertEqual(receipt.parse_text(raw, build_id="B1")["route"], "legacy")

    def test_rejects_missing_case(self):
        text = "\n".join(("LogPython: [EncounterActivation] route=data", "LogPython: [ERControlLatency] route=data", *(sample(case) for case in list(receipt.EXPECTED_CASES)[:-1])))
        with self.assertRaisesRegex(ValueError, "missing required"):
            receipt.parse_text(text, build_id="B1")

    def test_rejects_duplicate_case(self):
        text = log() + "\n" + sample("R2_hold_0.36s")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            receipt.parse_text(text, build_id="B1")

    def test_rejects_missing_montage_or_timing_fields(self):
        text = log().replace(sample("R2_hold_0.36s"), "sample case=R2_hold_0.36s montage= position=0.029 observed_ms=393.00")
        with self.assertRaisesRegex(ValueError, "malformed"):
            receipt.parse_text(text, build_id="B1")

    def test_rejects_negative_numeric_fields(self):
        text = log().replace(sample("R2_hold_0.36s"), sample("R2_hold_0.36s", observed="-1"))
        with self.assertRaisesRegex(ValueError, "non-negative"):
            receipt.parse_text(text, build_id="B1")


if __name__ == "__main__":
    unittest.main()
