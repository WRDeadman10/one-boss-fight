"""
Boss clips (Brief 12 deliveries wired in): the phase two roar and the stance break play the project's own clips (AN_Boss01_PhaseRoar, AN_Boss01_StaggerFall, AN_Boss01_StaggerDown) instead of the pack's montages.
  S1 a stance break: stages fall (0.7 s) -> down (the kneel loop, until 2.5 s) -> getup (the fall backwards at rate 0.6, about 1.2 s) -> over; every stage's montage plays the right clip (read from the montage's own segment),
     the boss's pelvis goes down at least 30 cm into the kneel and comes back to standing height, the boss is not staggered afterwards, the pack's knockdown montage never plays.
  S2 a second stance break right after the first works the same (the weak montage pointer and the loaded clips are reused).
  S3 the roar: health to 55 percent: the transition plays AN_Boss01_PhaseRoar (source name and montage segment), lasts 1.8 s, the boss is not held afterwards.
  S4 the fallback: with bUseClips off (through the test hook) the pack's knockdown montage plays and the stance break still runs its stages.
Boss held awake (HoldForTest), same scaffold as pie_posture_hits.py. Log prefix [BossClips]; ends with RESULT n/m passed. Run pie_debug_overlay.py once after an editor start first.
"""
import unreal

log = lambda m: unreal.log("[BossClips] " + m)
results = []
S = {"phase": "start", "t": 0.0, "now": 0.0, "wait": 0.0, "gen": None, "samples": None}
handle = None


def check(name, ok, detail=""):
    results.append(ok)
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def tags(*names):
    c = unreal.GameplayTagContainer()
    c.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return c


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def actors():
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return w, pc, pawn, boss


def P():
    w, pc, pawn, boss = actors()
    return {"w": w, "pc": pc, "pawn": pawn, "boss": boss, "enc": comp(boss, "RPGBossEncounter"), "tr": comp(boss, "RPGAttackTracker"), "dbg": comp(boss, "RPGCombatDebug"), "stg": comp(boss, "RPGBossStagger"),
            "post": comp(boss, "RPGBossPosture"), "ph": comp(boss, "RPGBossPhases")}


def until(cond, timeout, step=0.0):
    t0 = S["now"]
    while not cond():
        if S["now"] - t0 > timeout:
            return False
        yield step
    return True


def fresh():
    p = P()
    p["stg"].set_stagger_seconds_for_test(2.5)
    p["stg"].set_cooldown_for_test(0.0)
    p["enc"].reset_for_test()
    yield 0.8
    p = P()
    p["enc"].wake()
    p["enc"].hold_for_test(True)
    p["dbg"].debug_refill_player()
    p["tr"].enter_combat()
    comp(p["pawn"], "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
    yield 2.2


def boss_mesh():
    return P()["boss"].get_components_by_class(unreal.SkeletalMeshComponent)[0]


def montage_clip_name(m):
    """The name of the animation asset the boss's active montage plays (read by C++ from the montage's first segment)."""
    return P()["dbg"].debug_boss_montage_anim_name()


def sample():
    p = P()
    mesh = boss_mesh()
    inst = mesh.get_anim_instance()
    m = inst.get_current_active_montage() if inst else None
    pelvis = mesh.get_socket_location("pelvis").z
    S["samples"].append({"t": S["now"], "stage": p["stg"].get_clip_stage_name(), "staggered": p["stg"].is_staggered(), "clip": montage_clip_name(m) if m else None,
                         "mname": m.get_name() if m else None, "pos": inst.montage_get_position(m) if m else None, "pelvis": pelvis})


def stance_break(label, expect_clips=True):
    p = P()
    stand = boss_mesh().get_socket_location("pelvis").z
    S["samples"] = []
    result = p["stg"].force_break_for_test()
    yield from until(lambda: P()["stg"].is_staggered() is False and len(S["samples"]) > 30, 9.0)
    yield 0.4
    samples = S["samples"]
    S["samples"] = None
    stages = []
    for s in samples:
        if not stages or stages[-1] != s["stage"]:
            stages.append(s["stage"])
    # the stages in order and how long each lasted
    spans = {}
    for stage in ("fall", "down", "getup"):
        times = [s["t"] for s in samples if s["stage"] == stage]
        spans[stage] = (times[-1] - times[0]) if len(times) > 1 else 0.0
    lowest = min(s["pelvis"] for s in samples)
    last = samples[-1]
    if expect_clips:
        check("%s: the break started (%s) and the stages ran in order fall, down, getup" % (label, result), result == "started" and [x for x in stages if x != "none"] == ["fall", "down", "getup"], "%s" % stages)
        check("%s: fall about 0.7 s (%.2f), down until 2.5 s in total (%.2f after the fall), get-up about 1.2 s (%.2f)" % (label, spans["fall"], spans["down"], spans["getup"]),
              0.5 <= spans["fall"] <= 1.0 and 1.4 <= spans["down"] <= 2.3 and 0.8 <= spans["getup"] <= 1.7)
        clips = {}
        for s in samples:
            if s["stage"] != "none" and s["clip"]:
                clips.setdefault(s["stage"], set()).add(s["clip"])
        check("%s: every stage plays its clip (fall: StaggerFall, down: StaggerDown, getup: StaggerFall backwards) and never the pack's knockdown montage" % label,
              clips.get("fall") == {"AN_Boss01_StaggerFall"} and clips.get("down") == {"AN_Boss01_StaggerDown"} and clips.get("getup") == {"AN_Boss01_StaggerFall"} and not any((s["mname"] or "").startswith("Knockdown") for s in samples), "%s" % clips)
        getup = [s["pos"] for s in samples if s["stage"] == "getup" and s["pos"] is not None]
        check("%s: the get-up plays backwards (montage position falls from %.2f to %.2f)" % (label, getup[0] if getup else -1, getup[-1] if getup else -1), len(getup) >= 5 and getup[0] > getup[-1] + 0.3 and all(a >= b - 0.001 for a, b in zip(getup, getup[1:])))
    else:
        check("%s: the break started (%s), the pack's knockdown montage played and no clip stage was reported" % (label, result), result == "started" and any((s["mname"] or "").startswith("Knockdown") for s in samples) and all(s["stage"] == "none" for s in samples), "%s" % stages)
    check("%s: the pelvis went down at least 30 cm (%.0f to %.0f) and the boss stands again (%.0f), not staggered" % (label, stand, lowest, last["pelvis"]), stand - lowest >= 30.0 and abs(last["pelvis"] - stand) <= 15.0 and not last["staggered"], "")


def script():
    yield from fresh()
    yield from stance_break("S1 first stance break")
    yield 1.0
    yield from stance_break("S2 second stance break")

    # S3 the roar
    yield from fresh()
    p = P()
    p["dbg"].debug_set_boss_health_fraction(0.55)
    t0 = S["now"]
    started = yield from until(lambda: P()["ph"].is_in_transition(), 3.0)
    t_start = S["now"]
    inst = boss_mesh().get_anim_instance()
    m = inst.get_current_active_montage() if inst else None
    clip = montage_clip_name(m) if m else None
    source = P()["ph"].get_roar_source_name()
    ended = yield from until(lambda: not P()["ph"].is_in_transition(), 4.0)
    length = S["now"] - t_start
    check("S3 the roar plays the project's clip (source %s, montage segment %s)" % (source, clip), started and source == "AN_Boss01_PhaseRoar" and clip == "AN_Boss01_PhaseRoar", "")
    check("S3 the transition lasts 1.8 s (%.2f) and ends" % length, ended and 1.5 <= length <= 2.3, "")

    # S4 the fallback to the pack's montages
    yield from fresh()
    P()["stg"].set_use_clips_for_test(False)
    yield from stance_break("S4 fallback", expect_clips=False)
    P()["stg"].set_use_clips_for_test(True)


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        P()["stg"].set_use_clips_for_test(True)
    except Exception:
        pass
    log("RESULT %d/%d passed" % (sum(1 for r in results if r), len(results)))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = S
    s["t"] += dt
    s["now"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    w, pc, pawn, boss = actors()
    if pawn is None or boss is None:
        return
    if s["samples"] is not None:
        sample()
    if s["wait"] > 0:
        s["wait"] -= dt
        return
    if s["gen"] is None:
        if s["t"] < 9.0:
            return
        s["gen"] = script()
    try:
        s["wait"] = float(next(s["gen"]))
    except StopIteration:
        finish()


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        check("tick raised", False)
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
