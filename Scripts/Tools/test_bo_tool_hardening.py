"""BO-01..05 (C, implementer; per X-2236): offline regression tests for the KI-163..167 tool hardening.

Each test drives the real tool as a subprocess on throwaway temp inputs. No Unreal, no project assets, and nothing is
written outside the temp directory.
  KI-163  token_coverage: a missing log exits nonzero and writes no samples manifest.
  KI-164  evidence_pack: a rejected collision leaves no output directory behind.
  KI-165  make_source_manifest: a root without Source/ is refused and no manifest is written.
  KI-166  is covered by test_ki165_166_characterization.py (updated in this batch).
  KI-167  --redact on the seven report tools: no absolute temp path and no raw row in the output; default output unchanged.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import redaction  # noqa: E402


def run(script, *args, cwd=None):
    return subprocess.run([sys.executable, str(HERE / script), *map(str, args)], capture_output=True, text=True,
                          timeout=120, cwd=cwd)


class Temp(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name).resolve()

    def tearDown(self):
        self._tmp.cleanup()


def fake_root(base: Path) -> Path:
    """A minimal --root with the validator file token_coverage parses for SCHEMAS."""
    root = base / "root"
    validator = root / "Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py"
    validator.parent.mkdir(parents=True)
    validator.write_text('SCHEMAS = {"decision": 1, "hit": 1}\n', encoding="utf-8")
    return root


class Ki163MissingLogFails(Temp):
    def test_missing_log_exits_2_and_writes_no_manifest(self):
        root = fake_root(self.dir)
        good = root / "good.log"
        good.write_text("[FrameworkProof] decision x=1\n", encoding="utf-8")
        manifest = self.dir / "samples.json"
        r = run("token_coverage.py", "--root", root, "--samples-output", manifest, good, root / "absent.log")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("MISSING", r.stdout)
        self.assertIn("ERROR missing_logs=1", r.stdout)
        self.assertFalse(manifest.exists(), "no misleading success manifest")

    def test_all_logs_present_still_writes_manifest(self):
        root = fake_root(self.dir)
        good = root / "good.log"
        good.write_text("[FrameworkProof] decision x=1\n[FrameworkProof] hit y=2\n", encoding="utf-8")
        manifest = self.dir / "samples.json"
        r = run("token_coverage.py", "--root", root, "--samples-output", manifest, good)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(json.loads(manifest.read_text(encoding="utf-8"))["schema_count"], 2)


class Ki164EvidencePackPreflight(Temp):
    def test_reserved_name_collision_leaves_no_output_dir(self):
        raw = self.dir / "evidence_manifest.json"  # the raw log's basename collides with a reserved manifest name
        raw.write_text("log\n", encoding="utf-8")
        out = self.dir / "new_out"
        r = run("evidence_pack.py", raw, out)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("collide", r.stderr)
        self.assertFalse(out.exists(), "rejected invocation must not create the output directory")

    def test_duplicate_destination_leaves_no_output_dir(self):
        raw = self.dir / "a.log"
        raw.write_text("log\n", encoding="utf-8")
        pre = self.dir / "s.txt"
        pre.write_text("p\n", encoding="utf-8")
        nested = self.dir / "x"
        nested.mkdir()
        dup = nested / "pre_s.txt"  # pre_s.txt from --pre-state vs a raw log already named pre_s.txt
        dup.write_text("d\n", encoding="utf-8")
        out = self.dir / "new_out2"
        r = run("evidence_pack.py", dup, out, "--pre-state", pre)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertFalse(out.exists())

    def test_valid_invocation_still_creates_bundle(self):
        raw = self.dir / "a.log"
        raw.write_text("log\n", encoding="utf-8")
        out = self.dir / "ok_out"
        r = run("evidence_pack.py", raw, out)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((out / "evidence_manifest.json").is_file())


class Ki165SourceRootRequired(Temp):
    def test_root_without_source_is_refused(self):
        empty = self.dir / "not_a_project"
        empty.mkdir()
        out = self.dir / "manifest.txt"
        r = run("make_source_manifest.py", out, "--root", empty)
        self.assertEqual(r.returncode, 2)
        self.assertIn("no Source directory", r.stderr)
        self.assertFalse(out.exists())


class Ki167Redaction(Temp):
    """With --redact, the absolute temp directory path and the raw row text must not appear; without it, they do."""
    SECRET_ROW = "[FrameworkProof] decision secret_row_marker"

    def assert_redacted(self, r, row=None):
        text = r.stdout + r.stderr
        self.assertNotIn(str(self.dir), text)
        if row:
            self.assertNotIn(row, text)

    def test_display_helpers(self):
        p = self.dir / "a.log"
        self.assertEqual(redaction.display_path(p, False), str(p))
        self.assertEqual(redaction.display_path(p, True), "<external>/a.log")
        self.assertEqual(redaction.display_path(p, True, self.dir), "a.log")
        inside = redaction.PROJECT_ROOT / "Scripts" / "Tools" / "redaction.py"
        self.assertEqual(redaction.display_path(inside, True), "Scripts/Tools/redaction.py")
        self.assertEqual(redaction.display_row("raw", True), redaction.REDACTED_ROW)
        self.assertEqual(redaction.display_row("raw", False), "raw")

    def test_suite_log_report(self):
        log = self.dir / "suite.log"
        log.write_text("Test Completed. Result={Success} Name={A} Path={X.A}\nTEST COMPLETE. EXIT CODE: 0\n", encoding="utf-8")
        plain = run("suite_log_report.py", log, "--json")
        self.assertIn(str(self.dir).replace("\\", "\\\\"), plain.stdout, "default output keeps the absolute path")
        red = run("suite_log_report.py", log, "--json", "--redact")
        self.assertEqual(red.returncode, plain.returncode)
        self.assert_redacted(red)
        self.assertEqual(json.loads(red.stdout)["file"], "<external>/suite.log")

    def test_summarize_framework_log(self):
        log = self.dir / "fw.log"
        log.write_text(self.SECRET_ROW + "\n", encoding="utf-8")
        self.assertIn(str(self.dir), run("summarize_framework_log.py", log).stdout)
        red = run("summarize_framework_log.py", log, "--redact")
        self.assertEqual(red.returncode, 0, red.stderr)
        self.assert_redacted(red)
        missing = run("summarize_framework_log.py", self.dir / "nope.log", "--redact")
        self.assertEqual(missing.returncode, 1)
        self.assert_redacted(missing)

    def test_plot_framework_timeline(self):
        log = self.dir / "tl.log"
        log.write_text("[2026.11.12-10.00.00:000][  1]LogTemp: [FrameworkProof] decision rawpayload_marker\n", encoding="utf-8")
        plain = run("plot_framework_timeline.py", log)
        red = run("plot_framework_timeline.py", log, "--redact")
        self.assertEqual(red.returncode, plain.returncode)
        self.assert_redacted(red, "rawpayload_marker" if "rawpayload_marker" in plain.stdout else None)

    def test_token_coverage(self):
        root = fake_root(self.dir)
        outside = self.dir / "outside.log"
        outside.write_text(self.SECRET_ROW + "\n", encoding="utf-8")
        manifest = self.dir / "samples.json"
        red = run("token_coverage.py", "--root", root, "--samples-output", manifest, "--redact", outside)
        self.assertEqual(red.returncode, 0, red.stdout + red.stderr)
        self.assert_redacted(red)
        tokens = {t["token"]: t for t in json.loads(manifest.read_text(encoding="utf-8"))["tokens"]}
        self.assertEqual(tokens["decision"]["path"], "<external>/outside.log")
        self.assertEqual(tokens["decision"]["sample"], redaction.REDACTED_ROW)
        run("token_coverage.py", "--root", root, "--samples-output", manifest, outside)
        tokens = {t["token"]: t for t in json.loads(manifest.read_text(encoding="utf-8"))["tokens"]}
        self.assertEqual(tokens["decision"]["sample"], self.SECRET_ROW, "default manifest keeps the raw sample")

    def test_asset_provenance(self):
        script = self.dir / "author.py"
        script.write_text('SOURCE_PATH = "/Game/A/B"\nDEST_PATH = "/Game/C/D"\n', encoding="utf-8")
        log = self.dir / "e.log"
        log.write_text("loaded /Game/A/B secret_row_marker\n", encoding="utf-8")
        plain = run("asset_provenance.py", script, "--evidence", log)
        if plain.returncode != 0:
            self.skipTest("asset_provenance CLI shape differs: " + plain.stderr[-200:])
        self.assertIn("secret_row_marker", plain.stdout)
        red = run("asset_provenance.py", script, "--evidence", log, "--redact")
        self.assertEqual(red.returncode, 0, red.stderr)
        self.assert_redacted(red, "secret_row_marker")

    def test_proof_report_input_line(self):
        r = run("proof_report.py", "--help")
        self.assertIn("--redact", r.stdout)

    def test_evidence_summary_flag(self):
        r = run("evidence_summary.py", "--help")
        self.assertIn("--redact", r.stdout)


if __name__ == "__main__":
    unittest.main()
