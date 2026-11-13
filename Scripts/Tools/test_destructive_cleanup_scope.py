"""BM-11..15 (C, implementer; lane BM batch 3; KI-158..162): static characterization of the destructive cleanup in the five image/kit tools.

Nothing is executed: the scripts would delete real files in shared folders. Instead each test pins the CURRENT delete scope from source,
so any widening (a new delete call, a recursive delete, a new target) fails here and must be reviewed. Narrowing the scope is owner-gated
(OWNER_DECISIONS_PENDING KI-158-KI-162); these tests intentionally describe today's behaviour, not a fix.
"""
import ast
import re
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
STITCH = {  # script -> (os.remove line, frame-name pattern built from anim_dir)
    "stitch_contact_sheets.py": 50,
    "stitch_g2_g3_sheets.py": 46,
    "stitch_topdown_sheet.py": 54,
    "stitch_two_row_sheets.py": 65,
}
DELETE_NAMES = {"remove", "unlink", "rmtree", "rmdir", "removedirs"}


def delete_calls(tree):
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else func.id if isinstance(func, ast.Name) else ""
            if name in DELETE_NAMES:
                out.append((node.lineno, ast.unparse(func), ast.unparse(node.args[0]) if node.args else ""))
    return out


class StitchToolsDeleteScope(unittest.TestCase):
    def test_each_stitch_tool_has_exactly_one_non_recursive_delete(self):
        for name, line in STITCH.items():
            with self.subTest(script=name):
                calls = delete_calls(ast.parse((SCRIPTS / name).read_text(encoding="utf-8")))
                self.assertEqual(len(calls), 1, calls)
                lineno, func, arg = calls[0]
                self.assertEqual(func, "os.remove")      # single-file delete, never rmtree/rmdir
                self.assertEqual(lineno, line)
                self.assertIn(arg, ("frame_path", "f_path"))

    def test_deleted_files_are_frames_joined_onto_anim_dir(self):
        for name in STITCH:
            with self.subTest(script=name):
                source = (SCRIPTS / name).read_text(encoding="utf-8")
                self.assertRegex(source, r"(frame_path|f_path)\s*=\s*os\.path\.join\(anim_dir,")

    def test_no_stitch_tool_imports_shutil(self):
        for name in STITCH:
            with self.subTest(script=name):
                self.assertNotIn("shutil", (SCRIPTS / name).read_text(encoding="utf-8"))


class BenchKitDeleteScope(unittest.TestCase):
    def setUp(self):
        self.lines = (SCRIPTS / "MakeBenchKit.ps1").read_text(encoding="utf-8-sig").splitlines()

    def test_exactly_two_remove_item_calls(self):
        removes = [(i + 1, l.strip()) for i, l in enumerate(self.lines) if "Remove-Item" in l]
        self.assertEqual([n for n, _ in removes], [23, 76], removes)

    def test_recursive_delete_targets_only_the_kit_folder_under_outdir(self):
        self.assertIn("$Kit = Join-Path $OutDir 'OneBossFight_BenchKit'", self.lines[21])
        self.assertEqual(self.lines[22].strip(), "if (Test-Path $Kit) { Remove-Item $Kit -Recurse -Force }")

    def test_zip_delete_is_single_file_under_outdir(self):
        self.assertIn("$z = Join-Path $OutDir 'OneBossFight_BenchKit.zip'", self.lines[72])
        self.assertEqual(self.lines[75].strip(), "if (Test-Path $z) { Remove-Item $z -Force }")
        self.assertNotIn("-Recurse", self.lines[75])


if __name__ == "__main__":
    unittest.main()
