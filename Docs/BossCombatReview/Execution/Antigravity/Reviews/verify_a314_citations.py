#!/usr/bin/env python3
"""
verify_a314_citations.py
========================
Offline verification script for Order A-314:
1. Verifies F6C_PHASE_IMPLEMENTATION_PLAN.md pure CRLF and required section tokens.
2. Re-opens and verifies all exact C++ file:line citations across Source/.
"""

import sys
import os
from pathlib import Path

REQUIRED_DOC_TOKENS = [
    "F6c Phase Authority Implementation Plan",
    "Legacy Transition Authority",
    "RPGBossRules::ResolveTransition",
    "RPGBossRules::FFlags",
    "RPGBossRules::ETransitionResult",
    "Neutral-Only Gate Integration",
    "Card Data & MoveModel Phase Partitioning",
    "MoveModel.Phase"
]

EXACT_CITATIONS = [
    ("Source/OneBossFight/Player/RPGBossRules.h", 12, "namespace RPGBossRules"),
    ("Source/OneBossFight/Player/RPGBossRules.h", 14, "struct FFlags"),
    ("Source/OneBossFight/Player/RPGBossRules.h", 28, "enum class ETransitionResult"),
    ("Source/OneBossFight/Player/RPGBossRules.h", 72, "ResolveTransition"),
    ("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp", 79, "void ARPGFrameworkBossCharacter::Tick"),
    ("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp", 85, "bArrived&&!bStartedMove"),
    ("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp", 89, "S.PhaseId=Dependencies->FirstCard()->Spec().PhaseId;"),
    ("Source/OneBossFight/Player/RPGBossMoveCard.h", 48, "FName PhaseId;"),
    ("Source/OneBossFight/Player/RPGBossMoveModel.cpp", 30, 'if (S.PhaseId!=Card->Spec().PhaseId) return Refuse(Error,TEXT("MoveModel.Phase"));')
]


def main():
    print("================================================================================")
    print(" VERIFYING ORDER A-314 DELIVERABLES & EXACT C++ CITATIONS")
    print("================================================================================")

    doc_path = Path("Docs/BossCombatReview/Execution/Antigravity/Reviews/F6C_PHASE_IMPLEMENTATION_PLAN.md")
    if not doc_path.is_file():
        print(f"[FAIL] Missing plan doc: {doc_path}")
        sys.exit(1)

    raw_doc = doc_path.read_bytes()
    if b"\r\r\n" in raw_doc or (b"\n" in raw_doc and raw_doc.count(b"\n") != raw_doc.count(b"\r\n")):
        print("[FAIL] Line endings in plan doc are not pure CRLF")
        sys.exit(1)

    doc_text = raw_doc.decode("utf-8")
    for tok in REQUIRED_DOC_TOKENS:
        if tok not in doc_text:
            print(f"[FAIL] Missing token in plan doc: '{tok}'")
            sys.exit(1)
        print(f"[OK] Token verified: '{tok}'")

    print(f"[OK] F6C_PHASE_IMPLEMENTATION_PLAN.md: pure CRLF, {len(raw_doc)} bytes")

    # Verify exact citations
    for rel_path, line_no, token in EXACT_CITATIONS:
        p = Path(rel_path)
        if not p.is_file():
            print(f"[FAIL] Citation file does not exist: {p}")
            sys.exit(1)
        lines = p.read_text(encoding="utf-8").splitlines()
        if line_no > len(lines):
            print(f"[FAIL] Line {line_no} exceeds line count ({len(lines)}) in {rel_path}")
            sys.exit(1)
        line_content = lines[line_no - 1]
        if token not in line_content:
            print(f"[FAIL] Citation mismatch at {rel_path}:{line_no}\n  Expected token: '{token}'\n  Actual line:    '{line_content}'")
            sys.exit(1)
        print(f"[OK] Citation verified {rel_path}:{line_no} -> '{token}'")

    print("\n================================================================================")
    print(" ALL ORDER A-314 PLAN TOKENS & CITATIONS 100% VERIFIED OFFLINE")
    print("================================================================================")
    sys.exit(0)


if __name__ == "__main__":
    main()
