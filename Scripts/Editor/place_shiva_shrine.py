"""Places the Lord Shiva shrine (/Game/OneBossFight/Environment/Shrine/SM_Boss01_ShivaShrine) in L_SevarogArena behind the player start, turned to face it, with a box collision (log prefix [ShrinePlace]). Idempotent: an earlier actor labelled ShivaShrine is replaced. The mesh's face points to -Y in the engine (the exporter mirrors Y; AG's sockets read y -120 for the front), so the actor yaw is the direction to the spawn plus 90. Does not save the level: look first (Scripts/Editor/save_gate_frame.py style save, or save_shrine.py)."""
import math
import unreal

log = lambda m: unreal.log("[ShrinePlace] " + m)
mesh = unreal.load_asset("/Game/OneBossFight/Environment/Shrine/SM_Boss01_ShivaShrine")
spawn = unreal.Vector(-1800.0, 0.0, 100.0)
pos = unreal.Vector(-2250.0, -330.0, 0.0)
# the face is at -Y of the mesh: yaw = angle(to the spawn) - (-90)
to_spawn = math.degrees(math.atan2(spawn.y - pos.y, spawn.x - pos.x))
yaw = to_spawn + 90.0
try:
    unreal.EditorStaticMeshLibrary.remove_collisions(mesh)
    log("box collision added: %s" % unreal.EditorStaticMeshLibrary.add_simple_collisions(mesh, unreal.ScriptingCollisionShapeType.BOX))
    unreal.EditorAssetLibrary.save_asset("/Game/OneBossFight/Environment/Shrine/SM_Boss01_ShivaShrine", only_if_is_dirty=False)
except Exception as e:
    log("collision: %s" % e)
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if a.get_actor_label() == "ShivaShrine":
        unreal.EditorLevelLibrary.destroy_actor(a)
actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, pos, unreal.Rotator(0, 0, yaw))
actor.set_actor_label("ShivaShrine")
actor.set_folder_path("Dressing")
actor.static_mesh_component.set_static_mesh(mesh)
log("shrine placed at %s yaw %.1f (facing the spawn at %s)" % (pos, yaw, spawn))
