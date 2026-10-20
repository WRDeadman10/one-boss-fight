"""
Gate 1 / G1-9: scripted A2 timing scenarios (Freeze 35.3) against the stand-in attack (the pack's GS_ChargedAttack, tag Ability.Melee.CloseRare).
The boss is frozen dormant (RPGBossEncounter.bTestFreeze); each trial teleports the player in front of it, starts the move through RPGAttackTracker.StartMove("A2"), plays scripted input, and records
whether the player lost health, when, and the tracker's commit data. Open L_SevarogArena first; run with Scripts/run_in_editor.py. Log prefix [A2].
"""
import math
import unreal

log = lambda m: unreal.log("[A2] " + m)
DODGE_KEY = "Gamepad_FaceButton_Right"
DISTANCE = 200.0          # cm from the boss to the player at the start
TRIAL_LEN = 4.2
SETTLE = 2.0
TRIALS = 3
# (name, dodge press time or None, stick vector during the dodge, move start time or None, move stick vector)
SCENARIOS = [("stand still", None, None, None, None)]
for t in (0.30, 0.60, 0.90, 1.10, 1.25, 1.35, 1.45, 1.55, 1.65, 1.80, 1.95, 2.10, 2.30):
    SCENARIOS.append(("roll forward at %.2f" % t, t, (0.0, 1.0), None, None))
for t in (0.9, 1.25, 1.45):
    SCENARIOS.append(("roll sideways at %.2f" % t, t, (-1.0, 0.0), None, None))
SCENARIOS.append(("roll backward (no stick) at 1.10", 1.10, None, None, None))
for t in (0.4, 1.0, 1.45):
    SCENARIOS.append(("walk away left from %.2f" % t, None, None, t, (-1.0, 0.0)))
import os
_flt = os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved", "a2_filter.txt")
if os.path.exists(_flt):
    _words = [w.strip() for w in open(_flt, encoding="utf-8").read().split(",") if w.strip()]
    SCENARIOS = [sc for sc in SCENARIOS if any(w in sc[0] for w in _words)]
state = {"dmax": 0.0, "dhit": None, "keys": {}, "phase": "start", "t": 0.0, "i": 0, "n": 0, "running": False, "t0": 0.0, "hp0": None, "hit_t": None, "hp_min": None, "next": 0.0, "results": {}, "pass": 0}
handle = None


def world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def tags(*names):
    c = unreal.GameplayTagContainer()
    c.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return c


def health(actor):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="Attribute.Health")')
    try:
        return c.call_method("Get Current Attribute Value", args=(t,)) if c else None
    except Exception:
        return None


def key(pc, name, down):
    if state["keys"].get(name, False) != down:
        state["keys"][name] = down
        unreal.RPGInputTestUtils.set_key_down(pc, name, down)


def stick(pc, vec):
    unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Move"), unreal.Vector(vec[0], vec[1], 0))


def finish(reason):
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("---- summary (hits/trials, mean time of the hit) ----")
    for name, r in state["results"].items():
        hits = [x for x in r if x is not None]
        log("%-34s hit %d/%d%s" % (name, len(hits), len(r), ("  at %.2f s" % (sum(hits) / len(hits))) if hits else ""))
    log("finished: %s" % reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = state
    s["t"] += dt
    if s["t"] > 1500.0:
        finish("timeout")
        return
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wait", t=0.0)
        return
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    if pawn is None:
        return
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None)
    if s["phase"] == "wait":
        # wake the boss by standing close, let it draw its sword, then stop its behaviour
        if s["t"] > 9.0 and boss is not None and "woke" not in s:
            s["woke"] = s["t"]
            pawn.set_actor_location_and_rotation(unreal.Vector(boss.get_actor_location().x + 700, boss.get_actor_location().y, boss.get_actor_location().z), unreal.Rotator(0, 180, 0), False, True)
        if "woke" in s:
            dbg = comp(boss, "RPGCombatDebug")
            if dbg:
                dbg.debug_refill_player()
            mc = boss.get_components_by_class(unreal.SkeletalMeshComponent)
            inst = mc[0].get_anim_instance() if mc else None
            armed = (not comp(boss, "RPGBossEncounter").is_dormant()) and inst is not None and inst.get_current_active_montage() is None  # awake and between two attacks (the pack boss has no weapon actor: its sword is part of the mesh)
            if armed and s["t"] - s["woke"] > 4.0:
                comp(boss, "RPGBossEncounter").hold_for_test(True)
                log("boss armed and held")
                s.update(phase="run", t=0.0, next=3.0, home=boss.get_actor_location())
            elif s["t"] - s["woke"] > 40.0:
                log("boss never armed")
                finish("boss never armed")
        return
    tr = comp(boss, "RPGAttackTracker")
    dbg = comp(boss, "RPGCombatDebug")
    if s["i"] >= len(SCENARIOS):
        finish("all scenarios done")
        return
    name, dodge_t, dodge_stick, move_t, move_stick = SCENARIOS[s["i"]]
    if s["running"]:
        ts = s["t"] - s["t0"]
        # input
        if dodge_t is not None:
            key(pc, DODGE_KEY, dodge_t <= ts < dodge_t + 0.08)
            if dodge_stick is not None and dodge_t - 0.15 <= ts < dodge_t + 0.5:
                stick(pc, dodge_stick)
        if move_t is not None and ts >= move_t:
            stick(pc, move_stick)
        # outcome
        dist = (pawn.get_actor_location() - boss.get_actor_location()).length()
        s["dmax"] = max(s["dmax"], dist)
        hp = health(pawn)
        if hp is not None:
            if s["hp_min"] is None or hp < s["hp_min"] - 0.01:
                if s["hp0"] is not None and hp < s["hp0"] - 0.01 and s["hit_t"] is None:
                    s["hit_t"] = ts
                    s["dhit"] = dist
                s["hp_min"] = hp
        if ts >= TRIAL_LEN:
            key(pc, DODGE_KEY, False)
            res = s["results"].setdefault(name, [])
            res.append(s["hit_t"])
            log("%-34s trial %d: %s  health %s -> %s  player distance at the hit %s, farthest %.0f cm; boss commit at %.2f, active at %.2f, yaw drift %.1f deg, commits %d, interrupted %d" % (name, s["n"] + 1, ("HIT at %.2f s" % s["hit_t"]) if s["hit_t"] is not None else "no damage", s["hp0"], s["hp_min"], ("%.0f" % s["dhit"]) if s["dhit"] is not None else "-", s["dmax"],
                tr.get_last_commit_position(), tr.get_last_active_start_position(), tr.get_max_yaw_drift_after_commit(), tr.get_commit_count(), tr.get_interrupted_count()))
            s["running"] = False
            s["next"] = s["t"] + SETTLE
            s["n"] += 1
            if s["n"] >= TRIALS:
                s["n"] = 0
                s["i"] += 1
        return
    if s["t"] >= s["next"]:
        # reset: boss home facing +X, player in front facing the boss, full health, no leftover montage
        boss.set_actor_location_and_rotation(s["home"], unreal.Rotator(0, 0, 0), False, True)
        pawn.set_actor_location_and_rotation(unreal.Vector(s["home"].x + DISTANCE, s["home"].y, s["home"].z), unreal.Rotator(0, 180, 0), False, True)
        pc.set_control_rotation(unreal.Rotator(0, 180, 0))
        if dbg:
            dbg.debug_refill_player()
        s["keys"] = {}
        ok = tr.start_move("A2")
        hp = health(pawn)
        s.update(running=True, t0=s["t"], hp0=hp, hp_min=hp, hit_t=None, dmax=0.0, dhit=None)
        if not ok:
            log("start_move refused")


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("error")


assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name() == "L_SevarogArena", "open L_SevarogArena first"
handle = unreal.register_slate_post_tick_callback(tick)
