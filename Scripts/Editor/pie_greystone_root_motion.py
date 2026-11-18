"""Lead-run, no-save C-1257b displacement capture for one pawn route.

Run once with C1257_PLAYER_TARGET=mannequin and once with =greystone in
L_SevarogArena. The console switch is set before PIE; it never edits defaults.
The two logs must be paired only when map, start transform, play rates, and
five trials match. This script does not change component properties or rates.
"""
import math
import os
import re
import time
import unreal

LOG = "[GreystoneRootMotion] "
TARGET = os.environ.get("C1257_PLAYER_TARGET", "").strip().lower()
if TARGET not in ("mannequin", "greystone"):
    raise RuntimeError("C1257_PLAYER_TARGET must be mannequin or greystone")

EXPECTED_CHILD = "BP_GreystoneERPlayer_C"
TRIALS = 5
S = {"phase": "start", "elapsed": 0.0, "case": 0, "event": 0,
     "target": TARGET, "held": set(), "results": {"backstep": [], "quick_roll": []},
     "failures": [],
     "active_name": None, "started": False, "done": False}
HANDLE = None


def log(message):
    unreal.log(LOG + str(message))


def comp(actor, class_name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent)
                 if c.get_class().get_name() == class_name), None)


def soft_name(value):
    # C-1282 Lead fix: str(<loaded UObject>) is "<Object '/Game/..Name' (0x..) Class 'AnimMontage'>", so the old
    # suffix split produced garbage and the expected name never matched. Read the asset name directly.
    if value is None:
        return None
    if hasattr(value, "get_name"):
        return str(value.get_name())
    if hasattr(value, "get_asset_name"):
        return str(value.get_asset_name())
    match = re.search(r"'([^']+)'", str(value))
    text = match.group(1) if match else str(value)
    return text.rsplit(".", 1)[-1].rsplit("/", 1)[-1]


def active_montage(pawn):
    for mesh in pawn.get_components_by_class(unreal.SkeletalMeshComponent):
        instance = mesh.get_anim_instance()
        montage = instance.get_current_active_montage() if instance else None
        if montage:
            return montage.get_name(), instance, montage
    return None, None, None


def enter_combat_tag():
    tags = unreal.GameplayTagContainer()
    tags.import_text('(GameplayTags=((TagName="Ability.EnterCombat")))')
    return tags


def key(pc, name, down):
    if not unreal.RPGInputTestUtils.set_key_down(pc, name, down):
        raise RuntimeError("SetKeyDown failed: " + name)
    if down:
        S["held"].add(name)
    else:
        S["held"].discard(name)


def release(pc=None):
    pc = pc or S.get("pc")
    for name in tuple(S["held"]):
        try:
            unreal.RPGInputTestUtils.set_key_down(pc, name, False)
        except Exception:
            pass
    S["held"].clear()


def finish(reason):
    global HANDLE
    if S["done"]:
        return
    S["done"] = True
    release()
    try:
        unreal.SystemLibrary.execute_console_command(None, "rpg.GreystonePlayerTestPawn 0")
    except Exception:
        pass
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    back = S["results"]["backstep"]
    rolls = S["results"]["quick_roll"]
    back_ok = sum(1 for row in back if 84.0 <= row["distance_cm"] <= 98.0)
    roll_ok = sum(1 for row in rolls if 215.0 <= row["distance_cm"] <= 290.0)
    passed = back_ok == TRIALS and roll_ok == TRIALS
    log("RESULT target=%s pass=%s backstep=%d/%d quick_roll=%d/%d reason=%s" %
        (TARGET, passed, back_ok, TRIALS, roll_ok, TRIALS, reason))
    for kind, rows in (("backstep", back), ("quick_roll", rolls)):
        distances = [row["distance_cm"] for row in rows]
        mean = sum(distances) / len(distances) if distances else None
        low, high = (84.0, 98.0) if kind == "backstep" else (215.0, 290.0)
        log("SUMMARY target=%s move=%s completed=%d/%d mean_cm=%s range_cm=%s in_band=%d/%d" %
            (TARGET, kind, len(rows), TRIALS,
             "%.2f" % mean if mean is not None else "n/a",
             "%.2f..%.2f" % (min(distances), max(distances)) if distances else "n/a",
             sum(1 for value in distances if low <= value <= high), TRIALS))
    for failure in S["failures"]:
        log("FAILED_ATTEMPT target=%s move=%s n=%d reason=%s" %
            (TARGET, failure["move"], failure["trial"], failure["reason"]))
    log("finished: " + reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def fail_attempt(kind, index, reason):
    S["failures"].append({"move": kind, "trial": index + 1, "reason": reason})


def finish_trial(pawn, kind):
    end = pawn.get_actor_location()
    start = S["move_start"]
    dx, dy, dz = end.x - start.x, end.y - start.y, end.z - start.z
    distance = math.hypot(dx, dy)
    expected = S["expected_montage"]
    row = {"distance_cm": distance, "dx_cm": dx, "dy_cm": dy, "dz_cm": dz,
           "start": [start.x, start.y, start.z], "end": [end.x, end.y, end.z],
           "montage": S.get("active_name"), "expected": expected,
           "play_rate": S.get("play_rate"), "trial": S["move_trial_index"] + 1}
    S["results"][kind].append(row)
    low, high = (84.0, 98.0) if kind == "backstep" else (215.0, 290.0)
    log("TRIAL target=%s move=%s n=%d montage=%s expected=%s rate=%s start=(%.2f,%.2f,%.2f) end=(%.2f,%.2f,%.2f) delta=(%.2f,%.2f,%.2f) distance_cm=%.2f in_band=%s" %
        (TARGET, kind, row["trial"], row["montage"], expected, row["play_rate"],
         start.x, start.y, start.z, end.x, end.y, end.z, dx, dy, dz, distance,
         low <= distance <= high))
    S["trial_index"] += 1
    S.update(phase="trial_wait", elapsed=0.0, started=False, active_name=None)


def current_case():
    return ("backstep", S["trial_index"]) if S["trial_index"] < TRIALS else ("quick_roll", S["trial_index"] - TRIALS)


def tick(dt):
    try:
        _tick(dt)
    except Exception as exc:
        import traceback
        log("ERROR " + repr(exc) + "\n" + traceback.format_exc())
        finish("driver_error")


def _tick(dt):
    S["elapsed"] += dt
    if S["phase"] == "start":
        if S["elapsed"] >= 0.25:
            switch = 1 if TARGET == "greystone" else 0
            unreal.SystemLibrary.execute_console_command(None, "rpg.GreystonePlayerTestPawn %d" % switch)
            log("route_request target=%s cvar=%d defaults_changed=0" % (TARGET, switch))
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            S.update(phase="setup", elapsed=0.0)
        return

    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    S["pc"] = pc
    if pawn is None:
        if S["elapsed"] > 20.0:
            finish("no possessed pawn")
        return

    timing = comp(pawn, "RPGDodgeTiming")
    if not timing:
        finish("RPGDodgeTiming missing")
        return
    debug = comp(pawn, "RPGCombatDebug")
    if debug:
        debug.debug_refill_player()  # C-1283: the accepted probes refill every tick; run 3 lost quick roll 3 after 7 dodges
    class_name = pawn.get_class().get_name()
    if TARGET == "greystone" and class_name != EXPECTED_CHILD:
        if S["elapsed"] > 10.0:
            finish("test child was not selected; possessed class=" + class_name)
        return
    if TARGET == "mannequin" and class_name == EXPECTED_CHILD:
        finish("CVar-off control unexpectedly possessed Greystone child")
        return

    if S["phase"] == "setup":
        # Hold an encounter actor when the arena exposes the project's test hook.
        for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character):
            encounter = comp(actor, "RPGBossEncounter")
            if encounter:
                try:
                    encounter.hold_for_test(True)
                    log("boss_hold=1 class=%s" % actor.get_class().get_name())
                except Exception:
                    log("boss_hold=unavailable class=%s" % actor.get_class().get_name())
                break
        backstep = soft_name(timing.backstep_montage)
        quick = soft_name(timing.quick_montage)
        back_rate = float(timing.backstep_play_rate)
        quick_rate = float(timing.quick_play_rate)
        move_action = unreal.load_asset("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Move")
        if move_action is None:
            finish("pack IA_Move action is unavailable")
            return
        S.update(pawn=pawn, timing=timing, origin=pawn.get_actor_location(),
                 origin_rotation=pawn.get_actor_rotation(), backstep_name=backstep,
                 quick_name=quick, back_rate=back_rate, quick_rate=quick_rate,
                 move_action=move_action, trial_index=0)
        S["control_rotation"] = unreal.Rotator(pitch=0.0, yaw=S["origin_rotation"].yaw, roll=0.0)
        pc.set_control_rotation(S["control_rotation"])
        log("setup target=%s class=%s start=(%.2f,%.2f,%.2f) yaw=%.2f backstep=%s back_rate=%.3f quick_roll=%s quick_rate=%.3f directional_input=IA_Move(0,1,0) dodge_taps=1 input_context=%s" %
            (TARGET, class_name, S["origin"].x, S["origin"].y, S["origin"].z,
             S["origin_rotation"].yaw, backstep, back_rate, quick, quick_rate,
             timing.is_elden_ring_input_active()))
        if not timing.is_elden_ring_input_active():
            finish("Elden Ring dodge input context is inactive")
            return
        # C-1282 Lead fix: 1.4 s after possession SetKeyDown(Gamepad_FaceButton_Right) returned False in both arms
        # (UPlayerInput::InputKey reports a pressed key as unhandled until an Enhanced Input mapping holds it).
        # Use the warm-up the accepted first-dodge probes use: enter combat, settle 12 s, R2 draw, 3.7 s, then trials.
        asc = comp(pawn, "BP_AdvancedAbilitySystemComponent_C")
        if asc is None:
            finish("player ability component not found")
            return
        asc.call_method("Try Activate Abilities By Tag", args=(enter_combat_tag(),))
        log("WARMUP target=%s enter_combat=requested settle_s=12.0 draw=Gamepad_RightTrigger@0.5-1.2 trials_after_s=3.7" % TARGET)
        S.update(phase="settle", elapsed=0.0)
        return

    if S["phase"] == "settle":
        if S["elapsed"] > 12.0:
            S.update(phase="warmup", elapsed=0.0, warmup_sent=False)
        return

    if S["phase"] == "warmup":
        if S["elapsed"] >= 0.5 and not S["warmup_sent"]:
            key(pc, "Gamepad_RightTrigger", True)
            S["warmup_sent"] = True
        if S["elapsed"] >= 1.2 and "Gamepad_RightTrigger" in S["held"]:
            key(pc, "Gamepad_RightTrigger", False)
        if S["elapsed"] > 3.7:
            name, _, _ = active_montage(pawn)
            log("WARMUP_DONE target=%s input_context_active=%s active_montage=%s" %
                (TARGET, timing.is_elden_ring_input_active(), name))
            S.update(phase="trial_wait", elapsed=0.0)
        return

    if S["phase"] == "trial_wait":
        if S["elapsed"] < 1.0:
            return
        # C-1283: run 3 reset the pawn while roll 2 was still blending out and the next press was swallowed.
        settle_name, _, _ = active_montage(pawn)
        if settle_name is not None or pawn.get_velocity().length() > 5.0:
            if S["elapsed"] > 8.0:
                finish("pawn did not settle before the next trial (montage=%s)" % settle_name)
            return
        kind, index = current_case()
        pawn.set_actor_location_and_rotation(S["origin"], S["origin_rotation"], False, True)
        pc.set_control_rotation(S["control_rotation"])
        S["kind"], S["move_trial_index"] = kind, index
        S["expected_montage"] = S["backstep_name"] if kind == "backstep" else S["quick_name"]
        S["play_rate"] = S["back_rate"] if kind == "backstep" else S["quick_rate"]
        S["events"] = [(0.25, "Gamepad_FaceButton_Right", True), (0.37, "Gamepad_FaceButton_Right", False)]
        S.update(phase="input", elapsed=0.0, event=0, started=False,
                 active_name=None, direction_input_active=False)
        return

    if S["phase"] == "input":
        kind = S["kind"]
        move_active = kind == "quick_roll" and 0.10 <= S["elapsed"] <= 0.40
        if move_active:
            if not unreal.RPGInputTestUtils.inject_action(pc, S["move_action"], unreal.Vector(0.0, 1.0, 0.0)):
                fail_attempt(kind, S["move_trial_index"], "IA_Move forward injection failed")
                finish("directional quick-roll input could not be injected")
                return
            if not S["direction_input_active"]:
                log("DIRECTION_INPUT_START target=%s move=quick_roll action=IA_Move value=(0,1,0) controller_yaw=%.2f" %
                    (TARGET, S["control_rotation"].yaw))
                S["direction_input_active"] = True
        elif S["direction_input_active"]:
            log("DIRECTION_INPUT_STOP target=%s move=quick_roll elapsed=%.3f" % (TARGET, S["elapsed"]))
            S["direction_input_active"] = False
        while S["event"] < len(S["events"]) and S["elapsed"] >= S["events"][S["event"]][0]:
            _, button, down = S["events"][S["event"]]
            key(pc, button, down)
            S["event"] += 1
        name, instance, montage = active_montage(pawn)
        if not S["started"] and name == S["expected_montage"]:
            S["started"] = True
            S["active_name"] = name
            S["move_start"] = pawn.get_actor_location()
            log("MONTAGE_START target=%s move=%s name=%s position=%.3f play_rate=%.3f direction_input=%s" %
                (TARGET, kind, name, instance.montage_get_position(montage), S["play_rate"],
                 "IA_Move(0,1,0)" if kind == "quick_roll" else "none"))
        elif S["started"] and name != S["expected_montage"] and not S.get("settling"):
            # C-1283: the montage has ended; root motion keeps carrying the pawn through the blend-out.
            # Sample until it rests (< 5 cm/s) or 1.0 s, as the accepted C-1063 probe measured moved_cm.
            S["settling"] = True
            S["settle_started"] = S["elapsed"]
            end = pawn.get_actor_location()
            start = S["move_start"]
            S["montage_end_distance_cm"] = math.hypot(end.x - start.x, end.y - start.y)
            return
        if S.get("settling"):
            speed = pawn.get_velocity().length()
            if speed < 5.0 or S["elapsed"] - S["settle_started"] > 1.0:
                S["settling"] = False
                log("SETTLE target=%s move=%s n=%d montage_end_distance_cm=%.2f settle_s=%.3f rest_speed_cm_s=%.1f" %
                    (TARGET, kind, S["move_trial_index"] + 1, S["montage_end_distance_cm"],
                     S["elapsed"] - S["settle_started"], speed))
                finish_trial(pawn, kind)
                if S["trial_index"] >= 2 * TRIALS:
                    finish("all trials observed")
            return
        if S["elapsed"] > 6.0 and not S["started"]:
            log("MONTAGE_NOT_OBSERVED target=%s move=%s expected=%s actual=%s" %
                (TARGET, kind, S["expected_montage"], name))
            fail_attempt(kind, S["move_trial_index"], "expected montage did not start")
            finish("expected montage did not start")
            return
        if S["elapsed"] > 12.0 and S["started"]:
            fail_attempt(kind, S["move_trial_index"], "expected montage did not complete within 12 seconds")
            finish("expected montage did not complete within 12 seconds")


def start():
    global HANDLE
    HANDLE = unreal.register_slate_post_tick_callback(tick)
    log("driver_started target=%s trials_per_move=%d no_save=1" % (TARGET, TRIALS))


start()
