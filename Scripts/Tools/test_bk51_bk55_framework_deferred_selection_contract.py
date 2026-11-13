"""Offline source contracts for the BK-51..55 Sevarog deferred selection path."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class FrameworkDeferredSelectionContracts(unittest.TestCase):
    def read(self, path):
        return (ROOT / path).read_text(encoding="utf-8")

    def test_author_script_is_dry_run_by_default_and_never_overwrites(self):
        source = self.read("Scripts/Editor/author_framework_encounter_definition.py")
        self.assertIn("--write", source)
        self.assertIn("does_asset_exist", source)
        self.assertIn("DA_Sevarog_Framework_Encounter", source)
        self.assertIn('"use_framework_boss"', source)
        self.assertIn("stable_manifest_hash", source)
        self.assertIn("new_guid", source)
        self.assertIn("DRY_RUN", source)
        self.assertIn('READBACK = "--readback" in sys.argv', source)
        self.assertIn("def read_persisted", source)
        self.assertIn("[FrameworkEncounterAuthor] READBACK", source)
        self.assertIn('PHASE = "Phase_1"', source)
        self.assertIn('persisted["initial_boss_phase"] == PHASE', source)
        self.assertIn('persisted["framework_boss_profile"] == path(profile)', source)

    def test_deferred_activation_is_test_only_and_shipping_excluded(self):
        header = self.read("Source/OneBossFight/Player/RPGPlayerMovesSubsystem.h")
        implementation = self.read("Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp")
        self.assertIn("ActivateDeferredSelectionForTest", header)
        self.assertIn("#if !UE_BUILD_SHIPPING", implementation)
        self.assertIn("BuildWorldBindingForRebind", implementation)
        self.assertIn("ActivateDeferredSelectionForTest", implementation)
        boss = self.read("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp")
        self.assertIn("InitializeSelectedEncounterForTest", boss)
        selected_init = boss.split("bool ARPGFrameworkBossCharacter::InitializeSelectedEncounterForTest", 1)[1].split("bool ARPGFrameworkBossCharacter::InitializeWithProfileForTest", 1)[0]
        self.assertIn("Binding->ParticipantGeneration, Error, false, true)", selected_init)

    def test_live_driver_orders_pack_isolation_spawn_then_selector_trigger(self):
        source = self.read("Scripts/Editor/pie_sevarog_framework_live.py")
        isolate = source.index("isolate_ambient_encounter(world)")
        spawn_call = source.index("spawn_live_boss(world, pawn, profile)", isolate)
        spawn_api = source.index("spawn(world, cls, spawn_loc, spawn_rot)")
        trigger = source.index('"rpg.FrameworkEncounterSelection 1"')
        clear = source.index("clear_selection()", spawn_api)
        definition = source.index('"rpg.EncounterDefinition %s"', spawn_api)
        self.assertLess(isolate, spawn_call)
        self.assertLess(spawn_api, trigger)
        self.assertLess(clear, definition)
        self.assertLess(definition, trigger)
        self.assertIn("DA_Sevarog_Framework_Encounter", source)
        self.assertIn('SEVAROG_LIVE_DEFERRED_SELECTION") == "1"', source)
        self.assertIn("initialize_with_profile_for_test", source)

    def test_deferred_actor_reflection_uses_uobject_pointer_parameter(self):
        header = self.read("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.h")
        self.assertIn("InitializeSelectedEncounterForTest(const ARPGEncounterBinding* Binding", header)

    def test_bf_x05_receipt_requires_deferred_selection_witnesses(self):
        verifier = self.read("Scripts/Tools/verify_bf_x05_selected_route.py")
        tests = self.read("Scripts/Tools/test_bk3_bf_x05_verifier.py")
        self.assertIn("deferred_selection", verifier)
        self.assertIn("pack_isolated_before_spawn", verifier)
        self.assertIn("framework_spawn_before_selection", verifier)
        self.assertIn("deferred_selection", tests)


if __name__ == "__main__":
    unittest.main()
