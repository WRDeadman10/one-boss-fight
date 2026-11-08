"""Fail-closed validation for dynamic camera probe JSONL samples."""
import json
import math

NUMERIC = ("game_time_s", "player_boss_cm", "camera_distance_cm",
           "arm_target_cm", "boss_relative_angle_deg")
REQUIRED = ("run", "route", "sample_id", "frame_marker_id", "frame_time_s",
            *NUMERIC, "camera_inside_mesh_aabb", "hide_boss_inside")


def parse_sample(line, expected_run=None):
    record = json.loads(line)
    missing = [key for key in REQUIRED if key not in record]
    if missing:
        raise ValueError("missing fields: " + ",".join(missing))
    if record["route"] not in ("data", "legacy"):
        raise ValueError("invalid route")
    if expected_run is not None and record["run"] != expected_run:
        raise ValueError("stale run")
    if record["sample_id"] != record["frame_marker_id"]:
        raise ValueError("stale frame marker")
    if record["frame_time_s"] != record["game_time_s"]:
        raise ValueError("frame marker time mismatch")
    for key in NUMERIC:
        value = record[key]
        if value != "UNKNOWN" and (not isinstance(value, (int, float)) or
                                   isinstance(value, bool) or not math.isfinite(value)):
            raise ValueError("invalid numeric field: " + key)
    for key in ("camera_inside_mesh_aabb", "hide_boss_inside"):
        value = record[key]
        if not (isinstance(value, bool) or value == "UNKNOWN"):
            raise ValueError("invalid state field: " + key)
    return record
