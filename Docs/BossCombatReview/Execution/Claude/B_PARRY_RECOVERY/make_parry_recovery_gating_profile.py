"""Create an isolated PARRY proof map/profile for observing recovery gating."""
import unreal

DIR = "/Game/OneBossFight/FrameworkProof"
PROFILE_SRC = DIR + "/DA_Sevarog_ParryReaction_PARRY"
PROFILE_DST = DIR + "/DA_Sevarog_ParryRecovery_Gating_A4"
LEVEL_SRC = DIR + "/L_SevarogFrameworkProofPARRY"
LEVEL_DST = DIR + "/L_SevarogFrameworkProofParryRecoveryA4"

lib = unreal.EditorAssetLibrary
for path in (PROFILE_DST, LEVEL_DST):
    if lib.does_asset_exist(path):
        raise RuntimeError("destination exists; refusing to overwrite: " + path)
assert lib.duplicate_asset(PROFILE_SRC, PROFILE_DST), "profile duplicate failed"
profile = unreal.load_asset(PROFILE_DST)
profile.set_editor_property("parry_recovery_scale", 1.0)
profile.set_editor_property("parry_posture_amount", 0.0)
profile.set_editor_property("parry_grade_scale", False)
profile.set_editor_property("attack_count", 4)
assert abs(float(profile.get_editor_property("parry_recovery_scale")) - 1.0) < 1e-6
assert float(profile.get_editor_property("parry_posture_amount")) == 0.0
assert not bool(profile.get_editor_property("parry_grade_scale"))
assert int(profile.get_editor_property("attack_count")) == 4
assert lib.save_loaded_asset(profile)

# Load the source world and save it under a new name. Duplicating then loading a .umap crashes this editor.
assert unreal.EditorLevelLibrary.load_level(LEVEL_SRC), "source proof map load failed"
fixtures = [a for a in unreal.EditorLevelLibrary.get_all_level_actors()
            if a.get_class().get_name() == "RPGFrameworkProofFixture"]
if len(fixtures) != 1:
    raise RuntimeError("expected one framework proof fixture, got %d" % len(fixtures))
fixtures[0].set_editor_property("profile", profile)
assert fixtures[0].get_editor_property("profile").get_path_name() == profile.get_path_name()
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(world, LEVEL_DST), "save_map under the new name failed"
unreal.log("[CODEX_PARRY_RECOVERY_GATING_A4] profile/map created; scale=1 posture=0 gradeScale=0 attack_count=4")
