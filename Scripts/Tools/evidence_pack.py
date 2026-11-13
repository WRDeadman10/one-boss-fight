#!/usr/bin/env python3
"""Copy a raw log and optional pre/post state files into a hashed evidence folder."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))  # BO-41: atomic_io resolves as a script or as `python -m Scripts.Tools.*`
from atomic_io import atomic_create_copy, atomic_create_text


def file_identity(path: Path) -> tuple[int, str]:
    """Return byte count and SHA-256 without loading the whole evidence file into memory."""
    digest = hashlib.sha256()
    byte_count = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            byte_count += len(chunk)
            digest.update(chunk)
    return byte_count, digest.hexdigest()


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
    if out.exists():
        if not out.is_dir():
            parser.error(f"output root is not a directory: {out}")
        try:
            if next(out.iterdir(), None) is not None:
                parser.error(f"output root must be new or empty: {out}")
        except OSError as error:
            parser.error(f"cannot inspect output root {out}: {error}")
    # BO-02 / KI-164: every collision and destination check runs before the output root is created, so a rejected
    # invocation leaves no new directory behind.
    records = []
    planned = []
    reserved = {os.path.normcase(name) for name in ("evidence_manifest.json", "evidence_sha256.txt")}
    target_names = set()
    for source, label in sources:
        if source is None:
            continue
        try:
            target = safe_target(out, source, label)
        except ValueError as error:
            parser.error(str(error))
        target_identity = os.path.normcase(target.name)
        if target_identity in reserved or target_identity in target_names:
            parser.error(f"source destinations collide in output root: {target.name}")
        target_names.add(target_identity)
        planned.append((source, label, target))
    try:
        manifest_path = safe_output_path(out, "evidence_manifest.json")
        hashes_path = safe_output_path(out, "evidence_sha256.txt")
    except ValueError as error:
        parser.error(str(error))
    out.mkdir(parents=True, exist_ok=True)
    for source, label, target in planned:
        source_size, source_hash = file_identity(source)
        atomic_create_copy(source, target)
        copied_size, copied_hash = file_identity(target)
        if copied_size != source_size or copied_hash != source_hash:
            parser.error(f"published copy does not match source: {source}")
        records.append({"label": label, "file": target.name, "bytes": copied_size, "sha256": copied_hash})
    atomic_create_text(hashes_path, "".join(f"{item['sha256']}  {item['file']}\n" for item in records))
    # The manifest is the bundle's commit marker, so publish it last.
    atomic_create_text(manifest_path, json.dumps({"schema": 1, "files": records}, indent=2) + "\n")
    print(f"files={len(records)} output={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
