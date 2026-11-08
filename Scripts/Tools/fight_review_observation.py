"""Validate human-coded visual observations against same-run frame identities."""
import json
from pathlib import Path


STATES = {"seen", "not_seen", "obscured", "inconclusive"}


def validate_observation(row, run_id, frame_ids):
    if not isinstance(row, dict):
        raise ValueError("observation must be an object")
    if row.get("run") != run_id:
        raise ValueError("observation run mismatch")
    state = row.get("state")
    if state not in STATES:
        raise ValueError("unknown observation state")
    refs = row.get("frame_ids")
    if not isinstance(refs, list) or not refs:
        raise ValueError("observation needs at least one frame id")
    if any(ref not in frame_ids for ref in refs):
        raise ValueError("observation references a missing or foreign frame")
    if state in {"seen", "not_seen"} and row.get("evidence") != "decoded_frame_review":
        raise ValueError("seen/not_seen requires decoded frame review evidence")
    if state == "seen":
        if row.get("component_active") is True and row.get("visual_observed") is not True:
            raise ValueError("component activation cannot substitute for image evidence")
        if row.get("visual_observed") is not True:
            raise ValueError("seen requires explicit visual observation")
    if state in {"obscured", "inconclusive"} and not str(row.get("reason", "")).strip():
        raise ValueError("obscured/inconclusive state requires a reason")
    return {"run": run_id, "state": state, "frame_ids": refs,
            "reason": row.get("reason", ""), "evidence": row.get("evidence", "")}


def validate_review(rows, run_id, frame_ids):
    if not isinstance(rows, list) or not rows:
        raise ValueError("review rows must be a non-empty list")
    return [validate_observation(row, run_id, frame_ids) for row in rows]


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="JSON with run, frame_ids and observations")
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = validate_review(payload["observations"], payload["run"], set(payload["frame_ids"]))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
