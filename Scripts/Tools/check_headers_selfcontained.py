#!/usr/bin/env python3
"""Static C++ header include audit; reports suspects only, never claims compilation."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

INCLUDE = re.compile(r'^\s*#\s*include\s+[<"]([^>"]+)[>"]', re.M)


def inspect(path: Path, source_root: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    includes = INCLUDE.findall(text)
    suspects = []
    std_headers = {"cmath", "limits", "algorithm", "cstdint", "string", "utility", "vector", "random"}
    if "std::" in text and not any(item in std_headers or item.startswith("std") for item in includes):
        suspects.append("uses std:: without an apparent standard-library include")
    core_names = ("FMath::", "FVector", "FName", "FString", "TArray<", "TMap<", "TSet<", "TSharedPtr<", "TUniquePtr<", "FRandomStream")
    if any(name in text for name in core_names) and not any(item.endswith("CoreMinimal.h") or item.endswith("CoreTypes.h") for item in includes):
        suspects.append("uses common Unreal core types without CoreMinimal/CoreTypes include")
    generated = [item for item in includes if item.endswith(".generated.h")]
    if generated and (not includes or includes[-1] != generated[-1]):
        suspects.append("generated header is not the final include")
    for item in includes:
        if item.startswith(("Player/", "Boss/", "Combat/")) and not (source_root / item).is_file():
            suspects.append(f"project include not found: {item}")
    return suspects


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    repo = args.root.resolve()
    source = repo / "Source/OneBossFight"
    files = sorted(source.rglob("*.h"))
    total = 0
    for path in files:
        for issue in inspect(path, source):
            total += 1
            print(f"{path.relative_to(repo)}: {issue}")
    print(f"headers={len(files)} suspect_items={total}; static heuristic only, not a standalone compile")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
