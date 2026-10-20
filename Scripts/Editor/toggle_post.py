"""Debug: enables or disables an actor class by label. Edit LABEL/ENABLED. Log prefix [Toggle]."""
import unreal
LABEL, ENABLED = "DuskPost", True
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if a.get_actor_label() == LABEL:
        a.set_editor_property("enabled", ENABLED)
        unreal.log("[Toggle] %s enabled=%s" % (LABEL, ENABLED))
