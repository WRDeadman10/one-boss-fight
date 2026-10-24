#!/usr/bin/env python3
"""Empirical reporter for the two 2,000-health M14 bot calibration sets."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

HEALTH = 2000.0

# The flat driver records have no telegraph setting field. These time prefixes
# are the recorded calibration sets, not a heuristic.
SETS = (
    ("raw pacing (rpg.CloseTelegraph 0)", (
        "135708", "135948", "140235", "140515", "140601", "140829",
        "141052", "141131", "141402",
    )),
    ("telegraph 0.4", (
        "220426", "220721", "221000", "221227", "221511", "221742",
    )),
)

DAMAGE_RE = re.compile(
    r"= (?P<weapon>[0-9.]+) weapon hits \+ (?P<bleed>[0-9.]+) bleed procs"
    r" \+ (?P<riposte>[0-9.]+) riposte impacts"
)


def number(values: dict, name: str) -> float:
    return float(values.get(name, "0"))


def read_flat_record(root: Path, prefix: str) -> dict:
    matches = []
    for path in root.glob("20261023T{}*.json".format(prefix)):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if "build" in record and "metrics" in record:
            record["_path"] = path
            matches.append(record)
    if len(matches) != 1:
        raise ValueError("{}: expected one flat driver record, found {}".format(prefix, len(matches)))
    return matches[0]


def damage_parts(record: dict) -> dict[str, float]:
    for line in record.get("metrics", []):
        if line.startswith("METRIC boss_health ="):
            match = DAMAGE_RE.search(line)
            if match:
                return {name: float(value) for name, value in match.groupdict().items()}
    raise ValueError("{}: missing boss-health damage breakdown".format(record.get("run_id", "unknown")))


def pooled_rates(records: list[dict]) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for record in records:
        if record.get("outcome") != "boss_dead":
            continue
        values = result[record["build"]]
        values["seconds"] += number(record, "fight_seconds")
        values["damage"] += sum(damage_parts(record).values())
        values["completed"] += 1.0
    for values in result.values():
        values["dps"] = values["damage"] / values["seconds"]
    return result


def print_set(label: str, records: list[dict]) -> None:
    completed = sum(record.get("outcome") == "boss_dead" for record in records)
    mean_seconds = sum(number(record, "fight_seconds") for record in records) / len(records)
    mean_hits = sum(number(record, "hits_taken") for record in records) / len(records)
    rates = pooled_rates(records)
    print("\nCALIBRATION: {} ({} records, {} completed)".format(label, len(records), completed))
    print("mean fight seconds = {:.2f}; mean hits taken per run = {:.2f}".format(mean_seconds, mean_hits))
    print("build     completed-DPS")
    for build in ("Starter", "Strength", "Dex"):
        value = rates.get(build)
        print("{:<9} {}".format(build, "n/a" if not value else "{:.3f}".format(value["dps"])))
    print("run                 build     outcome       measured  predicted  error     hits  riposte  bleed")
    for record in records:
        measured = number(record, "fight_seconds")
        value = rates.get(record["build"])
        predicted = HEALTH / value["dps"] if value else 0.0
        error = (predicted - measured) * 100.0 / measured if measured else 0.0
        parts = damage_parts(record)
        print("{:<19} {:<8} {:<13} {:>8.3f} {:>9.3f} {:+6.2f}% {:>5} {:>8.1f} {:>6.1f}".format(
            record["run_id"], record["build"], record["outcome"], measured, predicted, error,
            int(number(record, "hits_taken")), parts["riposte"], parts["bleed"],
        ))


def main() -> int:
    project = Path(__file__).resolve().parents[1]
    root = project / "Saved" / "BalanceRuns"
    try:
        for label, prefixes in SETS:
            records = [read_flat_record(root, prefix) for prefix in prefixes]
            if any(number(record, "boss_start") != HEALTH for record in records):
                raise ValueError("{}: a record is not a {}-health calibration".format(label, int(HEALTH)))
            print_set(label, records)
    except ValueError as error:
        print("ERROR: {}".format(error))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
