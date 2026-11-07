#!/usr/bin/env python3
"""Validate the current AA/AB Codex queues contain ten ordered groups of five."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


ROW = re.compile(r"^\|\s*(AA-C|AB-C)(\d{2})\s*\|\s*(.*?)\s*\|", re.MULTILINE)
BATCH = re.compile(r"^## Batch (\d+)\b", re.MULTILINE)


def validate_queue(text: str, prefix: str) -> list[str]:
    issues: list[str] = []
    matches = list(ROW.finditer(text))
    ids = [f"{match.group(1)}{match.group(2)}" for match in matches if match.group(1) == prefix]
    expected = [f"{prefix}{number:02d}" for number in range(1, 51)]
    duplicates = sorted({task_id for task_id in ids if ids.count(task_id) > 1})
    if duplicates:
        issues.append(f"{prefix}: duplicate IDs: {', '.join(duplicates)}")
    missing = [task_id for task_id in expected if task_id not in ids]
    extra = [task_id for task_id in ids if task_id not in expected]
    if missing:
        issues.append(f"{prefix}: missing IDs: {', '.join(missing)}")
    if extra:
        issues.append(f"{prefix}: unexpected IDs: {', '.join(extra)}")
    if ids != expected:
        issues.append(f"{prefix}: table IDs must appear once in ascending 01..50 order")

    if prefix == "AB-C":
        headings = [int(value) for value in BATCH.findall(text)]
        if headings != list(range(1, 11)):
            issues.append("AB-C: batch headings must be exactly 1..10 in order")
        batch_for_row: list[int | None] = []
        active_batch: int | None = None
        for line in text.splitlines():
            heading = BATCH.match(line)
            if heading:
                active_batch = int(heading.group(1))
            row = ROW.match(line)
            if row and row.group(1) == prefix:
                batch_for_row.append(active_batch)
        counts = [batch_for_row.count(number) for number in range(1, 11)]
        if counts != [5] * 10:
            issues.append(f"AB-C: each numbered batch must contain five task rows; counts={counts}")
    else:
        marker_ids = [f"{match.group(1)}{match.group(2)}" for match in matches
                      if match.group(1) == prefix and "x- batch" in match.group(3).lower()]
        # C45 writes the next queue and C50 closes the lane instead of posting a
        # standalone X- row; both remain the fifth task in their ordered group.
        expected_markers = [f"{prefix}{number:02d}" for number in range(5, 45, 5)]
        if marker_ids != expected_markers:
            issues.append(f"{prefix}: X- batch rows must end groups 05,10,...,40 in order")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    cases = (("AA-C", root / "Documentation/Boss/QUEUE_AA.md"),
             ("AB-C", root / "Documentation/Boss/QUEUE_AB.md"))
    issues: list[str] = []
    for prefix, path in cases:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            issues.append(f"{prefix}: cannot read {path}: {error}")
            continue
        found = validate_queue(text, prefix)
        issues.extend(found)
        print(f"{prefix}: {'FAIL' if found else 'PASS'}; rows={len(ROW.findall(text))}")
    for issue in issues:
        print(f"ERROR: {issue}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
