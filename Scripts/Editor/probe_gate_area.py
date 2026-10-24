"""Lists the level actors near the fog gate with their bounds (log prefix [GateArea]): read-only, to place the M-08 frame."""
import unreal

log = lambda m: unreal.log("[GateArea] " + m)
gate = unreal.Vector(-3150.0, 0.0, 0.0)
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    loc = a.get_actor_location()
    if (loc - gate).length() > 1100.0:
        continue
    o, e = a.get_actor_bounds(False)
    log("%s | %s | loc (%.0f %.0f %.0f) yaw %.0f | bounds origin (%.0f %.0f %.0f) extent (%.0f %.0f %.0f)" % (a.get_actor_label(), a.get_class().get_name(), loc.x, loc.y, loc.z, a.get_actor_rotation().yaw, o.x, o.y, o.z, e.x, e.y, e.z))
log("DONE")
