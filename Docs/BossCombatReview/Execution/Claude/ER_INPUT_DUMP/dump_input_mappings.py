# Read-only dump of the player's input mappings (lead, Claude, 2026-11-06): which key and trigger reach the strong attack and the charged attack.
# Writes nothing to assets. Log prefix [InputDump].
import unreal

def log(msg):
    unreal.log("[InputDump] " + msg)

def describe_triggers(triggers):
    out = []
    for t in triggers or []:
        if t is None:
            continue
        name = t.get_class().get_name()
        extra = ""
        for prop in ("hold_time_threshold", "actuation_threshold", "b_is_one_shot", "is_one_shot"):
            try:
                extra += " %s=%s" % (prop, t.get_editor_property(prop))
            except Exception:
                pass
        out.append(name + extra)
    return out

def get_mappings(imc):
    for prop in ("mappings", "default_key_mappings"):
        try:
            value = imc.get_editor_property(prop)
        except Exception:
            continue
        try:
            return list(value.get_editor_property("mappings"))
        except Exception:
            return list(value)
    return []

for path in ("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/IMC_AdvancedControls",
             "/Game/OneBossFight/Input/IMC_Default"):
    imc = unreal.load_asset(path)
    if imc is None:
        log("MISSING " + path)
        continue
    maps = get_mappings(imc)
    log("IMC %s: %d mappings" % (path, len(maps)))
    for m in maps:
        try:
            action = m.get_editor_property("action")
            key = m.get_editor_property("key")
            triggers = m.get_editor_property("triggers")
            log("  %s <- %s triggers=%s" % (action.get_name() if action else "None", key.get_editor_property("key_name") if key else "None", describe_triggers(triggers)))
        except Exception as e:
            log("  mapping read error: %s" % e)

for name in ("IA_StrongAttack", "IA_ChargedAttack", "IA_StrongAttackSecondInput", "IA_NormalAttack", "IA_Block", "IA_Parry", "IA_Dodge", "IA_Sprint"):
    ia = unreal.load_asset("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/" + name)
    if ia is None:
        log("ACTION MISSING " + name)
        continue
    try:
        log("ACTION %s value_type=%s triggers=%s" % (name, ia.get_editor_property("value_type"), describe_triggers(ia.get_editor_property("triggers"))))
    except Exception as e:
        log("ACTION %s read error %s" % (name, e))
log("DONE")
