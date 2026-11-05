"""Create an isolated F5 profile/map with dodge-rate aggro switching enabled."""
import unreal

DIR = "/Game/OneBossFight/FrameworkProof"
PROFILE_SRC = DIR + "/DA_Sevarog_SelectorProof_F5"
PROFILE_DST = DIR + "/DA_Sevarog_AggroSwitch_R13"
LEVEL_SRC = DIR + "/L_SevarogFrameworkProofF5"
LEVEL_DST = DIR + "/L_SevarogFrameworkProofAggroSwitchR13"

lib = unreal.EditorAssetLibrary
for path in (PROFILE_DST, LEVEL_DST):
    if lib.does_asset_exist(path):
        raise RuntimeError("destination exists; refusing to overwrite: " + path)
assert lib.duplicate_asset(PROFILE_SRC, PROFILE_DST), "profile duplicate failed"
profile = unreal.load_asset(PROFILE_DST)
profile.set_editor_property("aggro_enabled", True)
profile.set_editor_property("aggro_dodge_enter_rate", 0.6)
profile.set_editor_property("aggro_dodge_exit_rate", 0.3)
profile.set_editor_property("aggro_dodge_window_seconds", 5.0)
assert bool(profile.get_editor_property("aggro_enabled"))
assert float(profile.get_editor_property("aggro_dodge_enter_rate")) > float(profile.get_editor_property("aggro_dodge_exit_rate"))
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
unreal.log("[CODEX_AGGRO_SWITCH_R13] created profile/map; bAggroEnabled=1, enter=0.6, exit=0.3, window=5s")
