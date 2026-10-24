"""Fog gate states in PIE (Gate 2 entrance moment): Idle while the boss sleeps, Closed (blocking, full mist) when it wakes, Idle again after an encounter reset, Cleared (open, mist gone) when the boss dies.
Log prefix [FogGate]."""
import unreal

log = lambda m: unreal.log("[FogGate] " + m)
state = {"phase": "start", "t": 0.0, "step": 0, "wait": 0.0, "res": [], "retries": {}}
handle = None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def check(name, ok, detail=""):
    state["res"].append((name, ok))
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    bad = [n for n, ok in state["res"] if not ok]
    log("SUMMARY %d checks, %d failed %s" % (len(state["res"]), len(bad), bad))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = state
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0, wait=9.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    gate = next(iter(unreal.GameplayStatics.get_all_actors_of_class(w, unreal.RPGFogGate)), None) if w else None
    if pawn is None or boss is None or gate is None or s["t"] < s["wait"]:
        return
    enc, dbg = comp(boss, "RPGBossEncounter"), comp(boss, "RPGCombatDebug")
    bl = boss.get_actor_location()
    n = s["step"]

    def nxt(wait):
        s["step"] += 1
        s["wait"] = s["t"] + wait

    def retry_once(key, detail, action, wait):
        if s["retries"].get(key):
            return False
        s["retries"][key] = True
        log("INFO retry %s: %s" % (key, detail))
        action()
        s["wait"] = s["t"] + wait
        return True

    if n == 0:
        check("Idle while the boss sleeps", gate.get_state_name() == "Idle" and not gate.is_blocking() and abs(gate.get_amount() - 0.35) < 0.05, "%s amount %.2f blocking %s" % (gate.get_state_name(), gate.get_amount(), gate.is_blocking()))
        pawn.set_actor_location_and_rotation(unreal.Vector(bl.x + 700, bl.y, bl.z), unreal.Rotator(0, 180, 0), False, True)
        nxt(0.8)
    elif n == 1:
        closed = gate.get_state_name() == "Closed" and gate.is_blocking()
        if not closed and retry_once("wake-1", "gate did not close after the approach; calling wake once more", enc.wake, 1.0):
            return
        check("Closed and blocking when the boss wakes", closed, "%s blocking %s" % (gate.get_state_name(), gate.is_blocking()))
        enc.hold_for_test(True)
        nxt(2.2)
    elif n == 2:
        full = gate.get_amount() > 0.98
        if not full and retry_once("fade-1", "mist had not reached full amount; refreshing wake once", enc.wake, 1.5):
            return
        check("Full mist after the fade", full, "amount %.2f" % gate.get_amount())
        enc.reset_for_test()
        dbg.debug_refill_player()
        nxt(2.5)
    elif n == 3:
        open_again = gate.get_state_name() == "Idle" and not gate.is_blocking() and abs(gate.get_amount() - 0.35) < 0.05
        if not open_again and retry_once("reset", "gate did not reopen after reset; repeating reset once", enc.reset_for_test, 2.5):
            dbg.debug_refill_player()
            return
        check("Open and thin again after an encounter reset", open_again, "%s amount %.2f blocking %s" % (gate.get_state_name(), gate.get_amount(), gate.is_blocking()))
        enc.wake()
        enc.hold_for_test(True)
        nxt(1.0)
    elif n == 4:
        closed_again = gate.get_state_name() == "Closed" and gate.is_blocking()
        if not closed_again and retry_once("wake-2", "gate did not close on the second wake; calling wake once more", enc.wake, 1.0):
            return
        check("Closed again at the second wake", closed_again)
        dbg.debug_kill_boss()
        nxt(2.4)
    elif n == 5:
        cleared = gate.get_state_name() == "Cleared" and not gate.is_blocking() and gate.get_amount() < 0.02
        if not cleared and retry_once("kill", "gate did not clear after kill; issuing one kill request again", dbg.debug_kill_boss, 2.4):
            return
        check("Cleared and open when the boss is dead", cleared, "%s amount %.2f blocking %s" % (gate.get_state_name(), gate.get_amount(), gate.is_blocking()))
        finish()
        s["step"] = 99


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
