#!/usr/bin/env python3
"""Check a normalized package manifest against G044 closure and project VFX assets."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

_G044_PATH = Path(__file__).with_name("check_g044_cook_manifest.py")
_G044_SPEC = importlib.util.spec_from_file_location("package_g044_cook_manifest", _G044_PATH)
if _G044_SPEC is None or _G044_SPEC.loader is None:
    raise ImportError(f"cannot load G044 checker: {_G044_PATH}")
g044 = importlib.util.module_from_spec(_G044_SPEC)
sys.modules[_G044_SPEC.name] = g044
_G044_SPEC.loader.exec_module(g044)


def vfx_package_paths(content_root: Path) -> set[str]:
    """Return /Game package names for every authored asset under project VFX."""
    root = content_root / "OneBossFight" / "VFX"
    if not root.is_dir():
        raise ValueError(f"project VFX content folder is missing: {root}")
    paths: set[str] = set()
    for item in root.rglob("*"):
        if item.is_file() and item.suffix.casefold() in {".uasset", ".umap"}:
            relative = item.relative_to(content_root).with_suffix("")
            paths.add(g044.package_path("/Game/" + relative.as_posix()))
    if not paths:
        raise ValueError(f"project VFX folder has no .uasset/.umap packages: {root}")
    return paths


def compare(required_file: Path, manifest_file: Path, configuration: str, content_root: Path) -> dict[str, Any]:
    required = g044.read_required(required_file)
    value = json.loads(manifest_file.read_text(encoding="utf-8-sig"))
    cooked, issues, roots = g044.validate_normalized_manifest(value, required)
    if issues:
        raise ValueError("; ".join(issues))
    if value["configuration"] != configuration:
        raise ValueError(f"manifest configuration {value['configuration']} does not match package {configuration}")
    vfx = vfx_package_paths(content_root)
    missing_closure = sorted(required - cooked)
    missing_vfx = sorted(vfx - cooked)
    return {
        "schema": "onebossfight.packaged-g044-vfx-check/v1",
        "build_id": value["build_id"],
        "configuration": configuration,
        "required_closure_sha256": hashlib.sha256(required_file.read_bytes()).hexdigest(),
        "normalized_manifest_sha256": hashlib.sha256(manifest_file.read_bytes()).hexdigest(),
        "vfx_package_count": len(vfx),
        "missing_closure": missing_closure,
        "missing_vfx": missing_vfx,
        "root_packages": roots,
        "verdict": "PASS" if required and not missing_closure and not missing_vfx else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--required", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path, help="normalized manifest exported from this package")
    parser.add_argument("--configuration", required=True, choices=("Development", "Shipping"))
    parser.add_argument("--content-root", required=True, type=Path, help="project Content directory")
    args = parser.parse_args()
    try:
        result = compare(args.required, args.manifest, args.configuration, args.content_root)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(json.dumps({"schema": "onebossfight.packaged-g044-vfx-check/v1", "verdict": "INVALID", "error": str(error)}, indent=2))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
