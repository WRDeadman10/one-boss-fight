"""Lead-run PIE default-wired standing/moving dodge classification probe.

Measures key-down to first observed player montage start in the editor's
game-tick sample. These are observation delays, not physical device latency.
The probe does not assign a runtime montage. It requires nonzero movement
input/velocity before calling a moving dodge result valid.

Run in L_SevarogArena, once per route. Set H019_ENCOUNTER_DEFINITION before
Editor startup for the data route; leave unset for legacy. Log prefix:
[ERDefaultDodge].
"""
import os
import time
import unreal

LOG = "[ERDefaultDodge] "
INPUT_ROOT = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
MOVE_ACTION = "/Game/OneBossFight/Input/IA_Move"

# Gamepad key names are the project control contract: R1=right shoulder,
# R2=right trigger, A=jump, B=dodge. Hold cases intentionally bracket the
# unknown IMC hold threshold so Lead can report which action actually fires.
CASES = [
    {"name": "R1_tap_light", "events": [(0.00, "Gamepad_RightShoulder", True), (0.12, "Gamepad_RightShoulder", False)]},
    {"name": "dodge_standing_tap", "events": [(0.00, "Gamepad_FaceButton_Right", True), (0.12, "Gamepad_FaceButton_Right", False)]},
    {"name": "dodge_moving_tap", "move": True, "measure_event": 0, "events": [(0.30, "Gamepad_FaceButton_Right", True), (0.42, "Gamepad_FaceButton_Right", False)]},
]
S = {"phase": "start", "elapsed": 0.0, "case": 0, "event": 0,
     "baseline": None, "last_position": None, "press_real": None,
     "observed": False, "held": set(), "done": False, "checks": []}
HANDLE = None


def valid_sample(case, montage, speed, input_size):
    if case == "R1_tap_light":
        return montage == "Attack_PrimaryA_Montage"
    if case == "dodge_standing_tap":
        return montage == "AM_ER_Backstep_Back" and input_size < 0.1
    if case == "dodge_moving_tap":
        return montage == "Dodge_Small_Forward_Roll_Montage" and speed >= 50.0 and input_size >= 0.1
    return False


def log(message):
    unreal.log(LOG + message)


def comp(actor, class_name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent)
                 if c.get_class().get_name() == class_name), None)


def player_montage(pawn):
    meshes = pawn.get_components_by_class(unreal.SkeletalMeshComponent)
    inst = meshes[0].get_anim_instance() if meshes else None
    montage = inst.get_current_active_montage() if inst else None
    if not montage:
        return None, None
    position = inst.montage_get_position(montage)
    return montage.get_name(), position


def enter_combat_tag():
    tags = unreal.GameplayTagContainer()
    tags.import_text('(GameplayTags=((TagName="Ability.EnterCombat")))')
    return tags


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
    if S["done"]:
        return
    S["done"] = True
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    release_all(None)
    log("RESULT pass=%s checks=%d/3 reason=%s" %
        (len(S["checks"]) == 3 and all(S["checks"]), sum(S["checks"]), reason))
    log("finished: " + reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


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
    debug = comp(pawn, "RPGCombatDebug")
    if debug:
        debug.debug_refill_player()

    if S["phase"] == "setup":
        if S["elapsed"] > 6.0:
            boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
                         if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None)
            if not boss:
                raise RuntimeError("expected boss not found; cannot hold a stable combat setup")
            encounter = comp(boss, "RPGBossEncounter")
            if encounter:
                encounter.hold_for_test(True)
            location = boss.get_actor_location()
            pawn.set_actor_location_and_rotation(unreal.Vector(location.x + 900, location.y, location.z),
                                                 unreal.Rotator(0, 0, 180), False, True)
            pc.set_control_rotation(unreal.Rotator(0, 0, 180))
            asc = comp(pawn, "BP_AdvancedAbilitySystemComponent_C")
            if not asc:
                raise RuntimeError("player ability component not found")
            asc.call_method("Try Activate Abilities By Tag", args=(enter_combat_tag(),))
            log("setup boss held=%s player_distance_cm=900" % bool(encounter))
            timing = comp(pawn, "RPGDodgeTiming")
            if timing is None:
                raise RuntimeError("RPGDodgeTiming missing")
            log("default_wiring backstep=%s" % timing.backstep_montage)
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
                 sample_montage=None, press_speed=None, press_input_size=None,
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
        if case.get("move") and S["elapsed"] < 1.1:
            pawn.add_movement_input(pawn.get_actor_forward_vector(), 1.0, True)
        events = case["events"]
        if case.get("move") and S["event"] == 0 and S["elapsed"] >= events[0][0] - 0.05 and not S.get("diag_done"):
            S["diag_done"] = True
            mv = pawn.get_movement_component()
            log("diag before press: speed_cm_s=%.1f last_input=%s pending_input=%s" % (
                pawn.get_velocity().length(), str(pawn.get_last_movement_input_vector()), str(pawn.get_pending_movement_input_vector())))
        while S["event"] < len(events) and S["elapsed"] >= events[S["event"]][0]:
            event_index = S["event"]
            _, key, down = events[event_index]
            if down and event_index == case.get("measure_event", 0):
                S["press_speed"] = pawn.get_velocity().length()
                S["press_input_size"] = pawn.get_last_movement_input_vector().length()
                log("PRESS case=%s speed_cm_s=%.1f last_input_size=%.3f pending_input_size=%.3f" %
                    (case["name"], S["press_speed"], S["press_input_size"],
                     pawn.get_pending_movement_input_vector().length()))
            set_key(pc, key, down)
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
            S["sample_montage"] = name
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
        case = CASES[S["case"]]["name"]
        passed = valid_sample(case, S.get("sample_montage"),
                              S.get("press_speed") or 0.0, S.get("press_input_size") or 0.0)
        S["checks"].append(passed)
        log("CHECK case=%s pass=%s montage=%s press_speed=%s press_input_size=%s" %
            (case, passed, S.get("sample_montage"), S.get("press_speed"), S.get("press_input_size")))
        S["case"] += 1
        S.update(phase="arm", elapsed=0.0)


HANDLE = unreal.register_slate_post_tick_callback(tick)
log("driver registered; observations are game-tick bounded, not device-latency claims")
