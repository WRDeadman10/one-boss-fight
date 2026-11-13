#!/usr/bin/env python3
"""Normalize an explicit captured cook-manifest export without inferring packages."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))  # BP-17: sibling atomic_io as a script or via -m
from atomic_io import atomic_write_text
from typing import Any

EXPORT_SCHEMA = "onebossfight.cook-package-manifest-export/v1"
OUTPUT_SCHEMA = "onebossfight.cook-package-manifest/v2"


class InputError(ValueError):
    pass


def _package_name(value: Any) -> bool:
    return (isinstance(value, str) and value.startswith("/") and "." not in value
            and all(part not in ("", ".", "..") for part in value.split("/")[1:]))


def normalize(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schema") != EXPORT_SCHEMA:
        raise InputError(f"input schema must be {EXPORT_SCHEMA}")
    build_id, configuration = value.get("build_id"), value.get("configuration")
    if not isinstance(build_id, str) or not build_id.strip():
        raise InputError("build_id must be nonempty captured text")
    if not isinstance(configuration, str) or not configuration.strip():
        raise InputError("configuration must be nonempty captured text")
    roots, packages = value.get("mount_roots"), value.get("packages")
    if not isinstance(roots, list) or not roots or not isinstance(packages, list):
        raise InputError("export requires mount_roots and packages arrays")
    mounts: list[dict[str, str]] = []
    for index, mount in enumerate(roots):
        if not isinstance(mount, dict):
            raise InputError(f"mount_roots[{index}] must be an object")
        point, filesystem = mount.get("mount_point"), mount.get("filesystem_root")
        if not isinstance(point, str) or not point.startswith("/"):
            raise InputError(f"mount_roots[{index}].mount_point must be rooted")
        if not isinstance(filesystem, str) or not filesystem.strip():
            raise InputError(f"mount_roots[{index}].filesystem_root must be captured text")
        mounts.append({"mount_point": point, "filesystem_root": filesystem})
    normalized_packages: list[str] = []
    for index, package in enumerate(packages):
        name = package.get("package_name") if isinstance(package, dict) else package
        if not _package_name(name):
            raise InputError(f"packages[{index}].package_name must be a rooted package name")
        if name in normalized_packages:
            raise InputError(f"duplicate package entry: {name}")
        normalized_packages.append(name)
    return {
        "schema": OUTPUT_SCHEMA,
        "build_id": build_id,
        "configuration": configuration,
        "mount_roots": mounts,
        "packages": normalized_packages,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path, help="captured cook-manifest export JSON")
    parser.add_argument("--output", type=Path, help="normalized manifest path (stdout when omitted)")
    args = parser.parse_args(argv)
    if args.output:
        try:
            aliases_input = args.output.resolve() == args.export.resolve()
            if not aliases_input and args.output.exists():
                aliases_input = args.output.samefile(args.export)
        except OSError as exc:
            print(f"INCONCLUSIVE: cannot safely compare export/output paths: {exc}", file=sys.stderr)
            return 2
        if aliases_input:
            print("INCONCLUSIVE: output aliases captured export; refusing to overwrite source evidence", file=sys.stderr)
            return 2
    try:
        value = json.loads(args.export.read_text(encoding="utf-8-sig"))
        encoded = json.dumps(normalize(value), sort_keys=True, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            atomic_write_text(args.output, encoded)  # BP-17: atomic replace; same LF bytes as before
        else:
            sys.stdout.write(encoded)
    except (OSError, UnicodeError, json.JSONDecodeError, InputError) as exc:
        print(f"INCONCLUSIVE: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
