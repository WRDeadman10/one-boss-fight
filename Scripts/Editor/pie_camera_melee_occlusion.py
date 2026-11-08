"""Lead-only PIE camera trace at 105/200/300 cm from the live boss.

Read-only camera/collision measurement; no component collision is changed.
Run under ENGINE_LOCK with -nosound. Marker: [MeleeCamera] finished:.
"""
import math
import sys
from pathlib import Path

import unreal

sys.path.insert(0, str(Path(unreal.Paths.project_dir()) / "Scripts" / "Editor"))
import pie_lead_common as plc

PREFIX = "[MeleeCamera] "
DISTANCES = (105.0, 200.0, 300.0)
S = {"phase": "start", "elapsed": 0.0, "index": 0, "wait": 0.0, "done": False}
HANDLE = None


def log(message):
    unreal.log(PREFIX + str(message))


def horizontal_distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def actors():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    return world, pc, pawn, plc.boss_actor(world)


def place(pc, pawn, boss, distance):
    origin = boss.get_actor_location()
    yaw = math.radians(boss.get_actor_rotation().yaw)
    x = origin.x + math.cos(yaw) * distance
    y = origin.y + math.sin(yaw) * distance
    facing = math.degrees(math.atan2(origin.y - y, origin.x - x))
    plc.place_player(pc, pawn, (x, y, origin.z + 20.0), facing)


def prop(item, name):
    try:
        return item.get_editor_property(name)
    except Exception as exc:
        return "UNREADABLE(%s)" % exc


def snapshot(world, pc, pawn, boss, requested):
    arms = pawn.get_components_by_class(unreal.SpringArmComponent)
    cameras = pawn.get_components_by_class(unreal.CameraComponent)
    capsules = boss.get_components_by_class(unreal.CapsuleComponent)
    if not arms or not cameras:
        raise RuntimeError("player spring arm/camera missing")
    arm = next((item for item in arms if item.get_name() == "CameraBoom"), arms[0])
    camera = next((item for item in cameras if item.get_name() == "FollowCamera"), cameras[0])
    pivot = arm.get_world_location()
    eye = camera.get_world_location()
    actual = horizontal_distance(pawn.get_actor_location(), boss.get_actor_location())
    log("SAMPLE requested_cm=%.1f actual_cm=%.1f target_arm=%s probe_size=%s probe_channel=%s pivot=%s camera=%s pivot_camera_cm=%.1f" %
        (requested, actual, prop(arm, "target_arm_length"), prop(arm, "probe_size"),
         prop(arm, "probe_channel"), pivot, eye, (eye - pivot).length()))
    for capsule in capsules:
        try:
            response = capsule.get_collision_response_to_channel(unreal.CollisionChannel.ECC_CAMERA)
        except Exception as exc:
            response = "UNREADABLE(%s)" % exc
        log("BOSS_CAPSULE name=%s collision_enabled=%s camera_response=%s" %
            (capsule.get_name(), prop(capsule, "collision_enabled"), response))
    try:
        # The unfixed-arm getter is not exposed in this UE Python build. This
        # estimate omits socket/target offsets, so label it approximate.
        yaw = math.radians(pc.get_control_rotation().yaw)
        forward = unreal.Vector(math.cos(yaw), math.sin(yaw), 0.0)
        unfixed = pivot - forward * float(prop(arm, "target_arm_length"))
        desired_kind = "approximate_no_offsets"
        hit = unreal.SystemLibrary.sphere_trace_single(
            world, pivot, unfixed, float(prop(arm, "probe_size")),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY2, False, [pawn],
            unreal.DrawDebugTrace.NONE, True)
        log("PROBE desired_kind=%s desired=%s sphere_trace=%s" % (desired_kind, unfixed, hit))
    except Exception as exc:
        log("PROBE UNREADABLE %s" % exc)
    try:
        manager = pc.player_camera_manager
        log("CAMERA_MANAGER eye=%s rotation=%s" %
            (manager.get_camera_location(), manager.get_camera_rotation()))
    except Exception as exc:
        log("CAMERA_MANAGER UNREADABLE %s" % exc)


def finish(reason):
    global HANDLE
    if S["done"]:
        return
    S["done"] = True
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    log("finished: " + reason)
    plc.end_play()


def tick(dt):
    try:
        S["elapsed"] += dt
        if S["phase"] == "start":
            if S["elapsed"] > 0.5:
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                S.update(phase="wait", elapsed=0.0)
            return
        world, pc, pawn, boss = actors()
        if S["phase"] == "wait":
            if all((world, pc, pawn, boss)) and S["elapsed"] > 6.0:
                S.update(phase="measure", elapsed=0.0, wait=0.0)
            elif S["elapsed"] > 25.0:
                finish("actors missing")
            return
        if S["elapsed"] > 30.0:
            finish("timeout")
            return
        if S["index"] >= len(DISTANCES):
            finish("three distances sampled")
            return
        distance = DISTANCES[S["index"]]
        if S["wait"] == 0.0:
            place(pc, pawn, boss, distance)
            S["wait"] = S["elapsed"] + 0.75
            return
        if S["elapsed"] >= S["wait"]:
            snapshot(world, pc, pawn, boss, distance)
            S["index"] += 1
            S["wait"] = 0.0
    except Exception:
        import traceback
        log("ERROR " + traceback.format_exc())
        finish("exception")


HANDLE = unreal.register_slate_post_tick_callback(tick)
