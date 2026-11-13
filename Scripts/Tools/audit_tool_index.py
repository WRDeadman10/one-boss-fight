#!/usr/bin/env python3
"""Check Documentation/Boss/TOOLS.md script paths and their CLI --help support."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

COMMAND = re.compile(r"\b(?:py|python(?:3)?)\s+(Scripts/Tools/[A-Za-z0-9_.-]+\.py)")
FLAG = re.compile(r"--[A-Za-z][A-Za-z0-9_-]*")
INLINE = re.compile(r"`([^`]+)`")


def indexed_tools(markdown: str) -> list[str]:
    return sorted(indexed_commands(markdown))


def indexed_commands(markdown: str) -> dict[str, set[str]]:
    commands: dict[str, set[str]] = {}
    for inline in INLINE.findall(markdown):
        match = COMMAND.search(inline)
        if match:
            commands.setdefault(match.group(1), set()).update(FLAG.findall(inline[match.end():]))
    return commands


def audit(root: Path, index: Path) -> list[str]:
    issues = []
    for relative, flags in indexed_commands(index.read_text(encoding="utf-8", errors="replace")).items():
        script = root / Path(relative)
        if not script.is_file():
            issues.append(f"MISSING {relative}")
            continue
        try:
            result = subprocess.run([sys.executable, str(script), "--help"], cwd=root,
                                    capture_output=True, text=True, timeout=15)
        except (OSError, subprocess.TimeoutExpired) as error:
            issues.append(f"HELP ERROR {relative}: {error}")
            continue
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip().splitlines()
            issues.append(f"HELP UNSUPPORTED {relative}: " + (detail[-1] if detail else f"exit={result.returncode}"))
        else:
            help_text = result.stdout + result.stderr
            for flag in sorted(flags):
                if flag not in help_text:
                    issues.append(f"FLAG UNSUPPORTED {relative}: {flag}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--index", type=Path, default=Path(__file__).resolve().parents[2] / "Documentation" / "Boss" / "TOOLS.md")
    args = parser.parse_args()
    root = args.root.resolve()
    index = args.index if args.index.is_absolute() else root / args.index
    if not index.is_file():
        parser.error(f"missing tool index: {index}")
    issues = audit(root, index)
    for issue in issues:
        print(issue)
    print(f"indexed_tools={len(indexed_tools(index.read_text(encoding='utf-8')))} issues={len(issues)}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
