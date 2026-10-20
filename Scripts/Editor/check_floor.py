"""Prints the floor material the arena actor holds and the one on its floor component, and the brazier mesh. Log prefix [Floor]."""
import unreal

arena = next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_class().get_name() == "RPGGreyboxArena")
fm = arena.get_editor_property("floor_material")
unreal.log("[Floor] property floor_material = %s" % (fm.get_path_name() if fm else None))
for c in arena.get_components_by_class(unreal.StaticMeshComponent):
    mats = [m.get_path_name() if m else None for m in c.get_materials()]
    unreal.log("[Floor] comp %s mesh=%s mats=%s hidden=%s" % (c.get_name(), c.static_mesh.get_name() if c.static_mesh else None, mats, c.get_editor_property("hidden_in_game")))
unreal.log("[Floor] pillar_material = %s ; wall_material = %s ; brazier = %s" % (arena.get_editor_property("pillar_material"), arena.get_editor_property("wall_material"), arena.get_editor_property("brazier")))
