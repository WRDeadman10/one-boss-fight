"""Sevarog on the pack, step 10: the triple combo and the Shockwave telegraph.
Combo: the pack's own mechanism. AN_PerformFollowUp at the end of the Sweep montage (70 %) plays the Backhand montage, and at the end of the Backhand montage
(60 %) plays the Overhead montage, when the target is within 450 cm; the first two entries of the close attack end type is 'wait' (1) like the pack boss's.
Telegraph: the shockwave ring marker (NS_Free_Spells_Circle) on the ground 0.45 s before the slam, same spot and size as the shockwave.
Edits montages in place (never deletes); safe to run twice."""
import re
import unreal

HEAD = open(r"C:/Users/winss/Documents/Unreal Projects/OneBossFight/Scripts/Editor/sevarog_pack_02_montages_abilities.py", encoding="utf-8").read()
exec(HEAD[:HEAD.index("ONLY_TOGGLE = globals()")])
log = lambda m: unreal.log("[SevPack10] " + m)
lib = unreal.AnimationLibrary
AN_FOLLOW = A + "AdvancedCombatFramework/CoreCombatSystem/AI/AnimNotifies/AN_PerformFollowUp.AN_PerformFollowUp_C"
NS_CIRCLE = "/Game/Free_Spells/VFX_Niagara/NS_Free_Spells_Circle"


def notify_class_names(montage):
    names = []
    for ev in lib.get_animation_notify_events(montage):
        for slot in ("notify", "notify_state_class"):
            o = ev.get_editor_property(slot)
            if o is not None:
                names.append(o.get_class().get_name())
    return names


def add_follow_up(montage_name, next_montage_name, chance):
    m = unreal.load_asset(MONT + "/" + montage_name)
    if "AN_PerformFollowUp_C" in notify_class_names(m):
        log("%s already has a follow-up" % montage_name)
        return
    length = m.get_play_length()
    notify = lib.add_animation_notify_event(m, "PackCombat", length * 0.55, load_class(AN_FOLLOW))
    notify.set_editor_property("ChanceToPerformFollowUp", chance)
    notify.set_editor_property("CloseRangeAttacksMaxDistance", 450.0)
    notify.set_editor_property("Close Anim Montage", [unreal.load_asset(MONT + "/" + next_montage_name)])
    m.modify()
    unreal.EditorAssetLibrary.save_loaded_asset(m, False)
    log("%s -> %s at %.2fs, chance %d" % (montage_name, next_montage_name, length * 0.55, chance))


add_follow_up("AM_SevPack_Sweep", "AM_SevPack_Backhand", 70)
add_follow_up("AM_SevPack_Backhand", "AM_SevPack_Overhead", 60)

# Close attack: Sweep and Backhand wait for the follow-up decision.
ga = unreal.load_asset(ABIL + "/GA_Sev_CloseAttack")
cdo = unreal.get_default_object(ga.generated_class())
entries = list(cdo.get_editor_property("AttackMontages"))
for i, name in enumerate(("AM_SevPack_Sweep", "AM_SevPack_Backhand", "AM_SevPack_Overhead")):
    text = entries[i].export_text()
    wait = "NewEnumerator1" if name != "AM_SevPack_Overhead" else "NewEnumerator0"
    entries[i].import_text(re.sub(r"(AbilityEndType_\d+_[0-9A-F]+)=NewEnumerator\d", lambda m: "%s=%s" % (m.group(1), wait), text))
cdo.set_editor_property("AttackMontages", entries)
ga.modify()
unreal.BlueprintEditorLibrary.compile_blueprint(ga)
unreal.EditorAssetLibrary.save_loaded_asset(ga, False)
log("close attack end types set")

# Shockwave telegraph.
shock = unreal.load_asset(MONT + "/AM_SevPack_Shockwave")
if True:
    spawn_count = notify_class_names(shock).count("RPGAN_SpawnEffect")
    if spawn_count < 2:
        seq = find_pack_asset("AnimSequence", "Ultimate_Swing_120fps")
        start, end = motion_window(seq)
        peak = (start + end) / 2.0
        marker = lib.add_animation_notify_event(shock, "PackCombat", max(peak - 0.45, 0.05), unreal.RPGAN_SpawnEffect)
        marker.set_editor_property("niagara_effect", unreal.load_asset(NS_CIRCLE))
        marker.set_editor_property("forward_offset", 200.0)
        marker.set_editor_property("ground_drop", 155.0)
        marker.set_editor_property("scale", 5.0)
        shock.modify()
        unreal.EditorAssetLibrary.save_loaded_asset(shock, False)
        log("shockwave telegraph added at %.2fs" % max(peak - 0.45, 0.05))
    else:
        log("shockwave already has the telegraph")
