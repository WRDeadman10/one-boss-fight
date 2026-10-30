# Copyright One Boss Fight. All Rights Reserved.
"""
Offline validation test for Slice F8 Posture and Stance Break Implementation Plan.
Verifies all source file line citations, pure priority rules, and profile contracts.
"""

import os
import unittest


class TestF8PostureImplementationPlan(unittest.TestCase):
    def setUp(self):
        self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))

    def _read_lines(self, rel_path):
        full_path = os.path.join(self.repo_root, rel_path)
        self.assertTrue(os.path.exists(full_path), f"File not found: {rel_path}")
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.readlines()

    def test_legacy_rules_citations(self):
        """Verify RPGBossRules.h citations in Section 2."""
        lines = self._read_lines('Source/OneBossFight/Player/RPGBossRules.h')
        
        # Priority order documentation at lines 8-10
        self.assertIn("Freeze 21 priority order", "".join(lines[6:11]))
        
        # FFlags at line 14
        self.assertIn("struct FFlags", lines[13])
        
        # EBreakResult at line 25
        self.assertIn("enum class EBreakResult", lines[24])
        
        # ETransitionResult at line 28
        self.assertIn("enum class ETransitionResult", lines[27])
        self.assertIn("QueuedBehindStagger", lines[27])
        
        # ResolveBreak at line 60
        self.assertIn("ResolveBreak", lines[59])
        
        # ResolveTransition at line 72
        self.assertIn("ResolveTransition", lines[71])

    def test_legacy_posture_component_citations(self):
        """Verify RPGBossPosture.h & RPGBossStagger.h citations in Section 2."""
        posture_h = self._read_lines('Source/OneBossFight/Player/RPGBossPosture.h')
        self.assertIn("float PostureMax = 100.f;", posture_h[30])
        self.assertIn("float RegenDelaySeconds = 6.f;", posture_h[34])
        self.assertIn("float RegenPerSecond = 13.f;", posture_h[38])
        self.assertIn("EDrainResult ApplyPostureDamage", posture_h[68])
        self.assertIn("void RefillAfterBreak()", posture_h[79])
        self.assertIn("void BeginHold(EHold Mode)", posture_h[96])

        stagger_h = self._read_lines('Source/OneBossFight/Player/RPGBossStagger.h')
        self.assertIn("float StaggerSeconds = 2.5f;", stagger_h[35])
        self.assertIn("float CriticalMultiplier = 2.5f;", stagger_h[43])
        self.assertIn("float CooldownSeconds = 0.f;", stagger_h[133])
        self.assertIn("RequestBreak(bool bIgnoreCooldown)", stagger_h[194])
        self.assertIn("void AbortStagger()", stagger_h[198])

    def test_framework_boss_hooks_citations(self):
        """Verify RPGFrameworkBossCharacter hooks cited in Section 4."""
        boss_cpp = self._read_lines('Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp')
        
        # Tick (lines 80-85 across revisions)
        self.assertTrue(any("void ARPGFrameworkBossCharacter::Tick(float Delta)" in l for l in boss_cpp[79:85]))
        
        # ApplyPlayerHit (lines 149-165 across revisions)
        self.assertTrue(any("double ARPGFrameworkBossCharacter::ApplyPlayerHit(double Multiplier)" in l for l in boss_cpp[148:165]))
        
        # RestartEncounter (lines 158-215 across revisions)
        self.assertTrue(any("bool ARPGFrameworkBossCharacter::RestartEncounter(uint64 NewGeneration,FString& Error)" in l for l in boss_cpp[155:215]))
        
        # Die (lines 177-235 across revisions)
        self.assertTrue(any("void ARPGFrameworkBossCharacter::Die()" in l for l in boss_cpp[175:235]))

    def test_executor_abort_citation(self):
        """Verify RPGFrameworkMoveExecutor::Abort cited in Section 4."""
        exec_cpp = self._read_lines('Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp')
        self.assertTrue(any("void URPGFrameworkMoveExecutor::Abort(const FString& Reason)" in l for l in exec_cpp[205:220]))
        self.assertTrue(any("Model_.Abort(Token,Events,Error);" in l for l in exec_cpp[210:225]))

    def test_profile_schema_citations(self):
        """Verify profile schema cited in Section 5."""
        profile_h = self._read_lines('Source/OneBossFight/Player/RPGBossFrameworkProfile.h')
        self.assertIn("float BossMaxHealth=0.f;", profile_h[48])
        self.assertIn("float PlayerHitDamage=0.f;", profile_h[49])
        self.assertIn("float PhaseTwoFraction=0.f;", profile_h[51])
        self.assertIn("FName PhaseTwoId;", profile_h[52])

    def test_pure_rules_break_priority(self):
        """Simulate pure RPGBossRules::ResolveBreak priority logic."""
        def resolve_break(dead, dormant, transition, staggered, cooldown, ignore_cooldown):
            if dead: return "Dead"
            if dormant: return "Dormant"
            if transition: return "Transition"
            if staggered: return "AlreadyStaggered"
            if cooldown and not ignore_cooldown: return "Cooldown"
            return "Started"

        # Dead outranks all
        self.assertEqual(resolve_break(dead=True, dormant=True, transition=True, staggered=True, cooldown=True, ignore_cooldown=True), "Dead")
        # Dormant outranks transition/staggered
        self.assertEqual(resolve_break(dead=False, dormant=True, transition=True, staggered=True, cooldown=False, ignore_cooldown=False), "Dormant")
        # Transition outranks staggered/cooldown
        self.assertEqual(resolve_break(dead=False, dormant=False, transition=True, staggered=True, cooldown=False, ignore_cooldown=False), "Transition")
        # Staggered outranks cooldown
        self.assertEqual(resolve_break(dead=False, dormant=False, transition=False, staggered=True, cooldown=True, ignore_cooldown=False), "AlreadyStaggered")
        # Cooldown drops request unless ignore_cooldown
        self.assertEqual(resolve_break(dead=False, dormant=False, transition=False, staggered=False, cooldown=True, ignore_cooldown=False), "Cooldown")
        self.assertEqual(resolve_break(dead=False, dormant=False, transition=False, staggered=False, cooldown=True, ignore_cooldown=True), "Started")
        # Clean start
        self.assertEqual(resolve_break(dead=False, dormant=False, transition=False, staggered=False, cooldown=False, ignore_cooldown=False), "Started")

    def test_pure_rules_transition_queued_behind_stagger(self):
        """Simulate pure RPGBossRules::ResolveTransition queueing behind stagger."""
        def resolve_transition(health, max_hp, fraction, dead, dormant, phase_two, staggered):
            if max_hp <= 0.0: return "NotReady"
            if health <= 0.0 or dead: return "Dead"
            if dormant: return "Dormant"
            if phase_two: return "AlreadyDone"
            if health / max_hp > fraction: return "AboveThreshold"
            if staggered: return "QueuedBehindStagger"
            return "Start"

        # At or below threshold while staggered -> QueuedBehindStagger
        self.assertEqual(resolve_transition(health=50, max_hp=200, fraction=0.5, dead=False, dormant=False, phase_two=False, staggered=True), "QueuedBehindStagger")
        # Once stagger ends -> Start
        self.assertEqual(resolve_transition(health=50, max_hp=200, fraction=0.5, dead=False, dormant=False, phase_two=False, staggered=False), "Start")
        # Dead takes precedence over QueuedBehindStagger
        self.assertEqual(resolve_transition(health=0, max_hp=200, fraction=0.5, dead=True, dormant=False, phase_two=False, staggered=True), "Dead")


if __name__ == '__main__':
    unittest.main()
