#!/usr/bin/env python3
"""
verify_a293_parity_map.py
Offline verification of F6A_LEGACY_PARITY_MAP.md citations, required sections, and CRLF cleanliness.
"""
from pathlib import Path

CITED_LINES = [
    (Path("Source/OneBossFight/Tests/RPGPlayerMovesAttachWitnessTests.cpp"), 441, "FRPGAttachWitnessBossTest"),
    (Path("Source/OneBossFight/Tests/RPGPlayerMovesAttachWitnessTests.cpp"), 448, "FRPGAttachWitnessPlayerTest"),
    (Path("Source/OneBossFight/Tests/RPGAutomationTests.cpp"), 1060, "FRPGPackWiringTest"),
    (Path("Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp"), 95, "bool URPGPlayerMovesSubsystem::IsPackBoss(const AActor* Actor)"),
    (Path("Source/OneBossFight/Player/RPGHitIntake.cpp"), 258, "void URPGHitIntake::AdjustBossHealth(AActor* Boss, double Adjust, const TCHAR* Why)"),
    (Path("Source/OneBossFight/Player/RPGHitIntake.cpp"), 399, "AActor* Target = HitResult.GetActor();"),
    (Path("Source/OneBossFight/UI/RPGBossHud.cpp"), 414, "bHaveHealth = RPGPack::ReadAttribute(Boss, TEXT(\"Attribute.Health\")"),
    (Path("Source/OneBossFight/Audio/RPGBossMusic.cpp"), 156, "bHaveHealth = RPGPack::ReadAttribute(Boss, TEXT(\"Attribute.Health\")"),
    (Path("Source/OneBossFight/Arena/RPGFogGate.cpp"), 98, "bHealth = ReadAttribute(*It, TEXT(\"Attribute.Health\")"),
    (Path("Source/OneBossFight/Player/RPGBossDamage.h"), 39, "inline bool IsAlive(const AActor* Actor)"),
    (Path("Source/OneBossFight/Player/RPGDamageScale.h"), 12, "struct FRPGDamageScaler"),
]

REQUIRED_SECTIONS = [
    "## 1. Executive Summary & Purpose",
    "## 2. Legacy Tests and Drivers Touching IsPackBoss and URPGHitIntake",
    "## 3. Census of Boss Health Consumers (Display & Rules)",
    "## 4. Anatomy of URPGHitIntake::AdjustBossHealth & Minimal Branch",
    "FRPGAttachWitnessBossTest",
    "FRPGAttachWitnessPlayerTest",
    "FRPGPackWiringTest",
    "pie_hit_intake.py",
    "RPGBossHud",
    "RPGBossMusic",
    "RPGFogGate",
    "AdjustBossHealth",
]

def main():
    print("================================================================================")
    print(" VERIFYING A-292 / A-293 F6A LEGACY PARITY MAP")
    print("================================================================================")

    doc_path = Path("Docs/BossCombatReview/Execution/Antigravity/Reviews/F6A_LEGACY_PARITY_MAP.md")
    assert doc_path.is_file(), f"Missing doc file: {doc_path}"

    raw = doc_path.read_bytes()
    assert b"\r\r\n" not in raw, "No double CRLF"
    assert b"\n" in raw, "Must have newlines"
    assert raw.endswith(b"\r\n"), "Must end with CRLF"
    for idx, b in enumerate(raw):
        if b == 0x0A:
            assert idx > 0 and raw[idx - 1] == 0x0D, f"Invalid LF at byte {idx}"
    print(f"[OK] F6A_LEGACY_PARITY_MAP.md raw bytes: {len(raw):,} bytes, pure CRLF")

    doc_text = raw.decode("utf-8")
    for req in REQUIRED_SECTIONS:
        assert req in doc_text, f"Missing required section/token: {req}"
        print(f"[OK] Found required section: {req[:40]}")

    for path, line_no, token in CITED_LINES:
        assert path.is_file(), f"Source file missing: {path}"
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        assert line_no <= len(lines), f"Line {line_no} out of range in {path} (total {len(lines)})"
        line_text = lines[line_no - 1]
        assert token in line_text, f"Token '{token}' not found on line {line_no} of {path.name} (found: '{line_text.strip()}')"
        print(f"[OK] Citation {path.name}:{line_no} verified: '{token[:50]}...'")

    print("\n================================================================================")
    print(" ALL 11 PROJECT SOURCE & TEST CITATIONS AND SECTIONS 100% VERIFIED OFFLINE")
    print("================================================================================")

if __name__ == "__main__":
    main()
