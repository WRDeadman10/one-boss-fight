"""Lead-run copy of the ER control probe for post-air array restoration.

Measures key-down to first observed player montage start in the editor's
game-tick sample. These are observation delays, not physical device latency.
The probe does not assert a particular montage or game feel: the ER clips are
still gated on owner video review and import.

Run in L_SevarogArena, once per route. Set H019_ENCOUNTER_DEFINITION before
Editor startup for the data route; leave unset for legacy. Log prefix:
[ERAirRestore].
"""
import os
import time
import unreal
import sys
from pathlib import Path
sys.path.insert(0, str(Path(unreal.Paths.project_dir()) / "Scripts" / "Editor"))
import pie_lead_common as plc

LOG = "[ERAirRestore] "

# Gamepad key names are the project control contract: R1=right shoulder,
# R2=right trigger, A=jump, B=dodge. Hold cases intentionally bracket the
# unknown IMC hold threshold so Lead can report which action actually fires.
CASES = [
    # Verify real movement is present before the moving-dodge press. IA_Move
    # action injection alone does not update CharacterMovement in this probe.
    {"name": "dodge_moving_tap", "move": True,
     "events": [(0.30, "Gamepad_FaceButton_Right", True), (0.42, "Gamepad_FaceButton_Right", False)]},
    {"name": "air_R1_then_ground_R1_R2", "measure_after": 0.25, "measure_event": 2,
     "ground_events": {4: "ground_R1", 6: "ground_R2"},
     "events": [(0.00, "Gamepad_FaceButton_Bottom", True), (0.12, "Gamepad_FaceButton_Bottom", False),
                (0.30, "Gamepad_RightShoulder", True), (0.42, "Gamepad_RightShoulder", False),
                (2.00, "Gamepad_RightShoulder", True), (2.12, "Gamepad_RightShoulder", False),
                (3.50, "Gamepad_RightTrigger", True), (3.62, "Gamepad_RightTrigger", False)]},
    {"name": "air_R2_then_ground_R1_R2", "measure_after": 0.25, "measure_event": 2,
     "ground_events": {4: "ground_R1", 6: "ground_R2"},
     "events": [(0.00, "Gamepad_FaceButton_Bottom", True), (0.12, "Gamepad_FaceButton_Bottom", False),
                (0.30, "Gamepad_RightTrigger", True), (0.42, "Gamepad_RightTrigger", False),
                (2.00, "Gamepad_RightShoulder", True), (2.12, "Gamepad_RightShoulder", False),
                (3.50, "Gamepad_RightTrigger", True), (3.62, "Gamepad_RightTrigger", False)]},
]
S = {"phase": "start", "elapsed": 0.0, "case": 0, "event": 0,
     "baseline": None, "last_position": None, "press_real": None,
     "observed": False, "held": set(), "done": False,
     "pending_result": None}
HANDLE = None


def log(message):
    unreal.log(LOG + message)


comp = plc.component
player_montage = plc.player_montage


def set_key(pc, key, down):
    ok = unreal.RPGInputTestUtils.set_key_down(pc, key, down)
    if down:
        S["held"].add(key)
    else:
        S["held"].discard(key)
    if not ok:
        raise RuntimeError("SetKeyDown failed for " + key)


def release_all(pc):
    pc = pc or S.get("last_pc")
    for key in list(S["held"]):
        try:
            unreal.RPGInputTestUtils.set_key_down(pc, key, False)
        except Exception:
            pass
    S["held"].clear()


def finish(reason):
    global HANDLE
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    release_all(None)
    plc.finished(log, reason)


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("driver error: " + traceback.format_exc())
        finish("exception")


def _tick(dt):
    S["elapsed"] += dt
    if S["phase"] == "start":
        if S["elapsed"] > 0.5:
            selection = os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()
            if selection:
                unreal.SystemLibrary.execute_console_command(None, "rpg.EncounterDefinition " + selection)
                log("route=data selection=" + selection)
            else:
                log("route=legacy (H019_ENCOUNTER_DEFINITION unset)")
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            S.update(phase="setup", elapsed=0.0)
        return

    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    S["last_pc"] = pc
    if pawn is None:
        if S["elapsed"] > 20.0:
            finish("no possessed player within 20 game seconds")
        return
    boss = plc.boss_actor(world)
    debug = plc.boss_debug(boss)
    if debug:
        plc.refill_player(boss)

    if S["phase"] == "setup":
        if S["elapsed"] > 6.0:
            if not boss:
                raise RuntimeError("expected boss not found; cannot hold a stable combat setup")
            encounter = comp(boss, "RPGBossEncounter")
            if encounter:
                encounter.hold_for_test(True)
            location = boss.get_actor_location()
            plc.place_player(pc, pawn, (location.x + 900, location.y, location.z), 180)
            plc.enter_combat(pawn)
            log("setup boss held=%s player_distance_cm=900" % bool(encounter))
            S.update(phase="settle", elapsed=0.0)
        return

    if S["phase"] == "warmup":
        # Match the accepted Lead probe: the first R2 charge draws the weapon;
        # exclude it from the latency samples.
        if S["elapsed"] >= 0.5 and not S["warmup_sent"]:
            set_key(pc, "Gamepad_RightTrigger", True)
            S["warmup_sent"] = True
        if S["elapsed"] >= 1.2 and "Gamepad_RightTrigger" in S["held"]:
            set_key(pc, "Gamepad_RightTrigger", False)
        if S["elapsed"] > 3.7:
            log("input_context_active=%s" % bool(comp(pawn, "RPGDodgeTiming") and
                comp(pawn, "RPGDodgeTiming").is_elden_ring_input_active()))
            S.update(phase="arm", elapsed=0.0)
        return

    if S["phase"] == "settle":
        if S["elapsed"] > 12.0:
            S.update(phase="warmup", elapsed=0.0, warmup_sent=False)
        return

    if S["phase"] == "arm":
        if S["case"] >= len(CASES):
            finish("all control samples recorded")
            return
        case = CASES[S["case"]]
        S.update(phase="observe", elapsed=0.0, event=0, observed=False,
                 baseline=player_montage(pawn), last_position=None,
                 press_real=time.perf_counter(), measurement_armed=not bool(case.get("measure_after")),
                 pending_result=None,
                 press_count_before=(comp(pawn, "RPGDodgeTiming").get_press_count()
                                     if case["name"] == "dodge_double_tap" and comp(pawn, "RPGDodgeTiming") else None))
        log("case=" + case["name"] + " baseline=" + str(S["baseline"]))
        return

    if S["phase"] == "observe":
        case = CASES[S["case"]]
        if not S["measurement_armed"] and S["elapsed"] >= case["measure_after"]:
            # Jump is a setup action. Start the latency clock from the attack key,
            # not from the jump montage that may already be playing.
            S["baseline"] = player_montage(pawn)
            S["press_real"] = time.perf_counter()
            S["measurement_armed"] = True
        # Optional moving cases use real CharacterMovement input, not
        # RPGInputTestUtils.inject_action(IA_Move), which does not move the pawn.
        if case.get("move") and S["elapsed"] < 0.8:
            pawn.add_movement_input(pawn.get_actor_forward_vector(), 1.0, True)
        events = case["events"]
        while S["event"] < len(events) and S["elapsed"] >= events[S["event"]][0]:
            event_index = S["event"]
            ground_label = case.get("ground_events", {}).get(event_index)
            movement = pawn.get_components_by_class(unreal.CharacterMovementComponent)
            if ground_label:
                if not movement:
                    log("GROUND_RESTORE_NO_MOVEMENT case=%s label=%s" % (case["name"], ground_label))
                    finish("cannot verify grounded state")
                    return
                prior_montage = player_montage(pawn)
                if movement[0].is_falling() or prior_montage[0]:
                    if S["elapsed"] - events[event_index][0] > 8.0:
                        log("GROUND_RESTORE_TIMEOUT case=%s label=%s falling=%s montage=%s" %
                            (case["name"], ground_label,
                             movement[0].is_falling() if movement else "unknown", prior_montage[0]))
                        finish("grounded follow-up timed out")
                        return
                    break
                S["pending_result"] = {"label": ground_label, "baseline": prior_montage,
                                        "since": S["elapsed"]}
            _, key, down = events[event_index]
            set_key(pc, key, down)
            if down and case.get("move") and event_index == case.get("measure_event", 0):
                speed = pawn.get_velocity().size()
                last_input = pawn.get_last_movement_input_vector()
                log("moving_press case=%s speed_cm_s=%.1f last_input=%s" %
                    (case["name"], speed, last_input))
            if down and event_index == case.get("measure_event", 0):
                S["press_real"] = time.perf_counter()
            S["event"] += 1

        name, position = player_montage(pawn)
        pending = S.get("pending_result")
        if pending:
            before_name, before_position = pending["baseline"]
            changed = bool(name and (name != before_name or (name == before_name and before_position is not None
                           and position is not None and position + 0.10 < before_position)))
            if changed:
                movement = pawn.get_components_by_class(unreal.CharacterMovementComponent)
                log("ground_result case=%s label=%s montage=%s falling=%s" %
                    (case["name"], pending["label"], name,
                     movement[0].is_falling() if movement else "unknown"))
                S["pending_result"] = None
            elif S["elapsed"] - pending["since"] > 1.0:
                log("NO_GROUND_MONTAGE case=%s label=%s baseline=%s final=%s" %
                    (case["name"], pending["label"], pending["baseline"], (name, position)))
                S["pending_result"] = None
        baseline_name, baseline_position = S["baseline"]
        started = bool(S["measurement_armed"] and name and (name != baseline_name or
                       (baseline_name == name and baseline_position is not None and
                        position is not None and position + 0.10 < baseline_position)))
        if started and not S["observed"]:
            latency = (time.perf_counter() - S["press_real"]) * 1000.0
            log("sample case=%s montage=%s position=%.3f observed_ms=%.2f tick_s=%.5f" %
                (case["name"], name, position, latency, dt))
            S["observed"] = True
        if S["event"] >= len(events) and S["elapsed"] > events[-1][0] + 2.0:
            if not S["observed"]:
                log("NO_MONTAGE_START case=%s baseline=%s final=%s" %
                    (case["name"], S["baseline"], (name, position)))
            release_all(pc)
            S.update(phase="cooldown", elapsed=0.0)
        return

    if S["phase"] == "cooldown" and S["elapsed"] > 2.5:
        S["case"] += 1
        S.update(phase="arm", elapsed=0.0)


HANDLE = unreal.register_slate_post_tick_callback(tick)
log("driver registered; verifies moving dodge input, then waits for airborne montage end and landing before ground R1/R2 follow-ups")
