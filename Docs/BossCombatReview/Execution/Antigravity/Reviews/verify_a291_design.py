#!/usr/bin/env python3
"""
verify_a291_design.py
Offline verification of F6_BOSS_LIFE_PHASE_DESIGN.md citations, requirement mappings, and CRLF cleanliness.
"""
from pathlib import Path

CITED_LINES = [
    (Path("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp"), 19, "GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);"),
    (Path("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp"), 21, "SetCanBeDamaged(false);"),
    (Path("Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp"), 99, "Class->GetName() == TEXT(\"BP_ExampleGreatSwordBoss_C\")"),
    (Path("Source/OneBossFight/Player/RPGHitIntake.cpp"), 399, "AActor* Target = HitResult.GetActor();"),
    (Path("Source/OneBossFight/Player/RPGHitIntake.cpp"), 400, "if (!Target || !URPGPlayerMovesSubsystem::IsPackBoss(Target))"),
    (Path("Source/OneBossFight/Player/RPGDamageResolver.h"), 133, "void SetLifeProvider(TFunction<bool()> InIsAlive, TFunction<int32()> InGeneration);"),
    (Path("Source/OneBossFight/Player/RPGDamageResolver.cpp"), 147, "const bool bAttackerAlive = ProviderIsAlive ? ProviderIsAlive() : RPGBossDamage::IsAlive(GetOwner());"),
    (Path("Source/OneBossFight/Player/RPGBossPhases.h"), 31, "float PhaseTwoHealthFraction = 0.6f;"),
    (Path("Source/OneBossFight/Player/RPGBossRules.h"), 72, "inline ETransitionResult ResolveTransition(const FFlags& F, double Health, double Max, float Fraction)"),
    (Path("Source/OneBossFight/Player/RPGBossEncounter.h"), 61, "int32 GetGeneration() const { return Generation; }"),
    (Path("Source/OneBossFight/Player/RPGBossEncounter.cpp"), 313, "++Generation; // every callback made for the old fight is stale from here on"),
    (Path("Source/OneBossFight/Pack/RPGPackTrace.cpp"), 40, "TargetProperties"),
    (Path("Config/DefaultEngine.ini"), 101, "CharacterMesh"),
]

REQUIRED_SECTIONS = [
    "## 1. Executive Summary & Problem Statement",
    "## 2. Pack Player Hit Detection Prerequisites on Framework Boss",
    "## 3. Boss HP Architecture, Resolver Seams, Generation Reset, and Death",
    "## 4. Minimal Phase Authority Mapped to BOSS-PHS-001..006",
    "## 5. Concrete Recommendation & Honest Unknowns",
    "BOSS-PHS-001: Phase Rule Set",
    "BOSS-PHS-002: Safe Transition Policy",
    "BOSS-PHS-003: Phase Monotonicity",
    "BOSS-PHS-004: Fair Heal Punish",
    "BOSS-PHS-005: Anti-Cheese with Counterplay",
    "BOSS-PHS-006: Phase State Deactivation",
    "[UNVERIFIED - Physics Asset Bone Coverage]",
    "[UNVERIFIED - Double Hit Sweep Priority]",
    "[UNVERIFIED - Player HUD Health Bar Linkage]",
]

def main():
    print("================================================================================")
    print(" VERIFYING A-291 F6 BOSS LIFE, TARGET INTERFACE, AND PHASE DESIGN")
    print("================================================================================")

    doc_path = Path("Docs/BossCombatReview/Execution/Antigravity/Reviews/F6_BOSS_LIFE_PHASE_DESIGN.md")
    assert doc_path.is_file(), f"Missing doc file: {doc_path}"

    raw = doc_path.read_bytes()
    assert b"\r\r\n" not in raw, "No double CRLF"
    assert b"\n" in raw, "Must have newlines"
    assert raw.endswith(b"\r\n"), "Must end with CRLF"
    for idx, b in enumerate(raw):
        if b == 0x0A:
            assert idx > 0 and raw[idx - 1] == 0x0D, f"Invalid LF at byte {idx}"
    print(f"[OK] F6_BOSS_LIFE_PHASE_DESIGN.md raw bytes: {len(raw):,} bytes, pure CRLF")

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
    print(" ALL 13 PROJECT SOURCE & CONFIG CITATIONS AND SECTIONS 100% VERIFIED OFFLINE")
    print("================================================================================")

if __name__ == "__main__":
    main()
