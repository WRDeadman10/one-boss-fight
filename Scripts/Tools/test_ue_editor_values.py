"""Offline fidelity tests for the reflected shapes used by the G044 Editor scripts."""
import importlib.util
import math
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "Editor" / "ue_editor_values.py"
SPEC = importlib.util.spec_from_file_location("ue_editor_values", MODULE_PATH)
ue = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ue)


class EngineArray(list):
    pass


class FakeUnreal:
    Array = EngineArray


class SoftPath:
    def export_text(self):
        return "SoftObjectPath('/Game/Boss/DA_Boss.DA_Boss')"

    def __str__(self):
        return "{}"


class ReflectedStruct:
    def export_text(self):
        return "(FieldPath=/Game/Boss/DA_Boss.DA_Boss,bEnabled=True,AttackCount=3)"

    def get_editor_property(self, name):
        fields = {"field_path": SoftPath(), "enabled": True, "attack_count": 3}
        if name not in fields:
            raise AttributeError(name)
        return fields[name]


class FakeClass:
    def __init__(self, path, parent=None):
        self.path, self.parent = path, parent

    def get_path_name(self):
        return self.path

    def is_child_of(self, expected):
        return self is expected or self.parent is expected


class FakeAsset:
    def __init__(self, cls):
        self.cls = cls

    def get_class(self):
        return self.cls


class FakeGuid:
    def get_editor_property(self, name):
        return {"a": -1, "b": 2, "c": 0x12345678, "d": 0}.get(name)


class UnrealEditorValuesTests(unittest.TestCase):
    def test_array_and_nested_struct_are_json_values(self):
        actual = ue.stable_value(EngineArray([ReflectedStruct()]), FakeUnreal, "fields")
        self.assertEqual(actual, [{
            "attack_count": 3,
            "enabled": True,
            "field_path": {"object_path": "/Game/Boss/DA_Boss.DA_Boss"},
        }])

    def test_export_text_only_nested_soft_path_matches_live_receipt_shape(self):
        actual = ue.stable_value(SoftPath(), FakeUnreal, "bleed.proc_effect")
        self.assertEqual(actual, {"object_path": "/Game/Boss/DA_Boss.DA_Boss"})

    def test_soft_object_path_uses_export_text_not_repr(self):
        self.assertEqual(ue.ue_path(SoftPath()), "/Game/Boss/DA_Boss.DA_Boss")

    def test_expected_class_accepts_child_uclass(self):
        base = FakeClass("/Script/OneBossFight.RPGBossDefinition")
        child = FakeClass("/Script/OneBossFight.RPGBossDerived", base)
        self.assertTrue(ue.is_expected_class(FakeAsset(child), base))

    def test_guid_format_preserves_unsigned_words(self):
        self.assertEqual(ue.guid_text(FakeGuid()), "FFFFFFFF-00000002-12345678-00000000")

    def test_nonfinite_values_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "health is non-finite"):
            ue.stable_value(math.inf, FakeUnreal, "health")


if __name__ == "__main__":
    unittest.main()
