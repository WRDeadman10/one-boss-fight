#!/usr/bin/env python3
"""Report declared source and destination asset paths in an authoring script."""
from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path

ASSET_PATH = re.compile(r"/Game/[A-Za-z0-9_./-]+")


def literal(node: ast.AST, values: dict[str, object]):
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, int, float, bool)):
        return node.value
    if isinstance(node, ast.Name):
        return values.get(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = literal(node.left, values), literal(node.right, values)
        if isinstance(left, str) and isinstance(right, str):
            return left + right
    if isinstance(node, (ast.List, ast.Tuple)):
        result = [literal(item, values) for item in node.elts]
        return result if all(item is not None for item in result) else None
    if isinstance(node, ast.Dict):
        result = {literal(k, values): literal(v, values) for k, v in zip(node.keys, node.values)}
        return result if all(k is not None and v is not None for k, v in result.items()) else None
    return None


def declarations(script: Path):
    source = script.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(source, filename=str(script))
    values: dict[str, object] = {}
    rows = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        names = [target.id for target in node.targets if isinstance(target, ast.Name)] if isinstance(node, ast.Assign) else ([node.target.id] if isinstance(node.target, ast.Name) else [])
        value = literal(node.value, values)
        for name in names:
            if value is not None:
                values[name] = value
            if any(marker in name.upper() for marker in ("PROFILE", "LEVEL", "MAP", "ASSET", "DEST", "SOURCE", "_SRC", "_DST")):
                rows.append((node.lineno, name, value))
    return source, rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", type=Path)
    parser.add_argument("--evidence", type=Path, action="append", default=[], help="log file or directory to search for declared asset paths")
    args = parser.parse_args()
    if not args.script.is_file():
        parser.error(f"authoring script does not exist: {args.script}")
    try:
        source, rows = declarations(args.script)
    except (OSError, SyntaxError) as exc:
        print(f"ERROR cannot inspect script: {exc}")
        return 2
    source_rows = [row for row in rows if any(key in row[1].upper() for key in ("SOURCE", "_SRC"))]
    dest_rows = [row for row in rows if any(key in row[1].upper() for key in ("DEST", "_DST", "_PATH")) or row[1].upper() in {"PROFILE_NAME", "LEVEL_NAME", "MAP_NAME"}]
    print(f"SCRIPT {args.script.resolve()}")
    for label, selected in (("SOURCE", source_rows), ("DESTINATION", dest_rows)):
        if not selected:
            print(f"{label} unknown (no statically declared source/destination variable)")
        for line, name, value in selected:
            print(f"{label} line={line} variable={name} value={value if value is not None else 'dynamic/unknown'}")
    asset_literals = sorted(set(ASSET_PATH.findall(source)))
    if asset_literals:
        print("ASSET_PATH_LITERALS " + ", ".join(asset_literals))
    evidence_refs = 0
    for evidence in args.evidence:
        paths = [evidence] if evidence.is_file() else sorted(evidence.rglob("*.log")) if evidence.is_dir() else []
        for log in paths:
            content = log.read_text(encoding="utf-8", errors="replace")
            for line_number, line in enumerate(content.splitlines(), 1):
                if any(path in line for path in asset_literals):
                    print(f"EVIDENCE {log}:{line_number}: {line.strip()}")
                    evidence_refs += 1
    if args.evidence and not evidence_refs:
        print("EVIDENCE no declared script asset path was found in supplied logs")
    print("No assets were loaded, saved, moved, or deleted by this report.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
