#!/usr/bin/env python3
"""Compare required G044 /Game package paths with a packaged cook manifest.

Inputs are UTF-8 text. The required file contains one exact /Game package path
per non-comment line; the cook manifest may be a UAT log or manifest text.
This is a deterministic offline comparison, not proof that a particular build
was packaged or launched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

PACKAGE = re.compile(r"/Game/[A-Za-z0-9_./-]+", re.IGNORECASE)
GAME_PACKAGE_PATH = re.compile(r"^/Game/(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+$", re.IGNORECASE)
NORMALIZED_SCHEMA = "onebossfight.g044-cook-manifest/v1"
COMPARISON_SCHEMA = "onebossfight.g044-cook-comparison/v1"
ROOT_ROLES = {"selection", "boss", "player"}


def package_path(value: str) -> str:
    value = value.strip().strip('"\' ,;()[]{}')
    value = re.sub(r"\.(uasset|umap)$", "", value, flags=re.IGNORECASE)
    head, separator, leaf = value.rpartition("/")
    if separator and "." in leaf:
        leaf = leaf.split(".", 1)[0]
        value = head + separator + leaf
    return value.rstrip(".,;:").casefold()


def read_required(path: Path) -> set[str]:
    required: set[str] = set()
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        item = line.strip()
        if not item or item.startswith("#"):
            continue
        match = PACKAGE.search(item)
        if not match:
            raise ValueError(f"{path}:{number}: expected a /Game package path")
        required.add(package_path(match.group(0)))
    return required


def read_cooked(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    return {package_path(match.group(0)) for match in PACKAGE.finditer(text)}


def validate_normalized_manifest(value: Any, required: set[str] | None = None) -> tuple[set[str], list[str], dict[str, str]]:
    """Validate an explicit JSON export; never infer roots from package order."""
    issues: list[str] = []
    if not isinstance(value, dict) or value.get("schema") != NORMALIZED_SCHEMA:
        return set(), [f"manifest schema must be {NORMALIZED_SCHEMA}"], {}
    allowed = {"schema", "build_id", "configuration", "root_packages", "packages", "source_manifest_sha256"}
    extra = set(value) - allowed
    if extra:
        issues.append("manifest has unknown fields: " + ", ".join(sorted(str(key) for key in extra)))
    for key in ("build_id", "configuration"):
        if not isinstance(value.get(key), str) or not value[key].strip():
            issues.append(f"manifest {key} must be nonempty")
    if value.get("configuration") not in ("Shipping", "Development"):
        issues.append("manifest configuration must be Shipping or Development")
    digest = value.get("source_manifest_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        issues.append("manifest source_manifest_sha256 must be 64 lowercase hexadecimal characters")
    roots = value.get("root_packages")
    normalized_roots: dict[str, str] = {}
    if not isinstance(roots, dict):
        issues.append("manifest root_packages must be an object")
    else:
        if set(roots) != ROOT_ROLES:
            issues.append("manifest root_packages must contain exactly selection, boss, and player")
        for role in sorted(ROOT_ROLES & set(roots)):
            raw = roots[role]
            if not isinstance(raw, str) or not GAME_PACKAGE_PATH.fullmatch(raw):
                issues.append(f"manifest root_packages.{role} must be a /Game package path without an object suffix")
            else:
                normalized_roots[role] = package_path(raw)
    entries = value.get("packages")
    cooked: set[str] = set()
    if not isinstance(entries, list) or not entries:
        issues.append("manifest packages must be a nonempty array")
    else:
        for index, raw in enumerate(entries):
            if not isinstance(raw, str) or not GAME_PACKAGE_PATH.fullmatch(raw):
                issues.append(f"manifest packages[{index}] must be a /Game package path without an object suffix")
                continue
            normalized = package_path(raw)
            if normalized in cooked:
                issues.append(f"manifest packages has duplicate path: {raw}")
            cooked.add(normalized)
    for role, root in normalized_roots.items():
        if root not in cooked:
            issues.append(f"manifest root {role} is not present in packages: {root}")
        if required is not None and root not in required:
            issues.append(f"manifest root {role} is not present in required closure: {root}")
    if len(set(normalized_roots.values())) != len(normalized_roots):
        issues.append("selection, boss, and player root package identities must be distinct")
    return cooked, issues, normalized_roots


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_summary(required: set[str], cooked: set[str], missing: list[str], editor_only: list[str],
                  required_file: Path, manifest_file: Path, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema": COMPARISON_SCHEMA,
        "input_sha256": {"required": sha256_file(required_file), "manifest": sha256_file(manifest_file)},
        "required_count": len(required),
        "cooked_game_path_count": len(cooked),
        "missing_count": len(missing),
        "editor_only_excluded_count": len(editor_only),
        "missing": sorted(missing),
        "editor_only_excluded": sorted(editor_only),
        "verdict": "PASS" if required and not missing else "FAIL",
        "manifest_identity": metadata or None,
    }


def compare(required: set[str], cooked: set[str]) -> list[str]:
    return sorted(required - cooked)


def compare_with_editor_only_folders(
    required: set[str], cooked: set[str], editor_only_folders: list[str]
) -> tuple[list[str], list[str]]:
    """Return (unexplained missing, explicitly allowlisted editor-only missing).

    Folder matches are path-component bounded, so allowing ``/Game/Foo`` does
    not also exclude ``/Game/Foobar``. Callers must supply reviewed folder
    roots; the checker has no implicit exemptions.
    """
    folders = {package_path(folder).rstrip("/") for folder in editor_only_folders}
    missing = required - cooked

    def is_allowlisted(path: str) -> bool:
        return any(path == folder or path.startswith(folder + "/") for folder in folders)

    excluded = sorted(path for path in missing if is_allowlisted(path))
    remaining = sorted(missing - set(excluded))
    return remaining, excluded


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--required", required=True, type=Path, help="H2 closure package list, one /Game path per line")
    manifest_group = parser.add_mutually_exclusive_group(required=True)
    manifest_group.add_argument("--manifest", type=Path, help="authoritative cooked-package manifest or UAT cook log")
    manifest_group.add_argument("--normalized-manifest", type=Path, help="validated normalized JSON export; not a raw UAT manifest")
    parser.add_argument("--json", action="store_true", help="print deterministic machine-readable comparison summary")
    parser.add_argument(
        "--editor-only-folder", action="append", default=[], metavar="/Game/Folder",
        help="explicitly reviewed editor-only reference folder to exclude from missing (repeatable)",
    )
    args = parser.parse_args()
    try:
        required = read_required(args.required)
        metadata = None
        manifest_path = args.manifest or args.normalized_manifest
        if args.normalized_manifest:
            normalized = json.loads(args.normalized_manifest.read_text(encoding="utf-8-sig"))
            cooked, issues, roots = validate_normalized_manifest(normalized, required)
            if issues:
                for issue in issues:
                    print("INVALID " + issue, file=sys.stderr)
                return 2
            metadata = {"build_id": normalized["build_id"], "configuration": normalized["configuration"],
                        "root_packages": roots}
        else:
            cooked = read_cooked(args.manifest)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    missing, editor_only = compare_with_editor_only_folders(required, cooked, args.editor_only_folder)
    if args.json:
        print(json.dumps(build_summary(required, cooked, missing, editor_only, args.required, manifest_path, metadata),
                         ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if required and not missing else 1
    print(
        f"[G044_COOK_MANIFEST] required={len(required)} cooked_game_paths={len(cooked)} "
        f"missing={len(missing)} editor_only_excluded={len(editor_only)}"
    )
    for path in editor_only:
        print(f"EDITOR_ONLY {path}")
    for path in missing:
        print(f"MISSING {path}")
    print("VERDICT " + ("PASS" if required and not missing else "FAIL"))
    return 0 if required and not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
