#!/usr/bin/env python3
"""
verify_a318_ki149_citations.py
==============================
Verifies exact file:line citations in KI149_COOLDOWN_EXHAUSTION_DESIGN.md against Source/.
Runs 100% offline.
"""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[5]

CITATIONS = [
    (
        "Source/OneBossFight/Player/RPGBossFrameworkProfile.h",
        47,
        "AttackCount"
    ),
    (
        "Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp",
        91,
        "InOne=0,InTwo=0"
    ),
    (
        "Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp",
        93,
        "Framework.Profile.PhaseCards"
    ),
    (
        "Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp",
        114,
        "Framework.Selector.NoCandidate"
    ),
    (
        "Source/OneBossFight/Player/RPGBossMoveSelector.cpp",
        41,
        "Selector.Cooldown"
    )
]

def main():
    print("Verifying KI149 design citations...")
    all_ok = True
    for rel_path, line_no, token in CITATIONS:
        full_path = REPO_ROOT / rel_path
        if not full_path.is_file():
            print(f"[FAIL] Missing file: {rel_path}")
            all_ok = False
            continue
        lines = full_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if line_no > len(lines):
            print(f"[FAIL] {rel_path}:{line_no} beyond file length {len(lines)}")
            all_ok = False
            continue
        actual_line = lines[line_no - 1]
        if token not in actual_line:
            print(f"[FAIL] {rel_path}:{line_no} does not contain '{token}': {actual_line.strip()[:60]}")
            all_ok = False
        else:
            print(f"[OK]   {rel_path}:{line_no} contains '{token}'")

    if not all_ok:
        sys.exit(1)
    print("All 5 citations verified successfully!")
    sys.exit(0)

if __name__ == "__main__":
    main()
