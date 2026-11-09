"""Lead PIE driver (owner 2026-11-07): one full fight against the Ember Warden for a review video.

The bot walks to the boss and cycles through every Elden Ring move so the owner can judge the new clips
in play: R1 light, R2 strong, standing dodge (backstep), jump+R1 (air light), jump+R2 (air heavy),
L1 block (pack IA_Block) and an R2 guard counter when the counter window arms.

Honesty notes logged at start and in the summary:
- the player is refilled by the boss's RPGCombatDebug when below 35 HP, so the fight reaches the end;
- the boss keeps its real health and AI (no hold, no damage scaling).
Ends when the boss dies (actor destroyed or health <= 0) or after MAX_FIGHT_SECONDS.
Log prefix [FullFight]; stop marker "[FullFight] finished:".
"""
import math
import json
import hashlib
import os
import re
import unreal
import sys
from pathlib import Path
sys.path.insert(0, str(Path(unreal.Paths.project_dir()) / "Scripts" / "Editor"))
import pie_lead_common as plc

FRAMES = os.environ.get("FIGHT_FRAMES", "D:/FightVideo/fight")
FIGHT_RUN = re.sub(r"[^A-Za-z0-9_-]+", "_", os.environ.get("FIGHT_RUN", "fight"))[:64] or "fight"
FIGHT_BUILD_ID = os.environ.get("FIGHT_BUILD_ID", "UNKNOWN").strip() or "UNKNOWN"
FIGHT_MAP_NAME = os.environ.get("FIGHT_MAP_NAME", "UNKNOWN").strip() or "UNKNOWN"
TOOL_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
FRAME_FPS = 15.0
FRAME_CONTEXT_SCHEMA = 1
PARRY_WATCH_SECONDS = 3.0
PARRY_CONTACT_WATCH_SECONDS = 0.60
FIGHT_PARRY_ONLY = os.environ.get("FIGHT_PARRY_ONLY", "0") == "1"
FIGHT_DODGE_ONLY = os.environ.get("FIGHT_DODGE_ONLY", "0") == "1"
FIGHT_DODGE_TARGET = os.environ.get("FIGHT_DODGE_TARGET", "all").strip()
PARRY_ONLY_CONTROL = os.environ.get("PARRY_ONLY_CONTROL", "0") == "1"
if FIGHT_DODGE_TARGET not in ("all", "Mid01"):
    raise ValueError("FIGHT_DODGE_TARGET must be 'all' or 'Mid01'")
if FIGHT_DODGE_TARGET != "all" and not FIGHT_DODGE_ONLY:
    raise ValueError("FIGHT_DODGE_TARGET requires FIGHT_DODGE_ONLY=1")
if sum((FIGHT_PARRY_ONLY, FIGHT_DODGE_ONLY, PARRY_ONLY_CONTROL)) > 1:
    raise ValueError("FIGHT_PARRY_ONLY, FIGHT_DODGE_ONLY and PARRY_ONLY_CONTROL are mutually exclusive")
# Positions are montage-local seconds measured at the boss HP drop, minus ~0.1 s.
# Populate only from witnessed PLAYER_HIT lines; absent evidence uses the 60% fallback.
PARRY_MOVE_PRESS_POSITIONS = {"A1b": 0.12, "A3b": 0.10, "A1": 0.27, "A3a": 0.42, "A2": 1.92}
PARRY_MONTAGE_PRESS_POSITIONS = {"Mid01_Anim_Montage": 0.62}
PARRY_LOG_ONLY_MONTAGES = {"GS_SprintAttackFollowUp_Montage"}
DODGE_ONLY_PLAYER_DISTANCE_CM = 200.0
DODGE_PRESS_LEAD_SECONDS = 0.15
DODGE_INPUT_HOLD_SECONDS = 0.10
DODGE_ACTION_LOCK_SECONDS = 0.45
DODGE_CONTACT_RESULT_SECONDS = 0.30
PARRY_CONTROL_MIN_DISTANCE_CM = 115.0
PARRY_CONTROL_MAX_DISTANCE_CM = 125.0
PARRY_CONTROL_HARD_MAX_DISTANCE_CM = 130.0
PARRY_PACK_CONTACT_POSITIONS = {
    "A1b": (0.190, 0.199, 0.231), "A3b": (0.152, 0.254),
    "A1": (0.351,), "A3a": (0.484, 0.530),
    "A2": (1.974, 2.030, 2.104),
    "Mid01_Anim_Montage": (0.696, 0.795),
    "GS_SprintAttackFollowUp_Montage": (0.070, 0.456),
}
# Earliest witnessed contact per tracked montage, so one roll can cover the
# multi-hit cluster. Sprint follow-up varies by occurrence; alternate its two
# witnessed contact positions across repeated playbacks.
DODGE_MOVE_CONTACT_POSITIONS = {"A1b": (0.190,), "A3b": (0.152,), "A1": (0.351,),
                                "A3a": (0.484,), "A2": (1.974,)}
DODGE_MONTAGE_CONTACT_POSITIONS = {"Mid01_Anim_Montage": (0.700,),
                                   "GS_SprintAttackFollowUp_Montage": (0.070, 0.456)}
DODGE_TARGET_MID01_MONTAGES = {"Mid01_Anim_Montage", "GS_SprintAttackFollowUp_Montage"}
PARRY_FRAME_OFFSETS = (("plus_0p05", 0.05), ("plus_0p15", 0.15), ("plus_0p30", 0.30))
PLAYER_HP_READY_GRACE_SECONDS = 5.0

LOG = "[FullFight] "
MAX_FIGHT_SECONDS = float(os.environ.get("FIGHT_MAX", "480"))
BLOCK_ACTION = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Block"
R1, R2, JUMP, DODGE = "Gamepad_RightShoulder", "Gamepad_RightTrigger", "Gamepad_FaceButton_Bottom", "Gamepad_FaceButton_Right"
# Each action: list of (time_s, key, down) plus the time the action lasts. "guard" is handled separately.
ACTIONS = {
    "light": ([(0.00, R1, True), (0.08, R1, False)], 1.0),
    "strong": ([(0.00, R2, True), (0.12, R2, False)], 1.5),
    "backstep": ([(0.00, DODGE, True), (0.10, DODGE, False)], 1.0),
    "air_light": ([(0.00, JUMP, True), (0.10, JUMP, False), (0.30, R1, True), (0.38, R1, False)], 1.6),
    "air_heavy": ([(0.00, JUMP, True), (0.10, JUMP, False), (0.30, R2, True), (0.42, R2, False)], 1.9),
}
CYCLE = ["light", "light", "strong", "backstep", "air_light", "guard", "light", "air_heavy", "backstep", "guard", "strong", "parry_watch"]
S = {"phase": "start", "elapsed": 0.0, "fight_time": 0.0, "held": set(), "cycle": 0, "action": None,
     "action_t": 0.0, "action_id": None, "action_count": 0, "event": 0, "beat": 0.0,
     "counts": {}, "refills": 0, "player_deaths": 0, "done": False, "boss_dead": False,
     "boss_health_start": "UNKNOWN", "boss_health_max_start": "UNKNOWN",
     "boss_ai_controller_start": "UNKNOWN", "boss_driver_mutations": 0,
     "g_last": None, "frame": 0, "pending": None, "g_shot": -1.0, "player_missing_at": None,
     "player_hp_ready": False, "last_player_hp": None, "parry_watch_seen": set(),
     "parry_watch_scheduled": {}, "parry_watch_pending": None,
     "parry_watch_observed": set(), "parry_missing_logged": False,
     "parry_timeout_action_ids": set(), "last_parry_diag_montage": None,
     "last_parry_diag_active": None, "parry_montage_last_position": {},
     "parry_montage_occurrences": {}, "parry_montage_seen": set(),
     "parry_pack_contact_samples": set(),
     "parry_synthetic_instance": 1000000,
     "dodge_watch_seen": set(), "dodge_watch_scheduled": {},
     "dodge_watch_pending": [], "dodge_attempt_count": 0,
     "pending_parry_frame": None, "air_light_count": 0, "action_instance": None}
HANDLE = None


def log(m):
    unreal.log(LOG + str(m))


def action_id(run, ordinal):
    return "%s:action:%05d" % (run, ordinal)


def boss_ai_controller(boss):
    try:
        controller = boss.get_controller() if boss else None
        return controller.get_class().get_name() if controller else "None"
    except Exception:
        return "UNKNOWN"


def run_provenance(run, build_id, map_name, configured_route, tier2, tool_sha256):
    return {"run": run, "build_id": build_id, "map": map_name, "route": configured_route,
            "tier2": bool(tier2), "tool_sha256": tool_sha256,
            "frame_context_schema": FRAME_CONTEXT_SCHEMA}


def receipt_summary(state, ending_reason, boss_health_end, boss_ai_controller_end):
    action_names = ("light", "strong", "backstep", "air_light", "air_heavy", "guard", "parry_watch",
                    "counter", "parry_contact", "dodge_watch", "dodge_attempt")
    return {"run": FIGHT_RUN, "fight_seconds": round(float(state["fight_time"]), 3),
            "boss_dead": bool(state["boss_dead"]), "reason": ending_reason,
            "action_counts": {name: int(state["counts"].get(name, 0)) for name in action_names},
            "player_refills": int(state["refills"]),
            "player_deaths": int(state["player_deaths"]), "frames": int(state["frame"]),
            "boss_health_start": state["boss_health_start"],
            "boss_health_max_start": state["boss_health_max_start"], "boss_health_end": boss_health_end,
            "boss_ai_controller_start": state["boss_ai_controller_start"],
            "boss_ai_controller_end": boss_ai_controller_end,
            "boss_driver_mutations": int(state["boss_driver_mutations"]),
            "boss_health_writes_by_driver": 0, "boss_ai_writes_by_driver": 0,
            "successful_parries": int(state["counts"].get("parry_contact", 0))}


def clear_action():
    S["action"] = None
    S["action_id"] = None
    S["action_t"] = 0.0


def comp(actor, name):
    return plc.component(actor, name)


def attr(actor, tag_name, maximum=False):
    if not maximum and tag_name == "Attribute.Health":
        try:
            return plc.health(actor)
        except Exception:
            return None
    c = comp(actor, "BP_AttributesComponent_C")
    if not c:
        return None
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag_name)
    try:
        return float(c.call_method("GetMaxAttributeValue" if maximum else "Get Current Attribute Value", args=(t,)))
    except Exception:
        return None


def montage(actor):
    try:
        name, _ = plc.player_montage(actor)
        return name or "None"
    except Exception:
        return "UNKNOWN"


def parry_window_state(move, tracker_active, tracker_instance, boss_montage, sweep_active, sweep_count):
    if tracker_active and str(move) not in ("", "None", "UNKNOWN"):
        return True, int(tracker_instance), "tracker"
    if boss_montage == "GS_Attack04_Montage" and sweep_active:
        return True, int(sweep_count), "boss_montage_sweep"
    return False, int(tracker_instance), "tracker"


def parry_press_target(move, boss_montage):
    """Return only a measured montage-origin target; unknown timings never use window fractions."""
    value = PARRY_MOVE_PRESS_POSITIONS.get(str(move))
    if isinstance(value, (int, float)):
        return float(value), "tracker_move"
    value = PARRY_MONTAGE_PRESS_POSITIONS.get(str(boss_montage))
    if isinstance(value, (int, float)):
        return float(value), "montage_name"
    if str(boss_montage) in PARRY_LOG_ONLY_MONTAGES:
        return None, "log_only"
    return None, "no_timing_target"


def parry_montage_occurrence(boss_montage, montage_position):
    """Identify each playback by montage-name change or a position reset."""
    name = str(boss_montage)
    position = _number_or_unknown(montage_position)
    if name in ("", "None", "UNKNOWN") or not isinstance(position, (int, float)):
        return None
    previous = S["parry_montage_last_position"].get(name)
    occurrences = S["parry_montage_occurrences"]
    if previous is None or position < previous - 0.05:
        occurrences[name] = occurrences.get(name, 0) + 1
    S["parry_montage_last_position"][name] = position
    return occurrences[name]


def dodge_contact_target(move, boss_montage, occurrence):
    """Return witnessed contact, press point and evidence source for one attack playback."""
    contacts = DODGE_MOVE_CONTACT_POSITIONS.get(str(move))
    source = "tracker_move"
    if not contacts:
        contacts = DODGE_MONTAGE_CONTACT_POSITIONS.get(str(boss_montage))
        source = "montage_name"
    if not contacts:
        return None, None, "no_timing_target"
    # One press per playback. Sprint's two distinct observed contact variants
    # are assigned to alternating occurrences, not both pressed in one swing.
    contact = float(contacts[(max(1, int(occurrence)) - 1) % len(contacts)])
    raw_press = contact - DODGE_PRESS_LEAD_SECONDS
    press = max(0.0, raw_press)
    if raw_press < 0.0:
        source += "_clamped"
    return contact, press, source


def dodge_target_allowed(boss_montage):
    """In targeted mode, wait only for the two witnessed Mid01/Sprint montages."""
    return FIGHT_DODGE_TARGET == "all" or str(boss_montage) in DODGE_TARGET_MID01_MONTAGES


def dodge_target_for_montage(move, boss_montage, occurrence):
    if not dodge_target_allowed(boss_montage):
        return None, None, "target_filtered"
    if FIGHT_DODGE_TARGET == "Mid01":
        move = "None"  # force montage-name timing for Mid01/Sprint-only runs
    return dodge_contact_target(move, boss_montage, occurrence)


def invulnerability_tag_active(pawn):
    """Read Status.Invulnerable without mutating player state; None means unreadable."""
    if pawn is None:
        return None
    try:
        tag = unreal.GameplayTag()
        tag.import_text('(TagName="Status.Invulnerable")')
        return bool(pawn.call_method("HasMatchingGameplayTag", args=(tag,)))
    except Exception:
        return None


def boolean_marker(value):
    return "true" if value is True else "false" if value is False else "UNKNOWN"


def pack_status_snapshot(pawn):
    """Read status tags that the pack impact decision may consume; never mutate tags."""
    names = ("Status.ParryActive", "Status.Blocking", "State.Blocking",
             "Ability.Parry", "Ability.Block", "Status.Invulnerable")
    values = []
    for name in names:
        try:
            tag = unreal.GameplayTag()
            tag.import_text('(TagName="%s")' % name)
            value = bool(pawn.call_method("HasMatchingGameplayTag", args=(tag,)))
        except Exception:
            value = None
        field = name.replace("Status.", "status").replace("State.", "state").replace("Ability.", "ability")
        values.append("%s=%s" % (field, boolean_marker(value)))
    return ",".join(values)


def parry_control_distance_action(distance_cm):
    """Maintain a conservative 115-125 cm no-input control band."""
    distance = _number_or_unknown(distance_cm)
    if not isinstance(distance, (int, float)):
        return "unknown"
    if distance > PARRY_CONTROL_HARD_MAX_DISTANCE_CM:
        return "clamp"
    if distance > PARRY_CONTROL_MAX_DISTANCE_CM:
        return "retreat"
    if distance < PARRY_CONTROL_MIN_DISTANCE_CM:
        return "approach"
    return "hold"


def parry_control_distance_step(pawn, boss, pc, distance_cm, mode):
    """Keep parry and no-parry runs in the same close band; return measured/control distance."""
    action = parry_control_distance_action(distance_cm)
    if action == "clamp":
        bl = boss.get_actor_location()
        plc.place_player(pc, pawn, (bl.x + PARRY_CONTROL_MIN_DISTANCE_CM, bl.y, bl.z), 180)
        controlled_distance = PARRY_CONTROL_MIN_DISTANCE_CM
    elif action == "retreat":
        pawn.add_movement_input(pawn.get_actor_forward_vector(), -1.0, True)
        controlled_distance = distance_cm
    elif action == "approach":
        pawn.add_movement_input(pawn.get_actor_forward_vector(), 1.0, True)
        controlled_distance = distance_cm
    else:
        controlled_distance = distance_cm
    if S["beat"] == 0.0:
        log("PARRY_CONTROL_RANGE mode=%s t=%.2f distance_cm=%.1f action=%s press=%d attacks=0 hard_max_cm=%.1f" %
            (mode, S["fight_time"], controlled_distance, action,
             1 if mode == "parry" else 0, PARRY_CONTROL_HARD_MAX_DISTANCE_CM))
    return controlled_distance


def log_player_hit(pawn, boss, hp_before, hp_after):
    """Log a real observed health drop with the boss tracker and montage position context."""
    before, after = _number_or_unknown(hp_before), _number_or_unknown(hp_after)
    if not isinstance(before, (int, float)) or not isinstance(after, (int, float)) or after >= before:
        return False
    tracker = comp(boss, "RPGAttackTracker") if boss else None
    try:
        move = str(tracker.get_current_move()) if tracker else "UNKNOWN"
        instance = int(tracker.get_attack_instance()) if tracker else -1
        tracker_position = _number_or_unknown(tracker.get_position()) if tracker else "UNKNOWN"
    except Exception:
        move, instance, tracker_position = "UNKNOWN", -1, "UNKNOWN"
    try:
        boss_montage, montage_position = plc.player_montage(boss) if boss else ("UNKNOWN", "UNKNOWN")
    except Exception:
        boss_montage, montage_position = "UNKNOWN", "UNKNOWN"
    log("PLAYER_HIT t=%.3f hp_before=%.1f hp_after=%.1f damage=%.1f boss_move=%s boss_instance=%d boss_montage=%s tracker_position=%s montage_position=%s player_status_tags=%s pack_impact_outcome=UNKNOWN" %
        (S["fight_time"], before, after, before - after, move, instance, boss_montage,
         _parry_position(tracker_position), _parry_position(_number_or_unknown(montage_position)),
         pack_status_snapshot(pawn)))
    return True


def parry_attempt_context(pawn, boss):
    """Capture attempt-time separation and player health; unreadable values stay explicit."""
    try:
        player_location = pawn.get_actor_location()
        boss_location = boss.get_actor_location()
        distance = math.sqrt(sum((float(getattr(player_location, axis)) -
                                  float(getattr(boss_location, axis))) ** 2
                                 for axis in ("x", "y", "z")))
    except Exception:
        distance = None
    return _number_or_unknown(distance), _number_or_unknown(attr(pawn, "Attribute.Health"))


def _number_or_unknown(value):
    number = _finite_number(value)
    return number if isinstance(number, (int, float)) else "UNKNOWN"


def _parry_number(value):
    return "UNKNOWN" if not isinstance(value, (int, float)) else "%.1f" % value


def _parry_position(value):
    return "UNKNOWN" if not isinstance(value, (int, float)) else "%.3f" % value


def parry_result_context(pending, pawn, boss, now):
    """Build comparable attempt-to-resolution telemetry for a no-contact result."""
    hp_after = _number_or_unknown(attr(pawn, "Attribute.Health"))
    hp_before = pending.get("player_hp_before")
    known_hp = isinstance(hp_after, (int, float)) and isinstance(hp_before, (int, float))
    hp_delta = hp_after - hp_before if known_hp else "UNKNOWN"
    took_damage = "UNKNOWN" if not known_hp else str(hp_delta < -0.01).lower()
    elapsed = max(0.0, float(now) - float(pending.get("attempt_time", now)))
    return ("distance_cm=%s player_hp_before=%s player_hp_after=%s player_hp_delta=%s "
            "player_took_damage=%s window_seconds=%.2f parry_window_seconds=%s "
            "tracker_window_seconds=%s watch_limit_seconds=%.2f" %
            (_parry_number(pending.get("distance_cm")), _parry_number(hp_before),
             _parry_number(hp_after), _parry_number(hp_delta), took_damage, elapsed,
             _parry_number(pending.get("parry_window_seconds")),
             _parry_position(pending.get("tracker_window_seconds")),
             float(pending.get("watch_limit_seconds", PARRY_WATCH_SECONDS))))


def actors():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = plc.boss_actor(world)
    return world, pc, pawn, boss


def key(pc, k, down):
    unreal.RPGInputTestUtils.set_key_down(pc, k, down)
    (S["held"].add if down else S["held"].discard)(k)


def release_all(pc):
    for k in list(S["held"]):
        try:
            unreal.RPGInputTestUtils.set_key_down(pc, k, False)
        except Exception:
            pass
    S["held"].clear()


def face(pc, pawn, boss):
    a, b = pawn.get_actor_location(), boss.get_actor_location()
    yaw = math.degrees(math.atan2(b.y - a.y, b.x - a.x))
    pc.set_control_rotation(unreal.Rotator(0.0, 0.0, yaw))
    return math.hypot(b.x - a.x, b.y - a.y)


def player_failure(pawn, hp, now):
    if pawn is None:
        if S["player_missing_at"] is None:
            S["player_missing_at"] = now
        if now - S["player_missing_at"] >= 3.0:
            return "player missing for 3 s"
        return None
    S["player_missing_at"] = None
    if hp is not None and hp > 0.0 and not S["player_hp_ready"]:
        S["player_hp_ready"] = True
        log("PLAYER_HP_READY hp=%.1f fight_time=%.3f" % (hp, now))
    if hp is not None and hp <= 0.0 and (
            S["player_hp_ready"] or now >= PLAYER_HP_READY_GRACE_SECONDS):
        return "player dead"
    return None


def capture(world):
    """One 960x540 in-engine frame per 1/15 s of game time; the next request waits for the previous PNG."""
    g = plc.game_time(world)
    if S["pending"] is not None and not os.path.exists(S["pending"]):
        return
    if S["pending"] is not None and S.get("pending_parry_frame"):
        ready = S.pop("pending_parry_frame")
        log("PARRY_FRAME_READY label=%s instance=%d frame=%d t=%.3f actual_offset=%.3f path=%s" %
            (ready["label"], ready["instance"], ready["frame"], ready["time"], ready["offset"], S["pending"]))
        log("PARRY_BLENDABLE %s %s" % (ready["label"], camera_blendables(ready["pawn"])))
    if g - S["g_shot"] < 1.0 / FRAME_FPS:
        return
    S["g_shot"] = g
    S["pending"] = "%s/f_%05d.png" % (FRAMES, S["frame"])
    unreal.SystemLibrary.execute_console_command(world, "HighResShot 960x540 filename=%s" % S["pending"])
    log("FRAME %d g=%.3f marker=%s:frame:%05d action=%s action_id=%s" %
        (S["frame"], g, FIGHT_RUN, S["frame"], S["action"], S["action_id"] or "None"))
    try:
        _, pc, pawn, boss = actors()
    except Exception:
        pc = pawn = boss = None
    log("FRAME_CONTEXT " + json.dumps(frame_camera_context(world, pc, pawn, boss, S["frame"]),
                                        sort_keys=True, allow_nan=False))
    parry_capture = S.get("parry_capture")
    if parry_capture:
        elapsed = S["fight_time"] - parry_capture["contact_time"]
        for label, offset in PARRY_FRAME_OFFSETS:
            if label not in parry_capture["captured"] and elapsed >= offset:
                parry_capture["captured"].add(label)
                S["pending_parry_frame"] = {"label": label, "instance": parry_capture["instance"],
                                             "frame": S["frame"], "time": S["fight_time"],
                                             "offset": elapsed, "pawn": parry_capture["pawn"]}
                log("PARRY_FRAME_REQUEST label=%s instance=%d frame=%d t=%.3f actual_offset=%.3f path=%s" %
                    (label, parry_capture["instance"], S["frame"], S["fight_time"], elapsed, S["pending"]))
                break
    S["frame"] += 1


def finish(reason):
    global HANDLE
    if S["done"]:
        return
    S["done"] = True
    pending_parry = S.get("parry_watch_pending")
    if pending_parry:
        log("PARRY_RESULT instance=%s outcome=interrupted reason=%s" %
            (pending_parry["instance"], reason))
        S["parry_watch_pending"] = None
    try:
        _, pc, _, _ = actors()
        if pc:
            release_all(pc)
    except Exception:
        pass
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    try:
        _, _, _, boss = actors()
        boss_health_end = attr(boss, "Attribute.Health") if boss else "UNKNOWN"
        boss_ai_end = boss_ai_controller(boss)
    except Exception:
        boss_health_end, boss_ai_end = "UNKNOWN", "UNKNOWN"
    summary = receipt_summary(S, reason, boss_health_end, boss_ai_end)
    log("RECEIPT_SUMMARY " + json.dumps(summary, sort_keys=True, allow_nan=False))
    log("SUMMARY fight_seconds=%.1f boss_dead=%s actions_json=%s player_refills=%d player_deaths=%d frames=%d" %
        (S["fight_time"], S["boss_dead"], json.dumps(S["counts"], sort_keys=True),
         S["refills"], S["player_deaths"], S["frame"]))
    log("finished: " + reason)
    plc.end_play()


def _xyz(value):
    try:
        coordinates = [float(value.x), float(value.y), float(value.z)]
        return coordinates if all(math.isfinite(part) for part in coordinates) else "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def _finite_number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else "UNKNOWN"
    except (TypeError, ValueError):
        return "UNKNOWN"


def frame_camera_context(world, pc, pawn, boss, frame_index):
    """Diagnostic framing estimate paired with a PNG; world occlusion stays explicitly unmeasured."""
    camera = next((item for item in pawn.get_components_by_class(unreal.CameraComponent)
                   if item.get_name() == "FollowCamera"), None) if pawn else None
    boss_in_frame = player_in_frame = camera_inside_boss_bounds = "UNKNOWN"
    try:
        if camera and pawn and boss:
            location = camera.get_world_location()
            rotation = camera.get_world_rotation()
            rotation_pair = (float(rotation.pitch), float(rotation.yaw))
            fov = float(camera.get_editor_property("field_of_view"))
            boss_in_frame = point_in_camera_frame(_xyz(location), rotation_pair, fov,
                                                  _xyz(boss.get_actor_location()))
            player_in_frame = point_in_camera_frame(_xyz(location), rotation_pair, fov,
                                                    _xyz(pawn.get_actor_location()))
            for component in boss.get_components_by_class(unreal.PrimitiveComponent):
                try:
                    bounds = component.get_bounds()
                    origin, extent = bounds.origin, bounds.box_extent
                    camera_inside_boss_bounds = point_in_bounds(_xyz(location), _xyz(origin), _xyz(extent))
                    if camera_inside_boss_bounds:
                        break
                except Exception:
                    continue
    except Exception:
        pass
    return {"schema": FRAME_CONTEXT_SCHEMA, "run": FIGHT_RUN,
            "frame_marker_id": "%s:frame:%05d" % (FIGHT_RUN, frame_index),
            "action_id": S["action_id"] or "None", "game_time_s": _finite_number(plc.game_time(world)),
            "camera_position": _xyz(camera.get_world_location()) if camera else "UNKNOWN",
            "player_position": _xyz(pawn.get_actor_location()) if pawn else "UNKNOWN",
            "boss_position": _xyz(boss.get_actor_location()) if boss else "UNKNOWN",
            "player_in_camera_frame_estimate": player_in_frame,
            "boss_in_camera_frame_estimate": boss_in_frame,
            "camera_inside_boss_component_bounds": camera_inside_boss_bounds,
            "world_occlusion": "UNMEASURED"}


def point_in_camera_frame(camera_position, pitch_yaw_degrees, horizontal_fov_degrees, point,
                          aspect_ratio=16.0 / 9.0):
    try:
        values = [float(value) for value in (*camera_position, *pitch_yaw_degrees, horizontal_fov_degrees,
                                              *point, aspect_ratio)]
        if not all(math.isfinite(value) for value in values):
            return None
        cx, cy, cz, pitch_degrees, yaw_degrees, fov, px, py, pz, aspect = values
        if not (0.0 < fov < 179.0 and aspect > 0.0):
            return None
        pitch, yaw = math.radians(pitch_degrees), math.radians(yaw_degrees)
        forward = (math.cos(pitch) * math.cos(yaw), math.cos(pitch) * math.sin(yaw), math.sin(pitch))
        right = (-math.sin(yaw), math.cos(yaw), 0.0)
        up = (-math.sin(pitch) * math.cos(yaw), -math.sin(pitch) * math.sin(yaw), math.cos(pitch))
        delta = (px - cx, py - cy, pz - cz)
        dot = lambda axis: sum(delta[index] * axis[index] for index in range(3))
        depth = dot(forward)
        if depth <= 0.0:
            return False
        tan_h = math.tan(math.radians(fov) / 2.0)
        tan_v = tan_h / aspect
        return abs(dot(right) / depth) <= tan_h and abs(dot(up) / depth) <= tan_v
    except (TypeError, ValueError, OverflowError):
        return None


def point_in_bounds(point, origin, extent):
    try:
        p, o, e = ([float(value) for value in values] for values in (point, origin, extent))
        if not all(math.isfinite(value) for value in p + o + e):
            return None
        return all(abs(p[index] - o[index]) <= abs(e[index]) for index in range(3))
    except (TypeError, ValueError, OverflowError):
        return None


def air_light_context(phase, world, pc, pawn, boss):
    cameras = pawn.get_components_by_class(unreal.CameraComponent) if pawn else []
    arms = pawn.get_components_by_class(unreal.SpringArmComponent) if pawn else []
    camera = next((item for item in cameras if item.get_name() == "FollowCamera"), cameras[0] if cameras else None)
    arm = next((item for item in arms if item.get_name() == "CameraBoom"), arms[0] if arms else None)
    try:
        distance = (pawn.get_actor_location() - boss.get_actor_location()).length()
    except Exception:
        distance = "UNKNOWN"
    try:
        arm_length = float(arm.get_editor_property("target_arm_length")) if arm else "UNKNOWN"
    except Exception:
        arm_length = "UNKNOWN"
    frame = S["frame"]
    row = {
        "run": FIGHT_RUN,
        "action_id": S["action_instance"],
        "action": "air_light",
        "phase": phase,
        "game_time_s": _finite_number(plc.game_time(world)),
        "player_boss_cm": _finite_number(distance),
        "player_position": _xyz(pawn.get_actor_location()) if pawn else "UNKNOWN",
        "boss_position": _xyz(boss.get_actor_location()) if boss else "UNKNOWN",
        "camera_position": _xyz(camera.get_world_location()) if camera else "UNKNOWN",
        "pivot_position": _xyz(arm.get_world_location()) if arm else "UNKNOWN",
        "arm_target_cm": _finite_number(arm_length),
        "frame_index": frame,
        "frame_marker_id": "%s:frame:%05d" % (FIGHT_RUN, frame),
    }
    log("AIR_LIGHT_CONTEXT " + json.dumps(row, sort_keys=True, allow_nan=False))


def apply_air_light_test_distance(pc, pawn, boss):
    raw = os.environ.get("AIR_LIGHT_START_DISTANCE_CM", "").strip()
    if not raw:
        return None
    distance = float(raw)
    if not math.isfinite(distance) or distance <= 0.0:
        raise RuntimeError("AIR_LIGHT_START_DISTANCE_CM must be a finite positive test position")
    boss_pos = boss.get_actor_location()
    player_pos = pawn.get_actor_location()
    dx, dy = player_pos.x - boss_pos.x, player_pos.y - boss_pos.y
    norm = math.hypot(dx, dy)
    if norm < 1.0:
        yaw = math.radians(boss.get_actor_rotation().yaw)
        dx, dy, norm = math.cos(yaw), math.sin(yaw), 1.0
    x, y = boss_pos.x + dx / norm * distance, boss_pos.y + dy / norm * distance
    face_yaw = math.degrees(math.atan2(boss_pos.y - y, boss_pos.x - x))
    plc.place_player(pc, pawn, (x, y, player_pos.z), face_yaw)
    actual = math.hypot(x - boss_pos.x, y - boss_pos.y)
    log("AIR_LIGHT_TEST_POSITION requested_cm=%.2f actual_cm=%.2f" % (distance, actual))
    return actual


def parry_watch_step(pawn, boss):
    """Press at observed montage-origin timing targets; count success only on player parry contact."""
    tracker = comp(boss, "RPGAttackTracker")
    sweep = comp(boss, "RPGBossLowSweep")
    parry = comp(pawn, "RPGPlayerParry")
    if not parry:
        if S["action"] == "parry_watch":
            log("PARRY_WATCH_RESULT outcome=missing_component tracker=%s sweep=%s parry=%s" % (bool(tracker), bool(sweep), bool(parry)))
            clear_action()
        elif not S["parry_missing_logged"]:
            log("PARRY_WATCH_AVAILABLE components_missing tracker=%s sweep=%s parry=%s" % (bool(tracker), bool(sweep), bool(parry)))
            S["parry_missing_logged"] = True
        return
    S["parry_missing_logged"] = False

    try: move = str(tracker.get_current_move()) if tracker else "None"
    except Exception: move = "UNKNOWN"
    try: instance = int(tracker.get_attack_instance()) if tracker else -1
    except Exception: instance = -1
    try: is_active = bool(tracker.is_active_window()) if tracker else False
    except Exception: is_active = False
    boss_montage = montage(boss)
    try:
        sweep_active = bool(sweep.is_blade_active()) if sweep else False
        sweep_count = int(sweep.get_sweep_count()) if sweep else 0
    except Exception:
        sweep_active, sweep_count = False, 0
    try:
        boss_montage, montage_position = plc.player_montage(boss)
        boss_montage = boss_montage or "None"
        montage_position = float(montage_position)
    except Exception:
        montage_position = -1.0
    try:
        tracker_position = float(tracker.get_position()) if tracker else -1.0
    except Exception:
        tracker_position = -1.0
    if (boss_montage != S.get("last_parry_diag_montage") or
            is_active != S.get("last_parry_diag_active")):
        log("PARRY_DIAG montage=%s tracker_move=%s tracker_instance=%d tracker_active=%s tracker_position=%.3f sweep_active=%s sweep_count=%d" %
            (boss_montage, move, instance, is_active, tracker_position, sweep_active, sweep_count))
        S["last_parry_diag_montage"] = boss_montage
        S["last_parry_diag_active"] = is_active
    active_window, observed_instance, window_source = parry_window_state(
        move, is_active, instance, boss_montage, sweep_active, sweep_count)
    current_montage_position = _number_or_unknown(montage_position)
    occurrence = parry_montage_occurrence(boss_montage, current_montage_position)
    contact_positions = PARRY_PACK_CONTACT_POSITIONS.get(move) or PARRY_PACK_CONTACT_POSITIONS.get(boss_montage, ())
    contact_samples = S.setdefault("parry_pack_contact_samples", set())
    if occurrence is not None and contact_positions:
        contact_key = ("tracker", instance) if instance >= 0 else ("montage", boss_montage, occurrence)
        for contact_index, contact_position in enumerate(contact_positions):
            sample_key = (contact_key, contact_index)
            if (sample_key not in contact_samples and
                    isinstance(current_montage_position, (int, float)) and
                    current_montage_position >= contact_position):
                contact_samples.add(sample_key)
                log("PACK_IMPACT_SAMPLE montage=%s move=%s instance=%d contact_index=%d target_position=%.3f sample_position=%.3f player_hp=%s player_status_tags=%s pack_impact_outcome=UNKNOWN reason=pack_blueprint_outcome_not_exposed_to_driver" %
                    (boss_montage, move, instance, contact_index + 1, contact_position,
                     current_montage_position, _parry_number(attr(pawn, "Attribute.Health")),
                     pack_status_snapshot(pawn)))
    pending = S.get("parry_watch_pending")
    if pending:
        current = int(parry.get_parried_count())
        delta = current - pending["parried_before"]
        sweep_current = int(sweep.get_parried_count()) if sweep else 0
        if delta == 1:
            S["counts"]["parry_contact"] = S["counts"].get("parry_contact", 0) + 1
            S["parry_capture"] = {"instance": pending["instance"],
                                   "contact_time": S["fight_time"], "captured": set(), "pawn": pawn,
                                   "recoil_seen": False}
            log("PARRY_CONTACT instance=%d move=%s source=%s t=%.3f parried_before=%d parried_after=%d parried_delta=%d press_count=%d sweep_parried_before=%d sweep_parried_after=%d boss_montage=%s" %
                (pending["instance"], pending["move"], pending["source"], S["fight_time"],
                 pending["parried_before"], current, delta, pending["press_count_after"],
                 pending["sweep_parried_before"], sweep_current, montage(boss)))
            log("PARRY_BLENDABLE at_contact %s" % camera_blendables(pawn))
            parry_feedback_step(boss)
            S["parry_watch_pending"] = None
            clear_action()
            return
        if delta > 1:
            log("PARRY_RESULT instance=%d outcome=unexpected_parried_delta delta=%d" %
                (pending["instance"], delta))
            S["parry_watch_pending"] = None
            clear_action()
            return
        if (S["action_t"] >= PARRY_CONTACT_WATCH_SECONDS or
                (boss_montage != pending["boss_montage"] and S["action_t"] >= 0.12)):
            context = parry_result_context(pending, pawn, boss, S["fight_time"])
            log("PARRY_RESULT instance=%d outcome=no_contact parried_before=%d parried_after=%d %s" %
                (pending["instance"], pending["parried_before"], current, context))
            S["parry_watch_pending"] = None
            clear_action()
            return
        return

    target_position, target_source = parry_press_target(move, boss_montage)
    tracked_target = target_source == "tracker_move" and instance >= 0
    montage_target = target_source == "montage_name" and occurrence is not None
    if target_source == "log_only" and occurrence is not None:
        log_key = (boss_montage, occurrence)
        if log_key not in S["parry_montage_seen"]:
            S["parry_montage_seen"].add(log_key)
            log("PARRY_UNTRACKED_BOSS_HITTER montage=%s tracker_move=%s tracker_active=%s montage_position=%.3f action=log_only reason=multiple_contact_points" %
                (boss_montage, move, is_active, float(montage_position)))
    observation_key = ("tracker", instance) if tracked_target else (("montage", boss_montage, occurrence) if montage_target else None)
    if observation_key is not None and observation_key not in S["parry_watch_observed"]:
        S["parry_watch_observed"].add(observation_key)
        window_start = window_end = -1.0
        if tracker:
            try:
                window_start = float(tracker.get_active_window_start_time())
                window_end = float(tracker.get_active_window_end_time())
            except Exception:
                pass
        attempt_instance = instance if tracked_target else int(S["parry_synthetic_instance"])
        if montage_target:
            S["parry_synthetic_instance"] += 1
        S["parry_watch_scheduled"][observation_key] = {
            "instance": attempt_instance, "move": move if tracked_target else "UNTRACKED",
            "source": "tracker" if tracked_target else "montage_target", "montage": boss_montage,
            "window_start": window_start, "window_end": window_end,
            "target_position": target_position,
            "tracker_window_seconds": window_end - window_start if window_end >= window_start >= 0.0 else "UNKNOWN",
            "target_source": target_source}
        log("PARRY_TARGET_SCHEDULED instance=%d move=%s source=%s montage=%s montage_position=%.3f press_target=%.3f target_source=%s tracker_active=%s" %
            (attempt_instance, S["parry_watch_scheduled"][observation_key]["move"],
             S["parry_watch_scheduled"][observation_key]["source"], boss_montage,
             float(montage_position), float(target_position), target_source, is_active))
    for key, scheduled in list(S["parry_watch_scheduled"].items()):
        if scheduled["montage"] != boss_montage:
            S["parry_watch_scheduled"].pop(key, None)
    schedule = S["parry_watch_scheduled"].get(observation_key)
    if (schedule and isinstance(current_montage_position, (int, float)) and
            isinstance(schedule["target_position"], (int, float)) and
            current_montage_position >= schedule["target_position"] and
            S["action"] in (None, "parry_watch") and not S["held"] and
            observation_key not in S["parry_watch_seen"]):
        instance = schedule["instance"]
        move = schedule["move"]
        S["parry_watch_seen"].add(observation_key)
        S["parry_watch_scheduled"].pop(observation_key, None)
        opportunistic = S["action"] is None
        before = int(parry.get_parried_count())
        press_before = int(parry.get_press_count())
        sweep_before = int(sweep.get_parried_count()) if sweep else 0
        distance_cm, player_hp_before = parry_attempt_context(pawn, boss)
        attempt_time = float(S["fight_time"])
        try:
            parry_window_seconds = _number_or_unknown(_property(parry, "window_seconds"))
        except Exception:
            parry_window_seconds = "UNKNOWN"
        try:
            opened = bool(parry.press())
        except Exception as exc:
            opened = False
            log("PARRY_PRESS_ERROR instance=%d reason=%s" % (instance, exc))
        press_after = int(parry.get_press_count())
        log("PARRY_ATTEMPT instance=%d move=%s active=%s source=%s montage=%s sweep_active=%s sweep_count=%d position=%.3f opened=%s parried_before=%d press_count_before=%d press_count_after=%d sweep_parried_before=%d distance_cm=%s player_hp_before=%s parry_window_seconds=%s tracker_window_seconds=%s watch_limit_seconds=%.2f window_start=%.3f window_end=%.3f target_source=%s player_status_tags=%s pack_impact_outcome=UNKNOWN" %
            (instance, move, is_active, schedule["source"], boss_montage, sweep_active, sweep_count,
             float(montage_position), opened, before, press_before, press_after, sweep_before,
             _parry_number(distance_cm), _parry_number(player_hp_before),
             _parry_number(parry_window_seconds), _parry_position(schedule["tracker_window_seconds"]),
             PARRY_CONTACT_WATCH_SECONDS, schedule["window_start"], schedule["window_end"],
             schedule["target_source"], pack_status_snapshot(pawn)))
        if opened:
            S["parry_watch_pending"] = {"instance": instance, "move": move, "source": schedule["source"],
                                         "parried_before": before, "press_count_after": press_after,
                                         "sweep_parried_before": sweep_before,
                                         "distance_cm": distance_cm, "player_hp_before": player_hp_before,
                                         "attempt_time": attempt_time,
                                         "parry_window_seconds": parry_window_seconds,
                                         "tracker_window_seconds": schedule["tracker_window_seconds"],
                                         "watch_limit_seconds": PARRY_CONTACT_WATCH_SECONDS,
                                         "boss_montage": boss_montage}
            if opportunistic:
                S["action_count"] += 1
                S["action_id"] = action_id(FIGHT_RUN, S["action_count"])
                S["counts"]["parry_watch"] = S["counts"].get("parry_watch", 0) + 1
                log("ACTION parry_watch t=%.2f id=%s source=opportunistic" %
                    (S["fight_time"], S["action_id"]))
                S["action"] = "parry_watch"
                S["action_t"] = 0.0
            log("PARRY_BLENDABLE at_press %s" % camera_blendables(pawn))
        else:
            log("PARRY_RESULT instance=%d outcome=window_refused parried_before=%d" % (instance, before))
            clear_action()
        return

    if S["action_t"] >= PARRY_WATCH_SECONDS:
        slot_id = S.get("action_id") or "unassigned"
        if slot_id not in S["parry_timeout_action_ids"]:
            S["parry_timeout_action_ids"].add(slot_id)
            log("PARRY_WATCH_RESULT outcome=timeout_no_live_tracker_window slot=%s seconds=%.2f reason=no_known_timing_target" %
                (slot_id, S["action_t"]))
        clear_action()


def dodge_watch_step(pawn, boss, pc, distance_cm, player_hit_this_tick=False):
    """Dodge at witnessed boss-montage contacts and sample the real i-frame tag there."""
    if S["action"] == "dodge_watch":
        S["action_t"] += max(0.0, float(S.get("tick_dt", 0.0)))
        if DODGE in S["held"] and S["action_t"] >= DODGE_INPUT_HOLD_SECONDS:
            key(pc, DODGE, False)
        if S["action_t"] >= DODGE_ACTION_LOCK_SECONDS:
            clear_action()

    try:
        tracker = comp(boss, "RPGAttackTracker")
        move = str(tracker.get_current_move()) if tracker else "None"
    except Exception:
        move = "UNKNOWN"
    try:
        boss_montage, montage_position = plc.player_montage(boss)
        boss_montage = boss_montage or "None"
        montage_position = float(montage_position)
    except Exception:
        boss_montage, montage_position = "UNKNOWN", -1.0
    # Sample the read-only tag once per pending dodge per tick, independently
    # of contact timing, so the first observed false->true edge is measurable.
    tag_samples = {}
    for pending in list(S["dodge_watch_pending"]):
        tag_active = invulnerability_tag_active(pawn)
        tag_samples[pending["id"]] = tag_active
        previous = pending.get("iframe_last_state")
        if previous is False and tag_active is True and pending.get("iframe_rise_delay") is None:
            pending["iframe_rise_delay"] = max(0.0, float(S["fight_time"]) - pending["press_time"])
            log("DODGE_IFRAME_TAG_RISE id=%s montage=%s delay_since_press=%.3f press_position=%.3f observed_position=%.3f" %
                (pending["id"], pending["montage"], pending["iframe_rise_delay"],
                 pending["press_position"], montage_position))
        elif previous is None and tag_active is True and not pending.get("iframe_unknown_first_seen"):
            pending["iframe_unknown_first_seen"] = True
            log("DODGE_IFRAME_TAG_FIRST_SEEN id=%s montage=%s delay_since_press=%.3f prior_state=UNKNOWN position=%.3f" %
                (pending["id"], pending["montage"],
                 max(0.0, float(S["fight_time"]) - pending["press_time"]), montage_position))
        pending["iframe_last_state"] = tag_active

    occurrence = parry_montage_occurrence(boss_montage, montage_position)
    if occurrence is None:
        return
    playback_key = (boss_montage, occurrence)

    # A contact observation is sampled on the first driver tick at/after the
    # witnessed montage position. Keep the observation window short and bound
    # each result to the same montage playback.
    for pending in list(S["dodge_watch_pending"]):
        same_playback = pending["playback_key"] == playback_key
        position_matches_contact = (same_playback and
                                     montage_position >= pending["contact_position"])
        if not pending["contact_observed"] and position_matches_contact:
            tag_active = tag_samples.get(pending["id"])
            pending["contact_observed"] = True
            pending["contact_time"] = float(S["fight_time"])
            pending["i_frame_tag_active_at_contact"] = tag_active
            log("DODGE_ATTEMPT id=%s montage=%s press_position=%.3f target_contact_position=%.3f contact_sample_position=%.3f i_frame_tag_active_at_contact=%s distance_cm=%.1f source=%s" %
                (pending["id"], boss_montage, pending["press_position"],
                 pending["contact_position"], montage_position,
                 boolean_marker(tag_active), pending["distance_cm"], pending["source"]))
            if player_hit_this_tick and montage_position <= pending["contact_position"] + 0.12:
                pending["player_hit_followed"] = True
        elif (pending["contact_observed"] and player_hit_this_tick and same_playback and
              pending["contact_position"] - 0.12 <= montage_position <= pending["contact_position"] + 0.35):
            if not pending["player_hit_followed"]:
                pending["player_hit_followed"] = True
                log("DODGE_HIT_LINK id=%s montage=%s position=%.3f outcome=PLAYER_HIT_FOLLOWED" %
                    (pending["id"], boss_montage, montage_position))
        expired = (pending["contact_observed"] and
                   float(S["fight_time"]) - pending["contact_time"] >= DODGE_CONTACT_RESULT_SECONDS)
        interrupted = not same_playback
        if expired or interrupted:
            log("DODGE_RESULT id=%s montage=%s contact_observed=%s press_tag=%s iframe_rise_delay=%s i_frame_tag_active_at_contact=%s player_hit_followed=%s reason=%s" %
                (pending["id"], pending["montage"],
                 str(bool(pending["contact_observed"])).lower(),
                 boolean_marker(pending.get("iframe_press_state")),
                 "%.3f" % pending["iframe_rise_delay"] if pending.get("iframe_rise_delay") is not None else "UNKNOWN",
                 boolean_marker(pending.get("i_frame_tag_active_at_contact")),
                 str(bool(pending["player_hit_followed"])).lower(),
                 "contact_window_elapsed" if expired else "montage_replaced_before_contact" if not pending["contact_observed"] else "montage_replaced"))
            S["dodge_watch_pending"].remove(pending)

    if not dodge_target_allowed(boss_montage):
        return
    contact_position, press_position, source = dodge_target_for_montage(move, boss_montage, occurrence)
    if contact_position is None:
        return
    if playback_key not in S["dodge_watch_seen"]:
        S["dodge_watch_seen"].add(playback_key)
        S["dodge_watch_scheduled"][playback_key] = {
            "contact_position": contact_position, "press_position": press_position,
            "source": source, "move": move}
        log("DODGE_TARGET_SCHEDULED montage=%s move=%s occurrence=%d contact_position=%.3f press_target=%.3f source=%s" %
            (boss_montage, move, occurrence, contact_position, press_position, source))
    schedule = S["dodge_watch_scheduled"].get(playback_key)
    if schedule is None:
        return
    if montage_position >= schedule["contact_position"] and distance_cm > DODGE_ONLY_PLAYER_DISTANCE_CM:
        S["dodge_watch_scheduled"].pop(playback_key, None)
        log("DODGE_TARGET_SKIPPED montage=%s occurrence=%d reason=outside_200cm distance_cm=%.1f" %
            (boss_montage, occurrence, distance_cm))
        return
    if distance_cm > DODGE_ONLY_PLAYER_DISTANCE_CM:
        pawn.add_movement_input(pawn.get_actor_forward_vector(), 1.0, True)
        return
    if montage_position > schedule["contact_position"] + 0.02:
        S["dodge_watch_scheduled"].pop(playback_key, None)
        log("DODGE_TARGET_SKIPPED montage=%s occurrence=%d reason=press_window_missed position=%.3f target_contact=%.3f" %
            (boss_montage, occurrence, montage_position, schedule["contact_position"]))
        return
    if (montage_position < schedule["press_position"] or
            S["action"] is not None or DODGE in S["held"]):
        return

    S["dodge_attempt_count"] += 1
    attempt_id = "%s:dodge:%04d" % (FIGHT_RUN, S["dodge_attempt_count"])
    S["counts"]["dodge_attempt"] = S["counts"].get("dodge_attempt", 0) + 1
    press_tag_state = invulnerability_tag_active(pawn)
    key(pc, DODGE, True)
    S["action"] = "dodge_watch"
    S["action_t"] = 0.0
    S["action_id"] = attempt_id
    S["dodge_watch_scheduled"].pop(playback_key, None)
    S["dodge_watch_pending"].append({
        "id": attempt_id, "montage": boss_montage, "playback_key": playback_key,
        "press_position": montage_position, "contact_position": schedule["contact_position"],
        "distance_cm": distance_cm, "source": schedule["source"], "contact_observed": False,
        "contact_time": None, "i_frame_tag_active_at_contact": None,
        "press_time": float(S["fight_time"]), "iframe_press_state": press_tag_state,
        "iframe_last_state": press_tag_state, "iframe_rise_delay": None,
        "iframe_unknown_first_seen": False,
        "player_hit_followed": False})
    log("DODGE_PRESS id=%s montage=%s move=%s press_position=%.3f target_contact_position=%.3f target_press_position=%.3f distance_cm=%.1f source=%s" %
        (attempt_id, boss_montage, move, montage_position, schedule["contact_position"],
         schedule["press_position"], distance_cm, schedule["source"]))


def _property(item, name):
    try:
        return item.get_editor_property(name)
    except (AttributeError, RuntimeError):
        return getattr(item, name)


def camera_blendables(pawn):
    """Return the actual FollowCamera weighted blendables, or explicit read failure."""
    try:
        cameras = pawn.get_components_by_class(unreal.CameraComponent)
        camera = next((item for item in cameras if item.get_name() == "FollowCamera"), None)
        if camera is None:
            return "camera=missing"
        settings = _property(camera, "post_process_settings")
        weighted = _property(settings, "weighted_blendables")
        entries = _property(weighted, "array")
        values = []
        for entry in entries:
            material = _property(entry, "object")
            name = material.get_name() if material else "None"
            values.append("%s=%.3f" % (name, float(_property(entry, "weight"))))
        return "camera=%s count=%d weights=[%s]" % (camera.get_name(), len(values), ",".join(values))
    except Exception as exc:
        return "read_error=%s" % exc


def parry_feedback_step(boss):
    """Witness the recoil montage separately from the parry contact count."""
    capture_state = S.get("parry_capture")
    if boss is None or not capture_state or capture_state["recoil_seen"]:
        return
    active_montage = montage(boss)
    if "ParryRecoil" in active_montage:
        capture_state["recoil_seen"] = True
        log("PARRY_RECOIL instance=%d t=%.3f montage=%s" %
            (capture_state["instance"], S["fight_time"], active_montage))


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("driver error: " + traceback.format_exc())
        finish("exception")


def _tick(dt):
    S["elapsed"] += dt
    if S["phase"] == "start":
        if S["elapsed"] > 0.5:
            sel = os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()
            if sel:
                unreal.SystemLibrary.execute_console_command(None, "rpg.EncounterDefinition " + sel)
            tier2 = os.environ.get("ER_FIGHT_TIER2", "0") == "1"
            unreal.SystemLibrary.execute_console_command(None, "rpg.Art.Tier2 " + ("1" if tier2 else "0"))
            log("TIER2 enabled=%s" % tier2)
            route = "data" if sel else "legacy"
            log("RUN_PROVENANCE " + json.dumps(run_provenance(
                FIGHT_RUN, FIGHT_BUILD_ID, FIGHT_MAP_NAME, route, tier2, TOOL_SHA256),
                sort_keys=True, allow_nan=False))
            log("route=%s; player refilled below 35 HP by the boss RPGCombatDebug; boss health and AI untouched" % ("data " + sel if sel else "legacy"))
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            S.update(phase="wait", elapsed=0.0)
        return
    world, pc, pawn, boss = actors()
    if S["phase"] == "wait":
        if pawn and boss and S["elapsed"] > 6.0:
            plc.enter_combat(pawn)
            bl = boss.get_actor_location()
            setup_distance = (180.0 if FIGHT_DODGE_ONLY else
                              120.0 if (PARRY_ONLY_CONTROL or FIGHT_PARRY_ONLY) else 700.0)
            plc.place_player(pc, pawn, (bl.x + setup_distance, bl.y, bl.z), 180)
            S["boss_health_start"] = attr(boss, "Attribute.Health")
            S["boss_health_max_start"] = attr(boss, "Attribute.Health", True)
            S["boss_ai_controller_start"] = boss_ai_controller(boss)
            log("setup boss_hp=%s/%s player_hp=%s/%s player_boss_cm=%.1f" % (attr(boss, "Attribute.Health"), attr(boss, "Attribute.Health", True), attr(pawn, "Attribute.Health"), attr(pawn, "Attribute.Health", True), setup_distance))
            log("BOSS_BASELINE hp=%s max_hp=%s ai_controller=%s driver_mutations=0" %
                (S["boss_health_start"], S["boss_health_max_start"], S["boss_ai_controller_start"]))
            S.update(phase="draw", elapsed=0.0)
        elif S["elapsed"] > 30.0:
            finish("no player/boss within 30 s")
        return
    if S["phase"] == "draw":
        if 0.3 <= S["elapsed"] and R2 not in S["held"] and S["elapsed"] < 0.4:
            key(pc, R2, True)
        if S["elapsed"] >= 1.0 and R2 in S["held"]:
            key(pc, R2, False)
        if S["elapsed"] >= 3.5:
            unreal.SystemLibrary.execute_console_command(world, "slomo 0.5")
            log("FIGHT_START slomo=0.5 frames=%s fps=%.0f" % (FRAMES, FRAME_FPS))
            S.update(phase="fight", elapsed=0.0)
        return
    # fight: all timing below uses GAME time (capture stalls real time)
    g = plc.game_time(world)
    gdt = 0.0 if S["g_last"] is None else max(0.0, g - S["g_last"])
    S["g_last"] = g
    dt = gdt
    S["fight_time"] += dt
    S["tick_dt"] = dt
    capture(world)
    parry_feedback_step(boss)
    if boss is None or (attr(boss, "Attribute.Health") is not None and attr(boss, "Attribute.Health") <= 0.0):
        if not S["boss_dead"]:
            S["boss_dead"] = True
            S["dead_at"] = S["fight_time"]
            log("BOSS_DEAD at %.1f s" % S["fight_time"])
        if S["fight_time"] - S["dead_at"] > 5.0:
            finish("boss dead")
        return
    if S["fight_time"] > MAX_FIGHT_SECONDS:
        finish("time limit")
        return
    hp = attr(pawn, "Attribute.Health") if pawn is not None else None
    previous_hp = _number_or_unknown(S.get("last_player_hp"))
    current_hp = _number_or_unknown(hp)
    player_hit_this_tick = False
    if isinstance(previous_hp, (int, float)) and isinstance(current_hp, (int, float)):
        player_hit_this_tick = log_player_hit(pawn, boss, previous_hp, current_hp)
    S["last_player_hp"] = current_hp
    failure = player_failure(pawn, hp, S["fight_time"])
    if failure:
        if failure == "player dead":
            S["player_deaths"] += 1
            log("PLAYER_DEATH count=%d t=%.3f reason=player_dead" %
                (S["player_deaths"], S["fight_time"]))
        finish(failure)
        return
    if pawn is None:
        return
    hpmax = attr(pawn, "Attribute.Health", True)
    # The pack reports a 1e6 max for the player; the playable bar is 100-120, so refill below 35 HP.
    if hp is not None and hp < 35.0:
        if plc.boss_debug(boss):
            hp_before = hp
            plc.refill_player(boss)
            S["refills"] += 1
            hp_after = attr(pawn, "Attribute.Health")
            boss_hp = attr(boss, "Attribute.Health")
            log("PLAYER_REFILL count=%d t=%.3f hp_before=%s hp_after=%s boss_hp=%s" %
                (S["refills"], S["fight_time"], hp_before, hp_after, boss_hp))
    S["beat"] += dt
    if S["beat"] >= 2.0:
        S["beat"] = 0.0
        log("BEAT t=%.1f boss_hp=%s player_hp=%s boss_montage=%s player_montage=%s action=%s" % (
            S["fight_time"], attr(boss, "Attribute.Health"), hp, montage(boss), montage(pawn), S["action"]))
    dist = face(pc, pawn, boss)
    if PARRY_ONLY_CONTROL:
        # Control mode logs the invariant `press=0 attacks=0` through the shared range helper.
        parry_control_distance_step(pawn, boss, pc, dist, "control")
        return
    if FIGHT_PARRY_ONLY:
        dist = parry_control_distance_step(pawn, boss, pc, dist, "parry")
    if FIGHT_DODGE_ONLY:
        if dist > DODGE_ONLY_PLAYER_DISTANCE_CM:
            measured_dist = dist
            bl = boss.get_actor_location()
            plc.place_player(pc, pawn, (bl.x + DODGE_ONLY_PLAYER_DISTANCE_CM - 5.0, bl.y, bl.z), 180)
            dist = DODGE_ONLY_PLAYER_DISTANCE_CM - 5.0
            log("DODGE_RANGE_CLAMP t=%.2f measured_before_cm=%.1f player_boss_cm=%.1f limit_cm=%.1f" %
                (S["fight_time"], measured_dist, dist, DODGE_ONLY_PLAYER_DISTANCE_CM))
        dodge_watch_step(pawn, boss, pc, dist, player_hit_this_tick)
        return
    if S["action"] != "parry_watch":
        parry_watch_step(pawn, boss)
        if S["action"] == "parry_watch":
            return
    if S["action"] is None:
        if FIGHT_PARRY_ONLY:
            return
        if dist > 260.0:
            pawn.add_movement_input(pawn.get_actor_forward_vector(), 1.0, True)
            return
        name = CYCLE[S["cycle"] % len(CYCLE)]
        S["cycle"] += 1
        if name == "air_light":
            apply_air_light_test_distance(pc, pawn, boss)
            dist = face(pc, pawn, boss)
        S["action_count"] += 1
        S.update(action=name, action_t=0.0, action_id=action_id(FIGHT_RUN, S["action_count"]),
                 event=0, guard_armed_at=None)
        S["counts"][name] = S["counts"].get(name, 0) + 1
        if name == "air_light":
            S["air_light_count"] += 1
            S["action_instance"] = "%s:air_light:%04d" % (FIGHT_RUN, S["air_light_count"])
            air_light_context("start", world, pc, pawn, boss)
        log("ACTION %s t=%.2f id=%s dist=%.0f" %
            (name, S["fight_time"], S["action_id"], dist))
        return
    S["action_t"] += dt
    name = S["action"]
    if name == "guard":
        action = unreal.load_asset(BLOCK_ACTION)
        dodge = comp(pawn, "RPGDodgeTiming")
        if S.get("guard_armed_at") is None:
            # The pack's block reaction can arrive just after the scripted L1 hold.
            # Stop injecting at 2.5 s, but keep this action open for one more
            # game second so a real late contact can still trigger the R2 tap.
            if S["action_t"] <= 2.5:
                unreal.RPGInputTestUtils.inject_action(pc, action, unreal.Vector(1.0, 0.0, 0.0))
            if dodge and dodge.is_guard_counter_armed():
                S["guard_armed_at"] = S["action_t"]
                key(pc, R2, True)
                S["counts"]["counter"] = S["counts"].get("counter", 0) + 1
                log("COUNTER t=%.2f id=%s" % (S["fight_time"], S["action_id"]))
            elif S["action_t"] > 3.5:
                clear_action()
        else:
            if R2 in S["held"] and S["action_t"] - S["guard_armed_at"] >= 0.12:
                key(pc, R2, False)
            if S["action_t"] - S["guard_armed_at"] >= 1.6:
                clear_action()
        return
    if name == "parry_watch":
        parry_watch_step(pawn, boss)
        return
    events, length = ACTIONS[name]
    while S["event"] < len(events) and S["action_t"] >= events[S["event"]][0]:
        _, k, down = events[S["event"]]
        key(pc, k, down)
        S["event"] += 1
    if S["action_t"] >= length:
        if name == "air_light":
            air_light_context("end", world, pc, pawn, boss)
        release_all(pc)
        clear_action()


HANDLE = unreal.register_slate_post_tick_callback(tick)
log("driver registered parry_only=%s dodge_only=%s dodge_target=%s parry_only_control=%s run=%s" %
    (FIGHT_PARRY_ONLY, FIGHT_DODGE_ONLY, FIGHT_DODGE_TARGET, PARRY_ONLY_CONTROL, FIGHT_RUN))
