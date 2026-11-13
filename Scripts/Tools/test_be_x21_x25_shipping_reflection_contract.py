#!/usr/bin/env python3
"""Offline reflection policy and guard parity for Queue BE X21-X25."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]


def source(path):
    return (ROOT / path).read_text(encoding="utf-8")


def editor_guarded_ufunction(header, name):
    pattern = (r"#if\s+WITH_EDITORONLY_DATA\s+UFUNCTION\([^\n]*\)\s+#endif\s+"
               r"[^;\n]*\b" + re.escape(name) + r"\s*\(")
    return re.search(pattern, header) is not None


class ShippingReflectionContract(unittest.TestCase):
    def test_resolver_test_hooks_are_editor_reflection_only_and_keep_cpp_defs(self):
        header = source("Source/OneBossFight/Player/RPGDamageResolver.h")
        cpp = source("Source/OneBossFight/Player/RPGDamageResolver.cpp")
        for name in ("ResolveForTest", "NoteOverlapForTest"):
            self.assertTrue(editor_guarded_ufunction(header, name), name)
            self.assertIn("URPGDamageResolver::" + name, cpp)
        self.assertIn("#if UE_BUILD_SHIPPING", cpp[cpp.index("URPGDamageResolver::ResolveForTest"):])
        self.assertTrue(editor_guarded_ufunction(header, "GetAuditCount" ) is False)

    def test_framework_test_bridge_uht_declarations_have_guard_parity(self):
        header = source("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.h")
        for name in ("InitializeWithProfileForTest", "StartCardForTest", "StartSelectedCardForTest",
                     "GetOutcomeForTest", "GetNavigationResultForTest", "StartComboForTest",
                     "SpawnFrameworkBossForTest"):
            self.assertTrue(editor_guarded_ufunction(header, name), name)

    def test_dodge_iframe_test_and_synthetic_hooks_are_editor_reflection_only(self):
        dodge = source("Source/OneBossFight/Player/RPGDodgeTiming.h")
        iframe = source("Source/OneBossFight/Player/RPGIFrameMonitor.h")
        dodge_cpp = source("Source/OneBossFight/Player/RPGDodgeTiming.cpp")
        iframe_cpp = source("Source/OneBossFight/Player/RPGIFrameMonitor.cpp")
        for name in ("IsGuardCounterArmed", "DebugArmGuardCounter", "DescribeGuardState"):
            self.assertTrue(editor_guarded_ufunction(dodge, name), name)
            self.assertIn("URPGDodgeTiming::" + name, dodge_cpp)
        self.assertTrue(editor_guarded_ufunction(iframe, "DebugForceOwned"))
        self.assertIn("URPGIFrameMonitor::DebugForceOwned", iframe_cpp)
        self.assertNotIn("#if WITH_EDITORONLY_DATA\n\tUFUNCTION(BlueprintCallable, Category = \"Dodge\")\n\t#endif\n\tvoid NotifySuccessfulGuardContact", dodge)

    def test_runtime_diagnostics_and_player_actions_stay_reflected(self):
        damage = source("Source/OneBossFight/Player/RPGDamageResolver.h")
        parry = source("Source/OneBossFight/Player/RPGPlayerParry.h")
        iframe = source("Source/OneBossFight/Player/RPGIFrameMonitor.h")
        dodge = source("Source/OneBossFight/Player/RPGDodgeTiming.h")
        self.assertRegex(damage, r"UFUNCTION\(BlueprintPure, Category = \"Damage\"\)\s+int32 GetAuditCount")
        self.assertRegex(parry, r"UFUNCTION\(BlueprintCallable, Category = \"Parry\"\)\s+bool Press")
        self.assertRegex(iframe, r"UFUNCTION\(BlueprintPure, Category = \"IFrame\"\)\s+bool IsInvulnerableNow")
        self.assertRegex(dodge, r"UFUNCTION\(BlueprintPure, Category = \"Dodge\"\)\s+FString GetStageName")


if __name__ == "__main__":
    unittest.main(verbosity=2)
