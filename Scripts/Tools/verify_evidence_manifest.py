#!/usr/bin/env python3
"""Verify an evidence_pack JSON manifest without changing evidence files."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


SHA256 = re.compile(r"[0-9a-f]{64}")


def source_references(value):
    if isinstance(value, dict):
        if "source_log" in value or "source_log_sha256" in value:
            yield value
        for child in value.values():
            yield from source_references(child)
    elif isinstance(value, list):
        for child in value:
            yield from source_references(child)


def verify(manifest: Path, require_bytes: bool = False,
           verify_source_references: bool = False,
           strict_membership: bool = False) -> list[str]:
    issues = []
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"{manifest}: cannot read manifest: {error}"]
    if not isinstance(data, dict) or data.get("schema") != 1 or not isinstance(data.get("files"), list):
        return [f"{manifest}: invalid schema; expected object schema=1 with files array"]
    root = manifest.resolve().parent
    seen = set()
    listed_paths = set()
    json_payloads = []
    for index, entry in enumerate(data["files"], 1):
        if not isinstance(entry, dict) or not isinstance(entry.get("file"), str) or not isinstance(entry.get("sha256"), str):
            issues.append(f"{manifest}: files[{index}] must have string file and sha256 fields")
            continue
        name = entry["file"]
        relative = Path(name)
        candidate = (root / relative).resolve()
        if relative.is_absolute() or ".." in relative.parts or not candidate.is_relative_to(root):
            issues.append(f"{manifest}: unsafe path {name!r} escapes evidence root")
            continue
        if name in seen:
            issues.append(f"{manifest}: duplicate file entry {name!r}")
            continue
        seen.add(name)
        if require_bytes and (type(entry.get("bytes")) is not int or entry["bytes"] < 0):
            issues.append(f"{manifest}: files[{index}] must have a nonnegative integer byte count")
        if not candidate.is_file():
            issues.append(f"{manifest}: missing file {name!r}")
            continue
        actual_size = candidate.stat().st_size
        actual_hash = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if "bytes" in entry and entry["bytes"] != actual_size:
            issues.append(f"{manifest}: size mismatch {name!r}: expected={entry['bytes']} actual={actual_size}")
        if actual_hash.lower() != entry["sha256"].lower():
            issues.append(f"{manifest}: hash mismatch {name!r}: expected={entry['sha256']} actual={actual_hash}")
        listed_paths.add(candidate.resolve())
        if verify_source_references and candidate.suffix.casefold() == ".json":
            try:
                json_payloads.append((candidate, json.loads(candidate.read_text(encoding="utf-8"))))
            except (OSError, UnicodeError, json.JSONDecodeError):
                # A listed JSON artifact need not be a receipt; its bytes are still checked above.
                pass

    if strict_membership:
        exempt = {manifest.resolve(), (root / "evidence_sha256.txt").resolve()}
        for path in root.rglob("*"):
            try:
                resolved = path.resolve()
            except OSError as error:
                issues.append(f"{manifest}: cannot resolve pack member {path}: {error}")
                continue
            if path.is_symlink():
                issues.append(f"{manifest}: symlink pack member is not allowed in strict mode: {path.relative_to(root)}")
                continue
            if path.is_file() and not resolved.is_relative_to(root):
                issues.append(f"{manifest}: pack member escapes evidence root: {path}")
            elif path.is_file() and resolved not in exempt and resolved not in listed_paths:
                issues.append(f"{manifest}: unlisted pack member {path.relative_to(root)}")

    if verify_source_references:
        for artifact, payload in json_payloads:
            for ref in source_references(payload):
                source_name = ref.get("source_log")
                source_hash = ref.get("source_log_sha256")
                label = f"{artifact.relative_to(root)} source reference"
                if not isinstance(source_name, str) or not source_name.strip():
                    issues.append(f"{label}: source_log must be nonempty text")
                    continue
                if not isinstance(source_hash, str) or SHA256.fullmatch(source_hash) is None:
                    issues.append(f"{label}: source_log_sha256 must be lowercase SHA-256")
                    continue
                cited = Path(source_name)
                candidate = cited if cited.is_absolute() else artifact.parent / cited
                try:
                    resolved = candidate.resolve(strict=True)
                    if not resolved.is_relative_to(root):
                        issues.append(f"{label}: path escapes evidence root: {source_name!r}")
                    elif not resolved.is_file():
                        issues.append(f"{label}: source is not a file: {source_name!r}")
                    elif resolved not in listed_paths:
                        issues.append(f"{label}: source is not listed in evidence manifest: {source_name!r}")
                    elif hashlib.sha256(resolved.read_bytes()).hexdigest() != source_hash:
                        issues.append(f"{label}: SHA-256 mismatch for {source_name!r}")
                except OSError as error:
                    issues.append(f"{label}: cannot read {source_name!r}: {error}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--require-bytes", action="store_true",
                        help="require a nonnegative byte count for every listed payload")
    parser.add_argument("--verify-source-references", action="store_true",
                        help="verify JSON source_log references stay in the pack, are listed, and match hashes")
    parser.add_argument("--strict-membership", action="store_true",
                        help="reject unlisted files under the pack root (excluding this manifest and evidence_sha256.txt)")
    args = parser.parse_args()
    issues = verify(args.manifest, require_bytes=args.require_bytes,
                    verify_source_references=args.verify_source_references,
                    strict_membership=args.strict_membership)
    for issue in issues:
        print("INVALID " + issue)
    if not issues:
        print(f"PASS {args.manifest}: manifest entries verified")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
