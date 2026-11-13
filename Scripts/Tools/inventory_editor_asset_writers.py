#!/usr/bin/env python3
"""Build a source-only inventory of Scripts/Editor Python writers."""
from __future__ import annotations

import argparse
import os
from collections import Counter
from pathlib import Path
import re

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))  # BP-01/02: sibling imports work as a script or as `python -m Scripts.Tools.*`
from atomic_io import atomic_create_text


SIGNALS = {
    "map_setup": re.compile(r"\b(save_map|new_level|load_map|open_level)\s*\(|\bget_all_level_actors\s*\(|\bLEVELS?\s*=\s*['\"]?/Game/[^\n]*Levels/", re.I),
    "creates": re.compile(r"\b(create_asset|duplicate_asset|import_asset|create_blueprint_asset|create_material_instance)\s*\(", re.I),
    "modifies": re.compile(r"\b(save_loaded_asset|save_asset|save_package|save_dirty_packages|set_editor_property|delete_asset|rename_asset|set_material|set_static_mesh)\s*\(", re.I),
}
ORDER = ("map_setup", "creates", "modifies")


def classify(text: str) -> tuple[str, list[str]]:
    hits = {category: sorted(set(pattern.findall(text))) for category, pattern in SIGNALS.items()}
    for category in ORDER:
        if hits[category]:
            return category, hits[category]
    return "read-only", []


def render(editor_dir: Path) -> str:
    rows = []
    counts: Counter[str] = Counter()
    for path in sorted(editor_dir.rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        category, signals = classify(text)
        counts[category] += 1
        rows.append((path.relative_to(editor_dir.parent.parent).as_posix(), category, ", ".join(signals) or "—"))
    lines = ["# T043 — Editor asset writer inventory", "",
             "Source-only heuristic inventory of `Scripts/Editor/**/*.py`. Categories come from literal API/map markers; scripts were not executed. Review the source before relying on a row, especially dynamic helper calls.", "",
             f"Scripts scanned: {len(rows)}. Counts: " + ", ".join(f"{key} {counts[key]}" for key in ("creates", "modifies", "map_setup", "read-only")), "",
             "| Script | Primary classification | Source markers |", "|---|---|---|"]
    lines.extend(f"| `{path}` | {category} | `{signals}` |" for path, category, signals in rows)
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--editor", type=Path, default=Path(__file__).resolve().parents[1] / "Editor")
    parser.add_argument("--output", type=Path, help="new Markdown output path; existing paths are refused")
    args = parser.parse_args()
    report = render(args.editor)
    if args.output:
        try:
            atomic_create_text(args.output, report)
        except FileExistsError as error:
            # O1 (BK-271..275): FileExistsError also comes from parent creation when a parent component is a file
            # (or from exhausted temp names); only claim "existing" when the output path really exists.
            if os.path.lexists(args.output):
                print(f"REFUSED existing inventory output: {args.output}")
            else:
                print(f"REFUSED cannot create inventory output: {args.output}: {error}")
            return 2
        print(f"WROTE {args.output}")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
