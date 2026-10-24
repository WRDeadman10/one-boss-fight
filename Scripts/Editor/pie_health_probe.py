"""Probe for the natural-wake health reset (Q7, 2026-10-23): logs the boss's current and maximum health from PIE start, wakes the encounter with the same calls the failing drivers use, and logs again every 0.2 s. No checks, no RESULT line is needed: read the [HealthProbe] lines.
Run after the warm-up (pie_debug_overlay.py, or RunDrivers). Log prefix [HealthProbe]."""
import unreal

log = lambda m: unreal.log("[HealthProbe] " + m)
state = {"phase": "start", "t": 0.0, "i": 0, "next": 0.0}
handle = None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def ctx():
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return w, pc, pawn, boss


def attr(boss, name):
    c = comp(boss, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="Attribute.Health")')
    try:
        return c.call_method(name, args=(t,))
    except Exception:
        return None


def sample(label):
    def fn(w, pc, pawn, boss):
        enc, ph = comp(boss, "RPGBossEncounter"), comp(boss, "RPGBossPhases")
        log("%s: health %s max %s dormant %s phase_two %s" % (label, attr(boss, "Get Current Attribute Value"), attr(boss, "GetMaxAttributeValue"), enc.is_dormant() if enc else None, ph.is_phase_two() if ph else None))
    return fn


def wake(w, pc, pawn, boss):
    enc = comp(boss, "RPGBossEncounter")
    log("WAKE now (enc.wake(), as pie_boss_hud does)")
    enc.wake()


STEPS = [(0.4, sample("pre %d" % k), True) for k in range(24)] + [(0.4, wake, True)] + [(0.2, sample("post %d" % k), True) for k in range(25)]


def _tick(dt):
    global handle
    s = state
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0, next=STEPS[0][0])
        return
    w, pc, pawn, boss = ctx()
    if pawn is None or boss is None or s["t"] < s["next"]:
        return
    if s["i"] >= len(STEPS):
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        log("DONE")
        return
    try:
        STEPS[s["i"]][1](w, pc, pawn, boss)
    except Exception:
        import traceback
        log("step raised " + traceback.format_exc())
    s["i"] += 1
    s["t"] = 0.0
    s["next"] = STEPS[s["i"]][0] if s["i"] < len(STEPS) else 0.5


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
