"""Lead-run PIE probe for owner-approved Elden Ring style player controls.

Measures key-down to first observed player montage start in the editor's
game-tick sample. These are observation delays, not physical device latency.
The probe does not assert a particular montage or game feel: the ER clips are
still gated on owner video review and import.

Run in L_SevarogArena, once per route. Set H019_ENCOUNTER_DEFINITION before
Editor startup for the data route; leave unset for legacy. Log prefix:
[ERControlLatency].
"""
import os
import time
import unreal
import sys
from pathlib import Path
sys.path.insert(0, str(Path(unreal.Paths.project_dir()) / "Scripts" / "Editor"))
import pie_lead_common as plc

LOG = "[ERControlLatency] "

# Gamepad key names are the project control contract: R1=right shoulder,
# R2=right trigger, A=jump, B=dodge. Hold cases intentionally bracket the
# unknown IMC hold threshold so Lead can report which action actually fires.
CASES = [
    {"name": "R1_tap_light", "events": [(0.00, "Gamepad_RightShoulder", True), (0.12, "Gamepad_RightShoulder", False)]},
    {"name": "R2_tap_strong", "events": [(0.00, "Gamepad_RightTrigger", True), (0.12, "Gamepad_RightTrigger", False)]},
    {"name": "R2_hold_0.34s", "events": [(0.00, "Gamepad_RightTrigger", True), (0.34, "Gamepad_RightTrigger", False)]},
    {"name": "R2_hold_0.35s_boundary", "events": [(0.00, "Gamepad_RightTrigger", True), (0.35, "Gamepad_RightTrigger", False)]},
    {"name": "R2_hold_0.36s", "events": [(0.00, "Gamepad_RightTrigger", True), (0.36, "Gamepad_RightTrigger", False)]},
    {"name": "R2_hold_0.70s", "events": [(0.00, "Gamepad_RightTrigger", True), (0.70, "Gamepad_RightTrigger", False)]},
    {"name": "jump_R1_air_light", "measure_after": 0.25, "measure_event": 2, "events": [(0.00, "Gamepad_FaceButton_Bottom", True), (0.12, "Gamepad_FaceButton_Bottom", False), (0.30, "Gamepad_RightShoulder", True), (0.42, "Gamepad_RightShoulder", False)]},
    {"name": "jump_R2_air_heavy", "measure_after": 0.25, "measure_event": 2, "events": [(0.00, "Gamepad_FaceButton_Bottom", True), (0.12, "Gamepad_FaceButton_Bottom", False), (0.30, "Gamepad_RightTrigger", True), (0.42, "Gamepad_RightTrigger", False)]},
    {"name": "dodge_standing_tap", "events": [(0.00, "Gamepad_FaceButton_Right", True), (0.12, "Gamepad_FaceButton_Right", False)]},
    # Apply character movement for 0.30 s before the dodge key so the sample
    # cannot silently become another standing tap.
    {"name": "dodge_moving_tap", "move": True, "events": [(0.30, "Gamepad_FaceButton_Right", True), (0.42, "Gamepad_FaceButton_Right", False)]},
    {"name": "dodge_double_tap", "events": [(0.00, "Gamepad_FaceButton_Right", True), (0.07, "Gamepad_FaceButton_Right", False), (0.14, "Gamepad_FaceButton_Right", True), (0.21, "Gamepad_FaceButton_Right", False)]},
]
S = {"phase": "start", "elapsed": 0.0, "case": 0, "event": 0,
     "baseline": None, "last_position": None, "press_real": None,
     "observed": False, "held": set(), "done": False}
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
        # Lead hotfix C-1098: one warmup press no longer reliably draws (BUILD-269 runs drew on the 4th press),
        # so retry the draw press up to 3 times until RPGBuildLoadout reports combat enabled and no montage plays.
        loadout = comp(pawn, "RPGBuildLoadout")
        drawn = bool(loadout and loadout.is_combat_enabled())
        attempts = S.get("warmup_attempts", 0)
        if not drawn and attempts < 3 and not S["warmup_sent"] and S["elapsed"] >= 0.5:
            set_key(pc, "Gamepad_RightTrigger", True)
            S["warmup_sent"] = True
            S["warmup_press_t"] = S["elapsed"]
            S["warmup_attempts"] = attempts + 1
        if S["warmup_sent"] and S["elapsed"] - S.get("warmup_press_t", 0.0) >= 0.7 and "Gamepad_RightTrigger" in S["held"]:
            set_key(pc, "Gamepad_RightTrigger", False)
        if S["warmup_sent"] and "Gamepad_RightTrigger" not in S["held"] and S["elapsed"] - S.get("warmup_press_t", 0.0) >= 3.2:
            S["warmup_sent"] = False  # allow another attempt if still sheathed
        settled = drawn and player_montage(pawn)[0] is None and S["elapsed"] - S.get("warmup_press_t", 0.0) >= 3.2
        exhausted = S.get("warmup_attempts", 0) >= 3 and not S["warmup_sent"]
        if settled or exhausted:
            log("draw_ready=%s attempts=%d" % (drawn, S.get("warmup_attempts", 0)))
            log("input_context_active=%s" % bool(comp(pawn, "RPGDodgeTiming") and
                comp(pawn, "RPGDodgeTiming").is_elden_ring_input_active()))
            if not drawn:
                raise RuntimeError("weapon not drawn after 3 warmup presses; samples would be invalid")
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
        if case.get("move") and S["elapsed"] < 0.8:
            pawn.add_movement_input(pawn.get_actor_forward_vector(), 1.0, True)
        events = case["events"]
        while S["event"] < len(events) and S["elapsed"] >= events[S["event"]][0]:
            event_index = S["event"]
            _, key, down = events[event_index]
            set_key(pc, key, down)
            if down and case.get("move") and event_index == case.get("measure_event", 0):
                speed = pawn.get_velocity().length()  # UE Python Vector has length(), not size() (Lead hotfix C-1098)
                last_input = pawn.get_last_movement_input_vector()
                log("moving_press case=%s speed_cm_s=%.1f last_input=%s" %
                    (case["name"], speed, last_input))
            if down and event_index == case.get("measure_event", 0):
                S["press_real"] = time.perf_counter()
            S["event"] += 1

        name, position = player_montage(pawn)
        baseline_name, baseline_position = S["baseline"]
        started = bool(S["measurement_armed"] and name and (name != baseline_name or
                       (baseline_name == name and baseline_position is not None and
                        position is not None and position + 0.10 < baseline_position)))
        if started and not S["observed"]:
            latency = (time.perf_counter() - S["press_real"]) * 1000.0
            log("sample case=%s montage=%s position=%.3f observed_ms=%.2f tick_s=%.5f" %
                (case["name"], name, position, latency, dt))
            S["observed"] = True
        if S["elapsed"] > events[-1][0] + 2.0:
            if not S["observed"]:
                log("NO_MONTAGE_START case=%s baseline=%s final=%s" %
                    (case["name"], S["baseline"], (name, position)))
            if case["name"] == "dodge_double_tap":
                timing = comp(pawn, "RPGDodgeTiming")
                log("dodge_double_tap press_delta=%s last_gap_s=%s last_press_full=%s forced_rolls=%s" %
                    (timing.get_press_count() - S["press_count_before"] if timing else None,
                     timing.get_last_press_gap() if timing else None,
                     timing.was_last_press_full() if timing else None,
                     timing.get_forced_roll_count() if timing else None))
            release_all(pc)
            S.update(phase="cooldown", elapsed=0.0)
        return

    if S["phase"] == "cooldown" and S["elapsed"] > 2.5:
        S["case"] += 1
        S.update(phase="arm", elapsed=0.0)


HANDLE = unreal.register_slate_post_tick_callback(tick)
log("driver registered; observations are game-tick bounded, not device-latency claims")
