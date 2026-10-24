"""Removes the scratch actor RemainsLook (log prefix [RemainsLook])."""
import unreal

for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if a.get_actor_label() == "RemainsLook":
        unreal.EditorLevelLibrary.destroy_actor(a)
        unreal.log("[RemainsLook] removed")
