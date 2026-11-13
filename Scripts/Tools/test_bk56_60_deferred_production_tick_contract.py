"""Offline contracts for BK-56..60 deferred production-selector Tick path."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEST_START_APIS = ("start_card_for_test", "start_combo_for_test", "start_selected_card_for_test")


class DeferredProductionTickContracts(unittest.TestCase):
    def read(self, path):
        return (ROOT / path).read_text(encoding="utf-8")

    def test_deferred_initialization_enables_production_tick_not_test_start_mode(self):
        source = self.read("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp")
        start = source.index("bool ARPGFrameworkBossCharacter::InitializeSelectedEncounterForTest")
        end = source.index("bool ARPGFrameworkBossCharacter::InitializeWithProfileForTest", start)
        selected_init = source[start:end]
        self.assertIn("Binding->ParticipantGeneration, Error, false, true)", selected_init)
        self.assertIn("bSelectedRouteInitialized=bAllowSelectedRoute", source)
        self.assertIn("ProofFixture.IsValid()||bTestInitialized||bSelectedRouteInitialized", source)
        tick = source[source.index("void ARPGFrameworkBossCharacter::Tick(float Delta)"):]
        self.assertIn("if(bTestInitialized)return;", tick)
        self.assertLess(tick.index("if(bTestInitialized)return;"), tick.index("Selector.Select(Executor->Model(),S,Decision,Pattern)"))

    def test_passive_deferred_observer_has_no_test_start_api_calls(self):
        source = self.read("Scripts/Editor/pie_sevarog_framework_live.py")
        start = source.index("def tick_deferred_selector(")
        end = source.index("def live_world(", start)
        observer = source[start:end]
        for api in TEST_START_APIS:
            self.assertNotIn(api, observer)
        self.assertIn("get_outcome_for_test()", observer)
        self.assertIn("DEFERRED_TICK_RESULT", observer)

    def test_deferred_spawn_branch_has_no_test_start_calls(self):
        source = self.read("Scripts/Editor/pie_sevarog_framework_live.py")
        start = source.index("def spawn_live_boss(")
        end = source.index("def place_player_for_card(", start)
        spawn = source[start:end]
        deferred_start = spawn.index('if os.environ.get("SEVAROG_LIVE_DEFERRED_SELECTION") == "1":')
        deferred_end = spawn.index("    else:", deferred_start)
        deferred_branch = spawn[deferred_start:deferred_end]
        for api in TEST_START_APIS:
            self.assertNotIn(api, deferred_branch)
        self.assertIn("activate()", deferred_branch)
        self.assertIn("get_selection_diagnostic", deferred_branch)
        self.assertIn("build_encounter_parity_snapshot", deferred_branch)
        self.assertIn("outcome=ActivationRefused", deferred_branch)

    def test_tick_selects_passive_deferred_monitor_before_test_start_paths(self):
        source = self.read("Scripts/Editor/pie_sevarog_framework_live.py")
        start = source.index("def tick(delta_seconds):")
        end = source.index("def ", start + 5)
        tick = source[start:end]
        deferred_branch = tick.index('if os.environ.get("SEVAROG_LIVE_DEFERRED_SELECTION") == "1":')
        deferred_call = tick.index("tick_deferred_selector(world, boss, now)", deferred_branch)
        deferred_return = tick.index("return", deferred_call)
        self.assertLess(deferred_branch, deferred_call)
        self.assertLess(deferred_call, deferred_return)
        self.assertLess(deferred_return, tick.index("tick_autonomous_selector(world, boss, now)"))
        self.assertLess(deferred_return, tick.index("boss.start_card_for_test(move_id)"))
        self.assertLess(deferred_return, tick.index("boss.start_combo_for_test(move_id)"))

    def test_test_health_override_is_refused_for_deferred_live_route(self):
        source = self.read("Scripts/Editor/pie_sevarog_framework_live.py")
        start = source.index("def apply_test_health_fraction(")
        end = source.index("def ", start + 5)
        function = source[start:end]
        self.assertIn("if os.environ.get(\"SEVAROG_LIVE_DEFERRED_SELECTION\") == \"1\":", function)
        self.assertIn("test boss-health override is forbidden", function)

    def test_failed_selection_snapshot_uses_pending_request_not_stale_active_fields(self):
        source = self.read("Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp")
        start = source.index("FString URPGPlayerMovesSubsystem::BuildEncounterParitySnapshot() const")
        end = source.index("\nvoid URPGPlayerMovesSubsystem::", start + 8)
        snapshot = source[start:end]
        self.assertIn('Selection->SetBoolField(TEXT("active_binding"), bHasBinding)', snapshot)
        self.assertIn('Selection->SetBoolField(TEXT("request_pending"), !bHasBinding && bHasRequest)', snapshot)
        self.assertIn("Store->GetRequestedDefinitionPathForDiagnostics()", snapshot)
        self.assertIn("Store->GetRequestedManifestHashForDiagnostics()", snapshot)
        self.assertIn("Store->GetRequestedInitialBossPhaseForDiagnostics()", snapshot)
        self.assertNotIn("LastEncounterManifestHash);", snapshot)
        self.assertNotIn("ActiveBossPhase.ToString()", snapshot)

    def test_task_runner_enforces_c1155_and_receipt_gates(self):
        runner = self.read("Scripts/Editor/run_bk56_60_deferred_selection.ps1")
        for lock in ("ENGINE_LOCK.json", "Docs\\BossCombatReview\\Execution\\ENGINE_LOCK.json"):
            self.assertIn(lock, runner)
        self.assertIn("Get-Process UnrealEditor*", runner)
        self.assertIn("CreateNew", runner)
        self.assertIn("owner_token", runner)
        self.assertIn("cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec", runner)
        self.assertIn("-nosound", runner)
        self.assertIn("FRAMEWORK_ENCOUNTER_WRITE", runner)
        self.assertIn("SEVAROG_LIVE_DEFERRED_SELECTION", runner)
        self.assertIn("content_asset_delta.txt", runner)
        self.assertIn("HEALTH_BASELINE_AFTER_PACK_STYLE_READY", runner)
        self.assertIn("DA_Boss_Sevarog_Draft.before.uasset", runner)
        self.assertIn("DA_Boss_Sevarog_Draft", runner)
        phase_author = self.read("Scripts/Editor/ensure_bk56_60_sevarog_initial_phase.py")
        self.assertIn("if PHASE_ID in ids", phase_author)
        self.assertIn('save_loaded_asset(boss)', phase_author)
        self.assertIn('BK56_AUTHOR_PHASE_WRITE', phase_author)

    def test_phase_prerequisite_refuses_unsourced_defaults_and_invalid_present_rows(self):
        source = self.read("Scripts/Editor/ensure_bk56_60_sevarog_initial_phase.py")
        self.assertIn('"BK56_PHASE_ENTRY_HEALTH_FRACTION"', source)
        self.assertIn('"BK56_PHASE_SPEED_MULTIPLIER"', source)
        self.assertIn('"BK56_PHASE_RATE_MULTIPLIER"', source)
        self.assertIn('"BK56_PHASE_ATTACK_MULTIPLIER"', source)
        self.assertIn("authoring defaults are not Sevarog evidence", source)
        self.assertIn("validate_values(values)", source)
        self.assertNotIn('"entry_health_fraction", 0.0', source)
        self.assertNotIn('"speed_multiplier", 1.0', source)

    def test_runner_order_matches_synchronous_activation_before_navigation_pass(self):
        runner = self.read("Scripts/Editor/run_bk56_60_deferred_selection.ps1")
        self.assertIn("$routeInit -gt $packReady", runner)
        self.assertIn("$activation -gt $routeInit", runner)
        self.assertIn("$spawn -gt $activation", runner)
        self.assertIn("$decision -gt $activation", runner)
        self.assertIn("$decision -lt $result", runner)
        self.assertIn("$monitor -gt $spawn", runner)
        self.assertIn("$result -gt $monitor", runner)
        driver = self.read("Scripts/Editor/pie_sevarog_framework_live.py")
        spawn_start = driver.index("def spawn_live_boss(")
        spawn_end = driver.index("def place_player_for_card(", spawn_start)
        spawn_block = driver[spawn_start:spawn_end]
        nav_start = driver.index("def validate_spawn_navigation(")
        nav_end = driver.index("def place_player_at_distance(", nav_start)
        nav_block = driver[nav_start:nav_end]
        self.assertIn("DEFERRED_SELECTION route=framework", spawn_block)
        self.assertIn("SPAWN PASS actor=", nav_block)
        tick = driver[driver.index("def tick(delta_seconds):"):]
        spawn_call = tick.index("boss = spawn_live_boss(world, pawn, profile)")
        spawn_return = tick.index("return", spawn_call)
        nav_check = tick.index("if not validate_spawn_navigation(boss, profile, pawn, now):")
        self.assertLess(spawn_call, spawn_return)
        self.assertLess(spawn_return, nav_check)


if __name__ == "__main__":
    unittest.main()
