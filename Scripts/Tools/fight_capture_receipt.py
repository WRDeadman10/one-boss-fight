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
FINISH_RE = re.compile(r"\[FullFight\] finished: (.+)$")
CONTACT_RE = re.compile(r"\[FullFight\] PARRY_CONTACT instance=(\d+) t=([0-9.eE+-]+) parried_delta=(\d+) boss_montage=(\S+)")
PARRY_DIAG_RE = re.compile(r"\[FullFight\] PARRY_DIAG montage=(\S+) tracker_move=(\S+) tracker_instance=(\d+) tracker_active=(true|false) tracker_position=([0-9.eE+-]+) sweep_active=(true|false) sweep_count=(\d+)")
PARRY_TIMEOUT_RE = re.compile(r"\[FullFight\] PARRY_WATCH_RESULT outcome=timeout_no_live_a4 slot=(\S+) seconds=([0-9.eE+-]+)")
PARRY_ATTEMPT_RE = re.compile(r"\[FullFight\] PARRY_ATTEMPT instance=(\d+) active=(true|false) source=(\S+) montage=(\S+) sweep_active=(true|false) sweep_count=(\d+) position=([0-9.eE+-]+) opened=(true|false) parried_before=(\d+)")


def validate_parry_diagnostics(lines):
    transitions, timeouts, attempts = [], [], []
    previous_montage = None
    timeout_slots = set()
    for line in lines:
        if "[FullFight] PARRY_DIAG " in line:
            match = PARRY_DIAG_RE.search(line)
            if not match:
                raise ValueError("malformed PARRY_DIAG transition")
            montage, move, instance, active, position, sweep, sweep_count = match.groups()
            if montage == previous_montage:
                raise ValueError("duplicate montage transition diagnostic")
            previous_montage = montage
            transitions.append({"montage": montage, "tracker_move": move, "tracker_instance": int(instance),
                                "tracker_active": active == "true", "tracker_position": _number(position, "tracker position"),
                                "sweep_active": sweep == "true", "sweep_count": int(sweep_count)})
        elif "outcome=timeout_no_live_a4" in line:
            match = PARRY_TIMEOUT_RE.search(line)
            if not match:
                raise ValueError("malformed parry timeout slot")
            slot, seconds = match.groups()
            if slot in timeout_slots:
                raise ValueError("duplicate timeout slot")
            timeout_slots.add(slot)
            timeouts.append({"slot": slot, "seconds": _number(seconds, "parry timeout seconds")})
        elif "[FullFight] PARRY_ATTEMPT " in line:
            match = PARRY_ATTEMPT_RE.search(line)
            if not match:
                raise ValueError("malformed PARRY_ATTEMPT source receipt")
            instance, active, source, montage, sweep_active, sweep_count, position, opened, before = match.groups()
            if active != "true":
                raise ValueError("parry attempt is not tied to a live window")
            if source == "boss_montage_sweep" and not (
                    montage == "GS_Attack04_Montage" and sweep_active == "true"):
                raise ValueError("A4 montage fallback lacks a live sweep witness")
            if source not in ("tracker", "boss_montage_sweep"):
                raise ValueError("unknown parry window source")
            attempts.append({"instance": int(instance), "source": source, "montage": montage,
                             "sweep_active": sweep_active == "true", "sweep_count": int(sweep_count),
                             "position": _number(position, "parry attempt position"),
                             "opened": opened == "true", "parried_before": int(before)})
    return {"transitions": transitions, "timeouts": timeouts, "attempts": attempts}


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
    required = ("run", "build_id", "map", "route", "tier2", "tool_sha256")
    for key in required:
        if key not in provenance or provenance[key] in (None, "", "UNKNOWN"):
            raise ValueError("missing or unknown provenance %s" % key)
    if provenance["route"] not in ("legacy", "data"):
        raise ValueError("invalid configured route")
    if not isinstance(provenance["tier2"], bool):
        raise ValueError("tier2 provenance must be boolean")
    if not re.fullmatch(r"[0-9a-f]{64}", str(provenance["tool_sha256"])):
        raise ValueError("invalid tool_sha256")
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
            instance, when, delta, montage = match.groups()
            if int(delta) != 1:
                raise ValueError("parry contact lacks an exact-one parried-count increment")
            contacts.append({"instance": int(instance), "time": _number(when, "parry contact time")})
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
            if context["world_occlusion"] not in ("UNMEASURED", "UNKNOWN"):
                raise ValueError("world_occlusion cannot claim clear without a trace receipt")
            if context["camera_inside_boss_component_bounds"] not in (True, False, "UNKNOWN"):
                raise ValueError("invalid camera bounds state")
            for field in ("player_in_camera_frame_estimate", "boss_in_camera_frame_estimate"):
                if context[field] not in (True, False, "UNKNOWN"):
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
    return {"run": run, "build_id": provenance["build_id"], "map": provenance["map"],
            "route_witness": routes[0], "tier2": provenance["tier2"], "tool_sha256": provenance["tool_sha256"],
            "fight_seconds": float(summary["fight_seconds"]), "boss_dead": summary_dead,
            "ending_reason": finishes[0], "action_counts": counts, "actions": by_action,
            "successful_parries": len(contacts), "player_refills": len(refills),
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
    print(json.dumps(parse_receipt(args.log.read_text(encoding="utf-8", errors="replace")),
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
