#!/usr/bin/env python3
"""Compare two SHA256 source manifests (sha256 whitespace relative/path)."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ENTRY = re.compile(r"^([0-9a-fA-F]{64})\s+[* ]?(.*?)\s*$")


def load(path: Path) -> dict[str, str]:
    result = {}
    for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = ENTRY.match(line)
        if not match:
            raise ValueError(f"{path}:{number}: expected SHA256 and path")
        digest, name = match.groups()
        result[name] = digest.lower()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()
    before, after = load(args.before), load(args.after)
    added, removed = sorted(after.keys() - before.keys()), sorted(before.keys() - after.keys())
    changed = sorted(key for key in before.keys() & after.keys() if before[key] != after[key])
    for label, paths in (("ADDED", added), ("REMOVED", removed), ("CHANGED", changed)):
        for path in paths:
            print(f"{label} {path}")
    print(f"before={len(before)} after={len(after)} added={len(added)} removed={len(removed)} changed={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
