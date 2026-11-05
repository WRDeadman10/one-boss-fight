#!/usr/bin/env python3
"""Verify normalized encounter soft-reference reachability against a cook package manifest.

Inputs are explicit JSON exports; this tool does not query Unreal or infer edges.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


GRAPH_SCHEMA = "onebossfight.encounter-package-graph/v1"
GRAPH_SCHEMA_V2 = "onebossfight.encounter-package-graph/v2"
MANIFEST_SCHEMA = "onebossfight.cook-package-manifest/v1"
MANIFEST_SCHEMA_V2 = "onebossfight.cook-package-manifest/v2"


def _render_chain(chain: list[str]) -> str:
    return chain[0] + "".join(chain[1:]) if chain else ""


def _package_path(value: Any, label: str, issues: list[str]) -> str | None:
    if (not isinstance(value, str) or not value.startswith("/") or "." in value
            or any(part in ("", ".", "..") for part in value.split("/")[1:])):
        issues.append(f"{label} must be a rooted package path without object suffix")
        return None
    return value


def reachable(graph: Any) -> tuple[set[str], dict[str, list[str]], list[str]]:
    issues: list[str] = []
    if not isinstance(graph, dict) or graph.get("schema") not in (GRAPH_SCHEMA, GRAPH_SCHEMA_V2):
        return set(), {}, [f"graph schema must be {GRAPH_SCHEMA} or {GRAPH_SCHEMA_V2}"]
    graph_v2 = graph["schema"] == GRAPH_SCHEMA_V2
    roots_raw, packages_raw = graph.get("roots"), graph.get("packages")
    if not isinstance(roots_raw, list) or not roots_raw or not isinstance(packages_raw, dict):
        return set(), {}, ["graph requires nonempty roots and packages object"]
    packages: dict[str, list[str]] = {}
    for raw_path, node in packages_raw.items():
        path = _package_path(raw_path, "package key", issues)
        if path is None:
            continue
        if not isinstance(node, dict) or not isinstance(node.get("references"), list):
            issues.append(f"{raw_path}: references must be an array")
            continue
        refs: list[tuple[str, str]] = []
        for index, raw_ref in enumerate(node["references"]):
            if graph_v2:
                if not isinstance(raw_ref, dict):
                    issues.append(f"{raw_path}.references[{index}] must preserve source_path and target_package")
                    continue
                source_path = raw_ref.get("source_path")
                if not isinstance(source_path, str) or not source_path.strip():
                    issues.append(f"{raw_path}.references[{index}].source_path must be nonempty")
                    continue
                raw_target = raw_ref.get("target_package")
                target = _package_path(raw_target, f"{raw_path}.references[{index}].target_package", issues)
                if target:
                    refs.append((target, source_path))
            else:
                target = _package_path(raw_ref, f"{raw_path}.references[{index}]", issues)
                if target:
                    refs.append((target, ""))
        packages[path] = refs
    roots: list[str] = []
    for index, raw_root in enumerate(roots_raw):
        root = _package_path(raw_root, f"roots[{index}]", issues)
        if root:
            roots.append(root)
    visited: set[str] = set()
    chains: dict[str, list[str]] = {}
    stack = [(root, [root]) for root in reversed(roots)]
    while stack:
        path, chain = stack.pop()
        if path in visited:
            continue
        visited.add(path)
        chains[path] = chain
        for ref, source_path in reversed(packages.get(path, [])):
            if ref not in visited:
                edge = f" --[{source_path}]--> {ref}" if source_path else f" -> {ref}"
                stack.append((ref, chain + [edge]))
    for path in sorted(visited):
        if path not in packages:
            issues.append(f"reachable package missing from graph: {_render_chain(chains[path])}")
    return visited, chains, issues


def verify(graph: Any, manifest: Any) -> list[str]:
    expected, chains, issues = reachable(graph)
    if not isinstance(manifest, dict) or manifest.get("schema") not in (MANIFEST_SCHEMA, MANIFEST_SCHEMA_V2):
        return issues + [f"manifest schema must be {MANIFEST_SCHEMA} or {MANIFEST_SCHEMA_V2}"]
    graph_object = graph if isinstance(graph, dict) else {}
    if manifest["schema"] == MANIFEST_SCHEMA_V2:
        for key in ("build_id", "configuration"):
            if not isinstance(manifest.get(key), str) or not manifest[key].strip():
                issues.append(f"manifest {key} must be nonempty")
            elif graph_object.get(key) != manifest[key]:
                issues.append(f"graph/manifest {key} mismatch: {graph_object.get(key)!r} != {manifest[key]!r}")
        mounts = manifest.get("mount_roots")
        if not isinstance(mounts, list) or not mounts:
            issues.append("manifest mount_roots must be a nonempty array")
        else:
            for index, mount in enumerate(mounts):
                if (not isinstance(mount, dict) or not isinstance(mount.get("mount_point"), str)
                        or not mount["mount_point"].startswith("/") or not isinstance(mount.get("filesystem_root"), str)
                        or not mount["filesystem_root"].strip()):
                    issues.append(f"manifest.mount_roots[{index}] must preserve mount_point and filesystem_root")
    entries = manifest.get("packages")
    if not isinstance(entries, list):
        return issues + ["manifest packages must be an array"]
    included: set[str] = set()
    for index, raw in enumerate(entries):
        package = _package_path(raw, f"manifest.packages[{index}]", issues)
        if package:
            if package in included:
                issues.append(f"duplicate manifest package: {package}")
            included.add(package)
    for package in sorted(expected - included):
        issues.append(f"missing reachable package: {_render_chain(chains[package])}")
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", type=Path, help="normalized selection dependency graph JSON")
    parser.add_argument("manifest", type=Path, help="normalized cook package manifest JSON")
    args = parser.parse_args(argv)
    try:
        graph = json.loads(args.graph.read_text(encoding="utf-8"))
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"INCONCLUSIVE: cannot read valid UTF-8 inputs: {exc}", file=sys.stderr)
        return 2
    issues = verify(graph, manifest)
    if issues:
        for issue in issues:
            print("FAIL: " + issue)
        return 1
    count = len(reachable(graph)[0])
    print(f"PASS: {count} reachable encounter packages are present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
