#!/usr/bin/env python3
"""List TODO/FIXME/XXX markers in source and documentation files."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MARKER = re.compile(r"\b(TODO|FIXME|XXX)\b", re.I)


def marker_lines(text: str) -> list:
    """BP-34: (1-based line number, line) for every TODO/FIXME/XXX line; moved from main()."""
    return [(number, line) for number, line in enumerate(text.splitlines(), 1) if MARKER.search(line)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path("."))
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    count = 0
    ignored = {".git", "Binaries", "Intermediate", "Saved", "node_modules", "__pycache__", "Archive"}
    candidates = [p for folder in ("Source", "Scripts", "Documentation") for p in (args.root / folder).rglob("*")]
    for path in sorted(candidates):
        if not path.is_file() or path.suffix.lower() not in {".h", ".cpp", ".py", ".ps1", ".md"}:
            continue
        if any(part in ignored for part in path.parts):
            continue
        try:
            for number, line in marker_lines(path.read_text(encoding="utf-8", errors="replace")):
                count += 1
                print(f"{path}:{number}: {line.strip()}")
        except OSError:
            continue
    print(f"markers={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
