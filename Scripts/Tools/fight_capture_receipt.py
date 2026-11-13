"""Validate a single-run full-fight capture log and return machine-readable evidence."""
import json
import math
import re
import argparse
from pathlib import Path


PROVENANCE_PREFIX = "[FullFight] RUN_PROVENANCE "
SUMMARY_PREFIX = "[FullFight] RECEIPT_SUMMARY "
FRAME_RE = re.compile(r"\[FullFight\] FRAME (\d+) g=([0-9.eE+-]+) marker=(\S+) action=(\S+) action_id=(\S+)")
ACTION_RE = re.compile(r"\[FullFight\] ACTION (\S+) t=([0-9.eE+-]+) id=(\S+)")
COUNTER_RE = re.compile(r"\[FullFight\] COUNTER t=([0-9.eE+-]+) id=(\S+)")
REFILL_RE = re.compile(r"\[FullFight\] PLAYER_REFILL count=(\d+) t=([0-9.eE+-]+) hp_before=([0-9.eE+-]+) hp_after=([0-9.eE+-]+) boss_hp=(\S+)")
DEATH_RE = re.compile(r"\[FullFight\] PLAYER_DEATH count=(\d+) t=([0-9.eE+-]+) reason=(.+)")
BOSS_DEAD_RE = re.compile(r"\[FullFight\] BOSS_DEAD at ([0-9.eE+-]+) s")
ROUTE_RE = re.compile(r"\[EncounterActivation\] route=(legacy|data)\b")
FRAME_CONTEXT_SCHEMA = 1
FINISH_RE = re.compile(r"\[FullFight\] finished: (.+)$")
CONTACT_RE = re.compile(r"\[FullFight\] PARRY_CONTACT instance=(\d+) move=(\S+) source=(\S+) t=([0-9.eE+-]+) parried_before=(\d+) parried_after=(\d+) parried_delta=(\d+) press_count=(\d+) sweep_parried_before=(\d+) sweep_parried_after=(\d+) boss_montage=(\S+)")
PARRY_DIAG_RE = re.compile(r"\[FullFight\] PARRY_DIAG montage=(\S+) tracker_move=(\S+) tracker_instance=(\d+) tracker_active=(true|false) tracker_position=([0-9.eE+-]+) sweep_active=(true|false) sweep_count=(\d+)")
PARRY_TIMEOUT_RE = re.compile(r"\[FullFight\] PARRY_WATCH_RESULT outcome=timeout_no_live_(?:a4|tracker_window) slot=(\S+) seconds=([0-9.eE+-]+)")
PARRY_ATTEMPT_RE = re.compile(r"\[FullFight\] PARRY_ATTEMPT instance=(\d+) move=(\S+) active=(true|false) source=(\S+) montage=(\S+) sweep_active=(true|false) sweep_count=(\d+) position=([0-9.eE+-]+) opened=(true|false) parried_before=(\d+) press_count_before=(\d+) press_count_after=(\d+) sweep_parried_before=(\d+)")
PARRY_RESULT_RE = re.compile(r"\[FullFight\] PARRY_RESULT instance=(\d+) outcome=(\S+) (.+)")


def validate_parry_diagnostics(lines):
    transitions, timeouts, attempts, results = [], [], [], []
    previous_transition = None
    attempt_instances = set()
    previous_press_count = None
    timeout_slots = set()
    result_instances = set()
    for line in lines:
        if "[FullFight] PARRY_DIAG " in line:
            match = PARRY_DIAG_RE.search(line)
            if not match:
                raise ValueError("malformed PARRY_DIAG transition")
            montage, move, instance, active, position, sweep, sweep_count = match.groups()
            transition = (montage, active)
            if transition == previous_transition:
                raise ValueError("duplicate montage/active transition diagnostic")
            previous_transition = transition
            transitions.append({"montage": montage, "tracker_move": move, "tracker_instance": int(instance),
                                "tracker_active": active == "true", "tracker_position": _number(position, "tracker position"),
                                "sweep_active": sweep == "true", "sweep_count": int(sweep_count)})
        elif "outcome=timeout_no_live_a4" in line or "outcome=timeout_no_live_tracker_window" in line:
            match = PARRY_TIMEOUT_RE.search(line)
            if not match:
                raise ValueError("malformed parry timeout slot")
            slot, seconds = match.groups()
            if slot in timeout_slots:
                raise ValueError("duplicate timeout slot")
            timeout_slots.add(slot)
            timeouts.append({"slot": slot, "seconds": _number(seconds, "parry timeout seconds")})
        elif "[FullFight] PARRY_RESULT " in line:
            match = PARRY_RESULT_RE.search(line)
            if not match:
                raise ValueError("malformed PARRY_RESULT")
            instance, outcome, details = match.groups()
            if int(instance) not in attempt_instances:
                raise ValueError("parry result has no preceding attempt")
            if int(instance) in result_instances:
                raise ValueError("duplicate parry result instance")
            result_instances.add(int(instance))
            if outcome == "no_contact":
                values = re.fullmatch(r"parried_before=(\d+) parried_after=(\d+)", details)
                if not values:
                    raise ValueError("malformed PARRY_RESULT no_contact")
                before, after = map(int, values.groups())
                if before != after:
                    raise ValueError("no-contact parry counter changed")
                results.append({"instance": int(instance), "outcome": outcome,
                                "parried_before": before, "parried_after": after})
            elif outcome == "window_refused":
                refused = re.fullmatch(r"parried_before=(\d+)", details)
                if not refused:
                    raise ValueError("malformed PARRY_RESULT window_refused")
                results.append({"instance": int(instance), "outcome": outcome,
                                "parried_before": int(refused.group(1))})
            elif outcome == "unexpected_parried_delta":
                delta = re.fullmatch(r"delta=(\d+)", details)
                if not delta or int(delta.group(1)) <= 1:
                    raise ValueError("malformed PARRY_RESULT unexpected delta")
                results.append({"instance": int(instance), "outcome": outcome, "delta": int(delta.group(1))})
            elif outcome == "interrupted" and re.fullmatch(r"reason=.+", details):
                results.append({"instance": int(instance), "outcome": outcome,
                                "reason": details[len("reason="): ]})
            else:
                raise ValueError("malformed PARRY_RESULT outcome")
        elif "[FullFight] PARRY_ATTEMPT " in line:
            match = PARRY_ATTEMPT_RE.search(line)
            if not match:
                raise ValueError("malformed PARRY_ATTEMPT source receipt")
            (instance, move, active, source, montage, sweep_active, sweep_count, position,
             opened, before, press_before, press_after, sweep_before) = match.groups()
            if active != "true":
                raise ValueError("parry attempt is not tied to a live window")
            if source == "boss_montage_sweep" and not (
                    montage == "GS_Attack04_Montage" and sweep_active == "true"):
                raise ValueError("A4 montage fallback lacks a live sweep witness")
            if source not in ("tracker", "boss_montage_sweep"):
                raise ValueError("unknown parry window source")
            if min(int(instance), int(sweep_count), int(before), int(press_before),
                   int(press_after), int(sweep_before)) < 0:
                raise ValueError("negative parry attempt counter")
            _number(position, "parry attempt position")
            if int(instance) in attempt_instances:
                raise ValueError("duplicate parry attempt instance")
            if previous_press_count is not None and int(press_before) != previous_press_count:
                raise ValueError("parry attempt press counter sequence is discontinuous")
            if int(press_after) != int(press_before) + 1:
                raise ValueError("parry attempt press counter did not increment exactly once")
            attempt_instances.add(int(instance))
            previous_press_count = int(press_after)
            attempts.append({"instance": int(instance), "move": move, "source": source, "montage": montage,
                             "sweep_active": sweep_active == "true", "sweep_count": int(sweep_count),
                             "position": _number(position, "parry attempt position"),
                             "opened": opened == "true", "parried_before": int(before),
                             "press_count_before": int(press_before), "press_count_after": int(press_after),
                             "sweep_parried_before": int(sweep_before)})
    return {"transitions": transitions, "timeouts": timeouts, "attempts": attempts, "results": results}


def _json_marker(lines, prefix, name):
    records = [line.split(prefix, 1)[1] for line in lines if prefix in line]
    if len(records) != 1:
        raise ValueError("expected exactly one %s marker" % name)
    try:
        value = json.loads(records[0])
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("malformed %s JSON" % name) from exc
    if not isinstance(value, dict):
        raise ValueError("%s must be a JSON object" % name)
    return value


def _number(value, label):
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid numeric %s" % label) from exc
    if not math.isfinite(result):
        raise ValueError("non-finite %s" % label)
    return result


def parse_receipt(source):
    """Fail closed unless one full-fight run has internally consistent totals and identities."""
    lines = source.splitlines()
    provenance = _json_marker(lines, PROVENANCE_PREFIX, "RUN_PROVENANCE")
    summary = _json_marker(lines, SUMMARY_PREFIX, "RECEIPT_SUMMARY")
    summary_fields = ("run", "fight_seconds", "boss_dead", "reason", "action_counts", "player_refills",
                      "player_deaths", "frames", "boss_health_start", "boss_health_end",
                      "boss_health_max_start",
                      "boss_ai_controller_start", "boss_ai_controller_end", "boss_driver_mutations",
                      "boss_health_writes_by_driver", "boss_ai_writes_by_driver", "successful_parries")
    for key in summary_fields:
        if key not in summary:
            raise ValueError("missing summary total/field %s" % key)
    required = ("run", "build_id", "map", "route", "tier2", "tool_sha256", "frame_context_schema")
    for key in required:
        if key not in provenance or provenance[key] in (None, "", "UNKNOWN"):
            raise ValueError("missing or unknown provenance %s" % key)
    if provenance["route"] not in ("legacy", "data"):
        raise ValueError("invalid configured route")
    if not isinstance(provenance["tier2"], bool):
        raise ValueError("tier2 provenance must be boolean")
    if not re.fullmatch(r"[0-9a-f]{64}", str(provenance["tool_sha256"])):
        raise ValueError("invalid tool_sha256")
    if type(provenance["frame_context_schema"]) is not int or provenance["frame_context_schema"] != FRAME_CONTEXT_SCHEMA:
        raise ValueError("unsupported frame_context_schema")
    run = str(provenance["run"])
    if summary.get("run") != run:
        raise ValueError("summary run does not match provenance")
    routes = sorted(set(ROUTE_RE.findall(source)))
    if routes != [provenance["route"]]:
        raise ValueError("route witness missing, duplicate, or mismatched")

    actions = {}
    frame_rows = []
    counters = []
    contacts = []
    context_rows = []
    refills = []
    deaths = []
    boss_dead = BOSS_DEAD_RE.findall(source)
    finishes = FINISH_RE.findall(source)
    if len(boss_dead) > 1 or len(finishes) != 1:
        raise ValueError("duplicate boss-death or missing/duplicate finish marker")

    for line in lines:
        if "[FullFight] ACTION " in line:
            match = ACTION_RE.search(line)
            if not match:
                raise ValueError("malformed ACTION marker")
            name, when, action_id = match.groups()
            when = _number(when, "action time")
            if action_id in actions:
                raise ValueError("duplicate action id")
            if not action_id.startswith(run + ":action:"):
                raise ValueError("action id belongs to another run")
            actions[action_id] = {"name": name, "time": when, "frames": []}
        elif "[FullFight] COUNTER " in line:
            match = COUNTER_RE.search(line)
            if not match:
                raise ValueError("malformed COUNTER marker")
            when, action_id = match.groups()
            if action_id not in actions or actions[action_id]["name"] != "guard":
                raise ValueError("counter does not reference a guard action")
            counters.append({"time": _number(when, "counter time"), "action_id": action_id})
        elif "[FullFight] PARRY_CONTACT " in line:
            match = CONTACT_RE.search(line)
            if not match:
                raise ValueError("malformed PARRY_CONTACT marker")
            (instance, move, source, when, before, after, delta, press_count,
             sweep_before, sweep_after, montage) = match.groups()
            if min(int(instance), int(before), int(after), int(delta), int(press_count),
                   int(sweep_before), int(sweep_after)) < 0:
                raise ValueError("negative parry contact counter")
            if int(delta) != 1 or int(after) - int(before) != 1:
                raise ValueError("parry contact lacks an exact-one parried-count increment")
            if source not in ("tracker", "boss_montage_sweep") or int(press_count) < 1:
                raise ValueError("parry contact lacks a valid source/press witness")
            if int(sweep_after) < int(sweep_before):
                raise ValueError("sweep parry counter regressed")
            contacts.append({"instance": int(instance), "move": move, "source": source,
                             "time": _number(when, "parry contact time"),
                             "parried_before": int(before), "parried_after": int(after),
                             "press_count": int(press_count), "sweep_parried_delta": int(sweep_after)-int(sweep_before)})
        elif "[FullFight] FRAME_CONTEXT " in line:
            raw = line.split("[FullFight] FRAME_CONTEXT ", 1)[1]
            try:
                context = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError("malformed FRAME_CONTEXT JSON") from exc
            if not isinstance(context, dict):
                raise ValueError("FRAME_CONTEXT must be a JSON object")
            required_context = ("run", "frame_marker_id", "action_id", "game_time_s", "camera_position",
                                "player_position", "boss_position", "player_in_camera_frame_estimate",
                                "boss_in_camera_frame_estimate", "camera_inside_boss_component_bounds",
                                "world_occlusion")
            if any(key not in context for key in required_context):
                raise ValueError("FRAME_CONTEXT missing required field")
            if type(context.get("schema")) is not int or context["schema"] != FRAME_CONTEXT_SCHEMA:
                raise ValueError("unsupported FRAME_CONTEXT schema")
            for field in ("run", "frame_marker_id", "action_id"):
                if not isinstance(context[field], str) or not context[field]:
                    raise ValueError("FRAME_CONTEXT identity fields must be non-empty strings")
            if not isinstance(context["world_occlusion"], str) or context["world_occlusion"] not in ("UNMEASURED", "UNKNOWN"):
                raise ValueError("world_occlusion cannot claim clear without a trace receipt")
            bounds_state = context["camera_inside_boss_component_bounds"]
            if (type(bounds_state) is not bool and bounds_state != "UNKNOWN"):
                raise ValueError("invalid camera bounds state")
            for field in ("player_in_camera_frame_estimate", "boss_in_camera_frame_estimate"):
                value = context[field]
                if type(value) is not bool and value != "UNKNOWN":
                    raise ValueError("invalid camera framing estimate")
            for field in ("camera_position", "player_position", "boss_position"):
                value = context[field]
                if value != "UNKNOWN" and (not isinstance(value, list) or len(value) != 3):
                    raise ValueError("invalid FRAME_CONTEXT coordinate %s" % field)
                if value != "UNKNOWN":
                    for coordinate in value:
                        _number(coordinate, "FRAME_CONTEXT " + field)
            context_rows.append(context)
        elif "[FullFight] PLAYER_REFILL " in line:
            match = REFILL_RE.search(line)
            if not match:
                raise ValueError("malformed PLAYER_REFILL marker")
            count, when, hp_before, hp_after, boss_hp = match.groups()
            refills.append({"count": int(count), "time": _number(when, "refill time"),
                            "hp_before": _number(hp_before, "refill hp_before"),
                            "hp_after": _number(hp_after, "refill hp_after"), "boss_hp": boss_hp})
        elif "[FullFight] PLAYER_DEATH " in line:
            match = DEATH_RE.search(line)
            if not match:
                raise ValueError("malformed PLAYER_DEATH marker")
            count, when, reason = match.groups()
            deaths.append({"count": int(count), "time": _number(when, "death time"), "reason": reason})
        elif "[FullFight] FRAME " in line:
            match = FRAME_RE.search(line)
            if not match:
                raise ValueError("malformed FRAME marker")
            index, when, marker, action, action_id = match.groups()
            index, when = int(index), _number(when, "frame time")
            if marker != "%s:frame:%05d" % (run, index):
                raise ValueError("frame marker belongs to another run or index")
            if frame_rows and (index != frame_rows[-1]["index"] + 1 or when <= frame_rows[-1]["time"]):
                raise ValueError("frame indices/times are not consecutive and increasing")
            row = {"index": index, "time": when, "action": action, "action_id": action_id}
            if action_id != "None":
                if action_id not in actions:
                    raise ValueError("frame references no matching action")
                actions[action_id]["frames"].append(index)
            frame_rows.append(row)

    if not actions or not frame_rows:
        raise ValueError("actions and frames are required")
    context_by_marker = {}
    expected_markers = {"%s:frame:%05d" % (run, frame["index"]) for frame in frame_rows}
    for context in context_rows:
        marker = context["frame_marker_id"]
        if marker in context_by_marker:
            raise ValueError("expected exactly one FRAME_CONTEXT for each frame; duplicate context row")
        if context["run"] != run:
            raise ValueError("FRAME_CONTEXT does not match frame identity: foreign run")
        if marker not in expected_markers:
            raise ValueError("FRAME_CONTEXT does not match frame identity: foreign frame marker")
        context_by_marker[marker] = context
    if len(context_rows) != len(frame_rows):
        raise ValueError("missing FRAME_CONTEXT (pre-context receipt cannot be upgraded) or duplicate context row")
    for frame in frame_rows:
        marker = "%s:frame:%05d" % (run, frame["index"])
        context = context_by_marker.get(marker)
        if not context:
            raise ValueError("missing FRAME_CONTEXT for frame")
        context_time = _number(context["game_time_s"], "FRAME_CONTEXT time")
        if (context["action_id"] != frame["action_id"] or abs(context_time - frame["time"]) > 0.005):
            raise ValueError("FRAME_CONTEXT does not match frame identity/action/time")
        frame["context"] = context
    for action_id, action in actions.items():
        if not action["frames"]:
            raise ValueError("action has no linked same-run frame: %s" % action_id)
    if [row["count"] for row in refills] != list(range(1, len(refills) + 1)):
        raise ValueError("refill sequence is not consecutive")
    if any(row["hp_before"] >= 35.0 or row["hp_after"] <= row["hp_before"] for row in refills):
        raise ValueError("refill does not show a below-threshold increase")
    if [row["count"] for row in deaths] != list(range(1, len(deaths) + 1)):
        raise ValueError("death sequence is not consecutive")

    actual_counts = {}
    for action in actions.values():
        actual_counts[action["name"]] = actual_counts.get(action["name"], 0) + 1
    if counters:
        actual_counts["counter"] = len(counters)
    if contacts:
        actual_counts["parry_contact"] = len(contacts)
    counts = summary.get("action_counts")
    if not isinstance(counts, dict):
        raise ValueError("summary action_counts must be an object")
    required_names = ("light", "strong", "backstep", "air_light", "air_heavy", "guard", "parry_watch",
                      "counter", "parry_contact")
    for name in required_names:
        if name not in counts:
            raise ValueError("missing action total for %s" % name)
    for name in set(counts) | set(actual_counts):
        if counts.get(name, 0) != actual_counts.get(name, 0):
            raise ValueError("action count mismatch for %s" % name)
    if summary.get("player_refills") != len(refills):
        raise ValueError("refill count mismatch")
    if summary.get("player_deaths") != len(deaths):
        raise ValueError("player-death count mismatch")
    if summary.get("frames") != len(frame_rows):
        raise ValueError("frame count mismatch")
    summary_dead = summary.get("boss_dead") is True
    if summary_dead != bool(boss_dead):
        raise ValueError("boss-death summary contradicts marker")
    if summary_dead != (finishes[0] == "boss dead"):
        raise ValueError("boss-death summary contradicts finish reason")
    if summary.get("reason") != finishes[0]:
        raise ValueError("summary ending reason contradicts finish marker")
    if summary.get("boss_driver_mutations") != 0:
        raise ValueError("driver reports boss health/AI mutation")
    if summary.get("boss_health_writes_by_driver") != 0 or summary.get("boss_ai_writes_by_driver") != 0:
        raise ValueError("driver reports boss health or AI writes")
    if summary.get("successful_parries") != len(contacts):
        raise ValueError("parry-contact count mismatch")
    controllers = (summary.get("boss_ai_controller_start"), summary.get("boss_ai_controller_end"))
    if any(value in (None, "", "UNKNOWN", "None") for value in controllers):
        raise ValueError("boss AI controller readback unknown")
    if controllers[0] != controllers[1]:
        raise ValueError("boss AI controller changed during fight")
    _number(summary.get("fight_seconds"), "fight_seconds")
    _number(summary.get("boss_health_start"), "boss_health_start")
    _number(summary.get("boss_health_max_start"), "boss_health_max_start")
    if summary.get("boss_health_end") not in (None, "UNKNOWN"):
        _number(summary["boss_health_end"], "boss_health_end")
    elif not summary_dead:
        raise ValueError("boss health end readback unknown before boss death")

    by_action = {}
    for action in actions.values():
        by_action.setdefault(action["name"], []).append(action)
    for name in required_names[:7]:
        by_action.setdefault(name, [])
    parry_diagnostics = validate_parry_diagnostics(lines)
    attempts_by_instance = {row["instance"]: row for row in parry_diagnostics["attempts"]}
    seen_result_instances = set()
    contact_instances = {row["instance"] for row in contacts}
    for result in parry_diagnostics["results"]:
        instance = result["instance"]
        attempt = attempts_by_instance.get(instance)
        if attempt is None:
            raise ValueError("parry result has no preceding attempt")
        if instance in seen_result_instances:
            raise ValueError("duplicate parry result instance")
        seen_result_instances.add(instance)
        if result["outcome"] == "window_refused":
            if (attempt["opened"] or result["parried_before"] != attempt["parried_before"] or
                    instance in contact_instances):
                raise ValueError("window-refused result contradicts attempt")
        elif result["outcome"] == "no_contact":
            if (not attempt["opened"] or result["parried_before"] != attempt["parried_before"] or
                    instance in contact_instances):
                raise ValueError("no-contact result contradicts attempt")
    action_ids = {action_id: action["name"] for action_id, action in actions.items()}
    for timeout in parry_diagnostics["timeouts"]:
        if action_ids.get(timeout["slot"]) != "parry_watch":
            raise ValueError("parry timeout slot has no matching parry_watch action")
    attempt_line_by_instance = {int(match.group(1)): index for index, line in enumerate(lines)
                                if (match := PARRY_ATTEMPT_RE.search(line))}
    contact_line_by_instance = {int(match.group(1)): index for index, line in enumerate(lines)
                                if (match := CONTACT_RE.search(line))}
    seen_contact_instances = set()
    previous_contact_count = None
    for contact in contacts:
        attempt = attempts_by_instance.get(contact["instance"])
        if contact["instance"] in seen_contact_instances:
            raise ValueError("duplicate successful parry contact")
        seen_contact_instances.add(contact["instance"])
        if previous_contact_count is not None and contact["parried_before"] != previous_contact_count:
            raise ValueError("successful parry counter sequence is discontinuous")
        if (attempt is None or not attempt["opened"] or
                attempt_line_by_instance.get(contact["instance"], len(lines)) >=
                contact_line_by_instance.get(contact["instance"], -1) or
                attempt["move"] != contact["move"] or
                attempt["source"] != contact["source"] or
                attempt["press_count_after"] != contact["press_count"] or
                attempt["parried_before"] != contact["parried_before"]):
            if attempt is not None and not attempt["opened"]:
                raise ValueError("contact attempt did not open")
            raise ValueError("parry contact has no preceding matching attempt")
        previous_contact_count = contact["parried_after"]
    for instance in attempts_by_instance:
        terminal_events = int(instance in contact_instances) + int(instance in seen_result_instances)
        if terminal_events != 1:
            raise ValueError("parry attempt lacks exactly one terminal outcome")
    return {"run": run, "build_id": provenance["build_id"], "map": provenance["map"],
            "frame_context_schema": FRAME_CONTEXT_SCHEMA,
            "route_witness": routes[0], "tier2": provenance["tier2"], "tool_sha256": provenance["tool_sha256"],
            "fight_seconds": float(summary["fight_seconds"]), "boss_dead": summary_dead,
            "ending_reason": finishes[0], "action_counts": counts, "actions": by_action,
            "successful_parries": len(contacts), "player_refills": len(refills),
            "parry_contacts": contacts,
            "player_deaths": len(deaths), "frames": frame_rows, "frame_context": context_rows,
            "parry_diagnostics": parry_diagnostics,
            "boss_health_start": summary.get("boss_health_start"),
            "boss_health_max_start": summary.get("boss_health_max_start"),
            "boss_health_end": summary.get("boss_health_end"),
            "boss_ai_controller_start": summary.get("boss_ai_controller_start"),
            "boss_ai_controller_end": summary.get("boss_ai_controller_end"),
            "boss_driver_mutations": summary["boss_driver_mutations"],
            "boss_health_writes_by_driver": summary["boss_health_writes_by_driver"],
            "boss_ai_writes_by_driver": summary["boss_ai_writes_by_driver"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True, type=Path)
    args = parser.parse_args()
    if not args.log.is_file():  # BP-11: a missing input is a named usage error (exit 2), not a traceback
        parser.error(f"input file not found: {args.log}")
    print(json.dumps(parse_receipt(args.log.read_text(encoding="utf-8", errors="replace")),
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
