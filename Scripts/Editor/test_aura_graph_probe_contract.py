from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
HEADER = ROOT / "Source/OneBossFightEditor/Public/AuraBoostLiteGraphAuthoringCommandlet.h"
SOURCE = ROOT / "Source/OneBossFightEditor/Private/AuraBoostLiteGraphAuthoringCommandlet.cpp"
RUNTIME_BUILD = ROOT / "Source/OneBossFight/OneBossFight.Build.cs"
EDITOR_BUILD = ROOT / "Source/OneBossFightEditor/OneBossFightEditor.Build.cs"
PROJECT = ROOT / "OneBossFight.uproject"
EDITOR_TARGET = ROOT / "Source/OneBossFightEditor.Target.cs"


class AuraGraphProbeContractTests(unittest.TestCase):
    def test_probe_is_isolated_in_editor_module(self):
        header = HEADER.read_text(encoding="utf-8")
        source = SOURCE.read_text(encoding="utf-8")
        runtime = RUNTIME_BUILD.read_text(encoding="utf-8")
        editor = EDITOR_BUILD.read_text(encoding="utf-8")
        project = PROJECT.read_text(encoding="utf-8")
        target = EDITOR_TARGET.read_text(encoding="utf-8")

        self.assertIn("UAuraBoostLiteGraphAuthoringCommandlet : public UCommandlet", header)
        self.assertIn('TEXT("/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_BoostLite")', source)
        self.assertIn("GetEmitterHandles()", source)
        self.assertIn("GetNodesOfClass", source)
        self.assertIn("INSPECT_ONLY_COMPLETE", source)
        self.assertNotIn("NiagaraEditor", runtime)
        self.assertIn('"NiagaraEditor"', editor)
        self.assertIn('"Name": "OneBossFightEditor"', project)
        self.assertIn('ExtraModuleNames.Add("OneBossFightEditor")', target)


if __name__ == "__main__":
    unittest.main()
