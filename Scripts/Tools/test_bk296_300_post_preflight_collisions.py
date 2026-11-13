"""BK-296..300 (C, implementer; X-2135): destination collisions raced in AFTER each caller's preflight, as real CLI
subprocesses.

The runpy wrapper replaces atomic_io.atomic_create_text or atomic_create_copy with a hook that, on the Nth call,
writes RACER bytes at that call's destination and then calls the real (exclusive, os.link) function - i.e. another
writer wins the path between the caller's own checks and publication. Throwaway temp dirs only; no project output,
lock, pack, asset, Unreal, build or PIE.
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

RACER = b"RACER-WROTE-THIS-FIRST\n"
WRAPPER = textwrap.dedent("""
    import runpy, sys
    from pathlib import Path
    tools, script, which, nth = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    sys.path.insert(0, tools)
    import atomic_io
    if which != "none":
        real = getattr(atomic_io, which)
        calls = []
        def raced(*args, **kwargs):
            calls.append(1)
            if len(calls) == nth:
                destination = Path(args[0] if which == "atomic_create_text" else args[1])
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(b"RACER-WROTE-THIS-FIRST\\n")
            return real(*args, **kwargs)
        setattr(atomic_io, which, raced)
    sys.argv = [script] + sys.argv[5:]
    runpy.run_path(script, run_name="__main__")
""")


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.wrapper = self.dir / "wrapper.py"
        self.wrapper.write_text(WRAPPER, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def cli(self, script, which, nth, *args):
        return subprocess.run([sys.executable, str(self.wrapper), str(HERE), str(HERE / script), which, str(nth),
                               *map(str, args)], capture_output=True, text=True, timeout=120)

    def tree(self, root):
        return {str(p.relative_to(root)): p.read_bytes() for p in sorted(Path(root).rglob("*")) if p.is_file()}

    def no_temps(self, root):
        self.assertEqual([p for p in Path(root).rglob("*.tmp")], [])


class Bk296O1Callers(Base):
    def test_raced_destination_is_refused_as_existing_and_racer_bytes_survive(self):
        editor = self.dir / "Scripts" / "Editor"
        editor.mkdir(parents=True)
        (editor / "a.py").write_text("x = 1\n", encoding="utf-8")
        for script, word in (("inventory_editor_asset_writers.py", "inventory"), ("audit_editor_save_safety.py", "audit")):
            with self.subTest(script=script):
                out = self.dir / f"{word}.md"
                r = self.cli(script, "atomic_create_text", 1, "--editor", editor, "--output", out)
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertEqual(r.stdout.splitlines()[0], f"REFUSED existing {word} output: {out}")
                self.assertEqual(out.read_bytes(), RACER)                 # the winner is never overwritten
                self.no_temps(self.dir)


class Bk297Scaffold(Base):
    ARGS = ("--name", "RaceProbe", "--requirement-id", "BOSS-TST-297", "--slug", "race")

    def test_collision_on_first_and_later_target(self):
        for nth, survivors in ((1, 0), (2, 1), (3, 2)):
            with self.subTest(nth=nth):
                root = self.dir / f"root{nth}"
                r = self.cli("new_rule_scaffold.py", "atomic_create_text", nth, *self.ARGS, "--output-root", root)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)    # uncaught FileExistsError
                self.assertIn("FileExistsError", r.stderr.strip().splitlines()[-1])
                self.assertNotIn("Scaffold created", r.stdout)
                self.assertEqual(len(r.stdout.strip().splitlines()) if r.stdout.strip() else 0, survivors)
                files = self.tree(root)
                self.assertEqual(len(files), survivors + 1)               # own survivors + the racer's file
                self.assertEqual(sum(v == RACER for v in files.values()), 1)
                self.no_temps(root)
                before = self.tree(root)
                rerun = self.cli("new_rule_scaffold.py", "none", 0, *self.ARGS, "--output-root", root)
                self.assertEqual(rerun.returncode, 2)
                self.assertIn("Refusing to overwrite existing scaffold target(s):", rerun.stderr)
                self.assertEqual(rerun.stderr.count("\n- "), survivors + 1)
                self.assertEqual(self.tree(root), before)                 # BK-299: byte-identical


class Bk298EvidencePack(Base):
    def inputs(self):
        raw, pre, post = self.dir / "raw.log", self.dir / "state.json", self.dir / "after.json"
        raw.write_bytes(b"raw\n" * 50)
        pre.write_bytes(b'{"pre":1}')
        post.write_bytes(b'{"post":2}')
        return raw, pre, post

    def test_collisions_after_root_preflight(self):
        raw, pre, post = self.inputs()
        cases = (("atomic_create_copy", 2, "pre_state.json", ["pre_state.json", "raw.log"]),
                 ("atomic_create_text", 1, "evidence_sha256.txt",
                  ["evidence_sha256.txt", "post_after.json", "pre_state.json", "raw.log"]))
        for which, nth, raced_name, members in cases:
            with self.subTest(which=which, nth=nth):
                out = self.dir / f"pack_{which}"
                r = self.cli("evidence_pack.py", which, nth, raw, out, "--pre-state", pre, "--post-state", post)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn("FileExistsError", r.stderr.strip().splitlines()[-1])
                self.assertEqual(r.stdout, "")                            # no files= completion line
                tree = self.tree(out)
                self.assertEqual(sorted(tree), members)
                self.assertEqual(tree[raced_name], RACER)                 # racer bytes not overwritten
                self.assertNotIn("evidence_manifest.json", tree)
                self.assertTrue(VM.verify(out / "evidence_manifest.json", require_bytes=True, strict_membership=True))
                self.no_temps(out)
                rerun = self.cli("evidence_pack.py", "none", 0, raw, out, "--pre-state", pre, "--post-state", post)
                self.assertEqual(rerun.returncode, 2)
                self.assertIn("output root must be new or empty", rerun.stderr)
                self.assertEqual(self.tree(out), tree)                    # BK-299: byte-identical


if __name__ == "__main__":
    unittest.main()
