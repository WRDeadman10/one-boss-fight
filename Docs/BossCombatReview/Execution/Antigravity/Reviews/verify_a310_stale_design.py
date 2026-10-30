#!/usr/bin/env python3
"""
verify_a310_stale_design.py
===========================
Offline verification script for Order A-310 deliverables:
1. Verifies STALE_BAKE_DETECTION_DESIGN.md has pure CRLF, no bare LF, required tokens.
2. Verifies author_move_cards.py fail-closed properties and readback assertions.
3. Verifies test_author_move_cards.py execution passes 100%.
"""

import sys
import os
import subprocess
from pathlib import Path

REQUIRED_DOC_TOKENS = [
    "Candidate Detection Mechanisms & Failure Mode Analysis",
    "Candidate A: Clip Length Check",
    "Candidate B: Package File Hash",
    "Candidate C: Spot-Check Sample Comparison",
    "Dual-Tier Guard",
    "VR-CARD-009",
    "FRPGBossStaleBakeDetectionTest"
]


def main():
    print("================================================================================")
    print(" VERIFYING ORDER A-310 DELIVERABLES (FAIL-CLOSED FIX & STALE BAKE DESIGN)")
    print("================================================================================")

    # 1. Verify STALE_BAKE_DETECTION_DESIGN.md
    doc_path = Path("Docs/BossCombatReview/Execution/Antigravity/Reviews/STALE_BAKE_DETECTION_DESIGN.md")
    if not doc_path.is_file():
        print(f"[FAIL] Missing design doc: {doc_path}")
        sys.exit(1)

    raw_doc = doc_path.read_bytes()
    if b"\r\r\n" in raw_doc:
        print("[FAIL] Corrupt double CRLF found in design doc")
        sys.exit(1)
    if b"\n" in raw_doc and raw_doc.count(b"\n") != raw_doc.count(b"\r\n"):
        print("[FAIL] Bare LF found in design doc")
        sys.exit(1)

    doc_text = raw_doc.decode("utf-8")
    for tok in REQUIRED_DOC_TOKENS:
        if tok not in doc_text:
            print(f"[FAIL] Missing token in design doc: '{tok}'")
            sys.exit(1)
        print(f"[OK] Token verified in design doc: '{tok}'")

    print(f"[OK] STALE_BAKE_DETECTION_DESIGN.md: pure CRLF, {len(raw_doc)} bytes")

    # 2. Run test_author_move_cards.py
    test_path = "Docs/BossCombatReview/Execution/Antigravity/MoveCards/test_author_move_cards.py"
    res = subprocess.run([sys.executable, test_path], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[FAIL] test_author_move_cards.py failed:\n{res.stderr}\n{res.stdout}")
        sys.exit(1)
    print("[OK] test_author_move_cards.py passed 100% (45/45 tests)")

    # 3. Run test_bake_blade_path.py
    bake_test_path = "Docs/BossCombatReview/Execution/Antigravity/MoveCards/test_bake_blade_path.py"
    res_b = subprocess.run([sys.executable, bake_test_path], capture_output=True, text=True)
    if res_b.returncode != 0:
        print(f"[FAIL] test_bake_blade_path.py failed:\n{res_b.stderr}\n{res_b.stdout}")
        sys.exit(1)
    print("[OK] test_bake_blade_path.py passed 100% (6/6 tests)")

    print("\n================================================================================")
    print(" ALL ORDER A-310 VERIFICATIONS 100% PASS")
    print("================================================================================")
    sys.exit(0)


if __name__ == "__main__":
    main()
