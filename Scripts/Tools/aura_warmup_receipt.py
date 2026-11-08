"""Validate that approved/candidate aura captures followed a bright warmup in the same run."""
import json
import math
from pathlib import Path


BRIGHTNESS_FLOOR = 5.0
MAX_WARMUP_FRAMES = 20
MAX_WARMUP_SECONDS = 4.0


def validate_warmup_receipt(records, run_id, route):
    if not isinstance(records, list) or not records:
        raise ValueError("manifest is empty")
    for row in records:
        if row.get("run") != run_id or row.get("route") != route:
            raise ValueError("run/route mismatch")
        if not isinstance(row.get("phase"), str) or "game_time_s" not in row:
            raise ValueError("manifest row lacks phase/time")

    ready_rows = []
    for index, target in enumerate(records):
        if target.get("phase") not in ("approved", "candidate"):
            continue
        warmups = []
        cursor = index - 1
        while cursor >= 0 and records[cursor].get("phase") == "warmup":
            warmups.insert(0, records[cursor])
            cursor -= 1
        if not warmups:
            raise ValueError("capture lacks same-run warmup")
        if len(warmups) > MAX_WARMUP_FRAMES:
            raise ValueError("warmup exceeds 20 frames")
        def finite(row, field):
            try:
                value = float(row[field])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError("invalid warmup %s" % field) from exc
            if not math.isfinite(value):
                raise ValueError("non-finite warmup %s" % field)
            return value

        ready = next((row for row in warmups if finite(row, "mean_gray") >= BRIGHTNESS_FLOOR), None)
        if ready is None:
            raise ValueError("no bright warmup before target capture")
        elapsed = finite(ready, "game_time_s") - finite(warmups[0], "game_time_s")
        if elapsed < 0.0 or elapsed > MAX_WARMUP_SECONDS:
            raise ValueError("warmup exceeds 4 game seconds")
        if finite(target, "mean_gray") < BRIGHTNESS_FLOOR:
            raise ValueError("target capture below brightness floor")
        ready_rows.append({"phase": target["phase"], "target_frame": target.get("frame"),
                           "ready_frame": ready.get("frame"), "warmup_frames": len(warmups),
                           "ready_elapsed_s": elapsed})
    if not ready_rows:
        raise ValueError("no approved or candidate target frame")
    return ready_rows


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--route", choices=("legacy", "data"), required=True)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(json.dumps(validate_warmup_receipt(rows, args.run, args.route), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
