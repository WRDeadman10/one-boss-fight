"""Lead-run PIE probe for the reproduced first backstep immediately after weapon draw.

Requires ENGINE_LOCK. No montage assignment: this reads the compiled runtime default,
performs the normal R2 combat/draw path, and records the first input plus two repeats.
"""
import sys
import time
import os
from pathlib import Path

import unreal

sys.path.insert(0, str(Path(unreal.Paths.project_dir()) / "Scripts" / "Editor"))
import pie_lead_common as plc

PREFIX = "[FirstDodgeAfterDraw] "
R2 = "Gamepad_RightTrigger"
DODGE = "Gamepad_FaceButton_Right"
CASE = os.environ.get("FIRST_DODGE_CASE", "standing").strip().lower()
EXPECTED_MONTAGE = {
    "standing": "AM_ER_Backstep_Mixamo_V2",
    "moving": "Dodge_Small_Forward_Roll_Montage",
}
STATE = {"gen": None, "done": False, "held": set(), "handle": None}


def log(message):
    unreal.log(PREFIX + str(message))


def actors():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    return world, pc, pawn


def key(pc, name, down):
    unreal.RPGInputTestUtils.set_key_down(pc, name, down)
    (STATE["held"].add if down else STATE["held"].discard)(name)


def buffered_input_tag(pawn):
    buffer = plc.component(pawn, "BP_InputBufferComponent_C")
    if buffer is None:
        return "UNKNOWN"
    try:
        return str(buffer.call_method("Get Buffered Input Tag"))
    except Exception:
        return "UNKNOWN"


def wait(seconds):
    world = actors()[0]
    end = plc.game_time(world) + seconds
    while plc.game_time(actors()[0]) < end:
        yield 0.0


def run():
    world, pc, pawn = actors()
    if not (world and pc and pawn):
        raise RuntimeError("PIE player/controller unavailable")
    loadout = plc.component(pawn, "RPGBuildLoadout")
    dodge = plc.component(pawn, "RPGDodgeTiming")
    log("runtime_default=%s" % dodge.get_editor_property("backstep_montage"))

    # Match the Lead showcase setup and draw cadence exactly.
    yield from wait(2.2)
    plc.enter_combat(pawn)
    yield from wait(1.0)
    for draw_attempt in range(1, 4):
        key(pc, R2, True)
        yield from wait(0.7)
        key(pc, R2, False)
        deadline = time.perf_counter() + 5.0
        while time.perf_counter() < deadline and not (loadout.is_combat_enabled() and plc.player_montage(pawn)[0] is None):
            yield 0.0
        if loadout.is_combat_enabled():
            break
    b_draw_ready = loadout.is_combat_enabled()
    log("draw_ready=%s draw_attempt=%d combat_enabled=%s montage=%s" %
        (b_draw_ready, draw_attempt, b_draw_ready, plc.player_montage(pawn)[0]))
    if not b_draw_ready:
        raise RuntimeError("R2 weapon draw did not reach combat-ready state")

    # Select one immediate first-press scenario per fresh Lead PIE process.
    if CASE not in ("standing", "moving"):
        raise RuntimeError("FIRST_DODGE_CASE must be standing or moving")
    log("scenario=%s expected_first_montage=%s runtime_assignment=none" % (CASE, EXPECTED_MONTAGE[CASE]))
    # No wait or runtime assignment between draw-ready and this first input.
    for attempt in range(1, 4):
        if attempt > 1:
            yield from wait(1.0)
        if CASE == "moving":
            move_end = plc.game_time(actors()[0]) + 0.30
            while plc.game_time(actors()[0]) < move_end:
                pawn.add_movement_input(pawn.get_actor_forward_vector(), 1.0, True)
                yield 0.0
        p0 = pawn.get_actor_location()
        n0 = dodge.get_press_count()
        buffer_before = buffered_input_tag(pawn)
        log("press_observables case=%s press=%d speed_cm_s=%.1f last_input_size=%.3f pending_input_size=%.3f buffered_input_tag=%s" %
            (CASE, attempt, pawn.get_velocity().length(), pawn.get_last_movement_input_vector().length(),
             pawn.get_pending_movement_input_vector().length(), buffer_before))
        key(pc, DODGE, True)
        yield 0.0
        key(pc, DODGE, False)
        buffer_after_press = buffered_input_tag(pawn)
        log("buffered_input_observation case=%s press=%d before=%s after_one_input_tick=%s" %
            (CASE, attempt, buffer_before, buffer_after_press))
        log("%s case=%s press_count_before=%d" % ("first_standing_dodge" if attempt == 1 and CASE == "standing" else "first_moving_dodge" if attempt == 1 else "repeat_dodge_press_%d" % attempt, CASE, n0))
        end = plc.game_time(actors()[0]) + 0.75
        sampled = False
        next_sample_time = plc.game_time(actors()[0])
        while plc.game_time(actors()[0]) < end:
            montage, montage_position = plc.player_montage(pawn)
            if montage is not None:
                sampled = True
            now = plc.game_time(actors()[0])
            if attempt == 1 and now >= next_sample_time:
                log("first_dodge_sample active_montage=%s montage_position=%s buffered_input_tag=%s moved_cm=%.1f stage=%s backstep_count=%d" %
                    (montage or "NONE", "%.3f" % montage_position if montage_position is not None else "UNKNOWN",
                     buffered_input_tag(pawn), (pawn.get_actor_location() - p0).length(), dodge.get_stage_name(), dodge.get_backstep_count()))
                next_sample_time = now + 0.05
            yield 0.0
        label = ("first_standing_result" if CASE == "standing" else "first_moving_result") if attempt == 1 else "repeat_dodge_result_%d" % attempt
        log("%s montage_seen=%s moved_cm=%.1f press_count=%d backstep_count=%d" %
            (label, sampled, (pawn.get_actor_location() - p0).length(), dodge.get_press_count(), dodge.get_backstep_count()))


def finish(reason):
    if STATE["done"]:
        return
    STATE["done"] = True
    try:
        _, pc, _ = actors()
        for name in list(STATE["held"]):
            unreal.RPGInputTestUtils.set_key_down(pc, name, False)
    except Exception:
        pass
    if STATE["handle"] is not None:
        unreal.unregister_slate_post_tick_callback(STATE["handle"])
        STATE["handle"] = None
    log("finished: " + reason)
    plc.end_play()


def tick(_dt):
    try:
        if STATE["gen"] is None:
            world, pc, pawn = actors()
            if not (world and pc and pawn):
                if not STATE.get("requested"):
                    STATE["requested"] = True
                    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                return
            STATE["gen"] = run()
        next(STATE["gen"])
    except StopIteration:
        finish("probe complete")
    except Exception as exc:
        log("ERROR %s" % exc)
        finish("probe error")


STATE["handle"] = unreal.register_slate_post_tick_callback(tick)
log("driver registered; Lead must hold ENGINE_LOCK and inspect the first result against repeat controls")
