from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HEADER = ROOT / "Source/OneBossFightEditor/Public/AuraBoostLiteGraphAuthoringCommandlet.h"
SOURCE = ROOT / "Source/OneBossFightEditor/Private/AuraBoostLiteGraphAuthoringCommandlet.cpp"
BUILD = ROOT / "Source/OneBossFightEditor/OneBossFightEditor.Build.cs"


class AuraGraphAuthoringContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = HEADER.read_text(encoding="utf-8") + SOURCE.read_text(encoding="utf-8")
        cls.build = BUILD.read_text(encoding="utf-8")

    def test_source_and_destination_are_project_copy_only(self) -> None:
        for literal in (
            'SourcePath = TEXT("/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_BoostLite")',
            'DestinationPath = TEXT("/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_BoostLite_Authored")',
            'ProductionPath = TEXT("/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura")',
            'PackRoot = TEXT("/Game/AdvancedARPGCombat")',
        ):
            self.assertIn(literal, self.text)
        self.assertIn("assert_safe_copy_paths", self.text)
        self.assertIn("DoesPackageExist(DestinationPath)", self.text)

    def test_graph_defaults_and_user_parameter_defaults_use_editor_data(self) -> None:
        for marker in (
            "UNiagaraNodeFunctionCall",
            "FNiagaraStackGraphUtilities",
            "TrySetDefaultValue",
            "FNiagaraParameterStore",
            'TEXT("User.Scale_All")',
            'TEXT("User.Color_Spiral1")',
        ):
            self.assertIn(marker, self.text)
        self.assertNotIn("RapidIterationParameters", self.text)
        self.assertNotIn("Serialize", self.text)
        self.assertIn('"NiagaraEditor"', self.build)
        runtime_build = BUILD.parents[1] / "OneBossFight" / "OneBossFight.Build.cs"
        self.assertNotIn('"NiagaraEditor"', runtime_build.read_text(encoding="utf-8"))

    def test_compile_save_reload_readback_is_fail_closed(self) -> None:
        for marker in (
            "RequestCompile(true",
            "WaitForCompilationComplete",
            "SavePackage",
            "LoadObject<UNiagaraSystem>",
            "ROUNDTRIP_PASS",
            "ENiagaraEmitterCalculateBoundMode::Fixed",
            "VerifyGraphInput",
            "VerifyGraphVec2",
            "ReadUserColor",
        ):
            self.assertIn(marker, self.text)
        self.assertIn("DestinationPath", self.text)


if __name__ == "__main__":
    unittest.main()
