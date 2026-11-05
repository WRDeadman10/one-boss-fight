#!/usr/bin/env python3
"""Compare required G044 /Game package paths with a packaged cook manifest.

Inputs are UTF-8 text. The required file contains one exact /Game package path
per non-comment line; the cook manifest may be a UAT log or manifest text.
This is a deterministic offline comparison, not proof that a particular build
was packaged or launched.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

PACKAGE = re.compile(r"/Game/[A-Za-z0-9_./-]+", re.IGNORECASE)


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
    parser.add_argument("--manifest", required=True, type=Path, help="authoritative cooked-package manifest or UAT cook log")
    parser.add_argument(
        "--editor-only-folder", action="append", default=[], metavar="/Game/Folder",
        help="explicitly reviewed editor-only reference folder to exclude from missing (repeatable)",
    )
    args = parser.parse_args()
    required = read_required(args.required)
    cooked = read_cooked(args.manifest)
    missing, editor_only = compare_with_editor_only_folders(required, cooked, args.editor_only_folder)
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
