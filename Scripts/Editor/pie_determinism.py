"""C-894 U-C07: six fixed-seed legacy/data PIE repeats; records tracker decisions for offline comparison.

Requires L_SevarogArena, a Development Editor build, H019_ENCOUNTER_DEFINITION for the data route,
and an empty OBF_DETERMINISM_OUT directory (defaults to Saved/U-C07). Lead-run only.
"""
import json
import math
import os
import unreal

LOG = "[Determinism] "
SEED = int(os.environ.get("OBF_DETERMINISM_SEED", "20261105"))
DATA_SELECTION = os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()
OUT_DIR = os.environ.get("OBF_DETERMINISM_OUT", os.path.join(unreal.Paths.project_saved_dir(), "U-C07"))
OUT_FILE = os.path.join(OUT_DIR, "determinism_runs.json")
RUN_SECONDS = 35.0
MAX_WAIT = 120.0
ATTACK_ACTION = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_NormalAttack"
DODGE_ACTION = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Dodge"
ATTACK_PULSES = tuple(float(t) for t in range(3, 34, 4))
DODGE_PULSES = tuple(float(t) for t in range(5, 34, 7))
INPUT_SCHEDULE = {
    "attack_action": ATTACK_ACTION,
    "attack_pulses_seconds": ATTACK_PULSES,
    "dodge_action": DODGE_ACTION,
    "dodge_pulses_seconds": DODGE_PULSES,
    "player_start_distance_cm": 250,
    "boss_behavior": "wake, then release hold for natural AI decisions",
    "duration_seconds": RUN_SECONDS,
}
state = {"phase": "prepare", "elapsed": 0.0, "run_index": 0, "run_elapsed": 0.0,
         "wait_elapsed": 0.0, "arms": [], "runs": [], "events": [], "previous": {}, "keys": {},
         "fatal": None, "handle": None, "run": None, "output_owned": False}


def log(message):
    unreal.log(LOG + str(message))


def editor_world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def game_world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def component(actor, class_name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent)
                 if c.get_class().get_name() == class_name), None)


def save_receipt():
    payload = {"schema": "u_c07_determinism_v1", "seed": SEED,
               "input_schedule": INPUT_SCHEDULE,
               "status": "failed" if state["fatal"] else ("complete" if len(state["runs"]) == 6 else "partial"),
               "fatal": state["fatal"], "runs": state["runs"]}
    os.makedirs(OUT_DIR, exist_ok=True)
    allowed = {os.path.basename(OUT_FILE)} if state["output_owned"] else set()
    if set(os.listdir(OUT_DIR)) - allowed:
        raise RuntimeError("refusing to overwrite or share a non-empty output directory: " + OUT_DIR)
    if not state["output_owned"] and os.path.exists(OUT_FILE):
        raise RuntimeError("refusing to overwrite existing receipt: " + OUT_FILE)
    with open(OUT_FILE, "w", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
    state["output_owned"] = True
    log("receipt=" + OUT_FILE)


def configure_arm(run):
    selection = DATA_SELECTION if run["route"] == "data" else '""'
    unreal.SystemLibrary.execute_console_command(None, "rpg.EncounterDefinition " + selection)
    unreal.SystemLibrary.execute_console_command(None, "rpg.DeterminismSeed %d" % SEED)
    log("arm route=%s repeat=%d seed=%d" % (run["route"], run["repeat"], SEED))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
    state.update(phase="await_world", elapsed=0.0, wait_elapsed=0.0, run_elapsed=0.0,
                 events=[], previous={}, keys={})


def capture_tick(world, dt):
    s = state
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    player = pc.get_controlled_pawn() if pc else None
    boss = next((actor for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
                 if actor.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None)
    if player is None or boss is None:
        return False
    tracker = component(boss, "RPGAttackTracker")
    encounter = component(boss, "URPGBossEncounter") or component(boss, "RPGBossEncounter")
    debug = component(boss, "URPGCombatDebug")
    if tracker is None or encounter is None:
        return False

    if s["phase"] == "await_world":
        start = boss.get_actor_location()
        yaw = math.radians(boss.get_actor_rotation().yaw)
        position = unreal.Vector(start.x - math.cos(yaw) * 250.0, start.y - math.sin(yaw) * 250.0, start.z + 20.0)
        facing = unreal.MathLibrary.find_look_at_rotation(position, start)
        player.set_actor_location_and_rotation(position, facing, False, True)
        if pc:
            pc.set_control_rotation(facing)
        try:
            if encounter.is_dormant():
                encounter.wake()
            encounter.hold_for_test(False)
        except Exception as exc:
            raise RuntimeError("could not release/wake boss for the natural AI pass: " + repr(exc))
        s["run"] = {"route": s["arms"][s["run_index"]]["route"],
                    "repeat": s["arms"][s["run_index"]]["repeat"], "seed": SEED,
                    "status": "running", "started": False, "events": [],
                    "final": {}, "input_schedule": INPUT_SCHEDULE, "inputs": []}
        if debug:
            debug.debug_refill_player()
        s["phase"] = "capture"
        s["run_elapsed"] = 0.0
        log("PIE_READY route=%s repeat=%d boss=%s player=%s" %
            (s["run"]["route"], s["run"]["repeat"], boss.get_name(), player.get_name()))
        return True

    s["run_elapsed"] += dt
    run = s["run"]
    if not run["started"]:
        run["started"] = True
        s["run_elapsed"] = 0.0

    # Refill the player on a fixed real-time cadence so an early death does not truncate later inputs.
    if debug and int(s["run_elapsed"] * 2) != int((s["run_elapsed"] - dt) * 2):
        debug.debug_refill_player()
    attack = next((t for t in ATTACK_PULSES if t <= s["run_elapsed"] < t + 0.12 and t not in s["keys"]), None)
    dodge = next((t for t in DODGE_PULSES if t <= s["run_elapsed"] < t + 0.12 and ("dodge", t) not in s["keys"]), None)
    if attack is not None:
        unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(ATTACK_ACTION), unreal.Vector(1, 0, 0))
        s["keys"][attack] = True
        run["inputs"].append({"action": "attack", "scheduled_seconds": attack})
    if dodge is not None:
        unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(DODGE_ACTION), unreal.Vector(1, 0, 0))
        s["keys"][("dodge", dodge)] = True
        run["inputs"].append({"action": "dodge", "scheduled_seconds": dodge})

    move = str(tracker.get_current_move())
    instance = int(tracker.get_attack_instance())
    commits = int(tracker.get_commit_count())
    illegal = int(tracker.get_illegal_start_count())
    doubles = int(tracker.get_double_launch_count())
    decision = (move, instance)
    if s["previous"].get("decision") != decision:
        s["events"].append({"kind": "tracker_move", "move": move, "instance": instance})
        s["previous"]["decision"] = decision
    counters = (commits, illegal, doubles)
    if s["previous"].get("counters") != counters:
        s["events"].append({"kind": "tracker_counters", "move": move,
                             "commits": commits, "illegal_starts": illegal,
                             "double_launches": doubles})
        s["previous"]["counters"] = counters

    mesh = player.get_components_by_class(unreal.SkeletalMeshComponent)
    anim = mesh[0].get_anim_instance() if mesh else None
    montage = anim.get_current_active_montage() if anim else None
    montage_name = montage.get_name() if montage else "None"
    if s["previous"].get("player_montage") != montage_name:
        s["events"].append({"kind": "player_montage", "name": montage_name})
        s["previous"]["player_montage"] = montage_name

    if s["run_elapsed"] >= RUN_SECONDS:
        run["status"] = "complete"
        run["events"] = s["events"]
        run["final"] = {"attack_instance": instance, "commits": commits,
                        "illegal_starts": illegal, "double_launches": doubles,
                        "participant_generation": str(encounter.get_participant_generation_text())
                        if hasattr(encounter, "get_participant_generation_text") else "unavailable"}
        s["runs"].append(run)
        save_receipt()
        log("RUN_JSON " + json.dumps(run, sort_keys=True, separators=(",", ":")))
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        s.update(phase="await_end", wait_elapsed=0.0, run=None)
    return True


def finish(reason):
    global state
    if state["handle"] is not None:
        unreal.unregister_slate_post_tick_callback(state["handle"])
        state["handle"] = None
    if game_world() is not None:
        try:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        except Exception:
            pass
    if reason:
        log("FAILED " + reason)
        state["fatal"] = reason
    try:
        save_receipt()
    except Exception as exc:
        log("receipt not saved: " + repr(exc))
    log("completed runs=%d/6" % len(state["runs"]))


def tick(dt):
    s = state
    try:
        if s["phase"] == "prepare":
            if editor_world().get_name() != "L_SevarogArena":
                raise RuntimeError("open L_SevarogArena before running the lead-owned determinism driver")
            if not DATA_SELECTION:
                raise RuntimeError("H019_ENCOUNTER_DEFINITION must name the selected-route definition")
            if not 0 <= SEED <= 4294967295:
                raise RuntimeError("OBF_DETERMINISM_SEED must be in the uint32 range 0..4294967295")
            if os.path.exists(OUT_DIR) and os.listdir(OUT_DIR):
                raise RuntimeError("output directory must be empty: " + OUT_DIR)
            os.makedirs(OUT_DIR, exist_ok=True)
            s["arms"] = [{"route": route, "repeat": repeat}
                          for route in ("legacy", "data") for repeat in range(1, 4)]
            s["phase"] = "next_arm"
        elif s["phase"] == "next_arm":
            if s["run_index"] >= 6:
                finish("")
                return
            configure_arm(s["arms"][s["run_index"]])
        elif s["phase"] == "await_world":
            s["wait_elapsed"] += dt
            world = game_world()
            if world is not None and capture_tick(world, dt):
                return
            if s["wait_elapsed"] > MAX_WAIT:
                raise RuntimeError("PIE world did not produce the expected player/boss/tracker components")
        elif s["phase"] == "capture":
            if game_world() is None:
                raise RuntimeError("PIE ended before the capture reached its terminal time")
            capture_tick(game_world(), dt)
            if s["phase"] == "capture" and s["run_elapsed"] > MAX_WAIT:
                raise RuntimeError("capture exceeded timeout")
        elif s["phase"] == "await_end":
            s["wait_elapsed"] += dt
            if game_world() is None:
                s["run_index"] += 1
                s["phase"] = "next_arm"
            elif s["wait_elapsed"] > MAX_WAIT:
                raise RuntimeError("PIE did not end after end-play was requested")
    except Exception as exc:
        finish(repr(exc))


state["handle"] = unreal.register_slate_post_tick_callback(tick)
log("driver loaded: seed=%d, 6 arms, 35 real seconds each; no Editor run has been started by import" % SEED)
