"""Offline source contracts for default-off, config-driven camera B+C options."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
HEADER = ROOT / "Source/OneBossFight/Player/RPGCameraRig.h"
CPP = ROOT / "Source/OneBossFight/Player/RPGCameraRig.cpp"
INI = ROOT / "Config/DefaultGame.ini"


class CameraConfigOptionsContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.header = HEADER.read_text(encoding="utf-8")
        cls.cpp = CPP.read_text(encoding="utf-8")
        cls.ini = INI.read_text(encoding="utf-8")

    def test_switches_are_config_properties_with_false_native_defaults(self):
        self.assertRegex(self.header, r"UCLASS\([^\n]*Config\s*=\s*Game")
        for name in ("bDefaultHideBossInside", "bDefaultLockOnFraming"):
            self.assertRegex(self.header, rf"UPROPERTY\([^\n]*Config[^\n]*\)\s*bool\s+{name}\s*=\s*false\s*;")
            self.assertRegex(self.ini, rf"{name}=False")

    def test_dev_cvars_are_tristate_overrides_and_do_not_exist_in_shipping(self):
        for cvar in ("HideBossInside", "LockOnFraming"):
            self.assertRegex(self.cpp, rf"#if\s+!UE_BUILD_SHIPPING[\s\S]*?rpg\.Camera\.{cvar}[\s\S]*?\),\s*-1\s*,")
        self.assertIn("Override >= 0", self.cpp)
        self.assertIn("Override != 0", self.cpp)

    def test_shipping_build_compiles_only_the_option_code_needed_for_config(self):
        for method_name in ("ApplyBossHideInsideOption", "ApplyLockOnFramingOption"):
            method = re.search(rf"void URPGCameraRig::{method_name}\([^\n]*\)\n\{{[\s\S]*?\n\}}", self.cpp)
            self.assertIsNotNone(method, method_name)
            self.assertIn("bDefault", method.group(0))
            self.assertRegex(method.group(0), r"int32 Override = -1;[\s\S]*?#if !UE_BUILD_SHIPPING[\s\S]*?#endif[\s\S]*?Override >= 0 \? Override != 0 : bDefault")
        self.assertIn("#if !UE_BUILD_SHIPPING\n\tconst bool bEnabled = CVarCameraBossBlocks", self.cpp)

    def test_cvar_off_overrides_true_config_and_default_override_uses_config(self):
        for method_name, cvar in (("ApplyBossHideInsideOption", "CVarCameraHideBossInside"),
                                  ("ApplyLockOnFramingOption", "CVarCameraLockOnFraming")):
            method = re.search(rf"void URPGCameraRig::{method_name}\([^\n]*\)\n\{{[\s\S]*?\n\}}", self.cpp).group(0)
            self.assertIn("Override = " + cvar, method)
            self.assertIn("Override >= 0 ? Override != 0 : bDefault", method)

    def test_cpp_preprocessor_guards_are_balanced(self):
        self.assertEqual(self.cpp.count("#if"), self.cpp.count("#endif"))


if __name__ == "__main__":
    unittest.main()
