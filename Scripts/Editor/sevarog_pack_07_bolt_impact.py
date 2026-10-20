"""Sevarog on the pack, step 7: Lightning impact. SevBoltAttackData (copy of the fireball attack data) with generic magic damage instead of fire and a
Sevarog particle as the impact effect (SevBoltImpactEffect, copy of FireballImpactEffect). Points GA_Sev_Lightning at it. Never deletes assets."""
import re
import unreal

log = lambda m: unreal.log("[SevPack7] " + m)
A = "/Game/AdvancedARPGCombat/MagicCombatSystem/Blueprints/"
OUT = "/Game/OneBossFight/SevarogPack"
BLAST = "/Game/ParagonSevarog/FX/Particles/Abilities/Subjugate/FX/P_Sevarog_Subjugate_Blast"
tools = unreal.AssetToolsHelpers.get_asset_tools()


def dup(src, name):
    existing = unreal.load_asset(OUT + "/" + name)
    return existing if existing else tools.duplicate_asset(name, OUT, unreal.load_asset(src))


impact = dup(A + "Abilities/FireBall/FireballImpactEffect", "SevBoltImpactEffect")
emitters = impact.get_editor_property("Impact Emitters")
log("impact emitters: %d entries" % len(list(emitters.keys())))
for key in list(emitters.keys()):
    text = emitters[key].export_text() if hasattr(emitters[key], "export_text") else str(emitters[key])
    log("  %s => %s" % (key, text[:260]))
    try:
        new = re.sub(r"/Game/[\w/]+\.[\w]+", BLAST + ".P_Sevarog_Subjugate_Blast", text)
        emitters[key].import_text(new)
    except Exception as exc:
        log("  rewrite failed: %s" % str(exc)[:100])
impact.set_editor_property("Impact Emitters", emitters)
unreal.EditorAssetLibrary.save_loaded_asset(impact)

data = dup(A + "Abilities/FireBall/FireBallAttackData", "SevBoltAttackData")
data.set_editor_property("Damage Gampelay Effect", unreal.load_asset(A + "GameplayEffects/GE_MagicDamage").generated_class() if hasattr(unreal.load_asset(A + "GameplayEffects/GE_MagicDamage"), "generated_class") else unreal.load_asset(A + "GameplayEffects/GE_MagicDamage"))
data.set_editor_property("Attack Impact Effects", [impact])
unreal.EditorAssetLibrary.save_loaded_asset(data)

ga = unreal.load_asset(OUT + "/Abilities/GA_Sev_Lightning")
cdo = unreal.get_default_object(ga.generated_class())
cdo.set_editor_property("AttackData", data)
unreal.BlueprintEditorLibrary.compile_blueprint(ga)
unreal.EditorAssetLibrary.save_loaded_asset(ga)
log("GA_Sev_Lightning.AttackData = %s" % data.get_name())
