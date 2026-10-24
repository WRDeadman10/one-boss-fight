"""Removes the scratch actor StatueLook, saves the imported corpse statue mesh (/Game/OneBossFight/Boss01/Remains/SM_Boss01_CorpseStatue) and the level (log prefix [StatueImport]). The statue is spawned by code on the boss's death, never placed in the level."""
import unreal

log = lambda m: unreal.log("[StatueImport] " + m)
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if a.get_actor_label() == "StatueLook":
        unreal.EditorLevelLibrary.destroy_actor(a)
        log("removed StatueLook")
mesh = unreal.load_asset("/Game/OneBossFight/Boss01/Remains/SM_Boss01_CorpseStatue")
log("slots %s" % [(str(s.material_slot_name), s.material_interface.get_name() if s.material_interface else None) for s in mesh.get_editor_property("static_materials")])
log("save mesh: %s" % unreal.EditorAssetLibrary.save_asset("/Game/OneBossFight/Boss01/Remains/SM_Boss01_CorpseStatue", only_if_is_dirty=False))
log("save level: %s" % unreal.EditorLoadingAndSavingUtils.save_current_level())
