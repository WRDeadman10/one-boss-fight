"""Prints the parameters of a few materials (log prefix [MatProbe]), read-only."""
import unreal

log = lambda m: unreal.log("[MatProbe] " + m)
for path in ("/Game/OneBossFight/Environment/Materials/M_Ember", "/Game/OneBossFight/Environment/Materials/MI_Arena_FogGate", "/Game/OneBossFight/Environment/Materials/MI_Arena_Stone"):
    m = unreal.load_asset(path)
    if not m:
        log("%s missing" % path)
        continue
    log("%s class %s" % (path, m.get_class().get_name()))
    try:
        log("  scalars %s" % list(unreal.MaterialEditingLibrary.get_scalar_parameter_names(m)))
        log("  vectors %s" % list(unreal.MaterialEditingLibrary.get_vector_parameter_names(m)))
    except Exception as e:
        log("  no params: %s" % e)
    if isinstance(m, unreal.MaterialInstanceConstant):
        log("  parent %s" % m.get_editor_property("parent"))
log("DONE")
