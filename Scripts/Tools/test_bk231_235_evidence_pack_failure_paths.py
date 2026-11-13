"""BK-231..235 (C, implementer; X-2079/X-2080/X-2082): failure-injection and compatibility regressions for the lead's
evidence_pack.py hotfix (P1 source/copy integrity, P2 new-or-empty output root, P3 normcase preflight).

Every publication step is failed in turn (copy, copy corruption, hash file, manifest) and the outcome must be safe:
no overwrite, and NO manifest - so verify() can never PASS a partial pack. Throwaway OS temp fixtures only; no project
evidence pack, Unreal, build or PIE.
"""
import contextlib
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
    err = io.StringIO()
    with mock.patch.object(sys, "argv", ["evidence_pack.py"] + [str(a) for a in argv]), contextlib.redirect_stderr(err), \
            contextlib.redirect_stdout(io.StringIO()):
        try:
            return EP.main(), err.getvalue()
        except SystemExit as exit_:
            return exit_.code, err.getvalue()


class Fixture:
    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "src").mkdir()
        self.out = self.root / "pack"
        return self

    def __exit__(self, *exc):
        self.tmp.cleanup()

    def file(self, name, data):
        path = self.root / "src" / name
        path.write_bytes(data)
        return path

    def three(self):
        return [self.file("run.log", RAW), self.out, "--pre-state", self.file("a.json", PRE),
                "--post-state", self.file("b.json", POST)]

    def no_false_pass(self, test):
        manifest = self.out / "evidence_manifest.json"
        test.assertFalse(manifest.exists(), "a failed run must not publish the commit-marker manifest")
        test.assertTrue(VM.verify(manifest), "verify() must refuse a pack without a manifest")


class ValidPacksUnchanged(unittest.TestCase):
    def test_new_and_empty_existing_output_roots_still_work(self):
        for precreate in (False, True):
            with self.subTest(precreate=precreate), Fixture() as f:
                if precreate:
                    f.out.mkdir()
                code, _ = run(f.three())
                self.assertEqual(code, 0)
                manifest = f.out / "evidence_manifest.json"
                self.assertEqual(VM.verify(manifest, require_bytes=True, strict_membership=True), [])
                data = json.loads(manifest.read_text(encoding="utf-8"))
                self.assertEqual([e["file"] for e in data["files"]], ["run.log", "pre_a.json", "post_b.json"])


class FailureInjection(unittest.TestCase):
    def test_copy_failure_on_second_file(self):
        with Fixture() as f:
            real, calls = EP.atomic_create_copy, []

            def fail_second(source, target):
                calls.append(target)
                if len(calls) == 2:
                    raise OSError("synthetic copy failure")
                return real(source, target)

            with mock.patch.object(EP, "atomic_create_copy", fail_second), self.assertRaises(OSError):
                run(f.three())
            f.no_false_pass(self)
            self.assertFalse((f.out / "evidence_sha256.txt").exists())

    def test_corrupted_copy_is_refused_before_any_hash_or_manifest(self):
        """P1: the published copy differs from its source -> exit 2, no hash file, no manifest."""
        with Fixture() as f:
            with mock.patch.object(EP, "atomic_create_copy", lambda s, t: Path(t).write_bytes(b"corrupt")):
                code, err = run(f.three())
            self.assertEqual(code, 2)
            self.assertIn("published copy does not match source", err)
            self.assertFalse((f.out / "evidence_sha256.txt").exists())
            f.no_false_pass(self)

    def test_same_size_corruption_is_caught_by_hash(self):
        with Fixture() as f:
            raw = f.file("run.log", RAW)
            with mock.patch.object(EP, "atomic_create_copy", lambda s, t: Path(t).write_bytes(b"X" * len(RAW))):
                code, _ = run([raw, f.out])
            self.assertEqual(code, 2)
            f.no_false_pass(self)

    def test_hash_file_or_manifest_publication_failure(self):
        for failing in ("evidence_sha256.txt", "evidence_manifest.json"):
            with self.subTest(failing=failing), Fixture() as f:
                real = EP.atomic_create_text

                def fail_on(path, text, *a, _name=failing, **k):
                    if Path(path).name == _name:
                        raise OSError("synthetic publish failure: " + _name)
                    return real(path, text, *a, **k)

                with mock.patch.object(EP, "atomic_create_text", fail_on), self.assertRaises(OSError):
                    run(f.three())
                f.no_false_pass(self)


class OutputRootAndPreflight(unittest.TestCase):
    def test_p2_non_empty_output_root_is_refused_before_any_write(self):
        with Fixture() as f:
            f.out.mkdir()
            (f.out / "unrelated.txt").write_bytes(b"old")
            code, err = run(f.three())
            self.assertEqual(code, 2)
            self.assertIn("output root must be new or empty", err)
            self.assertEqual(sorted(p.name for p in f.out.iterdir()), ["unrelated.txt"])

    def test_output_root_that_is_a_file_is_refused(self):
        with Fixture() as f:
            f.out.write_bytes(b"not a dir")
            code, err = run([f.file("run.log", RAW), f.out])
            self.assertEqual(code, 2)
            self.assertIn("not a directory", err)

    @unittest.skipUnless(os.name == "nt", "case-insensitive filesystem")
    def test_p3_windows_case_variants_are_refused_before_any_write(self):
        cases = (
            (["EVIDENCE_MANIFEST.JSON"], []),                      # reserved-name alias (X-2077 reproduction)
            (["Evidence_Sha256.TXT"], []),                         # the other reserved name
            (["Pre_x.log"], [("--pre-state", "x.log")]),          # raw vs pre destination alias
        )
        for raw_names, extras in cases:
            with self.subTest(raw=raw_names, extras=extras), Fixture() as f:
                argv = [f.file(raw_names[0], RAW), f.out]
                for flag, name in extras:
                    argv += [flag, f.file(name, PRE)]
                code, err = run(argv)
                self.assertEqual(code, 2, err)
                self.assertIn("collide", err)
                self.assertTrue(not f.out.exists() or list(f.out.iterdir()) == [])


class ProducerVerifierParity(unittest.TestCase):
    def test_every_produced_entry_matches_the_verifier_contract(self):
        with Fixture() as f:
            self.assertEqual(run(f.three())[0], 0)
            data = json.loads((f.out / "evidence_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(set(data), VM.TOP_LEVEL_KEYS)
            for entry in data["files"]:
                self.assertTrue(set(entry) <= VM.ENTRY_ALLOWED_KEYS and VM.ENTRY_REQUIRED_KEYS <= set(entry))
                self.assertIsInstance(entry["label"], str)
                self.assertRegex(entry["sha256"], r"^[0-9a-f]{64}$")
                self.assertIs(type(entry["bytes"]), int)


if __name__ == "__main__":
    unittest.main()
