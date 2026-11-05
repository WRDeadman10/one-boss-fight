"""Create an isolated long yaw/cone proof profile with eight attack decisions."""
import unreal

DIR = "/Game/OneBossFight/FrameworkProof"
PROFILE_SRC = DIR + "/DA_Sevarog_SelectorProof_F5"
PROFILE_DST = DIR + "/DA_Sevarog_YawCone_R6A8"
LEVEL_SRC = DIR + "/L_SevarogFrameworkProofF5"
LEVEL_DST = DIR + "/L_SevarogFrameworkProofYawConeR6A8"

lib = unreal.EditorAssetLibrary
for path in (PROFILE_DST, LEVEL_DST):
    if lib.does_asset_exist(path):
        raise RuntimeError("destination exists; refusing to overwrite: " + path)
assert lib.duplicate_asset(PROFILE_SRC, PROFILE_DST), "profile duplicate failed"
profile = unreal.load_asset(PROFILE_DST)
profile.set_editor_property("cone_hysteresis_degrees", 6.0)
profile.set_editor_property("attack_count", 8)
assert float(profile.get_editor_property("cone_hysteresis_degrees")) == 6.0
assert int(profile.get_editor_property("attack_count")) == 8
assert lib.save_loaded_asset(profile)

assert unreal.EditorLevelLibrary.load_level(LEVEL_SRC), "source proof map load failed"
fixtures = [a for a in unreal.EditorLevelLibrary.get_all_level_actors()
            if a.get_class().get_name() == "RPGFrameworkProofFixture"]
if len(fixtures) != 1:
    raise RuntimeError("expected one framework proof fixture, got %d" % len(fixtures))
fixtures[0].set_editor_property("profile", profile)
assert fixtures[0].get_editor_property("profile").get_path_name() == profile.get_path_name()
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(world, LEVEL_DST), "save_map under the new name failed"
unreal.log("[CODEX_YAW_CONE_R6A8] created profile/map with ConeHysteresisDegrees=6 and AttackCount=8")
