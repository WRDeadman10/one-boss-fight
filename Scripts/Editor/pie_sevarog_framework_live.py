"""C-1254a: Lead-run Sevarog framework duel driver; transient check never spawns or enters PIE."""
import os
import sys
import time
import uuid
import traceback
from pathlib import Path

import unreal

sys.path.insert(0, str(Path(unreal.Paths.project_dir()) / "Scripts" / "Editor"))
import pie_lead_common as plc

LOG = "[SevarogLive] "
PROFILE_PATH = "/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_FrameworkProfile_Draft"
EXPECTED_CARDS = (
    "Move_Sevarog_Swing1_Medium",
    "Move_Sevarog_Swing2_Medium",
    "Move_Sevarog_Swing3_Slow",
    "Move_Sevarog_Speedburst",
)
COMBO_SOURCE = "Move_Sevarog_Speedburst"
COMBO_FOLLOWUP = None
OUT_ROOT = "D:/FightVideo/sevarog_live"
SHOT_WIDTH, SHOT_HEIGHT = 960, 540
STATE = {"done": False, "world_requested": False, "started_at": 0.0, "next_index": 0,
         "active_id": None, "wait_started": 0.0, "pawn_wait": 0.0, "next_due": 0.0, "final_due": 0.0, "last_missing": 0.0,
         "combo_seen": False, "reason": "not_started", "shots": 0}
HANDLE = None


def log(message):
    unreal.log(LOG + str(message))


def read_property(obj, *names):
    last_error = None
    for name in names:
        try:
            return obj.get_editor_property(name)
        except Exception as error:
            last_error = error
    raise RuntimeError("cannot read reflected property %s: %s" % (names, last_error))


def profile_report():
    profile = unreal.load_asset(PROFILE_PATH)
    if profile is None:
        raise RuntimeError("authored framework profile did not load: " + PROFILE_PATH)
    library = getattr(unreal, "RPGBossCardValidationLibrary", None)
    validate = getattr(library, "validate_framework_profile_report", None) if library else None
    if not callable(validate):
        raise RuntimeError("production ValidateFrameworkProfileReport bridge is unavailable")
    report = str(validate(profile))
    if report != "PASS":
        raise RuntimeError("production profile resolution refused: " + report)
    cards = profile.get_editor_property("cards")
    if not cards:
        raise RuntimeError("resolved profile has no candidate cards")
    move_ids = []
    for candidate in cards:
        card = read_property(candidate, "card", "Card")
        if card is None:
            raise RuntimeError("profile contains a null candidate card")
        spec = read_property(card, "spec", "Spec")
        move_id = str(read_property(spec, "move_id", "MoveId"))
        move_ids.append(move_id)
    missing = [move_id for move_id in EXPECTED_CARDS if move_id not in move_ids]
    if missing:
        raise RuntimeError("profile is missing expected combo cards: " + ",".join(missing))
    log("PROFILE PASS path=%s candidates=%d move_ids=%s" %
        (PROFILE_PATH, len(move_ids), ",".join(move_ids)))
    nodes = read_property(profile, "combo_nodes", "ComboNodes")
    node_moves = {}
    for node in nodes:
        node_id = str(read_property(node, "node_id", "NodeId"))
        node_moves[node_id] = str(read_property(node, "move_id", "MoveId"))
    source_nodes = [node for node in nodes if str(read_property(node, "move_id", "MoveId")) == COMBO_SOURCE]
    if not source_nodes:
        raise RuntimeError("profile combo graph has no node for " + COMBO_SOURCE)
    edges = read_property(source_nodes[0], "edges", "Edges")
    if not edges:
        raise RuntimeError("profile combo node has no follow-up edge for " + COMBO_SOURCE)
    target_node = str(read_property(edges[0], "to_node", "ToNode"))
    followup = node_moves.get(target_node)
    if not followup:
        raise RuntimeError("profile combo edge points to missing node " + target_node)
    if followup not in move_ids:
        raise RuntimeError("combo follow-up card is missing from profile candidates: " + followup)
    log("PROFILE COMBO_NODES count=%d source=%s followup=%s target_node=%s" %
        (len(nodes), COMBO_SOURCE, followup, target_node))
    return profile, followup


def check_bridge_reflection():
    cls = getattr(unreal, "RPGFrameworkBossCharacter", None)
    if cls is None:
        raise RuntimeError("RPGFrameworkBossCharacter Python class is unavailable")
    init = getattr(cls, "initialize_with_profile_for_test", None)
    start = getattr(cls, "start_card_for_test", None)
    spawn = getattr(cls, "spawn_framework_boss_for_test", None)
    if not callable(init) or not callable(start) or not callable(spawn):
        raise RuntimeError("test bridge UFUNCTIONs are not exposed to Python")
    log("LIVE_API PASS initialize_with_profile_for_test=1 start_card_for_test=1 spawn_framework_boss_for_test=1")


def live_world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def finish(reason):
    global HANDLE
    if STATE["done"]:
        return
    STATE["done"] = True
    STATE["reason"] = str(reason)
    if HANDLE:
        try:
            unreal.unregister_slate_post_tick_callback(HANDLE)
        except Exception:
            pass
        HANDLE = None
    log("finished: %s shots=%d" % (STATE["reason"], STATE["shots"]))
    try:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception as error:
        log("END_PIE request_failed=%s" % error)


def spawn_live_boss(world, pawn, profile):
    cls = getattr(unreal, "RPGFrameworkBossCharacter", None)
    spawn = getattr(cls, "spawn_framework_boss_for_test", None) if cls else None
    if cls is None or not callable(spawn):
        raise RuntimeError("SpawnFrameworkBossForTest bridge is unavailable")
    player_loc = pawn.get_actor_location()
    player_forward = pawn.get_actor_forward_vector()
    spawn_loc = player_loc + player_forward * 160.0
    spawn_rot = unreal.Rotator(0.0, pawn.get_actor_rotation().yaw + 180.0, 0.0)
    boss = spawn(world, cls, spawn_loc, spawn_rot)
    if boss is None:
        raise RuntimeError("SpawnFrameworkBossForTest refused transient Sevarog spawn")
    try:
        initialized = boss.initialize_with_profile_for_test(profile, pawn)
    except Exception as error:
        boss.destroy_actor()
        raise RuntimeError("InitializeWithProfileForTest call failed: %s" % error)
    log("INIT_RESULT type=%s repr=%r" % (type(initialized).__name__, initialized))
    error_text = ""
    ok = initialized
    if isinstance(initialized, tuple):
        ok = initialized[0] if initialized else False
        error_text = str(initialized[1]) if len(initialized) > 1 else ""
    elif isinstance(initialized, str):
        error_text = initialized
        ok = not error_text
    if not ok:
        boss.destroy_actor()
        raise RuntimeError("profile initialization refused: %s" % error_text)
    STATE["started_at"] = plc.game_time(world)
    log("SPAWN PASS actor=%s initialPlayerDistanceCm=%.1f" %
        (boss.get_name(), (pawn.get_actor_location() - boss.get_actor_location()).length()))
    return boss


def shot(world, boss, move_id):
    if os.environ.get("SEVAROG_LIVE_SHOTS") != "1":
        return
    os.makedirs(OUT_ROOT, exist_ok=True)
    path = os.path.join(OUT_ROOT, "%s_%s.png" % (move_id, uuid.uuid4().hex[:8]))
    unreal.SystemLibrary.execute_console_command(
        world, "HighResShot %dx%d filename=%s" % (SHOT_WIDTH, SHOT_HEIGHT, path))
    STATE["shots"] += 1
    log("SHOT requested move=%s path=%s" % (move_id, path))


def tick(delta_seconds):
    if STATE["done"]:
        return
    try:
        world = live_world()
        if world is None:
            if not STATE["world_requested"]:
                STATE["world_requested"] = True
                STATE["wait_started"] = time.perf_counter()
                log("WAITING_FOR_PIE")
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            elif time.perf_counter() - STATE["wait_started"] > 60.0:
                finish("failed: PIE world did not start")
            return
        pc = unreal.GameplayStatics.get_player_controller(world, 0)
        pawn = pc.get_controlled_pawn() if pc else None
        if pawn is None:
            if STATE["pawn_wait"] == 0.0:
                STATE["pawn_wait"] = time.perf_counter()
            if time.perf_counter() - STATE["pawn_wait"] > 30.0:
                finish("failed: player pawn missing")
            return
        STATE["pawn_wait"] = 0.0
        profile = unreal.load_asset(PROFILE_PATH)
        if profile is None:
            raise RuntimeError("framework profile disappeared in PIE")
        cls = getattr(unreal, "RPGFrameworkBossCharacter", None)
        bosses = unreal.GameplayStatics.get_all_actors_of_class(world, cls) if cls else []
        boss = next((actor for actor in bosses if actor.get_name().startswith("RPGFrameworkBossCharacter")), None)
        if boss is None:
            now = time.perf_counter()
            if now - STATE["last_missing"] >= 2.0:
                STATE["last_missing"] = now
                log("HEARTBEAT missing_boss=1 player=1")
            boss = spawn_live_boss(world, pawn, profile)
            STATE["active_id"] = None
            return
        now = plc.game_time(world)
        if STATE["active_id"] is None and STATE["next_index"] < len(EXPECTED_CARDS):
            move_id = EXPECTED_CARDS[STATE["next_index"]]
            if move_id == "Move_Sevarog_Speedburst":
                away = boss.get_actor_forward_vector()
                target_loc = boss.get_actor_location() + away * 450.0
                pawn.set_actor_location(target_loc, False, None, unreal.TeleportType.TELEPORT_PHYSICS)
                log("SETUP move=%s requestedRangeCm=450" % move_id)
            if STATE["wait_started"] == 0.0:
                STATE["wait_started"] = now
                log("CARD request move=%s" % move_id)
            result = boss.start_card_for_test(move_id)
            if result:
                STATE["active_id"] = move_id
                STATE["wait_started"] = 0.0
                STATE["next_index"] += 1
                duration = 8.0
                log("CARD accepted move=%s targetDistanceCm=%.1f" %
                    (move_id, (pawn.get_actor_location() - boss.get_actor_location()).length()))
                shot(world, boss, move_id)
                STATE["next_due"] = now + duration
                if os.environ.get("SEVAROG_LIVE_SELF_TEST") == "1" and STATE["next_index"] == 1:
                    log("SELF_TEST PASS spawned=1 first_card=%s started=1" % move_id)
                    finish("self-test passed: spawned and started S1")
                    return
            elif now - STATE["wait_started"] > 35.0:
                raise RuntimeError("card start timed out move=%s" % move_id)
            return
        if STATE["active_id"] is not None and now >= STATE["next_due"]:
            if STATE["active_id"] == "Move_Sevarog_Speedburst":
                log("COMBO expected_followup=%s; inspect native combo_step/event logs for observed branch" % COMBO_FOLLOWUP)
            STATE["active_id"] = None
            STATE["wait_started"] = 0.0
            if STATE["next_index"] >= len(EXPECTED_CARDS):
                STATE["final_due"] = now + 12.0
        if STATE["next_index"] >= len(EXPECTED_CARDS) and STATE["active_id"] is None and STATE["final_due"] > 0.0 and now >= STATE["final_due"]:
            finish("driver complete: four profile cards requested; native combo events/warp summaries are in the UE log")
    except Exception as error:
        log("ERROR " + str(error))
        log(traceback.format_exc())
        finish("failed: %s" % error)


def main():
    global COMBO_FOLLOWUP
    profile, COMBO_FOLLOWUP = profile_report()
    if os.environ.get("SEVAROG_LIVE_TRANSIENT_CHECK") == "1":
        check_bridge_reflection()
        log("finished: transient profile and bridge reflection check only; no PIE, spawn, save, or map edit")
        return
    check_bridge_reflection()
    STATE["started_at"] = time.perf_counter()
    global HANDLE
    HANDLE = unreal.register_slate_post_tick_callback(tick)
    if not HANDLE:
        raise RuntimeError("could not register live-driver tick callback")
    log("READY awaiting PIE; profile=%s optionalShots=%s" %
        (PROFILE_PATH, os.environ.get("SEVAROG_LIVE_SHOTS") == "1"))


try:
    main()
except Exception as error:
    log("ERROR " + str(error))
    log("finished: refused before PIE or driver setup")
    raise
