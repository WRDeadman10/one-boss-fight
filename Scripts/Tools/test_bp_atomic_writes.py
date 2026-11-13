"""BP-16..19 (C, implementer; Queue BP batch 4) under X-2295: static + in-process tests only (no tool main() or subprocess).

  1. Static: the five converted tools have no direct `write_text`/`write_bytes`/`open(..., "w")` left; the no-overwrite
     report writer uses `atomic_create_text`.
  2. In-process byte equivalence on temp files: atomic_write_text(text) == Path.write_text(text, newline="\\n") for the
     four LF-pinned writers; make_fight_video's _platform_newlines/_write_platform_text == text-mode Path.write_text(text).
  3. atomic_create_text keeps the no-overwrite guarantee the report writer relied on.
Paths touched: a TemporaryDirectory, and the five tools' source files (read and parsed only). make_fight_video is imported
(its import-time safety is proven by cli_static_contract); main() is never called.
"""
import ast
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import atomic_io  # noqa: E402
import cli_static_contract  # noqa: E402
import make_fight_video  # noqa: E402

CONVERTED = ("audit_source_error_token_coverage", "mailbox_decision_digest", "normalize_cook_package_manifest",
             "normalize_encounter_selection_graph", "make_fight_video")
SAMPLES = ["a\nb\n", "no newline", "x\r\ny\n", "unicode é漢\n\n", ""]


def direct_writes(tool):
    found = []
    for node in ast.walk(ast.parse((HERE / f"{tool}.py").read_text(encoding="utf-8"))):
        if isinstance(node, ast.Call):
            name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", None)
            if name in ("write_text", "write_bytes"):
                found.append(f"{name}@{node.lineno}")
            if name == "open":
                modes = node.args[1:2] + [k.value for k in node.keywords if k.arg == "mode"]
                if any(isinstance(m, ast.Constant) and isinstance(m.value, str) and set(m.value) & set("wax+") for m in modes):
                    found.append(f"open(w)@{node.lineno}")
    return found


class StaticConversion(unittest.TestCase):
    def test_no_direct_writes_remain(self):
        for tool in CONVERTED:
            with self.subTest(tool=tool):
                self.assertEqual(direct_writes(tool), [])

    def test_report_writer_keeps_no_overwrite(self):
        source = (HERE / "audit_source_error_token_coverage.py").read_text(encoding="utf-8")
        self.assertIn("atomic_create_text(args.output", source)
        self.assertIn("refusing to overwrite existing report", source)

    def test_still_statically_proven(self):
        for tool in CONVERTED:
            with self.subTest(tool=tool):
                ok, reason = cli_static_contract.analyse(HERE / f"{tool}.py")
                self.assertTrue(ok, reason)


class ByteEquivalence(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_lf_pinned_writers(self):
        for i, text in enumerate(SAMPLES):
            with self.subTest(text=text):
                old, new = self.dir / f"old{i}", self.dir / f"new{i}"
                old.write_text(text, encoding="utf-8", newline="\n")
                atomic_io.atomic_write_text(new, text)
                self.assertEqual(new.read_bytes(), old.read_bytes())

    def test_platform_newline_writers(self):
        for i, text in enumerate(SAMPLES):
            with self.subTest(text=text):
                old, new, helper = self.dir / f"o{i}", self.dir / f"n{i}", self.dir / f"h{i}"
                old.write_text(text, encoding="utf-8")  # the former make_fight_video call shape
                atomic_io.atomic_write_text(new, make_fight_video._platform_newlines(text))
                make_fight_video._write_platform_text(helper, text)
                self.assertEqual(new.read_bytes(), old.read_bytes())
                self.assertEqual(helper.read_bytes(), old.read_bytes())

    def test_create_text_refuses_existing(self):
        target = self.dir / "report.md"
        atomic_io.atomic_create_text(target, "first\n")
        with self.assertRaises(FileExistsError):
            atomic_io.atomic_create_text(target, "second\n")
        self.assertEqual(target.read_bytes(), b"first\n")
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), ["report.md"], "no temp leftovers")


if __name__ == "__main__":
    unittest.main()
