"""Lead-run Ember notify timing parity probe; Codex must not execute this PIE driver.

The timing-only gate reads phase positions from native LogRPGAttack records.
Pack parry uses its unchanged collision-trace windows and is not part of this
tracker-timing acceptance gate. This bounded probe does not replace C-1132/C-1152.
"""
import json
import math
import re
import time
from pathlib import Path
import unreal

LOG = "[EmberNotifyParity] "
MOVES = ("A1", "A3a", "A3b")
C1132_PARITY_TOLERANCE_SECONDS = 0.08
MAX_TRIAL_TICK_SECONDS = 0.1
MAX_HITCH_RETRIES = 3
MAX_MOVE_SECONDS = {"A1": 1.6, "A3a": 1.2, "A3b": 1.8}
S = {"phase": "start", "elapsed": 0.0, "wake": 0.0, "finished": False,
     "rows": {}, "checks": [], "initial_timing_mode": None, "task": 0,
     "wait_started": None, "next_wait_heartbeat": 0.0, "result_emitted": False,
     "active_trial": None, "log_offsets": {}, "log_path": None,
     "log_error": None, "log_source_fresh": False,
     "pie_start_wall_time": None, "wake_started": None,
     "next_wake_heartbeat": 0.0, "current_trial": None,
     "clean_rows": {}, "hitch_retries": [], "hitch_exhausted": []}
HANDLE = None
TASKS = [(enabled, move) for enabled in (False, True) for move in MOVES]
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
            component(boss, "RPGCombatDebug"), pawn, boss)


def front(pawn, boss, distance_cm=180.0):
    # A3b is a branch stage; keep the pawn inside its live 400 cm frontal gate.
    location = boss.get_actor_location() + boss.get_actor_forward_vector() * distance_cm
    pawn_location = unreal.Vector(location.x, location.y, boss.get_actor_location().z)
    yaw = math.degrees(math.atan2(
        boss.get_actor_location().y - pawn_location.y,
        boss.get_actor_location().x - pawn_location.x))
    pawn.set_actor_location_and_rotation(
        pawn_location, unreal.Rotator(0, yaw, 0), False, True)


def record_trial(enabled, move, attempt=1):
    key = ("timing", "on" if enabled else "off", move, attempt)
    return S["rows"].setdefault(key, {"phases": {}, "started": False,
                                     "ended": False, "natural_recovery_end": False,
                                     "hitch": False, "max_tick_delta": 0.0})


def note_trial_tick(delta_seconds):
    trial = S.get("current_trial")
    if trial is None:
        return
    delta = float(delta_seconds)
    row = record_trial(trial["enabled"], trial["move"], trial["attempt"])
    row["max_tick_delta"] = max(row["max_tick_delta"], delta)
    log("TRIAL_TICK mode=%s move=%s attempt=%d delta=%.6f" %
        (trial["label"], trial["move"], trial["attempt"], delta))
    if delta > MAX_TRIAL_TICK_SECONDS:
        row["hitch"] = True
        log("TRIAL_HITCH mode=%s move=%s attempt=%d delta=%.6f limit=%.3f" %
            (trial["label"], trial["move"], trial["attempt"], delta, MAX_TRIAL_TICK_SECONDS))


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
    arm, label, move, attempt = trial
    if arm != "timing" or ATTACK_LOG_MARKER not in line:
        return
    if "attack %s " % move not in line:
        return
    row = record_trial(label == "on", move, attempt)
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
        row["end_phase"] = phase_before_end
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


def run_attempt(enabled, move, attempt, tracker, debug, pawn, boss):
    label = "on" if enabled else "off"
    row = record_trial(enabled, move, attempt)
    actual = set_timing_mode(tracker, enabled)
    front(pawn, boss)
    debug.debug_set_boss_health_fraction(1.0)
    debug.debug_refill_player()
    S["current_trial"] = {"enabled": enabled, "label": label, "move": move, "attempt": attempt}
    S["active_trial"] = ("timing", label, move, attempt)
    if not tracker.play_move_montage_for_test(move):
        row["start_refused"] = True
        row["clean"] = False
        row["timing_flag_ok"] = actual == enabled
        row["completion_ok"] = False
        S["current_trial"] = None
        S["active_trial"] = None
        log("TRIAL_RECEIPT mode=%s move=%s attempt=%d outcome=START_REFUSED max_delta=0.000000" %
            (label, move, attempt))
        return row, actual
    log("MOVE_BEGIN arm=timing mode=%s move=%s attempt=%d" % (label, move, attempt))
    limit = MAX_MOVE_SECONDS[move]
    started_at = S["elapsed"]
    while S["elapsed"] - started_at <= limit:
        tail_attack_log()
        if row["ended"]:
            break
        yield 0.0

    tail_attack_log()
    S["current_trial"] = None
    S["active_trial"] = None
    row["clean"] = not row["hitch"] and row["started"] and row["ended"]
    row["timing_flag_ok"] = actual == enabled
    row["completion_ok"] = row["started"] and row["ended"] and (row["natural_recovery_end"] or
        (move == "A3a" and row.get("end_reason") == "montage stopped" and row.get("end_phase") == "Active"))
    log("TRIAL_RECEIPT mode=%s move=%s attempt=%d outcome=%s max_delta=%.6f started=%s ended=%s" %
        (label, move, attempt, "HITCH" if row["hitch"] else ("CLEAN" if row["ended"] else "INCOMPLETE"),
         row["max_tick_delta"], row["started"], row["ended"]))
    return row, actual


def run_one(enabled, move, tracker, debug, pawn, boss):
    label = "on" if enabled else "off"
    final_row = None
    for attempt in range(1, MAX_HITCH_RETRIES + 2):
        row, actual = yield from run_attempt(enabled, move, attempt, tracker, debug, pawn, boss)
        if row["hitch"]:
            if attempt <= MAX_HITCH_RETRIES:
                retry = {"mode": label, "move": move, "hitch_attempt": attempt,
                         "retry_attempt": attempt + 1, "max_tick_delta": row["max_tick_delta"]}
                S["hitch_retries"].append(retry)
                log("HITCH_RETRY mode=%s move=%s hitch_attempt=%d retry_attempt=%d max_delta=%.6f" %
                    (label, move, attempt, attempt + 1, row["max_tick_delta"]))
                yield 0.35
                continue
            exhausted = {"mode": label, "move": move, "attempts": attempt,
                         "max_tick_delta": row["max_tick_delta"]}
            S["hitch_exhausted"].append(exhausted)
            log("HITCH_RETRY_EXHAUSTED mode=%s move=%s attempts=%d max_delta=%.6f" %
                (label, move, attempt, row["max_tick_delta"]))
            break
        if not row["clean"]:
            final_row = row
            S["clean_rows"][(label, move)] = None
            check("timing %s %s has a complete clean trial" % (label, move), False,
                  "start_refused=%s started=%s ended=%s" %
                  (row.get("start_refused", False), row["started"], row["ended"]))
            break
        final_row = row
        S["clean_rows"][(label, move)] = row
        check("timing %s %s clean-trial flag readback" % (label, move), row["timing_flag_ok"],
              "readback_matches=%s" % row["timing_flag_ok"])
        check("timing %s %s natural recovery end" % (label, move), row["completion_ok"],
              "phases=%s end_reason=%s end_phase=%s log_error=%s" %
              (json.dumps(row["phases"], sort_keys=True), row.get("end_reason"), row.get("end_phase"), S.get("log_error")))
        break
    if final_row is None:
        S["clean_rows"][(label, move)] = None
        check("timing %s %s has a clean trial" % (label, move), False,
              "HITCH_RETRY_EXHAUSTED attempts=%d" % (MAX_HITCH_RETRIES + 1))


def warmup_move(tracker, debug, pawn, boss):
    """Consume the first-play hitch on an unmeasured A1 timing run."""
    enabled = bool(S["initial_timing_mode"])
    label = "on" if enabled else "off"
    row = record_trial(enabled, "A1")
    key = ("timing", label, "A1", 1)
    S["active_trial"] = ("timing", label, "A1", 1)
    set_timing_mode(tracker, enabled)
    front(pawn, boss)
    debug.debug_set_boss_health_fraction(1.0)
    debug.debug_refill_player()
    log("WARMUP_BEGIN move=A1 mode=%s measured=false" % label)
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
        off = S["clean_rows"].get(("off", move))
        on = S["clean_rows"].get(("on", move))
        if off is None or on is None:
            log("INFO %s parity skipped: clean trial unavailable (off=%s on=%s)" %
                (move, off is not None, on is not None))
            continue
        for phase in ("Committed", "Active", "Recovery"):
            if (move == "A3a" and phase == "Recovery" and
                    off.get("end_reason") == on.get("end_reason") == "montage stopped" and
                    off.get("end_phase") == on.get("end_phase") == "Active"):
                log("INFO A3a Recovery parity not applicable: matching montage stopped in Active")
                continue
            off_value = off.get("phases", {}).get(phase)
            on_value = on.get("phases", {}).get(phase)
            ok = off_value is not None and on_value is not None and abs(off_value - on_value) <= C1132_PARITY_TOLERANCE_SECONDS
            check("%s %s parity" % (move, phase), ok,
                  "off=%s on=%s tolerance=%.3f" % (off_value, on_value, C1132_PARITY_TOLERANCE_SECONDS))
        terminal = evaluate_terminal_parity(move, off, on)
        if terminal[0] == "INFO":
            log("INFO %s Complete parity skipped: %s" % (move, terminal[1]))
        else:
            check("%s Complete parity" % move, terminal[0] == "PASS", terminal[1])
    emit_result()


def evaluate_terminal_parity(move, off, on):
    """Compare terminal timestamps only when both arms ended for the same reason."""
    if not off.get("ended") or not on.get("ended"):
        return "INFO", "one or both arms did not end (off=%s on=%s)" % (off.get("ended"), on.get("ended"))
    off_reason, on_reason = off.get("end_reason"), on.get("end_reason")
    if not off_reason or off_reason != on_reason:
        return "INFO", "terminal reasons differ or are unavailable (off=%s on=%s)" % (off_reason, on_reason)
    off_end = off.get("phases", {}).get("Complete")
    on_end = on.get("phases", {}).get("Complete")
    if off_end is None or on_end is None:
        return "INFO", "matching reason=%s but terminal time unavailable" % off_reason
    delta = abs(off_end - on_end)
    return ("PASS" if delta <= C1132_PARITY_TOLERANCE_SECONDS else "FAIL",
            "reason=%s off=%s on=%s delta=%.3f tolerance=%.3f" %
            (off_reason, off_end, on_end, delta, C1132_PARITY_TOLERANCE_SECONDS))


def emit_result():
    if S["result_emitted"]:
        return
    S["result_emitted"] = True
    passed = bool(S["checks"]) and all(S["checks"])
    clean_count = sum(row is not None for row in S["clean_rows"].values())
    retries = json.dumps(S["hitch_retries"], sort_keys=True, separators=(",", ":"))
    exhausted = json.dumps(S["hitch_exhausted"], sort_keys=True, separators=(",", ":"))
    log("RESULT %s clean_trials=%d/6 hitch_retries=%d retry_log=%s exhausted=%s checks=%d/%d C1132_tolerance=%.3fs" % (
        "PASS" if passed else "FAIL", clean_count, len(S["hitch_retries"]), retries, exhausted,
        sum(S["checks"]), len(S["checks"]), C1132_PARITY_TOLERANCE_SECONDS))


def scenario():
    yield 2.0
    tracker, encounter, debug, pawn, boss = parts()
    for name, value in (("tracker", tracker), ("encounter", encounter), ("debug", debug), ("pawn", pawn), ("boss", boss)):
        check("component %s exists" % name, value is not None)
    if any(value is None for value in (tracker, encounter, debug, pawn, boss)):
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
    for enabled, move in TASKS:
        yield from run_one(enabled, move, tracker, debug, pawn, boss)
        yield 0.35
    set_timing_mode(tracker, S["initial_timing_mode"])
    compare_results()


def finish():
    global HANDLE
    if S["finished"]:
        return
    S["finished"] = True
    tracker, encounter, debug, pawn, boss = parts()
    if tracker is not None and S["initial_timing_mode"] is not None:
        set_timing_mode(tracker, S["initial_timing_mode"])
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    tail_attack_log()
    log("RECEIPT " + json.dumps({
        "attempts": {"%s:%s:%d" % (key[1], key[2], key[3]): value for key, value in S["rows"].items()},
        "clean_rows": {"%s:%s" % key: value for key, value in S["clean_rows"].items()},
        "hitch_retries": S["hitch_retries"], "hitch_exhausted": S["hitch_exhausted"],
        "checks": len(S["checks"])},
        sort_keys=True, separators=(",", ":")))
    emit_result()
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    log("finished: parity probe complete")


def tick(delta_seconds):
    try:
        S["elapsed"] += delta_seconds
        note_trial_tick(delta_seconds)
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
            missing = [name for name, value in zip(("tracker", "encounter", "debug", "pawn", "boss"), current_parts) if value is None]
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
