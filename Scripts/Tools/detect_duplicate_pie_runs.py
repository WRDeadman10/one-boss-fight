#!/usr/bin/env python3
"""Detect byte-identical Unreal editor-run chunks in concatenated raw logs."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

START = "LogInit: Display: Running engine for game:"


def scan(path: Path) -> tuple[list[dict[str, object]], list[tuple[int, int, int, int]]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    starts = [index for index, line in enumerate(lines) if START in line]
    runs: list[dict[str, object]] = []
    seen: dict[str, tuple[int, int]] = {}
    duplicates: list[tuple[int, int, int, int]] = []
    for position, begin in enumerate(starts):
        end = starts[position + 1] - 1 if position + 1 < len(starts) else len(lines) - 1
        chunk = "\n".join(lines[begin:end + 1]) + "\n"
        digest = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
        run = {"start_line": begin + 1, "end_line": end + 1, "sha256": digest}
        runs.append(run)
        if digest in seen:
            old_start, old_end = seen[digest]
            duplicates.append((old_start, old_end, begin + 1, end + 1))
        else:
            seen[digest] = (begin + 1, end + 1)
    return runs, duplicates


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=Path)
    args = parser.parse_args()
    invalid = False
    duplicate_found = False
    for path in args.logs:
        if not path.is_file():
            print(f"ERROR missing log: {path}")
            invalid = True
            continue
        runs, duplicates = scan(path)
        print(f"LOG {path} runs={len(runs)}")
        if not runs:
            print(f"INCOMPLETE {path}: no Unreal run-start marker")
            invalid = True
            continue
        for run in runs:
            print(f"RUN lines={run['start_line']}-{run['end_line']} sha256={run['sha256']}")
        for old_start, old_end, new_start, new_end in duplicates:
            print(f"DUPLICATE lines={new_start}-{new_end} repeats lines={old_start}-{old_end}; raw lines retained")
            duplicate_found = True
    return 2 if invalid else 1 if duplicate_found else 0


if __name__ == "__main__":
    raise SystemExit(main())
