"""
Offline verification script for FIRST_FIVE_CARDS_DESIGN.md (A-244).
Verifies that all animation assets on disk, attack family lines, and Morgott
requirement IDs exist and match expected lines.
"""

import os
import sys

def verify_file_line(path, line_num, expected_token):
    if not os.path.isfile(path):
        print(f"FAILED: File not found: {path}")
        return False
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    if line_num > len(lines):
        print(f"FAILED: Line {line_num} out of range in {path} (total {len(lines)})")
        return False
    actual_line = lines[line_num - 1]
    if expected_token not in actual_line:
        print(f"FAILED: Expected '{expected_token}' in {path}:{line_num}, found: {actual_line.strip()[:80]}")
        return False
    print(f"VERIFIED: {path}:{line_num} -> {actual_line.strip()[:70]}")
    return True

def verify_asset(path):
    if not os.path.isfile(path):
        print(f"FAILED: Asset not found: {path}")
        return False
    size = os.path.getsize(path)
    print(f"VERIFIED ASSET: {path} ({size:,} bytes)")
    return True

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
    ref_doc = os.path.join(repo_root, "Documentation/Boss/Morgott_82_Point_Combat_Reference/Morgott_82_Point_Combat_Reference.md")

    citations = [
        (ref_doc, 40, "Curved sword slash / delayed overhead"),
        (ref_doc, 41, "Holy dagger double slash"),
        (ref_doc, 44, "Holy spear charge"),
        (ref_doc, 45, "Holy hammer overhead slam"),
        (ref_doc, 47, "Helicopter: holy sword spin finisher"),
    ]

    assets = [
        os.path.join(repo_root, "Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Slow.uasset"),
        os.path.join(repo_root, "Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing2_Medium.uasset"),
        os.path.join(repo_root, "Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_FAST_v2.uasset"),
        os.path.join(repo_root, "Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing3_Slow.uasset"),
        os.path.join(repo_root, "Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Speedburst.uasset"),
    ]

    req_ids = [
        "BOSS-AWR-003", "BOSS-ANM-002", "BOSS-PAC-001", "BOSS-HIT-001",
        "BOSS-COM-001", "BOSS-COM-003", "BOSS-COM-006", "BOSS-PAC-002",
        "BOSS-AWR-006", "BOSS-SEL-002", "BOSS-PAC-006", "BOSS-DEF-005",
        "BOSS-PAC-003", "BOSS-COM-007", "BOSS-DEF-004", "BOSS-HIT-007",
        "BOSS-MOV-001", "BOSS-MOV-003", "BOSS-ANM-004", "BOSS-PHS-005"
    ]

    all_ok = True
    print("--- Verifying Attack Family Citations ---")
    for path, line_num, token in citations:
        if not verify_file_line(path, line_num, token):
            all_ok = False

    print("\n--- Verifying Animation Assets on Disk ---")
    for asset in assets:
        if not verify_asset(asset):
            all_ok = False

    print("\n--- Verifying 82-Point Requirement IDs in Reference ---")
    with open(ref_doc, "r", encoding="utf-8", errors="replace") as f:
        ref_text = f.read()
    for req in req_ids:
        if req not in ref_text:
            print(f"FAILED: Requirement ID '{req}' not found in {ref_doc}")
            all_ok = False
        else:
            print(f"VERIFIED REQ ID: {req}")

    # Verify doc formatting
    design_doc = os.path.join(repo_root, "Docs/BossCombatReview/Execution/Antigravity/MoveCards/FIRST_FIVE_CARDS_DESIGN.md")
    raw_bytes = open(design_doc, "rb").read()
    if b"\r\r\n" in raw_bytes:
        print("FAILED: Double carriage returns found in FIRST_FIVE_CARDS_DESIGN.md")
        all_ok = False
    if b"\n\n" in raw_bytes:
        print("FAILED: Consecutive newlines found in FIRST_FIVE_CARDS_DESIGN.md")
        all_ok = False

    if not all_ok:
        print("\nVERIFICATION FAILED")
        sys.exit(1)

    print("\nALL CITATIONS, ASSETS, REQUIREMENT IDS & FILE INTEGRITY 100% VERIFIED.")

if __name__ == "__main__":
    main()
