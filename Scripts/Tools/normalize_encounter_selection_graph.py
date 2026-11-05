#!/usr/bin/env python3
"""Normalize an explicit Editor selection-graph export for cook reachability checks.

This tool consumes captured JSON only; it never queries the Editor or guesses asset refs.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

EXPORT_SCHEMA = "onebossfight.encounter-selection-graph-export/v1"
GRAPH_SCHEMA = "onebossfight.encounter-package-graph/v2"


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
    roots, raw_packages = value.get("roots"), value.get("packages")
    if not isinstance(roots, list) or not roots or not isinstance(raw_packages, dict):
        raise InputError("export requires nonempty roots and packages object")
    packages: dict[str, dict[str, list[dict[str, str]]]] = {}
    for package, node in raw_packages.items():
        if not _package_name(package):
            raise InputError(f"invalid package key: {package!r}")
        if not isinstance(node, dict) or not isinstance(node.get("references"), list):
            raise InputError(f"{package}: references must be an array")
        refs: list[dict[str, str]] = []
        for index, ref in enumerate(node["references"]):
            if not isinstance(ref, dict):
                raise InputError(f"{package}.references[{index}] must preserve source_path and target_package")
            source, target = ref.get("source_path"), ref.get("target_package")
            if not isinstance(source, str) or not source.strip():
                raise InputError(f"{package}.references[{index}].source_path must be nonempty")
            if not _package_name(target):
                raise InputError(f"{package}.references[{index}].target_package must be a rooted package name")
            refs.append({"source_path": source, "target_package": target})
        packages[package] = {"references": refs}
    for index, root in enumerate(roots):
        if not _package_name(root):
            raise InputError(f"roots[{index}] must be a rooted package name")
    return {
        "schema": GRAPH_SCHEMA,
        "build_id": build_id,
        "configuration": configuration,
        "roots": list(roots),
        "packages": packages,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path, help="captured Editor graph export JSON")
    parser.add_argument("--output", type=Path, help="normalized graph path (stdout when omitted)")
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
        source = json.loads(args.export.read_text(encoding="utf-8"))
        result = normalize(source)
        encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(encoded, encoding="utf-8", newline="\n")
        else:
            sys.stdout.write(encoded)
    except (OSError, UnicodeError, json.JSONDecodeError, InputError) as exc:
        print(f"INCONCLUSIVE: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
