"""Offline contracts for Claude's AY-C12..C14 Lead PIE preparations."""

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]
RESET_DRIVER = ROOT / "Scripts/Editor/pie_player_death_reset.py"
FIGHT_DRIVER = ROOT / "Scripts/Editor/pie_full_fight.py"
COMBAT_DEBUG = ROOT / "Source/OneBossFight/Player/RPGCombatDebug.cpp"
FRAMEWORK_BOSS_H = ROOT / "Source/OneBossFight/Boss/RPGFrameworkBossCharacter.h"


class AYLeadDriverContracts(unittest.TestCase):
    def test_c12_opens_real_parry_then_checks_new_pawn_before_cooldown_probe(self):
        source = RESET_DRIVER.read_text(encoding="utf-8")
        self.assertIn('("parry window lifecycle", setup_parry_lifecycle, noop, 0.0, 0.0)', source)
        self.assertIn('opened = bool(parry.press())', source)
        self.assertIn('active = bool(parry.is_window_open())', source)
        self.assertIn('has_tag(pawn, "Status.ParryActive")', source)
        self.assertIn('p["dbg"].debug_set_player_health(0.0)', source)
        self.assertIn('parry_window_before_probe=%s status_parry_active_before_probe=%s', source)
        self.assertIn('cooldown_ready = bool(parry.press())', source)
        self.assertIn('new_parried == 0 and press_before == 0 and cooldown_ready and press_after == 1', source)
        self.assertIn('not new_window and new_tag is False', source)
        self.assertIn('PARRY_LIFECYCLE stage=death_request', source)
        self.assertIn('matching_spawned_candidates=', source)
        self.assertIn('RESPAWN_WAIT elapsed=%.1f controller_pawn=%s class=%s', source)
        self.assertIn('> 45.0', source)

    def test_c13_debug_posture_hook_does_not_target_framework_boss_state(self):
        debug_source = COMBAT_DEBUG.read_text(encoding="utf-8")
        debug_hook = debug_source.split('void URPGCombatDebug::DebugDrainBossPosture', 1)[1].split(
            'void URPGCombatDebug::DebugSetBossHealthFraction', 1)[0]
        framework_header = FRAMEWORK_BOSS_H.read_text(encoding="utf-8")
        scope_report = (ROOT / "Documentation/Boss/AY_C13_POSTURE_DEBUG_SCOPE.md").read_text(encoding="utf-8")
        self.assertIn('FindComponentByClass<URPGBossPosture>()', debug_hook)
        self.assertIn('Posture=0.', framework_header)
        self.assertIn('PendingParryRecoverySeconds=0.', framework_header)
        self.assertIn('C13 status: N/A (C-1170)', scope_report)
        self.assertIn('not available in `L_SevarogArena`', scope_report)
        # The framework proof actor stores posture/recovery internally; do not
        # silently use the pack-only debug component probe as KI-177 evidence.
        self.assertFalse((ROOT / "Scripts/Editor/pie_ay_stance_recovery.py").exists())

    def test_c14_video_prep_keeps_normal_actions_parry_targets_and_tier2_opt_in(self):
        source = FIGHT_DRIVER.read_text(encoding="utf-8")
        self.assertIn('PARRY_MOVE_PRESS_POSITIONS = {"A1b": 0.12, "A3b": 0.10, "A1": 0.27, "A3a": 0.42, "A2": 1.92}', source)
        self.assertIn('PARRY_MONTAGE_PRESS_POSITIONS = {"Mid01_Anim_Montage": 0.62}', source)
        self.assertIn('PARRY_LOG_ONLY_MONTAGES = {"GS_SprintAttackFollowUp_Montage"}', source)
        self.assertIn('FIGHT_PARRY_ONLY = os.environ.get("FIGHT_PARRY_ONLY", "0") == "1"', source)
        self.assertIn('"light", "light", "strong", "backstep", "air_light", "guard", "light", "air_heavy"', source)
        self.assertIn('"parry_watch"', source)
        self.assertIn('tier2 = os.environ.get("ER_FIGHT_TIER2", "0") == "1"', source)
        self.assertIn('MAX_FIGHT_SECONDS = float(os.environ.get("FIGHT_MAX", "480"))', source)
        prep = (ROOT / "Documentation/Boss/AY_C14_OWNER_VIDEO3_PREP.md").read_text(encoding="utf-8")
        for value in ("FIGHT_MAX=150", "ER_FIGHT_TIER2=1", "FIGHT_RUN=owner_video3",
                      "FIGHT_FRAMES=D:/FightVideo/owner_video3/frames", "PARRY_RECOIL"):
            self.assertIn(value, prep)


if __name__ == "__main__":
    unittest.main()
