#!/usr/bin/env python3
"""Count C++ files, lines, and automation tests by Source/OneBossFight folder."""
from __future__ import annotations

import argparse
import collections
import re
from pathlib import Path

TEST_MACRO = re.compile(r"IMPLEMENT_(?:SIMPLE_)?AUTOMATION_TEST\s*\(")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    repo = args.root.resolve()
    source = repo / "Source/OneBossFight"
    if not source.is_dir():
        parser.error(f"missing source directory: {source}")
    counts: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0, 0, 0])
    files = sorted([*source.rglob("*.h"), *source.rglob("*.cpp")])
    for path in files:
        folder = path.parent.relative_to(source).parts[0] if path.parent != source else "(root)"
        row = counts[folder]
        row[0] += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        row[1] += len(text.splitlines())
        if any(part.lower() == "tests" for part in path.parts):
            row[2] += 1
            row[3] += len(TEST_MACRO.findall(text))
    print("folder | cpp/h files | lines | test files | automation tests")
    for folder, (file_count, lines, test_files, tests) in sorted(counts.items()):
        print(f"{folder} | {file_count} | {lines} | {test_files} | {tests}")
    print(f"TOTAL | {sum(v[0] for v in counts.values())} | {sum(v[1] for v in counts.values())} | {sum(v[2] for v in counts.values())} | {sum(v[3] for v in counts.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
