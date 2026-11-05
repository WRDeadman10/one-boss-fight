#!/usr/bin/env python3
"""Validate and summarize FrameworkProof RESULT rows with generation context."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

PROOF = re.compile(r"\[FrameworkProof\]\s+(\S+)(.*)")
FIELD = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)")
NUMERIC_FIELDS = {"acceptedHits", "attacks", "parriedHits", "guardedHits", "appliedDamage"}


def parse(path: Path) -> tuple[list[dict[str, object]], list[str]]:
    rows: list[dict[str, object]] = []
    diagnostics: list[str] = []
    active_generation: str | None = None
    for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        match = PROOF.search(line)
        if not match:
            continue
        token, payload = match.groups()
        pairs = FIELD.findall(payload)
        fields: dict[str, str] = {}
        for key, value in pairs:
            if token == "RESULT" and key in fields:
                diagnostics.append(f"ERROR line {number}: repeated field {key} in {token}")
            fields[key] = value
        if token == "encounter_reset" and "generation" in fields:
            active_generation = fields["generation"]
        elif "generation" in fields:
            active_generation = fields["generation"]
        if token != "RESULT":
            continue
        if not fields.get("outcome"):
            diagnostics.append(f"ERROR line {number}: RESULT is missing required field outcome")
        for key in sorted(NUMERIC_FIELDS & fields.keys()):
            if not fields[key].isdigit():
                diagnostics.append(f"ERROR line {number}: RESULT field {key} must be a nonnegative integer, got {fields[key]!r}")
        rows.append({"line": number, "generation": active_generation or "unknown", "fields": fields})
    seen: dict[str, int] = {}
    for row in rows:
        generation = str(row["generation"])
        if generation != "unknown" and generation in seen:
            diagnostics.append(f"WARN generation {generation}: repeated RESULT at lines {seen[generation]} and {row['line']}; check whether both terminal rows are expected")
        elif generation != "unknown":
            seen[generation] = int(row["line"])
    if len(rows) > 1:
        diagnostics.append(f"INFO found {len(rows)} RESULT rows; generation context is inferred from the latest proof generation field, unknown is explicit")
    return rows, diagnostics


def counter_delta(previous: dict[str, str] | None, current: dict[str, str]) -> dict[str, int] | None:
    """Derive per-interval deltas from actor-lifetime RESULT counter totals."""
    if previous is None:
        return None
    shared = (NUMERIC_FIELDS & previous.keys() & current.keys())
    if any(not previous[key].isdigit() or not current[key].isdigit() for key in shared):
        return None
    return {key: int(current[key]) - int(previous[key]) for key in sorted(shared)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    args = parser.parse_args()
    if not args.log.is_file():
        parser.error(f"missing log: {args.log}")
    rows, diagnostics = parse(args.log)
    for row in rows:
        fields = row["fields"]
        print(f"line={row['line']} generation={row['generation']} " + " ".join(f"{key}={value}" for key, value in sorted(fields.items())))
    for diagnostic in diagnostics:
        print(diagnostic)
    print(f"result_rows={len(rows)}")
    return 1 if any(item.startswith("ERROR ") for item in diagnostics) else 0


if __name__ == "__main__":
    raise SystemExit(main())
