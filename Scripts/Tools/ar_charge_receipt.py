#!/usr/bin/env python3
"""Read-only parser for retained ER control-latency R2 hold log rows."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


EXPECTED_CASES = {
    "R2_hold_0.34s": 0.34,
    "R2_hold_0.35s_boundary": 0.35,
    "R2_hold_0.36s": 0.36,
    "R2_hold_0.70s": 0.70,
}
# The driver's route line is authoritative for this receipt. Full editor logs
# also contain a default-startup route=data phrase, so generic route tokens
# would incorrectly make a valid legacy receipt look ambiguous.
ROUTE_RE = re.compile(r"\[(?:ERControlLatency|Showcase)\]\s+route=(legacy|data)(?:\s|$)")
SAMPLE_RE = re.compile(
    r"\bsample case=(?P<case>[A-Za-z0-9_.]+) montage=(?P<montage>[A-Za-z0-9_]+) "
    r"position=(?P<position>-?\d+(?:\.\d+)?) observed_ms=(?P<observed>-?\d+(?:\.\d+)?) "
    r"tick_s=(?P<tick>-?\d+(?:\.\d+)?)\b"
)


def parse_text(text: str, *, build_id: str, input_sha256: str = "") -> dict:
    """Parse one route's raw log. Build identity must be explicitly supplied."""
    build_id = str(build_id).strip()
    if not build_id:
        raise ValueError("build_id is required; it is not inferred from the log or filename")

    routes = {match.group(1) for line in text.splitlines() if (match := ROUTE_RE.search(line))}
    if len(routes) != 1:
        raise ValueError("input must contain exactly one explicit route=legacy or route=data")
    route = routes.pop()
    samples = {}
    for line in text.splitlines():
        if "sample case=R2_hold_" not in line:
            continue
        match = SAMPLE_RE.search(line)
        if not match:
            raise ValueError("malformed R2 hold sample row")
        case = match.group("case")
        if case not in EXPECTED_CASES:
            raise ValueError("unexpected R2 hold case: " + case)
        if case in samples:
            raise ValueError("duplicate R2 hold sample: " + case)
        row = {
            "case": case,
            "nominal_requested_hold_s": EXPECTED_CASES[case],
            "montage": match.group("montage"),
            "montage_position_s": float(match.group("position")),
            "observed_game_tick_bounded_ms": float(match.group("observed")),
            "tick_s": float(match.group("tick")),
        }
        if not row["montage"] or min(row["montage_position_s"], row["observed_game_tick_bounded_ms"], row["tick_s"]) < 0:
            raise ValueError("sample fields must be non-empty and non-negative")
        samples[case] = row

    missing = sorted(set(EXPECTED_CASES) - set(samples))
    if missing:
        raise ValueError("missing required R2 hold samples: " + ", ".join(missing))
    return {
        "schema": "onebossfight.er-charge-receipt/v1",
        "route": route,
        "build_id": build_id,
        "build_id_source": "explicit CLI/operator metadata; not present in parsed rows",
        "input_sha256": input_sha256,
        "observations_are_game_tick_bounded_not_device_latency": True,
        "samples": [samples[name] for name in EXPECTED_CASES],
        "parser_scope": "structured ERControlLatency route and sample rows from raw Unreal logs; unrelated startup route text and LogRPG* rows are ignored",
    }


def parse_file(path: Path, *, build_id: str) -> dict:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    return parse_text(raw.decode("utf-8", errors="replace"), build_id=build_id, input_sha256=digest)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path, help="one route's retained raw Unreal log or filtered P_* lines")
    parser.add_argument("--build-id", required=True, help="explicit Lead-reported build identity")
    args = parser.parse_args()
    try:
        result = parse_file(args.log, build_id=args.build_id)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
