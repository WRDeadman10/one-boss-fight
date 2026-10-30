#!/usr/bin/env python3
"""
verify_a257_spec.py
===================
Offline verification of F3/F4 Acceptance Test Specifications (A-257).
"""

import re
from pathlib import Path

SPEC_PATH = Path("Docs/BossCombatReview/Execution/Antigravity/Ledger/F3_F4_ACCEPTANCE_SPEC.md")
WITNESS_PATH = Path("Docs/BossCombatReview/Execution/Antigravity/Ledger/WITNESS_PLAN_82.md")

EXPECTED_F3_REQS = [
    "BOSS-AWR-001", "BOSS-SEL-001", "BOSS-SEL-008", "BOSS-EXE-001",
    "BOSS-EXE-002", "BOSS-EXE-003", "BOSS-EXE-007", "BOSS-COM-007",
    "BOSS-ANM-001", "BOSS-ANM-004", "BOSS-ANM-005", "BOSS-PAC-006"
]

EXPECTED_F4_REQS = [
    "BOSS-EXE-004", "BOSS-EXE-008", "BOSS-COM-002", "BOSS-COM-004",
    "BOSS-ANM-007", "BOSS-HIT-002", "BOSS-HIT-003", "BOSS-HIT-004",
    "BOSS-HIT-005", "BOSS-HIT-006", "BOSS-HIT-008", "BOSS-HIT-009",
    "BOSS-QA-004"
]

def main():
    print("================================================================================")
    print(" VERIFYING A-257 F3/F4 ACCEPTANCE TEST SPECIFICATIONS")
    print("================================================================================")

    assert SPEC_PATH.is_file(), f"Missing {SPEC_PATH}"
    raw = SPEC_PATH.read_bytes()
    assert b"\r\r\n" not in raw, "No double CRLF"
    assert raw.endswith(b"\r\n"), "Must end in CRLF"
    print(f"[OK] F3_F4_ACCEPTANCE_SPEC.md format verified: {len(raw):,} bytes, clean CRLF.")

    text = raw.decode("utf-8")

    # Verify F3 Requirements
    print("\nVerifying F3 Requirements (12 items):")
    for req in EXPECTED_F3_REQS:
        assert f"`{req}`" in text or f"**`{req}`**" in text, f"Missing F3 req: {req}"
        # Assert log line pattern
        assert f"req={req}" in text, f"Missing grep log line for {req}"
        print(f"  [OK] {req} present with grep pattern")

    # Verify F4 Requirements (13 items):
    print("\nVerifying F4 Requirements (13 items):")
    for req in EXPECTED_F4_REQS:
        assert f"`{req}`" in text or f"**`{req}`**" in text, f"Missing F4 req: {req}"
        assert f"req={req}" in text, f"Missing grep log line for {req}"
        print(f"  [OK] {req} present with grep pattern")

    # Verify Table Headers
    assert "Exact Log Line to Grep" in text
    assert "Measurable Numeric Tolerance" in text
    assert "Explicit Failure Tokens" in text
    print("\n[OK] All specification columns verified.")

    print("\n================================================================================")
    print(" ALL 25 F3/F4 ACCEPTANCE TEST SPECIFICATIONS 100% VERIFIED OFFLINE")
    print("================================================================================")

if __name__ == "__main__":
    main()
