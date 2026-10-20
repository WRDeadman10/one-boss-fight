import unreal
log = lambda m: unreal.log("[ProbeVars] " + m)
bp = unreal.load_asset("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Sword/GA_Sword_Melee")
try:
    nv = bp.get_editor_property("new_variables")
    log("new_variables: %d: %s" % (len(nv), [str(v.get_editor_property("var_name")) for v in nv][:30]))
except Exception as e:
    log("new_variables failed: " + str(e)[:200])
cdo = unreal.get_default_object(bp.generated_class())
for name in ("AttackMontages", "Attack Montages", "AttackData"):
    try:
        v = cdo.get_editor_property(name)
        log("%s -> %s" % (name, str(v)[:200]))
        if isinstance(v, (list, tuple)) and v:
            log("  first export: " + v[0].export_text()[:600])
    except Exception as e:
        log("%s failed: %s" % (name, str(e)[:100]))
