"""BK-226..230 (C, implementer; X-2072): source audit and temp-fixture regressions for evidence_pack.py.

No project evidence pack is read, created or overwritten. No Unreal/build/PIE.
"""
import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import evidence_pack as EP  # noqa: E402
import verify_evidence_manifest as VM  # noqa: E402

RAW, PRE, POST = b"raw log\n", b"pre state\n", b"post state\n"


def run(argv):
    """Run evidence_pack.main() with argv; return (exit_code, stderr)."""
    err = io.StringIO()
    with mock.patch.object(sys, "argv", ["evidence_pack.py"] + [str(a) for a in argv]), contextlib.redirect_stderr(err), \
            contextlib.redirect_stdout(io.StringIO()):
        try:
            code = EP.main()
        except SystemExit as exit_:
            code = exit_.code
    return code, err.getvalue()


class Fixture:
    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.src = self.root / "src"
        self.src.mkdir()
        self.out = self.root / "pack"
        return self

    def __exit__(self, *exc):
        self.tmp.cleanup()

    def file(self, name, data):
        path = self.src / name
        path.write_bytes(data)
        return path


class Bk226InputsAndSelection(unittest.TestCase):
    def test_missing_sources_exit_2_and_write_nothing(self):
        with Fixture() as f:
            code, err = run([f.src / "absent.log", f.out])
            self.assertEqual(code, 2)
            self.assertIn("must exist", err)
            self.assertFalse(f.out.exists())

    def test_destination_collisions_are_refused_before_any_copy(self):
        with Fixture() as f:
            raw = f.file("pre_x.log", RAW)            # raw keeps its name -> pre_x.log
            pre = f.file("x.log", PRE)                # pre -> pre_x.log: collision
            code, err = run([raw, f.out, "--pre-state", pre])
            self.assertEqual(code, 2)
            self.assertIn("collide", err)
            self.assertFalse(f.out.exists(), "BO-02 / KI-164: a rejected run creates no output directory")

    def test_reserved_names_are_refused(self):
        with Fixture() as f:
            code, err = run([f.file("evidence_manifest.json", RAW), f.out])
            self.assertEqual(code, 2)


class Bk227OutputConfinement(unittest.TestCase):
    def test_existing_destination_is_never_overwritten(self):
        with Fixture() as f:
            raw = f.file("run.log", RAW)
            f.out.mkdir()
            (f.out / "run.log").write_bytes(b"keep")
            code, err = run([raw, f.out])
            self.assertEqual(code, 2)
            self.assertIn("output root must be new or empty", err)
            self.assertEqual((f.out / "run.log").read_bytes(), b"keep")

    def test_existing_manifest_is_never_overwritten(self):
        with Fixture() as f:
            f.out.mkdir()
            (f.out / "evidence_manifest.json").write_text("{}", encoding="utf-8")
            code, _ = run([f.file("run.log", RAW), f.out])
            self.assertEqual(code, 2)
            self.assertEqual((f.out / "evidence_manifest.json").read_text(encoding="utf-8"), "{}")

    def test_symlinked_destination_is_refused(self):
        with Fixture() as f:
            raw = f.file("run.log", RAW)
            f.out.mkdir()
            try:
                os.symlink(f.root / "elsewhere.log", f.out / "run.log")
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable on this host")
            code, _ = run([raw, f.out])
            self.assertEqual(code, 2)


class Bk228IntegrityAndCleanup(unittest.TestCase):
    def test_hashes_and_bytes_match_the_published_copies(self):
        with Fixture() as f:
            code, _ = run([f.file("run.log", RAW), f.out, "--pre-state", f.file("a.json", PRE),
                           "--post-state", f.file("b.json", POST)])
            self.assertEqual(code, 0)
            data = json.loads((f.out / "evidence_manifest.json").read_text(encoding="utf-8"))
            for entry in data["files"]:
                payload = (f.out / entry["file"]).read_bytes()
                self.assertEqual((entry["bytes"], entry["sha256"]), (len(payload), hashlib.sha256(payload).hexdigest()))
            lines = (f.out / "evidence_sha256.txt").read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines, ["%s  %s" % (e["sha256"], e["file"]) for e in data["files"]])

    def test_manifest_is_the_commit_marker(self):
        """A failure while publishing leaves no manifest (by design :91-92), so verify() refuses the partial pack."""
        with Fixture() as f:
            raw = f.file("run.log", RAW)
            real = EP.atomic_create_text

            def fail_on_manifest(path, text, *a, **k):
                if Path(path).name == "evidence_manifest.json":
                    raise OSError("synthetic manifest publish failure")
                return real(path, text, *a, **k)

            with mock.patch.object(EP, "atomic_create_text", fail_on_manifest):
                with self.assertRaises(OSError):
                    run([raw, f.out])
            self.assertFalse((f.out / "evidence_manifest.json").exists())
            self.assertTrue(VM.verify(f.out / "evidence_manifest.json"))

    def test_gap_p1_copy_is_not_compared_with_its_source(self):
        """P1 (BK-228, :63-65): the manifest hashes the PUBLISHED copy only; nothing compares it with the source, so a
        copy that differs from its source (bad disk, concurrent writer, faulty copy) is recorded and exits 0. Rule:
        hash the source before copying and refuse (exit non-zero, no manifest) when source and copy hashes differ."""
        with Fixture() as f:
            raw = f.file("run.log", RAW)

            def corrupt_copy(source, target):
                Path(target).write_bytes(b"not the source")

            with mock.patch.object(EP, "atomic_create_copy", corrupt_copy):
                code, _ = run([raw, f.out])
            self.assertNotEqual(code, 0)
            self.assertFalse((f.out / "evidence_manifest.json").exists())


class Bk229SchemaAndCompatibility(unittest.TestCase):
    def test_schema_order_labels_and_verifier_round_trip(self):
        with Fixture() as f:
            code, _ = run([f.file("run.log", RAW), f.out, "--pre-state", f.file("a.json", PRE),
                           "--post-state", f.file("b.json", POST)])
            self.assertEqual(code, 0)
            data = json.loads((f.out / "evidence_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(sorted(data), ["files", "schema"])
            self.assertEqual(data["schema"], 1)
            self.assertEqual([(e["label"], e["file"]) for e in data["files"]],
                             [("raw", "run.log"), ("pre", "pre_a.json"), ("post", "post_b.json")])
            self.assertTrue(all(set(e) == {"label", "file", "bytes", "sha256"} for e in data["files"]))
            self.assertEqual(VM.verify(f.out / "evidence_manifest.json", require_bytes=True, strict_membership=True), [])


class Bk227Gaps(unittest.TestCase):
    def test_gap_p2_output_root_must_be_new_or_empty(self):
        """P2 (BK-227, :40-41): `out.mkdir(exist_ok=True)` publishes into an existing, non-empty folder; unrelated
        files then sit next to the pack and fail verify(strict_membership=True) later. Rule: require the output root
        to be new or empty (or at least list pre-existing members), refusing before any copy."""
        with Fixture() as f:
            f.out.mkdir()
            (f.out / "unrelated.txt").write_bytes(b"old")
            code, _ = run([f.file("run.log", RAW), f.out])
            self.assertNotEqual(code, 0)
            self.assertEqual(sorted(p.name for p in f.out.iterdir()), ["unrelated.txt"])

    @unittest.skipUnless(os.name == "nt", "case-insensitive filesystem collision")
    def test_gap_p3_case_variant_collisions_are_caught_before_copying(self):
        """P3 (BK-226, :44-55, Windows): collision and reserved-name checks compare exact strings, so `Pre_x.log`
        (raw) and `pre_x.log` (pre) - or a raw file named `EVIDENCE_MANIFEST.JSON` - pass planning and then fail at
        publish time (os.link FileExistsError, exit 1, traceback) AFTER earlier copies were published. Rule: compare
        os.path.normcase names (including the reserved set) during planning and exit 2 before any copy."""
        with Fixture() as f:
            raw = f.file("Pre_x.log", RAW)
            pre = f.file("x.log", PRE)
            try:
                code, _ = run([raw, f.out, "--pre-state", pre])
            except OSError:
                code = "raised"
            self.assertEqual(code, 2)
            self.assertFalse(f.out.exists(), "BO-02 / KI-164: a rejected run creates no output directory")

        with Fixture() as f:
            code, _ = run([f.file("EVIDENCE_MANIFEST.JSON", RAW), f.out])
            self.assertEqual(code, 2)
            self.assertFalse(f.out.exists(), "BO-02 / KI-164: a rejected run creates no output directory")


class Bk230Cli(unittest.TestCase):
    def test_success_exit_0_and_argparse_errors_exit_2(self):
        with Fixture() as f:
            self.assertEqual(run([f.file("run.log", RAW), f.out])[0], 0)
            self.assertEqual(run([])[0], 2)


if __name__ == "__main__":
    unittest.main()
