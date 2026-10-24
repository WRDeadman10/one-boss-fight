"""Places the scratch actor RemainsLook (corpse statue, scale 1.5) at (-1200, -900, 0) for pie_remains_material.py (log prefix [RemainsLook]). Remove it again with remove_remains_look.py before anything is saved."""
import unreal

mesh = unreal.load_asset("/Game/OneBossFight/Boss01/Remains/SM_Boss01_CorpseStatue")
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if a.get_actor_label() == "RemainsLook":
        unreal.EditorLevelLibrary.destroy_actor(a)
a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(-1200.0, -900.0, 0.0), unreal.Rotator(0, 0, 0))
a.set_actor_label("RemainsLook")
a.set_actor_scale3d(unreal.Vector(1.5, 1.5, 1.5))
a.static_mesh_component.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
a.static_mesh_component.set_static_mesh(mesh)
unreal.log("[RemainsLook] placed")
