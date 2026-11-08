"""Lead active camera-inside-boss probe (C-1079). Wakes the boss (not held), keeps the player 120-250 cm from it while
strafing around it with the camera facing the boss, and samples every 0.1 s of game time for 30 s.
Inside tests: (a) camera point inside any visible boss skeletal mesh world AABB (SystemLibrary.get_component_bounds);
(b) camera inside the boss capsule cylinder. Camera yaw orbits 60 deg/s so the boss passes behind the player. Env CAMERA_CVARS applies console vars before PIE.
Log prefix [CamEngage]; stop marker "[CamEngage] SUMMARY"."""
import math
import os
import sys
import time
from pathlib import Path

import unreal

sys.path.insert(0, str(Path(unreal.Paths.project_dir()) / "Scripts" / "Editor"))
import pie_lead_common as plc

LOG = "[CamEngage] "
DATA_ROUTE = os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()
ROUTE = "data" if DATA_ROUTE else "legacy"
S = {"gen": None, "done": False, "n": 0, "mesh_in": 0, "caps_in": 0, "unread": 0, "arm_short": 0, "dist": [], "hidden": 0}
HANDLE = None


def log(m):
    unreal.log(LOG + str(m))


def actors():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    return world, pc, pawn, (plc.boss_actor(world) if world else None)


def mesh_inside(cam, boss):
    names, unread, hidden = [], 0, 0
    for c in boss.get_components_by_class(unreal.SkeletalMeshComponent):
        try:
            if not c.is_visible():
                hidden += 1
                continue
            o, e, _r = unreal.SystemLibrary.get_component_bounds(c)
            if abs(cam.x - o.x) <= e.x and abs(cam.y - o.y) <= e.y and abs(cam.z - o.z) <= e.z:
                names.append(c.get_name())
        except Exception as exc:
            unread += 1
            if not S.get("logged_exc"):
                S["logged_exc"] = True
                log("BOUNDS_ERROR %s" % exc)
    return names, unread, hidden


def capsule_inside(cam, boss):
    cap = boss.get_components_by_class(unreal.CapsuleComponent)[0]
    r, h = cap.get_scaled_capsule_radius(), cap.get_scaled_capsule_half_height()
    c = cap.get_world_location()
    return math.hypot(cam.x - c.x, cam.y - c.y) <= r and abs(cam.z - c.z) <= h


def sample(world, pc, pawn, boss):
    arm = next((a for a in pawn.get_components_by_class(unreal.SpringArmComponent) if a.get_name() == "CameraBoom"), None)
    cam_c = next((c for c in pawn.get_components_by_class(unreal.CameraComponent) if c.get_name() == "FollowCamera"), None)
    cam, pivot = cam_c.get_world_location(), arm.get_world_location()
    names, unread, hidden = mesh_inside(cam, boss)
    caps = capsule_inside(cam, boss)
    arm_len = (cam - pivot).length()
    d = (pawn.get_actor_location() - boss.get_actor_location()).length()
    try:
        view_yaw = cam_c.get_world_rotation().yaw  # camera view yaw (a control-driven spring arm rotates its socket, not the arm component)
        yaw_gap = abs((view_yaw - pc.get_control_rotation().yaw + 540.0) % 360.0 - 180.0)
        to_b = math.degrees(math.atan2(boss.get_actor_location().y - pawn.get_actor_location().y, boss.get_actor_location().x - pawn.get_actor_location().x))
        boss_off = abs((view_yaw - to_b + 540.0) % 360.0 - 180.0)
    except Exception:
        yaw_gap, boss_off = -1.0, -1.0
    S.setdefault("boss_off", []).append(boss_off)
    S["n"] += 1
    S["mesh_in"] += 1 if names else 0
    S["caps_in"] += 1 if caps else 0
    S["unread"] += 1 if unread else 0
    S["hidden"] += 1 if hidden else 0
    S["arm_short"] += 1 if arm_len < 300.0 else 0
    S["dist"].append(d)
    if names or caps or S["n"] % 10 == 0 or os.environ.get("CAM_VERBOSE"):
        log("SAMPLE n=%d g=%.2f dist=%.0f arm=%.0f mesh_in=%s caps_in=%s hidden=%d unread=%d view_vs_control_yaw=%.0f view_vs_boss_yaw=%.0f control_yaw=%.1f bearing_to_boss=%.1f" %
            (S["n"], plc.game_time(world), d, arm_len, ",".join(names) or "-", caps, hidden, unread, yaw_gap, boss_off, pc.get_control_rotation().yaw, to_b))


def wait(sec):
    end = plc.game_time(actors()[0]) + sec
    while plc.game_time(actors()[0]) < end:
        yield 0.0


def drive():
    world, pc, pawn, boss = actors()
    enc = plc.component(boss, "RPGBossEncounter")
    if enc:
        enc.reset_for_test()
        yield from wait(1.0)
        enc.wake()
    log("PAWN_COMPONENTS " + ",".join(sorted(set(c.get_class().get_name() for c in pawn.get_components_by_class(unreal.ActorComponent)))))
    log("CONTROLLER " + pc.get_class().get_name())
    plc.refill_player(boss)
    plc.enter_combat(pawn)
    yield from wait(2.0)
    o = boss.get_actor_location()
    plc.place_player(pc, pawn, (o.x - 180.0, o.y, o.z + 20.0), 0.0)
    yield from wait(0.5)
    t0 = plc.game_time(actors()[0])
    next_sample, next_refill = t0, t0
    while True:
        world, pc, pawn, boss = actors()
        if not (pawn and boss):
            log("actors lost")
            return
        g = plc.game_time(world)
        if g - t0 >= 30.0:
            return
        o, p = boss.get_actor_location(), pawn.get_actor_location()
        dx, dy = o.x - p.x, o.y - p.y
        dist = math.hypot(dx, dy) or 1.0
        fx, fy = dx / dist, dy / dist
        side = 1.0 if int((g - t0) / 6.0) % 2 == 0 else -1.0
        radial = 0.8 if dist > 180.0 else (-0.8 if dist < 100.0 else 0.15)
        mv = unreal.Vector(-fy * side + fx * radial, fx * side + fy * radial, 0.0)
        if os.environ.get("CAM_MODE") == "retreat":
            # walk straight away from the boss (pawn faces away, boom points back through the boss); reset to 70 cm every 1.4 s
            if g >= S.get("next_reset", 0.0):
                S["next_reset"] = g + 1.4
                plc.place_player(pc, pawn, (o.x - fx * 70.0, o.y - fy * 70.0, p.z), math.degrees(math.atan2(-fy, -fx)))
            mv = unreal.Vector(-fx, -fy, 0.0)
        pawn.add_movement_input(mv, float(os.environ.get("CAM_SPEED", "1.0")), False)
        if os.environ.get("CAM_LOOK_TEST") and 10.0 <= g - t0 < 11.0:  # player look input for 1 s: C must stand down (IA_Look grace)
            if S.get("look_action") is None:
                S["look_action"] = unreal.load_asset("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Look")
            unreal.RPGInputTestUtils.inject_action(pc, S["look_action"], unreal.Vector(1.0, 0.0, 0.0))
            if not S.get("look_logged"):
                S["look_logged"] = True
                log("LOOK_INJECT start g=%.2f control_yaw=%.1f" % (g, pc.get_control_rotation().yaw))
        elif S.get("look_logged") and not S.get("look_end_logged"):
            S["look_end_logged"] = True
            log("LOOK_INJECT end g=%.2f control_yaw=%.1f" % (g, pc.get_control_rotation().yaw))
        mode = os.environ.get("CAM_MODE", "orbit")
        to_boss = math.degrees(math.atan2(dy, dx))
        if mode == "orbit":  # camera orbits 360 deg per 6 s
            pc.set_control_rotation(unreal.Rotator(0.0, -12.0, to_boss + (g - t0) * 60.0))
        elif mode == "away":  # player faces away from the boss: the camera arm passes through the boss (B trigger)
            pc.set_control_rotation(unreal.Rotator(0.0, -12.0, to_boss + 180.0))
        elif mode == "fixed" and not S.get("fixed_set"):  # control set once, never again (lets C engage)
            S["fixed_set"] = True
            pc.set_control_rotation(unreal.Rotator(0.0, -12.0, to_boss + 150.0))
        if g >= next_refill:
            plc.refill_player(boss)
            next_refill = g + 2.0
        if g >= next_sample:
            sample(world, pc, pawn, boss)
            next_sample = g + 0.1
        yield 0.0


def finish(reason):
    global HANDLE
    if S["done"]:
        return
    S["done"] = True
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    d = S["dist"] or [float("nan")]
    log("SUMMARY mode=%s route=%s cvars=%s finished=%s samples=%d mesh_inside=%d capsule_inside=%d arm_lt300=%d boss_mesh_hidden=%d unreadable=%d dist_min=%.0f dist_max=%.0f boss_off_last10_avg=%.0f" %
        (os.environ.get("CAM_MODE", "orbit"), ROUTE, os.environ.get("CAMERA_CVARS", ""), reason, S["n"], S["mesh_in"], S["caps_in"], S["arm_short"], S["hidden"], S["unread"], min(d), max(d), sum(S.get("boss_off",[0])[-10:]) / max(1, len(S.get("boss_off",[0])[-10:]))))
    plc.end_play()


def tick(dt):
    try:
        world = actors()[0]
        if S["gen"] is None:
            if world is None:
                if not S.get("req"):
                    S["req"] = True
                    if DATA_ROUTE:
                        unreal.SystemLibrary.execute_console_command(None, "rpg.EncounterDefinition " + DATA_ROUTE)
                    for cmd in [c.strip() for c in os.environ.get("CAMERA_CVARS", "").split(";") if c.strip()]:
                        unreal.SystemLibrary.execute_console_command(None, cmd)
                        log("CVAR " + cmd)
                    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                    S["t_req"] = time.perf_counter()
                return
            _, pc, pawn, boss = actors()
            if not (pawn and boss) or time.perf_counter() - S["t_req"] < 6.0:
                return
            S["gen"] = drive()
        next(S["gen"])
    except StopIteration:
        finish("complete")
    except Exception:
        import traceback
        log("ERROR " + traceback.format_exc())
        finish("exception")


HANDLE = unreal.register_slate_post_tick_callback(tick)
log("driver registered route=%s" % ROUTE)
