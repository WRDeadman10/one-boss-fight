"""Lead-run Ember timing and parry probes; Codex must not execute this PIE driver.

The TIMING arm runs each move with parry input disabled and reads phase positions
from the engine's LogRPGAttack records. The separate PARRY arm presses at the
C-1132-derived lead and accepts contact only through URPGPlayerParry's shared
NotifyParried counter. This bounded probe does not replace C-1132/C-1152.
"""
import json
import re
import time
from pathlib import Path
import unreal

LOG = "[EmberNotifyParity] "
MOVES = ("A1", "A3a", "A3b")
# Earliest Lead-observed PLAYER_HIT positions in C-1132 (montage-local seconds).
C1132_CONTACT_SECONDS = {"A1": 0.351, "A3a": 0.484, "A3b": 0.152}
C1132_PARRY_LEAD_SECONDS = 0.08
# C-1132's validated montage-origin press positions (hit position minus 0.08 s).
PARRY_PRESS_TARGET_SECONDS = {"A1": 0.27, "A3a": 0.42, "A3b": 0.10}
C1132_PARITY_TOLERANCE_SECONDS = 0.08
MAX_MOVE_SECONDS = {"A1": 1.6, "A3a": 1.2, "A3b": 1.8}
S = {"phase": "start", "elapsed": 0.0, "wake": 0.0, "finished": False,
     "rows": {}, "checks": [], "initial_timing_mode": None, "task": 0,
     "wait_started": None, "next_wait_heartbeat": 0.0, "result_emitted": False,
     "active_trial": None, "log_offsets": {}, "log_path": None,
     "log_error": None, "log_source_fresh": False,
     "pie_start_wall_time": None, "wake_started": None,
     "next_wake_heartbeat": 0.0}
HANDLE = None
TASKS = [(arm, enabled, move) for arm in ("timing", "parry")
         for enabled in (False, True) for move in MOVES]
WAIT_BOSS_TIMEOUT_SECONDS = 15.0
WAIT_HEARTBEAT_SECONDS = 2.0
WAIT_AWAKE_TIMEOUT_SECONDS = 30.0
ATTACK_LOG_MARKER = "LogRPGAttack:"


def log(message):
    unreal.log(LOG + str(message))


def check(name, passed, detail=""):
    S["checks"].append(bool(passed))
    log("CHECK %s %s %s" % ("PASS" if passed else "FAIL", name, detail))


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def component(actor, class_name):
    if actor is None:
        return None
    return next((item for item in actor.get_components_by_class(unreal.ActorComponent)
                 if item.get_class().get_name() == class_name), None)


def parts():
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((actor for actor in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character)
                 if actor.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return (component(boss, "RPGAttackTracker"), component(boss, "RPGBossEncounter"),
            component(boss, "RPGCombatDebug"), component(pawn, "RPGPlayerParry"), pawn, boss)


def front(pawn, boss):
    # A3b is a branch stage; keep the pawn inside its live 400 cm frontal gate.
    location = boss.get_actor_location() + boss.get_actor_forward_vector() * 180.0
    pawn.set_actor_location_and_rotation(
        unreal.Vector(location.x, location.y, boss.get_actor_location().z),
        unreal.Rotator(0, 0, 0), False, True)


def record_trial(arm, enabled, move):
    key = (arm, "on" if enabled else "off", move)
    return S["rows"].setdefault(key, {"phases": {}, "parry_contacts": [],
                                     "started": False, "ended": False,
                                     "natural_recovery_end": False})


def parse_abslog_argument(command_line):
    match = re.search(r"(?:^|\s)-abslog(?:=|\s+)(?:\"([^\"]+)\"|'([^']+)'|([^\s]+))", command_line, re.IGNORECASE)
    if not match:
        return None
    return next(value for value in match.groups() if value is not None).strip().strip('"\'')


def select_attack_log(command_line, saved_dir):
    """Prefer this process's -abslog target; Saved/Logs is fallback only."""
    explicit = parse_abslog_argument(command_line)
    if explicit:
        return Path(explicit)
    if re.search(r"(?:^|\s)-abslog(?:\s|=|$)", command_line, re.IGNORECASE):
        raise RuntimeError("-abslog is present but has no usable path")
    log_dir = Path(saved_dir) / "Logs"
    paths = sorted(log_dir.glob("*.log"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not paths:
        raise RuntimeError("-abslog absent and no project Saved/Logs file exists")
    return paths[0]


def baseline_attack_log():
    command_line = str(unreal.SystemLibrary.get_command_line())
    path = select_attack_log(command_line, unreal.Paths.project_saved_dir())
    if not path.is_file():
        raise RuntimeError("selected UE log does not exist: %s" % path)
    S["log_path"] = path
    S["log_offsets"] = {str(path): path.stat().st_size}


def validate_attack_log_freshness():
    path = S.get("log_path")
    started = S.get("pie_start_wall_time")
    if path is None or started is None:
        S["log_error"] = "log path or PIE start time missing"
        return False
    try:
        modified = path.stat().st_mtime
    except Exception as error:
        S["log_error"] = "cannot stat selected log: %s" % error
        return False
    if modified < started:
        S["log_error"] = "selected log mtime %.3f predates PIE start %.3f: %s" % (modified, started, path)
        return False
    S["log_source_fresh"] = True
    return True


def parse_attack_line(line, trial):
    """Accumulate transition values from native LogRPGAttack messages only."""
    arm, label, move = trial
    if arm != "timing" or ATTACK_LOG_MARKER not in line:
        return
    if "attack %s " % move not in line:
        return
    row = record_trial(arm, label == "on", move)
    if re.search(r"attack %s instance \d+ begins \(" % re.escape(move), line):
        row["started"] = True
        return
    events = (
        ("Committed", r"attack %s committed at ([0-9]+(?:\.[0-9]+)?) s" % re.escape(move)),
        ("Active", r"attack %s active window opens at ([0-9]+(?:\.[0-9]+)?) s" % re.escape(move)),
        ("Recovery", r"attack %s recovery from ([0-9]+(?:\.[0-9]+)?) s" % re.escape(move)),
    )
    for phase, pattern in events:
        match = re.search(pattern, line)
        if match:
            row["started"] = True
            row["phases"].setdefault(phase, float(match.group(1)))
            log("LOG_TRANSITION arm=timing mode=%s move=%s phase=%s pos=%s" %
                (label, move, phase, match.group(1)))
            return
    ended = re.search(
        r"attack %s instance \d+ ended \(([^)]*)\) at ([0-9]+(?:\.[0-9]+)?) s, phase was ([A-Za-z]+)" % re.escape(move), line)
    if ended:
        reason, position, phase_before_end = ended.groups()
        row["ended"] = True
        row["phases"].setdefault("Complete", float(position))
        row["natural_recovery_end"] = phase_before_end == "Recovery"
        row["end_reason"] = reason
        log("LOG_TRANSITION arm=timing mode=%s move=%s phase=Complete pos=%s prior=%s reason=%s" %
            (label, move, position, phase_before_end, reason))


def tail_attack_log():
    path = S.get("log_path")
    if path is None:
        return
    key = str(path)
    try:
        size = path.stat().st_size
        offset = S["log_offsets"].get(key, 0)
        if size < offset:
            offset = 0
        with path.open("r", encoding="utf-8", errors="replace") as stream:
            stream.seek(offset)
            new_text = stream.read()
            S["log_offsets"][key] = stream.tell()
        trial = S.get("active_trial")
        if trial:
            for line in new_text.splitlines():
                parse_attack_line(line, trial)
    except Exception as error:
        S["log_error"] = repr(error)


def set_timing_mode(tracker, enabled):
    tracker.set_use_montage_notify_timings_for_test(bool(enabled))
    return bool(tracker.get_use_montage_notify_timings_for_test())


def run_one(arm, enabled, move, tracker, debug, parry, pawn, boss):
    label = "on" if enabled else "off"
    row = record_trial(arm, enabled, move)
    S["active_trial"] = (arm, label, move)
    actual = set_timing_mode(tracker, enabled)
    check("%s %s %s timing flag readback" % (arm, label, move), actual == enabled, "readback=%s" % actual)
    front(pawn, boss)
    debug.debug_set_boss_health_fraction(1.0)
    debug.debug_refill_player()
    before_parries = parry.get_parried_count() if parry else -1
    if not tracker.play_move_montage_for_test(move):
        check("%s %s %s montage starts" % (arm, label, move), False, "PlayMoveMontageForTest refused")
        S["active_trial"] = None
        return
    log("MOVE_BEGIN arm=%s mode=%s move=%s" % (arm, label, move))
    parry_sent = False
    limit = MAX_MOVE_SECONDS[move]
    started_at = S["elapsed"]
    while S["elapsed"] - started_at <= limit:
        tail_attack_log()
        position = float(tracker.get_position())
        if arm == "timing" and row["ended"]:
            break

        if arm == "parry" and not parry_sent and position >= PARRY_PRESS_TARGET_SECONDS[move]:
            press_before = int(parry.get_press_count()) if parry else -1
            parry_sent = bool(parry and parry.press())
            press_after = int(parry.get_press_count()) if parry else -1
            log("PARRY_PRESS arm=parry mode=%s move=%s pos=%.4f opened=%s press_before=%d press_after=%d target=%.3f lead=%.3f" % (
                label, move, position, parry_sent, press_before, press_after,
                PARRY_PRESS_TARGET_SECONDS[move], C1132_PARRY_LEAD_SECONDS))

        # ParriedCount increments only inside the shared NotifyParried route.
        if arm == "parry" and parry and parry.get_parried_count() > before_parries:
            contact_position = float(tracker.get_position())
            after_parries = int(parry.get_parried_count())
            row["parry_contacts"].append(contact_position)
            row["parry_counter_delta"] = after_parries - before_parries
            log("PARRY_CONTACT arm=parry mode=%s move=%s pos=%.4f source=URPGPlayerParry.NotifyParried counter=GetParriedCount before=%d after=%d delta=%d" % (
                label, move, contact_position, before_parries, after_parries, row["parry_counter_delta"]))
            break
        yield 0.0

    tail_attack_log()
    S["active_trial"] = None
    if arm == "timing":
        check("%s %s %s natural recovery end" % (arm, label, move),
              row["started"] and row["ended"] and row["natural_recovery_end"],
              "phases=%s end_reason=%s log_error=%s" %
              (json.dumps(row["phases"], sort_keys=True), row.get("end_reason"), S.get("log_error")))
    else:
        check("%s %s %s NotifyParried contact" % (arm, label, move), bool(row["parry_contacts"]),
              "contacts=%s press_opened=%s parried_counter_delta=%s" %
              (json.dumps(row["parry_contacts"]), parry_sent, row.get("parry_counter_delta", 0)))
        check("%s %s %s shared counter increments once" % (arm, label, move),
              row.get("parry_counter_delta") == 1,
              "delta=%s" % row.get("parry_counter_delta", 0))


def warmup_move(tracker, debug, pawn, boss):
    """Consume the first-play hitch on an unmeasured, parry-free A1 run."""
    enabled = bool(S["initial_timing_mode"])
    label = "on" if enabled else "off"
    row = record_trial("timing", enabled, "A1")
    key = ("timing", label, "A1")
    S["active_trial"] = ("timing", label, "A1")
    set_timing_mode(tracker, enabled)
    front(pawn, boss)
    debug.debug_set_boss_health_fraction(1.0)
    debug.debug_refill_player()
    log("WARMUP_BEGIN move=A1 mode=%s measured=false parry=disabled" % label)
    if not tracker.play_move_montage_for_test("A1"):
        check("unmeasured A1 warm-up starts", False, "PlayMoveMontageForTest refused")
        S["active_trial"] = None
        S["rows"].pop(key, None)
        return
    started_at = S["elapsed"]
    while S["elapsed"] - started_at <= MAX_MOVE_SECONDS["A1"]:
        tail_attack_log()
        if row["ended"]:
            break
        yield 0.0
    tail_attack_log()
    S["active_trial"] = None
    check("unmeasured A1 warm-up reaches Recovery end",
          row["started"] and row["ended"] and row["natural_recovery_end"],
          "phases=%s end_reason=%s" % (json.dumps(row["phases"], sort_keys=True), row.get("end_reason")))
    S["rows"].pop(key, None)


def compare_results():
    for move in MOVES:
        off = S["rows"].get(("timing", "off", move), {})
        on = S["rows"].get(("timing", "on", move), {})
        for phase in ("Committed", "Active", "Recovery", "Complete"):
            off_value = off.get("phases", {}).get(phase)
            on_value = on.get("phases", {}).get(phase)
            ok = off_value is not None and on_value is not None and abs(off_value - on_value) <= C1132_PARITY_TOLERANCE_SECONDS
            check("%s %s parity" % (move, phase), ok,
                  "off=%s on=%s tolerance=%.3f" % (off_value, on_value, C1132_PARITY_TOLERANCE_SECONDS))
        for mode in ("off", "on"):
            row = S["rows"].get(("parry", mode, move), {})
            contacts = row.get("parry_contacts", [])
            within = any(abs(value - C1132_CONTACT_SECONDS[move]) <= C1132_PARITY_TOLERANCE_SECONDS for value in contacts)
            check("%s %s C-1132 contact" % (mode, move), within,
                  "observed=%s target=%.4f tolerance=%.3f" % (contacts, C1132_CONTACT_SECONDS[move], C1132_PARITY_TOLERANCE_SECONDS))
    emit_result()


def emit_result():
    if S["result_emitted"]:
        return
    S["result_emitted"] = True
    passed = bool(S["checks"]) and all(S["checks"])
    log("RESULT %s checks=%d/%d C1132_tolerance=%.3fs" % (
        "PASS" if passed else "FAIL", sum(S["checks"]), len(S["checks"]), C1132_PARITY_TOLERANCE_SECONDS))


def scenario():
    yield 2.0
    tracker, encounter, debug, parry, pawn, boss = parts()
    for name, value in (("tracker", tracker), ("encounter", encounter), ("debug", debug), ("parry", parry), ("pawn", pawn), ("boss", boss)):
        check("component %s exists" % name, value is not None)
    if any(value is None for value in (tracker, encounter, debug, parry, pawn, boss)):
        return
    S["initial_timing_mode"] = bool(tracker.get_use_montage_notify_timings_for_test())
    check("LogRPGAttack source log is fresh for this PIE run", validate_attack_log_freshness(),
          str(S.get("log_path") or S.get("log_error")))
    encounter.wake()
    encounter.hold_for_test(True)
    debug.debug_refill_player()
    S["wake_started"] = S["elapsed"]
    S["next_wake_heartbeat"] = S["elapsed"]
    while encounter.is_dormant() or encounter.is_waking():
        if S["elapsed"] >= S["next_wake_heartbeat"]:
            log("WAKE_HEARTBEAT elapsed=%.1f dormant=%s waking=%s" %
                (S["elapsed"] - S["wake_started"], encounter.is_dormant(), encounter.is_waking()))
            S["next_wake_heartbeat"] = S["elapsed"] + WAIT_HEARTBEAT_SECONDS
        if S["elapsed"] - S["wake_started"] >= WAIT_AWAKE_TIMEOUT_SECONDS:
            check("encounter awake before first move", False, "wake timeout")
            return
        yield 0.1
    check("encounter awake before first move", True, "dormant=False waking=False")
    encounter.hold_for_test(True)
    yield from warmup_move(tracker, debug, pawn, boss)
    yield 0.35
    for arm, enabled, move in TASKS:
        yield from run_one(arm, enabled, move, tracker, debug, parry, pawn, boss)
        yield 0.35
    set_timing_mode(tracker, S["initial_timing_mode"])
    compare_results()


def finish():
    global HANDLE
    if S["finished"]:
        return
    S["finished"] = True
    tracker, encounter, debug, parry, pawn, boss = parts()
    if tracker is not None and S["initial_timing_mode"] is not None:
        set_timing_mode(tracker, S["initial_timing_mode"])
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    tail_attack_log()
    log("RECEIPT " + json.dumps({"rows": {"%s:%s:%s" % key: value for key, value in S["rows"].items()},
                                 "checks": len(S["checks"])}, sort_keys=True, separators=(",", ":")))
    emit_result()
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    log("finished: parity probe complete")


def tick(delta_seconds):
    try:
        S["elapsed"] += delta_seconds
        if S["phase"] == "start":
            if S["elapsed"] >= 0.5:
                try:
                    baseline_attack_log()
                except Exception as error:
                    S["log_error"] = repr(error)
                S["pie_start_wall_time"] = time.time()
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                S["phase"] = "wait"
                S["wait_started"] = S["elapsed"]
                S["next_wait_heartbeat"] = S["elapsed"]
            return
        if S["phase"] == "wait":
            current_parts = parts()
            if all(current_parts):
                S["phase"] = "run"
                return
            missing = [name for name, value in zip(("tracker", "encounter", "debug", "parry", "pawn", "boss"), current_parts) if value is None]
            if S["elapsed"] >= S["next_wait_heartbeat"]:
                log("WAIT_HEARTBEAT elapsed=%.1f missing=%s" % (S["elapsed"] - S["wait_started"], ",".join(missing)))
                S["next_wait_heartbeat"] = S["elapsed"] + WAIT_HEARTBEAT_SECONDS
            if S["elapsed"] - S["wait_started"] >= WAIT_BOSS_TIMEOUT_SECONDS:
                check("boss and probe components appear before timeout", False,
                      "elapsed=%.1f missing=%s" % (S["elapsed"] - S["wait_started"], ",".join(missing)))
                finish()
            return
        if S["phase"] == "run":
            if S["elapsed"] < S["wake"]:
                return
            try:
                wait_seconds = next(GENERATOR)
                S["wake"] = S["elapsed"] + (float(wait_seconds) if wait_seconds else 0.0)
            except StopIteration:
                finish()
            except Exception as error:
                check("driver exception", False, repr(error))
                finish()
    except Exception as error:
        check("tick exception", False, repr(error))
        finish()


GENERATOR = scenario()
HANDLE = unreal.register_slate_post_tick_callback(tick)
