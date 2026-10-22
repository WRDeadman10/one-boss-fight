"""Probe (log prefix [AttrProbe]): what the pack's 'Modify Attribute' does to the player's stamina when called from Python (the same function the swing tracker calls from C++): -20, +5, -20 again, with a wait of one frame and of 0.5 s between.
Not a regression driver."""
import unreal

log = lambda m: unreal.log("[AttrProbe] " + m)
S = {"phase": "start", "t": 0.0, "now": 0.0, "wait": 0.0, "gen": None}
handle = None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def tag(name):
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % name)
    return t


def get(actor, name="Attribute.Stamina"):
    return comp(actor, "BP_AttributesComponent_C").call_method("Get Current Attribute Value", args=(tag(name),))


def modify(actor, delta, name="Attribute.Stamina"):
    comp(actor, "BP_AttributesComponent_C").call_method("Modify Attribute", args=(tag(name), 0, 0, delta))


def script(pawn):
    log("start stamina %.2f" % get(pawn))
    for delta in (-20.0, 5.0, -20.0, 15.0):
        before = get(pawn)
        modify(pawn, delta)
        same = get(pawn)
        yield 0.0
        nxt = get(pawn)
        yield 0.5
        later = get(pawn)
        log("modify %+.1f: before %.2f, same call %.2f, next frame %.2f, +0.5 s %.2f" % (delta, before, same, nxt, later))
    # the regeneration delay: how long until stamina comes back after -50
    modify(pawn, -50.0)
    for k in range(8):
        yield 0.5
        log("after -50, +%.1f s: %.2f" % (0.5 * (k + 1), get(pawn)))


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("done")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = S
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    if pawn is None:
        return
    if s["wait"] > 0:
        s["wait"] -= dt
        return
    if s["gen"] is None:
        if s["t"] < 9.0:
            return
        s["gen"] = script(pawn)
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
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
