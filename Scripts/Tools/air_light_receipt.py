"""Fail-closed parser for timestamped Air Light action-context records."""
import json
import math

REQUIRED = ("run", "action_id", "action", "phase", "game_time_s", "player_boss_cm",
            "player_position", "boss_position", "camera_position", "pivot_position",
            "arm_target_cm", "frame_index", "frame_marker_id")


def parse_context(line, expected_run=None):
    row = json.loads(line)
    missing = [key for key in REQUIRED if key not in row]
    if missing:
        raise ValueError("missing fields: " + ",".join(missing))
    if row["action"] != "air_light" or row["phase"] not in ("start", "end"):
        raise ValueError("invalid action/phase")
    if expected_run is not None and row["run"] != expected_run:
        raise ValueError("stale run")
    if not isinstance(row["frame_index"], int) or row["frame_index"] < 0:
        raise ValueError("invalid frame index")
    if row["frame_marker_id"] != "%s:frame:%05d" % (row["run"], row["frame_index"]):
        raise ValueError("frame identity mismatch")
    for key in ("game_time_s", "player_boss_cm", "arm_target_cm"):
        value = row[key]
        if value != "UNKNOWN" and (not isinstance(value, (int, float)) or
                                   isinstance(value, bool) or not math.isfinite(value)):
            raise ValueError("invalid finite number: " + key)
    for key in ("player_position", "boss_position", "camera_position", "pivot_position"):
        value = row[key]
        if value != "UNKNOWN" and (not isinstance(value, list) or len(value) != 3 or
                                   any(not isinstance(v, (int, float)) or isinstance(v, bool) or
                                       not math.isfinite(v) for v in value)):
            raise ValueError("invalid vector: " + key)
    return row
