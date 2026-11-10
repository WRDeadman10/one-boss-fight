"""Offline source contract for the Lead-run Sevarog authoring script."""
import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/Editor/author_sevarog_draft_cards.py"


class SevarogDraftAuthoringContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_authoring_scope_is_confined_to_project_data_allowlist(self):
        self.assertIn('PACKAGE_DIR = "/Game/OneBossFight/Data/Sevarog"', self.source)
        self.assertIn('startswith(PACKAGE_DIR + "/")', self.source)
        self.assertIn('SEVAROG_ROOT + "/"', self.source)
        self.assertIn("pack path is never a write target", self.source)
        for forbidden in ("duplicate_asset(", "delete_asset(", "rename_asset("):
            self.assertNotIn(forbidden, self.source)

    def test_all_five_sequences_use_same_sevarog_skeleton_and_marked_timings(self):
        self.assertEqual(self.source.count("/Animations/"), 7)  # five Sevarog clips plus two read-only player montages
        self.assertIn("/Meshes/Sevarog_Skeleton.Sevarog_Skeleton", self.source)
        self.assertIn("(0.467, 0.533, 0.667, 1.700)", self.source)
        self.assertIn("(0.200, 0.267, 1.133, 1.267)", self.source)
        self.assertIn("provisional, tune after PIE", self.source)

    def test_c1250_s3_s4_approved_values_and_no_unresolved_card_numbers(self):
        self.assertIn('"warp_max_distance_cm": 50.0', self.source)
        self.assertIn('"warp_max_distance_cm": 450.0', self.source)
        self.assertIn('"warp_end_seconds": 0.800', self.source)
        self.assertIn('"min_range_cm": 300.0', self.source)
        self.assertIn('"max_range_cm": 650.0', self.source)
        self.assertIn('"front_cone_degrees": 120.0', self.source)
        self.assertIn('"cooldown_seconds": 4.0', self.source)
        self.assertIn('"candidate_weight": 1.0', self.source)
        self.assertIn('"range_band_partition": True', self.source)
        self.assertIn('"warp_standoff_cm": 100.0', self.source)
        self.assertIn('"warp_standoff_cm": 120.0', self.source)
        self.assertIn('"combo_nodes": {"$runtime_combo": "S4_WHiff_S5_MEDIUM"}', self.source)
        self.assertIn('"Move_Sevarog_Swing1_Medium"', self.source)
        self.assertIn("profile_rows = rows[:4]", self.source)
        self.assertIn('"candidate_weight": 1.0', self.source)
        self.assertIn('"DA_Move_Sevarog_Speedburst_C1247"', self.source)
        self.assertIn("def validate_source_coverage(rows):", self.source)
        self.assertIn("def log_punish_estimates(rows):", self.source)
        self.assertIn("PUNISH_ESTIMATE", self.source)
        self.assertIn('if row["warp_away"] else row["warp_standoff_cm"]', self.source)
        self.assertIn("get_cpp_validation_bridge", self.source)
        self.assertIn("Editor-only C++ validation bridge is missing", self.source)
        main = next(node for node in self.tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
        main_text = ast.get_source_segment(self.source, main)
        self.assertLess(main_text.index("unresolved_gates(rows)"), main_text.index("get_cpp_validation_bridge"))
        self.assertLess(main_text.index("get_cpp_validation_bridge"), main_text.index("create_and_validate_assets"))

    def test_definition_profile_payloads_are_complete_with_field_provenance(self):
        self.assertIn('"use_montage_notify_timings": False', self.source)
        self.assertIn('"fixture_label": "F5 fixture"', self.source)
        self.assertIn('"punish_margin_seconds": 0.3', self.source)
        self.assertIn('PROFILE_FIELD_SOURCES = {', self.source)
        self.assertIn('DEFINITION_FIELD_SOURCES = {', self.source)
        self.assertIn("optional fields retain native C++ defaults", self.source)

    def test_cpp_diagnostics_are_printed_and_saves_only_follow_card_and_profile_validation(self):
        self.assertIn("VALIDATION ", self.source)
        self.assertIn("validate_card, validate_profile = bridge", self.source)
        self.assertIn("validate_card(card, loaded_assets[\"mesh\"])", self.source)
        self.assertIn("validate_profile(profile)", self.source)
        self.assertIn("no assets were saved", self.source)
        self.assertLess(self.source.index("validate_card(card"), self.source.index("save_loaded_asset("))
        self.assertLess(self.source.index("validate_profile(profile)"), self.source.index("save_loaded_asset("))
        self.assertIn('set_property(definition, "use_montage_notify_timings", False)', self.source)

    def test_cpp_bridge_is_editor_only_and_calls_runtime_validation(self):
        header = (ROOT / "Source/OneBossFightEditor/Public/RPGBossCardValidationLibrary.h").read_text(encoding="utf-8")
        source = (ROOT / "Source/OneBossFightEditor/Private/RPGBossCardValidationLibrary.cpp").read_text(encoding="utf-8")
        build_cs = (ROOT / "Source/OneBossFightEditor/OneBossFightEditor.Build.cs").read_text(encoding="utf-8")
        self.assertIn("UFUNCTION(BlueprintCallable", header)
        self.assertIn("ValidateMoveCard", header)
        self.assertIn("ValidateFrameworkProfile", header)
        self.assertIn("ValidateMoveCardReport", header)
        self.assertIn("ValidateFrameworkProfileReport", header)
        self.assertIn('getattr(library, "validate_move_card_report", None)', self.source)
        self.assertIn("RPGBossMoveCards::CompileResolved", source)
        self.assertIn("RPGFramework::ResolveProfile", source)
        target = (ROOT / "Source/OneBossFightEditor.Target.cs").read_text(encoding="utf-8")
        self.assertIn('ExtraModuleNames.Add("OneBossFightEditor")', target)
        self.assertIn('"OneBossFight"', build_cs)

    def test_combo_types_are_python_reflectable_and_forward_counterplay_uses_standoff(self):
        profile_header = (ROOT / "Source/OneBossFight/Player/RPGBossFrameworkProfile.h").read_text(encoding="utf-8")
        defense_header = (ROOT / "Source/OneBossFight/Player/RPGBossDefenseRules.h").read_text(encoding="utf-8")
        profile_source = (ROOT / "Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp").read_text(encoding="utf-8")
        native_test = (ROOT / "Source/OneBossFight/Tests/RPGBossDefenseTests.cpp").read_text(encoding="utf-8")
        self.assertIn("USTRUCT(BlueprintType)\nstruct FRPGBossComboEdgeData", profile_header)
        self.assertIn("USTRUCT(BlueprintType)\nstruct FRPGBossComboNodeData", profile_header)
        self.assertIn("UENUM(BlueprintType)", profile_header)
        self.assertIn("BlueprintReadWrite", profile_header)
        self.assertIn("EndDistanceCm=bWarpAway?CardMaxRangeCm+BackstepCm:WarpStandoffCm", defense_header)
        self.assertIn("double(S.WarpStandoffCm),S.bWarpAway,After,Moves", profile_source)
        self.assertIn("backstep margin remains 0.75 - 0.6833", native_test)
        self.assertIn("forward warp counterplay starts at its standoff", native_test)

    def test_dry_run_uses_transient_objects_and_complete_validator_path(self):
        self.assertIn('"RPGBossComboEdgeData": ("RpgBossComboEdgeData",)', self.source)
        self.assertIn('def dry_run(unreal_module, rows, bridge):', self.source)
        self.assertIn('"--dry-run" in sys.argv', self.source)
        self.assertIn("DRY-RUN COMPLETE all validators passed, 0 saved", self.source)
        dry_run = next(node for node in self.tree.body if isinstance(node, ast.FunctionDef) and node.name == "dry_run")
        dry_run_text = ast.get_source_segment(self.source, dry_run)
        self.assertIn("new_object(card_class)", dry_run_text)
        self.assertIn("new_object(profile_class)", dry_run_text)
        self.assertIn("new_object(definition_class)", dry_run_text)
        self.assertIn("validate_card(created[row[\"move_id\"]]", dry_run_text)
        self.assertIn("validate_profile(profile)", dry_run_text)
        self.assertNotIn("create_asset(", dry_run_text)
        self.assertNotIn("save_loaded_asset(", dry_run_text)
        self.assertIn("VALIDATOR framework_profile verdict=", dry_run_text)
        self.assertIn("authoritative punish_check and defense_check numbers", dry_run_text)
        self.assertIn("clamp_marked_recovery_to_clip(rows, loaded_assets)", dry_run_text)
        self.assertIn("TIMING_CLAMP", self.source)
        profile_header = (ROOT / "Source/OneBossFight/Player/RPGBossFrameworkProfile.h").read_text(encoding="utf-8")
        move_header = (ROOT / "Source/OneBossFight/Player/RPGBossMoveCard.h").read_text(encoding="utf-8")
        self.assertIn("USTRUCT(BlueprintType)\nstruct FRPGBossProfileCard", profile_header)
        self.assertIn("USTRUCT(BlueprintType)\nstruct FRPGBossMoveWindow", move_header)
        self.assertIn("USTRUCT(BlueprintType)\nstruct FRPGBossMoveCardSpec", move_header)
        self.assertRegex(profile_header, r"UPROPERTY\(EditAnywhere, BlueprintReadWrite\) TArray<FRPGBossProfileCard> Cards;")
        self.assertRegex(profile_header, r"UPROPERTY\(EditAnywhere, BlueprintReadWrite\) TArray<FRPGBossComboNodeData> ComboNodes;")

    def test_native_bridge_test_covers_positive_and_runtime_token_parity(self):
        test = (ROOT / "Source/OneBossFightEditor/Private/Tests/RPGBossCardValidationBridgeTests.cpp").read_text(encoding="utf-8")
        self.assertIn("valid synthetic card passes", test)
        self.assertIn("non-defensive card without a window fails", test)
        self.assertIn("MoveCard.Window", test)

    def test_forward_defense_requires_positive_distance_even_with_turn_budget(self):
        source = (ROOT / "Source/OneBossFight/Player/RPGBossMoveCard.cpp").read_text(encoding="utf-8")
        tests = (ROOT / "Source/OneBossFight/Tests/RPGBossMoveCardTests.cpp").read_text(encoding="utf-8")
        self.assertIn("!S.bWarpAway && !(S.WarpMaxDistanceCm > 0.f)", source)
        self.assertIn("WarpMaxDistanceCm=0.f;F.S.WarpMaxAngleDegrees=30.f", tests)
        self.assertIn("forward defensive reposition with positive distance is valid", tests)

    def test_no_selection_asset_is_written_by_this_script(self):
        self.assertNotIn("DA_Sevarog_G044_Encounter", self.source)
        self.assertNotIn('"selected"', self.source)
        self.assertIn('DEFINITION_NAME = "DA_Boss_Sevarog_Draft"', self.source)
        self.assertIn('PROFILE_NAME = "DA_Boss_Sevarog_FrameworkProfile_Draft"', self.source)


if __name__ == "__main__":
    unittest.main()
