#!/usr/bin/env python3
"""Copy a raw log and optional pre/post state files into a hashed evidence folder."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from atomic_io import atomic_create_copy, atomic_create_text


def safe_output_path(out: Path, filename: str) -> Path:
    """Return a fresh direct child of output root without following existing links."""
    target = out / filename
    resolved = target.resolve()
    if resolved.parent != out:
        raise ValueError(f"destination escapes output root: {target}")
    if target.exists() or target.is_symlink():
        raise ValueError(f"destination already exists; refusing overwrite: {target}")
    return target


def safe_target(out: Path, source: Path, label: str) -> Path:
    """Return a direct-child destination based on source basename and role."""
    filename = f"{label}_{source.name}" if label != "raw" else source.name
    return safe_output_path(out, filename)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_log", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--pre-state", type=Path)
    parser.add_argument("--post-state", type=Path)
    args = parser.parse_args()
    sources = [(args.raw_log, "raw"), (args.pre_state, "pre"), (args.post_state, "post")]
    if not args.raw_log.is_file() or any(path is not None and not path.is_file() for path, _ in sources):
        parser.error("raw log and any supplied state files must exist")
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    records = []
    planned = []
    reserved = {"evidence_manifest.json", "evidence_sha256.txt"}
    target_names = set()
    for source, label in sources:
        if source is None:
            continue
        try:
            target = safe_target(out, source, label)
        except ValueError as error:
            parser.error(str(error))
        if target.name in reserved or target.name in target_names:
            parser.error(f"source destinations collide in output root: {target.name}")
        target_names.add(target.name)
        planned.append((source, label, target))
    try:
        manifest_path = safe_output_path(out, "evidence_manifest.json")
        hashes_path = safe_output_path(out, "evidence_sha256.txt")
    except ValueError as error:
        parser.error(str(error))
    for source, label, target in planned:
        atomic_create_copy(source, target)
        records.append({"label": label, "file": target.name, "bytes": target.stat().st_size,
                        "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    atomic_create_text(hashes_path, "".join(f"{item['sha256']}  {item['file']}\n" for item in records))
    # The manifest is the bundle's commit marker, so publish it last.
    atomic_create_text(manifest_path, json.dumps({"schema": 1, "files": records}, indent=2) + "\n")
    print(f"files={len(records)} output={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
