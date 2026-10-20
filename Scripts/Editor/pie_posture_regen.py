"""Freeze S03/S04: boss posture regeneration. Drains posture to 40, samples it for 16 s; a second drain at 3 s must restart the delay. Expected: no gain for 6 s after the LAST drain, then 13 per second.
Log prefix [Posture]."""
import unreal

log = lambda m: unreal.log("[Posture] " + m)
state = {"t": 0.0, "phase": "start", "step": 0, "last": -1}
handle = None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def _tick(dt):
    global handle
    s = state
    s["t"] += dt
    if s["phase"] == "start" and s["t"] > 0.5:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
        s.update(phase="play", t=0.0)
        return
    if s["phase"] != "play":
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    if boss is None:
        return
    post, dbg = comp(boss, "RPGBossPosture"), comp(boss, "RPGCombatDebug")
    t = s["t"]
    if s["step"] == 0 and t > 9.0 and post.is_configured():
        dbg.debug_drain_boss_posture(60.0)
        s.update(step=1, t1=t)
        log("configured=%s, posture drained by 60" % post.is_configured())
    if s["step"] == 1:
        el = t - s["t1"]
        if el >= 3.0 and not s.get("second"):
            dbg.debug_drain_boss_posture(10.0)
            s["second"] = True
            log("t=%.1f second drain by 10 (to 30)" % el)
        if int(el * 2) != s["last"]:
            s["last"] = int(el * 2)
            log("t=%.1f posture %.1f drains %d" % (el, post.get_posture(), post.get_drain_count()))
        if el > 18:
            unreal.unregister_slate_post_tick_callback(handle)
            handle = None
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
            log("done")


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
