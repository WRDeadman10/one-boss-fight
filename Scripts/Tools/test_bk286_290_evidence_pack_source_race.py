"""BK-286..290 (C, implementer; X-2130): evidence_pack.py source-identity race boundary as real CLI runs.

The runpy wrapper replaces atomic_io.atomic_create_copy with a hook that, for the selected source only, mutates or
removes the source and then calls the real copy. evidence_pack.py hashes each source (file_identity) immediately
before atomic_create_copy, so the hook fires exactly between the initial source hash and the copy. Synthetic
temp-only data; no real pack/output, lock, asset, Unreal, build or PIE.
"""
import os
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
    import os, runpy, sys
    from pathlib import Path
    tools, script, action, victim = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    sys.path.insert(0, tools)
    import atomic_io
    real_copy = atomic_io.atomic_create_copy
    def hooked(source, target):
        if action != "none" and Path(source).name == victim:
            if action == "grow":
                Path(source).write_bytes(Path(source).read_bytes() + b"APPENDED-AFTER-HASH")
            elif action == "same_size":
                data = bytearray(Path(source).read_bytes()); data[0] ^= 0xFF; Path(source).write_bytes(bytes(data))
            elif action == "remove":
                os.remove(source)
        return real_copy(source, target)
    atomic_io.atomic_create_copy = hooked
    sys.argv = [script] + sys.argv[5:]
    runpy.run_path(script, run_name="__main__")
""")


class Fixture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.src = self.dir / "src"
        self.src.mkdir()
        self.raw, self.pre, self.post = self.src / "raw.log", self.src / "state.json", self.src / "after.json"
        self.original = {self.raw: b"raw-log\n" * 100, self.pre: b'{"pre":1}', self.post: b'{"post":2}'}
        for path, data in self.original.items():
            path.write_bytes(data)
        self.out = self.dir / "pack"
        self.wrapper = self.dir / "wrapper.py"
        self.wrapper.write_text(WRAPPER, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def run_pack(self, action="none", victim=""):
        args = [str(self.raw), str(self.out), "--pre-state", str(self.pre), "--post-state", str(self.post)]
        return subprocess.run([sys.executable, str(self.wrapper), str(HERE), str(HERE / "evidence_pack.py"),
                               action, victim, *args], capture_output=True, text=True, timeout=120)

    def members(self):
        return {p.name: p.read_bytes() for p in self.out.iterdir()} if self.out.exists() else {}

    def assert_no_commit(self):
        names = set(self.members())
        self.assertNotIn("evidence_manifest.json", names)
        self.assertNotIn("evidence_sha256.txt", names)
        self.assertTrue(VM.verify(self.out / "evidence_manifest.json", require_bytes=True, strict_membership=True))
        self.assertEqual([n for n in os.listdir(self.out) if n.endswith(".tmp")], [])


class Bk286OrderFromSource(unittest.TestCase):
    def test_hash_copy_rehash_order(self):
        lines = (HERE / "evidence_pack.py").read_text(encoding="utf-8").splitlines()
        first_hash = next(i for i, l in enumerate(lines) if "source_size, source_hash = file_identity(source)" in l)
        copy = next(i for i, l in enumerate(lines) if "atomic_create_copy(source, target)" in l)
        rehash = next(i for i, l in enumerate(lines) if "copied_size, copied_hash = file_identity(target)" in l)
        compare = next(i for i, l in enumerate(lines) if "copied_hash != source_hash" in l)
        self.assertEqual((first_hash + 1, copy + 1, rehash + 1), (copy, rehash, compare))  # adjacent, in order


class Bk287SourceMutatedAfterHash(Fixture):
    def test_mutation_is_refused_before_hash_file_and_manifest(self):
        for action in ("grow", "same_size"):
            with self.subTest(action=action):
                for p in self.out.glob("*") if self.out.exists() else ():
                    p.unlink()
                self.raw.write_bytes(self.original[self.raw])
                r = self.run_pack(action, "raw.log")
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)           # parser.error
                self.assertIn("published copy does not match source", r.stderr)
                self.assertEqual(r.stdout, "")
                members = self.members()
                self.assertEqual(sorted(members), ["raw.log"])                   # the mismatched copy stays
                self.assertEqual(members["raw.log"], self.raw.read_bytes())      # = the MUTATED source bytes
                self.assertNotEqual(members["raw.log"], self.original[self.raw])
                self.assert_no_commit()


class Bk288SourceRemovedAfterHash(Fixture):
    def test_removed_source_traceback_and_partial_members(self):
        r = self.run_pack("remove", "state.json")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)                   # uncaught -> traceback
        self.assertIn("Traceback (most recent call last)", r.stderr)
        self.assertIn("FileNotFoundError", r.stderr)
        self.assertIn("state.json", r.stderr.splitlines()[-1])
        self.assertEqual(r.stdout, "")
        members = self.members()
        self.assertEqual(sorted(members), ["raw.log"])                           # raw published before pre
        self.assertEqual(members["raw.log"], self.original[self.raw])
        self.assert_no_commit()


class Bk289RerunAfterRace(Fixture):
    def test_rerun_refuses_and_survivors_unchanged(self):
        for action, victim, expected in (("grow", "raw.log", 2), ("remove", "state.json", 1)):
            with self.subTest(action=action):
                for p in self.out.glob("*") if self.out.exists() else ():
                    p.unlink()
                for path, data in self.original.items():
                    path.write_bytes(data)
                self.assertEqual(self.run_pack(action, victim).returncode, expected)
                for path, data in self.original.items():                        # restore inputs for the rerun
                    path.write_bytes(data)
                before = self.members()
                r = self.run_pack()
                self.assertEqual(r.returncode, 2)
                self.assertIn("output root must be new or empty", r.stderr)
                self.assertEqual(r.stdout, "")
                self.assertEqual(self.members(), before)
                self.assert_no_commit()

    def test_control_clean_run(self):
        r = self.run_pack()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(VM.verify(self.out / "evidence_manifest.json", require_bytes=True, strict_membership=True), [])


if __name__ == "__main__":
    unittest.main()
