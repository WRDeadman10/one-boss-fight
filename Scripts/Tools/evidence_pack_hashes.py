#!/usr/bin/env python3
"""Write a fresh evidence_sha256.txt into each supplied evidence folder."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def write_manifest(root: Path) -> tuple[Path, int]:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"not an evidence directory: {root}")
    manifest = root / "evidence_sha256.txt"
    if manifest.exists() or manifest.is_symlink():
        raise FileExistsError(f"refusing existing evidence manifest: {manifest}")
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlink is not accepted in evidence pack: {path}")
        if not path.is_file():
            continue
        resolved = path.resolve(strict=True)
        resolved.relative_to(root)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(f"{digest}  {path.relative_to(root).as_posix()}")
    with manifest.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write("\n".join(rows) + ("\n" if rows else ""))
    return manifest, len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folders", nargs="+", type=Path, help="build/evidence directories to hash")
    args = parser.parse_args()
    seen: set[Path] = set()
    for folder in args.folders:
        resolved = folder.resolve(strict=True)
        if resolved in seen:
            parser.error(f"duplicate evidence directory: {resolved}")
        seen.add(resolved)
        try:
            manifest, count = write_manifest(resolved)
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        print(f"files={count} manifest={manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
