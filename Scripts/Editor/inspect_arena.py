"""
Prints the arena actor's components (class, mesh, relative transform, instance count) and the parameters of a few Megascans material instances. Log prefix [Inspect].
Run with Scripts/run_in_editor.py.
"""
import unreal

log = lambda m: unreal.log("[Inspect] " + m)
arena = next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_class().get_name() == "RPGGreyboxArena")
for c in arena.get_components_by_class(unreal.SceneComponent):
    mesh = None
    try:
        mesh = c.get_editor_property("static_mesh")
    except Exception:
        pass
    n = c.get_instance_count() if isinstance(c, unreal.InstancedStaticMeshComponent) else ""
    t = c.relative_location
    log("%-40s %-32s mesh=%s loc=(%.0f,%.0f,%.0f) scale=%s inst=%s hidden=%s coll=%s" % (c.get_name(), c.get_class().get_name(), mesh.get_name() if mesh else None, t.x, t.y, t.z, c.relative_scale3d, n, c.get_editor_property("hidden_in_game"), c.get_editor_property("collision_enabled") if hasattr(c, "get_editor_property") and isinstance(c, unreal.PrimitiveComponent) else ""))
for path in ("/Game/MS/Surfaces/Roman_Stone_Floor_thsjdfxq/MI_Roman_Stone_Floor_thsjdfxq_1",
             "/Game/MS/3D/Modular_Brick_Ruins_Kit_xjotbhkiy/MI_Modular_Brick_Ruins_Kit_xjotbhkiy",
             "/Game/OneBossFight/Environment/Materials/MI_Arena_Floor"):
    mi = unreal.EditorAssetLibrary.load_asset(path)
    if not mi:
        log("missing " + path)
        continue
    log("%s parent=%s" % (path.split("/")[-1], mi.get_editor_property("parent").get_name() if mi.get_editor_property("parent") else None))
    ml = unreal.MaterialEditingLibrary
    log("   scalars: %s" % [str(n) for n in ml.get_scalar_parameter_names(mi)][:40])
    log("   vectors: %s" % [str(n) for n in ml.get_vector_parameter_names(mi)][:20])
    log("   textures: %s" % [str(n) for n in ml.get_texture_parameter_names(mi)][:20])
