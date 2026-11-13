"""BK-281..285 (C, implementer; X-2128): evidence_pack.py partial-publication states as real CLI runs.

evidence_pack.py runs as a subprocess through a runpy wrapper that counts atomic_io.atomic_create_copy /
atomic_create_text calls and fails the Nth one with OSError (the real function runs for every other call). Inputs
and output roots are synthetic files in a throwaway OS temp dir; no project pack/output, lock, asset, Unreal,
build or PIE.
"""
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify_evidence_manifest as VM  # noqa: E402

WRAPPER = textwrap.dedent("""
    import runpy, sys
    tools, script, which, nth = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    sys.path.insert(0, tools)
    import atomic_io
    real = getattr(atomic_io, which) if which != "none" else None
    calls = []
    def counted(*args, **kwargs):
        calls.append(args)
        if len(calls) == nth:
            raise OSError(f"synthetic {which} failure on call {nth}")
        return real(*args, **kwargs)
    if real is not None:
        setattr(atomic_io, which, counted)
    sys.argv = [script] + sys.argv[5:]
    runpy.run_path(script, run_name="__main__")
""")


class Fixture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.raw = self.dir / "raw.log"
        self.pre = self.dir / "state.json"
        self.post = self.dir / "after.json"
        for path, data in ((self.raw, b"raw-log\n" * 100), (self.pre, b'{"pre":1}'), (self.post, b'{"post":2}')):
            path.write_bytes(data)
        self.out = self.dir / "pack"
        self.wrapper = self.dir / "wrapper.py"
        self.wrapper.write_text(WRAPPER, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def run_pack(self, which="none", nth=0):
        args = [str(self.raw), str(self.out), "--pre-state", str(self.pre), "--post-state", str(self.post)]
        return subprocess.run([sys.executable, str(self.wrapper), str(HERE), str(HERE / "evidence_pack.py"),
                               which, str(nth), *args], capture_output=True, text=True, timeout=120)

    def members(self):
        return sorted(p.name for p in self.out.iterdir()) if self.out.exists() else []

    def assert_partial_state(self, r, survivors, failure_text):
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual(r.stdout, "")                              # no "files=N output=" completion line
        self.assertIn(failure_text, r.stderr)
        self.assertEqual(self.members(), survivors)                 # no manifest, no temp
        self.assertNotIn("evidence_manifest.json", self.members())
        self.assertTrue(VM.verify(self.out / "evidence_manifest.json", require_bytes=True, strict_membership=True),
                        "the verifier must refuse a partial pack")
        for name, source in (("raw.log", self.raw), ("pre_state.json", self.pre)):
            if name in survivors:                                   # survivors are complete, exact copies
                self.assertEqual((self.out / name).read_bytes(), source.read_bytes())


class Bk281ContractFromSource(unittest.TestCase):
    def test_copies_then_hashes_then_manifest_last(self):
        lines = (HERE / "evidence_pack.py").read_text(encoding="utf-8").splitlines()
        copy = next(i for i, l in enumerate(lines) if "atomic_create_copy(source, target)" in l)
        hashes = next(i for i, l in enumerate(lines) if "atomic_create_text(hashes_path" in l)
        manifest = next(i for i, l in enumerate(lines) if "atomic_create_text(manifest_path" in l)
        claim = next(i for i, l in enumerate(lines) if 'print(f"files=' in l)
        self.assertLess(copy, hashes)
        self.assertLess(hashes, manifest)
        self.assertLess(manifest, claim)


class Bk282SecondCopyFails(Fixture):
    def test_second_copy_failure(self):
        r = self.run_pack("atomic_create_copy", 2)
        self.assert_partial_state(r, ["raw.log"], "OSError: synthetic atomic_create_copy failure on call 2")


class Bk283HashFileFails(Fixture):
    def test_hash_file_failure_after_all_copies(self):
        r = self.run_pack("atomic_create_text", 1)  # call 1 = evidence_sha256.txt, call 2 = manifest
        self.assert_partial_state(r, ["post_after.json", "pre_state.json", "raw.log"],
                                  "OSError: synthetic atomic_create_text failure on call 1")

    def test_manifest_failure_after_hash_file(self):
        r = self.run_pack("atomic_create_text", 2)
        self.assert_partial_state(r, ["evidence_sha256.txt", "post_after.json", "pre_state.json", "raw.log"],
                                  "OSError: synthetic atomic_create_text failure on call 2")


class Bk284RerunPartialOutput(Fixture):
    def test_rerun_refuses_without_overwrite_or_completion_claim(self):
        for which, nth in (("atomic_create_copy", 2), ("atomic_create_text", 1), ("atomic_create_text", 2)):
            with self.subTest(which=which, nth=nth):
                for p in self.out.glob("*") if self.out.exists() else ():
                    p.unlink()
                self.run_pack(which, nth)
                before = {p.name: p.read_bytes() for p in self.out.iterdir()}
                r = self.run_pack()                                  # clean rerun, no injection
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)  # argparse error
                self.assertIn("output root must be new or empty", r.stderr)
                self.assertEqual(r.stdout, "")
                self.assertEqual({p.name: p.read_bytes() for p in self.out.iterdir()}, before)
                self.assertNotIn("evidence_manifest.json", before)

    def test_clean_run_into_a_fresh_root_completes(self):
        r = self.run_pack()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), f"files=3 output={self.out.resolve()}")
        self.assertEqual(VM.verify(self.out / "evidence_manifest.json", require_bytes=True, strict_membership=True), [])


if __name__ == "__main__":
    unittest.main()
