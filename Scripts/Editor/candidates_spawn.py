"""Spawns the boss body candidates in a row far outside the arena (folder CandTest) so they can be photographed. Log prefix [Cand]. Cleanup: candidates_clear.py."""
import unreal

log = lambda m: unreal.log("[Cand] " + m)
LIST = [
    ("Sevarog", "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog"),
    ("SevarogBloodred", "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Skins/Tier_1/Sevarog_Red/Meshes/SevarogBloodred"),
    ("GruxWarchief", "/Game/ParagonGrux/Characters/Heroes/Grux/Skins/Tier_1/War_Chief/Meshes/GruxWarchief"),
    ("GruxChestplate", "/Game/ParagonGrux/Characters/Heroes/Grux/Skins/Tier_1_5/Chestplate/Meshes/GruxChestplate"),
    ("GruxMolten", "/Game/ParagonGrux/Characters/Heroes/Grux/Skins/Tier_2/Grux_Molten/Meshes/GruxMolten") if False else ("GruxMolten", "/Game/ParagonGrux/Characters/Heroes/Grux/Skins/Tier_2/Grux_Beetle_Molten/Meshes/GruxMolten"),
]
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for i, (name, path) in enumerate(LIST):
    mesh = unreal.load_asset(path)
    if not mesh:
        log("missing %s" % path)
        continue
    loc = unreal.Vector(-600, (i - 2) * 700, 0)
    a = sub.spawn_actor_from_class(unreal.SkeletalMeshActor, loc, unreal.Rotator(0, 180, 0))
    a.set_actor_label("Cand_" + name)
    a.set_folder_path("CandTest")
    c = a.skeletal_mesh_component
    c.set_skeletal_mesh_asset(mesh)
    b = mesh.get_bounds()
    # stand on the floor: the Paragon meshes have their feet at z = 0
    log("%s at y=%d bounds extent %.0f x %.0f x %.0f origin z %.0f" % (name, i * 700, b.box_extent.x, b.box_extent.y, b.box_extent.z, b.origin.z))
log("done")
