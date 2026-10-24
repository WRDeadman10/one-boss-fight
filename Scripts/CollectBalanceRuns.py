#!/usr/bin/env python3
"""Collect machine-readable BuildFight log events into per-run JSON and build summaries."""

import argparse
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path


EVENT_RE = re.compile(r"\[BuildFight\]\s+EVENT\s+(.*)$")
SUMMARY_RE = re.compile(r"\[BuildFight\]\s+RUN_SUMMARY\s+(.*)$")


def parse_fields(text):
    fields = {}
    for token in text.split():
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        fields[key] = value
    return fields


def number(fields, key, default=0.0):
    try:
        return float(fields.get(key, default))
    except (TypeError, ValueError):
        return default


def read_logs(logs):
    runs = {}
    for path in logs:
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            print("warning: could not read %s: %s" % (path, exc))
            continue
        for line in lines:
            match = EVENT_RE.search(line)
            kind = "event"
            if match is None:
                match = SUMMARY_RE.search(line)
                kind = "summary"
            if match is None:
                continue
            fields = parse_fields(match.group(1))
            run_id = fields.get("run")
            if not run_id:
                print("warning: ignored %s without run id in %s" % (kind, path.name))
                continue
            record = runs.setdefault(run_id, {"run_id": run_id, "events": [], "summary": None, "sources": []})
            record["sources"].append(str(path))
            if kind == "summary":
                record["summary"] = fields
            else:
                record["events"].append(fields)
    return runs


def stats(values):
    if not values:
        return {"n": 0}
    return {"n": len(values), "min": min(values), "median": statistics.median(values), "max": max(values), "mean": statistics.mean(values)}


def summarize_run(record):
    summary = record["summary"] or {}
    weapon = number(summary, "weapon")
    riposte = number(summary, "riposte")
    bleed = number(summary, "bleed")
    other = number(summary, "other")
    lost = number(summary, "health_lost")
    total = weapon + riposte + bleed + other
    record["accounting"] = {"weapon": weapon, "riposte": riposte, "bleed": bleed, "other": other,
                            "health_lost": lost, "event_sum": total, "delta": lost - total,
                            "closed": summary.get("accounting") == "closed" and abs(lost - total) <= 0.01}
    return record


def write_records(root, runs):
    output = root / "Saved" / "BalanceRuns"
    output.mkdir(parents=True, exist_ok=True)
    for run_id, record in sorted(runs.items()):
        with (output / (run_id + ".json")).open("w", encoding="utf-8") as handle:
            json.dump(record, handle, indent=2, sort_keys=True)
            handle.write("\n")


def print_builds(runs):
    by_build = defaultdict(list)
    bad = []
    for record in runs.values():
        summary = record["summary"]
        if summary is None:
            bad.append(record["run_id"] + " (missing RUN_SUMMARY)")
            continue
        if not record["accounting"]["closed"]:
            bad.append(record["run_id"])
        by_build[summary.get("build", "unknown")].append(record)
    for build, records in sorted(by_build.items()):
        fight_seconds = [number(record["summary"], "fight_seconds") for record in records]
        kind_damage = defaultdict(list)
        ripostes, bleeds, stamina, taken = [], [], [], []
        outcomes = Counter()
        for record in records:
            summary = record["summary"]
            outcomes[summary.get("outcome", "unknown")] += 1
            for event in record["events"]:
                name = event.get("event")
                if name == "hit":
                    kind_damage[event.get("kind", "Unknown")].append(number(event, "damage"))
                elif name == "riposte":
                    ripostes.append(number(event, "damage"))
                elif name == "bleed":
                    bleeds.append(number(event, "damage"))
                elif name == "stamina":
                    stamina.append(number(event, "value"))
                elif name == "taken":
                    taken.append(number(event, "damage"))
        print("%s: runs=%d fight_seconds=%s outcomes=%s" % (build, len(records), stats(fight_seconds), dict(sorted(outcomes.items()))))
        print("  damage_per_hit=%s" % {kind: stats(values) for kind, values in sorted(kind_damage.items())})
        print("  riposte_damage=%s bleed_damage=%s stamina_min=%s hits_taken=%s" % (
            stats(ripostes), stats(bleeds), min(stamina) if stamina else None,
            {"count": len(taken), "damage_total": sum(taken), "damage_per_hit": stats(taken)}))
    print("bad_accounting=%s" % (", ".join(bad) if bad else "none"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all-logs", action="store_true", help="also read OneBossFight-backup-*.log")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    logs_dir = root / "Saved" / "Logs"
    logs = [logs_dir / "OneBossFight.log"]
    if args.all_logs:
        logs.extend(sorted(logs_dir.glob("OneBossFight-backup-*.log")))
    runs = read_logs(logs)
    if not runs:
        print("no runs")
        return 0
    for record in runs.values():
        summarize_run(record)
    write_records(root, runs)
    print_builds(runs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
