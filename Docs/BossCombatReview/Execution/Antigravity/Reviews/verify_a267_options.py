#!/usr/bin/env python3
"""
verify_a267_options.py
Offline verification of F4_DAMAGE_SINK_OPTIONS.md citations and byte cleanliness.
"""
from pathlib import Path

CITED_LINES = [
    (Path("Source/OneBossFight/Player/RPGDamageResolver.h"), 25, "HP only: boss moves take no posture (Freeze 504); guard and hit reaction are not built"),
    (Path("Source/OneBossFight/Player/RPGDamageResolver.h"), 94, "inline ERPGDamageOutcome Decide(bool bTargetAlive, bool bAttackerAlive, bool bGenerationCurrent, bool bDuplicate, bool bTargetInvulnerable)"),
    (Path("Source/OneBossFight/Player/RPGDamageResolver.h"), 141, "FRPGDamageResult Resolve(AActor* Target, const FRPGDamagePayload& Payload);"),
    (Path("Source/OneBossFight/Player/RPGDamageResolver.cpp"), 132, "FRPGDamageResult URPGDamageResolver::Resolve(AActor* Target, const FRPGDamagePayload& Payload)"),
    (Path("Source/OneBossFight/Player/RPGDamageResolver.cpp"), 151, "RPGBossDamage::IsInvulnerable(Target)"),
    (Path("Source/OneBossFight/Player/RPGDamageResolver.cpp"), 159, "RPGBossDamage::HurtPlayer(Target, Payload.HPDamage, HealthBefore, HealthAfter)"),
    (Path("Source/OneBossFight/Player/RPGBossDamage.h"), 34, "inline bool IsInvulnerable(AActor* Player)"),
    (Path("Source/OneBossFight/Player/RPGBossDamage.h"), 46, "inline bool HurtPlayer(const AActor* Player, double Damage, double& Before, double& After)"),
    (Path("Source/OneBossFight/Pack/RPGBlueprintCall.h"), 222, "inline bool WriteAttribute(const AActor* Actor, const TCHAR* AttributeTag, double Value)"),
    (Path("Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp"), 225, "URPGDamageResolver::FindOrAdd(Pawn);"),
    (Path("Source/OneBossFight/Player/RPGBossLowSweep.cpp"), 91, "URPGDamageResolver* Resolver = URPGDamageResolver::FindOrAdd(GetOwner());"),
    (Path("Source/OneBossFight/Player/RPGBossLowSweep.cpp"), 126, "const FRPGDamageResult Result = Resolver->Resolve(const_cast<ACharacter*>(Player), Payload);"),
]

def main():
    print("================================================================================")
    print(" VERIFYING A-267 F4 DAMAGE SINK OPTIONS")
    print("================================================================================")

    doc_path = Path("Docs/BossCombatReview/Execution/Antigravity/Reviews/F4_DAMAGE_SINK_OPTIONS.md")
    assert doc_path.is_file(), f"Missing doc file: {doc_path}"

    raw = doc_path.read_bytes()
    assert b"\r\r\n" not in raw, "No double CRLF"
    assert b"\n" in raw, "Must have newlines"
    assert raw.endswith(b"\r\n"), "Must end with CRLF"
    for idx, b in enumerate(raw):
        if b == 0x0A:
            assert idx > 0 and raw[idx - 1] == 0x0D, f"Invalid LF at byte {idx}"
    print(f"[OK] F4_DAMAGE_SINK_OPTIONS.md raw bytes: {len(raw):,} bytes, pure CRLF")

    for path, line_no, token in CITED_LINES:
        assert path.is_file(), f"Source file missing: {path}"
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        assert line_no <= len(lines), f"Line {line_no} out of range in {path} (total {len(lines)})"
        line_text = lines[line_no - 1]
        assert token in line_text, f"Token '{token}' not found on line {line_no} of {path.name} (found: '{line_text.strip()}')"
        print(f"[OK] Citation {path.name}:{line_no} verified: '{token}'")

    print("\n================================================================================")
    print(" ALL 12 PROJECT SOURCE CITATIONS 100% VERIFIED OFFLINE")
    print("================================================================================")

if __name__ == "__main__":
    main()
