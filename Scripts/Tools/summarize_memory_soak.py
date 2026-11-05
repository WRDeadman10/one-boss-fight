#!/usr/bin/env python3
"""Summarize completed U-C05 legacy and selected 50-reset memory-soak logs."""
from __future__ import annotations

import argparse
import ast
import math
import re
from pathlib import Path


RESULT = re.compile(r"\[MemorySoak\] RESULT route=(legacy|selected) resets=(\d+)/(\d+) status=(PASS|INCOMPLETE) reason=(.*)$")
SAMPLE = re.compile(r"\[MemorySoak\] sample (\{.*\})$")


def parse_log(path: Path) -> dict:
    result = None
    samples = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        match = RESULT.search(line)
        if match:
            route, complete, expected, status, reason = match.groups()
            result = {"route": route, "complete": int(complete), "expected": int(expected),
                      "status": status, "reason": reason, "line": line_number}
        sample = SAMPLE.search(line)
        if sample:
            try:
                row = ast.literal_eval(sample.group(1))
            except (SyntaxError, ValueError) as exc:
                raise ValueError(f"{path}:{line_number}: malformed sample literal: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: sample must be a dictionary")
            samples.append(row)
    if result is None:
        raise ValueError(f"{path}: MemorySoak RESULT line missing")
    return {"result": result, "samples": samples, "path": str(path)}


def analyze(capture: dict) -> dict:
    result, samples = capture["result"], capture["samples"]
    issues = []
    if result["status"] != "PASS" or result["complete"] != 50 or result["expected"] != 50:
        issues.append("arm did not report PASS 50/50")
    if len(samples) != 101:
        issues.append(f"expected 101 samples, found {len(samples)}")
    if any(row.get("route") != result["route"] for row in samples):
        issues.append("sample route disagrees with result route")
    if any(row.get("gc_before_sample") is not True for row in samples):
        issues.append("a sample is missing its pre-sample GC marker")
    stages = [row.get("stage") for row in samples]
    if stages.count("baseline_after_warmup") != 1 or stages.count("before_reset") != 50 or stages.count("after_reset") != 50:
        issues.append("sample stage counts are not 1 baseline + 50 before/after reset")
    post = [row for row in samples if row.get("stage") == "after_reset"]
    actors, private = [], []
    for row in post:
        objects, memory = row.get("objects"), row.get("memory")
        if isinstance(objects, dict) and isinstance(objects.get("actors"), (int, float)):
            actors.append(float(objects["actors"]))
        if isinstance(memory, dict) and isinstance(memory.get("private_mb"), (int, float)) and math.isfinite(memory["private_mb"]):
            private.append(float(memory["private_mb"]))
    if len(actors) != len(post):
        issues.append("some post-reset actor census values are missing")
    if len(private) != len(post):
        issues.append("some post-reset private-memory values are missing/unavailable")
    after_cycles = sorted(row.get("cycle") for row in post if isinstance(row.get("cycle"), int))
    before_cycles = sorted(row.get("cycle") for row in samples if row.get("stage") == "before_reset" and isinstance(row.get("cycle"), int))
    if after_cycles != list(range(1, 51)) or before_cycles != list(range(1, 51)):
        issues.append("before/after reset cycle identities must each cover 1..50 exactly once")
    summary = {"route": result["route"], "valid": not issues, "issues": issues,
               "samples": len(samples), "post_actor_min": min(actors) if actors else None,
               "post_actor_max": max(actors) if actors else None,
               "post_private_first_mb": private[0] if private else None,
               "post_private_last_mb": private[-1] if private else None,
               "post_private_delta_mb": round(private[-1] - private[0], 1) if private else None}
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("legacy", type=Path)
    parser.add_argument("selected", type=Path)
    args = parser.parse_args()
    try:
        summaries = [analyze(parse_log(args.legacy)), analyze(parse_log(args.selected))]
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    for summary in summaries:
        state = "PASS" if summary["valid"] else "INCOMPLETE"
        print(f"{state} {summary['route']}: samples={summary['samples']} actor_range={summary['post_actor_min']}..{summary['post_actor_max']} private_mb_delta={summary['post_private_delta_mb']}")
        for issue in summary["issues"]:
            print("- " + issue)
    print("Interpretation: a monotonic or positive post-GC trend is a leak candidate, not proof; allocator/cache retention and workload variance remain possible.")
    return 0 if all(summary["valid"] for summary in summaries) else 2


if __name__ == "__main__":
    raise SystemExit(main())
