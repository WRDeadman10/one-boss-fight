#!/usr/bin/env python3
"""
verify_a301_f6a_review.py
Offline verification of F6A_CODE_SECOND_REVIEW.md.
"""
from pathlib import Path

REVIEW_PATH = Path("Docs/BossCombatReview/Execution/Antigravity/Reviews/F6A_CODE_SECOND_REVIEW.md")

REQUIRED_TOKENS = [
    "## 1. Executive Summary",
    "## 2. Detailed Findings & Triggering Sequences",
    "Finding 1: Double-Death Reentrancy",
    "Finding 2: Fatal Access Violation on Null",
    "Finding 3: Target Null Check Ordering",
    "Finding 4: Shipping Build Stripping",
    "Finding 5: GameThread Concurrency Guard",
    "Finding 6: Interface Cast Overhead",
    "## 3. Summary of Recommendations for F6b Integration",
    "Source/OneBossFight/Player/RPGNativeBossHealth.h",
    "Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp",
    "Source/OneBossFight/Pack/RPGBlueprintCall.h",
    "Source/OneBossFight/Player/RPGHitIntake.cpp",
]

CITED_LINES = [
    (Path("Source/OneBossFight/Player/RPGNativeBossHealth.h"), 16, "class ONEBOSSFIGHT_API IRPGNativeBossHealth"),
    (Path("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.h"), 27, "virtual bool ReadNativeHealth"),
    (Path("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp"), 134, "if (!bHittable||bDead||bFailed||!bInitialized||!FMath::IsFinite(Multiplier)||Multiplier<0.) return 0.;"),
    (Path("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp"), 138, "if (Health<=0.) Die();"),
    (Path("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp"), 160, "void ARPGFrameworkBossCharacter::Die()"),
    (Path("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp"), 163, "bDead=true;"),
    (Path("Source/OneBossFight/Pack/RPGBlueprintCall.h"), 213, "if (FCString::Stricmp(AttributeTag, TEXT(\"Attribute.Health\")) == 0)"),
    (Path("Source/OneBossFight/Pack/RPGBlueprintCall.h"), 215, "if (const IRPGNativeBossHealth* Native = Cast<const IRPGNativeBossHealth>(Actor))"),
    (Path("Source/OneBossFight/Player/RPGHitIntake.cpp"), 398, "void URPGHitIntake::InjectBossHitForTest(AActor* Boss)"),
    (Path("Source/OneBossFight/Player/RPGHitIntake.cpp"), 400, "#if UE_BUILD_SHIPPING"),
    (Path("Source/OneBossFight/Player/RPGHitIntake.cpp"), 417, "if (IRPGNativeBossHealth* Native = Cast<IRPGNativeBossHealth>(Target))"),
]


def check_crlf(path: Path):
    assert path.is_file(), f"Missing file: {path}"
    raw = path.read_bytes()
    assert b"\r\r\n" not in raw, f"{path}: double CRLF detected"
    assert b"\n" in raw, f"{path}: no newlines detected"
    assert raw.endswith(b"\r\n"), f"{path}: file does not end with CRLF"
    for idx, b in enumerate(raw):
        if b == 0x0A:
            assert idx > 0 and raw[idx - 1] == 0x0D, f"{path}: invalid bare LF at byte {idx}"
    print(f"[OK] {path.name}: pure CRLF, {len(raw):,} bytes")


def main():
    print("================================================================================")
    print(" VERIFYING F6A CODE SECOND-REVIEW (ORDER C-420)")
    print("================================================================================")

    check_crlf(REVIEW_PATH)

    review_text = REVIEW_PATH.read_text(encoding="utf-8")
    for tok in REQUIRED_TOKENS:
        assert tok in review_text, f"Missing required token in review doc: {tok}"
        print(f"[OK] Token verified: '{tok[:45]}'")

    for path, line_no, token in CITED_LINES:
        assert path.is_file(), f"Source file missing: {path}"
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        assert line_no <= len(lines), f"Line {line_no} out of range in {path} (total {len(lines)})"
        line_text = lines[line_no - 1]
        assert token in line_text, f"Token '{token}' not found on line {line_no} of {path.name} (found: '{line_text.strip()}')"
        print(f"[OK] Citation {path.name}:{line_no} verified: '{token[:40]}'")

    print("\n================================================================================")
    print(" ALL F6A SECOND-REVIEW CITATIONS & SECTIONS 100% VERIFIED OFFLINE")
    print("================================================================================")


if __name__ == "__main__":
    main()
