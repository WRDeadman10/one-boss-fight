#!/usr/bin/env python3
"""Print nested profile JSON values as a stable key/value table."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def walk(value, prefix=""):
    if isinstance(value, dict):
        for key in sorted(value):
            yield from walk(value[key], f"{prefix}.{key}" if prefix else str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk(item, f"{prefix}[{index}]")
    else:
        yield prefix, value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile_json", type=Path)
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    data = json.loads(args.profile_json.read_text(encoding="utf-8"))
    print("FIELD\tVALUE")
    for key, value in walk(data):
        print(f"{key}\t{json.dumps(value, ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
