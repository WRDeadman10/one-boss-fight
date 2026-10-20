"""Sevarog on the pack, step 4: L_SevarogPack, a copy of the art arena level (L_Greybox) for the pack framework.
Differences from L_Greybox: pack game mode (BP_AdvancedGameMode), no C++ boss / encounter trigger / benchmark runner, BP_SevarogBossPack at the
arena centre, a NavMeshBoundsVolume over the arena (the pack's AI walks on the navmesh). L_Greybox itself is untouched until stage 5."""
import unreal

log = lambda m: unreal.log("[SevPack4] " + m)
SRC = "/Game/OneBossFight/Levels/L_Greybox"
DST_DIR, DST_NAME = "/Game/OneBossFight/Levels", "L_SevarogPack"
BOSS = "/Game/OneBossFight/SevarogPack/BP_SevarogBossPack.BP_SevarogBossPack_C"
GAME_MODE = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_AdvancedGameMode.BP_AdvancedGameMode_C"

# The level is duplicated and opened beforehand with the plugin tools (asset duplicate, open_level): loading a map from inside a script crashes the editor.
assert unreal.EditorLevelLibrary.get_editor_world().get_name() == DST_NAME, "open L_SevarogPack first"

removed = []
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if a.get_class().get_name() in ("BP_SevarogBoss_C", "RPGEncounterTrigger", "RPGBenchmarkRunner") or a.get_class().get_name() == "BP_SevarogBossPack_C":
        removed.append(a.get_actor_label())
        a.destroy_actor()
log("removed %s" % removed)

world = unreal.EditorLevelLibrary.get_editor_world()
settings = world.get_world_settings()
settings.set_editor_property("default_game_mode", unreal.load_class(None, GAME_MODE))
log("game mode = %s" % settings.get_editor_property("default_game_mode").get_name())

boss = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.load_class(None, BOSS), unreal.Vector(0, 0, 160), unreal.Rotator(0, 0, 180))
boss.set_actor_label("SevarogBoss")

nav = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.NavMeshBoundsVolume, unreal.Vector(0, 0, 100))
nav.set_actor_label("ArenaNavBounds")
nav.set_actor_scale3d(unreal.Vector(80, 80, 12))  # brush is 200 cm: 16000 x 16000 x 2400 cm
log("boss and nav bounds placed")
# save_map writes a proper .umap (the plugin's asset duplicate wrote a .uasset World).
ok = unreal.EditorLoadingAndSavingUtils.save_map(world, "/Game/OneBossFight/Levels/L_SevarogArena")
log("saved as L_SevarogArena: %s" % ok)
