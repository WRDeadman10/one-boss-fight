"""Lead-only real A4 block -> armed counter -> R2/HP witness on both routes."""
import math
import os
import sys
import time
from pathlib import Path

import unreal

sys.path.insert(0, str(Path(unreal.Paths.project_dir()) / "Scripts" / "Editor"))
import pie_lead_common as plc

LOG = "[ERA4Counter] "
BLOCK_PATH = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Block"
R2 = "Gamepad_RightTrigger"
LANE_DISTANCE_CM = 140.0  # A4's authored 60–380 cm band; close enough for the counter clip's ~130 cm reach.
S = {"phase": "start", "elapsed": 0.0, "gen": None, "wake": 0.0,
     "done": False, "result": False, "r2_down": False}
HANDLE = None


def log(message):
    unreal.log(LOG + str(message))


def wait(seconds):
    deadline = time.perf_counter() + seconds
    while time.perf_counter() < deadline:
        yield 0.0


def actors():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    return world, pc, pawn, plc.boss_actor(world)


def boss_montage(boss):
    for mesh in boss.get_components_by_class(unreal.SkeletalMeshComponent):
        instance = mesh.get_anim_instance()
        montage = instance.get_current_active_montage() if instance else None
        if montage:
            return montage.get_name()
    return "None"


def key(pc, down):
    if not unreal.RPGInputTestUtils.set_key_down(pc, R2, down):
        raise RuntimeError("R2 input refused")
    S["r2_down"] = down


def block(pc, action):
    if not unreal.RPGInputTestUtils.inject_action(pc, action, unreal.Vector(1.0, 0.0, 0.0)):
        raise RuntimeError("IA_Block input refused")


def valid_counter(armed, montages, before, after):
    return (armed and "AM_ER_Attack_GuardCounter" in montages and
            isinstance(before, (int, float)) and isinstance(after, (int, float)) and
            math.isfinite(before) and math.isfinite(after) and after < before - 0.1)


def draw_ready(loadout, pawn):
    return bool(loadout.is_combat_enabled()) and plc.player_montage(pawn)[0] is None


def witness():
    world, pc, pawn, boss = actors()
    if not all((world, pc, pawn, boss)):
        raise RuntimeError("player/controller/boss unavailable")
    encounter = plc.component(boss, "RPGBossEncounter")
    tracker = plc.component(boss, "RPGAttackTracker")
    sweep = plc.component(boss, "RPGBossLowSweep")
    dodge = plc.component(pawn, "RPGDodgeTiming")
    loadout = plc.component(pawn, "RPGBuildLoadout")
    if not all((encounter, tracker, sweep, dodge, loadout)):
        raise RuntimeError("encounter/tracker/sweep/dodge/loadout component missing")
    action = unreal.load_asset(BLOCK_PATH)
    if action is None:
        raise RuntimeError("IA_Block asset missing")
    encounter.reset_for_test()
    yield from wait(1.0)
    encounter.wake()
    encounter.hold_for_test(True)
    plc.refill_player(boss)
    yield from wait(2.2)
    plc.enter_combat(pawn)
    # Draw before moving into the blade lane. C-1043 showed the style switch
    # can land after the first fixed wait, so poll readiness and retry.
    yield from wait(1.0)
    draw_ready_state = False
    for attempt in range(1, 4):
        key(pc, True)
        yield from wait(0.7)
        key(pc, False)
        deadline = time.perf_counter() + 5.0
        while time.perf_counter() < deadline:
            ready_now = draw_ready(loadout, pawn)
            if ready_now:
                draw_ready_state = True
                break
            yield 0.0
        log("DRAW_READY attempt=%d ready=%s combat_enabled=%s active_montage=%s" %
            (attempt, draw_ready_state, loadout.is_combat_enabled(), plc.player_montage(pawn)[0]))
        if draw_ready_state:
            break
    if not draw_ready_state:
        raise RuntimeError("weapon draw not ready after three R2 attempts")
    ready_deadline = time.perf_counter() + 5.0
    while not tracker.is_neutral() and time.perf_counter() < ready_deadline:
        yield 0.0
    if not tracker.is_neutral():
        raise RuntimeError("boss not neutral before A4")
    origin = boss.get_actor_location()
    yaw = math.radians(boss.get_actor_rotation().yaw)
    pos = (origin.x + math.cos(yaw) * LANE_DISTANCE_CM,
           origin.y + math.sin(yaw) * LANE_DISTANCE_CM, origin.z + 20.0)
    facing = math.degrees(math.atan2(origin.y - pos[1], origin.x - pos[0]))
    plc.place_player(pc, pawn, pos, facing)
    yield from wait(0.4)
    if not dodge.is_elden_ring_input_active():
        raise RuntimeError("Elden Ring input context inactive")
    for _ in range(10):
        block(pc, action)
        yield 0.0
    hp_before = plc.health(boss)
    if hp_before is None:
        raise RuntimeError("boss health unavailable")
    sweep_before = sweep.get_sweep_count()
    started = bool(tracker.start_move("A4", True))
    actual_distance = (pawn.get_actor_location() - boss.get_actor_location()).length()
    log("A4_START started=%s boss_hp=%.3f sweep_before=%d lane_cm=%.0f actual_distance_cm=%.1f block=IA_Block" %
        (started, hp_before, sweep_before, LANE_DISTANCE_CM, actual_distance))
    if not started:
        raise RuntimeError("A4 StartMove refused")
    armed = False
    deadline = time.perf_counter() + 7.0
    while time.perf_counter() < deadline:
        block(pc, action)
        armed = bool(dodge.is_guard_counter_armed())
        if armed:
            log("REAL_GUARD_ARMED game_time=%.3f A4_pos=%.3f active=%s sweep_delta=%d player_hp=%s guard_state=%s" %
                (plc.game_time(world), tracker.get_position(), tracker.is_active_window(),
                 sweep.get_sweep_count() - sweep_before, plc.health(pawn), dodge.describe_guard_state()))
            break
        yield 0.0
    if not armed:
        log("NO_REAL_GUARD_ARM A4_pos=%.3f sweep_delta=%d boss_montage=%s guard_state=%s" %
            (tracker.get_position(), sweep.get_sweep_count() - sweep_before,
             boss_montage(boss), dodge.describe_guard_state()))
        return
    # IA_Block is frame scoped. Stop injecting it before R2; press within the
    # source's armed 0.60 s window, with no synthetic arm or montage assignment.
    yield 0.0
    if not dodge.is_guard_counter_armed():
        raise RuntimeError("real guard window expired before R2")
    strong_before = dodge.get_elden_ring_strong_count()
    hp_before = plc.health(boss)
    press_time = plc.game_time(world)
    key(pc, True)
    log("COUNTER_R2_PRESS game_time=%.3f armed=True strong_before=%d boss_hp_before=%s distance_cm=%.1f" %
        (press_time, strong_before, hp_before, (pawn.get_actor_location() - boss.get_actor_location()).length()))
    montages = set()
    release_at = press_time + 0.12
    observe_until = press_time + 2.5
    while plc.game_time(world) < observe_until:
        now = plc.game_time(world)
        if S["r2_down"] and now >= release_at:
            key(pc, False)
            log("COUNTER_R2_RELEASE game_time=%.3f" % now)
        name, _ = plc.player_montage(pawn)
        meshes = pawn.get_components_by_class(unreal.SkeletalMeshComponent)
        if meshes and name and "AM_ER_Attack_GuardCounter" in name:
            hand = meshes[0].get_socket_location("hand_r")
            hand_distance = (hand - boss.get_actor_location()).length()
            log("COUNTER_REACH game_time=%.3f montage=%s hand_to_boss_cm=%.1f boss_hp=%s" %
                (now, name, hand_distance, plc.health(boss)))
        if name and name not in montages:
            montages.add(name)
            log("PLAYER_MONTAGE name=%s game_time=%.3f" % (name, now))
        yield 0.0
    hp_after = plc.health(boss)
    strong_after = dodge.get_elden_ring_strong_count()
    S["result"] = valid_counter(armed, montages, hp_before, hp_after)
    log("RESULT pass=%s real_guard=%s strong_delta=%d counter_montage=%s boss_hp_before=%s boss_hp_after=%s boss_hp_delta=%s" %
        (S["result"], armed, strong_after - strong_before,
         "AM_ER_Attack_GuardCounter" in montages, hp_before, hp_after,
         hp_after - hp_before if hp_after is not None and hp_before is not None else "unreadable"))


def finish(reason):
    global HANDLE
    if S["done"]:
        return
    S["done"] = True
    try:
        _, pc, _, boss = actors()
        if S["r2_down"] and pc:
            key(pc, False)
        encounter = plc.component(boss, "RPGBossEncounter") if boss else None
        if encounter:
            encounter.hold_for_test(False)
    except Exception:
        pass
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    log("SUMMARY pass=%s reason=%s" % (S["result"], reason))
    plc.end_play()


def tick(dt):
    try:
        S["elapsed"] += dt
        if S["elapsed"] > 45.0:
            finish("timeout")
            return
        if S["phase"] == "start":
            if S["elapsed"] > 0.5:
                selection = os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()
                if selection:
                    unreal.SystemLibrary.execute_console_command(None, "rpg.EncounterDefinition " + selection)
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                S.update(phase="wait", elapsed=0.0)
            return
        world, pc, pawn, boss = actors()
        if S["phase"] == "wait":
            if all((world, pc, pawn, boss)) and S["elapsed"] > 6.0:
                S.update(phase="run", gen=witness())
            elif S["elapsed"] > 25.0:
                finish("actors missing")
            return
        if world and plc.game_time(world) >= S["wake"]:
            try:
                S["wake"] = plc.game_time(world) + float(next(S["gen"]))
            except StopIteration:
                finish("witness complete")
    except Exception:
        import traceback
        log("ERROR " + traceback.format_exc())
        finish("exception")


HANDLE = unreal.register_slate_post_tick_callback(tick)
