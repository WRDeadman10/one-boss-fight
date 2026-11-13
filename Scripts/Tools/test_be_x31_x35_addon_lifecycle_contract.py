#!/usr/bin/env python3
"""Source-contract checks for framework add-on lifecycle and resolved-damage healing."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
EXECUTOR = (ROOT / "Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp").read_text(encoding="utf-8")
RULE_TESTS = (ROOT / "Source/OneBossFight/Tests/RPGBossMoveCardTests.cpp").read_text(encoding="utf-8")


def section(start: str, end: str) -> str:
    begin = EXECUTOR.index(start)
    finish = EXECUTOR.index(end, begin + len(start))
    return EXECUTOR[begin:finish]


class AddonLifecycleContract(unittest.TestCase):
    def test_abort_clears_area_snare_even_after_prior_terminal_state(self):
        body = section("void URPGFrameworkMoveExecutor::Abort(", "bool URPGFrameworkMoveExecutor::IsIdle()")
        self.assertLess(body.index("ClearAreaSnare(true)"), body.index("if (bAborted||bFinished) return"))

    def test_endplay_clears_snare_and_aborts_executor(self):
        body = section("void URPGFrameworkMoveExecutor::EndPlay(", "bool URPGFrameworkMoveExecutor::IsIdle()") if "bool URPGFrameworkMoveExecutor::IsIdle()" in EXECUTOR[EXECUTOR.index("void URPGFrameworkMoveExecutor::EndPlay("):] else EXECUTOR[EXECUTOR.index("void URPGFrameworkMoveExecutor::EndPlay("):]
        self.assertIn("ClearAreaSnare(true)", body)
        self.assertIn('Abort(TEXT("EndPlay"))', body)

    def test_snare_cleanup_clears_timer_restores_only_owned_speed_and_resets_state(self):
        body = section("void URPGFrameworkMoveExecutor::ClearAreaSnare(", "void URPGFrameworkMoveExecutor::TickChannelDrain(")
        self.assertIn("ClearTimer(AreaSnareTimer)", body)
        self.assertIn("FMath::IsNearlyEqual(Movement->MaxWalkSpeed,AreaSnareAppliedSpeed,.5f)", body)
        self.assertIn("Movement->MaxWalkSpeed=AreaSnareBaseSpeed", body)
        self.assertIn("AreaSnareTarget.Reset()", body)
        self.assertIn("AreaSnareEndsAt=0.", body)

    def test_area_effect_is_resolved_once_before_target_or_radius_early_returns(self):
        body = section("void URPGFrameworkMoveExecutor::TickAreaEffect(", "void URPGFrameworkMoveExecutor::TickAreaSnare()")
        self.assertIn("bAreaEffectResolved=true", body)
        self.assertLess(body.index("bAreaEffectResolved=true"), body.index("if (!TargetCharacter||TargetCharacter->IsActorBeingDestroyed()) return"))
        self.assertIn("bAreaEffectResolved", body)

    def test_channel_ticks_are_card_local_and_end_without_an_independent_timer(self):
        body = section("void URPGFrameworkMoveExecutor::TickChannelDrain(", "void URPGFrameworkMoveExecutor::BeginGrab(")
        self.assertIn("while (ChannelTickIndex<MaxTicks)", body)
        self.assertIn("PrevPosition>=TickAt||Position<TickAt", body)
        self.assertIn("bChannelFacingCaptured=false", body)
        self.assertNotIn("SetTimer", body)
        self.assertNotIn("SetTimerForNextTick", body)

    def test_channel_heal_uses_only_accepted_resolver_hpapplied(self):
        body = section("void URPGFrameworkMoveExecutor::TickChannelDrain(", "void URPGFrameworkMoveExecutor::BeginGrab(")
        applied = body.index("Applied=Result.HPApplied")
        accepted = body.index("if (Result.Outcome==ERPGDamageOutcome::Accepted)", applied)
        heal = body.index("CappedHeal(Applied,double(Channel.HealFraction)", accepted)
        self.assertLess(applied, accepted)
        self.assertLess(applied, heal)
        self.assertNotIn("CappedHeal(Channel.TickDamage", body)
        self.assertIn("partially accepted tick heals from resolved HP loss, not nominal tick damage", RULE_TESTS)
        self.assertIn("CappedHeal(6.,.5,50.,100.),3.", RULE_TESTS)
        self.assertIn("CappedHeal(6.,.5,99.,100.),1.", RULE_TESTS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
