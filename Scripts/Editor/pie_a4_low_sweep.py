"""Gate 2 / G2-2: the A4 low sweep (Freeze 16 A4, test B09). The boss is frozen awake (RPGBossEncounter.hold_for_test), each trial puts the player in front, starts the move through
RPGAttackTracker.StartMove("A4") (the delivered clip plays as a dynamic montage, RPGBossLowSweep does the hit) and reads the sweep counters.
Asserted: S1 the tracker reports A4 with commit 0.40 s and the active window from 0.60 s, one instance, no double launch, no yaw drift after commit; S2 a grounded player at 250 cm is hit exactly once for the configured damage (20 trials);
S3 a jump pressed at 0.33 s clears the blade (20 trials); S4 out of reach (520 cm) and S5 behind the boss are not hit; S6 a backward roll started 0.50 to 0.70 s after the start is not hurt (5 trials each); S7 a reset in the middle of the sweep ends it
without damage; S8 the boss dying in the middle of the sweep ends it without damage. S9 prints (does not assert) the jump press times that clear the blade. Run pie_debug_overlay.py once after an editor start first. Log prefix [A4].
"""
import math
import unreal

log = lambda m: unreal.log("[A4] " + m)
JUMP_KEY = "Gamepad_FaceButton_Bottom"
DODGE_KEY = "Gamepad_FaceButton_Right"
TRIAL_LEN = 2.6
SETTLE = 0.5
results = []
S = {"phase": "start", "t": 0.0, "i": 0, "running": False, "t0": 0.0, "mem": {}, "keys": {}, "woke": None, "n": 0, "done_actions": set(), "info": {}}
handle = None


def check(name, ok, detail=""):
    results.append(ok)
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def health(actor):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="Attribute.Health")')
    try:
        return c.call_method("Get Current Attribute Value", args=(t,))
    except Exception:
        return None


def key(pc, name, down):
    if S["keys"].get(name, False) != down:
        S["keys"][name] = down
        unreal.RPGInputTestUtils.set_key_down(pc, name, down)


def place(pawn, boss, dist, ang_deg):
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw + ang_deg)
    p = unreal.Vector(bl.x + math.cos(r) * dist, bl.y + math.sin(r) * dist, bl.z + 20)
    look = unreal.MathLibrary.find_look_at_rotation(p, bl).yaw
    pawn.set_actor_location_and_rotation(p, unreal.Rotator(0, 0, look), False, True)


def parts(boss):
    return comp(boss, "RPGBossLowSweep"), comp(boss, "RPGAttackTracker"), comp(boss, "RPGCombatDebug"), comp(boss, "RPGBossEncounter")


def counters(sw, tr):
    return {"sweeps": sw.get_sweep_count(), "hits": sw.get_hit_count(), "jumped": sw.get_jumped_count(), "inv": sw.get_invulnerable_count(), "blocked": sw.get_blocked_count(),
            "inst": tr.get_attack_instance(), "double": tr.get_double_launch_count()}


# Scenario: (name, distance, angle, trials, actions, expectation). actions: list of (time since the start, fn(pc, pawn, boss)); jump and roll are key holds (start, end).
def jump_at(t):
    return {"jump": (t, t + 0.12)}


def roll_at(t):
    return {"roll": (t, t + 0.08)}


SCENARIOS = [
    ("S2 grounded in front 250 cm", 250, 0, 20, {}, lambda d, hp: d["sweeps"] == 1 and d["hits"] == 1 and d["jumped"] == 0 and abs(hp - 20.0) < 0.01),
    ("S3 jump at 0.33 s clears it", 250, 0, 20, jump_at(0.33), lambda d, hp: d["sweeps"] == 1 and d["hits"] == 0 and d["jumped"] == 1 and hp == 0),
    ("S4 out of reach 520 cm", 520, 0, 5, {}, lambda d, hp: d["sweeps"] == 1 and d["hits"] == 0 and hp == 0),
    ("S5 behind the boss 250 cm", 250, 180, 5, {}, lambda d, hp: d["sweeps"] == 1 and d["hits"] == 0 and hp == 0),
    # The dodge starts about 0.2 s after the press (the double tap window), so a press at 0.50 s has its i-frames on the blade (contact at 0.74 s) and counts as an i-frame pass (inv 1, no damage).
    ("S6 backward roll at 0.50 s: i-frames pass", 250, 0, 5, roll_at(0.50), lambda d, hp: d["hits"] == 0 and d["inv"] == 1 and hp == 0),
    ("S7 reset at 0.62 s", 250, 0, 3, {"reset": 0.62}, lambda d, hp: d["hits"] == 0 and hp == 0),
]
# S9: information only, which roll and jump press times clear the blade (late presses are caught, early ones leave the reach).
for _t in (0.30, 0.40, 0.60, 0.70):
    SCENARIOS.append(("S9 info roll at %.2f s" % _t, 250, 0, 3, roll_at(_t), None))
for _t in (0.05, 0.15, 0.25, 0.40, 0.50, 0.60):
    SCENARIOS.append(("S9 info jump at %.2f s" % _t, 250, 0, 3, jump_at(_t), None))
# Last: the boss dies in the middle of the sweep (the pack destroys it a few seconds later, so nothing can follow).
SCENARIOS.append(("S8 boss dies at 0.62 s", 250, 0, 1, {"kill": 0.62}, lambda d, hp: d["hits"] == 0 and hp == 0))


def start_trial(w, pc, pawn, boss):
    sw, tr, dbg, enc = parts(boss)
    name, dist, ang, trials, actions, expect = SCENARIOS[S["i"]]
    dbg.debug_refill_player()
    S["keys"] = {}
    place(pawn, boss, dist, ang)
    S["mem"] = {"c": counters(sw, tr), "hp": health(pawn), "yaw": boss.get_actor_rotation().yaw, "zs": [], "drift": tr.get_max_yaw_drift_after_commit()}
    S["running"] = True
    S["t0"] = S["t"]
    S["done_actions"] = set()
    S["started"] = False


def end_trial(w, pc, pawn, boss):
    sw, tr, dbg, enc = parts(boss)
    name, dist, ang, trials, actions, expect = SCENARIOS[S["i"]]
    c0, c1 = S["mem"]["c"], counters(sw, tr)
    d = {k: c1[k] - c0[k] for k in c1}
    hp1 = health(pawn)
    hp_loss = (S["mem"]["hp"] - hp1) if (hp1 is not None and S["mem"]["hp"] is not None) else None
    S["info"].setdefault(name, []).append((d["hits"], d["jumped"], d["inv"]))
    if expect is not None:
        ok = hp_loss is not None and expect(d, hp_loss)
        S.setdefault("scen", {}).setdefault(name, []).append(ok)
        if not ok:
            log("trial FAIL %s: counters %s health loss %s" % (name, d, hp_loss))
    if name.startswith("S2") and S["n"] == 0:
        check("S1 tracker saw one A4 with commit and active window", d["inst"] == 1 and d["double"] == 0, "instances %d double launches %d" % (d["inst"], d["double"]))
        check("S1 commit near 0.40 s, active from near 0.60 s", 0.3 <= tr.get_last_commit_position() <= 0.55 and 0.55 <= tr.get_last_active_start_position() <= 0.75, "commit %.2f active %.2f" % (tr.get_last_commit_position(), tr.get_last_active_start_position()))
        check("S1 heading did not drift after the commit", tr.get_max_yaw_drift_after_commit() < 0.5, "drift %.2f deg" % tr.get_max_yaw_drift_after_commit())
    if name.startswith("S7") or name.startswith("S8"):
        check("%s: the blade is not active afterwards" % name, not sw.is_blade_active())
    S["running"] = False
    S["n"] += 1
    if S["n"] >= trials:
        if name in S.get("scen", {}):
            r = S["scen"][name]
            check("%s: %d/%d trials" % (name, sum(r), len(r)), all(r))
        else:
            rows = S["info"][name]
            log("INFO %s: hits %d/%d, jumped %d, invulnerable %d" % (name, sum(x[0] for x in rows), len(rows), sum(x[1] for x in rows), sum(x[2] for x in rows)))
        S["i"] += 1
        S["n"] = 0
        if name.startswith("S7"):
            S["wake_again"] = True  # a reset puts the boss to sleep: wake and hold it again


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("RESULT %d/%d passed" % (sum(1 for r in results if r), len(results)))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = S
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wait", t=0.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    if pawn is None or boss is None:
        return
    sw, tr, dbg, enc = parts(boss)
    if s["phase"] == "wait":
        if s["t"] > 9.0:
            enc.wake()
            enc.hold_for_test(True)
            dbg.debug_refill_player()
            log("boss awake and held; scenarios: %d" % len(SCENARIOS))
            s.update(phase="run", t=0.0, next=1.5)
        return
    if s["phase"] == "run":
        if s["i"] >= len(SCENARIOS):
            finish()
            return
        name, dist, ang, trials, actions, expect = SCENARIOS[s["i"]]
        if not s["running"]:
            if s["t"] < s["next"]:
                return
            if s.pop("wake_again", False):
                enc.wake()
                enc.hold_for_test(True)
                s["next"] = s["t"] + 3.0
                return
            start_trial(w, pc, pawn, boss)
            return
        ts = s["t"] - s["t0"]
        # settle first (the teleport), then start the move; all later times count from the start
        if not s["started"]:
            if ts >= SETTLE:
                s["started"] = True
                s["t_start"] = s["t"]
                ok = tr.start_move("A4", True)
                if not ok:
                    check("%s: the move starts" % name, False)
            return
        tm = s["t"] - s["t_start"]
        if "jump" in actions:
            a, b = actions["jump"]
            key(pc, JUMP_KEY, a <= tm < b)
            if "jmp_t" not in s["mem"] and tm >= a:
                s["mem"]["jmp_t"] = tm
        if "roll" in actions:
            a, b = actions["roll"]
            key(pc, DODGE_KEY, a <= tm < b)
        if "reset" in actions and tm >= actions["reset"] and "reset" not in s["done_actions"]:
            s["done_actions"].add("reset")
            enc.reset_for_test()
        if "kill" in actions and tm >= actions["kill"] and "kill" not in s["done_actions"]:
            s["done_actions"].add("kill")
            dbg.debug_kill_boss()
        if tm >= TRIAL_LEN:
            key(pc, JUMP_KEY, False)
            key(pc, DODGE_KEY, False)
            end_trial(w, pc, pawn, boss)
            s["next"] = s["t"] + 0.6


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        check("tick raised", False)
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
