"""Debug: hides or shows arena actor components by name (NAMES, VISIBLE). Log prefix [HideComp]."""
import unreal
NAMES, VISIBLE = ("Debris",), True
arena = next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_class().get_name() == "RPGGreyboxArena")
for c in arena.get_components_by_class(unreal.StaticMeshComponent):
    if c.get_name() in NAMES:
        c.set_editor_property("visible", VISIBLE)
        unreal.log("[HideComp] %s visible=%s" % (c.get_name(), VISIBLE))
