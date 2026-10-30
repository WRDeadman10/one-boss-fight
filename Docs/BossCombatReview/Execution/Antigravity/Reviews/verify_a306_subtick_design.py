#!/usr/bin/env python3
"""
verify_a306_subtick_design.py
Offline verification of KI147_HIT_WINDOW_SUBTICK_DESIGN.md.
"""
from pathlib import Path

DOC_PATH = Path("Docs/BossCombatReview/Execution/Antigravity/Reviews/KI147_HIT_WINDOW_SUBTICK_DESIGN.md")

REQUIRED_TOKENS = [
    "## 1. Executive Summary & Problem Recap",
    "## 2. Option 1: Runtime Sub-Tick Animation Pose Extraction (UE 5.5)",
    "## 3. Option 2: Baked Blade Path in MoveCard Data (Recommended)",
    "## 4. Definitive Recommendation: Option 2 (Baked Blade Path)",
    "## 5. Sweep-Coverage Unit Test Specification",
    "FRPGBakedBladeSample",
    "BaseCS",
    "TipCS",
    "ExtractSubTickBladePose",
    "FAnimationPoseData",
    "FCSPose",
    "GetComponentSpaceTransform",
    "FRPGBossSweepHitchCoverageTest",
    "SweepHitchCoverage",
]

CITED_LINES = [
    (Path("C:/Program Files/Epic Games/UE_5.5/Engine/Source/Runtime/Engine/Classes/Animation/AnimSequence.h"), 480, "void GetBonePose(struct FAnimationPoseData& OutAnimationPoseData"),
    (Path("C:/Program Files/Epic Games/UE_5.5/Engine/Source/Runtime/Engine/Classes/Animation/AnimSequence.h"), 569, "void GetBoneTransform(FTransform& OutAtom, FSkeletonPoseBoneIndex BoneIndex, double Time"),
    (Path("C:/Program Files/Epic Games/UE_5.5/Engine/Source/Runtime/Engine/Classes/Animation/AnimationPoseData.h"), 15, "struct FAnimationPoseData"),
    (Path("C:/Program Files/Epic Games/UE_5.5/Engine/Source/Runtime/Engine/Public/BonePose.h"), 407, "struct FCSPose"),
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
    print(" VERIFYING KI-147 SUB-TICK HIT WINDOW DESIGN (ORDER A-306)")
    print("================================================================================")

    check_crlf(DOC_PATH)

    doc_text = DOC_PATH.read_text(encoding="utf-8")
    for tok in REQUIRED_TOKENS:
        assert tok in doc_text, f"Missing required token in design doc: {tok}"
        print(f"[OK] Token verified: '{tok[:45]}'")

    for path, line_no, token in CITED_LINES:
        assert path.is_file(), f"Source file missing: {path}"
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        assert line_no <= len(lines), f"Line {line_no} out of range in {path} (total {len(lines)})"
        line_text = lines[line_no - 1]
        assert token in line_text, f"Token '{token}' not found on line {line_no} of {path.name} (found: '{line_text.strip()}')"
        print(f"[OK] Engine Citation {path.name}:{line_no} verified: '{token[:40]}'")

    print("\n================================================================================")
    print(" ALL SUB-TICK DESIGN CITATIONS & SECTIONS 100% VERIFIED OFFLINE")
    print("================================================================================")


if __name__ == "__main__":
    main()
