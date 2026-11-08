# Lead copy of Scripts/Editor/probe_camera_inside_boss.py + CAMERA_CVARS env (C-1079).
"""Lead-only dynamic melee camera telemetry; does not alter camera/collision.

Run in L_SevarogArena under ENGINE_LOCK. After the Lead starts PIE, the probe
waits for player/boss, then passively samples their live engagement. It does
not move actors, change collision, or choose a camera fix. Markers:
[CameraInsideBoss] SAMPLE and finished.
"""
import math
import os
import sys
from pathlib import Path

import unreal

sys.path.insert(0, str(Path(unreal.Paths.project_dir()) / "Scripts" / "Editor"))
import pie_lead_common as plc

LOG = "[CameraInsideBoss] "
PREFIX = LOG
DATA_ROUTE = os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()
EXPECTED_DATA = "/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter"
if DATA_ROUTE and DATA_ROUTE != EXPECTED_DATA:
    raise RuntimeError("H019_ENCOUNTER_DEFINITION must be unset or the selected G044 encounter")
ROUTE = "data" if DATA_ROUTE else "legacy"
S = {"phase": "start", "elapsed": 0.0, "samples": 0, "done": False}
HANDLE = None


def finite_vector(value):
    try:
        return all(math.isfinite(float(getattr(value, key))) for key in ("x", "y", "z"))
    except Exception:
        return False


def point_in_aabb(point, center, extent):
    if not all(finite_vector(v) for v in (point, center, extent)):
        return None
    return all(abs(float(getattr(point, axis)) - float(getattr(center, axis))) <=
               abs(float(getattr(extent, axis))) for axis in ("x", "y", "z"))


def log(message):
    unreal.log(PREFIX + str(message))


def prop(item, name):
    try:
        return item.get_editor_property(name)
    except Exception as exc:
        return "UNREADABLE(%s)" % exc


def actor_context():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    return world, pc, pawn, plc.boss_actor(world)


def component_bounds(component):
    try:
        bounds = component.get_bounds()
        origin = getattr(bounds, "origin", None)
        extent = getattr(bounds, "box_extent", None)
        if origin is None or extent is None:
            return None
        return origin, extent
    except Exception:
        return None


def visible_components(boss):
    found = []
    for cls in (unreal.SkeletalMeshComponent, unreal.StaticMeshComponent):
        for component in boss.get_components_by_class(cls):
            try:
                if component.is_visible() and not component.get_editor_property("hidden_in_game"):
                    found.append(component)
            except Exception:
                found.append(component)
    return found


def camera_inside(camera_position, boss):
    unreadable = []
    for component in visible_components(boss):
        bounds = component_bounds(component)
        if bounds is None:
            unreadable.append(component.get_name())
            continue
        inside = point_in_aabb(camera_position, bounds[0], bounds[1])
        if inside:
            return True, component.get_name(), unreadable
    if unreadable:
        return None, "none", unreadable
    return False, "none", unreadable


def sample(world, pc, pawn, boss):
    arms = pawn.get_components_by_class(unreal.SpringArmComponent)
    cameras = pawn.get_components_by_class(unreal.CameraComponent)
    capsules = boss.get_components_by_class(unreal.CapsuleComponent)
    if not arms or not cameras:
        raise RuntimeError("player spring arm/camera missing")
    arm = next((item for item in arms if item.get_name() == "CameraBoom"), arms[0])
    camera = next((item for item in cameras if item.get_name() == "FollowCamera"), cameras[0])
    pivot, eye = arm.get_world_location(), camera.get_world_location()
    inside, component_name, unreadable = camera_inside(eye, boss)
    try:
        actual_arm = float(prop(arm, "target_arm_length"))
    except (TypeError, ValueError):
        actual_arm = float("nan")
    try:
        current_length = (eye - pivot).length()
    except Exception:
        current_length = float("nan")
    try:
        boss_distance = (pawn.get_actor_location() - boss.get_actor_location()).length()
    except Exception:
        boss_distance = float("nan")
    responses = []
    for capsule in capsules:
        try:
            response = capsule.get_collision_response_to_channel(unreal.CollisionChannel.ECC_CAMERA)
        except Exception as exc:
            response = "UNREADABLE(%s)" % exc
        responses.append("%s:%s" % (capsule.get_name(), response))
    # The unfixed arm target omits socket/target offsets in this UE Python API.
    # Keep the trace explicitly estimated and record its hit component only as
    # a companion to the actual camera position and reported spring-arm length.
    sweep_component = "UNREADABLE"
    try:
        yaw = math.radians(pc.get_control_rotation().yaw)
        forward = unreal.Vector(math.cos(yaw), math.sin(yaw), 0.0)
        desired = pivot - forward * actual_arm
        result = unreal.SystemLibrary.sphere_trace_single(
            world, pivot, desired, float(prop(arm, "probe_size")),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY2, False, [pawn],
            unreal.DrawDebugTrace.NONE, True)
        hit = result[-1] if isinstance(result, tuple) else result
        try:
            component = hit.get_editor_property("component")
            sweep_component = component.get_name() if component else "none"
        except Exception:
            sweep_component = "UNREADABLE_HIT_RESULT"
    except Exception as exc:
        sweep_component = "UNREADABLE(%s)" % exc
    log("SAMPLE t=%.3f player_boss_cm=%.1f player=%s boss=%s camera=%s pivot=%s "
        "arm_target_cm=%s arm_actual_cm=%.1f approximate_sweep_hit_component=%s "
        "camera_inside_mesh_aabb=%s inside_component=%s capsule_camera_response=%s unreadable_bounds=%s" %
        (plc.game_time(world), boss_distance,
         pawn.get_actor_location(), boss.get_actor_location(), eye, pivot,
         prop(arm, "target_arm_length"), current_length, sweep_component, inside, component_name,
         ";".join(responses) or "none", ",".join(unreadable) or "none"))


def finish(reason):
    global HANDLE
    if S["done"]:
        return
    S["done"] = True
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    log("SUMMARY route=%s finished=%s samples=%d" % (ROUTE, reason, S["samples"]))
    plc.end_play(unreal)


def tick(dt):
    try:
        S["elapsed"] += dt
        if S["phase"] == "start":
            if S["elapsed"] > 0.5:
                if DATA_ROUTE:
                    unreal.SystemLibrary.execute_console_command(None, "rpg.EncounterDefinition " + DATA_ROUTE)
                cv = os.environ.get("CAMERA_CVARS", "").strip()
                for cmd in [c for c in cv.split(";") if c.strip()]:
                    unreal.SystemLibrary.execute_console_command(None, cmd.strip())
                    log("CVAR " + cmd.strip())
                log("ROUTE route=%s selection=%s circle_range_cm=150..250 passive=true" %
                    (ROUTE, DATA_ROUTE or "unset (legacy startup)"))
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                S.update(phase="wait", elapsed=0.0)
            return
        world, pc, pawn, boss = actor_context()
        if S["phase"] == "wait":
            if all((world, pc, pawn, boss)) and S["elapsed"] >= 6.0:
                plc.enter_combat(pawn, unreal)
                S.update(phase="sample", elapsed=0.0)
            elif S["elapsed"] >= 25.0:
                finish("actors missing")
            return
        if S["elapsed"] >= 30.0:
            finish("bounded observation complete")
            return
        if S["elapsed"] >= S["samples"] * 0.10:
            sample(world, pc, pawn, boss)
            S["samples"] += 1
    except Exception:
        import traceback
        log("ERROR " + traceback.format_exc())
        finish("exception")


HANDLE = unreal.register_slate_post_tick_callback(tick)
