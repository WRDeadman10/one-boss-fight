#!/usr/bin/env python3
"""Static source contract for C-1288 BK-2 driver controls and Shipping guard."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRIVER = (ROOT / "Scripts/Editor/pie_sevarog_framework_live.py").read_text(encoding="utf-8")
CHARACTER_CPP = (ROOT / "Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp").read_text(encoding="utf-8")
CHARACTER_H = (ROOT / "Source/OneBossFight/Boss/RPGFrameworkBossCharacter.h").read_text(encoding="utf-8")
VERIFIER = (ROOT / "Scripts/Tools/verify_c1278_x26_live_log.py").read_text(encoding="utf-8")
RUNNER = (ROOT / "Scripts/Editor/run_bk2_x26_locked_validation.ps1").read_text(encoding="utf-8")


class BK2X26DriverContractTests(unittest.TestCase):
    def test_card_override_is_allowlisted_and_preserves_default(self):
        self.assertIn("DEFAULT_EXPECTED_CARDS", DRIVER)
        self.assertIn("SEVAROG_LIVE_CARDS", DRIVER)
        self.assertIn("replace(\"+\", \",\")", DRIVER)
        self.assertIn("len(set(cards)) != len(cards)", DRIVER)
        for move in ("Ultimate_Swing_120fps_C1277", "Subjugation_C1277", "Soul_Siphon_C1277"):
            self.assertIn(move, DRIVER)

    def test_profile_initializer_is_bound_to_the_spawned_actor_instance(self):
        self.assertIn('getattr(boss, "initialize_with_profile_for_test", None)', DRIVER)
        self.assertNotIn('getattr(cls, "initialize_with_profile_for_test", None)', DRIVER)

    def test_fraction_hook_is_standalone_and_shipping_excluded(self):
        self.assertIn("SetBossHealthFractionForTest", CHARACTER_H)
        self.assertIn("bool ARPGFrameworkBossCharacter::SetBossHealthFractionForTest", CHARACTER_CPP)
        body = CHARACTER_CPP.split("bool ARPGFrameworkBossCharacter::SetBossHealthFractionForTest", 1)[1].split("FName ARPGFrameworkBossCharacter::StartSelectedCardForTest", 1)[0]
        self.assertIn("#if UE_BUILD_SHIPPING", body)
        self.assertIn("bTestInitialized", body)
        self.assertIn("NM_Standalone", body)
        self.assertIn("Fraction <= 0.0 || Fraction > 1.0", body)
        self.assertIn("SEVAROG_LIVE_BOSS_HEALTH_FRACTION", DRIVER)

    def test_s6_s7_s8_placements_and_dodge_out_variant_are_logged(self):
        for move, distance in (("Ultimate_Swing_120fps_C1277", "120.0"),
                               ("Subjugation_C1277", "600.0"),
                               ("Soul_Siphon_C1277", "400.0")):
            self.assertIn(move, DRIVER)
            self.assertIn(distance, DRIVER)
        self.assertIn("SEVAROG_LIVE_S7_DODGE_OUT", DRIVER)
        self.assertIn("release_plus_0.3s", DRIVER)
        self.assertIn("actualDistanceCm", DRIVER)

    def test_standalone_test_actor_uses_phase_gate_without_production_selector(self):
        tick = CHARACTER_CPP.split("void ARPGFrameworkBossCharacter::Tick", 1)[1].split("void ARPGFrameworkBossCharacter::EndPlay", 1)[0]
        idle = tick.split("if(bArrived&&!bStartedMove)", 1)[1]
        phase_gate = idle.split("// F6c phase gate", 1)[1].split("// Standalone test actors", 1)[0]
        self.assertIn("bPhaseTwoLatched=true", phase_gate)
        self.assertIn("CurrentPhaseId=P.PhaseTwoId", phase_gate)
        self.assertIn("if(bTestInitialized)return;", idle)
        self.assertLess(idle.index("if(bTestInitialized)return;"), idle.index("Selector.Select(Executor->Model(),S,Decision,Pattern)"))
        self.assertIn("!bTestInitialized&&P.LosSearchSeconds>0.f", idle)

    def test_test_health_fraction_survives_next_card_or_combo_start(self):
        setter = CHARACTER_CPP.split("bool ARPGFrameworkBossCharacter::SetBossHealthFractionForTest", 1)[1].split("FName ARPGFrameworkBossCharacter::StartSelectedCardForTest", 1)[0]
        card = CHARACTER_CPP.split("bool ARPGFrameworkBossCharacter::StartTestCardAtIndex", 1)[1].split("bool ARPGFrameworkBossCharacter::StartComboForTest", 1)[0]
        combo = CHARACTER_CPP.split("bool ARPGFrameworkBossCharacter::StartComboForTest", 1)[1].split("bool ARPGFrameworkBossCharacter::ValidateTarget", 1)[0]
        self.assertIn("bTestHealthOverridePending = true", setter)
        for body in (card, combo):
            self.assertIn("const bool bPreserveTestHealth=bTestHealthOverridePending", body)
            self.assertIn("if(bHittable&&!bPreserveTestHealth)Health=MaxHealth", body)
            self.assertIn("if(bPreserveTestHealth)bTestHealthOverridePending=false", body)
        self.assertIn("bTestHealthOverridePending=false", CHARACTER_CPP.split("bool ARPGFrameworkBossCharacter::RestartEncounter", 1)[1])

    def test_autonomous_test_selector_emits_candidate_and_refusal_traces(self):
        selected = CHARACTER_CPP.split("FName ARPGFrameworkBossCharacter::StartSelectedCardForTest", 1)[1].split("FName ARPGFrameworkBossCharacter::GetOutcomeForTest", 1)[0]
        self.assertIn("for(const FRPGBossSelectorTrace& Trace:Decision.Traces)", selected)
        self.assertIn("[FrameworkProof] candidate", selected)
        self.assertIn("[FrameworkProof] refusal", selected)

    def test_phase_two_probes_require_opt_in_latch_and_distinct_range_requests(self):
        api_guard = DRIVER.split('if os.environ.get("SEVAROG_LIVE_PHASE2_PROBES") == "1":', 1)[1]
        api_guard = api_guard.split('if not callable(getattr(cls, "get_navigation_result_for_test", None)):', 1)[0]
        self.assertIn('os.environ.get("SEVAROG_LIVE_AUTONOMOUS") != "1"', api_guard)
        self.assertIn('getattr(cls, "get_current_phase_for_test", None)', api_guard)

        probes = DRIVER.split("def tick_phase2_probes", 1)[1].split("def tick_autonomous_selector", 1)[0]
        self.assertIn('PHASE2_PROBES = (("s6_band", 115.0), ("s8_band", 400.0))', DRIVER)
        self.assertIn('boss.get_current_phase_for_test()', probes)
        self.assertIn('if phase != "Phase_2":', probes)
        self.assertLess(probes.index('if phase != "Phase_2":'), probes.index("place_player_at_distance(pawn, boss, distance, label)"))
        self.assertLess(probes.index("place_player_at_distance(pawn, boss, distance, label)"),
                        probes.index("boss.start_selected_card_for_test()"))
        self.assertIn('STATE["probe_index"] += 1', probes)
        self.assertIn('STATE["probe_index"] >= len(PHASE2_PROBES)', probes)

    def test_driver_waits_for_pack_style_before_initializing_test_target_health(self):
        status = DRIVER.split("def pack_style_status", 1)[1].split("def wait_for_pack_style", 1)[0]
        wait = DRIVER.split("def wait_for_pack_style", 1)[1].split("def profile_report", 1)[0]
        spawn = DRIVER.split("def spawn_live_boss", 1)[1].split("def place_player_for_card", 1)[0]
        tick = DRIVER.split("def tick(delta_seconds)", 1)[1].split("def start()", 1)[0]
        self.assertIn("BP_CombatComponent_C", status)
        self.assertIn("CurrentCombatStyle", status)
        self.assertIn("CurrentCombatStyle_None", status)
        self.assertIn("elapsed >= 30.0", wait)
        self.assertIn("pack_style_status(pawn)", spawn)
        self.assertIn("wait_for_pack_style(pawn)", tick)
        self.assertLess(tick.index("wait_for_pack_style(pawn)"), tick.index("spawn_live_boss(world, pawn, profile)"))

    def test_locked_runner_covers_full_health_s1_then_half_health_s6(self):
        self.assertIn("DD27jManifestHash=$manifest", RUNNER)
        self.assertIn("Invoke-BoundedCardSelfTest 'S1' 'Move_Sevarog_Swing1_Medium' ''", RUNNER)
        self.assertIn("Invoke-BoundedCardSelfTest 'S6' 'Move_Sevarog_Ultimate_Swing_120fps_C1277' '0.5'", RUNNER)
        self.assertIn("PACK_STYLE_READY component=BP_CombatComponent_C", RUNNER)
        self.assertIn("${stage}_ORDER_VALID=$order", RUNNER)
        self.assertIn("$cardIndex -gt $spawnIndex", RUNNER)
        self.assertIn("CreateNew", RUNNER)
        self.assertIn("owner_token -eq $token", RUNNER)
        self.assertIn("NO_ASSET_SAVES=1", RUNNER)

    def test_verifier_is_tied_to_c1278_table_and_prints_evidence(self):
        self.assertIn("C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md", VERIFIER)
        for row in ("X26-P1", "X26-P2", "X26-S6", "X26-S7a", "X26-S7b", "X26-S8a", "X26-S8b"):
            self.assertIn(row, VERIFIER)
        self.assertIn("for line in row[\"evidence\"]", VERIFIER)
        self.assertIn("RESULT ", VERIFIER)


if __name__ == "__main__":
    unittest.main()
