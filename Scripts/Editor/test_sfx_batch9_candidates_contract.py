import os
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONTENT_ROOT = os.path.join(PROJECT_ROOT, "Content")
SPEC_PATH = os.path.join(PROJECT_ROOT, "Documentation", "Boss", "SFX_12_BATCH9_CANDIDATE_SPEC.md")

CANDIDATE_ASSETS = [
    "StarterContent/Audio/Starter_Wind05.uasset",
    "StarterContent/Audio/Starter_Wind06.uasset",
    "StarterContent/Audio/Starter_Background_Cue.uasset",
    "StarterContent/Audio/Fire01_Cue.uasset",
    "StarterContent/Audio/Fire_Sparks01_Cue.uasset",
    "AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Fire01_Cue.uasset",
    "AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/CosmicRift/A_Ability_CosmicRift02.uasset",
    "StarterContent/Audio/Collapse_Cue.uasset",
    "StarterContent/Audio/Collapse01.uasset",
    "AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/HitSounds/A_Guardian_Impact02.uasset",
    "AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue.uasset",
    "StarterContent/Audio/Steam01_Cue.uasset",
    "StarterContent/Audio/Smoke01_Cue.uasset",
    "AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Hover.uasset",
    "AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Select01.uasset",
    "AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Box_Confirm.uasset",
    "AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Select02.uasset",
]

class TestSFXBatch9CandidatesContract(unittest.TestCase):
    def test_spec_file_exists(self):
        self.assertTrue(os.path.isfile(SPEC_PATH), f"Spec file missing: {SPEC_PATH}")

    def test_spec_content_structure(self):
        with open(SPEC_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        for task_id in ["SFX-41", "SFX-42", "SFX-43", "SFX-44", "SFX-45"]:
            self.assertIn(task_id, content, f"Task {task_id} missing from spec")

        self.assertIn("No Wiring", content)
        self.assertIn("Awaiting Owner Audition Selection", content)

    def test_all_candidate_assets_exist_on_disk(self):
        for asset in CANDIDATE_ASSETS:
            full_path = os.path.join(CONTENT_ROOT, asset.replace("/", os.sep))
            self.assertTrue(os.path.isfile(full_path), f"Candidate asset missing on disk: {full_path}")

if __name__ == "__main__":
    unittest.main()
