"""Create an isolated F5 profile/map with consecutive-whiff fatigue enabled."""
import unreal

DIR = "/Game/OneBossFight/FrameworkProof"
PROFILE_SRC = DIR + "/DA_Sevarog_SelectorProof_F5"
PROFILE_DST = DIR + "/DA_Sevarog_Fatigue_R15A6"
LEVEL_SRC = DIR + "/L_SevarogFrameworkProofF5"
LEVEL_DST = DIR + "/L_SevarogFrameworkProofFatigueR15A6"

lib = unreal.EditorAssetLibrary
for path in (PROFILE_DST, LEVEL_DST):
    if lib.does_asset_exist(path):
        raise RuntimeError("destination exists; refusing to overwrite: " + path)
assert lib.duplicate_asset(PROFILE_SRC, PROFILE_DST), "profile duplicate failed"
profile = unreal.load_asset(PROFILE_DST)
profile.set_editor_property("fatigue_grace_whiffs", 1)
profile.set_editor_property("fatigue_floor", 0.5)
profile.set_editor_property("attack_count", 6)
entries = list(profile.get_editor_property("cards"))
if not entries:
    raise RuntimeError("profile has no candidate card entries")
for entry in entries:
    entry.set_editor_property("cooldown_seconds", 0.0)
profile.set_editor_property("cards", entries)
assert int(profile.get_editor_property("fatigue_grace_whiffs")) == 1
assert abs(float(profile.get_editor_property("fatigue_floor")) - 0.5) < 1e-6
assert int(profile.get_editor_property("attack_count")) == 6
saved_entries = list(profile.get_editor_property("cards"))
if not saved_entries or any(abs(float(e.get_editor_property("cooldown_seconds"))) > 1e-4 for e in saved_entries):
    raise RuntimeError("candidate cooldown readback mismatch")
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
unreal.log("[CODEX_FATIGUE_R15A6] created profile/map with graceWhiffs=1, floor=0.5, attackCount=6")
