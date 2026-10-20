import unreal
log = lambda m: unreal.log("[Bolt] " + m)
F = "/Game/AdvancedARPGCombat/MagicCombatSystem/Blueprints/Abilities/FireBall/"
ad = unreal.load_asset(F + "FireBallAttackData")
log("attackdata class=%s" % ad.get_class().get_name())
for n in ("ImpactCue", "Impact Cue", "GameplayCues", "HitCue", "Gameplay Cue", "Damage", "PoiseDamage", "ImpactGameplayCue", "AttackType", "ImpactEffect"):
    try:
        v = ad.get_editor_property(n)
        log("%s = %s" % (n, v.export_text() if hasattr(v, "export_text") else v))
    except Exception:
        pass
bp = unreal.load_asset(F + "FireballImpactEffect")
sub = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary
for h in sub.k2_gather_subobject_data_for_blueprint(bp):
    d = lib.get_data(h)
    o = lib.get_object(d)
    log("comp %s | %s" % (lib.get_display_name(d), o.get_class().get_name() if o else "?"))
    if isinstance(o, unreal.ParticleSystemComponent):
        log("  template=%s" % o.get_editor_property("template"))
