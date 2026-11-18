"""Contract test for author_production_framework_profile.py."""
import importlib.util
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/Editor/author_production_framework_profile.py"


class ProductionFrameworkProfileContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding="utf-8")
        spec = importlib.util.spec_from_file_location("author_prod_profile", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_target_health_is_mandatory_with_no_default(self):
        # Missing argument and missing env var must fail closed
        with self.assertRaises(self.module.Refusal) as ctx:
            self.module.parse_target_health(argv=[], environ={})
        self.assertIn("TargetHealth is mandatory and has no default value", str(ctx.exception))

    def test_target_health_rejects_invalid_values(self):
        # Reject zero
        with self.assertRaises(self.module.Refusal) as ctx:
            self.module.parse_target_health(argv=["--target-health", "0"], environ={})
        self.assertIn("positive finite float", str(ctx.exception))

        # Reject negative
        with self.assertRaises(self.module.Refusal) as ctx:
            self.module.parse_target_health(argv=["--target-health", "-100"], environ={})
        self.assertIn("positive finite float", str(ctx.exception))

        # Reject NaN
        with self.assertRaises(self.module.Refusal) as ctx:
            self.module.parse_target_health(argv=["--target-health", "nan"], environ={})
        self.assertIn("positive finite float", str(ctx.exception))

        # Reject non-numeric
        with self.assertRaises(self.module.Refusal) as ctx:
            self.module.parse_target_health(argv=["--target-health", "abc"], environ={})
        self.assertIn("must be numeric", str(ctx.exception))

    def test_target_health_accepts_positive_finite_floats(self):
        val = self.module.parse_target_health(argv=["--target-health", "800.0"], environ={})
        self.assertEqual(val, 800.0)

        val_eq = self.module.parse_target_health(argv=["--target-health=800.0"], environ={})
        self.assertEqual(val_eq, 800.0)

        val_env = self.module.parse_target_health(argv=[], environ={"SEVAROG_TARGET_HEALTH": "800.0"})
        self.assertEqual(val_env, 800.0)

        val_arg = self.module.parse_target_health(target_health_arg=800.0)
        self.assertEqual(val_arg, 800.0)

        # Deviating values must fail closed against owner approval
        with self.assertRaises(self.module.Refusal) as ctx:
            self.module.parse_target_health(argv=["--target-health=100.0"], environ={})
        self.assertIn("does not match owner-approved production value", str(ctx.exception))

        with self.assertRaises(self.module.Refusal) as ctx:
            self.module.parse_target_health(environ={"SEVAROG_TARGET_HEALTH": "500"})
        self.assertIn("does not match owner-approved production value", str(ctx.exception))

    def test_production_card_specs_and_soft_references(self):
        specs = self.module.PRODUCTION_CARD_SPECS
        self.assertEqual(len(specs), 7)
        card_names = [s[0] for s in specs]
        self.assertIn("DA_Move_Sevarog_Swing1_Medium_C1247", card_names)
        self.assertIn("DA_Move_Sevarog_Swing2_Medium_C1247", card_names)
        self.assertIn("DA_Move_Sevarog_Swing3_Slow_C1247", card_names)
        self.assertIn("DA_Move_Sevarog_Speedburst_C1247", card_names)
        self.assertIn("DA_Move_Sevarog_Ultimate_Swing_120fps_C1277", card_names)
        self.assertIn("DA_Move_Sevarog_Subjugation_C1277", card_names)
        self.assertIn("DA_Move_Sevarog_Soul_Siphon_C1277", card_names)

        o1 = self.module.load_o1_values(ROOT)
        payload = self.module.build_profile_payload(o1, target_health=800.0)
        self.assertIn("$soft_object", payload["mesh"])
        self.assertIn("$soft_class", payload["anim_class"])
        self.assertIn("$soft_class", payload["target_pawn_class"])
        self.assertIn("$soft_object", payload["player_light_montage"])
        self.assertIn("$soft_object", payload["player_heavy_montage"])
        self.assertEqual(payload["combo_root"], "S4")
        self.assertIn("$runtime_combo", payload["combo_nodes"])

    def test_set_property_fails_closed_on_error(self):
        class FailingObj:
            def set_editor_property(self, name, value):
                raise RuntimeError("Engine rejection: property readonly or missing")

        with self.assertRaises(self.module.Refusal) as ctx:
            self.module.set_property(FailingObj(), "test_prop", 123)
        self.assertIn("Property write failed for test_prop", str(ctx.exception))

    def test_transient_validation_and_readback_wiring(self):
        self.assertIn("transient_profile = unreal.new_object(profile_class)", self.source)
        self.assertIn("apply_properties_to_profile(unreal, transient_profile, payload)", self.source)
        self.assertIn("verify_profile_readback(unreal, reloaded_asset, payload, validate_profile)", self.source)
        self.assertIn("def verify_profile_readback(", self.source)
        self.assertIn("def approved_float_matches(actual, expected, tol=1e-4):", self.source)
        self.assertIn("require(approved_float_matches(val, expected)", self.source)

    def test_approved_float_matches_contract(self):
        fn = self.module.approved_float_matches
        self.assertTrue(fn(0.10000000149011612, 0.1))
        self.assertTrue(fn(0.6000000238418579, 0.6))
        self.assertTrue(fn(13.00005, 13.0))
        self.assertFalse(fn(13.00015, 13.0))
        self.assertFalse(fn(float("nan"), 0.1))
        self.assertFalse(fn(float("inf"), 0.1))
        self.assertFalse(fn("not-a-number", 0.1))

    def test_receipt_emission_order_and_guard(self):
        self.assertIn("def write_receipt_file(receipt):", self.source)
        write_idx = self.source.index("def write_receipt_file(")
        main_idx = self.source.index("def main(")
        self.assertLess(write_idx, main_idx)
        self.assertIn("write_receipt_file(receipt)\n        print(\"[ProductionProfileAuthor] OFFLINE_RECEIPT:", self.source)
        self.assertIn("write_receipt_file(receipt)\n        unreal.log(\"[ProductionProfileAuthor] READBACK_PASS", self.source)
        self.assertIn("write_receipt_file(receipt)\n        unreal.log(\"[ProductionProfileAuthor] DRY_RUN_PASS", self.source)
        self.assertIn("write_receipt_file(receipt)\n    unreal.log(\"[ProductionProfileAuthor] WRITTEN_PASS", self.source)

    def test_o1_values_match_owner_approved_decisions(self):
        o1 = self.module.load_o1_values(ROOT)
        self.assertEqual(float(o1["Stats.MaxHealth"]), 1500.0)
        self.assertEqual(float(o1["Stats.MaxPosture"]), 100.0)
        self.assertEqual(float(o1["Stats.PostureRegenDelay"]), 6.0)
        self.assertEqual(float(o1["Stats.PostureRegenRate"]), 13.0)
        self.assertEqual(float(o1["Phases[Phase_1].EntryHealthFraction"]), 0.6)

    def test_load_o1_values_enforces_exact_approved_values(self):
        # Exact approved values table must match DECISIONS.md exactly
        expected = self.module.EXACT_APPROVED_O1_VALUES
        self.assertEqual(expected["Stats.MaxHealth"], 1500.0)
        self.assertEqual(expected["Stats.MaxPosture"], 100.0)
        self.assertEqual(expected["Stats.PostureRegenDelay"], 6.0)
        self.assertEqual(expected["Stats.PostureRegenRate"], 13.0)
        self.assertEqual(expected["Phases[Phase_1].EntryHealthFraction"], 0.6)

    def test_native_production_identity_branch_contract(self):
        cpp_path = ROOT / "Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp"
        cpp_source = cpp_path.read_text(encoding="utf-8")
        self.assertIn('bProd=P.FixtureLabel==TEXT("Production")', cpp_source)
        self.assertIn('const bool bSelector=bF5||bProd;', cpp_source)
        self.assertIn('if (!(bF3||bF4||bSelector)', cpp_source)
        self.assertIn('if (P.bRangeBandPartition && !bSelector)', cpp_source)
        self.assertIn('if (!bSelector || P.BossMaxHealth<=0.f', cpp_source)

        tests_cpp_path = ROOT / "Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp"
        tests_cpp_source = tests_cpp_path.read_text(encoding="utf-8")
        self.assertIn('FFrameworkProductionProfile', tests_cpp_source)
        self.assertIn('P->FixtureLabel=TEXT("Production")', tests_cpp_source)

    def test_full_readback_property_and_card_coverage(self):
        self.assertIn('scalar_fields = (', self.source)
        self.assertIn('"fixture_label"', self.source)
        self.assertIn('"boss_max_health"', self.source)
        self.assertIn('"target_health"', self.source)
        self.assertIn('"posture_max"', self.source)
        self.assertIn('"posture_regen_delay_seconds"', self.source)
        self.assertIn('"posture_regen_per_second"', self.source)
        self.assertIn('"phase_two_fraction"', self.source)
        self.assertIn('"phase_two_id"', self.source)
        self.assertIn('soft_ref_fields = (', self.source)
        self.assertIn('"mesh"', self.source)
        self.assertIn('"anim_class"', self.source)
        self.assertIn('"target_pawn_class"', self.source)
        self.assertIn('"player_light_montage"', self.source)
        self.assertIn('"player_heavy_montage"', self.source)
        self.assertIn('for i, (spec_name, spec_cooldown, spec_weight) in enumerate(PRODUCTION_CARD_SPECS):', self.source)
        self.assertIn('"cooldown_seconds"', self.source)
        self.assertIn('"hyper_armor"', self.source)
        self.assertIn('"kite_weight_multiplier"', self.source)
        self.assertIn('"heavy_finisher"', self.source)
        self.assertIn('mesh_relative_transform', self.source)
        self.assertIn('"combo_nodes"', self.source)
        self.assertIn('expected_card_path = PACKAGE_DIR + "/" + spec_name + "." + spec_name', self.source)
        self.assertIn('require(actual_path == expected_path', self.source)
        self.assertIn('raise Refusal("mesh_relative_transform rotation has unknown/unsupported type:', self.source)
        self.assertIn('match_direct = (abs(qx) < 1e-4 and abs(qy) < 1e-4', self.source)

    def test_profile_payload_applies_o1_and_preserves_f5_fixture(self):
        o1 = self.module.load_o1_values(ROOT)
        payload = self.module.build_profile_payload(o1, target_health=800.0)
        self.assertEqual(payload["boss_max_health"], 1500.0)
        self.assertEqual(payload["posture_max"], 100.0)
        self.assertEqual(payload["posture_regen_delay_seconds"], 6.0)
        self.assertEqual(payload["posture_regen_per_second"], 13.0)
        self.assertEqual(payload["player_posture_hit_amount"], 60.0)
        self.assertEqual(payload["stagger_seconds"], 2.5)
        self.assertEqual(payload["phase_two_fraction"], 0.6)
        self.assertEqual(payload["phase_two_id"], "Phase_2")
        self.assertEqual(payload["fixture_label"], "Production")
        self.assertEqual(payload["target_health"], 800.0)
        self.assertTrue(payload["damage_enabled"])

    def test_safety_invariants_and_path_separation(self):
        self.assertIn('PROFILE_NAME = "DA_Boss_Sevarog_FrameworkProfile_Production"', self.source)
        self.assertIn('F5_FIXTURE_PATH = PACKAGE_DIR + "/DA_Boss_Sevarog_FrameworkProfile_Draft"', self.source)
        self.assertIn('ENCOUNTER_PATH = PACKAGE_DIR + "/DA_Sevarog_Framework_Encounter"', self.source)
        self.assertIn('require(ASSET_PATH != F5_FIXTURE_PATH', self.source)
        self.assertIn('require(ASSET_PATH != ENCOUNTER_PATH', self.source)
        self.assertNotIn("/Game/AdvancedARPGCombat", self.module.ASSET_PATH)
        self.assertEqual(self.module.ASSET_PATH, "/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_FrameworkProfile_Production")

    def test_encounter_payload_and_canonical_hash_contract(self):
        enc_payload = self.module.build_encounter_payload()
        self.assertEqual(enc_payload["schema"], 1)
        self.assertEqual(enc_payload["boss_slot"], "Boss")
        self.assertEqual(enc_payload["player_slot"], "Player")
        self.assertEqual(enc_payload["initial_boss_phase"], "Phase_1")
        self.assertEqual(enc_payload["boss_definition"], "/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_Draft")
        self.assertEqual(enc_payload["player_definition"], "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft_V3")
        self.assertTrue(enc_payload["use_framework_boss"])
        self.assertEqual(enc_payload["framework_boss_profile"], self.module.ASSET_PATH)

        enc_hash = self.module.compute_encounter_manifest_hash(enc_payload)
        self.assertEqual(enc_hash, "62ecc592e0c2ad57ec0b5d70afd56ba7ea1dc7f9d0fd1dc7a3fc1b625ac6d305")

        self.assertIn("def verify_encounter_readback(", self.source)
        self.assertIn("Encounter stable_manifest_hash mismatch", self.source)
        self.assertIn("Encounter framework_boss_profile path mismatch", self.source)
        self.assertIn("rebind_encounter", self.source)


if __name__ == "__main__":
    unittest.main()
