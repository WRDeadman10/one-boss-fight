"""BK-66..68 (C, implementer; X-1993): read-only verifier for one BK-56..60 runner receipt bundle.

Reads only the small text receipts the runner writes into its evidence folder (status.txt, failure_status.txt,
pie_exit.txt, lock_result.txt) and, if present, deferred_pie.log for a contradiction check. It never launches Unreal,
reads assets, touches locks or writes anything.

Outcomes (exit code):
  0  SUCCESS  - a complete, consistent success receipt: the live deferred route is proven by the runner's own checks.
  1  FAILURE  - a well-formed failure receipt: the run failed at a named stage; the live route is NOT proven.
  2  INVALID  - missing, malformed or contradictory receipts (for example success and failure both present, a
                failure claiming DEFERRED_PIE=PASS, or a success receipt next to a refusal marker in the PIE log).
A refusal marker never makes a route successful: only status.txt can, and only when every rule below holds.

BK-71..73 (X-1995): a purported SUCCESS also requires deferred_pie.log to prove a production selector decision on the
selected route (verify_pie_log). The marker order is derived from source, not from the runner's predicate:
  PACK_STYLE_READY (driver :113) < selected_route_initialized (RPGFrameworkBossCharacter.cpp:167, logged inside
  ActivateDeferredSelectionForTest via InitializeSelectedEncounterForTest, RPGPlayerMovesSubsystem.cpp:1245)
  < deferred_selected (RPGPlayerMovesSubsystem.cpp:1259) < DEFERRED_SELECTION (driver :479, after activate() returns)
  < SPAWN PASS (driver :279, a later tick's navigation check) < DEFERRED_TICK_MONITOR (driver :372)
  < DEFERRED_TICK_RESULT (driver :381/:387); every [CARD_DECISION] (RPGFrameworkBossCharacter.cpp:813, production Tick)
  lies after deferred_selected and before the result. Terminal outcomes that can carry a success: TimeCap with
  activeState=Active, or BossDefeated, and only with >= 1 decision. Succeeded is reachable only on the test route
  (RPGFrameworkBossCharacter.cpp:899-915, bTestInitialized), so on the selected route it is a contradiction.
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Stages the runner assigns before each step (run_bk56_60_deferred_selection.ps1, `$stage = ...`).
STAGES = (
    "lock acquisition", "focused offline contracts", "Development build", "DD27j-pinned native suite",
    "Sevarog Phase_1 prerequisite", "encounter author/readback", "deferred PIE",
    "Content asset delta verification", "success status",
)
PIE_OR_LATER = {"deferred PIE", "Content asset delta verification", "success status"}
EXPECTED_LOCKS = 2  # repo-root and Execution C-1155 locks

ZERO_EXITS = ("BUILD_EXIT", "SUITE_EXIT", "FOCUSED_CONTRACTS_EXIT", "PY_COMPILE_EXIT", "PIE_EXIT")
PASS_FIELDS = ("PHASE_PREREQUISITE", "ASSET_READBACK", "DEFERRED_PIE")
TRUE_FIELDS = ("PIE_ORDER_VALID", "HEALTH_BASELINE_AFTER_PACK_STYLE_READY", "TEST_START_APIS_ABSENT",
               "CONTENT_DELTA_ONLY_EXPECTED_ASSETS")
SUCCESS_FIELDS = set(ZERO_EXITS + PASS_FIELDS + TRUE_FIELDS) | {
    "SUITE_STARTED", "SUITE_PASSED", "SUITE_FAILED", "DD27J", "NO_MAP_OR_OTHER_CONTENT_SAVES"}
REFUSAL = re.compile(r"outcome=ActivationRefused|deferred selected-route activation refused|\[FrameworkEncounterAuthor\] REFUSED")


class ReceiptError(ValueError):
    pass


def parse_receipt(text, continuation_key=None):
    """KEY=VALUE lines. Duplicate keys are rejected. A line without '=' continues `continuation_key` (multi-line ERROR)."""
    fields, last = {}, None
    for raw in text.replace("﻿", "").splitlines():
        line = raw.rstrip("\r")
        if not line.strip():
            continue
        if "=" not in line:
            if continuation_key and last == continuation_key:
                fields[last] += "\n" + line
                continue
            raise ReceiptError("malformed line (no '='): %r" % line)
        key, value = line.split("=", 1)
        key = key.strip()
        if not re.fullmatch(r"[A-Z0-9_]+", key):
            raise ReceiptError("malformed key: %r" % key)
        if key in fields:
            raise ReceiptError("duplicate key: %s" % key)
        fields[key], last = value.strip(), key
    return fields


def as_int(fields, key, errors):
    value = fields.get(key)
    if value is None or not re.fullmatch(r"-?\d+", value):
        errors.append("%s must be an integer, got %r" % (key, value))
        return None
    return int(value)


def read(path):
    return path.read_text(encoding="utf-8-sig", errors="replace") if path.is_file() else None


def check_locks(folder, errors, expected=None):
    text = read(folder / "lock_result.txt")
    if text is None:
        errors.append("lock_result.txt is missing (the runner writes it in finally on every path)")
        return
    try:
        locks = parse_receipt(text)
    except ReceiptError as error:
        errors.append("lock_result.txt: %s" % error)
        return
    count = as_int(locks, "LOCKS_RELEASED", errors)
    if count is None:
        return
    if expected is not None and count != expected:
        errors.append("LOCKS_RELEASED must be %d for a success receipt, got %d" % (expected, count))
    elif not 0 <= count <= EXPECTED_LOCKS:
        errors.append("LOCKS_RELEASED out of range 0..%d: %d" % (EXPECTED_LOCKS, count))


def pie_exit_file(folder, errors):
    text = read(folder / "pie_exit.txt")
    if text is None:
        return None
    try:
        fields = parse_receipt(text)
    except ReceiptError as error:
        errors.append("pie_exit.txt: %s" % error)
        return None
    return as_int(fields, "PIE_EXIT", errors)


# --- BK-71..73: deferred PIE log cross-check for a purported success -------------------------------------------
SINGLE_MARKERS = (
    ("PACK_STYLE_READY", re.compile(r"\[SevarogLive\] PACK_STYLE_READY ")),
    ("selected_route_initialized", re.compile(r"\[FrameworkProof\] selected_route_initialized route=data profile=\S+ generation=\d+ targetHealthAfterPackStyle=[0-9.]+ testStartApis=0")),
    ("deferred_selected", re.compile(r"\[EncounterActivation\] deferred_selected route=data definition=(\S+) hash=([0-9a-f]+) ")),
    ("DEFERRED_SELECTION", re.compile(r"\[SevarogLive\] DEFERRED_SELECTION route=framework definition=(\S+) hash=([0-9a-f]+) .*test_start_calls=0")),
    ("SPAWN PASS", re.compile(r"\[SevarogLive\] SPAWN PASS ")),
    ("DEFERRED_TICK_MONITOR", re.compile(r"\[SevarogLive\] DEFERRED_TICK_MONITOR route=selected-framework-production-tick selector_trigger=none test_start_calls=0 saves=0 ")),
    ("DEFERRED_TICK_RESULT", re.compile(r"\[SevarogLive\] DEFERRED_TICK_RESULT route=selected-framework-production-tick outcome=(\w+)")),
)
CARD_DECISION = re.compile(r"\[CARD_DECISION\] seq=(\d+) attack=\d+ card=(\S+) score=\S+ rangeCm=\S+ phase=(\S+)")
DECISION_TRACE = re.compile(r"\[FrameworkProof\] decision attack=\d+ chosen=(\S+) .* seq=(\d+)")
TEST_START_EVIDENCE = re.compile(r"autonomous_test_selection|\[SevarogLive\] COMBO_START|\[SevarogLive\] CARD accepted move=|PHASE2_PROBE|combo_test_start")
SAVE_EVIDENCE = re.compile(r"saves=(?!0\b)\d+|LogSavePackage|Saving package")
SUCCESS_OUTCOMES = {"TimeCap", "BossDefeated"}


def normalize_asset_path(path):
    """'/Game/A/B.B' and '/Game/A/B' name the same asset."""
    return path.split(".", 1)[0].rstrip("/")


def verify_pie_log(log_text):
    """Errors for a deferred PIE log that is offered as proof of a selected-route production decision."""
    errors = []
    lines = log_text.replace("\x00", "").splitlines()
    found = {}
    for name, pattern in SINGLE_MARKERS:
        hits = [(i, pattern.search(line)) for i, line in enumerate(lines) if pattern.search(line)]
        if not hits:
            errors.append("missing marker: %s" % name)
        elif len(hits) > 1:
            errors.append("duplicate marker: %s (%d times)" % (name, len(hits)))
        else:
            found[name] = hits[0]
    order = [name for name, _ in SINGLE_MARKERS if name in found]
    for earlier, later in zip(order, order[1:]):
        if found[earlier][0] >= found[later][0]:
            errors.append("out-of-order markers: %s must precede %s" % (earlier, later))
    if "deferred_selected" in found and "DEFERRED_SELECTION" in found:
        native, driver = found["deferred_selected"][1], found["DEFERRED_SELECTION"][1]
        if normalize_asset_path(native.group(1)) != normalize_asset_path(driver.group(1)):
            errors.append("route identity mismatch: definition %s vs %s" % (native.group(1), driver.group(1)))
        if native.group(2) != driver.group(2):
            errors.append("route identity mismatch: hash %s vs %s" % (native.group(2), driver.group(2)))
    result_line = lines[found["DEFERRED_TICK_RESULT"][0]] if "DEFERRED_TICK_RESULT" in found else ""
    outcome = found["DEFERRED_TICK_RESULT"][1].group(1) if "DEFERRED_TICK_RESULT" in found else None
    if outcome is not None:
        if outcome == "Succeeded":
            errors.append("contradiction: outcome=Succeeded is reachable only on the test route (bTestInitialized)")
        elif outcome not in SUCCESS_OUTCOMES:
            errors.append("terminal outcome %s cannot prove a selected-route success" % outcome)
        if outcome == "TimeCap" and "activeState=Active" not in result_line:
            errors.append("TimeCap result must report activeState=Active")
        if not re.search(r"saves=0\b", result_line):
            errors.append("result marker must carry saves=0")
    decisions = [(i, m) for i, line in enumerate(lines) for m in [CARD_DECISION.search(line)] if m]
    traces = {(m.group(2), m.group(1)) for line in lines for m in [DECISION_TRACE.search(line)] if m}
    start = found["deferred_selected"][0] if "deferred_selected" in found else None
    end = found["DEFERRED_TICK_RESULT"][0] if "DEFERRED_TICK_RESULT" in found else None
    if not decisions:
        errors.append("no production selector decision ([CARD_DECISION]) on the selected route")
    seqs = []
    for index, match in decisions:
        if start is not None and index < start:
            errors.append("decision seq=%s precedes deferred_selected (not on the selected route)" % match.group(1))
        if end is not None and index > end:
            errors.append("decision seq=%s follows the terminal result" % match.group(1))
        if (match.group(1), match.group(2)) not in traces:
            errors.append("decision seq=%s card=%s has no matching [FrameworkProof] decision trace" % (match.group(1), match.group(2)))
        seqs.append(int(match.group(1)))
    if len(seqs) != len(set(seqs)):
        errors.append("duplicate decision seq values: %s" % sorted(seqs))
    elif seqs != sorted(seqs):
        errors.append("decision seq values are not increasing: %s" % seqs)
    for line in lines:
        if TEST_START_EVIDENCE.search(line):
            errors.append("test-start evidence on the deferred route: %s" % line.strip()[:160])
            break
    for line in lines:
        if SAVE_EVIDENCE.search(line):
            errors.append("save evidence in the deferred PIE log: %s" % line.strip()[:160])
            break
    if REFUSAL.search(log_text):
        errors.append("contradiction: refusal marker in a log offered as success")
    return errors


def verify_success(folder, status_text, errors):
    try:
        fields = parse_receipt(status_text)
    except ReceiptError as error:
        errors.append("status.txt: %s" % error)
        return
    missing = sorted(SUCCESS_FIELDS - set(fields))
    extra = sorted(set(fields) - SUCCESS_FIELDS)
    if missing:
        errors.append("status.txt missing fields: %s" % ", ".join(missing))
    if extra:
        errors.append("status.txt unexpected fields: %s" % ", ".join(extra))
    for key in ZERO_EXITS:
        value = as_int(fields, key, errors) if key in fields else None
        if value not in (None, 0):
            errors.append("%s must be 0 for success, got %d" % (key, value))
    started = as_int(fields, "SUITE_STARTED", errors) if "SUITE_STARTED" in fields else None
    passed = as_int(fields, "SUITE_PASSED", errors) if "SUITE_PASSED" in fields else None
    failed = as_int(fields, "SUITE_FAILED", errors) if "SUITE_FAILED" in fields else None
    if started is not None and started <= 0:
        errors.append("SUITE_STARTED must be positive, got %d" % started)
    if None not in (started, passed) and passed != started:
        errors.append("SUITE_PASSED (%d) must equal SUITE_STARTED (%d)" % (passed, started))
    if failed not in (None, 0):
        errors.append("SUITE_FAILED must be 0, got %d" % failed)
    if "DD27J" in fields and not re.fullmatch(r"[0-9a-f]{64}", fields["DD27J"]):
        errors.append("DD27J must be a 64-hex manifest hash")
    for key in PASS_FIELDS:
        if key in fields and fields[key] != "PASS":
            errors.append("%s must be PASS, got %r" % (key, fields[key]))
    for key in TRUE_FIELDS:
        if key in fields and fields[key] != "True":
            errors.append("%s must be True, got %r" % (key, fields[key]))
    if "NO_MAP_OR_OTHER_CONTENT_SAVES" in fields and fields["NO_MAP_OR_OTHER_CONTENT_SAVES"] != "1":
        errors.append("NO_MAP_OR_OTHER_CONTENT_SAVES must be 1")
    file_exit = pie_exit_file(folder, errors)
    if file_exit is None and not any(e.startswith("pie_exit.txt") for e in errors):
        errors.append("pie_exit.txt is missing for a success receipt")
    elif file_exit is not None and fields.get("PIE_EXIT") not in (None, str(file_exit)):
        errors.append("pie_exit.txt PIE_EXIT=%d disagrees with status.txt PIE_EXIT=%s" % (file_exit, fields.get("PIE_EXIT")))
    log = read(folder / "deferred_pie.log")
    if log is None:
        errors.append("deferred_pie.log is missing: a success cannot be proven without the PIE log (fail closed)")
    else:
        errors.extend("deferred_pie.log: " + error for error in verify_pie_log(log))
    check_locks(folder, errors, expected=EXPECTED_LOCKS)


def verify_failure(folder, failure_text, errors):
    try:
        fields = parse_receipt(failure_text, continuation_key="ERROR")
    except ReceiptError as error:
        errors.append("failure_status.txt: %s" % error)
        return
    for key in ("STAGE", "ERROR", "PIE_EXIT"):
        if key not in fields:
            errors.append("failure_status.txt missing %s" % key)
    extra = sorted(set(fields) - {"STAGE", "ERROR", "PIE_EXIT"})
    if extra:
        errors.append("failure_status.txt unexpected fields (a failure cannot carry success claims): %s" % ", ".join(extra))
    if "DEFERRED_PIE" in fields or re.search(r"(?m)^DEFERRED_PIE=PASS", failure_text):
        errors.append("failure_status.txt must not claim DEFERRED_PIE=PASS")
    stage = fields.get("STAGE")
    if stage is not None and stage not in STAGES:
        errors.append("unknown STAGE %r" % stage)
    if "ERROR" in fields and not fields["ERROR"].strip():
        errors.append("ERROR must be non-empty")
    pie_exit = fields.get("PIE_EXIT")
    file_exit = pie_exit_file(folder, errors)
    # BK-211..213 (X-2060): the runner sets $pieExit and writes pie_exit.txt together, only in the deferred PIE stage
    # after the PIE process exits (run_bk56_60_deferred_selection.ps1:161-162), and the failure record echoes it
    # (:198). So a non-empty PIE_EXIT always has a matching pie_exit.txt, and a pre-PIE stage has neither.
    if pie_exit:
        if not re.fullmatch(r"-?\d+", pie_exit):
            errors.append("PIE_EXIT must be empty or an integer, got %r" % pie_exit)
        elif file_exit is not None and int(pie_exit) != file_exit:
            errors.append("pie_exit.txt PIE_EXIT=%d disagrees with failure_status.txt PIE_EXIT=%s" % (file_exit, pie_exit))
        elif file_exit is None and not any(e.startswith("pie_exit.txt") for e in errors):
            errors.append("failure_status.txt PIE_EXIT=%s has no pie_exit.txt receipt (the runner writes both together)"
                          % pie_exit)
        if stage is not None and stage not in PIE_OR_LATER:
            errors.append("pre-PIE failure stage %r must have an empty PIE_EXIT (PIE never ran), got %r" % (stage, pie_exit))
    elif stage in PIE_OR_LATER and file_exit is not None:
        errors.append("failure at %r has pie_exit.txt=%d but failure_status.txt PIE_EXIT is empty" % (stage, file_exit))
    if stage is not None and stage not in PIE_OR_LATER and file_exit is not None:
        errors.append("pre-PIE failure stage %r must not have a pie_exit.txt" % stage)
    check_locks(folder, errors)


def verify_bundle(folder):
    folder = Path(folder)
    errors = []
    status_text = read(folder / "status.txt")
    failure_text = read(folder / "failure_status.txt")
    if status_text is not None and failure_text is not None:
        errors.append("contradiction: both status.txt (success) and failure_status.txt are present")
        return {"folder": str(folder), "outcome": "INVALID", "live_route": "NOT_PROVEN", "errors": errors}
    if status_text is None and failure_text is None:
        errors.append("neither status.txt nor failure_status.txt is present")
        return {"folder": str(folder), "outcome": "INVALID", "live_route": "NOT_PROVEN", "errors": errors}
    if status_text is not None:
        verify_success(folder, status_text, errors)
        outcome = "INVALID" if errors else "SUCCESS"
    else:
        verify_failure(folder, failure_text, errors)
        outcome = "INVALID" if errors else "FAILURE"
    return {"folder": str(folder), "outcome": outcome,
            "live_route": "PASS" if outcome == "SUCCESS" else "NOT_PROVEN", "errors": errors}


EXIT_CODES = {"SUCCESS": 0, "FAILURE": 1, "INVALID": 2}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("folder", help="BK-56..60 runner evidence folder (Run_<timestamp>)")
    parser.add_argument("--json", action="store_true", help="print the result as JSON")
    args = parser.parse_args(argv)
    result = verify_bundle(args.folder)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("%s live_route=%s %s" % (result["outcome"], result["live_route"], result["folder"]))
        for error in result["errors"]:
            print("  - " + error)
    return EXIT_CODES[result["outcome"]]


if __name__ == "__main__":
    sys.exit(main())
