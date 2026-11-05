#!/usr/bin/env python3
"""Find literal known-map paths passed to load_asset in Scripts/Editor Python."""
from __future__ import annotations

import argparse
import ast
from pathlib import Path


def static_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = static_string(node.left), static_string(node.right)
        if left is not None and right is not None:
            return left + right
    return None


def known_maps(content_dir: Path) -> set[str]:
    result = set()
    for path in content_dir.rglob("*.umap"):
        relative = path.relative_to(content_dir).with_suffix("").as_posix()
        result.add("/Game/" + relative)
    return result


def scan_text(text: str, known: set[str], path: str = "<memory>") -> list[str]:
    try:
        tree = ast.parse(text, filename=path)
    except SyntaxError as error:
        return [f"{path}:{error.lineno}: Python parse error: {error.msg}"]
    findings = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute) or node.func.attr != "load_asset":
            continue
        if not node.args:
            continue
        value = static_string(node.args[0])
        if value is None:
            continue
        normalized = value.split(".", 1)[0]
        if normalized in known:
            findings.append(f"{path}:{node.lineno}: load_asset uses map package {normalized}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--editor", type=Path, default=Path(__file__).parents[1] / "Editor")
    parser.add_argument("--content", type=Path, default=Path(__file__).parents[2] / "Content")
    args = parser.parse_args()
    maps = known_maps(args.content)
    files = sorted(args.editor.rglob("*.py"))
    findings = []
    unparsed = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        result = scan_text(text, maps, path.as_posix())
        if result and "Python parse error:" in result[0]:
            unparsed.append((path, result[0]))
        else:
            findings.extend(result)
    print(f"[EDITOR_MAP_LOADS] scripts={len(files)} known_maps={len(maps)} violations={len(findings)} unparsed={len(unparsed)}")
    for finding in findings:
        print("VIOLATION " + finding)
    for path, message in unparsed:
        print(f"UNPARSED {path.as_posix()}: {message}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
