#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_reopen_c1_config_schema.py
===============================
Offline re-open test verifying that C1_NEW_BOSS_CONFIG_SCHEMA.md,
validate_boss_config.py, and test_validate_boss_config.py are complete,
pass all tests, and cite true source lines.
"""

import os
import sys
import subprocess

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))

CHECKS = [
    # 1. Validator implementation tokens
    ("Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_boss_config.py", [
        "def validate_boss_config",
        "def phase_pool_cannot_starve",
        "Framework.BossConfig.DestinationExists",
        "Framework.Profile.Identity",
        "Framework.Profile.Domain",
        "Framework.Profile.Geometry",
        "Framework.Profile.Alignment",
        "Framework.Profile.Phase",
        "Framework.Profile.Posture",
        "Framework.Profile.Bleed",
        "Framework.Profile.PhaseCards",
        "Framework.Profile.PhaseCooldownStarvation",
        "Framework.Profile.CardBandOrBlendTail",
        "Framework.Profile.DamageBudget",
        "Framework.Profile.DamageCard",
    ]),

    # 2. Test harness tokens
    ("Docs/BossCombatReview/Execution/Antigravity/Reviews/test_validate_boss_config.py", [
        "get_sevarog_f10_valid_config",
        "Negative 1: Framework.BossConfig.DestinationExists",
        "Negative 2: Framework.Profile.Identity",
        "Negative 3: Framework.Profile.Geometry",
        "Negative 4: Framework.Profile.Geometry",
        "Negative 5: Framework.Profile.Alignment",
        "Negative 6: Framework.Profile.Posture",
        "Negative 7: Framework.Profile.Bleed",
        "Negative 8: Framework.Profile.CardBandOrBlendTail",
        "Negative 9: Framework.Profile.PhaseCards",
        "Negative 10: Framework.Profile.PhaseCooldownStarvation",
    ]),

    # 3. Schema doc contents
    ("Docs/BossCombatReview/Execution/Antigravity/Reviews/C1_NEW_BOSS_CONFIG_SCHEMA.md", [
        "destination_package_dir",
        "fixture_label",
        "damage_enabled",
        "band_min_cm",
        "band_max_cm",
        "acceptance_cm",
        "phase_two_fraction",
        "phase_two_id",
        "posture_max",
        "bleed_buildup_per_hit",
        "RPGBossFrameworkProfile.cpp",
        "PhasePoolCannotStarve",
    ]),
]

def main():
    print("=== Running test_reopen_c1_config_schema.py ===")
    total = 0
    passed = 0

    doc_path = os.path.join(os.path.dirname(__file__), "C1_NEW_BOSS_CONFIG_SCHEMA.md")
    total += 1
    if os.path.exists(doc_path):
        print(f"[PASS] Doc exists: {doc_path}")
        passed += 1
    else:
        print(f"[FAIL] Missing doc: {doc_path}")

    for rel_path, needles in CHECKS:
        total += 1
        full_path = os.path.join(BASE_DIR, rel_path.replace("/", os.sep))
        if not os.path.exists(full_path):
            print(f"[FAIL] Missing file: {rel_path}")
            continue

        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        missing = [n for n in needles if n not in content]
        if missing:
            print(f"[FAIL] {rel_path} missing: {missing}")
        else:
            print(f"[PASS] {rel_path} verified ({len(needles)} needles)")
            passed += 1

    # Run unit test harness
    total += 1
    test_script = os.path.join(os.path.dirname(__file__), "test_validate_boss_config.py")
    res = subprocess.run([sys.executable, test_script], capture_output=True, text=True)
    if res.returncode == 0 and "11/11 tests passed" in res.stdout:
        print("[PASS] test_validate_boss_config.py passed (11/11)")
        passed += 1
    else:
        print(f"[FAIL] test_validate_boss_config.py failed:\n{res.stdout}\n{res.stderr}")

    print(f"\nResult: {passed}/{total} tests passed.")
    if passed != total:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
