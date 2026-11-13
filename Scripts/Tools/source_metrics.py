#!/usr/bin/env python3
"""Count C++ files, lines, and automation tests by Source/OneBossFight folder."""
from __future__ import annotations

import argparse
import collections
import re
from pathlib import Path

TEST_MACRO = re.compile(r"IMPLEMENT_(?:SIMPLE_)?AUTOMATION_TEST\s*\(")


def file_metrics(path: Path, source: Path, text: str):
    """BP-34: (folder bucket, line count, is a test file, automation-test macro count) for one file; moved from main()."""
    folder = path.parent.relative_to(source).parts[0] if path.parent != source else "(root)"
    is_test = any(part.lower() == "tests" for part in path.parts)
    return folder, len(text.splitlines()), is_test, len(TEST_MACRO.findall(text)) if is_test else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    repo = args.root.resolve()
    source = repo / "Source/OneBossFight"
    if not source.is_dir():
        parser.error(f"missing source directory: {source}")
    counts: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0, 0, 0])
    files = sorted([*source.rglob("*.h"), *source.rglob("*.cpp")])
    for path in files:
        folder, lines, is_test, tests = file_metrics(path, source, path.read_text(encoding="utf-8", errors="replace"))
        row = counts[folder]
        row[0] += 1
        row[1] += lines
        if is_test:
            row[2] += 1
            row[3] += tests
    print("folder | cpp/h files | lines | test files | automation tests")
    for folder, (file_count, lines, test_files, tests) in sorted(counts.items()):
        print(f"{folder} | {file_count} | {lines} | {test_files} | {tests}")
    print(f"TOTAL | {sum(v[0] for v in counts.values())} | {sum(v[1] for v in counts.values())} | {sum(v[2] for v in counts.values())} | {sum(v[3] for v in counts.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
