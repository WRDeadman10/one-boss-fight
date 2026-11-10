"""Capture side-view stills while stepping Sevarog-owned sequences in PIE.

This is a read-only visual probe. It holds/hides the arena boss, temporarily
uses the Sevarog mesh on the player pawn, saves no assets, restores that mesh,
and ends PIE. Run only when the Lead has handed over the Editor.
Log prefix [SevarogFrames]; stop marker "[SevarogFrames] finished:".
"""
import os
import sys
import time
import traceback
import uuid
from pathlib import Path

import unreal

sys.path.insert(0, str(Path(unreal.Paths.project_dir()) / "Scripts" / "Editor"))
import pie_lead_common as plc
from sevarog_clip_frame_rules import sample_times


LOG = "[SevarogFrames] "
FRAME_RATE = 15.0
BRIGHT_BYTES = 300000  # same threshold as C-1225 FitLead
SHOT_WIDTH = 960
SHOT_HEIGHT = 540
OUT_ROOT = "D:/FightVideo/sevarog_frames"
MESH_ASSET_PATH = "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog"
MESH_DISK_RELATIVE = os.path.join(
    "Content", "ParagonSevarog", "Characters", "Heroes", "Sevarog", "Meshes", "Sevarog.uasset"
)
ANIM_ROOT = "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/"
CLIPS = (
    "Swing1_Medium",
    "Swing2_Medium",
    "Swing3_Slow",
    "Swing1_FAST_v2",
    "Speedburst",
    "Ultimate_Swing_120fps",
    "Subjugation",
    "Soul_Siphon",
)

STATE = {
    "world_requested": False,
    "started_at": 0.0,
    "generator": None,
    "done": False,
    "shots": 0,
    "reason": "not_started",
    "mesh": None,
    "original_mesh": None,
    "original_mode": None,
}
HANDLE = None


def log(message):
    unreal.log(LOG + str(message))


def actors():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = plc.boss_actor(world) if world else None
    return world, pc, pawn, boss


def wait_game_seconds(seconds):
    world = actors()[0]
    if not world:
        raise RuntimeError("PIE world disappeared during capture")
    end_at = plc.game_time(world) + float(seconds)
    while plc.game_time(actors()[0]) < end_at:
        yield 0.0


def shot(path):
    world = actors()[0]
    if not world:
        raise RuntimeError("PIE world disappeared before HighResShot")
    unreal.SystemLibrary.execute_console_command(
        world,
        "HighResShot %dx%d filename=%s" % (SHOT_WIDTH, SHOT_HEIGHT, path),
    )
    deadline = time.perf_counter() + 15.0
    while not os.path.exists(path) and time.perf_counter() < deadline:
        yield 0.0
    # Match the Lead capture driver's post-shot spacing so the PNG finishes writing.
    yield from wait_game_seconds(0.1)
    return os.path.getsize(path) if os.path.exists(path) else 0


def warm(out_dir, clip_name):
    """Require two consecutive bright side-view frames before measured frames."""
    warm_dir = os.path.join(OUT_ROOT, "_warm")
    os.makedirs(warm_dir, exist_ok=True)
    run_id = uuid.uuid4().hex
    streak = 0
    for index in range(40):
        path = os.path.join(warm_dir, "_warm_%s_%s_%02d.png" % (clip_name, run_id, index))
        if os.path.exists(path):
            raise RuntimeError("refusing to overwrite warm-up frame: %s" % path)
        size = yield from shot(path)
        streak = streak + 1 if size > BRIGHT_BYTES else 0
        # This path is unique to this invocation and was checked absent before capture.
        if os.path.exists(path):
            os.remove(path)
        if streak >= 2:
            log("WARM_OK clip=%s attempts=%d" % (clip_name, index + 1))
            return True
        yield from wait_game_seconds(0.15)
    log("WARM_FAIL clip=%s" % clip_name)
    return False


def capture_clip(mesh, sequence, clip_name, duration):
    out_dir = os.path.join(OUT_ROOT, clip_name)
    os.makedirs(out_dir, exist_ok=True)
    times = sample_times(duration, FRAME_RATE)
    targets = [os.path.join(out_dir, "%s_%03d_%.3f.png" % (clip_name, index, t))
               for index, t in enumerate(times)]
    collisions = [path for path in targets if os.path.exists(path)]
    if collisions:
        raise RuntimeError("refusing to overwrite existing frame: %s" % collisions[0])

    mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    mesh.play_animation(sequence, False)
    mesh.set_play_rate(0.0)
    mesh.set_position(0.0, False)
    yield from wait_game_seconds(0.2)
    if not (yield from warm(out_dir, clip_name)):
        raise RuntimeError("side-view warm-up did not produce two bright frames for %s" % clip_name)

    for index, (t, path) in enumerate(zip(times, targets)):
        mesh.set_position(float(t), False)
        mesh.set_play_rate(0.0)
        # C-1243 Lead fix: SkeletalMeshComponent.tick_animation/refresh_bone_transforms are not exposed to UE 5.5 Python.
        # The proven pie_fit_lead.py pattern is set_position then a short game-time wait so the pose renders.
        yield from wait_game_seconds(0.15)
        size = 0
        for attempt in range(8):
            size = yield from shot(path)
            if size > BRIGHT_BYTES:
                break
            if os.path.exists(path):
                # Measured targets were absent in the preflight and are owned by this run.
                os.remove(path)
            yield from wait_game_seconds(0.2)
        bright = size > BRIGHT_BYTES
        log("FRAME clip=%s index=%03d time=%.3f bytes=%d bright=%d" %
            (clip_name, index, t, size, int(bright)))
        if not bright:
            raise RuntimeError("frame stayed dark after 8 captures: %s" % path)
        STATE["shots"] += 1


def restore_player_mesh():
    mesh = STATE.get("mesh")
    original_mesh = STATE.get("original_mesh")
    if mesh is None or original_mesh is None:
        return
    try:
        mesh.set_skeletal_mesh_asset(original_mesh)
        original_mode = STATE.get("original_mode")
        if original_mode is not None:
            mesh.set_animation_mode(original_mode)
        log("PLAYER_MESH_RESTORED asset=%s" % original_mesh.get_name())
    except Exception:
        log("RESTORE_ERROR " + traceback.format_exc())
    finally:
        STATE["mesh"] = None
        STATE["original_mesh"] = None
        STATE["original_mode"] = None


def witness(pawn, boss):
    try:
        encounter = plc.component(boss, "RPGBossEncounter")
        if encounter is None:
            raise RuntimeError("RPGBossEncounter component missing on arena boss")
        encounter.hold_for_test(True)
        boss.set_actor_hidden_in_game(True)

        mesh = next((component for component in pawn.get_components_by_class(unreal.SkeletalMeshComponent)
                     if component.get_name() == "CharacterMesh0"), None)
        if mesh is None:
            raise RuntimeError("player CharacterMesh0 component not found")
        original_mesh = mesh.get_editor_property("skeletal_mesh")
        if original_mesh is None:
            raise RuntimeError("player CharacterMesh0 has no mesh to restore")
        STATE["mesh"] = mesh
        STATE["original_mesh"] = original_mesh
        STATE["original_mode"] = mesh.get_editor_property("animation_mode")

        project_dir = unreal.Paths.project_dir()
        mesh_disk_path = os.path.join(project_dir, MESH_DISK_RELATIVE)
        if not os.path.isfile(mesh_disk_path):
            raise RuntimeError("Sevarog mesh file missing on disk: %s" % mesh_disk_path)
        sevarog_mesh = unreal.load_asset(MESH_ASSET_PATH)
        if sevarog_mesh is None:
            raise RuntimeError("Sevarog mesh asset failed to load: %s" % MESH_ASSET_PATH)
        mesh.set_skeletal_mesh_asset(sevarog_mesh)
        mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)

        clips = []
        for clip_name in CLIPS:
            disk_path = os.path.join(project_dir, "Content", "ParagonSevarog", "Characters", "Heroes",
                                     "Sevarog", "Animations", clip_name + ".uasset")
            asset_path = ANIM_ROOT + clip_name
            if not os.path.isfile(disk_path):
                raise RuntimeError("clip file missing on disk: %s" % disk_path)
            sequence = unreal.load_asset(asset_path)
            if sequence is None:
                raise RuntimeError("clip asset failed to load: %s" % asset_path)
            duration = float(sequence.get_play_length())
            if duration <= 0.0:
                raise RuntimeError("clip has non-positive duration: %s" % asset_path)
            clips.append((clip_name, sequence, duration))

        # Preflight all measured output paths before taking the first frame.
        for clip_name, _, duration in clips:
            out_dir = os.path.join(OUT_ROOT, clip_name)
            times = sample_times(duration, FRAME_RATE)
            for index, t in enumerate(times):
                path = os.path.join(out_dir, "%s_%03d_%.3f.png" % (clip_name, index, t))
                if os.path.exists(path):
                    raise RuntimeError("refusing to overwrite existing frame: %s" % path)

        yaw = pawn.get_actor_rotation().yaw + 90.0
        pc = unreal.GameplayStatics.get_player_controller(actors()[0], 0)
        if pc is None:
            raise RuntimeError("player controller disappeared")
        pc.set_control_rotation(unreal.Rotator(roll=0.0, pitch=-5.0, yaw=yaw))
        yield from wait_game_seconds(0.5)

        log("START mesh=%s clips=%d fps=15 view=side" % (sevarog_mesh.get_name(), len(clips)))
        for clip_name, sequence, duration in clips:
            yield from capture_clip(mesh, sequence, clip_name, duration)
        STATE["reason"] = "complete"
    finally:
        restore_player_mesh()


def finish(reason):
    global HANDLE
    if STATE["done"]:
        return
    STATE["done"] = True
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    if reason != "complete":
        STATE["reason"] = reason
    restore_player_mesh()
    log("finished: %s shots=%d" % (STATE["reason"], STATE["shots"]))
    plc.end_play()


def tick(delta_seconds):
    try:
        if not STATE["started_at"]:
            STATE["started_at"] = time.perf_counter()
        world, _, pawn, boss = actors()
        if world is None:
            if not STATE["world_requested"]:
                STATE["world_requested"] = True
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                STATE["started_at"] = time.perf_counter()
            elif time.perf_counter() - STATE["started_at"] > 30.0:
                finish("failed: PIE world did not start")
            return
        if pawn is None or boss is None:
            if STATE["started_at"] and time.perf_counter() - STATE["started_at"] > 30.0:
                finish("failed: player pawn or arena boss not found")
            return
        if STATE["generator"] is None:
            STATE["generator"] = witness(pawn, boss)
        next(STATE["generator"])
    except StopIteration:
        finish("complete")
    except Exception:
        log("ERROR " + traceback.format_exc())
        finish("failed: exception")


HANDLE = unreal.register_slate_post_tick_callback(tick)
log("driver registered; waiting for PIE")
