#!/usr/bin/env python3
"""
verify_a255_staging.py
======================
Offline verification of Greystone Persona Click Steps and Staged C++ Subsystem/Component (A-255).
"""

from pathlib import Path

BASE_DIR = Path("Docs/BossCombatReview/Execution/Antigravity/GreystoneBridge")
STAGING_DIR = BASE_DIR / "Staging"

EXPECTED_STAGED_FILES = [
    "RPGGreystoneVisualBridgeComponent.h",
    "RPGGreystoneVisualBridgeComponent.cpp",
    "RPGGreystoneVisualBridgeSubsystem.h",
    "RPGGreystoneVisualBridgeSubsystem.cpp",
    "WEAPON_OPTION_AB_MEASUREMENT_PLAN.md"
]

REFERENCED_CONTENT_ASSETS = [
    Path("Content/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone.uasset"),
    Path("Content/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone_Skeleton.uasset"),
    Path("Content/OneBossFight/GreystonePack/RTG_CombatMannequin_To_Greystone.uasset"),
]

def main():
    print("================================================================================")
    print(" VERIFYING A-255 GREYSTONE PERSONA CLICK STEPS & STAGED C++ INJECTOR")
    print("================================================================================")

    # 1. Verify GREYSTONE_PERSONA_CLICK_STEPS.md
    click_steps = BASE_DIR / "GREYSTONE_PERSONA_CLICK_STEPS.md"
    assert click_steps.is_file(), f"Missing {click_steps}"
    raw_steps = click_steps.read_bytes()
    assert b"\r\r\n" not in raw_steps, "No double CRLF in click steps"
    assert b"ABP_Greystone_VisualBridge" in raw_steps
    assert b"Retarget Pose From Mesh" in raw_steps
    assert b"RTG_CombatMannequin_To_Greystone" in raw_steps
    assert raw_steps.endswith(b"\r\n"), "Must end in CRLF"
    print(f"[OK] GREYSTONE_PERSONA_CLICK_STEPS.md verified: {len(raw_steps):,} bytes, clean CRLF.")

    # 2. Verify Staged Files
    for filename in EXPECTED_STAGED_FILES:
        file_path = STAGING_DIR / filename
        assert file_path.is_file(), f"Missing staged file: {file_path}"
        raw = file_path.read_bytes()
        assert b"\r\r\n" not in raw, f"Double CRLF in {filename}"
        assert raw.endswith(b"\r\n"), f"Must end in CRLF: {filename}"
        print(f"[OK] Staged file {filename} verified: {len(raw):,} bytes, clean CRLF.")

    # 3. Verify Include Order: Own Header First
    cpp_comp = (STAGING_DIR / "RPGGreystoneVisualBridgeComponent.cpp").read_text(encoding="utf-8").splitlines()
    assert '#include "RPGGreystoneVisualBridgeComponent.h"' in cpp_comp[0], "Component .cpp must include own header first"
    print("[OK] Component .cpp verified: own header first on line 1.")

    cpp_sub = (STAGING_DIR / "RPGGreystoneVisualBridgeSubsystem.cpp").read_text(encoding="utf-8").splitlines()
    assert '#include "RPGGreystoneVisualBridgeSubsystem.h"' in cpp_sub[0], "Subsystem .cpp must include own header first"
    print("[OK] Subsystem .cpp verified: own header first on line 1.")

    # 4. Verify Content Assets on Disk
    for asset in REFERENCED_CONTENT_ASSETS:
        assert asset.is_file(), f"Referenced asset missing on disk: {asset}"
        print(f"[OK] Referenced asset confirmed on disk: {asset.name}")

    print("\n================================================================================")
    print(" ALL A-255 VERIFICATION CHECKS 100% PASSED OFFLINE")
    print("================================================================================")

if __name__ == "__main__":
    main()
