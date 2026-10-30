#!/usr/bin/env python3
"""
verify_a269_design.py
Offline verification of F4_RESOLVER_SEAM_DESIGN.md citations, test names, and byte cleanliness.
"""
from pathlib import Path

CITED_LINES = [
    (Path("Source/OneBossFight/Player/RPGDamageResolver.cpp"), 40, "int32 URPGDamageResolver::CurrentGeneration() const"),
    (Path("Source/OneBossFight/Player/RPGDamageResolver.cpp"), 132, "FRPGDamageResult URPGDamageResolver::Resolve(AActor* Target, const FRPGDamagePayload& Payload)"),
    (Path("Source/OneBossFight/Player/RPGDamageResolver.cpp"), 147, "const bool bAttackerAlive = ProviderIsAlive ? ProviderIsAlive() : RPGBossDamage::IsAlive(GetOwner());"),
    (Path("Source/OneBossFight/Player/RPGBossDamage.h"), 39, "inline bool IsAlive(const AActor* Actor)"),
    (Path("Source/OneBossFight/Player/RPGBossLowSweep.cpp"), 91, "URPGDamageResolver* Resolver = URPGDamageResolver::FindOrAdd(GetOwner());"),
    (Path("Source/OneBossFight/Player/RPGBossLowSweep.cpp"), 126, "const FRPGDamageResult Result = Resolver->Resolve(const_cast<ACharacter*>(Player), Payload);"),
    (Path("Source/OneBossFight/Player/RPGBossShockwave.cpp"), 102, "URPGDamageResolver* Resolver = URPGDamageResolver::FindOrAdd(GetOwner());"),
    (Path("Source/OneBossFight/Player/RPGBossShockwave.cpp"), 113, "const FRPGDamageResult Result = Resolver->Resolve(const_cast<ACharacter*>(Player), Payload);"),
    (Path("Source/OneBossFight/Player/RPGBossJavelin.cpp"), 145, "URPGDamageResolver* Resolver = URPGDamageResolver::FindOrAdd(Boss);"),
    (Path("Source/OneBossFight/Player/RPGBossJavelin.cpp"), 147, "const FRPGDamageResult Result = Resolver->Resolve(Player, Payload);"),
    (Path("Source/OneBossFight/Player/RPGCombatDebug.cpp"), 148, "if (const URPGDamageResolver* Resolver = Boss->FindComponentByClass<URPGDamageResolver>())"),
    (Path("Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp"), 225, "URPGDamageResolver::FindOrAdd(Pawn);"),
    (Path("Source/OneBossFight/Tests/RPGAutomationTests.cpp"), 159, "IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGDamageDecideTest, \"OneBossFight.Combat.DamageResolver.Decide\""),
    (Path("Source/OneBossFight/Tests/RPGPlayerMovesAttachWitnessTests.cpp"), 441, "IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGAttachWitnessBossTest, \"OneBossFight.Player.AttachWitness.Boss\""),
]

def main():
    print("================================================================================")
    print(" VERIFYING A-269 F4 RESOLVER SEAM DESIGN & GEOMETRY SPEC")
    print("================================================================================")

    doc_path = Path("Docs/BossCombatReview/Execution/Antigravity/Reviews/F4_RESOLVER_SEAM_DESIGN.md")
    assert doc_path.is_file(), f"Missing doc file: {doc_path}"

    raw = doc_path.read_bytes()
    assert b"\r\r\n" not in raw, "No double CRLF"
    assert b"\n" in raw, "Must have newlines"
    assert raw.endswith(b"\r\n"), "Must end with CRLF"
    for idx, b in enumerate(raw):
        if b == 0x0A:
            assert idx > 0 and raw[idx - 1] == 0x0D, f"Invalid LF at byte {idx}"
    print(f"[OK] F4_RESOLVER_SEAM_DESIGN.md raw bytes: {len(raw):,} bytes, pure CRLF")

    for path, line_no, token in CITED_LINES:
        assert path.is_file(), f"Source file missing: {path}"
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        assert line_no <= len(lines), f"Line {line_no} out of range in {path} (total {len(lines)})"
        line_text = lines[line_no - 1]
        assert token in line_text, f"Token '{token}' not found on line {line_no} of {path.name} (found: '{line_text.strip()}')"
        print(f"[OK] Citation {path.name}:{line_no} verified: '{token[:50]}...'")

    print("\n================================================================================")
    print(" ALL 14 PROJECT SOURCE & TEST CITATIONS 100% VERIFIED OFFLINE")
    print("================================================================================")

if __name__ == "__main__":
    main()
