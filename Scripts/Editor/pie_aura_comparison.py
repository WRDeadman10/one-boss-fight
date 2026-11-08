"""Lead-only fixed-state capture comparing the approved and boost aura systems.

Run on both routes through RunLeadPie.ps1 after Antigravity has authored the
separate candidate. Transient PIE component swap only; never saves an asset.
Capture pacing and serialized 960x540 HighResShot requests follow
P_SHOWCASE/pie_showcase.py:capture. Codex must not run this Editor script.
"""
import os
import math
import json
import hashlib
import re
import sys
import time
import zlib
from datetime import datetime
from pathlib import Path

import unreal

sys.path.insert(0, str(Path(unreal.Paths.project_dir()) / "Scripts" / "Editor"))
import pie_lead_common as plc
from aura_png_metrics import mean_gray

LOG = "[AuraCompare] "
APPROVED_PATH = "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura.NS_Boss_PhaseTwoAura"
CANDIDATE_PATH = "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_Boost.NS_Boss_PhaseTwoAura_Boost"
EXPECTED_DATA = "/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter"
DATA_ROUTE = os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()
if DATA_ROUTE and DATA_ROUTE != EXPECTED_DATA:
    raise RuntimeError("H019_ENCOUNTER_DEFINITION must be unset or the selected G044 encounter")
ROUTE = "data" if DATA_ROUTE else "legacy"
APPROVED_ONLY = os.environ.get("AURA_COMPARE_APPROVED_ONLY", "0") == "1"
RUN_TAG = os.environ.get("AURA_COMPARE_RUN", datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"))
if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", RUN_TAG):
    raise RuntimeError("AURA_COMPARE_RUN must be 1-64 safe filename characters")
OUT = Path("D:/FightVideo/aura_compare") / ROUTE
MANIFEST = OUT / (RUN_TAG + ".manifest.jsonl")
FPS = 15.0
MAX_WARMUP_FRAMES = 20
WARMUP_BRIGHTNESS_FLOOR = 5.0
S = {"phase": "start", "elapsed": 0.0, "gen": None, "done": False,
     "component": None, "original": None, "frames": [], "pending": None,
     "last_shot": -1.0}
HANDLE = None


def log(message):
    unreal.log(LOG + str(message))


def capture_phase(label):
    if label == "approved":
        return "approved"
    if label == "boost_candidate":
        return "candidate"
    if "discard" in label:
        return "warmup"
    return "unknown"


def capture_failure(label, reason):
    phase = capture_phase(label)
    log("CAPTURE_FAILURE run=%s route=%s phase=%s capture_id=%s label=%s path=%s reason=%s" %
        (RUN_TAG, ROUTE, phase, RUN_TAG + ":" + label, label, S.get("pending") or "NONE", reason))
    raise RuntimeError(reason)


def actors():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = plc.boss_actor(world) if world else None
    return world, pc, pawn, boss


def attribute(actor, method, value=None):
    comp = plc.component(actor, "BP_AttributesComponent_C")
    if comp is None:
        raise RuntimeError("boss AttributesComponent missing")
    tag = unreal.GameplayTag()
    tag.import_text('(TagName="Attribute.Health")')
    args = (tag,) if value is None else (tag, float(value))
    result = comp.call_method(method, args=args)
    return float(result) if value is None else result


def aura_component(boss):
    matches = []
    for component in boss.get_components_by_class(unreal.NiagaraComponent):
        asset = component.get_asset()
        if asset and asset.get_path_name() == APPROVED_PATH:
            matches.append(component)
    if len(matches) != 1:
        raise RuntimeError("expected exactly one approved aura component; found %d" % len(matches))
    return matches[0]


def lane(pc, pawn, boss, distance=260.0):
    origin = boss.get_actor_location()
    yaw = math.radians(boss.get_actor_rotation().yaw)
    pos = (origin.x + math.cos(yaw) * distance,
           origin.y + math.sin(yaw) * distance, origin.z + 20.0)
    facing = math.degrees(math.atan2(origin.y - pos[1], origin.x - pos[0]))
    plc.place_player(pc, pawn, pos, facing)


def wait(seconds):
    deadline = time.perf_counter() + seconds
    while time.perf_counter() < deadline:
        yield 0.0


def wait_game_seconds(seconds, world):
    start = plc.game_time(world)
    deadline = time.perf_counter() + 20.0
    while plc.game_time(world) - start < seconds:
        if time.perf_counter() >= deadline:
            raise RuntimeError("game-time settle timed out after %.1f real seconds" % 20.0)
        yield 0.0
    log("GAME_SETTLE requested=%.3f actual=%.3f" %
        (seconds, plc.game_time(world) - start))


def path_of(asset):
    return asset.get_path_name() if asset else "NONE"


def safe_text(read):
    try:
        value = read()
        return str(value) if value is not None else "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def write_manifest(label, png, brightness):
    world, pc, pawn, boss = actors()
    camera = next((item for item in pawn.get_components_by_class(unreal.CameraComponent)
                   if item.get_name() == "FollowCamera"), None) if pawn else None
    spring_arm = next(iter(pawn.get_components_by_class(unreal.SpringArmComponent)), None) if pawn else None
    asset = safe_text(lambda: path_of(S["component"].get_asset())) if S["component"] else "UNKNOWN"
    component = S["component"]
    active = safe_text(lambda: bool(component.is_active())) if component else "UNKNOWN"
    attach_parent = safe_text(lambda: path_of(component.get_attach_parent())) if component else "UNKNOWN"
    attach_socket = safe_text(lambda: component.get_attach_socket_name()) if component else "UNKNOWN"
    component_position = safe_text(lambda: component.get_world_location()) if component else "UNKNOWN"
    component_rotation = safe_text(lambda: component.get_world_rotation()) if component else "UNKNOWN"
    phase = ("approved" if label == "approved" else
             "candidate" if label == "boost_candidate" else
             "warmup" if "discard" in label else "unknown")
    health = safe_text(lambda: "%.4f" % attribute(boss, "Get Current Attribute Value")) if boss else "UNKNOWN"
    maximum = safe_text(lambda: "%.4f" % attribute(boss, "GetMaxAttributeValue")) if boss else "UNKNOWN"
    record = {
        "run": RUN_TAG,
        "capture_id": RUN_TAG + ":" + label,
        "route": ROUTE,
        "frame": label,
        "phase": phase,
        "game_time_s": plc.game_time(world),
        "completion": "READY",
        "asset": asset,
        "active": active,
        "attach_parent": attach_parent,
        "attach_socket": attach_socket,
        "component_position": component_position,
        "component_rotation": component_rotation,
        "health": health,
        "max_health": maximum,
        "camera": camera.get_name() if camera else "UNKNOWN",
        "camera_position": safe_text(lambda: camera.get_world_location()) if camera else "UNKNOWN",
        "control_rotation": safe_text(lambda: pc.get_control_rotation()) if pc else "UNKNOWN",
        "pivot_position": safe_text(lambda: spring_arm.get_world_location()) if spring_arm else "UNKNOWN",
        "mean_gray": round(brightness, 3),
        "png": str(png),
        "png_exists": Path(png).is_file(),
        "png_sha256": hashlib.sha256(Path(png).read_bytes()).hexdigest(),
    }
    with MANIFEST.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")
    log("MANIFEST " + json.dumps(record, sort_keys=True))
    return record


def log_frame_ready(label, png, manifest):
    log("FRAME_READY label=%s path=%s asset=%s active=%s attach_parent=%s attach_socket=%s component_pos=%s component_rot=%s" %
        (label, png, manifest.get("asset", "UNKNOWN"), manifest.get("active", "UNKNOWN"),
         manifest.get("attach_parent", "UNKNOWN"), manifest.get("attach_socket", "UNKNOWN"),
         manifest.get("component_position", "UNKNOWN"), manifest.get("component_rotation", "UNKNOWN")))


def capture(label, world):
    if S["pending"] and not Path(S["pending"]).is_file():
        return False
    now = plc.game_time(world)
    if now - S["last_shot"] < 1.0 / FPS:
        return False
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / (RUN_TAG + "_" + label + ".png")
    if target.exists():
        raise RuntimeError("refusing to overwrite prior capture: %s" % target)
    S["pending"] = target.resolve().as_posix()
    S["last_shot"] = now
    command = "HighResShot 960x540 filename=%s" % S["pending"]
    log("CAPTURE_COMMAND " + command)
    unreal.SystemLibrary.execute_console_command(world, command)
    S["frames"].append(label)
    phase = capture_phase(label)
    log("FRAME_REQUEST run=%s route=%s phase=%s capture_id=%s label=%s g=%.3f resolution=960x540 path=%s" %
        (RUN_TAG, ROUTE, phase, RUN_TAG + ":" + label, label, now, target))
    return True


def wait_capture(label, world, discarded=False):
    # Lead fix (C-1075): capture() returns False while the 1/FPS pacing window or a prior PNG is pending;
    # keep retrying until the HighResShot request is actually issued, otherwise S["pending"] stays None.
    request_deadline = time.perf_counter() + 20.0
    while not capture(label, world):
        if time.perf_counter() > request_deadline:
            capture_failure(label, "HighResShot request was never issued")
        yield 0.0
    deadline = time.perf_counter() + 20.0
    path = Path(S["pending"])
    last_size = None
    stable_polls = 0
    brightness = None
    while time.perf_counter() < deadline:
        if path.is_file():
            size = path.stat().st_size
            stable_polls = stable_polls + 1 if size == last_size and size > 33 else 0
            last_size = size
            if stable_polls >= 2:
                try:
                    brightness = mean_gray(path)
                    break
                except (OSError, ValueError, zlib.error):
                    stable_polls = 0
        yield 0.0
    if brightness is None:
        capture_failure(label, "HighResShot did not produce a complete readable PNG")
    log("FRAME_BRIGHTNESS label=%s mean_gray=%.3f threshold=5 discarded=%s" %
        (label, brightness, discarded))
    if not discarded and brightness < 5.0:
        capture_failure(label, "captured frame below brightness floor: mean_gray=%.3f threshold=5" % brightness)
    manifest = write_manifest(label, S["pending"], brightness)
    log_frame_ready(label, S["pending"], manifest)
    S["pending"] = None
    return brightness


def warmup_until_visible(world, label_prefix="warmup_discard"):
    start = plc.game_time(world)
    for index in range(1, MAX_WARMUP_FRAMES + 1):
        label = "%s_%d" % (label_prefix, index)
        brightness = yield from wait_capture(label, world, discarded=True)
        elapsed = plc.game_time(world) - start
        log("WARMUP_PROBE index=%d/%d mean_gray=%.3f floor=%.1f game_elapsed=%.3f" %
            (index, MAX_WARMUP_FRAMES, brightness, WARMUP_BRIGHTNESS_FLOOR, elapsed))
        if brightness >= WARMUP_BRIGHTNESS_FLOOR:
            log("WARMUP_READY frames=%d game_elapsed=%.3f mean_gray=%.3f" %
                (index, elapsed, brightness))
            return
        if elapsed >= 4.0:
            break
    raise RuntimeError("warmup brightness floor not reached within %d frames / 4.0 game seconds" %
                       MAX_WARMUP_FRAMES)


def witness():
    world, pc, pawn, boss = actors()
    if not all((world, pc, pawn, boss)):
        raise RuntimeError("PIE world/player/boss missing")
    OUT.mkdir(parents=True, exist_ok=True)
    if MANIFEST.exists():
        raise RuntimeError("refusing to append to a prior run manifest: %s" % MANIFEST)
    encounter = plc.component(boss, "RPGBossEncounter")
    if not encounter:
        raise RuntimeError("RPGBossEncounter missing")
    encounter.reset_for_test()
    yield from wait(1.0)
    encounter.wake()
    encounter.hold_for_test(True)
    maximum = attribute(boss, "GetMaxAttributeValue")
    if maximum <= 0.0:
        raise RuntimeError("boss max health is not positive")
    attribute(boss, "Set Current Attribute Value", maximum * 0.5)
    lane(pc, pawn, boss)
    plc.enter_combat(pawn)
    yield from wait_game_seconds(3.0, world)
    health = attribute(boss, "Get Current Attribute Value")
    S["component"] = aura_component(boss)
    S["original"] = S["component"].get_asset()
    if path_of(S["original"]) != APPROVED_PATH or not S["component"].is_active():
        raise RuntimeError("approved aura not active at 50%% HP: asset=%s active=%s" %
                           (path_of(S["original"]), S["component"].is_active()))
    camera = next((item for item in pawn.get_components_by_class(unreal.CameraComponent)
                   if item.get_name() == "FollowCamera"), None)
    if camera is None:
        raise RuntimeError("FollowCamera missing; refusing unverified comparison framing")
    log("SETUP route=%s health=%.2f max=%.2f fraction=%.4f player_boss_cm=%.1f camera=%s camera_pos=%s control_rot=%s asset=%s" %
        (ROUTE, health, maximum, health / maximum,
         (pawn.get_actor_location() - boss.get_actor_location()).length(),
         camera.get_name(), camera.get_world_location(), pc.get_control_rotation(),
         path_of(S["original"])))
    log("COMPARE_MODE approved_only=%s run=%s route=%s" % (APPROVED_ONLY, RUN_TAG, ROUTE))
    yield from warmup_until_visible(world)
    yield from wait_capture("approved", world)

    if APPROVED_ONLY:
        log("APPROVED_ONLY complete; candidate was not loaded or swapped")
        return

    candidate = unreal.load_asset(CANDIDATE_PATH)
    if not candidate:
        raise RuntimeError("required aura candidate missing: " + CANDIDATE_PATH)
    setter = getattr(S["component"], "set_asset", None)
    if not callable(setter):
        raise RuntimeError("NiagaraComponent.set_asset unavailable; refusing editor-property mutation")
    activate = getattr(S["component"], "activate", None)
    if not callable(activate):
        raise RuntimeError("NiagaraComponent.activate unavailable; refusing inactive candidate comparison")
    setter(candidate)
    activate(True)
    yield from wait_game_seconds(3.0, world)
    actual = S["component"].get_asset()
    if path_of(actual) != CANDIDATE_PATH or not S["component"].is_active():
        raise RuntimeError("candidate runtime readback mismatch asset=%s active=%s" %
                           (path_of(actual), S["component"].is_active()))
    log("CANDIDATE_READBACK asset=%s active=%s health=%.2f max=%.2f fraction=%.4f" %
        (path_of(actual), S["component"].is_active(),
         attribute(boss, "Get Current Attribute Value"), maximum,
         attribute(boss, "Get Current Attribute Value") / maximum))
    yield from warmup_until_visible(world, "candidate_discard")
    yield from wait_capture("boost_candidate", world)


def finish(reason):
    global HANDLE
    if S["done"]:
        return
    S["done"] = True
    try:
        if S["component"] and S["original"]:
            restore_original_asset(S["component"], S["original"])
    except Exception as exc:
        log("RESTORE_ERROR %s" % exc)
    unreal.SystemLibrary.execute_console_command(None, "rpg.Art.Tier2 0")
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    log("SUMMARY route=%s frames=%s reason=%s output=%s" % (ROUTE, ",".join(S["frames"]), reason, OUT))
    plc.end_play()


def restore_original_asset(component, original):
    component.set_asset(original)
    activate = getattr(component, "activate", None)
    if callable(activate):
        activate(True)
    restored = path_of(component.get_asset())
    if restored != path_of(original):
        raise RuntimeError("transient aura restore mismatch: %s" % restored)
    log("RESTORE asset=%s verified=true" % restored)
    return restored


def tick(dt):
    try:
        S["elapsed"] += dt
        if S["elapsed"] > 75.0:
            finish("timeout")
            return
        if S["phase"] == "start":
            if S["elapsed"] > 0.5:
                if DATA_ROUTE:
                    unreal.SystemLibrary.execute_console_command(None, "rpg.EncounterDefinition " + DATA_ROUTE)
                unreal.SystemLibrary.execute_console_command(None, "rpg.Art.Tier2 1")
                log("ROUTE route=%s selection=%s" % (ROUTE, DATA_ROUTE or "unset (legacy startup)"))
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                S.update(phase="wait", elapsed=0.0)
            return
        world, _, _, boss = actors()
        if S["phase"] == "wait":
            if world and boss and S["elapsed"] >= 6.0:
                S.update(phase="run", gen=witness())
            return
        if S["phase"] == "run":
            next(S["gen"])
    except StopIteration:
        finish("comparison captured and transient component restored")
    except Exception:
        import traceback
        log("ERROR " + traceback.format_exc())
        finish("error")


HANDLE = unreal.register_slate_post_tick_callback(tick)
log("driver registered; Lead-only, no asset save; candidate must exist before run")
