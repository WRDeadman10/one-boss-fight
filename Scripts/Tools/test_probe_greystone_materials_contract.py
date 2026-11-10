#!/usr/bin/env python3
"""Offline contract test for BB-A15 read-only Greystone material/texture probe."""

import ast
import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROBE_PATH = ROOT / "Scripts" / "Editor" / "probe_greystone_materials_textures.py"


class ProbeGreystoneMaterialsContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = PROBE_PATH.read_text(encoding="utf-8")

    def test_valid_python_syntax_and_offline_import(self) -> None:
        ast.parse(self.source, filename=str(PROBE_PATH))
        spec = importlib.util.spec_from_file_location("probe_greystone_materials_textures", PROBE_PATH)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        self.assertIsNone(module.unreal)
        self.assertEqual(module.CHILD_BP_PATH, "/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer")
        self.assertEqual(module.PARENT_BP_PATH, "/Game/OneBossFight/GreystonePack/BP_GreystonePlayer")
        with self.assertRaises(RuntimeError):
            module.run_probe(write_report=False)

    def test_strictly_read_only_no_asset_save_or_mutation_calls(self) -> None:
        forbidden = (
            r"save_loaded_asset|save_asset|save_package|delete_asset|"
            r"set_editor_property|create_asset|duplicate_asset|rename_asset"
        )
        self.assertIsNone(
            re.search(forbidden, self.source),
            "Read-only probe must not reference save/mutation asset APIs",
        )
        self.assertIn("include_hard_package_references=True", self.source)
        self.assertIn("include_soft_package_references=True", self.source)
        self.assertIn("MaterialEditingLibrary.get_used_textures", self.source)


if __name__ == "__main__":
    unittest.main()
