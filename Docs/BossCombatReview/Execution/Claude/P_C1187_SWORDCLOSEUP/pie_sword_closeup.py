"""Lead close-up capture (C-1187): Ember Warden greatsword grip after the C-1172 trace routing + A-681 grip fix.
Holds the boss, hides the player mesh and stands the player 230 cm from the boss so its own camera frames him, from two angles (35 and 90 deg),
captures idle frames, then one tracked A1 swing at slomo 0.5. HighResShot 960x540, warm-up until a bright frame.
Log prefix [SwordCloseup]; stop marker "[SwordCloseup] finished:". Saves nothing; frames go to SWORD_FRAMES (D:)."""
import math
import os
import sys
import time
from pathlib import Path

import unreal

sys.path.insert(0, str(Path(unreal.Paths.project_dir()) / "Scripts" / "Editor"))
import pie_lead_common as plc

LOG = "[SwordCloseup] "
FRAMES = os.environ.get("SWORD_FRAMES", "D:/FightVideo/sword_closeup")
S = {"gen": None, "done": False, "frame": 0, "pending": None, "t_req": 0.0}
HANDLE = None


def log(m):
    unreal.log(LOG + str(m))


def actors():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    return world, pc, pawn, (plc.boss_actor(world) if world else None)


def wait(seconds):
    end = plc.game_time(actors()[0]) + seconds
    while plc.game_time(actors()[0]) < end:
        yield 0.0


def shot(label):
    """Request one HighResShot and wait (real time) until the PNG exists."""
    world = actors()[0]
    path = "%s/%s_%03d.png" % (FRAMES, label, S["frame"])
    S["frame"] += 1
    unreal.SystemLibrary.execute_console_command(world, "HighResShot 960x540 filename=%s" % path)
    deadline = time.perf_counter() + 15.0
    while not os.path.exists(path) and time.perf_counter() < deadline:
        yield 0.0
    log("FRAME %s exists=%s g=%.3f" % (path, os.path.exists(path), plc.game_time(actors()[0])))
    return path


def place_camera(world, pc, pawn, boss, angle_deg, dist=230.0):
    """Hide the player mesh and stand the (invisible) player dist cm from the boss at angle_deg off the boss's facing,
    looking at the boss, so the player's own camera frames the boss at close range."""
    loc = boss.get_actor_location()
    yaw = math.radians(boss.get_actor_rotation().yaw + angle_deg)
    pos = (loc.x + math.cos(yaw) * dist, loc.y + math.sin(yaw) * dist, loc.z + 20.0)
    facing = math.degrees(math.atan2(loc.y - pos[1], loc.x - pos[0]))
    pawn.set_actor_hidden_in_game(True)
    plc.place_player(pc, pawn, pos, facing)
    pc.set_control_rotation(unreal.Rotator(0.0, -8.0, facing))
    log("CAMERA angle=%d player_pos=%s" % (angle_deg, pos))


def log_boss_meshes(boss, tag):
    """C-1198: name every rendered static/skeletal mesh on the boss (to identify the second blade)."""
    for cls in (unreal.StaticMeshComponent, unreal.SkeletalMeshComponent):
        for c in boss.get_components_by_class(cls):
            try:
                mesh = c.static_mesh if cls is unreal.StaticMeshComponent else c.get_skeletal_mesh_asset()
            except Exception:
                mesh = None
            try:
                parent = c.get_attach_parent()
                sock = c.get_attach_socket_name()
            except Exception:
                parent, sock = None, None
            log("MESH %s comp=%s mesh=%s visible=%s hidden_in_game=%s parent=%s socket=%s" % (
                tag, c.get_name(), mesh.get_name() if mesh else None, c.is_visible(),
                c.get_editor_property("hidden_in_game") if False else "n/a", parent.get_name() if parent else None, sock))


def witness():
    world, pc, pawn, boss = actors()
    encounter = plc.component(boss, "RPGBossEncounter")
    tracker = plc.component(boss, "RPGAttackTracker")
    encounter.reset_for_test()
    yield from wait(1.0)
    encounter.wake()
    encounter.hold_for_test(True)
    plc.refill_player(boss)
    yield from wait(2.5)
    log_boss_meshes(boss, "after_wake")
    for angle in (35, 90):
        place_camera(world, pc, pawn, boss, angle)
        yield from wait(0.6)
        # warm up until a frame is not black (black 960x540 PNG ~10 KB)
        bright = 0
        for _ in range(30):  # need 3 consecutive bright frames after the camera move (C-1188)
            p = yield from shot("warm_a%d" % angle)
            bright = bright + 1 if os.path.exists(p) and os.path.getsize(p) > 300000 else 0
            if bright >= 3:
                break
        for _ in range(3):
            yield from shot("idle_a%d" % angle)
            yield from wait(0.3)
        unreal.SystemLibrary.execute_console_command(actors()[0], "slomo 0.4")
        started = bool(tracker.start_move("Close", True))  # X-1688: A1-family via the pack Close ability
        log("CLOSE started=%s angle=%d" % (started, angle))
        log_boss_meshes(boss, "swing_a%d" % angle)
        t0 = plc.game_time(actors()[0])
        while plc.game_time(actors()[0]) - t0 < 3.0:
            yield from shot("swing_a%d" % angle)
            yield from wait(0.08)
        unreal.SystemLibrary.execute_console_command(actors()[0], "slomo 1")
        yield from wait(1.5)


def finish(reason):
    global HANDLE
    if S["done"]:
        return
    S["done"] = True
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    log("finished: %s frames=%d" % (reason, S["frame"]))
    plc.end_play()


def tick(dt):
    try:
        world = actors()[0]
        if S["gen"] is None:
            if world is None:
                if not S.get("requested"):
                    S["requested"] = True
                    sel = os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()
                    if sel:
                        unreal.SystemLibrary.execute_console_command(None, "rpg.EncounterDefinition " + sel)
                    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                    S["t_req"] = time.perf_counter()
                return
            _, pc, pawn, boss = actors()
            if not (pawn and boss) or time.perf_counter() - S["t_req"] < 6.0:
                return
            os.makedirs(FRAMES, exist_ok=True)
            S["gen"] = witness()
        next(S["gen"])
    except StopIteration:
        finish("all angles recorded")
    except Exception:
        import traceback
        log("ERROR " + traceback.format_exc())
        finish("exception")


HANDLE = unreal.register_slate_post_tick_callback(tick)
log("driver registered")
