import os
import unittest

class TestSFXBatch8CandidatesContract(unittest.TestCase):
    def setUp(self):
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.content_dir = os.path.join(self.project_root, "Content")
        self.candidates = [
            "AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Select01.uasset",
            "AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Box_Confirm.uasset",
            "RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_1_Cue.uasset",
            "RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_5_Cue.uasset",
            "AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Hover.uasset",
            "RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_2_Cue.uasset",
            "ParagonGreystone/Audio/Cues/Greystone_Effort_BreathingRun.uasset",
            "ParagonGreystone/Audio/Cues/Greystone_Effort_BreathingLowHealth.uasset",
            "ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_BreathingRun.uasset",
            "ParagonGreystone/Audio/Cues/Greystone_Health_Low.uasset",
            "ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Health_Critical.uasset",
            "ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Health_Low.uasset",
            "ParagonGreystone/Audio/Cues/Greystone_Status_Defeat.uasset",
            "ParagonGreystone/Audio/Cues/Greystone_Death.uasset",
            "ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Status_Defeat.uasset"
        ]

    def test_all_15_candidates_exist(self):
        for rel_path in self.candidates:
            full_path = os.path.join(self.content_dir, rel_path.replace("/", os.sep))
            self.assertTrue(os.path.exists(full_path), f"Candidate audio asset missing: {rel_path}")

    def test_candidate_spec_doc_exists(self):
        spec_path = os.path.join(self.project_root, "Documentation", "Boss", "SFX_11_BATCH8_CANDIDATE_SPEC.md")
        self.assertTrue(os.path.exists(spec_path), f"Spec doc missing: {spec_path}")

    def test_candidate_spec_mentions_all_tasks(self):
        spec_path = os.path.join(self.project_root, "Documentation", "Boss", "SFX_11_BATCH8_CANDIDATE_SPEC.md")
        with open(spec_path, "r", encoding="utf-8") as f:
            content = f.read()
        for task_id in ["SFX-36", "SFX-37", "SFX-38", "SFX-39", "SFX-40"]:
            self.assertIn(task_id, content, f"Task {task_id} missing from spec doc")

if __name__ == "__main__":
    unittest.main()
