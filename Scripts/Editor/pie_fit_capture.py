"""Lead-run blind candidate fit captures. Run from the Unreal Editor Python environment.

Reads Saved/ERFit_<blind ID>.json, swaps only the live PIE player mesh, and plays
the six source and retarget sequences in single-node mode. No project asset is
saved or assigned to gameplay. Codex must not launch this PIE script.
"""

import json
import math
import os
import re
import sys
import time
import traceback
from pathlib import Path

try:
    import unreal
except ImportError:  # Offline contract tests import the pure helpers below.
    unreal = None


BLIND_IDS = {"Candidate_A", "Candidate_B", "Candidate_C"}
CLIP_IDS = {"ER-A1", "ER-A2", "ER-A3", "ER-A4", "PACK-ROLL", "PACK-BLOCK"}
DATA_DEFINITION = "/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter"
VIEWS = (("side", 90.0), ("three_quarter", 45.0))
WARMUP_FLOOR = 5.0
MAX_WARMUP_FRAMES = 20
WARMUP_BRIGHT_STREAK = 3
MAX_CAPTURE_ATTEMPTS = 10
MIN_CAPTURE_SPACING_GAME_SECONDS = 0.2
MIN_CAPTURE_SPACING_TICKS = 5
OWNED_FRAME_RE = re.compile(r"[A-Za-z0-9_-]+_(?:side|three_quarter)_\d{3}(?:_attempt_\d{2})?\.png")
LOG_PREFIX = "[FitCapture] "
STATE = {"phase": "start", "elapsed": 0.0, "generator": None, "done": False}
HANDLE = None


def validate_manifest(data, blind_id):
    """Validate the Lead-only retarget manifest without exposing its identity fields."""
    if blind_id not in BLIND_IDS:
        raise ValueError("blind id must be Candidate_A, Candidate_B, or Candidate_C")
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("unsupported ER fit manifest")
    if data.get("blind_id") != blind_id:
        raise ValueError("manifest blind id does not match -ERFitBlindId")
    mesh = data.get("target_mesh")
    source_mesh = data.get("source_mesh")
    if not valid_asset_path(mesh) or not valid_asset_path(source_mesh):
        raise ValueError("manifest mesh path is invalid")
    rows = data.get("clips")
    if not isinstance(rows, list) or len(rows) != 6:
        raise ValueError("manifest must contain exactly six clips")
    seen = set()
    normalized = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("clip row must be an object")
        clip_id = row.get("id")
        if clip_id not in CLIP_IDS or clip_id in seen:
            raise ValueError("clip ids must be the six unique fit-kit slots")
        seen.add(clip_id)
        name = row.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", name):
            raise ValueError("clip name is not safe for a capture filename")
        if not valid_asset_path(row.get("source")) or not valid_asset_path(row.get("output")):
            raise ValueError("clip animation path is invalid")
        normalized.append({"id": clip_id, "name": name,
                           "source": row["source"], "output": row["output"]})
    if seen != CLIP_IDS:
        raise ValueError("manifest clip inventory is incomplete")
    return {"blind_id": blind_id, "candidate_mesh": mesh,
            "source_mesh": source_mesh, "clips": normalized}


def valid_asset_path(value):
    return isinstance(value, str) and bool(re.fullmatch(r"/Game/[A-Za-z0-9_/-]+(?:\.[A-Za-z0-9_]+)?", value)) and ".." not in value


def command_line_blind_id(command_line):
    match = re.search(r"(?:^|\s)-ERFitBlindId=(Candidate_[ABC])(?:\s|$)", command_line)
    if not match:
        raise ValueError("pass exactly one -ERFitBlindId=Candidate_A|Candidate_B|Candidate_C")
    return match.group(1)


def capture_filename(clip_name, view, index=1):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", clip_name) or view not in {"side", "three_quarter"}:
        raise ValueError("unsafe capture identity")
    if not isinstance(index, int) or index < 1 or index > 999:
        raise ValueError("capture index must be 1..999")
    return "%s_%s_%03d.png" % (clip_name, view, index)


def update_bright_streak(streak, brightness, floor=WARMUP_FLOOR):
    return streak + 1 if brightness >= floor else 0


def capture_spacing_complete(start_game_seconds, current_game_seconds, elapsed_ticks,
                             min_game_seconds=MIN_CAPTURE_SPACING_GAME_SECONDS,
                             min_ticks=MIN_CAPTURE_SPACING_TICKS):
    return (elapsed_ticks >= min_ticks and
            current_game_seconds - start_game_seconds + 1e-6 >= min_game_seconds)


def wait_capture_spacing(world):
    """Wait for both game-time spacing and distinct PIE/editor callback ticks."""
    start_game_seconds = float(unreal.GameplayStatics.get_time_seconds(world))
    ticks = 0
    current_game_seconds = start_game_seconds
    while not capture_spacing_complete(start_game_seconds, current_game_seconds, ticks):
        yield 0.0
        ticks += 1
        current_game_seconds = float(unreal.GameplayStatics.get_time_seconds(world))
    log("capture_spacing game_seconds=%.3f ticks=%d" %
        (current_game_seconds - start_game_seconds, ticks))


def is_look_component_class(class_name):
    return isinstance(class_name, str) and class_name.startswith("RPGLook")


def preview_player_pose(boss_location, player_location, boss_yaw_degrees, distance=500.0):
    """Place player at a fixed radius from the boss, facing radially away from it."""
    dx = float(player_location.x) - float(boss_location.x)
    dy = float(player_location.y) - float(boss_location.y)
    magnitude = math.hypot(dx, dy)
    if magnitude < 1.0:
        angle = math.radians(float(boss_yaw_degrees) + 180.0)
        dx, dy = math.cos(angle), math.sin(angle)
    else:
        dx, dy = dx / magnitude, dy / magnitude
    yaw = math.degrees(math.atan2(dy, dx))
    return (float(boss_location.x) + dx * distance,
            float(boss_location.y) + dy * distance,
            float(player_location.z), yaw)


def retry_bright_capture(capture_attempt, on_retry, floor=WARMUP_FLOOR,
                         max_attempts=MAX_CAPTURE_ATTEMPTS):
    """Yield through capture attempts until bright, or fail after a bounded retry budget."""
    for attempt in range(1, max_attempts + 1):
        brightness = yield from capture_attempt(attempt)
        if brightness >= floor:
            return attempt, brightness
        on_retry(attempt, brightness)
    raise RuntimeError("capture remained below brightness floor after %d attempts" % max_attempts)


def clear_owned_frames(target):
    """Clear only our own numbered PNG frames; leave unrelated user files untouched."""
    target.mkdir(parents=True, exist_ok=True)
    existing = list(target.iterdir())
    unexpected = [item.name for item in existing
                  if not item.is_file() or not OWNED_FRAME_RE.fullmatch(item.name)]
    if unexpected:
        raise RuntimeError("refusing to clear non-driver content in fit output folder: %s" %
                           ", ".join(unexpected))
    for item in existing:
        item.unlink()
    return len(existing)


def log(message):
    unreal.log(LOG_PREFIX + str(message))


def camera_diagnostics(pc, pawn):
    manager = getattr(pc, "player_camera_manager", None) if pc else None
    player_location = None
    camera_location = None
    try:
        player_location = pawn.get_actor_location() if pawn else None
        player_text = "(%.1f,%.1f,%.1f)" % (player_location.x, player_location.y, player_location.z)
    except Exception:
        player_text = "UNKNOWN"
    try:
        camera_location = manager.get_camera_location() if manager else None
        camera_text = "(%.1f,%.1f,%.1f)" % (camera_location.x, camera_location.y, camera_location.z)
    except Exception:
        camera_text = "UNKNOWN"
    fade_values = {}
    if manager:
        for output, candidates in (("fade_enabled", ("b_enable_fading", "enable_fading")),
                                   ("fade_amount", ("fade_alpha", "fade_amount")),
                                   ("fade_time_remaining", ("fade_time_remaining",))):
            fade_values[output] = "UNAVAILABLE"
            for field in candidates:
                try:
                    fade_values[output] = str(manager.get_editor_property(field))
                    break
                except Exception:
                    pass
    trace_name = "UNAVAILABLE"
    if manager and player_location and camera_location:
        try:
            result = unreal.SystemLibrary.line_trace_single(
                pawn.get_world(), camera_location, player_location,
                unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [pawn],
                unreal.DrawDebugTrace.NONE, True)
            if isinstance(result, tuple):
                result = result[-1]
            blocked = bool(result.get_editor_property("blocking_hit"))
            actor = result.get_editor_property("actor") if blocked else None
            trace_name = actor.get_name() if actor else ("HIT_NO_ACTOR" if blocked else "CLEAR")
        except Exception:
            trace_name = "UNAVAILABLE"
    return "player=%s camera=%s camera_player_trace=%s fade_enabled=%s fade_amount=%s fade_time_remaining=%s" % (
        player_text, camera_text, trace_name,
        fade_values.get("fade_enabled", "UNAVAILABLE"), fade_values.get("fade_amount", "UNAVAILABLE"),
        fade_values.get("fade_time_remaining", "UNAVAILABLE"))


def actors():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = None
    if world:
        boss = next((actor for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
                     if actor.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None)
    return world, pc, pawn, boss


def manifest_data(blind_id):
    path = Path(unreal.Paths.project_saved_dir()) / ("ERFit_%s.json" % blind_id)
    with path.open("r", encoding="utf-8") as stream:
        data = json.load(stream)
    return validate_manifest(data, blind_id)


def mesh_component(pawn):
    components = pawn.get_components_by_class(unreal.SkeletalMeshComponent)
    component = next((item for item in components if item.get_name() == "Mesh"), None)
    if component is None and len(components) == 1:
        component = components[0]
    if component is None:
        raise RuntimeError("could not uniquely identify player skeletal mesh component")
    return component


def set_mesh(mesh_component_, mesh_asset):
    if not mesh_asset:
        raise RuntimeError("fit manifest references a missing mesh")
    mesh_component_.set_skeletal_mesh_asset(mesh_asset)
    mesh_component_.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)


def screenshot(world, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RuntimeError("refusing to overwrite an existing fit capture: %s" % path)
    command = "HighResShot 960x540 filename=%s" % path.resolve().as_posix()
    log("request resolution=960x540 file=%s" % path.name)
    unreal.SystemLibrary.execute_console_command(world, command)


def wait_png(path, timeout=20.0):
    deadline = time.perf_counter() + timeout
    prior_size = None
    stable = 0
    while time.perf_counter() < deadline:
        if path.is_file():
            size = path.stat().st_size
            stable = stable + 1 if size > 33 and size == prior_size else 0
            prior_size = size
            if stable >= 2:
                sys.path.insert(0, str(Path(unreal.Paths.project_dir()) / "Scripts" / "Editor"))
                from aura_png_metrics import mean_gray
                return mean_gray(path)
        yield 0.0
    raise RuntimeError("HighResShot timed out or did not produce a stable PNG")


def aim_view(pc, pawn, offset):
    actor_yaw = float(pawn.get_actor_rotation().yaw)
    pc.set_control_rotation(unreal.Rotator(roll=0.0, pitch=-3.0, yaw=actor_yaw + offset))


def capture_frame_with_retries(world, final_path, clip_name, view_name, index):
    attempt_paths = {}

    def attempt_capture(attempt):
        temp_path = final_path.with_name("%s_%s_%03d_attempt_%02d.png" %
                                         (clip_name, view_name, index, attempt))
        attempt_paths[attempt] = temp_path
        screenshot(world, temp_path)
        brightness = yield from wait_png(temp_path)
        yield from wait_capture_spacing(world)
        return brightness

    def on_retry(attempt, brightness):
        temp_path = attempt_paths[attempt]
        log("capture_retry clip=%s view=%s index=%03d attempt=%d/%d mean_gray=%.3f floor=%.1f" %
            (clip_name, view_name, index, attempt, MAX_CAPTURE_ATTEMPTS, brightness, WARMUP_FLOOR))
        try:
            temp_path.unlink(missing_ok=True)
        except OSError as exc:
            raise RuntimeError("could not discard dark retry frame: " + str(exc))

    attempt, brightness = yield from retry_bright_capture(
        attempt_capture, on_retry, max_attempts=MAX_CAPTURE_ATTEMPTS)
    temp_path = attempt_paths[attempt]
    if final_path.exists():
        raise RuntimeError("refusing to overwrite existing fit capture: %s" % final_path)
    temp_path.replace(final_path)
    return attempt, brightness


def capture_sequence(world, pc, pawn, mesh, asset_path, clip_name, view_name, view_yaw, out_dir, warmup_dir):
    sequence = unreal.load_asset(asset_path)
    if not sequence:
        raise RuntimeError("fit manifest animation could not be loaded")
    aim_view(pc, pawn, view_yaw)
    mesh.play_animation(sequence, False)
    mesh.set_position(0.0, False)
    mesh.set_play_rate(0.0)
    # Let the first-use render resources settle. Warmup images stay under Saved, not in AG's evidence folder.
    brightness = None
    bright_streak = 0
    for warm_index in range(1, MAX_WARMUP_FRAMES + 1):
        warm = warmup_dir / ("%s_%s_warmup_%03d.png" % (clip_name, view_name, warm_index))
        screenshot(world, warm)
        brightness = yield from wait_png(warm)
        yield from wait_capture_spacing(world)
        log("warmup clip=%s view=%s frame=%d mean_gray=%.3f floor=%.1f" %
            (clip_name, view_name, warm_index, brightness, WARMUP_FLOOR))
        log("warmup_state clip=%s view=%s frame=%d %s" %
            (clip_name, view_name, warm_index, camera_diagnostics(pc, pawn)))
        bright_streak = update_bright_streak(bright_streak, brightness)
        log("warmup_streak clip=%s view=%s current=%d required=%d" %
            (clip_name, view_name, bright_streak, WARMUP_BRIGHT_STREAK))
        if bright_streak >= WARMUP_BRIGHT_STREAK:
            break
        if warm_index < MAX_WARMUP_FRAMES:
            yield 0.0
    if brightness is None or bright_streak < WARMUP_BRIGHT_STREAK:
        raise RuntimeError("warmup did not reach %d consecutive bright frames" % WARMUP_BRIGHT_STREAK)
    duration = max(0.0, float(sequence.get_play_length()))
    sample_times = [min(duration, duration * fraction) for fraction in (0.0, 0.25, 0.5, 0.75, 0.99)]
    for index, sample_time in enumerate(sample_times, start=1):
        mesh.set_position(sample_time, False)
        final_path = out_dir / capture_filename(clip_name, view_name, index)
        attempts, final_brightness = yield from capture_frame_with_retries(
            world, final_path, clip_name, view_name, index)
        log("frame clip=%s view=%s index=%03d time=%.3f/%.3f mean_gray=%.3f attempts=%d file=%s" %
            (clip_name, view_name, index, sample_time, duration, final_brightness, attempts, final_path.name))


def run_capture():
    command_line = unreal.SystemLibrary.get_command_line()
    blind_id = command_line_blind_id(command_line)
    manifest = manifest_data(blind_id)
    route_value = os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()
    if route_value and route_value != DATA_DEFINITION:
        raise RuntimeError("fit captures require the G044 DATA route")
    if not route_value:
        raise RuntimeError("fit captures require H019_ENCOUNTER_DEFINITION for the DATA route")
    output_root = Path("D:/FightVideo/fit_test")
    # Give each blind run its own matching baseline folder so three sequential
    # candidate captures never overwrite the shared Candidate_0 evidence.
    targets = [output_root / "Candidate_0" / blind_id, output_root / blind_id]
    for target in targets:
        cleared = clear_owned_frames(target)
        if cleared:
            log("cleared_driver_frames dir=%s count=%d" % (target.as_posix(), cleared))

    world, pc, pawn, boss = actors()
    if not all((world, pc, pawn, boss)):
        raise RuntimeError("PIE world/player/boss is not ready")
    encounter = next((component for component in boss.get_components_by_class(unreal.ActorComponent)
                      if component.get_class().get_name() == "RPGBossEncounter"), None)
    if encounter is None:
        raise RuntimeError("boss encounter component is missing")
    encounter.hold_for_test(True)
    # Keep the held boss in-world; hiding it avoids world-bounds and encounter teardown effects.
    boss.set_actor_hidden_in_game(True)
    hidden_look_components = 0
    for component in boss.get_components_by_class(unreal.ActorComponent):
        class_name = component.get_class().get_name()
        if is_look_component_class(class_name):
            if hasattr(component, "set_visibility"):
                component.set_visibility(False, True)
                hidden_look_components += 1
            elif hasattr(component, "set_hidden_in_game"):
                component.set_hidden_in_game(True)
                hidden_look_components += 1
    log("boss_held_hidden look_components_hidden=%d" % hidden_look_components)

    # Keep player and camera inside the arena footprint near the hidden boss.
    boss_location = boss.get_actor_location()
    old_player_location = pawn.get_actor_location()
    preview_x, preview_y, preview_z, preview_yaw = preview_player_pose(
        boss_location, old_player_location, boss.get_actor_rotation().yaw)
    pawn.set_actor_location_and_rotation(unreal.Vector(preview_x, preview_y, preview_z),
                                         unreal.Rotator(roll=0.0, pitch=0.0, yaw=preview_yaw),
                                         False, True)
    pc.set_control_rotation(unreal.Rotator(roll=0.0, pitch=-3.0, yaw=preview_yaw))
    log("preview_player distance_from_boss_cm=%.1f camera_yaw_base=%.1f location=(%.1f,%.1f,%.1f)" %
        (math.hypot(preview_x - boss_location.x, preview_y - boss_location.y),
         preview_yaw, preview_x, preview_y, preview_z))
    mesh = mesh_component(pawn)
    candidate_mesh = unreal.load_asset(manifest["candidate_mesh"])
    mannequin_mesh = unreal.load_asset(manifest["source_mesh"])
    if not candidate_mesh or not mannequin_mesh:
        raise RuntimeError("manifest mesh asset failed to load")
    run_stamp = time.strftime("%Y%m%dT%H%M%S", time.gmtime()) + "_%03d" % (int(time.time() * 1000) % 1000)
    project_saved = (Path(unreal.Paths.project_saved_dir()) / "ERFitCaptureWarmup" /
                     blind_id / run_stamp)
    unreal.SystemLibrary.execute_console_command(world, "slomo 0.5")
    log("started blind_id=%s clips=6 views=2 baseline=Candidate_0 route=DATA" % blind_id)
    try:
        for label, body, row_key, out_dir in (
                ("Candidate_0", mannequin_mesh, "source", targets[0]),
                (blind_id, candidate_mesh, "output", targets[1])):
            set_mesh(mesh, body)
            for row in manifest["clips"]:
                for view_name, view_yaw in VIEWS:
                    yield from capture_sequence(world, pc, pawn, mesh, row[row_key], row["name"],
                                                view_name, view_yaw, out_dir,
                                                project_saved / label / row["id"])
        log("finished: blind_id=%s baseline=Candidate_0 clips=6 views=2" % blind_id)
    finally:
        unreal.SystemLibrary.execute_console_command(world, "slomo 1.0")
        mesh.set_play_rate(1.0)


def tick(delta_seconds):
    global HANDLE
    if STATE["done"]:
        return
    try:
        if STATE["generator"] is None:
            world, _, _, _ = actors()
            if world is None:
                return
            STATE["generator"] = run_capture()
        next(STATE["generator"])
    except StopIteration:
        STATE["done"] = True
        if HANDLE is not None:
            unreal.unregister_slate_post_tick_callback(HANDLE)
            HANDLE = None
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception:
        STATE["done"] = True
        log("ERROR " + traceback.format_exc())
        log("finished: FAILED")
        try:
            world, _, _, _ = actors()
            if world:
                unreal.SystemLibrary.execute_console_command(world, "slomo 1.0")
        finally:
            if HANDLE is not None:
                unreal.unregister_slate_post_tick_callback(HANDLE)
                HANDLE = None
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def start():
    global HANDLE
    if unreal is None:
        raise RuntimeError("run this capture script inside the Unreal Editor Python environment")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
    HANDLE = unreal.register_slate_post_tick_callback(tick)


if __name__ == "__main__":
    start()
