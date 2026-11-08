"""Lead-only PIE witness: real A4 blade contact into a timed player parry.

Run with RunLeadPie.ps1, not from a second editor. The script opts Tier 2 in,
holds the encounter for a deterministic A4, and restores the cvars on exit.
It reports contact, the boss recoil montage, and the legend feedback pulse
separately; a pressed parry without contact is never a pass.
"""
import math
import os
import sys
import time
from pathlib import Path

import unreal

sys.path.insert(0, str(Path(unreal.Paths.project_dir()) / "Scripts" / "Editor"))
import pie_lead_common as plc

PREFIX = "[Tier2Parry] "
RUN_TAG = time.strftime("run_%Y%m%d_%H%M%S")
S = {"phase": "start", "elapsed": 0.0, "gen": None, "wake": 0.0,
     "done": False, "result": False, "frame_pending": None, "frames": []}
HANDLE = None


def log(message):
    unreal.log(PREFIX + str(message))


def console(command):
    unreal.SystemLibrary.execute_console_command(None, command)


def actors():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    return world, pc, pawn, plc.boss_actor(world)


def real_wait(seconds):
    until = time.perf_counter() + seconds
    while time.perf_counter() < until:
        yield 0.0


def place_near_boss(pc, pawn, boss, distance=250.0):
    origin = boss.get_actor_location()
    yaw = math.radians(boss.get_actor_rotation().yaw)
    location = (origin.x + math.cos(yaw) * distance,
                origin.y + math.sin(yaw) * distance, origin.z + 20.0)
    facing = math.degrees(math.atan2(origin.y - location[1], origin.x - location[0]))
    plc.place_player(pc, pawn, location, facing)


def boss_montage(boss):
    for mesh in boss.get_components_by_class(unreal.SkeletalMeshComponent):
        instance = mesh.get_anim_instance()
        montage = instance.get_current_active_montage() if instance else None
        if montage:
            return montage.get_name()
    return "None"


def _property(item, name):
    try:
        return item.get_editor_property(name)
    except (AttributeError, RuntimeError):
        return getattr(item, name)


def camera_blendables(pawn):
    """Report actual camera blendables, including PPM weight, or an explicit read limit."""
    try:
        cameras = pawn.get_components_by_class(unreal.CameraComponent)
        camera = next((item for item in cameras if item.get_name() == "FollowCamera"), None)
        if camera is None:
            camera = next(iter(cameras), None)
        if camera is None:
            return "camera=missing"
        settings = _property(camera, "post_process_settings")
        weighted = _property(settings, "weighted_blendables")
        entries = _property(weighted, "array")
        weights = []
        for entry in entries:
            material = _property(entry, "object")
            name = material.get_name() if material else "None"
            weights.append("%s=%.3f" % (name, float(_property(entry, "weight"))))
        return "camera=%s count=%d weights=[%s]" % (camera.get_name(), len(weights), ",".join(weights))
    except Exception as exc:
        return "read_error=%s" % exc


def request_frame(world, label, elapsed):
    """HighResShot requests are serialized; log actual game-time offsets."""
    pending = S["frame_pending"]
    if pending is not None and not pending.exists():
        return False
    folder = frame_folder()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (label + ".png")
    unreal.SystemLibrary.execute_console_command(world, "HighResShot 960x540 filename=" + path.as_posix())
    S["frame_pending"] = path
    S["frames"].append((label, elapsed, str(path)))
    offset = "baseline" if elapsed is None else "%.3f" % elapsed
    log("FRAME label=%s actual_offset=%s path=%s" % (label, offset, path))
    return True


def frame_folder():
    route = "data" if os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip() else "legacy"
    return Path(os.environ.get("TIER2_PARRY_FRAMES", "D:/FightVideo/tier2_parry_" + route)) / RUN_TAG


def warmup_frame(world):
    """Discard the first black HighResShot seen in C-1036 before the A4 timeline."""
    folder = frame_folder()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "warmup_discard.png"
    unreal.SystemLibrary.execute_console_command(world, "HighResShot 960x540 filename=" + path.as_posix())
    log("FRAME warmup_discard path=%s" % path)
    deadline = time.perf_counter() + 5.0
    while not path.exists() and time.perf_counter() < deadline:
        yield 0.0
    if not path.exists():
        raise RuntimeError("warmup HighResShot did not arrive")


def baseline_frame(world, label):
    if not request_frame(world, label, None):
        raise RuntimeError("prior baseline HighResShot did not arrive")
    path = S["frame_pending"]
    deadline = time.perf_counter() + 5.0
    while not path.exists() and time.perf_counter() < deadline:
        yield 0.0
    if not path.exists():
        raise RuntimeError("baseline HighResShot did not arrive: " + label)


def witness():
    world, pc, pawn, boss = actors()
    if not all((world, pc, pawn, boss)):
        raise RuntimeError("player, controller or live boss missing")
    encounter = plc.component(boss, "RPGBossEncounter")
    tracker = plc.component(boss, "RPGAttackTracker")
    sweep = plc.component(boss, "RPGBossLowSweep")
    parry = plc.component(pawn, "RPGPlayerParry")
    tier2 = plc.component(boss, "RPGTier2BossPresentation")
    legend = plc.component(boss, "RPGBossLegend")
    if not all((encounter, tracker, sweep, parry, tier2, legend)):
        raise RuntimeError("parry witness components missing: %s" %
                           [bool(x) for x in (encounter, tracker, sweep, parry, tier2, legend)])
    plc.enter_combat(pawn)
    encounter.reset_for_test()
    yield from real_wait(1.0)
    encounter.wake()
    encounter.hold_for_test(True)
    plc.refill_player(boss)
    yield from real_wait(2.2)
    world, pc, pawn, boss = actors()
    if not all((world, pc, pawn, boss)):
        raise RuntimeError("actor missing after encounter reset")
    ready_deadline = time.perf_counter() + 5.0
    while not tracker.is_neutral() and time.perf_counter() < ready_deadline:
        yield 0.0
    if not tracker.is_neutral():
        raise RuntimeError("boss did not become neutral after wake clip")
    place_near_boss(pc, pawn, boss)
    unreal.SystemLibrary.execute_console_command(world, "ShowFlag.EyeAdaptation 0")
    log("capture exposure: ShowFlag.EyeAdaptation 0; settling visible arena for 2.2 real seconds")
    yield from real_wait(2.2)
    yield from warmup_frame(world)
    yield from baseline_frame(world, "baseline_1")
    yield from real_wait(0.5)
    yield from baseline_frame(world, "baseline_2")
    # Slow the world only for visual capture. Parry and tracker windows are
    # game-time windows, so the relative attack/parry timing is unchanged.
    unreal.SystemLibrary.execute_console_command(world, "slomo 0.25")
    initial = sweep.get_parried_count()
    sweep_before = sweep.get_sweep_count()
    start_game = plc.game_time(world)
    started = bool(tracker.start_move("A4", True))
    log("A4 requested started=%s parried_before=%d distance_cm=%.1f boss_montage=%s" %
        (started, initial, math.hypot(pawn.get_actor_location().x - boss.get_actor_location().x,
                                       pawn.get_actor_location().y - boss.get_actor_location().y), boss_montage(boss)))
    if not started:
        raise RuntimeError("A4 StartMove refused")
    # A4 uses RPGBossLowSweep's tracker active window rather than the pack's
    # ANS_CollisionTrace. Press on that observed window edge, not a wall-clock
    # delay from StartMove; the blade crosses the frontal player later in the arc.
    opened = False
    pressed = False
    before_requested = False
    active_deadline = time.perf_counter() + 6.0
    while time.perf_counter() < active_deadline:
        pos = tracker.get_position()
        active = bool(tracker.is_active_window())
        origin, target = boss.get_actor_location(), pawn.get_actor_location()
        distance = math.hypot(target.x - origin.x, target.y - origin.y)
        log("A4 tick g=%.3f pos=%.3f active=%s sweep=%d montage=%s distance_cm=%.1f" %
            (plc.game_time(world) - start_game, pos, active,
             sweep.get_sweep_count() - sweep_before, boss_montage(boss), distance))
        if not before_requested and pos >= 0.50 and not active:
            before_requested = request_frame(world, "press_minus_0p1", pos - 0.60)
            log("BLENDABLE before_press %s" % camera_blendables(pawn))
        if active and pos >= 0.71:
            opened = bool(parry.press())
            pressed = True
            press_game = plc.game_time(world)
            log("parry_press at observed A4 active window opened=%s pos=%.3f distance_cm=%.1f" %
                (opened, pos, distance))
            log("BLENDABLE at_press %s" % camera_blendables(pawn))
            break
        yield 0.0
    if not pressed:
        raise RuntimeError("A4 never entered its live sweep window")
    deadline = time.perf_counter() + 5.0
    recoil_seen = False
    contact = False
    targets = (("press_plus_0p05", 0.05), ("press_plus_0p15", 0.15), ("press_plus_0p30", 0.30))
    next_frame = 0
    while time.perf_counter() < deadline:
        if not contact and sweep.get_parried_count() > initial:
            contact = True
            log("BLENDABLE at_real_contact %s" % camera_blendables(pawn))
        recoil_seen |= "ParryRecoil" in boss_montage(boss)
        since_press = plc.game_time(world) - press_game
        if next_frame < len(targets) and since_press >= targets[next_frame][1]:
            label, _ = targets[next_frame]
            if request_frame(world, label, since_press):
                log("BLENDABLE %s %s" % (label, camera_blendables(pawn)))
                next_frame += 1
        if contact and recoil_seen and next_frame == len(targets):
            break
        yield 0.0
    log("RESULT opened=%s real_contact=%s parried_delta=%d recoil_montage_seen=%s" %
        (opened, contact, sweep.get_parried_count() - initial, recoil_seen))
    log("BLENDABLE after_contact %s" % camera_blendables(pawn))
    log("frames_captured=%d/%d; requested offsets are reported above, visual PPM proof requires Lead inspection" %
        (len(S["frames"]), 6))
    S["result"] = opened and contact and sweep.get_parried_count() == initial + 1 and recoil_seen
    yield from real_wait(0.5)


def finish(reason):
    global HANDLE
    if S["done"]:
        return
    S["done"] = True
    try:
        _, _, _, boss = actors()
        encounter = plc.component(boss, "RPGBossEncounter") if boss else None
        if encounter:
            encounter.hold_for_test(False)
    except Exception:
        pass
    console("rpg.Art.Tier2 0")
    console("rpg.Legend 0")
    console("slomo 1")
    console("ShowFlag.EyeAdaptation 1")
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
                    console("rpg.EncounterDefinition " + selection)
                console("rpg.Art.Tier2 1")
                console("rpg.Legend 1")
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                S.update(phase="wait", elapsed=0.0)
            return
        if S["phase"] == "wait":
            world, pc, pawn, boss = actors()
            if all((world, pc, pawn, boss)) and S["elapsed"] > 6.0:
                S.update(phase="run", gen=witness())
            elif S["elapsed"] > 25.0:
                finish("actors missing")
            return
        world, _, _, _ = actors()
        if world is None:
            raise RuntimeError("PIE world lost")
        if plc.game_time(world) >= S["wake"]:
            try:
                S["wake"] = plc.game_time(world) + float(next(S["gen"]))
            except StopIteration:
                finish("witness complete")
    except Exception:
        import traceback
        log("ERROR " + traceback.format_exc())
        finish("exception")


HANDLE = unreal.register_slate_post_tick_callback(tick)
