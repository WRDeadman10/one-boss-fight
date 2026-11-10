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
        self.assertIn("get_material_instance_texture_parameter_value", self.source)
        self.assertIn("get_base_material", self.source)

    def test_collect_used_textures_walks_material_instance_parent_and_base(self) -> None:
        spec = importlib.util.spec_from_file_location("probe_greystone_materials_textures", PROBE_PATH)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)

        class FakeTexture:
            def __init__(self, path: str) -> None:
                self._path = path

            def get_path_name(self) -> str:
                return self._path

        class FakeMaterial:
            def __init__(self, path: str) -> None:
                self._path = path

            def get_path_name(self) -> str:
                return self._path

        class FakeTPV:
            def __init__(self, tex: FakeTexture) -> None:
                self._tex = tex

            def get_editor_property(self, name: str):
                return self._tex if name == "parameter_value" else None

        class FakeMIC:
            def __init__(self, path: str, parent=None, tpvs=None, base=None) -> None:
                self._path = path
                self._parent = parent
                self._tpvs = tpvs or []
                self._base = base

            def get_path_name(self) -> str:
                return self._path

            def get_editor_property(self, name: str):
                if name == "parent":
                    return self._parent
                if name == "texture_parameter_values":
                    return self._tpvs
                return None

            def get_base_material(self):
                return self._base

        tex_param = FakeTexture("/Game/ParagonGreystone/Characters/Heroes/Greystone/Textures/T_Greystone_D.T_Greystone_D")
        tex_override = FakeTexture("/Game/ParagonGreystone/Characters/Heroes/Greystone/Textures/T_Greystone_N.T_Greystone_N")
        tex_base = FakeTexture("/Game/ParagonGreystone/Characters/Global/Textures/T_Global_Default.T_Global_Default")
        base_mat = FakeMaterial("/Game/ParagonGreystone/Materials/M_Base.M_Base")
        parent_mic = FakeMIC("/Game/ParagonGreystone/Materials/MIC_Parent.MIC_Parent", parent=base_mat)
        leaf_mic = FakeMIC(
            "/Game/ParagonGreystone/Materials/MIC_Leaf.MIC_Leaf",
            parent=parent_mic,
            tpvs=[FakeTPV(tex_override)],
            base=base_mat,
        )

        class FakeMatLib:
            @staticmethod
            def get_texture_parameter_names(obj):
                return ["Albedo"] if obj is leaf_mic else []

            @staticmethod
            def get_material_instance_texture_parameter_value(obj, pname: str):
                return tex_param if (obj is leaf_mic and pname == "Albedo") else None

            @staticmethod
            def get_used_textures(mat):
                if not isinstance(mat, FakeMaterial):
                    raise TypeError("Cannot nativize MaterialInstanceConstant as Material")
                return [tex_base]

        class FakeUnreal:
            Material = FakeMaterial
            MaterialEditingLibrary = FakeMatLib

        orig_unreal = module.unreal
        try:
            module.unreal = FakeUnreal
            textures = module._collect_used_textures(leaf_mic)
        finally:
            module.unreal = orig_unreal

        self.assertEqual(
            textures,
            [
                "/Game/ParagonGreystone/Characters/Global/Textures/T_Global_Default.T_Global_Default",
                "/Game/ParagonGreystone/Characters/Heroes/Greystone/Textures/T_Greystone_D.T_Greystone_D",
                "/Game/ParagonGreystone/Characters/Heroes/Greystone/Textures/T_Greystone_N.T_Greystone_N",
            ],
        )


if __name__ == "__main__":
    unittest.main()
