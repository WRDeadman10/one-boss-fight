#!/usr/bin/env python3
"""Summarize staged benchmark summary.json files without modifying them."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


# A Development build writes next to the staged game, a Shipping build to the user's local data folder (found 2026-10-24): both are searched by default.
DEFAULT_ROOTS = [Path("Saved/StagedBuilds/Windows/OneBossFight/Saved/Benchmark")]
if os.environ.get("LOCALAPPDATA"):
    DEFAULT_ROOTS.append(Path(os.environ["LOCALAPPDATA"]) / "OneBossFight" / "Saved" / "Benchmark")
REMOTE_GPU_MARKERS = ("remote display", "virtual")


def value(summary: dict[str, Any], name: str) -> str:
    current = summary.get(name)
    if isinstance(current, float):
        return f"{current:.2f}"
    return str(current) if current is not None else "-"


def label_for(path: Path, summary: dict[str, Any]) -> str:
    return str(summary.get("label") or path.parent.name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, action="append", help="benchmark root (repeatable; default: the staged build folder and the local data folder of a Shipping build)")
    args = parser.parse_args()

    roots = args.root or DEFAULT_ROOTS
    summaries = sorted(path for root in roots if root.is_dir() for path in root.rglob("summary.json"))
    if not summaries:
        print("No summary.json files under: " + "; ".join(str(root) for root in roots))
        return 0

    columns = ("label", "gpu", "avg_fps", "p95_ms", "p99_ms", "max_ms", "game_p99", "render_p99", "gpu_p99", "meets_target")
    rows: list[tuple[str, ...]] = []
    invalid_gpu = False
    invalid_json = False
    invalid_fight = False
    for path in summaries:
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"ERROR {path}: {error}", file=sys.stderr)
            invalid_json = True
            continue
        if not isinstance(parsed, dict):
            print(f"ERROR {path}: root JSON value is not an object", file=sys.stderr)
            invalid_json = True
            continue
        gpu = str(parsed.get("gpu") or "")
        if parsed.get("fight_mode") is True and parsed.get("fight_started") is False:
            invalid_fight = True  # fight mode asked for, the bot never found the boss: an idle arena was measured
            print(f"INVALID {path}: fight_mode is true but fight_started is false (the bot never started the fight)", file=sys.stderr)
        if any(marker in gpu.casefold() for marker in REMOTE_GPU_MARKERS):
            invalid_gpu = True
        rows.append((
            label_for(path, parsed), gpu or "-", value(parsed, "avg_fps"), value(parsed, "p95_ms"), value(parsed, "p99_ms"), value(parsed, "max_ms"),
            value(parsed, "game_thread_p99_ms"), value(parsed, "render_thread_p99_ms"), value(parsed, "gpu_p99_ms"), value(parsed, "meets_target"),
        ))

    widths = [len(column) for column in columns]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))
    divider = "-+-".join("-" * width for width in widths)
    print(" | ".join(column.ljust(widths[index]) for index, column in enumerate(columns)))
    print(divider)
    for row in rows:
        print(" | ".join(cell.ljust(widths[index]) for index, cell in enumerate(row)))

    if invalid_gpu:
        print("INVALID: one or more benchmark runs used a Remote Display or Virtual GPU.", file=sys.stderr)
    if invalid_json:
        print("INVALID: one or more benchmark summary files could not be read.", file=sys.stderr)
    if invalid_fight:
        print("INVALID: one or more fight-mode runs never started the fight (fight_started false).", file=sys.stderr)
    return 1 if invalid_gpu or invalid_json or invalid_fight else 0


if __name__ == "__main__":
    raise SystemExit(main())
