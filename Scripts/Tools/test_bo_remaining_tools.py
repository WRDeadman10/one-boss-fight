"""BO-41..44 (C, implementer; scope C-1504 under X-2267): the lane tools outside the KI-167 set. Synthetic only.

  BO-41  `python -m Scripts.Tools.<tool>` works for evidence_pack and make_source_manifest (fixed import order) and the
         four KI-166 JSON tools, with the same exit code and stdout as a direct script run.
  BO-42  --help and no-argument smoke across all 13 lane tools in both invocation styles: help exits 0, a usage error
         exits 2, never a traceback.
  BO-43  make_source_manifest boundaries: Source as a file, an empty Source, nested/hidden files, a relative --root, an
         output inside Source.
  BO-44  evidence_pack preflight (KI-164): output root that is a file, a non-empty folder or relative; missing state
         files; the same file as raw and pre-state. Every rejection exits 2 and creates no folder.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

LANE_TOOLS = ("token_coverage", "evidence_pack", "make_source_manifest", "profile_dump", "card_table",
              "validate_baked_cards", "plugin_dependencies", "proof_report", "asset_provenance", "evidence_summary",
              "suite_log_report", "summarize_framework_log", "plot_framework_timeline")
# Tools that accept a no-argument run (no required positional), and the exit code they then return.
NO_ARG_OK = {"token_coverage", "plugin_dependencies"}


def script(tool, *args, cwd=None):
    return subprocess.run([sys.executable, str(HERE / f"{tool}.py"), *map(str, args)], capture_output=True, text=True,
                          timeout=180, cwd=cwd)


def module(tool, *args):
    return subprocess.run([sys.executable, "-m", f"Scripts.Tools.{tool}", *map(str, args)], capture_output=True, text=True,
                          timeout=180, cwd=REPO)


class Temp(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name).resolve()

    def tearDown(self):
        self._tmp.cleanup()


class Bo41ModuleInvocation(Temp):
    def test_module_matches_script(self):
        raw = self.dir / "r.log"
        raw.write_text("raw\n", encoding="utf-8")
        proj = self.dir / "proj"
        (proj / "Source").mkdir(parents=True)
        (proj / "Source" / "a.cpp").write_text("int a;\n", encoding="utf-8")
        (proj / "Demo.uproject").write_text('{"Plugins": []}', encoding="utf-8")
        good = self.dir / "c.json"
        good.write_text('{"cards": [{"MoveId": "M", "Windows": []}]}', encoding="utf-8")
        cases = {
            "evidence_pack": lambda tag: (raw, self.dir / f"pack_{tag}"),
            "make_source_manifest": lambda tag: (self.dir / f"m_{tag}.txt", "--root", proj),
            "profile_dump": lambda tag: (good,), "card_table": lambda tag: (good,),
            "validate_baked_cards": lambda tag: (good,), "plugin_dependencies": lambda tag: ("--root", proj),
        }
        for tool, args in cases.items():
            with self.subTest(tool=tool):
                a, m = script(tool, *args("s"), cwd=REPO), module(tool, *args("m"))
                self.assertNotIn("ModuleNotFoundError", m.stderr, m.stderr[-300:])
                self.assertEqual((a.returncode, m.returncode), (0, 0), a.stderr + m.stderr)
                norm = lambda text: text.replace("pack_s", "X").replace("pack_m", "X").replace("m_s.txt", "X").replace("m_m.txt", "X")
                self.assertEqual(norm(a.stdout), norm(m.stdout))


class Bo42HelpAndUsageSmoke(unittest.TestCase):
    def test_help_and_no_args_all_tools_both_styles(self):
        for tool in LANE_TOOLS:
            for style, runner in (("script", lambda *a: script(tool, *a, cwd=REPO)), ("module", lambda *a: module(tool, *a))):
                with self.subTest(tool=tool, style=style):
                    h = runner("--help")
                    self.assertEqual(h.returncode, 0, h.stderr[-300:])
                    self.assertIn("usage:", h.stdout)
                    self.assertNotIn("Traceback", h.stderr)
                    if tool in NO_ARG_OK:
                        continue
                    n = runner()
                    self.assertEqual(n.returncode, 2, n.stderr[-300:])
                    self.assertIn("usage:", n.stderr)
                    self.assertNotIn("Traceback", n.stderr)


class Bo43SourceManifestBoundaries(Temp):
    def run_manifest(self, *args, cwd=None):
        return script("make_source_manifest", *args, cwd=cwd)

    def test_source_as_file_is_refused(self):
        (self.dir / "Source").write_text("x", encoding="utf-8")
        out = self.dir / "m.txt"
        r = self.run_manifest(out, "--root", self.dir)
        self.assertEqual(r.returncode, 2)
        self.assertIn("no Source directory", r.stderr)
        self.assertFalse(out.exists())

    def test_empty_source_directory_is_a_valid_empty_manifest(self):
        """Pinned: KI-165 requires that Source exists; an existing but empty Source gives files=0, exit 0 and an empty manifest."""
        (self.dir / "Source").mkdir()
        out = self.dir / "m.txt"
        r = self.run_manifest(out, "--root", self.dir)
        self.assertEqual(r.returncode, 0)
        self.assertTrue(r.stdout.startswith("files=0 "))
        self.assertEqual(out.read_bytes(), b"")

    def test_nested_hidden_files_sorted_relative_root(self):
        src = self.dir / "Source"
        (src / "b" / ".hidden").mkdir(parents=True)
        (src / "b" / ".hidden" / "h.cpp").write_text("h", encoding="utf-8")
        (src / "a.cpp").write_text("a", encoding="utf-8")
        (src / "b" / "c.h").write_text("c", encoding="utf-8")
        r = self.run_manifest("m.txt", "--root", ".", cwd=self.dir)
        self.assertEqual(r.returncode, 0, r.stderr)
        rows = [line.split("  ", 1)[1] for line in (self.dir / "m.txt").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(rows, ["Source/a.cpp", "Source/b/.hidden/h.cpp", "Source/b/c.h"], "sorted, POSIX, hidden included")

    def test_output_inside_source_is_refused(self):
        (self.dir / "Source").mkdir()
        (self.dir / "Source" / "a.cpp").write_text("a", encoding="utf-8")
        out = self.dir / "Source" / "manifest.txt"
        r = self.run_manifest(out, "--root", self.dir)
        self.assertEqual(r.returncode, 2)
        self.assertIn("outside the scanned Source directory", r.stderr)
        self.assertFalse(out.exists())


class Bo44EvidencePackPreflight(Temp):
    def setUp(self):
        super().setUp()
        self.raw = self.dir / "r.log"
        self.raw.write_text("raw\n", encoding="utf-8")

    def assert_rejected(self, r, out, text):
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn(text, r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_output_root_is_a_file(self):
        blocker = self.dir / "blk"
        blocker.write_text("f", encoding="utf-8")
        self.assert_rejected(script("evidence_pack", self.raw, blocker), blocker, "not a directory")
        self.assertEqual(blocker.read_text(encoding="utf-8"), "f", "the file is untouched")

    def test_output_root_non_empty(self):
        out = self.dir / "ne"
        out.mkdir()
        (out / "z").write_text("z", encoding="utf-8")
        self.assert_rejected(script("evidence_pack", self.raw, out), out, "new or empty")
        self.assertEqual(sorted(p.name for p in out.iterdir()), ["z"])

    def test_missing_state_file_creates_nothing(self):
        out = self.dir / "o"
        self.assert_rejected(script("evidence_pack", self.raw, out, "--pre-state", self.dir / "missing.txt"), out, "must exist")
        self.assertFalse(out.exists())
        self.assert_rejected(script("evidence_pack", self.dir / "missing.log", out), out, "must exist")
        self.assertFalse(out.exists())

    def test_relative_output_root(self):
        r = script("evidence_pack", "r.log", "rel_out", cwd=self.dir)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(sorted(p.name for p in (self.dir / "rel_out").iterdir()),
                         ["evidence_manifest.json", "evidence_sha256.txt", "r.log"])

    def test_same_file_as_raw_and_pre_state_is_pinned(self):
        """Pinned: one file given as both raw log and pre-state is copied twice under distinct names (r.log, pre_r.log)."""
        out = self.dir / "o2"
        r = script("evidence_pack", self.raw, out, "--pre-state", self.raw)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(sorted(p.name for p in out.iterdir()),
                         ["evidence_manifest.json", "evidence_sha256.txt", "pre_r.log", "r.log"])


if __name__ == "__main__":
    unittest.main()
