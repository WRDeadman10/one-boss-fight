"""BO-36..38 (C, implementer; scoped in C-1500 under X-2258): JSON input edges for the four KI-166 tools. Synthetic only.

  BO-36  encodings: a UTF-8 BOM is accepted; UTF-16 and invalid bytes fail closed (exit 2, ERROR naming the file).
  BO-37  deep nesting: json.loads RecursionError fails closed; profile_dump prints any structure json
         accepted prints (the parser's own limit is reached before the recursive walk's; pinned).
  BO-38  non-standard constants and duplicate keys: pinned characterization (NaN/Infinity are parsed; duplicate keys
         keep the last value); validate_baked_cards still rejects non-finite sample values.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import profile_dump  # noqa: E402

TOOLS = ("profile_dump", "card_table", "validate_baked_cards")
VALID = '{"cards": [{"MoveId": "M", "Windows": [{"BakedSamples": []}]}]}'


def run(tool, *args):
    return subprocess.run([sys.executable, str(HERE / f"{tool}.py"), *map(str, args)], capture_output=True, text=True, timeout=120)


class Temp(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def put(self, name, data: bytes):
        path = self.dir / name
        path.write_bytes(data)
        return path

    def assert_named_failure(self, r, path):
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertTrue(r.stderr.strip().splitlines()[-1].startswith("ERROR "), r.stderr)
        self.assertIn(str(path.name), r.stderr)
        self.assertEqual(r.stdout, "")


class Bo36Encodings(Temp):
    def test_utf8_bom_is_accepted_by_all_four_tools(self):
        good = self.put("bom.json", b"\xef\xbb\xbf" + VALID.encode())
        for tool in TOOLS:
            with self.subTest(tool=tool):
                self.assertEqual(run(tool, good).returncode, 0)
        root = self.dir / "proj"
        root.mkdir()
        (root / "Demo.uproject").write_bytes(b"\xef\xbb\xbf" + b'{"Plugins": []}')
        r = run("plugin_dependencies", "--root", root)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("project=Demo.uproject", r.stdout)

    def test_bom_does_not_change_parsed_values(self):
        plain = self.put("p.json", b'{"a": {"b": 1}}')
        bom = self.put("b.json", b"\xef\xbb\xbf" + b'{"a": {"b": 1}}')
        self.assertEqual(run("profile_dump", plain).stdout, run("profile_dump", bom).stdout)

    def test_utf16_and_invalid_bytes_fail_closed(self):
        utf16 = self.put("u16.json", VALID.encode("utf-16"))
        invalid = self.put("bad.json", b'{"a": "\xff\xfe\xfa"}')
        for tool in TOOLS:
            for path in (utf16, invalid):
                with self.subTest(tool=tool, file=path.name):
                    r = run(tool, path)
                    self.assert_named_failure(r, path)
                    self.assertIn("cannot read input", r.stderr)


class Bo37DeepNesting(Temp):
    def test_parser_recursion_fails_closed(self):
        deep = self.put("deep.json", b"[" * 200000)
        for tool in TOOLS:
            with self.subTest(tool=tool):
                r = run(tool, deep)
                self.assert_named_failure(r, deep)
                self.assertIn("nesting is too deep", r.stderr)
        root = self.dir / "proj"
        root.mkdir()
        (root / "Demo.uproject").write_bytes(b'{"Plugins": ' + b"[" * 200000 + b"}")
        r = run("plugin_dependencies", "--root", root)
        self.assert_named_failure(r, root / "Demo.uproject")

    def test_profile_dump_prints_deep_but_parseable_structures(self):
        value = 1
        # Pin: json.loads accepts ~995 levels and fails (RecursionError, now a named failure) at ~1000, BEFORE the recursive
        # walk would overflow, so profile_dump's recursive walk handles every structure json.loads can return.
        for _ in range(950):
            value = {"k": value}
        path = self.put("d.json", json.dumps(value).encode())
        r = run("profile_dump", path)
        self.assertEqual(r.returncode, 0, r.stderr[-300:])
        self.assertEqual(r.stdout.splitlines()[1], ".".join(["k"] * 950) + "\t1")

class Bo38ConstantsAndDuplicates(Temp):
    def test_nan_infinity_are_parsed_and_printed(self):
        path = self.put("n.json", b'{"a": NaN, "b": Infinity, "c": -Infinity}')
        r = run("profile_dump", path)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.splitlines()[1:], ["a\tNaN", "b\tInfinity", "c\t-Infinity"])

    def test_duplicate_keys_keep_the_last_value(self):
        path = self.put("dup.json", b'{"a": 1, "a": 2}')
        self.assertEqual(run("profile_dump", path).stdout.splitlines()[1], "a\t2")

    def test_card_table_constants_and_duplicates(self):
        """X-2264: card_table prints parsed non-finite timings as Python floats, and the last duplicate key wins for scalar
        and list fields alike (here a later "Windows" with 1 sample replaces an earlier one with 2)."""
        data = (b'{"cards": [{"MoveId": "A", "MoveId": "B", "CommitSeconds": NaN, "ActiveStartSeconds": Infinity,'
                b' "ActiveEndSeconds": -Infinity, "Windows": [{"BakedSamples": [1, 2]}], "Windows": [{"BakedSamples": [1]}]}]}')
        r = run("card_table", self.put("ct.json", data))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines()[1], "B\t\tnan\tinf\t-inf\t\t1")

    def test_plugin_dependencies_constants_and_duplicates(self):
        """X-2264: through the real .uproject and .uplugin paths, a duplicate "Plugins" or "FriendlyName" key keeps the last
        value. A non-boolean "Enabled": NaN is printed as `nan` and counted as enabled by `bool()`. Pinned quirk: Unreal never
        writes NaN, and the tool's contract is reporting, not validation, so behaviour is unchanged."""
        root = self.dir / "proj"
        (root / "Plugins" / "X").mkdir(parents=True)
        (root / "Demo.uproject").write_bytes(
            b'{"Plugins": [{"Name": "X", "Enabled": false}], "Plugins": [{"Name": "X", "Enabled": NaN}, {"Name": "Y", "Enabled": true}]}')
        (root / "Plugins" / "X" / "X.uplugin").write_bytes(
            b'{"FriendlyName": "Old", "FriendlyName": "New", "Plugins": [{"Name": "Dep", "Name": "Dep2"}], "Version": Infinity}')
        r = run("plugin_dependencies", "--root", root)
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.splitlines()
        self.assertTrue(lines[0].startswith("New\tenabled=nan\tdependencies=Dep2\t"), lines[0])
        self.assertTrue(lines[1].startswith("Y\tenabled=True\tdescriptor=not found"), lines[1])
        self.assertEqual(lines[2], "project=Demo.uproject descriptors=1 enabled_entries=2")

    def test_validate_baked_cards_rejects_non_finite_samples(self):
        data = ('{"cards": [{"MoveId": "M", "Windows": [{"WindowId": "W", "StartSeconds": 0, "EndSeconds": 1, "BakedSamples": ['
                '{"TimeSeconds": 0.1, "BaseCS": [0, 0, 0], "TipCS": [1, 1, 1]},'
                '{"TimeSeconds": NaN, "BaseCS": [0, 0, 0], "TipCS": [1, 1, 1]},'
                '{"TimeSeconds": 0.3, "BaseCS": [Infinity, 0, 0], "TipCS": [1, 1, 1]}]}]}]}')
        r = run("validate_baked_cards", self.put("c.json", data.encode()))
        self.assertEqual(r.returncode, 1)
        self.assertIn("samples=3 issues=2", r.stdout)


if __name__ == "__main__":
    unittest.main()
