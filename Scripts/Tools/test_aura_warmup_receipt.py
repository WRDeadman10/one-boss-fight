"""Offline contracts for aura capture's brightness-ready manifests."""
import json
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from Scripts.Tools.aura_warmup_receipt import ASSETS, MANIFEST_SCHEMA, validate_warmup_receipt


def record(label, phase, brightness, game_time):
    return {"run": "runA", "route": "data", "capture_id": "runA:" + label,
            "schema": 1, "build_id": "BUILD-TEST", "map": "L_SevarogArena",
            "frame": label, "phase": phase,
            "asset": ("/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_Boost.NS_Boss_PhaseTwoAura_Boost"
                      if label.startswith("candidate_discard") or phase == "candidate" else
                      "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura.NS_Boss_PhaseTwoAura"),
            "active": "True",
            "mean_gray": brightness, "game_time_s": game_time}


class AuraWarmupReceiptTests(unittest.TestCase):
    def test_receipt_asset_ids_match_the_comparison_driver(self):
        source = (Path(__file__).resolve().parents[2] / "Scripts" / "Editor" /
                  "pie_aura_comparison.py").read_text(encoding="utf-8")
        self.assertIn('APPROVED_PATH = "' + ASSETS["approved"] + '"', source)
        self.assertIn('CANDIDATE_DEFAULT_PATH = "' + ASSETS["candidate"] + '"', source)
        self.assertIn("MANIFEST_SCHEMA = %d" % MANIFEST_SCHEMA, source)
        self.assertIn('"build_id": AURA_COMPARE_BUILD_ID', source)
        self.assertIn('"map": AURA_COMPARE_MAP', source)

    def test_candidate_receipt_accepts_named_lite_variant_and_rejects_unrelated_asset(self):
        rows = [record("warmup_discard_1", "warmup", 6.0, 1.0),
                record("approved", "approved", 6.0, 1.1),
                record("candidate_discard_1", "warmup", 6.0, 2.0),
                record("boost_candidate", "candidate", 6.0, 2.1)]
        lite = "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_BoostLite.NS_Boss_PhaseTwoAura_BoostLite"
        for row in rows[2:]:
            row["asset"] = lite
        self.assertEqual(len(validate_warmup_receipt(rows, "runA", "data")), 2)
        unrelated = [dict(row) for row in rows]
        unrelated[-1]["asset"] = "/Game/Other/NS_Boss_PhaseTwoAura_BoostLite.NS_Boss_PhaseTwoAura_BoostLite"
        with self.assertRaisesRegex(ValueError, "candidate target asset identity mismatch"):
            validate_warmup_receipt(unrelated, "runA", "data")

    def test_manifest_requires_supported_schema_and_known_build_map_route(self):
        rows = [record("warmup_discard_1", "warmup", 6.0, 1.0),
                record("approved", "approved", 6.0, 1.1)]
        for changed, error in ((dict(rows[0], schema=2), "unsupported manifest schema"),
                               (dict(rows[0], build_id="UNKNOWN"), "build_id"),
                               (dict(rows[0], build_id="  "), "build_id"),
                               (dict(rows[0], map="UNKNOWN"), "map"),
                               (dict(rows[0], route="unknown"), "route")):
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                validate_warmup_receipt([changed, rows[1]], "runA", "data")

    def test_run_and_frame_labels_are_safe_components_and_provenance_is_constant(self):
        rows = [record("warmup_discard_1", "warmup", 6.0, 1.0),
                record("approved", "approved", 6.0, 1.1)]
        unsafe = [dict(rows[0], frame="../approved", capture_id="runA:../approved"), rows[1]]
        with self.assertRaisesRegex(ValueError, "unsafe frame label"):
            validate_warmup_receipt(unsafe, "runA", "data")
        changed = [rows[0], dict(rows[1], build_id="BUILD-OTHER")]
        with self.assertRaisesRegex(ValueError, "provenance drift"):
            validate_warmup_receipt(changed, "runA", "data")
        changed_map = [rows[0], dict(rows[1], map="L_Other")]
        with self.assertRaisesRegex(ValueError, "provenance drift"):
            validate_warmup_receipt(changed_map, "runA", "data")
        changed_route = [rows[0], dict(rows[1], route="legacy")]
        with self.assertRaisesRegex(ValueError, "run/route mismatch"):
            validate_warmup_receipt(changed_route, "runA", "data")
        with self.assertRaisesRegex(ValueError, "unsafe run id"):
            validate_warmup_receipt([dict(rows[0], run="../run", capture_id="../run:warmup_discard_1"), rows[1]],
                                    "../run", "data")

    def test_frame_labels_reject_both_separators_and_control_characters(self):
        rows = [record("warmup_discard_1", "warmup", 6.0, 1.0),
                record("approved", "approved", 6.0, 1.1)]
        for unsafe_label in ("folder\\frame", "folder/frame", "bad\nframe", "bad\x00frame"):
            changed = [dict(rows[0], frame=unsafe_label, capture_id="runA:" + unsafe_label), rows[1]]
            with self.subTest(label=repr(unsafe_label)), self.assertRaisesRegex(ValueError, "unsafe frame label"):
                validate_warmup_receipt(changed, "runA", "data")

    def test_approved_frame_requires_bright_same_run_warmup_within_bounds(self):
        rows = [record("warmup_discard_1", "warmup", 0.0, 10.0),
                record("warmup_discard_2", "warmup", 6.0, 10.1),
                record("approved", "approved", 7.0, 10.2)]
        result = validate_warmup_receipt(rows, "runA", "data")
        self.assertEqual(result[0]["warmup_frames"], 2)
        self.assertEqual(result[0]["ready_frame"], "warmup_discard_2")

    def test_all_black_too_many_stale_and_candidate_without_warmup_fail(self):
        black = [record("warmup_discard_1", "warmup", 0.0, 1.0),
                 record("approved", "approved", 6.0, 1.1)]
        with self.assertRaisesRegex(ValueError, "no bright warmup"):
            validate_warmup_receipt(black, "runA", "data")
        too_many = [record("warmup_discard_%d" % n, "warmup", 0.0, n / 15) for n in range(1, 22)]
        too_many += [record("warmup_discard_22", "warmup", 6.0, 22 / 15),
                     record("approved", "approved", 6.0, 23 / 15)]
        with self.assertRaisesRegex(ValueError, "20 frames"):
            validate_warmup_receipt(too_many, "runA", "data")
        with self.assertRaisesRegex(ValueError, "run/route mismatch"):
            validate_warmup_receipt([record("warmup_discard_1", "warmup", 6.0, 1.0),
                                     record("approved", "approved", 6.0, 1.1)], "other", "data")
        delayed = [record("warmup_discard_1", "warmup", 6.0, 1.0),
                   record("approved", "approved", 6.0, 6.0)]
        with self.assertRaisesRegex(ValueError, "target capture exceeds"):
            validate_warmup_receipt(delayed, "runA", "data")
        nonfinite = [record("warmup_discard_1", "warmup", float("inf"), 1.0),
                     record("approved", "approved", 6.0, 1.1)]
        with self.assertRaisesRegex(ValueError, "non-finite"):
            validate_warmup_receipt(nonfinite, "runA", "data")

    def test_capture_identity_labels_and_order_are_strict(self):
        valid = [record("warmup_discard_1", "warmup", 6.0, 1.0),
                 record("approved", "approved", 6.0, 1.1),
                 record("candidate_discard_1", "warmup", 6.0, 2.0),
                 record("boost_candidate", "candidate", 6.0, 2.1)]
        validate_warmup_receipt(valid, "runA", "data")
        duplicate = [valid[0], dict(valid[1]), dict(valid[1])]
        with self.assertRaisesRegex(ValueError, "duplicate frame label"):
            validate_warmup_receipt(duplicate, "runA", "data")
        skipped = [record("warmup_discard_1", "warmup", 6.0, 1.0),
                   record("warmup_discard_3", "warmup", 6.0, 1.1),
                   record("approved", "approved", 6.0, 1.2)]
        with self.assertRaisesRegex(ValueError, "sequential warmup"):
            validate_warmup_receipt(skipped, "runA", "data")
        stale = [dict(valid[0], capture_id="other:approved"), valid[1]]
        with self.assertRaisesRegex(ValueError, "capture identity"):
            validate_warmup_receipt(stale, "runA", "data")
        wrong_phase = [valid[0], dict(valid[1], frame="boost_candidate",
                                      capture_id="runA:boost_candidate")]
        with self.assertRaisesRegex(ValueError, "phase/label mismatch"):
            validate_warmup_receipt(wrong_phase, "runA", "data")

    def test_every_manifest_row_has_finite_monotonic_time_and_targets_are_ordered(self):
        base = [record("warmup_discard_1", "warmup", 6.0, 1.0),
                record("approved", "approved", 6.0, 1.1),
                record("candidate_discard_1", "warmup", 6.0, 2.0),
                record("boost_candidate", "candidate", 6.0, 2.1)]
        validate_warmup_receipt(base, "runA", "data")
        with self.assertRaisesRegex(ValueError, "non-finite.*game_time"):
            validate_warmup_receipt([dict(base[0], game_time_s=float("nan"))] + base[1:],
                                    "runA", "data")
        with self.assertRaisesRegex(ValueError, "time regression"):
            validate_warmup_receipt([base[0], dict(base[1], game_time_s=0.9)] + base[2:],
                                    "runA", "data")
        with self.assertRaisesRegex(ValueError, "candidate capture precedes"):
            validate_warmup_receipt([base[0], dict(base[3], game_time_s=1.1),
                                     dict(base[1], game_time_s=1.2)], "runA", "data")
        with self.assertRaisesRegex(ValueError, "warmup phase order"):
            validate_warmup_receipt([base[0], base[1], record("warmup_discard_2", "warmup", 6.0, 1.2)],
                                    "runA", "data")

    def test_cli_malformed_manifest_is_nonzero_without_success_json(self):
        tool = Path(__file__).with_name("aura_warmup_receipt.py")
        bad = [record("warmup_discard_1", "warmup", 6.0, 1.0),
               dict(record("approved", "approved", 6.0, 1.1), capture_id="stale:capture")]
        with tempfile.TemporaryDirectory() as root:
            manifest = Path(root) / "manifest.jsonl"
            manifest.write_text("\n".join(json.dumps(row) for row in bad), encoding="utf-8")
            result = subprocess.run([sys.executable, str(tool), "--manifest", str(manifest),
                                     "--run", "runA", "--route", "data"],
                                    capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "")

    def test_cli_optional_png_verification_reports_run_route_and_file_count(self):
        tool = Path(__file__).with_name("aura_warmup_receipt.py")
        with tempfile.TemporaryDirectory(prefix="aura receipt space ") as root:
            rows = [record("warmup_discard_1", "warmup", 6.0, 1.0),
                    record("approved", "approved", 6.0, 1.1)]
            for row in rows:
                png = Path(root) / (row["frame"] + " capture.png")
                self.assertIn(" ", str(png))
                self.assertIn("\\", str(png))
                png.write_bytes(("synthetic " + row["frame"]).encode())
                row.update(png=str(png), png_exists=True,
                           png_sha256=hashlib.sha256(png.read_bytes()).hexdigest())
            manifest = Path(root) / "manifest.jsonl"
            manifest.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
            result = subprocess.run([sys.executable, str(tool), "--manifest", str(manifest),
                                     "--run", "runA", "--route", "data", "--verify-png-files"],
                                    capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["run"], "runA")
        self.assertEqual(receipt["route"], "data")
        self.assertEqual(receipt["verified_png_files"], 2)
        self.assertEqual(receipt["manifest_schema"], 1)
        self.assertEqual(receipt["png_verification"], "sha256")
        self.assertEqual(len(receipt["targets"]), 1)
        self.assertEqual(set(receipt), {"run", "route", "manifest_schema", "verified_png_files",
                                        "png_verification", "targets"})
        self.assertIs(type(receipt["manifest_schema"]), int)
        self.assertIs(type(receipt["verified_png_files"]), int)
        self.assertIs(type(receipt["targets"]), list)
        self.assertEqual(set(receipt["targets"][0]), {"phase", "target_frame", "ready_frame",
                                                     "warmup_frames", "ready_elapsed_s"})
        self.assertIs(type(receipt["targets"][0]["warmup_frames"]), int)
        self.assertIs(type(receipt["targets"][0]["ready_elapsed_s"]), float)

    def test_asset_and_active_state_are_bound_through_each_warmup_target(self):
        rows = [record("warmup_discard_1", "warmup", 6.0, 1.0),
                record("approved", "approved", 6.0, 1.1),
                record("candidate_discard_1", "warmup", 6.0, 2.0),
                record("boost_candidate", "candidate", 6.0, 2.1)]
        validate_warmup_receipt(rows, "runA", "data")
        wrong_asset = [dict(row) for row in rows]
        wrong_asset[1]["asset"] = "/Game/Other.Other"
        with self.assertRaisesRegex(ValueError, "approved target asset"):
            validate_warmup_receipt(wrong_asset, "runA", "data")
        wrong_active = [dict(row) for row in rows]
        wrong_active[-1]["active"] = "False"
        with self.assertRaisesRegex(ValueError, "target is not active"):
            validate_warmup_receipt(wrong_active, "runA", "data")
        borrowed = [dict(row) for row in rows]
        borrowed[2]["asset"] = rows[0]["asset"]
        with self.assertRaisesRegex(ValueError, "warmup asset"):
            validate_warmup_receipt(borrowed, "runA", "data")

    def test_optional_png_hash_verification_is_opt_in_and_fail_closed(self):
        with tempfile.TemporaryDirectory() as root:
            rows = [record("warmup_discard_1", "warmup", 6.0, 1.0),
                    record("approved", "approved", 6.0, 1.1)]
            for row in rows:
                png = Path(root) / (row["frame"] + ".png")
                png.write_bytes(("synthetic " + row["frame"]).encode())
                row.update(png=str(png), png_exists=True,
                           png_sha256=hashlib.sha256(png.read_bytes()).hexdigest())
            validate_warmup_receipt(rows, "runA", "data")
            validate_warmup_receipt([dict(rows[0]), dict(rows[1], png_sha256="0" * 64)],
                                    "runA", "data")
            with self.assertRaisesRegex(ValueError, "PNG hash mismatch"):
                validate_warmup_receipt([dict(rows[0]), dict(rows[1], png_sha256="0" * 64)],
                                        "runA", "data", verify_png_files=True)
            missing = [dict(rows[0]), dict(rows[1], png=str(Path(root) / "missing.png"))]
            with self.assertRaisesRegex(ValueError, "PNG file missing"):
                validate_warmup_receipt(missing, "runA", "data", verify_png_files=True)

    def test_png_paths_must_be_unique_per_capture(self):
        rows = [record("warmup_discard_1", "warmup", 6.0, 1.0),
                record("approved", "approved", 6.0, 1.1)]
        duplicate_path = os.path.abspath("same capture.png")
        for row in rows:
            row["png"] = duplicate_path
        with self.assertRaisesRegex(ValueError, "duplicate PNG path"):
            validate_warmup_receipt(rows, "runA", "data")

    def test_png_paths_are_unique_after_path_normalization(self):
        rows = [record("warmup_discard_1", "warmup", 6.0, 1.0),
                record("approved", "approved", 6.0, 1.1)]
        base = Path(os.path.abspath("same capture.png"))
        rows[0]["png"] = str(base.parent / "nested" / ".." / base.name)
        rows[1]["png"] = str(base)
        with self.assertRaisesRegex(ValueError, "duplicate PNG path"):
            validate_warmup_receipt(rows, "runA", "data")

    def test_approved_only_and_full_comparison_manifest_shapes(self):
        approved_only = [record("warmup_discard_1", "warmup", 6.0, 1.0),
                         record("approved", "approved", 6.0, 1.1)]
        full = approved_only + [record("candidate_discard_1", "warmup", 6.0, 2.0),
                                record("boost_candidate", "candidate", 6.0, 2.1)]
        self.assertEqual(len(validate_warmup_receipt(approved_only, "runA", "data")), 1)
        self.assertEqual(len(validate_warmup_receipt(full, "runA", "data")), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
