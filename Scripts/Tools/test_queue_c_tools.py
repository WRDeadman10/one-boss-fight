"""Offline fixture checks for Queue C parser, suite, diff, and path tools."""
import json
import hashlib
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from diff_suite_logs import compare, load, main as diff_main
from detect_duplicate_pie_runs import scan as scan_duplicate_pie_runs
from evidence_pack import main as evidence_pack_main, safe_target
from framework_results import counter_delta, parse
from proof_report import check_identity, main as proof_report_main, run_completeness_issues
from suite_log_report import main as suite_log_main, summarize
from verify_evidence_manifest import verify as verify_evidence_manifest


class QueueCToolTests(unittest.TestCase):
    def test_duplicate_pie_run_detector_preserves_original_line_boundaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "combined.log"
            run = "LogInit: Display: Running engine for game: OneBossFight\n[FrameworkProof] RESULT outcome=CompletedTelemetryOnly\nLogExit: Exiting.\n"
            log.write_text("header\n" + run + run, encoding="utf-8")
            runs, duplicates = scan_duplicate_pie_runs(log)
        self.assertEqual([(row["start_line"], row["end_line"]) for row in runs], [(2, 4), (5, 7)])
        self.assertEqual(duplicates, [(2, 4, 5, 7)])

    def test_boss_proof_console_registrations_are_non_shipping_guarded(self):
        source_root = Path(__file__).resolve().parents[2] / "Source/OneBossFight"
        registrations = []
        for source in source_root.rglob("*.cpp"):
            guards = []
            for line_number, line in enumerate(source.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("#if "):
                    guards.append("!UE_BUILD_SHIPPING" in stripped)
                elif stripped.startswith("#endif") and guards:
                    guards.pop()
                if "TAutoConsoleVariable" in line and '"rpg.BossProof' in line:
                    registrations.append((source, line_number, any(guards)))
        self.assertTrue(registrations, "expected at least one BossProof console registration")
        unguarded = [f"{path}:{line}" for path, line, guarded in registrations if not guarded]
        self.assertEqual(unguarded, [], "Shipping-visible BossProof registrations: " + ", ".join(unguarded))

    def test_evidence_manifest_reports_mutated_original_relative_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = root / "run.log"
            original = b"original evidence\n"
            evidence.write_bytes(original)
            manifest = root / "evidence_manifest.json"
            manifest.write_text(json.dumps({"schema": 1, "files": [{
                "file": evidence.name,
                "bytes": len(original),
                "sha256": hashlib.sha256(original).hexdigest(),
            }]}), encoding="utf-8")
            self.assertEqual(verify_evidence_manifest(manifest), [])
            evidence.write_bytes(b"mutated evidence\n")
            issues = verify_evidence_manifest(manifest)
        self.assertEqual(len(issues), 2)
        self.assertTrue(any("size mismatch 'run.log'" in issue for issue in issues))
        self.assertTrue(any("hash mismatch 'run.log'" in issue for issue in issues))

    def test_evidence_manifest_rejects_duplicate_entries_and_symlink_escape(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp)
            evidence = root / "run.log"
            evidence.write_text("evidence\n", encoding="utf-8")
            digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
            manifest = root / "evidence_manifest.json"
            row = {"file": "run.log", "sha256": digest}
            manifest.write_text(json.dumps({"schema": 1, "files": [row, row]}), encoding="utf-8")
            issues = verify_evidence_manifest(manifest)
            self.assertTrue(any("duplicate file entry 'run.log'" in issue for issue in issues))

            external = Path(outside) / "outside.log"
            external.write_text("outside\n", encoding="utf-8")
            link = root / "escape.log"
            try:
                link.symlink_to(external)
            except (OSError, NotImplementedError) as error:
                self.skipTest("symlink creation unavailable: %s" % error)
            link_hash = hashlib.sha256(external.read_bytes()).hexdigest()
            manifest.write_text(json.dumps({"schema": 1, "files": [{"file": "escape.log", "sha256": link_hash}]}), encoding="utf-8")
            issues = verify_evidence_manifest(manifest)
        self.assertTrue(any("unsafe path 'escape.log'" in issue for issue in issues))

    def test_evidence_manifest_documents_dot_alias_as_separate_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = root / "run.log"
            evidence.write_text("evidence\n", encoding="utf-8")
            digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
            manifest = root / "evidence_manifest.json"
            manifest.write_text(json.dumps({"schema": 1, "files": [
                {"file": "run.log", "sha256": digest},
                {"file": "./run.log", "sha256": digest},
            ]}), encoding="utf-8")
            self.assertEqual(verify_evidence_manifest(manifest), [])

    def test_expected_sheet_enabled_and_control_log_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expected = root / "FEATURE_EXPECTED.md"
            expected.write_text("## PASS\n- enabled feature emits `los_resume`\n- no `combo_start` control token\n", encoding="utf-8")
            enabled = root / "enabled.log"
            control = root / "control.log"
            enabled.write_text("[FrameworkProof] los_resume\n", encoding="utf-8")
            control.write_text("[FrameworkProof] los_resume\n[FrameworkProof] combo_start root=Root move=Move maxDepth=1\n", encoding="utf-8")

            with patch.object(sys, "argv", ["proof_report.py", str(enabled), str(expected)]), redirect_stdout(StringIO()):
                self.assertEqual(proof_report_main(), 0)
            output = StringIO()
            with patch.object(sys, "argv", ["proof_report.py", str(control), str(expected)]), redirect_stdout(output):
                self.assertEqual(proof_report_main(), 1)
            self.assertIn("expected absent combo_start", output.getvalue())
            self.assertIn(f"FAIL {expected}:3", output.getvalue())
            self.assertIn(f"sha256={hashlib.sha256(control.read_bytes()).hexdigest()}", output.getvalue())
            self.assertIn("mtime_utc=", output.getvalue())

    def test_proof_report_paired_control_token_leak_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expected = root / "FEATURE_EXPECTED.md"
            expected.write_text("## PASS\n- enabled feature emits `los_resume`\n- no `combo_start` in the negative control\n", encoding="utf-8")
            enabled = root / "enabled.log"
            enabled.write_text("[FrameworkProof] los_resume\n", encoding="utf-8")
            control = root / "control.log"
            control.write_text("plain negative-control evidence\n", encoding="utf-8")
            output = StringIO()
            with patch.object(sys, "argv", ["proof_report.py", str(enabled), str(expected), "--control-log", str(control)]), redirect_stdout(output):
                self.assertEqual(proof_report_main(), 0)
            self.assertIn("absent combo_start", output.getvalue())

            control.write_text("[FrameworkProof] combo_start root=Root move=Move maxDepth=1\n", encoding="utf-8")
            output = StringIO()
            with patch.object(sys, "argv", ["proof_report.py", str(enabled), str(expected), "--control-log", str(control)]), redirect_stdout(output):
                self.assertEqual(proof_report_main(), 1)
            self.assertIn("expected absent combo_start", output.getvalue())

    def test_proof_report_reports_run_identity_mismatch_before_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expected = root / "FEATURE_EXPECTED.md"
            expected.write_text("## PASS\n- emits `los_resume`\n", encoding="utf-8")
            log = root / "run.log"
            log.write_text("profile=WrongProfile\n[FrameworkProof] los_resume\n", encoding="utf-8")
            output = StringIO()
            argv = ["proof_report.py", str(log), str(expected), "--expect-profile", "ExpectedProfile"]
            with patch.object(sys, "argv", argv), redirect_stdout(output):
                self.assertEqual(proof_report_main(), 1)
            report = output.getvalue()
            self.assertIn("IDENTITY MISMATCH profile", report)
            self.assertLess(report.index("IDENTITY MISMATCH"), report.index("Evidence presence report"))

    def test_proof_report_missing_expected_identity_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "run.log"
            log.write_text("[FrameworkProof] los_resume\n", encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                failures = check_identity(log, {"map": "L_SevarogArena"})
        self.assertEqual(len(failures), 1)
        self.assertIn("IDENTITY MISSING", output.getvalue())

    def test_proof_report_requires_paired_control_identity_and_matches_positive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expected = root / "FEATURE_EXPECTED.md"
            expected.write_text("## PASS\n- emits `los_resume`\n", encoding="utf-8")
            enabled = root / "enabled.log"
            control = root / "control.log"
            enabled.write_text("map=Arena profile=Profile source=abc123\n[FrameworkProof] los_resume\n", encoding="utf-8")
            control.write_text("map=Arena profile=Profile source=abc123\n", encoding="utf-8")
            argv = ["proof_report.py", str(enabled), str(expected), "--control-log", str(control),
                    "--control-expect-map", "Arena", "--control-expect-profile", "Profile",
                    "--control-expect-source", "abc123"]
            output = StringIO()
            with patch.object(sys, "argv", argv), redirect_stdout(output):
                self.assertEqual(proof_report_main(), 0)
            self.assertIn("IDENTITY MATCH map=Arena", output.getvalue())
            self.assertIn("IDENTITY MATCH source=abc123", output.getvalue())

            control.write_text("map=Other profile=OtherProfile source=changed\n", encoding="utf-8")
            argv[argv.index("Arena")] = "Other"
            argv[argv.index("Profile")] = "OtherProfile"
            argv[argv.index("abc123")] = "changed"
            output = StringIO()
            with patch.object(sys, "argv", argv), redirect_stdout(output):
                self.assertEqual(proof_report_main(), 1)
            self.assertIn("IDENTITY MISMATCH paired map differs", output.getvalue())
            self.assertIn("IDENTITY MISMATCH paired profile differs", output.getvalue())
            self.assertIn("IDENTITY MISMATCH paired source differs", output.getvalue())

            control.write_text("profile=Profile\n", encoding="utf-8")
            argv[argv.index("Other")] = "Arena"
            argv[argv.index("OtherProfile")] = "Profile"
            argv[argv.index("changed")] = "abc123"
            output = StringIO()
            with patch.object(sys, "argv", argv), redirect_stdout(output):
                self.assertEqual(proof_report_main(), 1)
            self.assertIn("IDENTITY MISSING control missing required map", output.getvalue())

    def test_proof_report_completeness_accepts_repeated_result_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "run.log"
            log.write_text("[FrameworkProof] RESULT outcome=Completed\n[FrameworkProof] RESULT outcome=Completed\nLogExit: Exiting.\n", encoding="utf-8")
            self.assertEqual(run_completeness_issues(log), [])

    def test_proof_report_distinguishes_incomplete_run_from_feature_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expected = root / "FEATURE_EXPECTED.md"
            expected.write_text("## PASS\n- emits `los_resume`\n", encoding="utf-8")
            log = root / "run.log"
            log.write_text("[FrameworkProof] los_resume\nLogExit: Exiting.\n", encoding="utf-8")
            output = StringIO()
            argv = ["proof_report.py", str(log), str(expected), "--require-complete-run"]
            with patch.object(sys, "argv", argv), redirect_stdout(output):
                self.assertEqual(proof_report_main(), 2)
            self.assertIn("missing terminal [FrameworkProof] RESULT", output.getvalue())
            self.assertIn("RESULT: INCOMPLETE RUN", output.getvalue())

            log.write_text("[FrameworkProof] RESULT outcome=Completed\n[FrameworkProof] los_resume\n", encoding="utf-8")
            output = StringIO()
            with patch.object(sys, "argv", argv), redirect_stdout(output):
                self.assertEqual(proof_report_main(), 2)
            self.assertIn("missing orderly LogExit", output.getvalue())

    def test_result_lifetime_counters_use_successive_result_deltas(self):
        gen_one = {"acceptedHits": "3", "attacks": "4"}
        gen_two = {"acceptedHits": "5", "attacks": "6"}
        self.assertIsNone(counter_delta(None, gen_one))
        self.assertEqual(counter_delta(gen_one, gen_two), {"acceptedHits": 2, "attacks": 2})

    def test_framework_results_flags_missing_repeated_and_nonnumeric_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "results.log"
            log.write_text("""[FrameworkProof] RESULT acceptedHits=x
[FrameworkProof] encounter_reset generation=2 oldState=Dead
[FrameworkProof] RESULT outcome=Won acceptedHits=2
[FrameworkProof] RESULT outcome=Won attacks=oops
""", encoding="utf-8")
            rows, diagnostics = parse(log)
        self.assertEqual([row["generation"] for row in rows], ["unknown", "2", "2"])
        self.assertTrue(any("missing required field outcome" in item for item in diagnostics))
        self.assertTrue(any("acceptedHits must be" in item for item in diagnostics))
        self.assertTrue(any("repeated RESULT" in item for item in diagnostics))

    def test_suite_summary_json_data_is_deterministic_and_names_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "suite.log"
            log.write_text("""Test Completed. Result={Success} Name={Alpha} Path={Suite.Alpha}
Test Completed. Result={Fail} Name={Beta} Path={Suite.Beta}
""", encoding="utf-8")
            result = summarize(log)
        encoded_a = json.dumps(result, sort_keys=True)
        encoded_b = json.dumps(result, sort_keys=True)
        self.assertEqual(encoded_a, encoded_b)
        self.assertEqual((result["finished"], result["passed"], result["failed"]), (2, 1, 1))
        self.assertEqual(result["failures"], ["Suite.Beta"])

    def test_suite_diff_states(self):
        before = {"A": "Success", "B": "Success"}
        self.assertEqual(compare(before, before), ([], [], []))
        self.assertEqual(compare(before, {"A": "Fail", "C": "Success"}), (["C"], ["B"], ["A"]))

    def test_suite_diff_rejects_logs_without_completion_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "empty.log"
            log.write_text("startup only\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "no Test Completed"):
                load(log)

    def test_suite_diff_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            before, same, changed, invalid = (root / name for name in ("before.log", "same.log", "changed.log", "invalid.log"))
            row = "Test Completed. Result={Success} Name={Alpha} Path={Suite.Alpha}\n"
            marker = "TEST COMPLETE. EXIT CODE: 0\n"
            before.write_text(row + marker, encoding="utf-8")
            same.write_text(row + marker, encoding="utf-8")
            changed.write_text(row.replace("Success", "Fail") + marker, encoding="utf-8")
            invalid.write_text("startup only\n", encoding="utf-8")
            for other, expected in ((same, 0), (changed, 1), (invalid, 3)):
                with patch.object(sys, "argv", ["diff_suite_logs.py", str(before), str(other)]), redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                    self.assertEqual(diff_main(), expected)
            partial = root / "partial.log"
            partial.write_text(row, encoding="utf-8")
            output = StringIO()
            with patch.object(sys, "argv", ["diff_suite_logs.py", str(before), str(partial)]), redirect_stdout(output), redirect_stderr(StringIO()):
                self.assertEqual(diff_main(), 3)
            self.assertIn("PARTIAL", output.getvalue())

    def test_suite_summary_duplicate_identity_is_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "duplicates.log"
            row = "Test Completed. Result={Success} Name={Alpha} Path={Suite.Alpha}\n"
            log.write_text(row + row + "TEST COMPLETE. EXIT CODE: 0\n", encoding="utf-8")
            self.assertEqual(summarize(log)["duplicate_names"], ["Suite.Alpha"])
            with patch.object(sys, "argv", ["suite_log_report.py", str(log)]), redirect_stdout(StringIO()):
                self.assertEqual(suite_log_main(), 1)

    def test_suite_summary_requires_terminal_marker_unless_allow_partial(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            empty = root / "empty.log"
            empty.write_text("startup only\n", encoding="utf-8")
            output = StringIO()
            with patch.object(sys, "argv", ["suite_log_report.py", str(empty)]), redirect_stdout(output):
                self.assertEqual(suite_log_main(), 2)
            self.assertIn("PARTIAL", output.getvalue())

            partial = root / "partial.log"
            partial.write_text("Test Completed. Result={Success} Name={Alpha} Path={Suite.Alpha}\n", encoding="utf-8")
            with patch.object(sys, "argv", ["suite_log_report.py", str(partial)]), redirect_stdout(StringIO()):
                self.assertEqual(suite_log_main(), 2)
            output = StringIO()
            with patch.object(sys, "argv", ["suite_log_report.py", str(partial), "--allow-partial"],), redirect_stdout(output):
                self.assertEqual(suite_log_main(), 0)
            self.assertIn("not a pass certificate", output.getvalue())

            complete = root / "complete.log"
            complete.write_text("Test Completed. Result={Success} Name={Alpha} Path={Suite.Alpha}\nTEST COMPLETE. EXIT CODE: 0\n", encoding="utf-8")
            output = StringIO()
            with patch.object(sys, "argv", ["suite_log_report.py", str(complete)]), redirect_stdout(output):
                self.assertEqual(suite_log_main(), 0)
            self.assertIn("completion=COMPLETE", output.getvalue())

            empty_complete = root / "empty_complete.log"
            empty_complete.write_text("TEST COMPLETE. EXIT CODE: 0\n", encoding="utf-8")
            with patch.object(sys, "argv", ["suite_log_report.py", str(empty_complete)]), redirect_stdout(StringIO()):
                self.assertEqual(suite_log_main(), 2)

    def test_suite_tools_accept_truncated_logs_with_completed_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            partial_a, partial_b = root / "partial_a.log", root / "partial_b.log"
            partial_a.write_text("header\nTest Completed. Result={Success} Name={Alpha} Path={Suite.Alpha}\nno terminal marker", encoding="utf-8")
            partial_b.write_text("different header\nTest Completed. Result={Success} Name={Alpha} Path={Suite.Alpha}\ntruncated", encoding="utf-8")
            self.assertEqual(summarize(partial_a)["finished"], 1)
            self.assertEqual(load(partial_a), load(partial_b))

    def test_evidence_target_is_a_direct_child_of_output_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            out = root / "evidence"
            out.mkdir()
            source_dir = root / "nested"
            source_dir.mkdir()
            source = source_dir / "raw.log"
            source.write_text("evidence", encoding="utf-8")
            target = safe_target(out, source, "raw")
            self.assertEqual(target.parent, out)
            self.assertTrue(target.resolve().is_relative_to(out))

    def test_evidence_pack_copies_source_and_manifest_within_output_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            source_dir = root / "source" / "nested"
            source_dir.mkdir(parents=True)
            source = source_dir / "raw.log"
            source.write_text("fixture evidence", encoding="utf-8")
            out = root / "evidence"
            with patch.object(sys, "argv", ["evidence_pack.py", str(source), str(out)]), redirect_stdout(StringIO()):
                self.assertEqual(evidence_pack_main(), 0)
            copied = out / "raw.log"
            manifest = json.loads((out / "evidence_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(copied.read_text(encoding="utf-8"), "fixture evidence")
            self.assertTrue(copied.resolve().is_relative_to(out))
            self.assertEqual(manifest["files"][0]["file"], "raw.log")

    def test_evidence_pack_rejects_reserved_manifest_name_before_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            source = root / "evidence_manifest.json"
            source.write_text("not a manifest", encoding="utf-8")
            out = root / "evidence"
            with patch.object(sys, "argv", ["evidence_pack.py", str(source), str(out)]), redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                with self.assertRaises(SystemExit) as error:
                    evidence_pack_main()
            self.assertEqual(error.exception.code, 2)
            self.assertFalse((out / source.name).exists())


if __name__ == "__main__":
    unittest.main()
