"""Create an isolated WarpEaseInOut proof profile, card, and map; never overwrite assets."""
import unreal

DIR = "/Game/OneBossFight/FrameworkProof"
CARD_SRC = DIR + "/Cards/Move_Sevarog_HeavyWarp_ANM006"
CARD_DST = DIR + "/Cards/Move_Sevarog_HeavyWarp_EASE_R1"
PROFILE_SRC = DIR + "/DA_Sevarog_Warp_ANM006"
PROFILE_DST = DIR + "/DA_Sevarog_WarpEase_R1"
LEVEL_SRC = DIR + "/L_SevarogFrameworkProofANM006"
LEVEL_DST = DIR + "/L_SevarogFrameworkProofWarpEaseR1"

lib = unreal.EditorAssetLibrary
for path in (CARD_DST, PROFILE_DST, LEVEL_DST):
    if lib.does_asset_exist(path):
        raise RuntimeError("destination exists; refusing to overwrite: " + path)

assert lib.duplicate_asset(CARD_SRC, CARD_DST), "card duplicate failed"
card = unreal.load_asset(CARD_DST)
spec = card.get_editor_property("spec")
if bool(spec.get_editor_property("warp_ease_in_out")):
    raise RuntimeError("source card already has WarpEaseInOut enabled")
if float(spec.get_editor_property("warp_max_distance_cm")) <= 0.0:
    raise RuntimeError("source card has no positive warp distance budget")
spec.set_editor_property("warp_ease_in_out", True)
card.set_editor_property("spec", spec)
assert bool(card.get_editor_property("spec").get_editor_property("warp_ease_in_out"))
assert lib.save_loaded_asset(card)

assert lib.duplicate_asset(PROFILE_SRC, PROFILE_DST), "profile duplicate failed"
profile = unreal.load_asset(PROFILE_DST)
entries = list(profile.get_editor_property("cards"))
replaced = 0
for entry in entries:
    old = entry.get_editor_property("card")
    if old and old.get_path_name() == unreal.load_asset(CARD_SRC).get_path_name():
        entry.set_editor_property("card", card)
        replaced += 1
if replaced != 1:
    raise RuntimeError("expected exactly one source card reference, got %d" % replaced)
profile.set_editor_property("cards", entries)
assert lib.save_loaded_asset(profile)

# lead change: a duplicated map crashed the editor on load before (world GC leak): load the SOURCE map, set the profile in memory, save under the new name
assert unreal.EditorLevelLibrary.load_level(LEVEL_SRC), "source proof map load failed"
fixtures = [a for a in unreal.EditorLevelLibrary.get_all_level_actors()
            if a.get_class().get_name() == "RPGFrameworkProofFixture"]
if len(fixtures) != 1:
    raise RuntimeError("expected one framework proof fixture, got %d" % len(fixtures))
fixtures[0].set_editor_property("profile", profile)
assert fixtures[0].get_editor_property("profile").get_path_name() == profile.get_path_name()
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(world, LEVEL_DST), "save_map under the new name failed"
unreal.log("[CODEX_WARP_EASE_R1] created isolated card/profile/map; WarpEaseInOut=1")
