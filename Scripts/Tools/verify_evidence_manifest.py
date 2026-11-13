#!/usr/bin/env python3
"""Verify an evidence_pack JSON manifest without changing evidence files."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path


SHA256 = re.compile(r"[0-9a-f]{64}")
# BK-221..225 (X-2068): exact manifest shape (audit findings E1-E8 in BK_216_220_EVIDENCE_MANIFEST_AUDIT.md).
TOP_LEVEL_KEYS = {"schema", "files"}
ENTRY_REQUIRED_KEYS = {"file", "sha256"}
ENTRY_ALLOWED_KEYS = {"file", "sha256", "bytes", "label"}


class ManifestFormatError(ValueError):
    pass


def _refuse_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ManifestFormatError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _refuse_constant(name):
    raise ManifestFormatError(f"non-finite JSON constant {name} is not allowed")


def load_manifest_json(text):
    """E1/E2: strict JSON - duplicate keys and NaN/Infinity are refused (ValueError)."""
    return json.loads(text, object_pairs_hook=_refuse_duplicate_keys, parse_constant=_refuse_constant)


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
        data = load_manifest_json(manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:  # ValueError covers JSONDecodeError and ManifestFormatError
        return [f"{manifest}: cannot read manifest: {error}"]
    # E3: schema must be the integer 1 (True and 1.0 compare equal to 1 but are refused).
    if not isinstance(data, dict) or type(data.get("schema")) is not int or data.get("schema") != 1 \
            or not isinstance(data.get("files"), list):
        return [f"{manifest}: invalid schema; expected object schema=1 with files array"]
    # E7: unknown top-level keys (typos, unrelated claims such as "verdict") are refused.
    unknown_top = sorted(set(data) - TOP_LEVEL_KEYS)
    if unknown_top:
        return [f"{manifest}: invalid schema; unknown top-level keys {unknown_top} (allowed: files, schema)"]
    # E4: a manifest that lists nothing verifies nothing.
    if not data["files"]:
        return [f"{manifest}: invalid schema; files array is empty (an evidence manifest must list at least one file)"]
    root = manifest.resolve().parent
    seen = set()
    listed_paths = set()
    json_payloads = []
    for index, entry in enumerate(data["files"], 1):
        if not isinstance(entry, dict) or not isinstance(entry.get("file"), str) or not isinstance(entry.get("sha256"), str):
            issues.append(f"{manifest}: files[{index}] must have string file and sha256 fields")
            continue
        unknown_keys = sorted(set(entry) - ENTRY_ALLOWED_KEYS)
        if unknown_keys:  # E7
            issues.append(f"{manifest}: files[{index}] has unknown keys {unknown_keys} (allowed: bytes, file, label, sha256)")
            continue
        # evidence_pack.py emits a descriptive label on every entry; it is metadata, not identity.
        if "label" in entry and not isinstance(entry["label"], str):
            issues.append(f"{manifest}: files[{index}] label must be text")
            continue
        if SHA256.fullmatch(entry["sha256"]) is None:  # E6: exact lowercase 64-hex, like source_log_sha256
            issues.append(f"{manifest}: files[{index}] sha256 must be 64 lowercase hex, got {entry['sha256']!r}")
            continue
        if "bytes" in entry and (type(entry["bytes"]) is not int or entry["bytes"] < 0):  # E8: never a bool/float
            issues.append(f"{manifest}: files[{index}] must have a nonnegative integer byte count")
            continue
        name = entry["file"]
        relative = Path(name)
        candidate = (root / relative).resolve()
        if relative.is_absolute() or ".." in relative.parts or not candidate.is_relative_to(root):
            issues.append(f"{manifest}: unsafe path {name!r} escapes evidence root")
            continue
        identity = os.path.normcase(str(candidate))  # E5: a.txt, ./a.txt and (on Windows) A.TXT are one file
        if identity in seen:
            issues.append(f"{manifest}: duplicate file entry {name!r} (same file as an earlier entry)")
            continue
        seen.add(identity)
        if require_bytes and (type(entry.get("bytes")) is not int or entry["bytes"] < 0):
            issues.append(f"{manifest}: files[{index}] must have a nonnegative integer byte count")
        if not candidate.is_file():
            issues.append(f"{manifest}: missing file {name!r}")
            continue
        actual_size = candidate.stat().st_size
        actual_hash = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if "bytes" in entry and entry["bytes"] != actual_size:
            issues.append(f"{manifest}: size mismatch {name!r}: expected={entry['bytes']} actual={actual_size}")
        if actual_hash != entry["sha256"]:
            issues.append(f"{manifest}: hash mismatch {name!r}: expected={entry['sha256']} actual={actual_hash}")
        listed_paths.add(candidate.resolve())
        if verify_source_references and candidate.suffix.casefold() == ".json":
            try:
                json_payloads.append((candidate, json.loads(candidate.read_text(encoding="utf-8-sig"))))
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
