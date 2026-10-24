"""Creates the project-owned close attack montages AM_Boss01_A1, AM_Boss01_A3a, AM_Boss01_A3b (log prefix [CloseMontages]) from AG's authored clips, with the notify classes of the pack's close attack montages (read from GS_Attack03 for A1, GS_Attack01 for A3a, GS_Attack02 for A3b: damage trace state, movement lock, desired rotation, sound, end-of-ability, follow-up) placed at the authored times of the timing sheets:
  A1  AN_Boss01_A1_QuickSlash  length 1.200  commit 0.33  active 0.35 .. 0.50
  A3a AN_Boss01_A3a_Combo1     length 0.800  commit 0.38  active 0.40 .. 0.60
  A3b AN_Boss01_A3b_Combo2     length 1.3333 commit 0.13  active 0.15 .. 0.40
The slot is the pack boss's (read from GS_Attack01), blend 0.25 in and out as the pack montages. New assets only, an existing montage is left as it is (REBUILD = True clears its notifies and places them again: the asset keeps its identity). Nothing in the pack is changed.
Open points that the PIE driver of the integration must settle (the pack montages' notify TIMES are not readable from Python): the time of AN_PerformFollowUp in A3a and of AN_EndAnimatingAbility."""
import unreal

log = lambda m: unreal.log("[CloseMontages] " + m)
DEST = "/Game/OneBossFight/Boss01/Animations"
PACK = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/"
REBUILD = False
AL = unreal.AnimationLibrary
SPEC = [
    # name, clip, pack montage to read the classes from, commit, active start, active end, follow up time (None: no follow up notify)
    ("AM_Boss01_A1", "AN_Boss01_A1_QuickSlash", "GS_Attack03_Montage", 0.33, 0.35, 0.50, None),
    ("AM_Boss01_A3a", "AN_Boss01_A3a_Combo1", "GS_Attack01_Montage", 0.38, 0.40, 0.60, 0.75),
    ("AM_Boss01_A3b", "AN_Boss01_A3b_Combo2", "GS_Attack02_Montage", 0.13, 0.15, 0.40, None),
]
tools = unreal.AssetToolsHelpers.get_asset_tools()
slot = unreal.RPGMontageUtils.get_montage_slot(unreal.load_asset(PACK + "GS_Attack01_Montage"))


def classes_of(pack_montage):
    out = {}
    for e in AL.get_animation_notify_events(unreal.load_asset(PACK + pack_montage)):
        state = e.get_editor_property("notify_state_class")
        notify = e.get_editor_property("notify")
        obj = state if state is not None else notify
        if obj is not None:
            out[obj.get_class().get_name()] = (obj.get_class(), state is not None, obj)
    return out


def build(name, clip_name, pack_name, commit, a0, a1, follow):
    path = DEST + "/" + name
    clip = unreal.load_asset(DEST + "/" + clip_name)
    existing = unreal.EditorAssetLibrary.does_asset_exist(path)
    if existing and not REBUILD:
        log("%s exists, left as it is" % name)
        return
    if existing:
        m = unreal.load_asset(path)
        for track in list(AL.get_animation_notify_track_names(m)):
            AL.remove_animation_notify_track(m, track)
    else:
        factory = unreal.AnimMontageFactory()
        factory.set_editor_property("source_animation", clip)
        m = tools.create_asset(name, DEST, unreal.AnimMontage, factory)
        unreal.RPGMontageUtils.set_montage_slot(m, slot)
        m.set_editor_property("enable_auto_blend_out", True)
    length = m.get_editor_property("sequence_length")
    cls = classes_of(pack_name)
    log("%s: length %.4f, pack classes %s" % (name, length, sorted(cls)))
    track = "Boss01Close"
    AL.add_animation_notify_track(m, track, unreal.LinearColor(1, 0.5, 0.2, 1))
    placed = []

    def state(cname, t0, dur):
        if cname in cls and cls[cname][1]:
            AL.add_animation_notify_state_event(m, track, t0, dur, cls[cname][0])
            placed.append("%s %.2f+%.2f" % (cname, t0, dur))

    def event(cname, t, fix=None):
        if cname in cls and not cls[cname][1]:
            n = AL.add_animation_notify_event(m, track, t, cls[cname][0])
            if fix:
                fix(n, cls[cname][2])
            placed.append("%s %.2f" % (cname, t))

    state("ANS_DisableMovement_C", 0.0, a1)
    state("ANS_SetDesiredRotation_C", 0.0, commit)
    state("ANS_CollisionTrace_C", a0, a1 - a0)
    event("AnimNotify_PlaySound", max(a0 - 0.02, 0.0), lambda n, src: n.set_editor_property("sound", src.get_editor_property("sound")) or n.set_editor_property("pitch_multiplier", src.get_editor_property("pitch_multiplier")))
    if follow is not None:
        event("AN_PerformFollowUp_C", follow)
    event("AN_EndAnimatingAbility_C", length - 0.02)
    log("%s notifies placed: %s" % (name, placed))
    unreal.EditorAssetLibrary.save_loaded_asset(m)


for spec in SPEC:
    build(*spec)
for name, *_ in SPEC:
    m = unreal.load_asset(DEST + "/" + name)
    if m:
        log("check %s: length %.4f, notifies %s" % (name, m.get_editor_property("sequence_length"), sorted(str(e.get_editor_property("notify_name")) for e in AL.get_animation_notify_events(m))))
log("DONE")
