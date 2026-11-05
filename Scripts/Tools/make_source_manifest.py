#!/usr/bin/env python3
"""Write a sorted SHA-256 manifest for project Source files."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from atomic_io import atomic_write_text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    source = args.root / "Source"
    rows = []
    for path in sorted(p for p in source.rglob("*") if p.is_file()):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(f"{digest}  {path.relative_to(args.root).as_posix()}\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(args.output, "".join(rows))
    print(f"files={len(rows)} manifest={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
