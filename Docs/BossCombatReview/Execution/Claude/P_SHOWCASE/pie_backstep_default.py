"""Lead showcase capture (owner 2026-11-08 "Yes, showcase clips"): each new move performed cleanly in open ground
against the held Ember Warden, 960x540 in-engine frames at 15 fps of game time (slomo 0.5), one SEG marker per clip.

Segments: backstep x2, air_light x2, air_heavy x2, guard_counter x2 (real blocked A4 -> R2), parry x1 (real A4 parry,
Tier 2 recoil + distortion). Boss held between moves (hold_for_test), Tier 2 on, player refilled. Frames are captured only
inside segments. Log prefix [Showcase]; stop marker "[Showcase] finished:".
"""
import math
import os
import sys
import time
from pathlib import Path

import unreal

sys.path.insert(0, str(Path(unreal.Paths.project_dir()) / "Scripts" / "Editor"))
import pie_lead_common as plc

LOG = "[Showcase] "
FRAMES = os.environ.get("SHOWCASE_FRAMES", "D:/FightVideo/showcase")
FPS = 15.0
R1, R2, JUMP, DODGE = "Gamepad_RightShoulder", "Gamepad_RightTrigger", "Gamepad_FaceButton_Bottom", "Gamepad_FaceButton_Right"
BLOCK_PATH = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Block"
S = {"gen": None, "done": False, "frame": 0, "pending": None, "g_shot": -1.0, "capturing": False, "seg": None, "held": set()}
HANDLE = None


def log(m):
    unreal.log(LOG + str(m))


def actors():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    return world, pc, pawn, (plc.boss_actor(world) if world else None)


def key(pc, k, down):
    unreal.RPGInputTestUtils.set_key_down(pc, k, down)
    (S["held"].add if down else S["held"].discard)(k)


def capture(world):
    if not S["capturing"]:
        return
    g = plc.game_time(world)
    if S["pending"] is not None and not os.path.exists(S["pending"]):
        return
    if g - S["g_shot"] < 1.0 / FPS:
        return
    S["g_shot"] = g
    S["pending"] = "%s/f_%05d.png" % (FRAMES, S["frame"])
    unreal.SystemLibrary.execute_console_command(world, "HighResShot 960x540 filename=%s" % S["pending"])
    log("FRAME %d g=%.3f seg=%s" % (S["frame"], g, S["seg"]))
    S["frame"] += 1


def wait(seconds):
    """Wait in GAME seconds (capture stalls real time)."""
    world = actors()[0]
    end = plc.game_time(world) + seconds
    while plc.game_time(actors()[0]) < end:
        yield 0.0


def seg_begin(name):
    S["seg"] = name
    S["capturing"] = True
    log("SEG_BEGIN %s frame=%d" % (name, S["frame"]))


def seg_end():
    log("SEG_END %s frame=%d" % (S["seg"], S["frame"]))
    S["capturing"] = False
    S["seg"] = None


def lane(pc, pawn, boss, distance):
    origin = boss.get_actor_location()
    yaw = math.radians(boss.get_actor_rotation().yaw)
    pos = (origin.x + math.cos(yaw) * distance, origin.y + math.sin(yaw) * distance, origin.z + 20.0)
    facing = math.degrees(math.atan2(origin.y - pos[1], origin.x - pos[0]))
    plc.place_player(pc, pawn, pos, facing)


def taps(pc, events):
    """events: list of (game_time_offset, key, down)."""
    world = actors()[0]
    t0 = plc.game_time(world)
    for t, k, down in events:
        while plc.game_time(actors()[0]) - t0 < t:
            yield 0.0
        key(pc, k, down)


def wait_neutral(tracker, limit=6.0):
    deadline = time.perf_counter() + limit
    while not tracker.is_neutral() and time.perf_counter() < deadline:
        yield 0.0


def witness():
    world, pc, pawn, boss = actors()
    encounter = plc.component(boss, "RPGBossEncounter")
    tracker = plc.component(boss, "RPGAttackTracker")
    dodge = plc.component(pawn, "RPGDodgeTiming")
    loadout = plc.component(pawn, "RPGBuildLoadout")
    parry = plc.component(pawn, "RPGPlayerParry")
    block_action = unreal.load_asset(BLOCK_PATH)
    log("runtime BackstepMontage=DEFAULT (no assignment) value=%s" % dodge.get_editor_property("backstep_montage"))
    encounter.reset_for_test()
    yield from wait(1.0)
    encounter.wake()
    encounter.hold_for_test(True)
    plc.refill_player(boss)
    yield from wait(2.2)
    plc.enter_combat(pawn)
    yield from wait(1.0)
    for attempt in range(3):
        key(pc, R2, True)
        yield from wait(0.7)
        key(pc, R2, False)
        deadline = time.perf_counter() + 5.0
        while time.perf_counter() < deadline and not (loadout.is_combat_enabled() and plc.player_montage(pawn)[0] is None):
            yield 0.0
        if loadout.is_combat_enabled():
            break
    log("draw ready=%s" % loadout.is_combat_enabled())
    unreal.SystemLibrary.execute_console_command(actors()[0], "slomo 0.5")

    for rep in range(3):
        plc.refill_player(boss)
        lane(pc, pawn, boss, 300.0)
        yield from wait(0.6)
        seg_begin("mixamo_backstep_%d" % (rep + 1))
        yield from wait(0.3)
        p0 = pawn.get_actor_location()
        yield from taps(pc, [(0.0, DODGE, True), (0.10, DODGE, False)])
        t_end = plc.game_time(actors()[0]) + 2.2
        while plc.game_time(actors()[0]) < t_end:
            p = pawn.get_actor_location()
            log("POS rep=%d g=%.3f dist_from_start_cm=%.1f montage=%s" % (rep + 1, plc.game_time(actors()[0]), (p - p0).length(), plc.player_montage(pawn)[0]))
            yield 0.0
        seg_end()
    unreal.SystemLibrary.execute_console_command(actors()[0], "slomo 1")


def finish(reason):
    global HANDLE
    if S["done"]:
        return
    S["done"] = True
    try:
        _, pc, _, _ = actors()
        for k in list(S["held"]):
            unreal.RPGInputTestUtils.set_key_down(pc, k, False)
    except Exception:
        pass
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    log("SUMMARY frames=%d" % S["frame"])
    log("finished: " + reason)
    plc.end_play()


def tick(dt):
    try:
        world = actors()[0]
        if S["gen"] is None:
            if world is None:
                if not S.get("requested"):
                    S["requested"] = True
                    unreal.SystemLibrary.execute_console_command(None, "rpg.Art.Tier2 1")
                    sel = os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()
                    if sel:
                        unreal.SystemLibrary.execute_console_command(None, "rpg.EncounterDefinition " + sel)
                    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                    S["t_req"] = time.perf_counter()
                return
            _, pc, pawn, boss = actors()
            if not (pawn and boss) or time.perf_counter() - S["t_req"] < 6.0:
                return
            S["gen"] = witness()
        capture(world)
        next(S["gen"])
    except StopIteration:
        finish("all segments recorded")
    except Exception:
        import traceback
        log("ERROR " + traceback.format_exc())
        finish("exception")


HANDLE = unreal.register_slate_post_tick_callback(tick)
log("driver registered")
