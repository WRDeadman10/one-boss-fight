"""Lead-run PIE comparison of Ember A1/A3a/A3b with notify timing disabled/enabled.

This driver is intentionally authored but not executed by Codex. It runs each
move twice in one held encounter, samples tracker transitions, and attempts a
parry 0.08 seconds before the earliest C-1132 observed hit position. The final
comparison applies an 0.08-second contact/phase-position tolerance derived from
that C-1132 timing margin; it is a bounded parity probe, not a replacement for
the C-1132/C-1152 full acceptance matrix.
"""
import json
import unreal

LOG = "[EmberNotifyParity] "
MOVES = ("A1", "A3a", "A3b")
# Earliest Lead-observed PLAYER_HIT positions in C-1132 (montage-local seconds).
C1132_CONTACT_SECONDS = {"A1": 0.351, "A3a": 0.484, "A3b": 0.152}
C1132_PARRY_LEAD_SECONDS = 0.08
C1132_PARITY_TOLERANCE_SECONDS = 0.08
MAX_MOVE_SECONDS = {"A1": 1.6, "A3a": 1.2, "A3b": 1.8}
S = {"phase": "start", "elapsed": 0.0, "wake": 0.0, "finished": False,
     "rows": {}, "checks": [], "initial_timing_mode": None, "task": 0,
     "wait_started": None, "next_wait_heartbeat": 0.0, "result_emitted": False}
HANDLE = None
TASKS = [(enabled, move) for enabled in (False, True) for move in MOVES]
WAIT_BOSS_TIMEOUT_SECONDS = 15.0
WAIT_HEARTBEAT_SECONDS = 2.0


def log(message):
    unreal.log(LOG + str(message))


def check(name, passed, detail=""):
    S["checks"].append(bool(passed))
    log("CHECK %s %s %s" % ("PASS" if passed else "FAIL", name, detail))


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def component(actor, class_name):
    if actor is None:
        return None
    return next((item for item in actor.get_components_by_class(unreal.ActorComponent)
                 if item.get_class().get_name() == class_name), None)


def parts():
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((actor for actor in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character)
                 if actor.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return (component(boss, "RPGAttackTracker"), component(boss, "RPGBossEncounter"),
            component(boss, "RPGCombatDebug"), component(pawn, "RPGPlayerParry"), pawn, boss)


def front(pawn, boss):
    # A3b is a branch stage; keep the pawn inside its live 400 cm frontal gate.
    location = boss.get_actor_location() + boss.get_actor_forward_vector() * 180.0
    pawn.set_actor_location_and_rotation(
        unreal.Vector(location.x, location.y, boss.get_actor_location().z),
        unreal.Rotator(0, 0, 0), False, True)


def record_for(enabled, move):
    key = ("on" if enabled else "off", move)
    return S["rows"].setdefault(key, {"phases": {}, "parry_contacts": [], "started": False, "ended": False})


def set_timing_mode(tracker, enabled):
    tracker.set_use_montage_notify_timings_for_test(bool(enabled))
    return bool(tracker.get_use_montage_notify_timings_for_test())


def run_one(enabled, move, tracker, debug, parry, pawn, boss):
    label = "on" if enabled else "off"
    actual = set_timing_mode(tracker, enabled)
    check("%s %s timing flag readback" % (label, move), actual == enabled, "readback=%s" % actual)
    front(pawn, boss)
    debug.debug_set_boss_health_fraction(1.0)
    if debug:
        debug.debug_refill_player()
    row = record_for(enabled, move)
    before_parries = parry.get_parried_count() if parry else -1
    if not tracker.play_move_montage_for_test(move):
        check("%s %s montage starts" % (label, move), False, "PlayMoveMontageForTest refused")
        return
    check("%s %s montage starts" % (label, move), True)
    log("MOVE_BEGIN mode=%s move=%s" % (label, move))
    previous_phase = None
    parry_sent = False
    limit = MAX_MOVE_SECONDS[move]
    started_at = S["elapsed"]
    while S["elapsed"] - started_at <= limit:
        current_move = str(tracker.get_current_move())
        phase = str(tracker.get_phase_name())
        position = float(tracker.get_position())
        if current_move == move and phase not in ("None", ""):
            row["started"] = True
            if phase != previous_phase:
                log("TRANSITION mode=%s move=%s phase=%s pos=%.4f commit_pos=%.4f active_pos=%.4f" % (
                    label, move, phase, position, float(tracker.get_last_commit_position()),
                    float(tracker.get_last_active_start_position())))
                if phase in ("Committed", "Active", "Recovery"):
                    row["phases"].setdefault(phase, position)
                previous_phase = phase
        elif row["started"] and phase in ("None", ""):
            row["ended"] = True
            row["phases"].setdefault("Complete", position)
            log("TRANSITION mode=%s move=%s phase=Complete pos=%.4f" % (label, move, position))
            break

        if not parry_sent and position >= C1132_CONTACT_SECONDS[move] - C1132_PARRY_LEAD_SECONDS:
            parry_sent = bool(parry and parry.press())
            log("PARRY_PRESS mode=%s move=%s pos=%.4f opened=%s target=%.4f lead=%.3f" % (
                label, move, position, parry_sent, C1132_CONTACT_SECONDS[move], C1132_PARRY_LEAD_SECONDS))

        if parry and parry.get_parried_count() > before_parries:
            contact_position = float(tracker.get_position())
            row["parry_contacts"].append(contact_position)
            before_parries = parry.get_parried_count()
            log("PARRY_CONTACT mode=%s move=%s pos=%.4f total=%d" % (
                label, move, contact_position, before_parries))
        yield 0.0

    check("%s %s tracker completed" % (label, move), row["started"] and row["ended"],
          "phases=%s" % json.dumps(row["phases"], sort_keys=True))
    check("%s %s parry contact recorded" % (label, move), bool(row["parry_contacts"]),
          "contacts=%s" % json.dumps(row["parry_contacts"]))


def compare_results():
    for move in MOVES:
        off = S["rows"].get(("off", move), {})
        on = S["rows"].get(("on", move), {})
        for phase in ("Committed", "Active", "Recovery", "Complete"):
            off_value = off.get("phases", {}).get(phase)
            on_value = on.get("phases", {}).get(phase)
            ok = off_value is not None and on_value is not None and abs(off_value - on_value) <= C1132_PARITY_TOLERANCE_SECONDS
            check("%s %s parity" % (move, phase), ok,
                  "off=%s on=%s tolerance=%.3f" % (off_value, on_value, C1132_PARITY_TOLERANCE_SECONDS))
        for mode, row in (("off", off), ("on", on)):
            contacts = row.get("parry_contacts", [])
            within = any(abs(value - C1132_CONTACT_SECONDS[move]) <= C1132_PARITY_TOLERANCE_SECONDS for value in contacts)
            check("%s %s C-1132 contact" % (mode, move), within,
                  "observed=%s target=%.4f tolerance=%.3f" % (contacts, C1132_CONTACT_SECONDS[move], C1132_PARITY_TOLERANCE_SECONDS))
    emit_result()


def emit_result():
    if S["result_emitted"]:
        return
    S["result_emitted"] = True
    passed = bool(S["checks"]) and all(S["checks"])
    log("RESULT %s checks=%d/%d C1132_tolerance=%.3fs" % (
        "PASS" if passed else "FAIL", sum(S["checks"]), len(S["checks"]), C1132_PARITY_TOLERANCE_SECONDS))


def scenario():
    yield 2.0
    tracker, encounter, debug, parry, pawn, boss = parts()
    for name, value in (("tracker", tracker), ("encounter", encounter), ("debug", debug), ("parry", parry), ("pawn", pawn), ("boss", boss)):
        check("component %s exists" % name, value is not None)
    if any(value is None for value in (tracker, encounter, debug, parry, pawn, boss)):
        return
    S["initial_timing_mode"] = bool(tracker.get_use_montage_notify_timings_for_test())
    encounter.wake()
    encounter.hold_for_test(True)
    debug.debug_refill_player()
    for enabled, move in TASKS:
        yield from run_one(enabled, move, tracker, debug, parry, pawn, boss)
        yield 0.35
    set_timing_mode(tracker, S["initial_timing_mode"])
    compare_results()


def finish():
    global HANDLE
    if S["finished"]:
        return
    S["finished"] = True
    tracker, encounter, debug, parry, pawn, boss = parts()
    if tracker is not None and S["initial_timing_mode"] is not None:
        set_timing_mode(tracker, S["initial_timing_mode"])
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    log("RECEIPT " + json.dumps({"rows": {"%s:%s" % key: value for key, value in S["rows"].items()},
                                 "checks": len(S["checks"])}, sort_keys=True, separators=(",", ":")))
    emit_result()
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    log("finished: parity probe complete")


def tick(delta_seconds):
    try:
        S["elapsed"] += delta_seconds
        if S["phase"] == "start":
            if S["elapsed"] >= 0.5:
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                S["phase"] = "wait"
                S["wait_started"] = S["elapsed"]
                S["next_wait_heartbeat"] = S["elapsed"]
            return
        if S["phase"] == "wait":
            current_parts = parts()
            if all(current_parts):
                S["phase"] = "run"
                return
            missing = [name for name, value in zip(("tracker", "encounter", "debug", "parry", "pawn", "boss"), current_parts) if value is None]
            if S["elapsed"] >= S["next_wait_heartbeat"]:
                log("WAIT_HEARTBEAT elapsed=%.1f missing=%s" % (S["elapsed"] - S["wait_started"], ",".join(missing)))
                S["next_wait_heartbeat"] = S["elapsed"] + WAIT_HEARTBEAT_SECONDS
            if S["elapsed"] - S["wait_started"] >= WAIT_BOSS_TIMEOUT_SECONDS:
                check("boss and probe components appear before timeout", False,
                      "elapsed=%.1f missing=%s" % (S["elapsed"] - S["wait_started"], ",".join(missing)))
                finish()
            return
        if S["phase"] == "run":
            if S["elapsed"] < S["wake"]:
                return
            try:
                wait_seconds = next(GENERATOR)
                S["wake"] = S["elapsed"] + (float(wait_seconds) if wait_seconds else 0.0)
            except StopIteration:
                finish()
            except Exception as error:
                check("driver exception", False, repr(error))
                finish()
    except Exception as error:
        check("tick exception", False, repr(error))
        finish()


GENERATOR = scenario()
HANDLE = unreal.register_slate_post_tick_callback(tick)
