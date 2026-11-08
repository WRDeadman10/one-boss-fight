"""Lead-run, read-only ER air reach probe derived from P_C992_AIRHITS.

Run once per route in L_SevarogArena. Set H019_ENCOUNTER_DEFINITION before
Editor startup for the data route; leave unset for legacy. Set
RPG_ER_AIR_TEST_DISTANCE_CM to vary horizontal player-to-boss setup distance
(default 160 cm). Runtime-only optional air montage assignment is used; no
asset is saved. Logs montage position, falling state, actual pawn/boss and
right-hand/boss distances, and health delta for controls and both air attacks.
Log prefix: [ERAirReach]. These observations diagnose reach; they are not a
device-latency measurement or standalone gameplay acceptance.
"""

import os
import time
import unreal

LOG = "[ERAirReach] "
MOVE_ACTION = "/Game/OneBossFight/Input/IA_Move"
SAMPLE_PERIOD = 0.05
TEST_DISTANCE_CM = float(os.environ.get("RPG_ER_AIR_TEST_DISTANCE_CM", "160"))

CASES = [
    {"name": "R1_ground_control", "events": [(0.00, "Gamepad_RightShoulder", True), (0.12, "Gamepad_RightShoulder", False)]},
    {"name": "R2_ground_control", "events": [(0.00, "Gamepad_RightTrigger", True), (0.12, "Gamepad_RightTrigger", False)]},
    {"name": "jump_R1_air_light", "measure_after": 0.25, "measure_event": 2,
     "events": [(0.00, "Gamepad_FaceButton_Bottom", True), (0.12, "Gamepad_FaceButton_Bottom", False),
                (0.30, "Gamepad_RightShoulder", True), (0.42, "Gamepad_RightShoulder", False)]},
    {"name": "jump_R2_air_heavy", "measure_after": 0.25, "measure_event": 2,
     "events": [(0.00, "Gamepad_FaceButton_Bottom", True), (0.12, "Gamepad_FaceButton_Bottom", False),
                (0.30, "Gamepad_RightTrigger", True), (0.42, "Gamepad_RightTrigger", False)]},
]

STATE = {"phase": "start", "elapsed": 0.0, "case": 0, "event": 0,
         "baseline": None, "held": set(), "handle": None,
         "sample_elapsed": 0.0, "observed_montage": False}


def log(message):
    unreal.log(LOG + str(message))


def component(actor, class_name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent)
                 if c.get_class().get_name() == class_name), None) if actor else None


def boss_actor(world):
    return next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
                 if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if world else None


def player_montage(pawn):
    meshes = pawn.get_components_by_class(unreal.SkeletalMeshComponent) if pawn else []
    instance = meshes[0].get_anim_instance() if meshes else None
    montage = instance.get_current_active_montage() if instance else None
    position = instance.montage_get_position(montage) if (instance and montage) else None
    return (montage.get_name() if montage else None), position


def health(actor):
    attributes = component(actor, "BP_AttributesComponent_C")
    if not attributes:
        return None
    tag = unreal.GameplayTag()
    tag.import_text('(TagName="Attribute.Health")')
    try:
        return attributes.call_method("Get Current Attribute Value", args=(tag,))
    except Exception as exc:
        return "error:%s" % exc


def enter_combat_tag():
    tags = unreal.GameplayTagContainer()
    tags.import_text('(GameplayTags=((TagName="Ability.EnterCombat")))')
    return tags


def set_key(pc, key, down):
    if not unreal.RPGInputTestUtils.set_key_down(pc, key, down):
        raise RuntimeError("SetKeyDown failed for " + key)
    if down:
        STATE["held"].add(key)
    else:
        STATE["held"].discard(key)


def release_all(pc):
    for key in list(STATE["held"]):
        try:
            unreal.RPGInputTestUtils.set_key_down(pc, key, False)
        except Exception:
            pass
    STATE["held"].clear()


def actors():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    return world, pc, pawn, boss_actor(world)


def finish(reason):
    handle = STATE.get("handle")
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        STATE["handle"] = None
    try:
        _, pc, _, _ = actors()
        release_all(pc)
    except Exception:
        STATE["held"].clear()
    log("finished: " + reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def sample_reach(case_name, elapsed, pawn, boss):
    montage_name, position = player_montage(pawn)
    movement = pawn.get_movement_component()
    root_distance = (pawn.get_actor_location() - boss.get_actor_location()).length()
    meshes = pawn.get_components_by_class(unreal.SkeletalMeshComponent)
    hand_distance = None
    hand_z = None
    if meshes:
        hand = meshes[0].get_socket_location("hand_r")
        hand_distance = (hand - boss.get_actor_location()).length()
        hand_z = hand.z
    log("reach case=%s t=%.3f montage=%s pos=%s falling=%s pawn_to_boss_cm=%.1f hand_r_to_boss_cm=%s hand_r_z=%s" %
        (case_name, elapsed, montage_name,
         ("%.3f" % position) if position is not None else None,
         movement.is_falling() if movement else None, root_distance,
         ("%.1f" % hand_distance) if hand_distance is not None else None,
         ("%.1f" % hand_z) if hand_z is not None else None))
    if montage_name and not STATE["observed_montage"]:
        STATE["observed_montage"] = True
        log("first_montage case=%s montage=%s position=%s" % (case_name, montage_name, position))


def tick(delta_seconds):
    try:
        _tick(delta_seconds)
    except Exception:
        import traceback
        log("driver error: " + traceback.format_exc())
        finish("exception")


def _tick(delta_seconds):
    STATE["elapsed"] += delta_seconds
    if STATE["phase"] == "start":
        if STATE["elapsed"] > 0.5:
            selection = os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()
            if selection:
                unreal.SystemLibrary.execute_console_command(None, "rpg.EncounterDefinition " + selection)
                log("route=data selection=" + selection)
            else:
                log("route=legacy (H019_ENCOUNTER_DEFINITION unset)")
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            STATE.update(phase="setup", elapsed=0.0)
        return

    world, pc, pawn, boss = actors()
    if not pawn or not boss or not pc:
        if STATE["elapsed"] > 20.0:
            finish("player or boss unavailable")
        return
    debug = component(pawn, "RPGCombatDebug")
    if debug:
        debug.debug_refill_player()

    if STATE["phase"] == "setup":
        if STATE["elapsed"] > 6.0:
            encounter = component(boss, "RPGBossEncounter")
            if encounter:
                encounter.hold_for_test(True)
            boss_location = boss.get_actor_location()
            pawn.set_actor_location_and_rotation(
                unreal.Vector(boss_location.x + TEST_DISTANCE_CM, boss_location.y, boss_location.z),
                unreal.Rotator(0, 0, 180), False, True)
            pc.set_control_rotation(unreal.Rotator(0, 0, 180))
            actual_distance = (pawn.get_actor_location() - boss.get_actor_location()).length()
            ability_system = component(pawn, "BP_AdvancedAbilitySystemComponent_C")
            if not ability_system:
                raise RuntimeError("player ability component not found")
            ability_system.call_method("Try Activate Abilities By Tag", args=(enter_combat_tag(),))
            timing = component(pawn, "RPGDodgeTiming")
            light = unreal.load_asset("/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Light")
            heavy = unreal.load_asset("/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Heavy_Plunge")
            if not timing or not light or not heavy:
                raise RuntimeError("RPGDodgeTiming or ER air montage asset not found")
            timing.air_light_montage = light
            timing.air_heavy_montage = heavy
            log("setup held=%s requested_distance_cm=%.1f actual_pawn_boss_cm=%.1f assigned_air_light=%s air_heavy=%s" %
                (bool(encounter), TEST_DISTANCE_CM, actual_distance, light.get_name(), heavy.get_name()))
            STATE.update(phase="settle", elapsed=0.0)
        return

    if STATE["phase"] == "settle":
        if STATE["elapsed"] > 8.0:
            STATE.update(phase="warmup", elapsed=0.0, warmup_pressed=False, warmup_released=False)
        return

    if STATE["phase"] == "warmup":
        if STATE["elapsed"] >= 0.5 and not STATE["warmup_pressed"]:
            set_key(pc, "Gamepad_RightTrigger", True)
            STATE["warmup_pressed"] = True
        if STATE["elapsed"] >= 0.8 and not STATE["warmup_released"]:
            set_key(pc, "Gamepad_RightTrigger", False)
            STATE["warmup_released"] = True
        if STATE["elapsed"] > 3.0:
            timing = component(pawn, "RPGDodgeTiming")
            log("input_context_active=%s" % bool(timing and timing.is_elden_ring_input_active()))
            STATE.update(phase="arm", elapsed=0.0, case=0)
        return

    if STATE["phase"] == "arm":
        if STATE["case"] >= len(CASES):
            finish("all reach cases recorded")
            return
        case = CASES[STATE["case"]]
        STATE.update(phase="observe", elapsed=0.0, event=0, observed_montage=False,
                     sample_elapsed=0.0, baseline=player_montage(pawn),
                     hp_before=health(boss), press_real=time.perf_counter(),
                     measurement_armed=not bool(case.get("measure_after")))
        log("case=%s baseline=%s boss_hp_before=%s pawn_to_boss_cm=%.1f" %
            (case["name"], STATE["baseline"], STATE["hp_before"],
             (pawn.get_actor_location() - boss.get_actor_location()).length()))
        return

    if STATE["phase"] == "observe":
        case = CASES[STATE["case"]]
        if not STATE.get("measurement_armed", not bool(case.get("measure_after"))) and STATE["elapsed"] >= case["measure_after"]:
            STATE["baseline"] = player_montage(pawn)
            STATE["press_real"] = time.perf_counter()
            STATE["measurement_armed"] = True
        events = case["events"]
        while STATE["event"] < len(events) and STATE["elapsed"] >= events[STATE["event"]][0]:
            event_index = STATE["event"]
            _, key, down = events[event_index]
            set_key(pc, key, down)
            if down and event_index == case.get("measure_event", 0):
                STATE["press_real"] = time.perf_counter()
            STATE["event"] += 1
        STATE["sample_elapsed"] += delta_seconds
        if STATE["sample_elapsed"] >= SAMPLE_PERIOD:
            STATE["sample_elapsed"] = 0.0
            sample_reach(case["name"], STATE["elapsed"], pawn, boss)
        if STATE["elapsed"] > events[-1][0] + 1.6:
            release_all(pc)
            STATE.update(phase="cooldown", elapsed=0.0)
        return

    if STATE["phase"] == "cooldown" and STATE["elapsed"] > 2.5:
        hp_after = health(boss)
        hp_before = STATE.get("hp_before")
        delta = (hp_after - hp_before) if isinstance(hp_after, (int, float)) and isinstance(hp_before, (int, float)) else None
        log("result case=%s boss_hp_before=%s after=%s delta=%s" %
            (CASES[STATE["case"]]["name"], hp_before, hp_after, delta))
        STATE["case"] += 1
        STATE.update(phase="arm", elapsed=0.0, measurement_armed=False)


STATE["handle"] = unreal.register_slate_post_tick_callback(tick)
log("registered; read-only reach and HP observations; no asset saves")
