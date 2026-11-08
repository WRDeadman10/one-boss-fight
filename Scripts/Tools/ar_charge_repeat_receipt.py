#!/usr/bin/env python3
"""Stamp and aggregate independent route-identified R2 charge trial receipts."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics
import sys
from typing import Any

_PARSER_PATH = Path(__file__).with_name("ar_charge_receipt.py")
_SPEC = importlib.util.spec_from_file_location("ar_charge_receipt_for_repeat", _PARSER_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load charge receipt parser: {_PARSER_PATH}")
base = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = base
_SPEC.loader.exec_module(base)


def stamp(path: Path, *, build_id: str, route: str, trial_index: int, repetitions: int = 5) -> dict[str, Any]:
    if route not in ("legacy", "data"):
        raise ValueError("route must be legacy or data")
    if repetitions != 5 or not 1 <= trial_index <= repetitions:
        raise ValueError("trial index must be 1..5 and planned repetitions must be 5")
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig", errors="replace")
    if "input_context_active=True" not in text:
        raise ValueError("run lacks input_context_active=True; stop and return the failed run")
    if "SUMMARY finished: all control samples recorded" not in text:
        raise ValueError("run lacks the [ERControlLatency] SUMMARY finished completion marker; stop and return the failed run")
    if "draw_ready=True" not in text:
        raise ValueError("run lacks draw_ready=True; warmup was not confirmed and charge samples are invalid")
    parsed = base.parse_text(text, build_id=build_id, input_sha256=hashlib.sha256(raw).hexdigest())
    if parsed["route"] != route:
        raise ValueError(f"requested route {route} does not match log route {parsed['route']}")
    return {
        "schema": "onebossfight.er-charge-repeat-run/v1",
        "build_id": parsed["build_id"],
        "route": route,
        "trial_index": trial_index,
        "planned_repetitions_per_route": repetitions,
        "trial_id": f"{route}-R{trial_index:02d}",
        "raw_log_sha256": parsed["input_sha256"],
        "observations_are_game_tick_bounded_not_device_latency": True,
        "samples": parsed["samples"],
    }


def aggregate(paths: list[Path], *, build_id: str) -> dict[str, Any]:
    if not str(build_id).strip():
        raise ValueError("explicit --build-id is required")
    if len(paths) != 10:
        raise ValueError(f"exactly ten run receipts are required (5 per route); got {len(paths)}")
    runs: list[dict[str, Any]] = []
    for path in paths:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8-sig"))
        if not isinstance(value, dict) or value.get("schema") != "onebossfight.er-charge-repeat-run/v1":
            raise ValueError(f"{path}: unsupported repeat-run receipt schema")
        if value.get("build_id") != build_id:
            raise ValueError(f"{path}: build ID does not match requested build")
        route = value.get("route")
        trial_index = value.get("trial_index")
        if route not in ("legacy", "data") or type(trial_index) is not int or not 1 <= trial_index <= 5:
            raise ValueError(f"{path}: invalid route/trial identity")
        if value.get("planned_repetitions_per_route") != 5 or value.get("trial_id") != f"{route}-R{trial_index:02d}":
            raise ValueError(f"{path}: trial identity does not match the five-run schedule")
        if value.get("observations_are_game_tick_bounded_not_device_latency") is not True:
            raise ValueError(f"{path}: timing boundary flag is missing")
        if not isinstance(value.get("raw_log_sha256"), str) or len(value["raw_log_sha256"]) != 64:
            raise ValueError(f"{path}: raw log hash is missing")
        samples = value.get("samples")
        sample_cases = [row.get("case") for row in samples] if isinstance(samples, list) and all(isinstance(row, dict) for row in samples) else []
        if sample_cases != list(base.EXPECTED_CASES):
            raise ValueError(f"{path}: sample cases are missing, duplicated, or out of canonical order")
        runs.append({**value, "receipt_sha256": hashlib.sha256(raw).hexdigest()})

    keys = [(run["route"], run["trial_index"]) for run in runs]
    if len(set(keys)) != 10:
        raise ValueError("duplicate route/trial identity")
    expected = {(route, trial) for route in ("legacy", "data") for trial in range(1, 6)}
    if set(keys) != expected:
        raise ValueError("schedule must contain exactly trials 1..5 for both routes")

    summary: dict[str, Any] = {}
    for route in ("legacy", "data"):
        route_runs = sorted((run for run in runs if run["route"] == route), key=lambda item: item["trial_index"])
        summary[route] = {}
        for case in base.EXPECTED_CASES:
            values = [next(row for row in run["samples"] if row["case"] == case) for run in route_runs]
            delays = [row["observed_game_tick_bounded_ms"] for row in values]
            summary[route][case] = {
                "trial_ids": [run["trial_id"] for run in route_runs],
                "montages": [row["montage"] for row in values],
                "observed_game_tick_bounded_ms": delays,
                "median_observed_game_tick_bounded_ms": statistics.median(delays),
                "tick_s": [row["tick_s"] for row in values],
            }
    return {
        "schema": "onebossfight.er-charge-repeat-batch/v1",
        "build_id": build_id,
        "planned_repetitions_per_route": 5,
        "run_count": 10,
        "routes": ["legacy", "data"],
        "timing_scope": "game-tick-bounded, not physical device latency; descriptive summary only, no causality inferred",
        "runs": [{key: run[key] for key in ("route", "trial_index", "trial_id", "raw_log_sha256", "receipt_sha256")} for run in sorted(runs, key=lambda item: (item["route"], item["trial_index"]))],
        "summary": summary,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("stamp", help="parse one raw route log and attach explicit trial identity")
    one.add_argument("log", type=Path)
    one.add_argument("--build-id", required=True)
    one.add_argument("--route", required=True, choices=("legacy", "data"))
    one.add_argument("--trial-index", required=True, type=int, choices=range(1, 6))
    one.add_argument("--output", type=Path, help="write receipt (stdout if omitted)")
    batch = sub.add_parser("aggregate", help="validate and summarize the exact ten-receipt batch")
    batch.add_argument("--build-id", required=True)
    batch.add_argument("--run", action="append", required=True, type=Path, help="repeat exactly ten times")
    args = parser.parse_args(argv)
    try:
        if args.command == "stamp":
            result = stamp(args.log, build_id=args.build_id, route=args.route, trial_index=args.trial_index)
            encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
            if args.output:
                if args.output.resolve() == args.log.resolve():
                    raise ValueError("receipt output must not overwrite the raw log")
                args.output.write_text(encoded, encoding="utf-8", newline="\n")
            else:
                sys.stdout.write(encoded)
            return 0
        result = aggregate(args.run, build_id=args.build_id)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"schema": "onebossfight.er-charge-repeat/v1", "verdict": "INVALID", "error": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
