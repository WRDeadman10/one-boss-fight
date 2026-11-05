#!/usr/bin/env python3
"""Validate a freshly assembled bench kit before it is copied or zipped."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


BASE_FILES = (
    "BENCHKIT_README.md",
    "BUILD_INFO.txt",
    "Scripts/RunBenchmark.ps1",
    "Scripts/BenchmarkEncounterSelection.psm1",
    "Scripts/PackagedSmoke.ps1",
    "Scripts/PackagedRunLog.psm1",
    "Scripts/CheckPackagedLog.ps1",
    "Scripts/CheckShippingBinary.py",
    "Scripts/Tools/check_bench_kit.py",
    "Saved/StagedBuilds/Windows/OneBossFight.exe",
    "Saved/StagedBuilds/Windows/Manifest_UFSFiles_Win64.txt",
    "Saved/StagedBuilds/Windows/Manifest_NonUFSFiles_Win64.txt",
)
DEVELOPMENT_FILES = (
    "Saved/StagedBuilds_Development/Windows/OneBossFight.exe",
    "Saved/StagedBuilds_Development/Windows/Manifest_UFSFiles_Win64.txt",
    "Saved/StagedBuilds_Development/Windows/Manifest_NonUFSFiles_Win64.txt",
)


def validate(kit_root: Path, include_development: bool = False, development_only: bool = False) -> dict[str, Any]:
    required = list(BASE_FILES)
    if include_development or development_only:
        required.extend(DEVELOPMENT_FILES)
    if development_only:
        required = [p for p in required if not p.startswith("Saved/StagedBuilds/Windows/")]
    missing = [name for name in required if not (kit_root / name).is_file()]
    empty = [name for name in required if (kit_root / name).is_file() and (kit_root / name).stat().st_size == 0]
    symbols = [p.relative_to(kit_root).as_posix() for p in kit_root.rglob("*.pdb") if p.is_file()]
    files = [p for p in kit_root.rglob("*") if p.is_file()]
    issues = []
    if missing:
        issues.append("missing required files: " + ", ".join(missing))
    if empty:
        issues.append("required files are empty: " + ", ".join(empty))
    if symbols:
        issues.append("debug PDB files must be archived separately, not included in the transfer kit: " + ", ".join(symbols))
    info_path = kit_root / "BUILD_INFO.txt"
    if info_path.is_file():
        info = info_path.read_text(encoding="utf-8-sig", errors="replace")
        if not re.search(r"(?m)^Package build ID: OBF-(?:SHIPPING|DEVELOPMENT)-[A-Za-z0-9T_-]+$", info):
            issues.append("BUILD_INFO.txt must include a generated package build ID")
        if not re.search(r"(?m)^Executable SHA-256: [0-9a-f]{64}$", info):
            issues.append("BUILD_INFO.txt must include the executable SHA-256")
    return {
        "schema": "onebossfight.bench-kit-check/v1",
        "kit_root": str(kit_root.resolve()),
        "include_development": include_development,
        "development_only": development_only,
        "file_count": len(files),
        "total_bytes": sum(p.stat().st_size for p in files),
        "missing": missing,
        "empty": empty,
        "pdb_files": symbols,
        "issues": issues,
        "verdict": "PASS" if not issues else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit-root", required=True, type=Path)
    parser.add_argument("--include-development", action="store_true")
    parser.add_argument("--development-only", action="store_true")
    args = parser.parse_args()
    result = validate(args.kit_root, args.include_development, args.development_only)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
