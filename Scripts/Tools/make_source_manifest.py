#!/usr/bin/env python3
"""Write a sorted SHA-256 manifest for project Source files."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))  # BO-41: atomic_io resolves as a script or as `python -m Scripts.Tools.*`
from atomic_io import atomic_write_text


def output_aliases(output: Path, inputs) -> Path | None:
    """BK-301..305: return the input that `output` would overwrite (same resolved path or same file), else None."""
    target = Path(output).resolve()
    for item in inputs:
        candidate = Path(item)
        if candidate.resolve() == target:
            return candidate
        if target.exists() and candidate.exists() and target.samefile(candidate):
            return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    source = args.root / "Source"
    if not source.is_dir():  # BO-03 / KI-165: refuse a root without Source/ instead of writing an empty manifest.
        parser.error(f"no Source directory under root: {args.root}")
    rows = []
    scanned = sorted(p for p in source.rglob("*") if p.is_file())
    aliased = output_aliases(args.output, scanned)
    if aliased is not None:
        parser.error(f"output aliases a scanned Source file; refusing to overwrite it: {aliased}")
    if args.output.resolve().is_relative_to(source.resolve()):
        parser.error("output must be outside the scanned Source directory")
    for path in scanned:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(f"{digest}  {path.relative_to(args.root).as_posix()}\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(args.output, "".join(rows))
    print(f"files={len(rows)} manifest={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
