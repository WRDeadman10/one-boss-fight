#!/usr/bin/env python3
"""Check KI-NNN mentions in C++ source against Documentation/KNOWN_ISSUES.md."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

IDS = re.compile(r"\bKI-(\d{3})\b")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    known = {int(value) for value in IDS.findall((root / "Documentation/KNOWN_ISSUES.md").read_text(encoding="utf-8"))}
    references = 0
    for path in sorted((root / "Source").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".h", ".cpp"}:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for value in IDS.findall(line):
                references += 1
                if int(value) not in known:
                    print(f"{path.relative_to(root)}:{number}: KI-{value} missing from KNOWN_ISSUES.md")
    print(f"references={references} documented_ids={len(known)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
