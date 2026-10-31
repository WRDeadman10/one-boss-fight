#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_reopen_c1_howto.py
=======================
Offline re-open test verifying that Documentation/Boss/C1_NEW_BOSS_HOWTO.md
exists, every cited script and file exists on disk, every troubleshooting
token is authentic, and command syntax / negative assertions satisfy review defects.
"""

import os
import re
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

BASE_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", "..", "..", ".."))

FILES_TO_CHECK = [
    "Docs/BossCombatReview/Execution/Claude/C1/new_boss.py",
    "Docs/BossCombatReview/Execution/Claude/run_editor_script.ps1",
    "Docs/BossCombatReview/Execution/Claude/F4/run_pie.ps1",
    "Docs/BossCombatReview/Execution/Antigravity/Reviews/grade_f10_log.py",
    "Docs/BossCombatReview/Execution/Antigravity/MoveCards/bake_blade_path.py",
    "Docs/BossCombatReview/Execution/Antigravity/MoveCards/author_move_cards.py",
    "Docs/BossCombatReview/Execution/Antigravity/MoveCards/verify_baked_cards.py",
    "Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp",
    "Source/OneBossFight/Player/RPGBossMoveCard.cpp",
]

TOKENS_TO_VERIFY = [
    ("Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp", [
        "Framework.Profile.Identity",
        "Framework.Profile.Domain",
        "Framework.Profile.Geometry",
        "Framework.Profile.Alignment",
        "Framework.Profile.Phase",
        "Framework.Profile.PhaseCards",
        "Framework.Profile.PhaseCooldownStarvation",
        "Framework.Profile.Posture",
        "Framework.Profile.Bleed",
        "Framework.Profile.CardBandOrBlendTail",
        "Framework.Profile.DamageBudget",
        "Framework.Profile.AnimSkeleton",
        "HasSlotNode",
    ]),
    ("Source/OneBossFight/Player/RPGBossMoveCard.cpp", [
        "MoveCard.Socket",
        "MoveCard.Timeline",
        "MoveCard.UnsupportedRootMotion",
        "MoveCard.BakedSamples",
    ]),
]


def main():
    print("=== Running test_reopen_c1_howto.py ===")
    total = 0
    passed = 0

    doc_path = os.path.join(BASE_DIR, "Documentation", "Boss", "C1_NEW_BOSS_HOWTO.md")
    total += 1
    if os.path.exists(doc_path) and os.path.getsize(doc_path) > 0:
        print(f"[PASS] Doc exists: {doc_path} ({os.path.getsize(doc_path)} bytes)")
        passed += 1
    else:
        print(f"[FAIL] Missing or empty doc: {doc_path}")

    with open(doc_path, "r", encoding="utf-8") as f:
        doc_content = f.read()

    for rel_path in FILES_TO_CHECK:
        total += 1
        full_path = os.path.join(BASE_DIR, rel_path.replace("/", os.sep))
        if os.path.exists(full_path):
            print(f"[PASS] File exists: {rel_path}")
            passed += 1
        else:
            print(f"[FAIL] Missing cited file: {rel_path}")

    for rel_path, tokens in TOKENS_TO_VERIFY:
        total += 1
        full_path = os.path.join(BASE_DIR, rel_path.replace("/", os.sep))
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        missing = [t for t in tokens if t not in content]
        if missing:
            print(f"[FAIL] {rel_path} missing tokens: {missing}")
        else:
            print(f"[PASS] {rel_path} verified all {len(tokens)} tokens")
            passed += 1

    # Check (1): Every -OutDir argument starts with a drive letter
    total += 1
    outdir_matches = re.findall(r'-OutDir\s+"([^"]+)"', doc_content)
    if outdir_matches and all(re.match(r'^[A-Za-z]:[\\/]', p) for p in outdir_matches):
        print(f"[PASS] All {len(outdir_matches)} -OutDir paths are absolute drive paths: {outdir_matches}")
        passed += 1
    else:
        print(f"[FAIL] Non-absolute -OutDir found: {outdir_matches}")

    # Check (2): -OutDir must be absolute sentence present
    total += 1
    if "-OutDir must be absolute, the editor does not run from the repo root" in doc_content:
        print("[PASS] Absolute -OutDir explanation sentence confirmed")
        passed += 1
    else:
        print("[FAIL] Missing -OutDir absolute explanation sentence")

    # Check (3): -Inject example is a list of seconds
    total += 1
    inject_match = re.search(r'-Inject\s+"([^"]+)"', doc_content)
    if inject_match and re.match(r'^\d+(\.\d+)?(,\s*\d+(\.\d+)?)*$', inject_match.group(1)):
        print(f"[PASS] -Inject example is comma-separated seconds list: {inject_match.group(1)}")
        passed += 1
    else:
        print(f"[FAIL] Invalid -Inject example: {inject_match.group(1) if inject_match else 'None'}")

    # Check (4): -InjectPie example is a list of seconds
    total += 1
    injectpie_match = re.search(r'-InjectPie\s+"([^"]+)"', doc_content)
    if injectpie_match and re.match(r'^\d+(\.\d+)?(,\s*\d+(\.\d+)?)*$', injectpie_match.group(1)):
        print(f"[PASS] -InjectPie example is comma-separated seconds list: {injectpie_match.group(1)}")
        passed += 1
    else:
        print(f"[FAIL] Invalid -InjectPie example: {injectpie_match.group(1) if injectpie_match else 'None'}")

    # Check (5): Negative assertion - DriftExceeded absent
    total += 1
    if "DriftExceeded" not in doc_content:
        print("[PASS] Negative assertion passed: 'DriftExceeded' absent")
        passed += 1
    else:
        print("[FAIL] 'DriftExceeded' found in doc")

    # Check (6): Negative assertion - 0.05 absent
    total += 1
    if "0.05" not in doc_content:
        print("[PASS] Negative assertion passed: '0.05' absent")
        passed += 1
    else:
        print("[FAIL] '0.05' found in doc")

    # Check (7): Negative assertion - -Count absent
    total += 1
    if "-Count" not in doc_content:
        print("[PASS] Negative assertion passed: '-Count' absent")
        passed += 1
    else:
        print("[FAIL] '-Count' found in doc")

    # Check (8): Exact deletion rule quoted from CLAUDE.md
    total += 1
    exact_deletion_quote = 'CLAUDE.md: "Never delete and recreate assets that other assets reference"'
    if exact_deletion_quote in doc_content:
        print(f"[PASS] Exact deletion quote verified: '{exact_deletion_quote}'")
        passed += 1
    else:
        print(f"[FAIL] Missing exact deletion quote: '{exact_deletion_quote}'")

    print(f"\nResult: {passed}/{total} tests passed.")
    if passed != total:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
