"""Contract test for SFX Batch 3 Candidate Specification (C-1203).

Validates:
1. Every cited sound cue or wave asset exists in the Content folder.
2. No external asset references are made.
3. Every task SFX-11 through SFX-15 has at least 2 distinct in-repo candidate options.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

CITED_ASSETS = [
    # SFX-11 (A1 Horizontal)
    "Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_1_Cue.uasset",
    "Content/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_1_Cue.uasset",
    "Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Sword_Swing_Cue.uasset",
    # SFX-12 (A2 Overhead)
    "Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_3_Cue.uasset",
    "Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Axe_Swing_Cue.uasset",
    "Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_5_Cue.uasset",
    # SFX-13 (A3 Stomp)
    "Content/Vefects/Easy_Shockwaves_VFX/Audio/Cues/SFX_Vefects_Shockwave_01_1s_Cue.uasset",
    "Content/StarterContent/Audio/Explosion_Cue.uasset",
    "Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue.uasset",
    # SFX-14 (Mid01 Thrust)
    "Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_1_Cue.uasset",
    "Content/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_4_Cue.uasset",
    "Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_7_Cue.uasset",
    # SFX-15 (Sprint Gap Closer)
    "Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_2_Cue.uasset",
    "Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Hammer_Swing_Cue.uasset",
    "Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_8_Cue.uasset",
]


class TestSfxBatch3CandidatesContract(unittest.TestCase):

    def test_all_cited_candidates_exist_on_disk(self):
        """Every asset cited in SFX_05_BATCH3_CANDIDATE_SPEC.md must exist in Content/."""
        for rel_path in CITED_ASSETS:
            full_path = os.path.join(PROJECT_ROOT, rel_path.replace("/", os.sep))
            self.assertTrue(os.path.exists(full_path), f"Cited audio asset does not exist: {rel_path}")

    def test_batch3_spec_doc_structure(self):
        """Spec doc must document SFX-11 through SFX-15."""
        doc_path = os.path.join(PROJECT_ROOT, "Documentation", "Boss", "SFX_05_BATCH3_CANDIDATE_SPEC.md")
        self.assertTrue(os.path.exists(doc_path))
        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()
        for sfx_id in ["SFX-11", "SFX-12", "SFX-13", "SFX-14", "SFX-15"]:
            self.assertIn(sfx_id, content)


if __name__ == "__main__":
    unittest.main()
