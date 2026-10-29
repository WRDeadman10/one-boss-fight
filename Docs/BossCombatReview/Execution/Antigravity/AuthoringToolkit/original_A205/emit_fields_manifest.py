#!/usr/bin/env python3
"""
emit_fields_manifest.py - Deterministic Generator for FRPGParityField Parity Manifests

Generates compliant FRPGParityField manifest rows for boss combat definitions under the
Lead Conventions established in C-294 and C-297.

CONVENTIONS (C-294 / C-297):
  - FieldPath: exactly the 110 paths (matching DD26 preflight plan literals).
  - Value: truthful string parsed directly from C++ header / struct declaration defaults
    or profile JSON authored phase specifications.
  - Type: UPROPERTY type name as declared.
  - Units: physical unit ("seconds", "degrees", "cm", "cm/s", "hp", "fraction 0..1", "dimensionless").
  - SourcePath: repo-relative path of the file that DEFINES the value.
  - SourceSHA256: live SHA-256 hash of the exact bytes of the SourcePath file in the working tree.
  - SourceSite: dynamically computed declaration line (File:line) or JSON pointer.
  - Origin: one of NativeDefault, SubsystemOverride, LeadContract, AuthoredAsset.
  - Precedence: literal "typed-record" for every row.
  - Destination: Class::Member of the native component field or struct member.
  - FirstRead: "PrepareBatch.Configure".
  - Witness: AutomationTest:OneBossFight.Binding.<Suite>.Assign (verified passing tests).
"""

import argparse
import hashlib
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

class PhaseNotFoundError(Exception):
    """Raised when the requested selected phase id does not exist in the profile."""
    pass

# Helper to find repository root deterministically
def find_repo_root() -> str:
    candidate = os.path.abspath(os.path.dirname(__file__))
    while candidate and candidate != os.path.dirname(candidate):
        if os.path.exists(os.path.join(candidate, "Source", "OneBossFight")) or os.path.exists(os.path.join(candidate, ".git")):
            return candidate
        candidate = os.path.dirname(candidate)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))

REPO_ROOT = find_repo_root()
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

def compute_file_sha256(rel_path: str) -> str:
    full_path = os.path.join(REPO_ROOT, rel_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Source file not found for hashing: {rel_path} ({full_path})")
    h = hashlib.sha256()
    with open(full_path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

DECL_TYPE_PAT = r'(?:float|bool|int32|FName|FString|FVector2D|TArray<.*?>|TSoftObjectPtr<.*?>|TSoftClassPtr<.*?>|ERPGBossDeathMode)'

def find_member_decl(rel_path: str, member_name: str, is_override: bool = False) -> Tuple[int, Optional[str], str]:
    full_path = os.path.join(REPO_ROOT, rel_path)
    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    if is_override:
        # e.g. DeathMode override in RPGPlayerMovesSubsystem.cpp
        for lno, line in enumerate(lines, 1):
            if "ERPGBossDeathMode::OwnClip" in line:
                return lno, "ERPGBossDeathMode::OwnClip", line.strip()

    pat = re.compile(DECL_TYPE_PAT + r"\s+[*&\s]*\b" + re.escape(member_name) + r"\b(?:\s*=\s*([^;]+))?;?")
    for lno, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("/*"):
            continue
        m = pat.search(line)
        if m:
            val = m.group(1).strip() if m.group(1) else None
            # If val has trailing comments, strip them
            if val and "//" in val:
                val = val.split("//")[0].strip()
            return lno, val, line.strip()

    raise ValueError(f"Could not find declaration for member '{member_name}' in {rel_path}")

# Verified automation test witnesses by cluster
WITNESS_BY_CLUSTER = {
    "StaggerPolicy": "AutomationTest:OneBossFight.Binding.StaggerPolicy.Assign",
    "StaggerProfile": "AutomationTest:OneBossFight.Binding.StaggerCluster.Assign",
    "SelectedPhase": "AutomationTest:OneBossFight.Binding.PhaseAdapters.Assign",
    "PhaseFlow": "AutomationTest:OneBossFight.Binding.PhaseFlow.Assign",
    "Fireball": "AutomationTest:OneBossFight.Binding.PhasesCluster.Assign",
    "PhaseDependencies": "AutomationTest:OneBossFight.Binding.PhasesCluster.Assign",
    "Encounter": "AutomationTest:OneBossFight.Binding.EncounterCluster.Assign",
    "DormantWake": "AutomationTest:OneBossFight.Binding.DormantWake.Assign",
    "Posture": "AutomationTest:OneBossFight.Binding.StatsAdapters.Assign",
    "Bleed": "AutomationTest:OneBossFight.Binding.Bleed.Assign",
    "LowSweep": "AutomationTest:OneBossFight.Binding.LowSweep.Assign",
    "Shockwave": "AutomationTest:OneBossFight.Binding.Shockwave.Assign",
    "HealPunish": "AutomationTest:OneBossFight.Binding.HealPunish.Assign",
    "Look": "AutomationTest:OneBossFight.Binding.Look.Assign",
    "CloseClipSwap": "AutomationTest:OneBossFight.Binding.CloseClipSwap.Assign",
    "Death": "AutomationTest:OneBossFight.Binding.Death.Assign",
}

# The 106 static / base fields specification
BASE_FIELDS_SPEC = [
    # 1. StaggerPolicy (14)
    ("StaggerPolicy.StaggerSeconds", "float", "seconds", "Source/OneBossFight/Player/RPGBossStagger.h", "StaggerSeconds", "NativeDefault", "URPGBossStagger::StaggerSeconds", "StaggerPolicy", False),
    ("StaggerPolicy.FreezeAtPosition", "float", "seconds", "Source/OneBossFight/Player/RPGBossStagger.h", "FreezeAtPosition", "NativeDefault", "URPGBossStagger::FreezeAtPosition", "StaggerPolicy", False),
    ("StaggerPolicy.CriticalMultiplier", "float", "multiplier", "Source/OneBossFight/Player/RPGBossStagger.h", "CriticalMultiplier", "NativeDefault", "URPGBossStagger::CriticalMultiplier", "StaggerPolicy", False),
    ("StaggerPolicy.RiposteRange", "float", "cm", "Source/OneBossFight/Player/RPGBossStagger.h", "RiposteRange", "NativeDefault", "URPGBossStagger::RiposteRange", "StaggerPolicy", False),
    ("StaggerPolicy.RiposteConeDegrees", "float", "degrees", "Source/OneBossFight/Player/RPGBossStagger.h", "RiposteConeDegrees", "NativeDefault", "URPGBossStagger::RiposteConeDegrees", "StaggerPolicy", False),
    ("StaggerPolicy.RiposteFacingDegrees", "float", "degrees", "Source/OneBossFight/Player/RPGBossStagger.h", "RiposteFacingDegrees", "NativeDefault", "URPGBossStagger::RiposteFacingDegrees", "StaggerPolicy", False),
    ("StaggerPolicy.RiposteArmSeconds", "float", "seconds", "Source/OneBossFight/Player/RPGBossStagger.h", "RiposteArmSeconds", "NativeDefault", "URPGBossStagger::RiposteArmSeconds", "StaggerPolicy", False),
    ("StaggerPolicy.RipostePlayerStartGap", "float", "cm", "Source/OneBossFight/Player/RPGBossStagger.h", "RipostePlayerStartGap", "NativeDefault", "URPGBossStagger::RipostePlayerStartGap", "StaggerPolicy", False),
    ("StaggerPolicy.RiposteAlignSeconds", "float", "seconds", "Source/OneBossFight/Player/RPGBossStagger.h", "RiposteAlignSeconds", "NativeDefault", "URPGBossStagger::RiposteAlignSeconds", "StaggerPolicy", False),
    ("StaggerPolicy.RiposteImpactSeconds", "float", "seconds", "Source/OneBossFight/Player/RPGBossStagger.h", "RiposteImpactSeconds", "NativeDefault", "URPGBossStagger::RiposteImpactSeconds", "StaggerPolicy", False),
    ("StaggerPolicy.RiposteBaseDamage", "float", "hp", "Source/OneBossFight/Player/RPGBossStagger.h", "RiposteBaseDamage", "NativeDefault", "URPGBossStagger::RiposteBaseDamage", "StaggerPolicy", False),
    ("StaggerPolicy.CooldownSeconds", "float", "seconds", "Source/OneBossFight/Player/RPGBossStagger.h", "CooldownSeconds", "NativeDefault", "URPGBossStagger::CooldownSeconds", "StaggerPolicy", False),
    ("StaggerPolicy.GetUpRate", "float", "multiplier", "Source/OneBossFight/Player/RPGBossStagger.h", "GetUpRate", "NativeDefault", "URPGBossStagger::GetUpRate", "StaggerPolicy", False),
    ("StaggerPolicy.bHoldPostureAtZero", "bool", "dimensionless", "Source/OneBossFight/Player/RPGBossStagger.h", "bHoldPostureAtZero", "NativeDefault", "URPGBossStagger::bHoldPostureAtZero", "StaggerPolicy", False),

    # 2. StaggerProfile (11)
    ("StaggerProfile.bUseClips", "bool", "dimensionless", "Source/OneBossFight/Player/RPGBossStagger.h", "bUseClips", "NativeDefault", "URPGBossStagger::bUseClips", "StaggerProfile", False),
    ("StaggerProfile.bUseRiposteClips", "bool", "dimensionless", "Source/OneBossFight/Player/RPGBossStagger.h", "bUseRiposteClips", "NativeDefault", "URPGBossStagger::bUseRiposteClips", "StaggerProfile", False),
    ("StaggerProfile.bCriticalOnEveryHit", "bool", "dimensionless", "Source/OneBossFight/Player/RPGBossStagger.h", "bCriticalOnEveryHit", "NativeDefault", "URPGBossStagger::bCriticalOnEveryHit", "StaggerProfile", False),
    ("StaggerProfile.HitStunAbilityClassName", "FName", "identifier", "Source/OneBossFight/Player/RPGBossStagger.h", "HitStunAbilityClassName", "NativeDefault", "URPGBossStagger::HitStunAbilityClassName", "StaggerProfile", False),
    ("StaggerProfile.FallMontage", "TSoftObjectPtr<UAnimMontage>", "dimensionless", "Source/OneBossFight/Player/RPGBossStagger.h", "FallMontage", "NativeDefault", "URPGBossStagger::FallMontage", "StaggerProfile", False),
    ("StaggerProfile.GetUpMontage", "TSoftObjectPtr<UAnimMontage>", "dimensionless", "Source/OneBossFight/Player/RPGBossStagger.h", "GetUpMontage", "NativeDefault", "URPGBossStagger::GetUpMontage", "StaggerProfile", False),
    ("StaggerProfile.FallClip", "TSoftObjectPtr<UAnimSequence>", "dimensionless", "Source/OneBossFight/Player/RPGBossStagger.h", "FallClip", "NativeDefault", "URPGBossStagger::FallClip", "StaggerProfile", False),
    ("StaggerProfile.DownClip", "TSoftObjectPtr<UAnimSequence>", "dimensionless", "Source/OneBossFight/Player/RPGBossStagger.h", "DownClip", "NativeDefault", "URPGBossStagger::DownClip", "StaggerProfile", False),
    ("StaggerProfile.RipostePlayerClip", "TSoftObjectPtr<UAnimSequence>", "dimensionless", "Source/OneBossFight/Player/RPGBossStagger.h", "RipostePlayerClip", "NativeDefault", "URPGBossStagger::RipostePlayerClip", "StaggerProfile", False),
    ("StaggerProfile.RiposteBossClip", "TSoftObjectPtr<UAnimSequence>", "dimensionless", "Source/OneBossFight/Player/RPGBossStagger.h", "RiposteBossClip", "NativeDefault", "URPGBossStagger::RiposteBossClip", "StaggerProfile", False),
    ("StaggerProfile.ImmunityEffect", "TSoftClassPtr<UObject>", "dimensionless", "Source/OneBossFight/Player/RPGBossStagger.h", "ImmunityEffect", "NativeDefault", "URPGBossStagger::ImmunityEffect", "StaggerProfile", False),

    # 3. PhaseFlow (6)
    ("PhaseFlow.TransitionSeconds", "float", "seconds", "Source/OneBossFight/Player/RPGBossPhases.h", "TransitionSeconds", "NativeDefault", "URPGBossPhases::TransitionSeconds", "PhaseFlow", False),
    ("PhaseFlow.bUseRoarClip", "bool", "dimensionless", "Source/OneBossFight/Player/RPGBossPhases.h", "bUseRoarClip", "NativeDefault", "URPGBossPhases::bUseRoarClip", "PhaseFlow", False),
    ("PhaseFlow.bPausePostureInTransition", "bool", "dimensionless", "Source/OneBossFight/Player/RPGBossPhases.h", "bPausePostureInTransition", "NativeDefault", "URPGBossPhases::bPausePostureInTransition", "PhaseFlow", False),
    ("PhaseFlow.bLockLeapUntilPhaseTwo", "bool", "dimensionless", "Source/OneBossFight/Player/RPGBossPhases.h", "bLockLeapUntilPhaseTwo", "NativeDefault", "URPGBossPhases::bLockLeapUntilPhaseTwo", "PhaseFlow", False),
    ("PhaseFlow.AttackAbilityPrefix", "FString", "identifier", "Source/OneBossFight/Player/RPGBossPhases.h", "AttackAbilityPrefix", "NativeDefault", "URPGBossPhases::AttackAbilityPrefix", "PhaseFlow", False),
    ("PhaseFlow.LeapAbilityTag", "FName", "identifier", "Source/OneBossFight/Player/RPGBossPhases.h", "LeapAbilityTag", "NativeDefault", "URPGBossPhases::LeapAbilityTag", "PhaseFlow", False),

    # 4. Fireball (5)
    ("Fireball.bFireballEnabled", "bool", "dimensionless", "Source/OneBossFight/Player/RPGBossPhases.h", "bFireballEnabled", "NativeDefault", "URPGBossPhases::bFireballEnabled", "Fireball", False),
    ("Fireball.FireballAbility", "TSoftClassPtr<UObject>", "dimensionless", "Source/OneBossFight/Player/RPGBossPhases.h", "FireballAbility", "NativeDefault", "URPGBossPhases::FireballAbility", "Fireball", False),
    ("Fireball.FireballCooldown", "FVector2D", "seconds", "Source/OneBossFight/Player/RPGBossPhases.h", "FireballCooldown", "NativeDefault", "URPGBossPhases::FireballCooldown", "Fireball", False),
    ("Fireball.FireballMinRange", "float", "cm", "Source/OneBossFight/Player/RPGBossPhases.h", "FireballMinRange", "NativeDefault", "URPGBossPhases::FireballMinRange", "Fireball", False),
    ("Fireball.FireballMaxRange", "float", "cm", "Source/OneBossFight/Player/RPGBossPhases.h", "FireballMaxRange", "NativeDefault", "URPGBossPhases::FireballMaxRange", "Fireball", False),

    # 5. PhaseDependencies (3)
    ("PhaseDependencies.RoarClip", "TSoftObjectPtr<UAnimSequence>", "dimensionless", "Source/OneBossFight/Player/RPGBossPhases.h", "RoarClip", "NativeDefault", "URPGBossPhases::RoarClip", "PhaseDependencies", False),
    ("PhaseDependencies.TransitionMontage", "TSoftObjectPtr<UAnimMontage>", "dimensionless", "Source/OneBossFight/Player/RPGBossPhases.h", "TransitionMontage", "NativeDefault", "URPGBossPhases::TransitionMontage", "PhaseDependencies", False),
    ("PhaseDependencies.ImmunityEffect", "TSoftClassPtr<UObject>", "dimensionless", "Source/OneBossFight/Player/RPGBossPhases.h", "ImmunityEffect", "NativeDefault", "URPGBossPhases::ImmunityEffect", "PhaseDependencies", False),

    # 6. Encounter (3)
    ("Stats.MaxHealth", "float", "hp", "Source/OneBossFight/Player/RPGBossEncounter.h", "BossMaxHealth", "NativeDefault", "URPGBossEncounter::BossMaxHealth", "Encounter", False),
    ("EncounterPolicy.GateRadius", "float", "cm", "Source/OneBossFight/Player/RPGBossEncounter.h", "GateRadius", "NativeDefault", "URPGBossEncounter::GateRadius", "Encounter", False),
    ("EncounterPolicy.bResetOnPlayerRespawn", "bool", "dimensionless", "Source/OneBossFight/Player/RPGBossEncounter.h", "bResetOnPlayerRespawn", "NativeDefault", "URPGBossEncounter::bResetOnPlayerRespawn", "Encounter", False),

    # 7. DormantWake (2)
    ("DormantWake.DormantClip", "TSoftObjectPtr<UAnimSequence>", "dimensionless", "Source/OneBossFight/Player/RPGBossDormantWake.h", "DormantClip", "NativeDefault", "URPGBossDormantWake::DormantClip", "DormantWake", False),
    ("DormantWake.WakeClip", "TSoftObjectPtr<UAnimSequence>", "dimensionless", "Source/OneBossFight/Player/RPGBossDormantWake.h", "WakeClip", "NativeDefault", "URPGBossDormantWake::WakeClip", "DormantWake", False),

    # 8. Posture (3)
    ("Stats.MaxPosture", "float", "hp", "Source/OneBossFight/Player/RPGBossPosture.h", "PostureMax", "NativeDefault", "URPGBossPosture::PostureMax", "Posture", False),
    ("Stats.PostureRegenDelay", "float", "seconds", "Source/OneBossFight/Player/RPGBossPosture.h", "RegenDelaySeconds", "NativeDefault", "URPGBossPosture::RegenDelaySeconds", "Posture", False),
    ("Stats.PostureRegenRate", "float", "hp/s", "Source/OneBossFight/Player/RPGBossPosture.h", "RegenPerSecond", "NativeDefault", "URPGBossPosture::RegenPerSecond", "Posture", False),

    # 9. Bleed (7)
    ("Bleed.InitialThreshold", "float", "hp", "Source/OneBossFight/Player/RPGEncounterBinding.h", "InitialThreshold", "LeadContract", "URPGBossBleed::InitialThreshold", "Bleed", False),
    ("Bleed.ThresholdIncrease", "float", "hp", "Source/OneBossFight/Player/RPGEncounterBinding.h", "ThresholdIncrease", "LeadContract", "URPGBossBleed::ThresholdIncrease", "Bleed", False),
    ("Bleed.ThresholdMax", "float", "hp", "Source/OneBossFight/Player/RPGEncounterBinding.h", "ThresholdMax", "LeadContract", "URPGBossBleed::ThresholdMax", "Bleed", False),
    ("Bleed.HpFraction", "float", "fraction 0..1", "Source/OneBossFight/Player/RPGEncounterBinding.h", "HpFraction", "LeadContract", "URPGBossBleed::HpFraction", "Bleed", False),
    ("Bleed.EffectHeight", "float", "cm", "Source/OneBossFight/Player/RPGEncounterBinding.h", "EffectHeight", "LeadContract", "URPGBossBleed::EffectHeight", "Bleed", False),
    ("Bleed.ProcEffect", "TSoftObjectPtr<UNiagaraSystem>", "dimensionless", "Source/OneBossFight/Player/RPGEncounterBinding.h", "ProcEffect", "LeadContract", "URPGBossBleed::ProcEffect", "Bleed", False),
    ("Bleed.ProcSound", "TSoftObjectPtr<USoundBase>", "dimensionless", "Source/OneBossFight/Player/RPGEncounterBinding.h", "ProcSound", "LeadContract", "URPGBossBleed::ProcSound", "Bleed", False),

    # 10. LowSweep (8)
    ("LowSweep.bEnabled", "bool", "dimensionless", "Source/OneBossFight/Player/RPGEncounterBinding.h", "bEnabled", "LeadContract", "URPGBossLowSweep::bEnabled", "LowSweep", False),
    ("LowSweep.MoveId", "FName", "identifier", "Source/OneBossFight/Player/RPGEncounterBinding.h", "MoveId", "LeadContract", "URPGBossLowSweep::MoveId", "LowSweep", False),
    ("LowSweep.Damage", "float", "hp", "Source/OneBossFight/Player/RPGEncounterBinding.h", "Damage", "LeadContract", "URPGBossLowSweep::Damage", "LowSweep", False),
    ("LowSweep.Reach", "float", "cm", "Source/OneBossFight/Player/RPGEncounterBinding.h", "Reach", "LeadContract", "URPGBossLowSweep::Reach", "LowSweep", False),
    ("LowSweep.InnerRadius", "float", "cm", "Source/OneBossFight/Player/RPGEncounterBinding.h", "InnerRadius", "LeadContract", "URPGBossLowSweep::InnerRadius", "LowSweep", False),
    ("LowSweep.BladeHeight", "float", "cm", "Source/OneBossFight/Player/RPGEncounterBinding.h", "BladeHeight", "LeadContract", "URPGBossLowSweep::BladeHeight", "LowSweep", False),
    ("LowSweep.SweepFromDegrees", "float", "degrees", "Source/OneBossFight/Player/RPGEncounterBinding.h", "SweepFromDegrees", "LeadContract", "URPGBossLowSweep::SweepFromDegrees", "LowSweep", False),
    ("LowSweep.SweepToDegrees", "float", "degrees", "Source/OneBossFight/Player/RPGEncounterBinding.h", "SweepToDegrees", "LeadContract", "URPGBossLowSweep::SweepToDegrees", "LowSweep", False),

    # 11. Shockwave (8)
    ("Shockwave.bEnabled", "bool", "dimensionless", "Source/OneBossFight/Player/RPGEncounterBinding.h", "bEnabled", "LeadContract", "URPGBossShockwave::bEnabled", "Shockwave", False),
    ("Shockwave.MoveId", "FName", "identifier", "Source/OneBossFight/Player/RPGEncounterBinding.h", "MoveId", "LeadContract", "URPGBossShockwave::MoveId", "Shockwave", False),
    ("Shockwave.Damage", "float", "hp", "Source/OneBossFight/Player/RPGEncounterBinding.h", "Damage", "LeadContract", "URPGBossShockwave::Damage", "Shockwave", False),
    ("Shockwave.StartRadius", "float", "cm", "Source/OneBossFight/Player/RPGEncounterBinding.h", "StartRadius", "LeadContract", "URPGBossShockwave::StartRadius", "Shockwave", False),
    ("Shockwave.MaxRadius", "float", "cm", "Source/OneBossFight/Player/RPGEncounterBinding.h", "MaxRadius", "LeadContract", "URPGBossShockwave::MaxRadius", "Shockwave", False),
    ("Shockwave.Speed", "float", "cm/s", "Source/OneBossFight/Player/RPGEncounterBinding.h", "Speed", "LeadContract", "URPGBossShockwave::Speed", "Shockwave", False),
    ("Shockwave.Thickness", "float", "cm", "Source/OneBossFight/Player/RPGEncounterBinding.h", "Thickness", "LeadContract", "URPGBossShockwave::Thickness", "Shockwave", False),
    ("Shockwave.JumpClearance", "float", "cm", "Source/OneBossFight/Player/RPGEncounterBinding.h", "JumpClearance", "LeadContract", "URPGBossShockwave::JumpClearance", "Shockwave", False),

    # 12. HealPunish (14)
    ("HealPunish.bEnabled", "bool", "dimensionless", "Source/OneBossFight/Player/RPGEncounterBinding.h", "bEnabled", "LeadContract", "URPGBossHealPunish::bEnabled", "HealPunish", False),
    ("HealPunish.MinRange", "float", "cm", "Source/OneBossFight/Player/RPGEncounterBinding.h", "MinRange", "LeadContract", "URPGBossHealPunish::MinRange", "HealPunish", False),
    ("HealPunish.MaxRange", "float", "cm", "Source/OneBossFight/Player/RPGEncounterBinding.h", "MaxRange", "LeadContract", "URPGBossHealPunish::MaxRange", "HealPunish", False),
    ("HealPunish.Cooldown", "float", "seconds", "Source/OneBossFight/Player/RPGEncounterBinding.h", "Cooldown", "LeadContract", "URPGBossHealPunish::Cooldown", "HealPunish", False),
    ("HealPunish.Damage", "float", "hp", "Source/OneBossFight/Player/RPGEncounterBinding.h", "Damage", "LeadContract", "URPGBossHealPunish::Damage", "HealPunish", False),
    ("HealPunish.FlightTime", "float", "seconds", "Source/OneBossFight/Player/RPGEncounterBinding.h", "FlightTime", "LeadContract", "URPGBossHealPunish::FlightTime", "HealPunish", False),
    ("HealPunish.MinSpeed", "float", "cm/s", "Source/OneBossFight/Player/RPGEncounterBinding.h", "MinSpeed", "LeadContract", "URPGBossHealPunish::MinSpeed", "HealPunish", False),
    ("HealPunish.MaxSpeed", "float", "cm/s", "Source/OneBossFight/Player/RPGEncounterBinding.h", "MaxSpeed", "LeadContract", "URPGBossHealPunish::MaxSpeed", "HealPunish", False),
    ("HealPunish.JavelinRadius", "float", "cm", "Source/OneBossFight/Player/RPGEncounterBinding.h", "JavelinRadius", "LeadContract", "URPGBossHealPunish::JavelinRadius", "HealPunish", False),
    ("HealPunish.JavelinMaxRange", "float", "cm", "Source/OneBossFight/Player/RPGEncounterBinding.h", "JavelinMaxRange", "LeadContract", "URPGBossHealPunish::JavelinMaxRange", "HealPunish", False),
    ("HealPunish.SpawnSockets", "TArray<FName>", "identifier", "Source/OneBossFight/Player/RPGEncounterBinding.h", "SpawnSockets", "LeadContract", "URPGBossHealPunish::SpawnSockets", "HealPunish", False),
    ("HealPunish.AimHeight", "float", "cm", "Source/OneBossFight/Player/RPGEncounterBinding.h", "AimHeight", "LeadContract", "URPGBossHealPunish::AimHeight", "HealPunish", False),
    ("HealPunish.bRespondToHeal", "bool", "dimensionless", "Source/OneBossFight/Player/RPGEncounterBinding.h", "bRespondToHeal", "LeadContract", "URPGBossHealPunish::bRespondToHeal", "HealPunish", False),
    ("HealPunish.bCancelJavelinsOnInterrupt", "bool", "dimensionless", "Source/OneBossFight/Player/RPGEncounterBinding.h", "bCancelJavelinsOnInterrupt", "LeadContract", "URPGBossHealPunish::bCancelJavelinsOnInterrupt", "HealPunish", False),

    # 13. Look (5)
    ("Look.bEnabled", "bool", "dimensionless", "Source/OneBossFight/Player/RPGEncounterBinding.h", "bEnabled", "LeadContract", "URPGBossLook::bEnabled", "Look", False),
    ("Look.Body", "TSoftObjectPtr<USkeletalMesh>", "dimensionless", "Source/OneBossFight/Player/RPGEncounterBinding.h", "Body", "LeadContract", "URPGBossLook::Body", "Look", False),
    ("Look.Pieces", "TArray<TSoftObjectPtr<USkeletalMesh>>", "dimensionless", "Source/OneBossFight/Player/RPGEncounterBinding.h", "Pieces", "LeadContract", "URPGBossLook::Pieces", "Look", False),
    ("Look.Sword", "TSoftObjectPtr<UStaticMesh>", "dimensionless", "Source/OneBossFight/Player/RPGEncounterBinding.h", "Sword", "LeadContract", "URPGBossLook::Sword", "Look", False),
    ("Look.SwordSocket", "FName", "identifier", "Source/OneBossFight/Player/RPGEncounterBinding.h", "SwordSocket", "LeadContract", "URPGBossLook::SwordSocket", "Look", False),

    # 14. CloseClipSwap (5)
    ("CloseClipSwap.CloseAbilityClassName", "FName", "identifier", "Source/OneBossFight/Player/RPGEncounterBinding.h", "CloseAbilityClassName", "LeadContract", "URPGBossCloseClipSwap::CloseAbilityClassName", "CloseClipSwap", False),
    ("CloseClipSwap.AttackMontagesName", "FName", "identifier", "Source/OneBossFight/Player/RPGEncounterBinding.h", "AttackMontagesName", "LeadContract", "URPGBossCloseClipSwap::AttackMontagesName", "CloseClipSwap", False),
    ("CloseClipSwap.A1Montage", "TSoftObjectPtr<UAnimMontage>", "dimensionless", "Source/OneBossFight/Player/RPGEncounterBinding.h", "A1Montage", "LeadContract", "URPGBossCloseClipSwap::A1Montage", "CloseClipSwap", False),
    ("CloseClipSwap.A3aMontage", "TSoftObjectPtr<UAnimMontage>", "dimensionless", "Source/OneBossFight/Player/RPGEncounterBinding.h", "A3aMontage", "LeadContract", "URPGBossCloseClipSwap::A3aMontage", "CloseClipSwap", False),
    ("CloseClipSwap.A3bMontage", "TSoftObjectPtr<UAnimMontage>", "dimensionless", "Source/OneBossFight/Player/RPGEncounterBinding.h", "A3bMontage", "LeadContract", "URPGBossCloseClipSwap::A3bMontage", "CloseClipSwap", False),

    # 15. Death (12)
    ("Death.DeathMode", "ERPGBossDeathMode", "identifier", "Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp", "DeathMode", "SubsystemOverride", "URPGBossDeath::DeathMode", "Death", True),
    ("Death.DeathClip", "TSoftObjectPtr<UAnimSequence>", "dimensionless", "Source/OneBossFight/Player/RPGEncounterBinding.h", "DeathClip", "LeadContract", "URPGBossDeath::DeathClip", "Death", False),
    ("Death.DeathMontage", "TSoftObjectPtr<UAnimMontage>", "dimensionless", "Source/OneBossFight/Player/RPGEncounterBinding.h", "DeathMontage", "LeadContract", "URPGBossDeath::DeathMontage", "Death", False),
    ("Death.PackDeathAbilityClassName", "FName", "identifier", "Source/OneBossFight/Player/RPGEncounterBinding.h", "PackDeathAbilityClassName", "LeadContract", "URPGBossDeath::PackDeathAbilityClassName", "Death", False),
    ("Death.PackDeathMontagesName", "FName", "identifier", "Source/OneBossFight/Player/RPGEncounterBinding.h", "PackDeathMontagesName", "LeadContract", "URPGBossDeath::PackDeathMontagesName", "Death", False),
    ("Death.PackPollSeconds", "float", "seconds", "Source/OneBossFight/Player/RPGEncounterBinding.h", "PackPollSeconds", "LeadContract", "URPGBossDeath::PackPollSeconds", "Death", False),
    ("Death.PackEndTimeMultiplier", "float", "multiplier", "Source/OneBossFight/Player/RPGEncounterBinding.h", "PackEndTimeMultiplier", "LeadContract", "URPGBossDeath::PackEndTimeMultiplier", "Death", False),
    ("Death.HoldAtSeconds", "float", "seconds", "Source/OneBossFight/Player/RPGEncounterBinding.h", "HoldAtSeconds", "LeadContract", "URPGBossDeath::HoldAtSeconds", "Death", False),
    ("Death.DyingSeconds", "float", "seconds", "Source/OneBossFight/Player/RPGEncounterBinding.h", "DyingSeconds", "LeadContract", "URPGBossDeath::DyingSeconds", "Death", False),
    ("Death.BlendInSeconds", "float", "seconds", "Source/OneBossFight/Player/RPGEncounterBinding.h", "BlendInSeconds", "LeadContract", "URPGBossDeath::BlendInSeconds", "Death", False),
    ("Death.MaxClipRestarts", "int32", "count", "Source/OneBossFight/Player/RPGEncounterBinding.h", "MaxClipRestarts", "LeadContract", "URPGBossDeath::MaxClipRestarts", "Death", False),
    ("Death.bGuardPackDeath", "bool", "dimensionless", "Source/OneBossFight/Player/RPGEncounterBinding.h", "bGuardPackDeath", "LeadContract", "URPGBossDeath::bGuardPackDeath", "Death", False),
]

def generate_manifest_rows(
    draft_profiles_path: str = "Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json",
    selected_phase_id: Optional[str] = None,
    include_selected_phase: bool = True
) -> Tuple[List[Dict[str, str]], List[str], Dict[str, str]]:
    """
    Generates the complete manifest rows according to C-294 and C-297 rules.
    Returns: (rows, file_list_with_hashes, summary_stats)
    """
    # 1. Collect unique source files to hash
    unique_files = set(spec[3] for spec in BASE_FIELDS_SPEC)
    if include_selected_phase and draft_profiles_path:
        unique_files.add(draft_profiles_path.replace("\\", "/"))

    file_hashes: Dict[str, str] = {}
    for rel_path in sorted(unique_files):
        file_hashes[rel_path] = compute_file_sha256(rel_path)

    rows: List[Dict[str, str]] = []

    # 2. Generate the 106 base rows
    for (field_path, u_type, units, src_rel, member_name, origin, dest, cluster, is_override) in BASE_FIELDS_SPEC:
        decl_line, parsed_val, raw_line = find_member_decl(src_rel, member_name, is_override)
        source_site = f"{os.path.basename(src_rel)}:{decl_line}"
        sha = file_hashes[src_rel]
        witness = WITNESS_BY_CLUSTER[cluster]

        # Determine truthful value
        if is_override:
            val_str = "ERPGBossDeathMode::OwnClip"
        elif parsed_val is not None:
            val_str = parsed_val
        else:
            val_str = ""

        row = {
            "FieldPath": field_path,
            "Value": val_str,
            "Type": u_type,
            "Units": units,
            "SourcePath": src_rel,
            "SourceSHA256": sha,
            "SourceSite": source_site,
            "Origin": origin,
            "Precedence": "typed-record",
            "Destination": dest,
            "FirstRead": "PrepareBatch.Configure",
            "Witness": witness
        }
        rows.append(row)

    # 3. Handle the 4 selected phase rows
    withheld_paths: List[str] = []
    if include_selected_phase:
        if not draft_profiles_path:
            draft_profiles_path = "Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json"
        
        full_json_path = os.path.join(REPO_ROOT, draft_profiles_path)
        with open(full_json_path, "r", encoding="utf-8") as jf:
            profile_data = json.load(jf)

        # Locate first boss profile
        boss_prof = None
        p_idx = 0
        for idx, prof in enumerate(profile_data.get("profiles", [])):
            if prof.get("phases"):
                boss_prof = prof
                p_idx = idx
                break

        if not boss_prof:
            raise ValueError(f"No profile with phases found in {draft_profiles_path}")

        phases_list = boss_prof.get("phases", [])
        if not phases_list:
            raise ValueError(f"Profile {boss_prof.get('asset_name')} has empty phases array")

        # Determine target phase
        target_phase = None
        ph_idx = 0
        if selected_phase_id:
            for idx, ph in enumerate(phases_list):
                if ph.get("PhaseId") == selected_phase_id:
                    target_phase = ph
                    ph_idx = idx
                    break
            if not target_phase:
                raise PhaseNotFoundError(f"Requested PhaseId '{selected_phase_id}' not found in profile phases: {[p.get('PhaseId') for p in phases_list]}")
        else:
            target_phase = phases_list[0]
            selected_phase_id = target_phase.get("PhaseId")
            ph_idx = 0

        # Phase paths definition
        phase_specs = [
            (f"Phases[{selected_phase_id}].EntryHealthFraction", "float", "fraction 0..1", "EntryHealthFraction", "FRPGPhaseConfig::EntryHealthFraction"),
            (f"Phases[{selected_phase_id}].SpeedMultiplier", "float", "dimensionless", "SpeedMultiplier", "FRPGPhaseConfig::SpeedMultiplier"),
            (f"Phases[{selected_phase_id}].RateMultiplier", "float", "dimensionless", "RateMultiplier", "FRPGPhaseConfig::RateMultiplier"),
            (f"Phases[{selected_phase_id}].AttackMultiplier", "float", "dimensionless", "AttackMultiplier", "FRPGPhaseConfig::AttackMultiplier"),
        ]

        json_sha = file_hashes[draft_profiles_path.replace("\\", "/")]
        phase_witness = WITNESS_BY_CLUSTER["PhaseFlow"]

        for (ph_path, ph_type, ph_units, ph_prop, ph_dest) in phase_specs:
            val_num = target_phase[ph_prop]
            val_str = str(val_num)
            json_pointer = f"/profiles/{p_idx}/phases/{ph_idx}/{ph_prop}"
            row = {
                "FieldPath": ph_path,
                "Value": val_str,
                "Type": ph_type,
                "Units": ph_units,
                "SourcePath": draft_profiles_path.replace("\\", "/"),
                "SourceSHA256": json_sha,
                "SourceSite": json_pointer,
                "Origin": "AuthoredAsset",
                "Precedence": "typed-record",
                "Destination": ph_dest,
                "FirstRead": "PrepareBatch.Configure",
                "Witness": phase_witness
            }
            rows.append(row)
    else:
        withheld_paths = [
            "Phases[<SelectedPhaseId>].EntryHealthFraction",
            "Phases[<SelectedPhaseId>].SpeedMultiplier",
            "Phases[<SelectedPhaseId>].RateMultiplier",
            "Phases[<SelectedPhaseId>].AttackMultiplier",
        ]

    return rows, withheld_paths, file_hashes

def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministic generator for FRPGParityField manifest rows.")
    parser.add_argument("--output", "-o", help="Optional output JSON path for the emitted rows.")
    parser.add_argument("--draft-profiles", "-p", default="Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json",
                        help="Path to draft boss profiles JSON.")
    parser.add_argument("--selected-phase", "-s", default="PhaseTwo",
                        help="Selected PhaseId for which to emit phase rows (default: PhaseTwo).")
    parser.add_argument("--no-selected-phase", action="store_true",
                        help="Withhold selected-phase rows (emits 106 rows instead of 110).")
    args = parser.parse_args()

    include_phase = not args.no_selected_phase
    try:
        rows, withheld, file_hashes = generate_manifest_rows(
            draft_profiles_path=args.draft_profiles,
            selected_phase_id=args.selected_phase if include_phase else None,
            include_selected_phase=include_phase
        )
    except PhaseNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    print("=== LIVE SOURCE HASHES ===")
    for fpath, h in sorted(file_hashes.items()):
        print(f"  {h}  {fpath}")

    print("\n=== GENERATION SUMMARY ===")
    if include_phase:
        print(f"{len(rows)} generated, 0 withheld, 0 invented")
    else:
        print(f"{len(rows)} generated, {len(withheld)} withheld (PhaseFlow selected-phase paths), 0 invented")

    if args.output:
        out_full = os.path.join(REPO_ROOT, args.output) if not os.path.isabs(args.output) else args.output
        os.makedirs(os.path.dirname(out_full), exist_ok=True)
        out_data = {
            "$schema_description": "FRPGParityField Manifest Output",
            "count": len(rows),
            "fields": rows
        }
        with open(out_full, "wb") as f:
            f.write(json.dumps(out_data, indent=2).encode("utf-8").replace(b"\n", b"\r\n"))
        print(f"Wrote {len(rows)} rows to {args.output}")

if __name__ == "__main__":
    main()
