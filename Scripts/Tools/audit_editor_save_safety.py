#!/usr/bin/env python3
"""Report first explicit save and preceding assertions/overwrite guards in Editor writers."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))  # BP-01/02: sibling imports work as a script or as `python -m Scripts.Tools.*`
from inventory_editor_asset_writers import classify
from atomic_io import atomic_create_text


SAVE = re.compile(r"\b(save_loaded_asset|save_asset|save_package|save_map|save_dirty_packages)\s*\(")
ASSERTION = re.compile(r"\bassert\b|\brequire\s*\(|\braise\s+[A-Za-z_]")
GUARD = re.compile(r"does_asset_exist|asset_exists|\bis_file\s*\(|\bexists\s*\(|already exists|refuse.?if.?exists|overwrite", re.I)


def analyze(text: str) -> dict[str, object]:
    lines = text.splitlines()
    saves = [(number, match.group(1)) for number, line in enumerate(lines, 1) for match in SAVE.finditer(line)]
    if not saves:
        return {"first_save": None, "save_api": None, "assertions": [], "guards": []}
    first_line, save_api = saves[0]
    assertions = [number for number, line in enumerate(lines[:first_line - 1], 1) if ASSERTION.search(line)]
    guards = [number for number, line in enumerate(lines[:first_line - 1], 1) if GUARD.search(line)]
    return {"first_save": first_line, "save_api": save_api, "assertions": assertions, "guards": guards}


def render(editor_dir: Path) -> tuple[str, dict[str, int]]:
    rows = []
    counts = {"writers": 0, "save_found": 0, "guard_marker_before_save": 0, "no_explicit_save": 0}
    for path in sorted(editor_dir.rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        category, _ = classify(text)
        if category == "read-only":
            continue
        counts["writers"] += 1
        result = analyze(text)
        first = result["first_save"]
        if first is None:
            counts["no_explicit_save"] += 1
            save = "NO EXPLICIT SAVE"
            assertions = guards = "—"
        else:
            counts["save_found"] += 1
            counts["guard_marker_before_save"] += bool(result["guards"])
            save = f"{result['save_api']}:{first}"
            assertions = ",".join(map(str, result["assertions"])) or "none detected"
            guards = ",".join(map(str, result["guards"])) or "none detected"
        rel = path.relative_to(editor_dir.parent.parent).as_posix()
        rows.append((rel, category, save, assertions, guards))
    lines = ["# T045 — Editor content first-save and collision-guard audit", "",
             "Static source inventory only. A listed assertion/guard marker may not validate every field or destination; review call context. Wrapper-driven saves and dynamic helper calls may not appear as literal save sites.", "",
             f"Writer scripts: {counts['writers']}; explicit save found: {counts['save_found']}; no explicit save: {counts['no_explicit_save']}; at least one guard marker before first save: {counts['guard_marker_before_save']}.", "",
             "| Script | T043 category | First explicit save | Earlier assertions/requirements | Earlier collision/refusal guard markers |", "|---|---|---|---|---|"]
    lines.extend(f"| `{rel}` | {category} | {save} | {assertions} | {guards} |" for rel, category, save, assertions, guards in rows)
    return "\n".join(lines) + "\n", counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--editor", type=Path, default=Path(__file__).resolve().parents[1] / "Editor")
    parser.add_argument("--output", type=Path, help="new Markdown output; existing file is refused")
    args = parser.parse_args()
    report, counts = render(args.editor)
    if args.output:
        try:
            atomic_create_text(args.output, report)
        except FileExistsError as error:
            # O1 (BK-271..275): FileExistsError also comes from parent creation when a parent component is a file
            # (or from exhausted temp names); only claim "existing" when the output path really exists.
            if os.path.lexists(args.output):
                print(f"REFUSED existing audit output: {args.output}")
            else:
                print(f"REFUSED cannot create audit output: {args.output}: {error}")
            return 2
        print(f"WROTE {args.output}")
    else:
        print(report, end="")
    print("[EDITOR_SAVE_AUDIT] " + " ".join(f"{key}={value}" for key, value in counts.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
