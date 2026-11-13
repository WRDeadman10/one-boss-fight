"""BM-16..20 (C, implementer; lane BM batch 4): characterization of KI-165 (make_source_manifest accepts a root without Source/) and
KI-166 (malformed JSON in profile_dump / card_table / validate_baked_cards / plugin_dependencies). Real subprocess runs on throwaway temp
inputs; the tools only read the input and (manifest) write the given output inside the temp dir. BO-03/BO-04 (X-2236) landed the fixes;
these tests now pin the fixed, fail-closed behaviour.
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(script, *args):
    return subprocess.run([sys.executable, str(HERE / script), *map(str, args)], capture_output=True, text=True, timeout=60)


def last_line(text):
    lines = text.strip().splitlines()
    return lines[-1] if lines else ""


class Fixture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.bad = self.dir / "bad.json"
        self.bad.write_text("{not json", encoding="utf-8")
        self.array = self.dir / "array.json"
        self.array.write_text("[1, 2]", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()


class Ki166MalformedJson(Fixture):
    """BO-04 (X-2236): the fix landed. Bad input now fails closed with exit 2, a one-line diagnostic naming the input, no traceback, no stdout."""

    def assert_named_failure(self, r, path):
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertTrue(last_line(r.stderr).startswith("ERROR "), r.stderr)
        self.assertIn(str(path), r.stderr, "the diagnostic names the input file (KI-166)")
        self.assertEqual(r.stdout, "", "no partial output before the failure")

    def test_syntax_error_names_the_input(self):
        for script in ("profile_dump.py", "card_table.py", "validate_baked_cards.py"):
            with self.subTest(script=script):
                r = run(script, self.bad)
                self.assert_named_failure(r, self.bad)
                self.assertIn("malformed JSON", r.stderr)

    def test_wrong_shape_fails_closed_per_tool(self):
        self.assert_named_failure(run("profile_dump.py", self.array), self.array)
        self.assert_named_failure(run("card_table.py", self.array), self.array)
        self.assert_named_failure(run("validate_baked_cards.py", self.array), self.array)

    def test_plugin_dependencies_malformed_uproject(self):
        root = self.dir / "proj"
        root.mkdir()
        bad = root / "Demo.uproject"
        bad.write_text("{bad", encoding="utf-8")
        self.assert_named_failure(run("plugin_dependencies.py", "--root", root), bad.name)

    def test_plugin_dependencies_malformed_uplugin_prints_no_rows(self):
        root = self.dir / "proj2"
        (root / "Plugins" / "P").mkdir(parents=True)
        (root / "Demo.uproject").write_text('{"Plugins": [{"Name": "P", "Enabled": true}]}', encoding="utf-8")
        (root / "Plugins" / "P" / "P.uplugin").write_text("[1]", encoding="utf-8")
        self.assert_named_failure(run("plugin_dependencies.py", "--root", root), "P.uplugin")

    def test_valid_inputs_still_succeed(self):
        good = self.dir / "cards.json"
        good.write_text('{"cards": [{"MoveId": "M", "Windows": [{"BakedSamples": []}]}]}', encoding="utf-8")
        for script in ("card_table.py", "validate_baked_cards.py"):
            with self.subTest(script=script):
                self.assertEqual(run(script, good).returncode, 0)
        prof = self.dir / "profile.json"
        prof.write_text('{"a": {"b": 1}}', encoding="utf-8")
        r = run("profile_dump.py", prof)
        self.assertEqual(r.returncode, 0)
        self.assertIn("a.b	1", r.stdout)


class Ki165RootWithoutSource(Fixture):
    def test_missing_source_directory_is_refused(self):
        """BO-03 (X-2236): the fix landed. No Source/ means exit 2 and no manifest is written."""
        empty_root = self.dir / "not_a_project"
        empty_root.mkdir()
        out = self.dir / "manifest.txt"
        r = run("make_source_manifest.py", out, "--root", empty_root)
        self.assertEqual(r.returncode, 2)
        self.assertIn("no Source directory", r.stderr)
        self.assertFalse(out.exists())

    def test_control_root_with_source_lists_files(self):
        root = self.dir / "proj"
        (root / "Source").mkdir(parents=True)
        (root / "Source" / "a.cpp").write_text("int a;\n", encoding="utf-8")
        out = self.dir / "manifest.txt"
        r = run("make_source_manifest.py", out, "--root", root)
        self.assertEqual(r.returncode, 0)
        self.assertTrue(r.stdout.startswith("files=1 manifest="))
        self.assertIn("Source/a.cpp", out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
