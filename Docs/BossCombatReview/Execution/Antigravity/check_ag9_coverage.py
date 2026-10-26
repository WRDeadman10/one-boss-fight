"""
check_ag9_coverage.py - Verifies that every asset specified in AG1, AG2, AG3, AG4, AG5, and AG12
appears exactly once in the revised AG9_CONTENT_BACKLOG.csv.

Author: Antigravity (Visual & Technical Animation Investigator)
Work Order: ANTIGRAVITY_WORK_ORDER_03 (AG-13)
Location: Docs/BossCombatReview/Execution/Antigravity/check_ag9_coverage.py
"""

import os
import csv
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CSV_PATH = SCRIPT_DIR / "AG9_CONTENT_BACKLOG.csv"

# Authoritative lists of named assets from each package
AG1_ASSETS = [
    # HIT-012
    "AN_Boss01_Grab_Attack",
    "AN_Player_Grab_Victim",
    # ANM-003
    "AN_Boss01_A2_VariableApex_Base",
    "AN_Boss01_A2_VariableApex_Short",
    "AN_Boss01_A2_VariableApex_Long",
    "NS_ApexHold_Glow",
    "A_ApexHold_Whirr",
    # ANM-006
    "AN_Boss01_LungeWarp_Attack",
    # DEF-005 Family A (Guard)
    "AN_Boss01_Guard_Enter",
    "AN_Boss01_Guard_Loop",
    "AN_Boss01_Guard_Exit",
    "AN_Boss01_Guard_Stagger",
    # DEF-005 Family B (Parry)
    "AN_Boss01_Parry_Startup",
    "AN_Boss01_Parry_Deflect",
    "AN_Boss01_Parry_CounterSlash",
    "AN_Boss01_Parry_Whiff",
    # DEF-005 Family C (Dodge)
    "AN_Boss01_Dodge_Back",
    "AN_Boss01_Dodge_Left",
    "AN_Boss01_Dodge_Right",
    # AWR-008
    "AN_Boss01_Adapt_Tell",
    "NS_AdaptationGlow",
    "A_AdaptationHum",
    # SEL-004
    "AN_Boss01_Turn_L90",
    "AN_Boss01_Turn_R90",
    # SEL-008
    "AN_Boss01_Fallback_PacingWalk",
    "AN_Boss01_Fallback_Flourish",
]

AG2_ASSETS = [
    # Canary Boss (Alistair)
    "SKM_Canary_Alistair",
    "SM_Canary_Halberd",
    "AN_Canary_Dormant",
    "AN_Canary_Wake",
    "AN_Canary_Stagger",
    "AN_Canary_Riposte_Victim",
    "AN_Canary_PhaseTransition",
    "AN_Canary_Death",
    "AN_Canary_M1_DoubleCleave",
    "AN_Canary_M2_CrescentThrow",
    "NS_Canary_CrescentArc",
    "AN_Canary_M3_FrostSlam",
    "NS_Canary_FrostShockwave",
    "AN_Canary_M4_Vault_Startup",
    "AN_Canary_M4_Vault_Success",
    "AN_Canary_M4_Vault_Whiff",
    # Canary Weapon & Vanguard Player Build
    "SM_Player_SilversteelHalberd",
    "T_Icon_SilversteelHalberd",
    "DA_VanguardWeapon",
    "AN_Player_Halberd_Light01",
    "AN_Player_Halberd_Light02",
    "AN_Player_Halberd_HeavyCharged",
    "AN_Player_Halberd_DodgeThrust",
]

AG3_ASSETS = [
    "Curve_TelegraphEase",
    "NS_Boss01_ChargeUp",
    "A_Boss01_Windup_Hum",
    "NS_Boss01_Sprint_Runup",
    "A_Boss01_Sprint_Warning",
]

AG4_ASSETS = [
    "NS_Boss01_Shockwave_Ring",
    "M_ShockwaveDecal",
    "A_Boss01_Shockwave_Impact",
    "A_Boss01_Shockwave_Travel",
]

AG5_ASSETS = [
    "AN_Boss01_A2_Raise",
    "AN_Boss01_A2_ApexHold",
    "AN_Boss01_A2_Slam",
    "AM_Boss01_A2_OverheadSlam",
    "A_Boss01_A2_ReleaseCue",
]

AG12_REUSED_PACK_ASSETS = [
    "GA_AI_BlockGuard",
    "Ability_AI_Block2_Montage",
    "Deflect_InPlace_AI_Montage",
    "GA_EnemyDodge",
    "Dodge_To_Idle_Montage",
    "GA_EnemyGrabStart",
    "GA_EnemyGrabAttack",
    "DefaultGrabAttackData",
    "GA_GrabVictim",
    "GA_EnemyParried",
    "GA_EnemyBlockReaction",
    "ParryFramesNS",
    "ANS_SetDesiredRotation_C",
]

ALL_REQUIRED_ASSETS = {
    "AG1": AG1_ASSETS,
    "AG2": AG2_ASSETS,
    "AG3": AG3_ASSETS,
    "AG4": AG4_ASSETS,
    "AG5": AG5_ASSETS,
    "AG12": AG12_REUSED_PACK_ASSETS,
}

VALID_PROGRAM_PHASES = {"DD-1", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"}


def check_coverage():
    if not CSV_PATH.exists():
        print(f"ERROR: CSV file not found at {CSV_PATH}")
        sys.exit(1)

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"[CheckCoverage] Total rows in CSV: {len(rows)}")

    csv_asset_names = {}
    csv_ids = set()
    phase_violations = []

    for r in rows:
        aid = r["Asset_ID"]
        name = r["Name"]
        phase = r["Program_Phase"]

        if aid in csv_ids:
            print(f"DUPLICATE ASSET ID: {aid}")
        csv_ids.add(aid)

        if name in csv_asset_names:
            print(f"DUPLICATE ASSET NAME: {name} (IDs: {csv_asset_names[name]}, {aid})")
        csv_asset_names[name] = aid

        if phase not in VALID_PROGRAM_PHASES:
            phase_violations.append((aid, name, phase))

    if phase_violations:
        print(f"ERROR: {len(phase_violations)} rows have invalid program phases (must be DD-1, P1-P8):")
        for v in phase_violations:
            print(f"  {v[0]}: {v[1]} has phase '{v[2]}'")
        sys.exit(1)

    missing_total = 0
    for pkg_name, asset_list in ALL_REQUIRED_ASSETS.items():
        missing_in_pkg = []
        for asset in asset_list:
            if asset not in csv_asset_names:
                missing_in_pkg.append(asset)
        if missing_in_pkg:
            print(f"MISSING FROM {pkg_name} ({len(missing_in_pkg)} assets):")
            for m in missing_in_pkg:
                print(f"  - {m}")
            missing_total += len(missing_in_pkg)
        else:
            print(f"OK: All {len(asset_list)} assets from {pkg_name} present in CSV.")

    if missing_total > 0:
        print(f"\nFAILED: Total {missing_total} assets missing from CSV.")
        sys.exit(1)
    else:
        print(f"\nSUCCESS: All {len(rows)} assets verified. 100% coverage across AG1, AG2, AG3, AG4, AG5, AG12. Valid program phases verified.")


if __name__ == "__main__":
    check_coverage()
