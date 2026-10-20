"""Prints every mapping in IMC_Default with its modifiers and triggers, and each action's value type."""
import unreal

imc = unreal.load_asset("/Game/OneBossFight/Input/IMC_Default")
for m in imc.get_editor_property("mappings"):
    action = m.get_editor_property("action")
    key = m.get_editor_property("key").get_editor_property("key_name")
    mods = []
    for mod in m.get_editor_property("modifiers"):
        if mod is None:
            mods.append('NULL')
            continue
        desc = mod.get_class().get_name()
        for prop in ("order", "scalar", "dead_zone_type", "lower_threshold", "upper_threshold"):
            try:
                desc += " %s=%s" % (prop, mod.get_editor_property(prop))
            except Exception:
                pass
        mods.append(desc)
    trig = [t.get_class().get_name() if t else 'NULL' for t in m.get_editor_property("triggers")]
    unreal.log("[IMCInspect] %s <- %s | mods=%s | triggers=%s | type=%s" % (
        action.get_name(), key, mods, trig, action.get_editor_property("value_type")))
