#!/usr/bin/env python3
"""Validate and compare the six U-C07 Lead-run determinism arms."""
import argparse
import json
from pathlib import Path


EXPECTED = {(route, repeat) for route in ("legacy", "data") for repeat in (1, 2, 3)}


def compare(left, right):
    errors = []
    for label, receipt in (("left", left), ("right", right)):
        if receipt.get("schema") != "u_c07_determinism_v1":
            errors.append(f"{label}: unsupported schema")
        if receipt.get("status") != "complete" or receipt.get("fatal") is not None:
            errors.append(f"{label}: receipt is not a clean complete run")
        if not isinstance(receipt.get("runs"), list):
            errors.append(f"{label}: runs must be a list")
    if errors:
        return errors
    if left.get("seed") != right.get("seed"):
        errors.append("seed mismatch")
    if left.get("input_schedule") != right.get("input_schedule"):
        errors.append("input schedule mismatch")

    def index(receipt, label):
        found = {}
        for run in receipt["runs"]:
            if not isinstance(run, dict):
                errors.append(f"{label}: each run must be an object")
                continue
            key = (run.get("route"), run.get("repeat"))
            if key not in EXPECTED:
                errors.append(f"{label}: unexpected run identity {key!r}")
            elif key in found:
                errors.append(f"{label}: duplicate run identity {key!r}")
            else:
                found[key] = run
            if run.get("status") != "complete":
                errors.append(f"{label}: {key!r} is not complete")
            if not isinstance(run.get("events"), list) or not isinstance(run.get("inputs"), list):
                errors.append(f"{label}: {key!r} must include event and injected-input lists")
        missing = EXPECTED - found.keys()
        if missing:
            errors.append(f"{label}: missing runs {sorted(missing)}")
        return found

    li, ri = index(left, "left"), index(right, "right")
    def signature(run):
        return run.get("inputs"), run.get("events")

    for label, runs in (("left", li), ("right", ri)):
        complete = [runs[key] for key in sorted(EXPECTED & runs.keys())]
        if complete:
            reference = signature(complete[0])
            for run in complete[1:]:
                if signature(run) != reference:
                    errors.append(f"{label}: {run.get('route')}/repeat {run.get('repeat')} differs from the first route/repeat trace")
    for key in sorted(EXPECTED & li.keys() & ri.keys()):
        a, b = li[key], ri[key]
        if a.get("seed") != left.get("seed") or b.get("seed") != right.get("seed"):
            errors.append(f"{key!r}: run seed does not match receipt")
        if a.get("input_schedule") != left.get("input_schedule") or b.get("input_schedule") != right.get("input_schedule"):
            errors.append(f"{key!r}: run input schedule does not match receipt")
        if a.get("events") != b.get("events"):
            errors.append(f"{key!r}: tracker/AI event trace differs")
        if a.get("inputs") != b.get("inputs"):
            errors.append(f"{key!r}: injected input trace differs")
    return errors


def load(path):
    with Path(path).open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: receipt root must be an object")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", help="first determinism_runs.json")
    parser.add_argument("right", help="second determinism_runs.json")
    args = parser.parse_args()
    try:
        errors = compare(load(args.left), load(args.right))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    if errors:
        print("FAIL")
        for error in errors:
            print("- " + error)
        return 1
    print("PASS: both receipts contain six complete matching arms; seed, schedule, inputs, and event traces agree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
