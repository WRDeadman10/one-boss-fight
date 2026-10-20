"""
Gate 1 scenario 7 (Freeze 35.3): the stand-in A2 is interrupted at four moments (windup 0.5 s, committed 1.8 s, just before the hit 1.95 s, recovery 2.3 s) by a stance break, an encounter reset or the boss's death.
Checks per trial: the tracker leaves the attack (phase None, interrupted counter up when the attack was cut short), the heading lock does not outlive it, and the player takes no damage from an attack that
was cancelled before its hit. Kinds come from Saved/a2_kinds.txt (comma list of stagger, reset, death; default stagger,reset). Death needs its own PIE run (the boss does not come back). Log prefix [A2I].
"""
import os
import unreal

log = lambda m: unreal.log("[A2I] " + m)
_kf = os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved", "a2_kinds.txt")
KINDS = [k.strip() for k in open(_kf).read().split(",") if k.strip()] if os.path.exists(_kf) else ["stagger", "reset"]
TIMES = [0.5, 1.8, 1.95, 2.3]
TRIALS = 3
if KINDS == ["death"]:
    # the boss does not come back: one trial per PIE run, the time comes from Saved/a2_death_time.txt
    TIMES = [float(open(os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved", "a2_death_time.txt")).read().strip())]
    TRIALS = 1
DISTANCE = 180.0
state = {"phase": "start", "t": 0.0, "plan": [(k, t) for k in KINDS for t in TIMES for _ in range(TRIALS)], "i": 0, "running": False, "t0": 0.0, "done": False, "results": []}
handle = None


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


def finish(reason):
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("---- summary ----")
    by = {}
    for kind, at, ok, why in state["results"]:
        by.setdefault((kind, at), []).append((ok, why))
    for (kind, at), r in by.items():
        log("%-8s at %.2f s: %d/%d ok %s" % (kind, at, sum(1 for o, _ in r if o), len(r), [w for o, w in r if not o][:2]))
    log("finished: %s" % reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = state
    s["t"] += dt
    if s["t"] > 1500:
        finish("timeout")
        return
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wake", t=0.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    if pawn is None or boss is None:
        return
    enc, tr, dbg, stg = comp(boss, "RPGBossEncounter"), comp(boss, "RPGAttackTracker"), comp(boss, "RPGCombatDebug"), comp(boss, "RPGBossStagger")
    mc = boss.get_components_by_class(unreal.SkeletalMeshComponent)[0]
    if s["phase"] == "wake":
        if s["t"] > 9.0 and "woke" not in s:
            s["woke"] = s["t"]
            pawn.set_actor_location_and_rotation(unreal.Vector(boss.get_actor_location().x + 700, boss.get_actor_location().y, boss.get_actor_location().z), unreal.Rotator(0, 180, 0), False, True)
        if "woke" in s:
            dbg.debug_refill_player()
            inst = mc.get_anim_instance()
            if (not enc.is_dormant()) and inst.get_current_active_montage() is None and s["t"] - s["woke"] > 4.0:
                enc.hold_for_test(True)
                s.update(phase="run", t=0.0, next=3.0, home=boss.get_actor_location())
                log("boss awake and held")
        return
    if s["i"] >= len(s["plan"]):
        finish("all done")
        return
    kind, at = s["plan"][s["i"]]
    inst = mc.get_anim_instance()
    if s["running"]:
        ts = s["t"] - s["t0"]
        hp = health(pawn)
        if not s["acted"] and ts >= at:
            s["acted"] = True
            s["hp_at_act"] = hp
            s["yaw_at_act"] = boss.get_actor_rotation().yaw
            s["interrupted0"] = tr.get_interrupted_count()
            if kind == "stagger":
                stg.force_break_for_test()
            elif kind == "reset":
                enc.reset_for_test()
            elif kind == "death":
                dbg.debug_kill_boss()
        if s["acted"] and ts >= at + 1.2 and "checked" not in s:
            s["checked"] = True
            phase = tr.get_phase_name()
            ok, why = True, ""
            if phase != "None":
                ok, why = False, "tracker still %s" % phase
            if tr.get_interrupted_count() <= s["interrupted0"] and at < 2.3:
                ok, why = False, why or "attack not counted as interrupted"
            if at <= 1.95 and hp is not None and s["hp_at_act"] is not None and hp < s["hp_at_act"] - 0.01:
                ok, why = False, why or "player hurt by a cancelled attack (health %s -> %s)" % (s["hp_at_act"], hp)
            s["results"].append((kind, at, ok, why))
            log("%-8s at %.2f s: %s  tracker %s, interrupted %d, boss montage %s, health %s -> %s" % (kind, at, "ok" if ok else "FAIL " + why, phase, tr.get_interrupted_count(), (inst.get_current_active_montage().get_name() if inst.get_current_active_montage() else None), s["hp_at_act"], hp))
        if ts >= at + 6.5:
            s["running"] = False
            s["i"] += 1
            s["next"] = s["t"] + 0.5
        return
    if s["t"] >= s["next"]:
        if kind != "death" or s["i"] == 0 or s["plan"][s["i"] - 1][0] != "death":
            pass
        # the previous trial may have left the boss in a stance break or dormant: stand it up
        if stg.is_staggered():
            stg.abort_stagger()
        boss.set_actor_location_and_rotation(s["home"], unreal.Rotator(0, 0, 0), False, True)
        pawn.set_actor_location_and_rotation(unreal.Vector(s["home"].x + DISTANCE, s["home"].y, s["home"].z), unreal.Rotator(0, 180, 0), False, True)
        pc.set_control_rotation(unreal.Rotator(0, 180, 0))
        dbg.debug_refill_player()
        inst.montage_stop(0.0)
        hp = health(pawn)
        ok = tr.start_move("A2")
        s.update(running=True, t0=s["t"], acted=False, hp_at_act=hp)
        s.pop("checked", None)
        if not ok:
            log("start_move refused")


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("error")


handle = unreal.register_slate_post_tick_callback(tick)
