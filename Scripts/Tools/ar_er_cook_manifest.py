#!/usr/bin/env python3
"""Read-only same-build check for the eight ER/Tier 2 cook package paths."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

_CHECKER_PATH = Path(__file__).with_name("check_g044_cook_manifest.py")
_SPEC = importlib.util.spec_from_file_location("ar_g044_cook_manifest", _CHECKER_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load normalized manifest validator: {_CHECKER_PATH}")
g044 = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = g044
_SPEC.loader.exec_module(g044)

DEFAULT_REQUIRED = Path(__file__).with_name("er_tier2_required_cook_assets.txt")


def _read_exact_required(path: Path) -> set[str]:
    rows: list[str] = []
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        item = line.strip()
        if not item or item.startswith("#"):
            continue
        package = g044.PACKAGE.fullmatch(item)
        if not package or not item.startswith("/Game/"):
            raise ValueError(f"{path}:{number}: expected one exact /Game package path")
        rows.append(g044.package_path(item))
    if len(rows) != 8:
        raise ValueError(f"required ER/Tier 2 list must contain exactly eight package paths (got {len(rows)})")
    if len(set(rows)) != len(rows):
        raise ValueError("required ER/Tier 2 list contains duplicate package paths")
    return set(rows)


def compare(required_file: Path, manifest_file: Path, build_id: str, configuration: str) -> dict[str, Any]:
    build_id = str(build_id).strip()
    configuration = str(configuration).strip()
    if not build_id:
        raise ValueError("explicit --build-id is required")
    if configuration not in ("Development", "Shipping"):
        raise ValueError("explicit --configuration must be Development or Shipping")

    required = _read_exact_required(required_file)
    raw = manifest_file.read_bytes()
    value = json.loads(raw.decode("utf-8-sig"))
    cooked, issues, _roots = g044.validate_normalized_manifest(value)
    if issues:
        raise ValueError("invalid normalized manifest: " + "; ".join(issues))
    if value["build_id"].strip() != build_id:
        raise ValueError("explicit build ID does not match normalized manifest")
    if value["configuration"] != configuration:
        raise ValueError("explicit configuration does not match normalized manifest")

    missing = sorted(required - cooked)
    return {
        "schema": "onebossfight.er-tier2-cook-check/v1",
        "build_id": build_id,
        "configuration": configuration,
        "route_independent_cook_check": True,
        "required_list_sha256": hashlib.sha256(required_file.read_bytes()).hexdigest(),
        "normalized_manifest_sha256": hashlib.sha256(raw).hexdigest(),
        "source_manifest_sha256": value["source_manifest_sha256"],
        "required_package_count": len(required),
        "missing_packages": missing,
        "verdict": "PASS" if not missing else "FAIL",
        "claim_scope": "cook-manifest package presence only; no staged identity, loadability, or packaged runtime proof",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="normalized manifest exported from the exact package under review")
    parser.add_argument("--build-id", required=True, help="Lead-reported package Build ID; must match the manifest")
    parser.add_argument("--configuration", required=True, choices=("Development", "Shipping"))
    parser.add_argument("--required", type=Path, default=DEFAULT_REQUIRED, help="defaults to the canonical eight-package list")
    args = parser.parse_args(argv)
    try:
        result = compare(args.required, args.manifest, args.build_id, args.configuration)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"schema": "onebossfight.er-tier2-cook-check/v1", "verdict": "INVALID", "error": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
