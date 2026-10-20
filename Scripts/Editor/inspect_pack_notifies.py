"""Reads the property values of the pack boss montage notifies (GS_Attack01, GS_LeapAttack) so our Sevarog montages can copy them."""
import unreal

log = lambda m: unreal.log("[PackNotify] " + m)
P = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/"


def val(o, n):
    try:
        v = o.get_editor_property(n)
        return v.export_text() if hasattr(v, "export_text") else (v.get_path_name() if hasattr(v, "get_path_name") else str(v))
    except Exception:
        return "<n/a>"


PROPS = {
    "AN_ToggleCombat_C": [], "ANS_CollisionTrace_C": ["Collision Target Tag", "EventTag", "AttackData", "Swing Direction", "TraceRadiusModifier"],
    "ANS_SetDesiredRotation_C": ["RotationInterpSpeed", "Desired Rotation Type"],
    "AN_EndAnimatingAbility_C": ["Result"],
    "AN_PerformFollowUp_C": ["ChanceToPerformFollowUp"],
}
for name in ("GS_EquipWeapon_Montage", "GS_UnequipWeapon_Montage"):
    m = unreal.load_asset(P + name)
    log("== %s len=%.2f" % (name, m.get_play_length()))
    for ev in unreal.AnimationLibrary.get_animation_notify_events(m):
        for slot in ("notify_state_class", "notify"):
            o = ev.get_editor_property(slot)
            if o is None:
                continue
            cls = o.get_class().get_name()
            log("  %s %s" % (slot, cls) + "".join(" | %s=%s" % (n, val(o, n)) for n in PROPS.get(cls, [])))
        # timing
        try:
            log("    time=%.3f" % ev.get_editor_property("trigger_time_offset"))
        except Exception:
            pass
