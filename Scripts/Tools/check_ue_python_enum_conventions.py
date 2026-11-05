#!/usr/bin/env python3
"""Flag known UE Python UENUM prefix/member/integer-cast hazards."""
from __future__ import annotations

import argparse
from pathlib import Path
import re


# These two UE 5.5.4 Python mappings were directly confirmed by C-791/C-852.
ENUMS = {
    "ERPGBossComboOutcome": {"HIT", "WHIFF", "GUARDED", "PARRIED"},
    "ERPGBossDeathMode": {"PACK_MONTAGE", "OWN_CLIP"},
}
ACCESS = re.compile(r"\bunreal\.(E?RPGBoss(?:ComboOutcome|DeathMode))\.([A-Za-z_][A-Za-z0-9_]*)")
INTEGER_CAST = re.compile(r"\bint\s*\(\s*unreal\.(?:RPGBossComboOutcome|RPGBossDeathMode)\.[A-Za-z_][A-Za-z0-9_]*\s*\)")


def scan_text(text: str, path: str = "<memory>", enums: dict[str, set[str]] | None = None) -> list[str]:
    enums = enums or ENUMS
    issues = []
    cpp_names = set(enums)
    python_names = {name[1:]: members for name, members in enums.items()}
    for match in ACCESS.finditer(text):
        class_name, member = match.groups()
        line = text.count("\n", 0, match.start()) + 1
        if class_name in cpp_names:
            issues.append(f"{path}:{line}: E-prefixed reflected enum access {class_name}; use {class_name[1:]}")
        elif member not in python_names.get(class_name, set()):
            issues.append(f"{path}:{line}: unknown/noncanonical UE Python enum member {class_name}.{member}")
    for match in INTEGER_CAST.finditer(text):
        line = text.count("\n", 0, match.start()) + 1
        issues.append(f"{path}:{line}: integer coercion of reflected enum member; compare .value")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--editor", type=Path, default=Path(__file__).resolve().parents[1] / "Editor")
    args = parser.parse_args()
    files = sorted(args.editor.rglob("*.py"))
    findings = [finding for path in files for finding in scan_text(path.read_text(encoding="utf-8", errors="replace"), path.as_posix())]
    print(f"[UE_PY_ENUM] scripts={len(files)} reflected_enum_mappings={len(ENUMS)} findings={len(findings)}")
    for finding in findings:
        print("FINDING " + finding)
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
