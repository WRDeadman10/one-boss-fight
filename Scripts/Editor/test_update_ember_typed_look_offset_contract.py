"""Offline regression contract for Unreal FTransform/Quat readback."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("update_ember_typed_look_offset.py")
EDITOR_DIR = str(SCRIPT_PATH.parent)
if EDITOR_DIR not in sys.path:
    sys.path.insert(0, EDITOR_DIR)

# The production updater is import-safe for this test and only needs the Unreal
# module at runtime when main() is executed by the Editor.
sys.modules.setdefault("unreal", types.ModuleType("unreal"))
SPEC = importlib.util.spec_from_file_location("ember_look_updater", SCRIPT_PATH)
UPDATER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(UPDATER)


class FakeRotator:
    def __init__(self, pitch, yaw, roll):
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll


class FakeQuat:
    """Mirrors UE Python's FQuat surface: rotator(), not pitch/yaw/roll."""
    def __init__(self, pitch, yaw, roll):
        self.expected = FakeRotator(pitch, yaw, roll)
        self.converted = False

    def rotator(self):
        self.converted = True
        return self.expected


class FakeVector:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


class FakeTransform:
    def __init__(self, translation, rotation, scale3d):
        self.translation = translation
        self.rotation = rotation
        self.scale3d = scale3d


class UpdateEmberTypedLookOffsetContract(unittest.TestCase):
    def test_ftransform_quaternion_readback_uses_rotator_conversion(self):
        quat = FakeQuat(19.84, -1.84, -10.48)
        values = UPDATER.rotation_values(quat)
        self.assertTrue(quat.converted)
        self.assertEqual(values, (19.84, -1.84, -10.48))

    def test_offset_match_accepts_target_ftransform_with_fake_quat(self):
        transform = FakeTransform(
            FakeVector(0.0, 0.0, 0.0),
            FakeQuat(19.84, -1.84, -10.48),
            FakeVector(1.0, 1.0, 1.0),
        )
        self.assertTrue(UPDATER.offset_matches(
            transform, (19.84, -1.84, -10.48)))


if __name__ == "__main__":
    unittest.main()
