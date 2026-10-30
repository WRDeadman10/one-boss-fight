#!/usr/bin/env python3
"""
verify_a252_review.py
Offline verification of F3A_LIFECYCLE_REVIEW.md (A-252).
"""

from pathlib import Path

STAGING_ROOT = Path("Docs/BossCombatReview/Execution/Codex/Framework/F3/Staging")

CITED_LINES = [
    (STAGING_ROOT / "Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp", 112, "void URPGFrameworkMoveExecutor::Abort"),
    (STAGING_ROOT / "Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp", 94, "Executor->Abort(TEXT(\"EndPlay\"))"),
    (STAGING_ROOT / "Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp", 121, "void URPGFrameworkMoveExecutor::EndPlay"),
    (STAGING_ROOT / "Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp", 71, "OwnedMontage=nullptr;bFinished=true;"),
    (STAGING_ROOT / "Source/OneBossFight/Boss/RPGFrameworkBossController.cpp", 22, "const FPathFollowingRequestResult R=MoveTo(Request,&Path);"),
    (STAGING_ROOT / "Source/OneBossFight/Boss/RPGFrameworkBossController.cpp", 33, "if (OwnedRequest==FAIRequestID::InvalidRequest||RequestID!=OwnedRequest) return;"),
    (STAGING_ROOT / "Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp", 65, "Now-StartWorldSeconds>Profile->WalkTimeoutSeconds"),
    (STAGING_ROOT / "Source/OneBossFight/Player/RPGBossMoveModel.cpp", 84, "Token.Generation==Epoch"),
]

def main():
    print("================================================================================")
    print(" VERIFYING A-252 F3A LIFECYCLE REVIEW")
    print("================================================================================")

    doc_path = Path("Docs/BossCombatReview/Execution/Antigravity/Reviews/F3A_LIFECYCLE_REVIEW.md")
    assert doc_path.is_file(), f"Missing doc file: {doc_path}"

    raw = doc_path.read_bytes()
    assert b"\r\r\n" not in raw, "No double CRLF"
    assert b"\n" in raw, "Must have newlines"
    print(f"[OK] F3A_LIFECYCLE_REVIEW.md raw bytes: {len(raw):,} bytes, clean CRLF")

    for path, line_no, token in CITED_LINES:
        assert path.is_file(), f"Staged source file missing: {path}"
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        assert line_no <= len(lines), f"Line {line_no} out of range in {path}"
        line_text = lines[line_no - 1]
        assert token in line_text, f"Token '{token}' not found on line {line_no} of {path.name} (found: '{line_text.strip()}')"
        print(f"[OK] Citation {path.name}:{line_no} verified: '{token}'")

    print("\n================================================================================")
    print(" ALL 8 STAGED SOURCE CITATIONS 100% VERIFIED OFFLINE")
    print("================================================================================")

if __name__ == "__main__":
    main()
