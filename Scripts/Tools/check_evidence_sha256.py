#!/usr/bin/env python3
"""Verify files listed by Claude B_*/evidence_sha256.txt manifests."""
from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

ENTRY = re.compile(r"^([0-9a-fA-F]{64})(?:\s+(?:\d+\s+)?\*?)(.+?)\s*$")


def check_manifest(manifest: Path) -> list[str]:
    issues: list[str] = []
    root = manifest.resolve().parent
    try:
        # PowerShell's historical UTF-8 output commonly prefixes the file with a BOM.
        lines = manifest.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    except OSError as error:
        return [f"{manifest}: cannot read manifest: {error}"]
    for number, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = ENTRY.match(line)
        if not match:
            issues.append(f"{manifest}:{number}: malformed manifest entry")
            continue
        expected, name = match.groups()
        candidate = (root / name.strip()).resolve()
        if not candidate.is_relative_to(root):
            issues.append(f"{manifest}:{number}: unsafe path escapes manifest root: {name.strip()}")
            continue
        if not candidate.is_file():
            issues.append(f"{manifest}:{number}: missing {name.strip()}")
            continue
        digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if digest.lower() != expected.lower():
            issues.append(f"{manifest}:{number}: hash mismatch {name.strip()} expected={expected} actual={digest}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path("."), help="repository root")
    args = parser.parse_args()
    base = args.root.resolve() / "Docs" / "BossCombatReview" / "Execution" / "Claude"
    manifests = sorted(base.glob("B_*/evidence_sha256.txt"))
    if not manifests:
        print(f"No evidence manifests found under {base}")
        return 1
    issues = [issue for manifest in manifests for issue in check_manifest(manifest)]
    for issue in issues:
        print(issue)
    entries_checked = 0
    for manifest in manifests:
        for raw in manifest.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            line = raw.strip()
            if line and not line.startswith("#") and ENTRY.match(line):
                entries_checked += 1
    print(f"manifests={len(manifests)} entries_checked={entries_checked} mismatches={len(issues)}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
