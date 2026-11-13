#!/usr/bin/env python3
"""Report files containing both CRLF and LF line endings (or lone CR)."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys


def line_ending_counts(data: bytes):
    """BP-34: (CRLF, lone LF, lone CR) counts, or None for binary data (NUL in the first 4 KiB); moved from main()."""
    if b"\0" in data[:4096]:
        return None
    crlf = data.count(b"\r\n")
    return crlf, data.count(b"\n") - crlf, data.count(b"\r") - crlf


def is_mixed(crlf: int, lf: int, cr: int) -> bool:
    """BP-34: mixed CRLF+LF endings or any lone CR; moved from main()."""
    return bool((crlf and lf) or cr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    mixed = 0
    files = 0
    ignored = {".git", "Binaries", "Intermediate", "Saved", "node_modules", "__pycache__", "Archive"}
    candidates = [p for folder in ("Source", "Scripts", "Documentation", "Config") for p in (args.root / folder).rglob("*")]
    candidates += list(args.root.glob("*.uproject")) + list(args.root.glob("*.uplugin"))
    for path in sorted(candidates):
        if not path.is_file() or path.suffix.lower() not in {".h", ".cpp", ".py", ".ps1", ".md", ".ini", ".json", ".uproject", ".uplugin"} or any(part in ignored for part in path.parts):
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        counted = line_ending_counts(data)
        if counted is None:
            continue
        files += 1
        crlf, lf, cr = counted
        if is_mixed(crlf, lf, cr):
            mixed += 1
            print(f"{path}: CRLF={crlf} LF={lf} lone_CR={cr}")
    print(f"files={files} mixed_or_lone_cr={mixed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
