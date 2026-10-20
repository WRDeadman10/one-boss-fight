"""Fireball enemy ability defaults, its montage notifies, and the projectile Blueprint components."""
import unreal
log = lambda m: unreal.log("[Fireball] " + m)
M = "/Game/AdvancedARPGCombat/MagicCombatSystem/"


def text(v):
    if isinstance(v, (list, tuple, unreal.Array)):
        return "[" + "; ".join(text(x) for x in v)[:700] + "]"
    if isinstance(v, (dict, unreal.Map)):
        return "{" + ", ".join("%s: %s" % (text(k), text(x)) for k, x in v.items())[:500] + "}"
    if hasattr(v, "export_text"):
        return v.export_text()[:500]
    if hasattr(v, "get_path_name"):
        return v.get_path_name()
    return str(v)[:300]


ga = unreal.load_asset(M + "Blueprints/AI/ExampleMagicEnemy/GA_Fireball_Enemy")
cdo = unreal.get_default_object(ga.generated_class())
for n in ("AttackMontages", "ProjectilesToFire", "Projectile Socket Name", "ProjectileRange", "Projectile Range", "bAimProjectileAtCamera?", "Projectile Object Types",
          "ProjectileHandSocketNames", "Head Shot Multiplier", "AttackData", "Random Attack Index?", "ResetAttackTime"):
    try:
        log("%s = %s" % (n, text(cdo.get_editor_property(n))))
    except Exception:
        log("%s = <n/a>" % n)
for name in ("FireMagicProjectile_01_MagicEnemy_Montage",):
    m = unreal.load_asset(M + "Animations/ExampleMagicEnemy/" + name)
    log("== %s len=%.2f" % (name, m.get_play_length()))
    for ev in unreal.AnimationLibrary.get_animation_notify_events(m):
        for slot in ("notify_state_class", "notify"):
            o = ev.get_editor_property(slot)
            if o is None:
                continue
            props = ""
            for n in ("Event Tag", "Event Magnitude", "Optional Object", "RotationInterpSpeed"):
                try:
                    props += " | %s=%s" % (n, text(o.get_editor_property(n)))
                except Exception:
                    pass
            log("  %s %s%s" % (slot, o.get_class().get_name(), props))
bp = unreal.load_asset(M + "Blueprints/Abilities/FireBall/BP_FireBallProjectile")
sub = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary
for h in sub.k2_gather_subobject_data_for_blueprint(bp):
    d = lib.get_data(h)
    o = lib.get_object(d)
    log("comp %s | %s | inherited=%s" % (lib.get_display_name(d), o.get_class().get_name() if o else "?", lib.is_inherited_component(d)))
