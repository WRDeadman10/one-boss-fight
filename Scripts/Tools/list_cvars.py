#!/usr/bin/env python3
"""List rpg.* console-variable names mentioned in project source/config."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

CVAR = re.compile(r'TEXT\s*\(\s*"(rpg\.[^"]+)"')
PERF = re.compile(r'^\s*RPG_PERF_SWITCH\s*\(\s*\w+\s*,\s*"([^"]+)"', re.M)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    seen = set()
    for folder in ("Source/OneBossFight", "Config"):
        for path in sorted((args.root / folder).rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".h", ".cpp", ".ini"}:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            lines = text.splitlines()
            number = 0
            while number < len(lines):
                if "TAutoConsoleVariable" in lines[number]:
                    start = number + 1
                    block = [lines[number]]
                    while ";" not in lines[number] and number + 1 < len(lines):
                        number += 1
                        block.append(lines[number])
                    for name in CVAR.findall("\n".join(block)):
                        if not name.endswith("."):
                            seen.add((name, path.relative_to(args.root).as_posix(), start))
                for match in PERF.finditer(lines[number]):
                    seen.add(("rpg.Perf." + match.group(1), path.relative_to(args.root).as_posix(), number + 1))
                number += 1
    for name, filename, line in sorted(seen):
        print(f"{name}\t{filename}:{line}")
    print(f"registered_names={len({x[0] for x in seen})} registration_sites={len(seen)} (comments, tests, and caller strings excluded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
