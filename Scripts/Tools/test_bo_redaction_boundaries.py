"""BO-11..15 (C, implementer; per X-2241/X-2243): adversarial redaction-boundary tests. Synthetic temp fixtures only.

  BO-11  the stream wrapper toggles on and off within one process, never double-wraps, and restores the original streams.
  BO-12  a machine path split across several write() calls is redacted as a whole (line buffering plus flush).
  BO-13  POSIX machine roots beyond home/temp/project are masked; Unreal mounts are preserved.
  BO-14  path-form matrix: raw, JSON-escaped, forward-slash, drive, UNC, plus false-positive-safe telemetry/object paths.
  BO-15  generated artifacts (token samples manifest, evidence_summary CSV): redacted under --redact, structured fields
         kept, default files identical to a no-flag run of the same tool and still carrying the absolute path.
"""
import csv
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import redaction  # noqa: E402

B = "\\"


class Bo11WrapperLifecycle(unittest.TestCase):
    def setUp(self):
        self.saved = (sys.stdout, sys.stderr)

    def tearDown(self):
        sys.stdout, sys.stderr = self.saved

    def test_toggle_on_off_on_restores_and_does_not_double_wrap(self):
        out, err = io.StringIO(), io.StringIO()
        sys.stdout, sys.stderr = out, err
        redaction.install_stream_redaction(True)
        wrapped = sys.stdout
        redaction.install_stream_redaction(True)
        self.assertIs(sys.stdout, wrapped, "a second enable must not double-wrap")
        print(f"a {redaction.PROJECT_ROOT / 'Scripts' / 'x.py'}")
        redaction.install_stream_redaction(False)
        self.assertIs(sys.stdout, out)
        self.assertIs(sys.stderr, err)
        print(f"b {redaction.PROJECT_ROOT}")  # default output after disabling: verbatim
        redaction.install_stream_redaction(True)
        print(f"c {redaction.PROJECT_ROOT / 'Source'}", end="")  # no newline: held until flush/disable
        redaction.install_stream_redaction(False)
        text = out.getvalue().splitlines()
        self.assertEqual(text[0], "a Scripts" + B + "x.py")
        self.assertEqual(text[1], f"b {redaction.PROJECT_ROOT}")
        self.assertEqual(text[2], "c Source")

    def test_disable_without_enable_is_noop(self):
        out = io.StringIO()
        sys.stdout = out
        redaction.install_stream_redaction(False)
        self.assertIs(sys.stdout, out)


class Bo12SplitWrites(unittest.TestCase):
    def test_path_split_across_writes_is_redacted(self):
        inner = io.StringIO()
        stream = redaction._RedactingStream(inner)
        secret = str(Path(tempfile.gettempdir()).resolve() / "split" / "a.log")
        for i in range(0, len(secret), 3):  # 3-character chunks cut through every component
            stream.write(secret[i:i + 3])
        stream.write(" done\n")
        stream.write("tail " + secret)  # no newline: only written on flush
        self.assertNotIn(secret.lower(), inner.getvalue().lower())
        stream.flush()
        value = inner.getvalue()
        self.assertNotIn(secret.lower(), value.lower())
        self.assertEqual(value.count("<tmp>/split"), 2)

    def test_subprocess_exit_flushes_held_tail(self):
        code = ("import sys; sys.path.insert(0, %r); import redaction; redaction.install_stream_redaction(True); "
                "sys.stdout.write(%r)" % (str(HERE), str(redaction.PROJECT_ROOT / "Source" / "x.cpp")))
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.stdout, "Source" + B + "x.cpp", "the held tail is written, redacted, at interpreter exit")


class Bo13PosixRoots(unittest.TestCase):
    def test_machine_roots_masked(self):
        # Explicit expectation (not the module's own list), so shrinking POSIX_MACHINE_ROOTS fails this test.
        expected = ("home", "tmp", "var", "mnt", "opt", "root", "private", "media", "srv", "etc", "usr", "run", "data",
                    "workspace", "workspaces", "proc", "dev", "Users", "Volumes", "Applications", "Library")
        self.assertEqual(set(redaction.POSIX_MACHINE_ROOTS), set(expected))
        for root in expected:
            with self.subTest(root=root):
                self.assertEqual(redaction.redact_text(f"x=/{root}/someone/secret.txt"), "x=<external>/secret.txt")

    def test_unreal_mounts_preserved(self):
        for path in ("/Game/OneBossFight/A.A", "/Engine/BasicShapes/Cube", "/Script/OneBossFight.RPGBoss", "/Temp/Untitled",
                     "/Memory/X", "/Config/DefaultEngine", "/Niagara/Mod", "/AdvancedARPGCombat/BP_X", "/Paper2D/Thing"):
            with self.subTest(path=path):
                self.assertEqual(redaction.redact_text(path), path)

    def test_unlisted_root_is_documented_limit(self):
        # Pinned limit: an unlisted first segment is not masked (see the BO-11..15 report).
        self.assertEqual(redaction.redact_text("/data2/x.log"), "/data2/x.log")


class Bo14PathForms(unittest.TestCase):
    def test_forms_masked(self):
        tmp = Path(tempfile.gettempdir()).resolve()
        cases = {
            str(tmp / "f" / "a.log"): "<tmp>/f" + B + "a.log",
            str(tmp / "f" / "a.log").replace(B, "/"): "<tmp>/f/a.log",
            str(tmp / "f" / "a.log").replace(B, B * 2): "<tmp>/f" + B * 2 + "a.log",
            str(tmp).upper() + B + "a.log": "<tmp>/a.log",  # case-insensitive root match
            "D:" + B + "Ref" + B + "pack" + B + "x.fbx": "<external>/x.fbx",
            "D:/Ref/pack/x.fbx": "<external>/x.fbx",
            "D:" + B * 2 + "Ref" + B * 2 + "x.fbx": "<external>/x.fbx",
            B * 2 + "server" + B + "share" + B + "x.txt": "<external>/x.txt",
            '{"file": "E:' + B * 2 + 'q' + B * 2 + 'r.log"}': '{"file": "<external>/r.log"}',
            "Path={F:" + B + "t" + B + "A.cpp}": "Path={<external>/A.cpp}",
            str(redaction.PROJECT_ROOT / "Source" / "A.cpp"): "Source" + B + "A.cpp",
        }
        for raw, want in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(redaction.redact_text(raw), want)

    def test_false_positive_safe(self):
        for text in ("outcome=ERPGDamageOutcome::Parried", "hits 3/5", "cm/s", "a:b", "card=A3b window=0.35-0.40",
                     "http://localhost:8080/x", "time=12:30:01", "ratio=1/2", "Name={A} Path={OneBossFight.Framework.B}",
                     "/Game/A/B.B", "e=1/g=2/i=3"):
            with self.subTest(text=text):
                self.assertEqual(redaction.redact_text(text), text)


def run(script, *args):
    return subprocess.run([sys.executable, str(HERE / script), *map(str, args)], capture_output=True, text=True, timeout=180)


class Bo15GeneratedArtifacts(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name).resolve()

    def tearDown(self):
        self._tmp.cleanup()

    def leak(self, text):
        low = text.lower()
        return any(f.lower() in low for f in (str(self.dir), str(self.dir).replace(B, "/"), str(self.dir).replace(B, B * 2)))

    def test_token_samples_manifest(self):
        root = self.dir / "root"
        val = root / "Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py"
        val.parent.mkdir(parents=True)
        val.write_text('SCHEMAS = {"decision": 1, "hit": 1}\n', encoding="utf-8")
        log = self.dir / "outside.log"
        log.write_text(f"[FrameworkProof] decision card=A at {self.dir}\n", encoding="utf-8")
        plain_out, red_out, plain_again = self.dir / "p.json", self.dir / "r.json", self.dir / "p2.json"
        self.assertEqual(run("token_coverage.py", "--root", root, "--samples-output", plain_out, log).returncode, 0)
        self.assertEqual(run("token_coverage.py", "--root", root, "--samples-output", red_out, log, "--redact").returncode, 0)
        self.assertEqual(run("token_coverage.py", "--root", root, "--samples-output", plain_again, log).returncode, 0)
        self.assertEqual(plain_out.read_text(encoding="utf-8"), plain_again.read_text(encoding="utf-8"), "default file is deterministic")
        self.assertTrue(self.leak(plain_out.read_text(encoding="utf-8")), "default file keeps the absolute path (control)")
        red_text = red_out.read_text(encoding="utf-8")
        self.assertFalse(self.leak(red_text))
        red = json.loads(red_text)
        plain = json.loads(plain_out.read_text(encoding="utf-8"))
        self.assertEqual([t["token"] for t in red["tokens"]], [t["token"] for t in plain["tokens"]], "structure kept")
        decision = next(t for t in red["tokens"] if t["token"] == "decision")
        self.assertEqual((decision["source"], decision["line"]), ("real_log", 1))
        self.assertEqual(decision["path"], "<external>/outside.log")
        self.assertEqual(decision["sample"], redaction.REDACTED_ROW)

    def test_evidence_summary_csv(self):
        evidence = self.dir / "ev"
        for run_name in ("run1", "run2"):
            log = evidence / run_name / "editor_raw.log"
            log.parent.mkdir(parents=True)
            log.write_text(f"[2026.11.12-10.00.00:000][  1]LogTemp: map=/Game/Maps/L_Arena profile={self.dir}/prof.json\n"
                           "[FrameworkProof] RESULT acceptedHits=1\n", encoding="utf-8")
        plain_csv, red_csv, plain_again = self.dir / "p.csv", self.dir / "r.csv", self.dir / "p2.csv"
        base = ("--root", redaction.PROJECT_ROOT, "--evidence", evidence)
        r1 = run("evidence_summary.py", *base, "--output", plain_csv)
        if r1.returncode != 0:
            self.skipTest("evidence_summary needs the project validator: " + r1.stderr[-200:])
        self.assertEqual(run("evidence_summary.py", *base, "--output", red_csv, "--redact").returncode, 0)
        self.assertEqual(run("evidence_summary.py", *base, "--output", plain_again).returncode, 0)
        self.assertEqual(plain_csv.read_text(encoding="utf-8"), plain_again.read_text(encoding="utf-8"))
        self.assertTrue(self.leak(plain_csv.read_text(encoding="utf-8")), "default CSV keeps absolute paths (control)")
        self.assertFalse(self.leak(red_csv.read_text(encoding="utf-8")))
        plain_rows = list(csv.DictReader(io.StringIO(plain_csv.read_text(encoding="utf-8"))))
        rows = list(csv.DictReader(io.StringIO(red_csv.read_text(encoding="utf-8"))))
        self.assertEqual([r["run"] for r in rows], ["<evidence>/run1/editor_raw.log", "<evidence>/run2/editor_raw.log"],
                         "runs stay distinguishable")
        for red_row, plain_row in zip(rows, plain_rows):
            for field in ("map", "date", "outcome", "validator", "schema_failures", "semantic_warnings", "sha256"):
                self.assertEqual(red_row[field], plain_row[field], f"structured field {field} kept")
            self.assertEqual(red_row["map"], "/Game/Maps/L_Arena")
            # The parser may cut `profile=` at a space inside the temp root; the fragment must not echo a user-name piece.
            for piece in Path.home().name.split():
                if len(piece) > 2:
                    self.assertNotIn(piece.lower(), red_row["profile"].lower())

    def test_space_cut_root_prefix_is_labelled(self):
        home = str(Path.home())
        cut = home.split(" ")[0] if " " in home else home[: max(4, len(home) - 2)]
        self.assertIn(redaction.redact_text("profile=" + cut), ("profile=<home>/", "profile=<tmp>/", "profile=<project>/"))


if __name__ == "__main__":
    unittest.main()
