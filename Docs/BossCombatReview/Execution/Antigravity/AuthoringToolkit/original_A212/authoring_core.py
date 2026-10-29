#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
authoring_core.py
=================
Pure Python shared validation core and invariant enforcement library for OneBossFight
authoring tools (AG-CONTENT04 / Deliverables A, B, C, D).

Design Invariants:
    1. Zero Unreal Dependencies: This module uses standard library only and contains no
       import of the 'unreal' module or Unreal Engine C++ APIs at module level.
    2. Exact Native Normalization: Matches Unreal Engine 5.5 String.cpp.inl TrimQuotesInline
       and RPGCombatRegistry::Normalize (FString::TrimQuotes trims at most one leading and
       one trailing double quote; single quotes are preserved). ASCII parity scope.
    3. Strict FName Semantics: Case-insensitive ASCII comparison without whitespace stripping.
    4. Canonical Paths: Rejects path traversal, double slashes, backslashes, colons, and
       non-canonical segments.
    5. Immutable Snapshot Comparison: Deep recursive value-by-value comparison of source
       inventories, property dictionaries, package sets, and dirty flags.
    6. Native Capability & Domain Alignment: Strictly enforces backend native capability
       constraints from RPGBossPhaseAdapters.cpp and RPGBossStatsAdapters.cpp (health override
       floor > 1.0, attack scale floor >= 1.0, threshold domain 0.0 < fraction <= 1.0).
    7. Fail-Closed Error Reporting: All domain, schema, and path errors halt processing with
       explicit diagnostics. Partial operations report exact created packages without rollback claims.
    8. Offline Float64 Qualification: All offline tests and validators run in CPython float64,
       which does NOT certify native float32 conversion or input-mode parity. The authoring toolkit
       uses struct.pack('f') / struct.unpack('f') to simulate native float32 truncation and verify
       that valid float32 values survive round-trip, but offline execution does not execute native
       UE5.5 C++ serialization, memory layouts, or input-mode controller parity.
"""

import copy
import math
import re
import struct
from typing import Dict, List, Tuple, Any, Optional, Set

# ---------------------------------------------------------------------------
# IEEE 754 32-Bit Float Bounds & Helpers
# ---------------------------------------------------------------------------
FLOAT32_MAX = 3.4028234663852886e+38
FLOAT32_MIN = -3.4028234663852886e+38


def to_float32(val: Any) -> float:
    """
    Converts a numerical scalar into an IEEE 754 32-bit single-precision float
    (simulating Unreal Engine C++ float property storage).
    Raises ValueError if a finite float64 value overflows float32 range.
    """
    f = float(val)
    if math.isnan(f):
        return float('nan')
    if math.isinf(f):
        return f
    if f > FLOAT32_MAX or f < FLOAT32_MIN:
        raise ValueError(f"Value {val} overflows 32-bit single-precision float range [{FLOAT32_MIN}, {FLOAT32_MAX}]")
    try:
        return struct.unpack('f', struct.pack('f', f))[0]
    except OverflowError:
        raise ValueError(f"Value {val} overflows 32-bit single-precision float")

# ---------------------------------------------------------------------------
# Canonical Project Roots & Constants
# ---------------------------------------------------------------------------
APPROVED_SOURCE_CATALOG = "/Game/OneBossFight/Data/Catalog/DA_CombatCatalog"
APPROVED_OUTPUT_ROOT = "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/"
APPROVED_BOSS_DRAFTS_ROOT = "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/"

TARGET_BUILD_ASSET_NAME = "DA_Build_Custom_Vanguard"
TARGET_CATALOG_ASSET_NAME = "DA_CombatCatalog_VanguardCloned"

# Native C++ Class Paths in /Script/OneBossFight
CLASS_CATALOG_PATH = "/Script/OneBossFight.RPGCombatCatalog"
CLASS_BUILD_DEF_PATH = "/Script/OneBossFight.RPGBuildDefinition"
CLASS_WEAPON_DEF_PATH = "/Script/OneBossFight.RPGWeaponDefinition"
CLASS_BOSS_DEF_PATH = "/Script/OneBossFight.RPGBossDefinition"
CLASS_ENCOUNTER_BINDING_PATH = "/Script/OneBossFight.RPGEncounterBinding"

# Native Backend Arithmetic & Capability Floors
# Source: RPGBossStatsAdapters.h / cpp (NativeHealthOverrideFloor)
NATIVE_HEALTH_OVERRIDE_FLOOR = 1.0
# Source: RPGBossPhaseAdapters.h / cpp (NativeDamageScaleFloor)
NATIVE_DAMAGE_SCALE_FLOOR = 1.0
# Source: RPGBossStaggerPolicyAdapters.h (NativeCriticalMultiplierFloor)
NATIVE_CRITICAL_MULTIPLIER_FLOOR = 1.0

# Pinned 3-Build Legacy Compatibility Contract (Source: RPGCombatCatalog.cpp:158-172 & RPGBuildRules.h:50-57)
PINNED_LEGACY_CONTRACT = {
    0: {
        "BuildId": "Starter",
        "ConsoleName": "Starter",
        "DisplayName": "Starter",
        "UiOrder": 0,
        "WeaponId": "Starter",
        "ExpectedStyle": "SwordCombatStyle"
    },
    1: {
        "BuildId": "Strength",
        "ConsoleName": "Strength",
        "DisplayName": "Strength",
        "UiOrder": 1,
        "WeaponId": "Strength",
        "ExpectedStyle": "ClaymoreCombatStyle"
    },
    2: {
        "BuildId": "Dex",
        "ConsoleName": "Dex",
        "DisplayName": "Dex",
        "UiOrder": 2,
        "WeaponId": "Dex",
        "ExpectedStyle": "DualSwordCombatStyle"
    }
}

# Reserved Console/Alias Keywords (Source: RPGCombatCatalog.cpp:154)
RESERVED_KEYWORDS = frozenset({"none", "off"})

# Target Custom Build Specification (Recipe 2 from AG-CONTENT-02)
CUSTOM_BUILD_SPEC = {
    "BuildId": "Build_Custom_Vanguard",
    "ConsoleName": "vanguard",
    "Aliases": ["vanguard_alt"],
    "DisplayName": "Vanguard Claymore",
    "UiOrder": 3,
    "LegacySlot": -1,  # INDEX_NONE
    "WeaponId": "Strength",
    "Icon": ""
}

# ---------------------------------------------------------------------------
# Native URPGBossDefinition Field Specs (Source: RPGEncounterBinding.h)
# ---------------------------------------------------------------------------
NATIVE_BOSS_STATS_FIELDS = {
    "MaxHealth": float,
    "MaxPosture": float,
    "PostureRegenDelay": float,
    "PostureRegenRate": float
}

NATIVE_ENCOUNTER_POLICY_FIELDS = {
    "GateRadius": float,
    "bResetOnPlayerRespawn": bool
}

NATIVE_STAGGER_POLICY_FIELDS = {
    "StaggerSeconds": float,
    "FreezeAtPosition": float,
    "CriticalMultiplier": float,
    "RiposteRange": float,
    "RiposteConeDegrees": float,
    "RiposteFacingDegrees": float,
    "RiposteArmSeconds": float,
    "RipostePlayerStartGap": float,
    "RiposteAlignSeconds": float,
    "RiposteImpactSeconds": float,
    "RiposteBaseDamage": float,
    "CooldownSeconds": float,
    "GetUpRate": float,
    "bHoldPostureAtZero": bool
}

NATIVE_PHASE_FLOW_FIELDS = {
    "TransitionSeconds": float,
    "bUseRoarClip": bool,
    "bPausePostureInTransition": bool,
    "bLockLeapUntilPhaseTwo": bool,
    "AttackAbilityPrefix": str,
    "LeapAbilityTag": str
}

NATIVE_FIREBALL_FIELDS = {
    "bFireballEnabled": bool,
    "FireballAbility": str,
    "FireballCooldown": list,  # FVector2D -> list of 2 finite floats
    "FireballMinRange": float,
    "FireballMaxRange": float
}

NATIVE_PHASE_DEPENDENCY_FIELDS = {
    "RoarClip": str,
    "TransitionMontage": str,
    "ImmunityEffect": str
}

NATIVE_STAGGER_PROFILE_FIELDS = {
    "bUseClips": bool,
    "bUseRiposteClips": bool,
    "bCriticalOnEveryHit": bool,
    "HitStunAbilityClassName": str,
    "FallMontage": str,
    "GetUpMontage": str,
    "FallClip": str,
    "DownClip": str,
    "RipostePlayerClip": str,
    "RiposteBossClip": str,
    "ImmunityEffect": str
}

NATIVE_DORMANT_WAKE_FIELDS = {
    "DormantClip": str,
    "WakeClip": str
}

NATIVE_BLEED_FIELDS = {
    "InitialThreshold": float,
    "ThresholdIncrease": float,
    "ThresholdMax": float,
    "HpFraction": float,
    "EffectHeight": float,
    "ProcEffect": str,
    "ProcSound": str
}

NATIVE_LOW_SWEEP_FIELDS = {
    "bEnabled": bool,
    "MoveId": str,
    "Damage": float,
    "Reach": float,
    "InnerRadius": float,
    "BladeHeight": float,
    "SweepFromDegrees": float,
    "SweepToDegrees": float
}

NATIVE_SHOCKWAVE_FIELDS = {
    "bEnabled": bool,
    "MoveId": str,
    "Damage": float,
    "StartRadius": float,
    "MaxRadius": float,
    "Speed": float,
    "Thickness": float,
    "JumpClearance": float
}

NATIVE_HEAL_PUNISH_FIELDS = {
    "bEnabled": bool,
    "MinRange": float,
    "MaxRange": float,
    "Cooldown": float,
    "Damage": float,
    "FlightTime": float,
    "MinSpeed": float,
    "MaxSpeed": float,
    "JavelinRadius": float,
    "JavelinMaxRange": float,
    "SpawnSockets": list,
    "AimHeight": float,
    "bRespondToHeal": bool,
    "bCancelJavelinsOnInterrupt": bool
}

NATIVE_LOOK_FIELDS = {
    "bEnabled": bool,
    "Body": str,
    "Pieces": list,
    "Sword": str,
    "SwordSocket": str,
}

NATIVE_CLOSE_CLIP_SWAP_FIELDS = {
    "CloseAbilityClassName": str,
    "AttackMontagesName": str,
    "A1Montage": str,
    "A3aMontage": str,
    "A3bMontage": str,
}

NATIVE_DEATH_FIELDS = {
    "DeathMode": str,
    "DeathClip": str,
    "DeathMontage": str,
    "PackDeathAbilityClassName": str,
    "PackDeathMontagesName": str,
    "PackPollSeconds": float,
    "PackEndTimeMultiplier": float,
    "HoldAtSeconds": float,
    "DyingSeconds": float,
    "BlendInSeconds": float,
    "MaxClipRestarts": int,
    "bGuardPackDeath": bool,
}

NATIVE_PHASE_CONFIG_FIELDS = {
    "PhaseId": str,
    "EntryHealthFraction": float,
    "SpeedMultiplier": float,
    "RateMultiplier": float,
    "AttackMultiplier": float
}

NATIVE_PARITY_FIELD_FIELDS = {
    "FieldPath": str,
    "Value": str,
    "Type": str,
    "Units": str,
    "SourcePath": str,
    "SourceSHA256": str,
    "SourceSite": str,
    "Origin": str,
    "Precedence": str,
    "Destination": str,
    "FirstRead": str,
    "Witness": str
}


# ---------------------------------------------------------------------------
# Native JSON to Generated Python Property Mapping (UE5.5 PyGenUtil Parity)
# ---------------------------------------------------------------------------
def pythonize_property_name(name: str, is_bool: bool = False) -> str:
    """
    Mirrors Unreal Engine 5.5 PyGenUtil::PythonizePropertyName (PyGenUtil.cpp:1833-1855):
    1. Repeatedly strips leading 'b' + uppercase and 'In' + uppercase for ANY property type.
    2. Converts CamelCase/PascalCase to snake_case lowercase using word-boundary regexes
       (which approximate the engine's CamelCaseBreakIterator beyond the 64 checked native field names).
    3. Maps reserved identifier 'self' to '_self'.
    """
    # Repeatedly strip leading 'b' + Uppercase and 'In' + Uppercase for ANY property type
    changed = True
    while changed:
        changed = False
        if len(name) >= 2 and name[0] == 'b' and name[1].isupper():
            name = name[1:]
            changed = True
        elif len(name) >= 3 and name.startswith('In') and name[2].isupper():
            name = name[2:]
            changed = True

    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    py_name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    if py_name == 'self':
        return '_self'
    return py_name


def _make_spec_mappings(spec: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, str]]:
    n2p = {}
    p2n = {}
    for k, v in spec.items():
        is_b = (v is bool)
        py_k = pythonize_property_name(k, is_bool=is_b)
        n2p[k] = py_k
        p2n[py_k] = k
    return n2p, p2n


STATS_NATIVE_TO_PY, STATS_PY_TO_NATIVE = _make_spec_mappings(NATIVE_BOSS_STATS_FIELDS)
ENCOUNTER_POLICY_NATIVE_TO_PY, ENCOUNTER_POLICY_PY_TO_NATIVE = _make_spec_mappings(NATIVE_ENCOUNTER_POLICY_FIELDS)
STAGGER_POLICY_NATIVE_TO_PY, STAGGER_POLICY_PY_TO_NATIVE = _make_spec_mappings(NATIVE_STAGGER_POLICY_FIELDS)
PHASE_FLOW_NATIVE_TO_PY, PHASE_FLOW_PY_TO_NATIVE = _make_spec_mappings(NATIVE_PHASE_FLOW_FIELDS)
FIREBALL_NATIVE_TO_PY, FIREBALL_PY_TO_NATIVE = _make_spec_mappings(NATIVE_FIREBALL_FIELDS)
PHASE_DEPENDENCY_NATIVE_TO_PY, PHASE_DEPENDENCY_PY_TO_NATIVE = _make_spec_mappings(NATIVE_PHASE_DEPENDENCY_FIELDS)
STAGGER_PROFILE_NATIVE_TO_PY, STAGGER_PROFILE_PY_TO_NATIVE = _make_spec_mappings(NATIVE_STAGGER_PROFILE_FIELDS)
DORMANT_WAKE_NATIVE_TO_PY, DORMANT_WAKE_PY_TO_NATIVE = _make_spec_mappings(NATIVE_DORMANT_WAKE_FIELDS)
BLEED_NATIVE_TO_PY, BLEED_PY_TO_NATIVE = _make_spec_mappings(NATIVE_BLEED_FIELDS)
LOW_SWEEP_NATIVE_TO_PY, LOW_SWEEP_PY_TO_NATIVE = _make_spec_mappings(NATIVE_LOW_SWEEP_FIELDS)
SHOCKWAVE_NATIVE_TO_PY, SHOCKWAVE_PY_TO_NATIVE = _make_spec_mappings(NATIVE_SHOCKWAVE_FIELDS)
HEAL_PUNISH_NATIVE_TO_PY, HEAL_PUNISH_PY_TO_NATIVE = _make_spec_mappings(NATIVE_HEAL_PUNISH_FIELDS)
LOOK_NATIVE_TO_PY, LOOK_PY_TO_NATIVE = _make_spec_mappings(NATIVE_LOOK_FIELDS)
CLOSE_CLIP_SWAP_NATIVE_TO_PY, CLOSE_CLIP_SWAP_PY_TO_NATIVE = _make_spec_mappings(NATIVE_CLOSE_CLIP_SWAP_FIELDS)
DEATH_NATIVE_TO_PY, DEATH_PY_TO_NATIVE = _make_spec_mappings(NATIVE_DEATH_FIELDS)
PHASE_CONFIG_NATIVE_TO_PY, PHASE_CONFIG_PY_TO_NATIVE = _make_spec_mappings(NATIVE_PHASE_CONFIG_FIELDS)
PARITY_FIELD_NATIVE_TO_PY, PARITY_FIELD_PY_TO_NATIVE = _make_spec_mappings(NATIVE_PARITY_FIELD_FIELDS)

STRUCT_SPECS = {
    "stats": (NATIVE_BOSS_STATS_FIELDS, STATS_NATIVE_TO_PY, STATS_PY_TO_NATIVE),
    "encounter_policy": (NATIVE_ENCOUNTER_POLICY_FIELDS, ENCOUNTER_POLICY_NATIVE_TO_PY, ENCOUNTER_POLICY_PY_TO_NATIVE),
    "stagger_policy": (NATIVE_STAGGER_POLICY_FIELDS, STAGGER_POLICY_NATIVE_TO_PY, STAGGER_POLICY_PY_TO_NATIVE),
    "phase_flow": (NATIVE_PHASE_FLOW_FIELDS, PHASE_FLOW_NATIVE_TO_PY, PHASE_FLOW_PY_TO_NATIVE),
    "fireball": (NATIVE_FIREBALL_FIELDS, FIREBALL_NATIVE_TO_PY, FIREBALL_PY_TO_NATIVE),
    "phase_dependencies": (NATIVE_PHASE_DEPENDENCY_FIELDS, PHASE_DEPENDENCY_NATIVE_TO_PY, PHASE_DEPENDENCY_PY_TO_NATIVE),
    "stagger_profile": (NATIVE_STAGGER_PROFILE_FIELDS, STAGGER_PROFILE_NATIVE_TO_PY, STAGGER_PROFILE_PY_TO_NATIVE),
    "dormant_wake": (NATIVE_DORMANT_WAKE_FIELDS, DORMANT_WAKE_NATIVE_TO_PY, DORMANT_WAKE_PY_TO_NATIVE),
    "bleed": (NATIVE_BLEED_FIELDS, BLEED_NATIVE_TO_PY, BLEED_PY_TO_NATIVE),
    "low_sweep": (NATIVE_LOW_SWEEP_FIELDS, LOW_SWEEP_NATIVE_TO_PY, LOW_SWEEP_PY_TO_NATIVE),
    "shockwave": (NATIVE_SHOCKWAVE_FIELDS, SHOCKWAVE_NATIVE_TO_PY, SHOCKWAVE_PY_TO_NATIVE),
    "heal_punish": (NATIVE_HEAL_PUNISH_FIELDS, HEAL_PUNISH_NATIVE_TO_PY, HEAL_PUNISH_PY_TO_NATIVE),
    "look": (NATIVE_LOOK_FIELDS, LOOK_NATIVE_TO_PY, LOOK_PY_TO_NATIVE),
    "close_clip_swap": (NATIVE_CLOSE_CLIP_SWAP_FIELDS, CLOSE_CLIP_SWAP_NATIVE_TO_PY, CLOSE_CLIP_SWAP_PY_TO_NATIVE),
    "death": (NATIVE_DEATH_FIELDS, DEATH_NATIVE_TO_PY, DEATH_PY_TO_NATIVE),
    "phases": (NATIVE_PHASE_CONFIG_FIELDS, PHASE_CONFIG_NATIVE_TO_PY, PHASE_CONFIG_PY_TO_NATIVE),
    "fields": (NATIVE_PARITY_FIELD_FIELDS, PARITY_FIELD_NATIVE_TO_PY, PARITY_FIELD_PY_TO_NATIVE),
}

# ---------------------------------------------------------------------------
# C++ Struct to Unreal Python Wrapper Class Mapping (Verified in DD27c Stage 2)
# ---------------------------------------------------------------------------
SPEC_TO_STRUCT_MAP: Dict[str, Tuple[str, str]] = {
    "stats": ("FRPGBossStatsConfig", "RPGBossStatsConfig"),
    "encounter_policy": ("FRPGEncounterPolicyConfig", "RPGEncounterPolicyConfig"),
    "stagger_policy": ("FRPGStaggerPolicyConfig", "RPGStaggerPolicyConfig"),
    "phase_flow": ("FRPGPhaseFlowConfig", "RPGPhaseFlowConfig"),
    "fireball": ("FRPGFireballConfig", "RPGFireballConfig"),
    "phase_dependencies": ("FRPGPhaseDependencyConfig", "RPGPhaseDependencyConfig"),
    "stagger_profile": ("FRPGStaggerProfileConfig", "RPGStaggerProfileConfig"),
    "dormant_wake": ("FRPGDormantWakeConfig", "RPGDormantWakeConfig"),
    "bleed": ("FRPGBleedConfig", "RPGBleedConfig"),
    "low_sweep": ("FRPGLowSweepConfig", "RPGLowSweepConfig"),
    "shockwave": ("FRPGShockwaveConfig", "RPGShockwaveConfig"),
    "heal_punish": ("FRPGHealPunishConfig", "RPGHealPunishConfig"),
    "look": ("FRPGLookConfig", "RPGLookConfig"),
    "close_clip_swap": ("FRPGCloseClipSwapConfig", "RPGCloseClipSwapConfig"),
    "death": ("FRPGDeathConfig", "RPGDeathConfig"),
    "phases": ("FRPGPhaseConfig", "RPGPhaseConfig"),
    "fields": ("FRPGParityField", "RPGParityField"),
}

# C++ FName property names requiring unreal.Name wrapper
FNAME_PROPERTIES = {
    "MoveId", "SwordSocket", "CloseAbilityClassName", "AttackMontagesName",
    "PackDeathAbilityClassName", "PackDeathMontagesName", "HitStunAbilityClassName",
    "PhaseId", "AttackAbilityPrefix", "LeapAbilityTag", "FireballAbility"
}


# ---------------------------------------------------------------------------
# Explicit Conversion Helpers (Order A-212 / DD27c Evidence Grounded)
# ---------------------------------------------------------------------------
def to_soft_ref(path_str: Any, unreal_module: Any = None) -> Tuple[Any, str]:
    """
    Converts path string to soft object reference representation without assumptions.
    Tries unreal.SoftObjectPath(path_str) if unreal_module has SoftObjectPath.
    Falls back to str.
    Returns: (converted_value, form_name_used)
    """
    if unreal_module is not None and hasattr(unreal_module, "SoftObjectPath") and callable(getattr(unreal_module, "SoftObjectPath")):
        try:
            return unreal_module.SoftObjectPath(str(path_str) if path_str else ""), "unreal.SoftObjectPath"
        except Exception:
            pass
    return str(path_str) if path_str is not None else "", "str"


def to_fname(name_str: Any, unreal_module: Any = None) -> Tuple[Any, str]:
    """
    Converts name string to FName representation.
    Tries unreal.Name(name_str) if unreal_module has Name.
    Falls back to str.
    Returns: (converted_value, form_name_used)
    """
    if unreal_module is not None and hasattr(unreal_module, "Name") and callable(getattr(unreal_module, "Name")):
        try:
            return unreal_module.Name(str(name_str) if name_str else ""), "unreal.Name"
        except Exception:
            pass
    return str(name_str) if name_str is not None else "", "str"


def to_death_mode(mode_val: Any, unreal_module: Any = None) -> Tuple[Any, str]:
    """
    Converts death mode string to ERPGBossDeathMode enumerator.
    Maps:
      'PackMontage' / 'PACK_MONTAGE' -> unreal.RPGBossDeathMode.PACK_MONTAGE
      'OwnClip' / 'OWN_CLIP' -> unreal.RPGBossDeathMode.OWN_CLIP
    Returns: (converted_value, form_name_used)
    """
    s = str(mode_val).upper().replace("ERPGBOSSDEATHMODE::", "").replace(" ", "_")
    attr_name = "OWN_CLIP" if ("OWN_CLIP" in s or "OWNCLIP" in s) else "PACK_MONTAGE"

    if unreal_module is not None and hasattr(unreal_module, "RPGBossDeathMode"):
        enum_cls = getattr(unreal_module, "RPGBossDeathMode")
        if hasattr(enum_cls, attr_name):
            return getattr(enum_cls, attr_name), f"unreal.RPGBossDeathMode.{attr_name}"
    return attr_name, f"str({attr_name})"


def convert_property_for_engine(native_key: str, val: Any, expected_type: Any, unreal_module: Any = None) -> Tuple[Any, str]:
    """
    Explicit, documented property value conversion for Unreal Engine 5.5 Python API:
    - float: to_float32(val)
    - int: int(val)
    - bool: bool(val)
    - DeathMode: to_death_mode(val, unreal_module)
    - FName properties: to_fname(val, unreal_module)
    - TSoftObjectPtr (mesh/anim/vfx/sound soft paths): to_soft_ref(val, unreal_module)
    - FString (in parity fields): str(val)
    - FVector2D (FireballCooldown): unreal.Vector2D or [float, float]
    - TArray<FName> (SpawnSockets): list of to_fname
    - TArray<TSoftObjectPtr> (Pieces): list of to_soft_ref
    """
    if expected_type is float and val is not None:
        return to_float32(val), "to_float32"
    if expected_type is int and val is not None:
        return int(val), "int"
    if expected_type is bool and val is not None:
        return bool(val), "bool"

    if native_key == "DeathMode":
        return to_death_mode(val, unreal_module)

    if native_key in FNAME_PROPERTIES:
        return to_fname(val, unreal_module)

    if expected_type is list:
        if native_key == "FireballCooldown":
            x = float(val[0]) if len(val) > 0 else 0.0
            y = float(val[1]) if len(val) > 1 else 0.0
            if unreal_module is not None and hasattr(unreal_module, "Vector2D") and callable(getattr(unreal_module, "Vector2D")):
                try:
                    return unreal_module.Vector2D(x, y), "unreal.Vector2D"
                except Exception:
                    pass
            return [to_float32(x), to_float32(y)], "list[float32]"
        elif native_key == "SpawnSockets":
            items = []
            for item in (val or []):
                cv, _ = to_fname(item, unreal_module)
                items.append(cv)
            return items, "list[unreal.Name]"
        elif native_key == "Pieces":
            items = []
            for item in (val or []):
                cv, _ = to_soft_ref(item, unreal_module)
                items.append(cv)
            return items, "list[unreal.SoftObjectPath]"
        else:
            return list(val or []), "list"

    if expected_type is str:
        is_soft_path = any(kw in native_key for kw in [
            "Clip", "Montage", "Effect", "Sound", "Body", "Sword", "Skeleton", "Animation"
        ])
        if is_soft_path:
            return to_soft_ref(val, unreal_module)
        return str(val if val is not None else ""), "str"

    return copy.deepcopy(val), "deepcopy"


def create_struct_instance(struct_key: str, native_dict: Dict[str, Any], unreal_module: Any = None) -> Any:
    """
    Instantiates an Unreal Engine UStruct wrapper via its default constructor
    (e.g. unreal.RPGBleedConfig()), and populates each property via inst.set_editor_property(py_name, converted_value).
    NEVER passes dictionaries as struct properties; NEVER uses setattr/getattr/hasattr attribute style.
    If unreal_module is None or struct class unavailable (pure offline fallback), returns dict with pythonized keys.
    """
    if struct_key not in STRUCT_SPECS:
        raise KeyError(f"Unknown struct key '{struct_key}'")

    fields_spec, _, _ = STRUCT_SPECS[struct_key]

    if unreal_module is not None:
        cpp_name, py_class_name = SPEC_TO_STRUCT_MAP[struct_key]
        if hasattr(unreal_module, py_class_name):
            cls = getattr(unreal_module, py_class_name)
            inst = cls()
            for native_k, expected_type in fields_spec.items():
                py_k = pythonize_property_name(native_k)
                if native_k in native_dict:
                    raw_val = native_dict[native_k]
                    converted_val, _ = convert_property_for_engine(native_k, raw_val, expected_type, unreal_module)
                    inst.set_editor_property(py_k, converted_val)
            return inst

    # Fallback for pure offline non-unreal dictionary mode
    res = {}
    for native_k, expected_type in fields_spec.items():
        py_k = pythonize_property_name(native_k)
        if native_k in native_dict:
            res[py_k] = native_dict[native_k]
    return res


def map_native_dict_to_python_keys(native_dict: Dict[str, Any], fields_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translates native C++ CamelCase JSON property names to generated UE5.5 Python snake_case
    property names, stripping leading 'b'+upper and 'In'+upper per PyGenUtil::PythonizePropertyName.
    Converts list cooldowns into explicit 2-float elements.
    Validates that float values do not overflow 32-bit single-precision float.
    """
    py_dict = {}
    for native_k, val in native_dict.items():
        py_k = pythonize_property_name(native_k)
        expected_type = fields_spec.get(native_k)
        if expected_type is float and val is not None:
            to_float32(val)
            py_dict[py_k] = float(val)
        elif expected_type is list and native_k == "FireballCooldown" and isinstance(val, (list, tuple)):
            for x in val:
                to_float32(x)
            py_dict[py_k] = [float(x) for x in val]
        elif expected_type is list and native_k in ("SpawnSockets", "Pieces") and isinstance(val, (list, tuple)):
            py_dict[py_k] = [str(x) for x in val]
        else:
            py_dict[py_k] = copy.deepcopy(val)
    return py_dict


def extract_canonical_primitives(struct_obj: Any, fields_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reads back actual scalar, vector, and soft path properties from an Unreal Python struct
    wrapper or dictionary, converting them to canonical JSON primitives keyed by the native
    C++ CamelCase property names.

    CRITICAL INVARIANTS (PER ORDER A-212 / DD27c EVIDENCE):
    - In Unreal Engine 5.5, struct wrappers expose properties ONLY via inst.get_editor_property(py_name).
      hasattr(struct_obj, py_name) is FALSE for all struct properties.
    - If struct_obj has get_editor_property, properties MUST be read via get_editor_property.
    - Dictionaries are read ONLY by generated Python keys.
    """
    canonical = {}
    has_get_editor_prop = hasattr(struct_obj, "get_editor_property") and callable(getattr(struct_obj, "get_editor_property"))

    for native_k, expected_type in fields_spec.items():
        py_k = pythonize_property_name(native_k)

        raw_val = None
        if isinstance(struct_obj, dict):
            if py_k in struct_obj:
                raw_val = struct_obj[py_k]
            else:
                raise KeyError(f"Missing generated property '{py_k}' in struct dictionary (native name '{native_k}')")
        elif has_get_editor_prop:
            try:
                raw_val = struct_obj.get_editor_property(py_k)
            except Exception as ex:
                raise AttributeError(
                    f"Struct wrapper get_editor_property failed for '{py_k}' "
                    f"(native CamelCase name '{native_k}'): {str(ex)}"
                )
        elif hasattr(struct_obj, py_k):
            raw_val = getattr(struct_obj, py_k)
        else:
            raise AttributeError(
                f"Struct wrapper missing generated attribute '{py_k}' "
                f"(native CamelCase name '{native_k}' is not exposed by Unreal Python wrappers)"
            )

        if expected_type is float:
            canonical[native_k] = float(raw_val)
        elif expected_type is int:
            canonical[native_k] = int(raw_val)
        elif expected_type is bool:
            canonical[native_k] = bool(raw_val)
        elif native_k == "DeathMode":
            if hasattr(raw_val, "name"):
                canonical[native_k] = str(raw_val.name)
            else:
                s = str(raw_val).upper().replace("ERPGBOSSDEATHMODE::", "").replace(" ", "_")
                canonical[native_k] = "PACK_MONTAGE" if "PACK" in s else "OWN_CLIP"
        elif expected_type is str:
            if hasattr(raw_val, "to_string") and callable(getattr(raw_val, "to_string")):
                canonical[native_k] = str(raw_val.to_string())
            elif hasattr(raw_val, "asset_path_name"):
                canonical[native_k] = str(raw_val.asset_path_name)
            else:
                canonical[native_k] = str(raw_val)
        elif expected_type is list:
            if native_k == "FireballCooldown":
                if hasattr(raw_val, "x") and hasattr(raw_val, "y"):
                    canonical[native_k] = [float(raw_val.x), float(raw_val.y)]
                elif isinstance(raw_val, (list, tuple)):
                    canonical[native_k] = [float(x) for x in raw_val]
                else:
                    raise TypeError(f"Cannot extract Vector2D from {type(raw_val)}")
            elif native_k in ("SpawnSockets", "Pieces"):
                canonical[native_k] = [
                    str(x.to_string()) if hasattr(x, "to_string") else (str(x.asset_path_name) if hasattr(x, "asset_path_name") else str(x))
                    for x in (raw_val or [])
                ]
            else:
                canonical[native_k] = list(raw_val or [])
        else:
            canonical[native_k] = copy.deepcopy(raw_val)

    return canonical


def normalize_native_expected_for_readback(native_dict: Dict[str, Any], fields_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes expected native dictionary values for canonical readback comparison:
    Simulates Unreal Engine float32 storage by round-tripping float values through
    IEEE 754 single-precision float (struct 'f').
    Refuses any requested float value that is finite in float64 but overflows float32.
    """
    normalized = {}
    for k, v in native_dict.items():
        expected_type = fields_spec.get(k)
        if expected_type is float and v is not None:
            normalized[k] = to_float32(v)
        elif k == "DeathMode" and isinstance(v, str):
            s = str(v).upper().replace("ERPGBOSSDEATHMODE::", "").replace(" ", "_")
            normalized[k] = "PACK_MONTAGE" if "PACK" in s else "OWN_CLIP"
        elif expected_type is list and k == "FireballCooldown" and isinstance(v, (list, tuple)):
            normalized[k] = [to_float32(x) for x in v]
        elif expected_type is list and k in ("SpawnSockets", "Pieces") and isinstance(v, (list, tuple)):
            normalized[k] = [str(x) for x in v]
        elif isinstance(v, dict) and isinstance(expected_type, dict):
            normalized[k] = normalize_native_expected_for_readback(v, expected_type)
        else:
            normalized[k] = copy.deepcopy(v)
    return normalized


# ---------------------------------------------------------------------------
# Complete Native Capability & Domain Validators
# ---------------------------------------------------------------------------
def validate_boss_stats_domain(stats_data: Dict[str, Any]) -> List[str]:
    """
    Enforces native capability bounds from RPGBossStatsAdapters.cpp:73-99:
    - MaxHealth must be strictly greater than NATIVE_HEALTH_OVERRIDE_FLOOR (1.0).
    - MaxPosture must be strictly positive (> 0.0).
    - PostureRegenDelay and PostureRegenRate must be non-negative (>= 0.0).
    """
    errs = []
    if not isinstance(stats_data, dict):
        return ["stats must be a dictionary"]
    max_hp = stats_data.get("MaxHealth")
    if max_hp is not None and type(max_hp) in (float, int) and not isinstance(max_hp, bool):
        if float(max_hp) <= NATIVE_HEALTH_OVERRIDE_FLOOR:
            errs.append(f"stats.MaxHealth {max_hp} must be strictly greater than {NATIVE_HEALTH_OVERRIDE_FLOOR} (native health override floor)")
    max_posture = stats_data.get("MaxPosture")
    if max_posture is not None and type(max_posture) in (float, int) and not isinstance(max_posture, bool):
        if float(max_posture) <= 0.0:
            errs.append(f"stats.MaxPosture {max_posture} must be strictly positive (> 0.0)")
    for regen_fld in ("PostureRegenDelay", "PostureRegenRate"):
        r_val = stats_data.get(regen_fld)
        if r_val is not None and type(r_val) in (float, int) and not isinstance(r_val, bool):
            if float(r_val) < 0.0:
                errs.append(f"stats.{regen_fld} {r_val} cannot be negative")
    return errs


def validate_encounter_policy_domain(enc_data: Dict[str, Any]) -> List[str]:
    """
    Enforces native bounds from RPGBossEncounterPolicyAdapters.cpp:57-65:
    - GateRadius must be finite and not negative (>= 0.0; 0 = no gate).
    """
    errs = []
    if not isinstance(enc_data, dict):
        return ["encounter_policy must be a dictionary"]
    gr = enc_data.get("GateRadius")
    if gr is not None and type(gr) in (float, int) and not isinstance(gr, bool):
        if float(gr) < 0.0:
            errs.append(f"encounter_policy.GateRadius {gr} cannot be negative (0 or more)")
    return errs


def validate_stagger_policy_domain(stg_data: Dict[str, Any]) -> List[str]:
    """
    Enforces exact scalar domain bounds from RPGBossStaggerPolicyAdapters.h:20-28:
    - Non-negative fields (zero keeps native immediate / empty / no-cooldown meaning):
      StaggerSeconds, FreezeAtPosition, RiposteRange, RiposteArmSeconds,
      RipostePlayerStartGap, RiposteImpactSeconds, RiposteBaseDamage, CooldownSeconds.
    - Strictly positive fields (divided by in native code):
      RiposteAlignSeconds (> 0.0), GetUpRate (> 0.0). Both require finite float inverse.
    - Angular bounds: RiposteConeDegrees and RiposteFacingDegrees in [0.0, 360.0].
    - CriticalMultiplier at least 1.0 (NATIVE_CRITICAL_MULTIPLIER_FLOOR); below 1 adds health.
    """
    errs = []
    if not isinstance(stg_data, dict):
        return ["stagger_policy must be a dictionary"]

    non_neg_fields = [
        "StaggerSeconds", "FreezeAtPosition", "RiposteRange", "RiposteArmSeconds",
        "RipostePlayerStartGap", "RiposteImpactSeconds", "RiposteBaseDamage", "CooldownSeconds"
    ]
    for f in non_neg_fields:
        val = stg_data.get(f)
        if val is not None and type(val) in (float, int) and not isinstance(val, bool):
            if float(val) < 0.0:
                errs.append(f"stagger_policy.{f} {val} cannot be negative")

    for pos_f in ("RiposteAlignSeconds", "GetUpRate"):
        val = stg_data.get(pos_f)
        if val is not None and type(val) in (float, int) and not isinstance(val, bool):
            f_val = float(val)
            if f_val <= 0.0:
                errs.append(f"stagger_policy.{pos_f} {val} must be strictly positive (> 0.0)")
            elif not math.isfinite(1.0 / f_val):
                errs.append(f"stagger_policy.{pos_f} {val} has non-finite inverse")

    for ang_f in ("RiposteConeDegrees", "RiposteFacingDegrees"):
        val = stg_data.get(ang_f)
        if val is not None and type(val) in (float, int) and not isinstance(val, bool):
            f_val = float(val)
            if f_val < 0.0 or f_val > 360.0:
                errs.append(f"stagger_policy.{ang_f} {val} out of angular range [0.0, 360.0]")

    crit = stg_data.get("CriticalMultiplier")
    if crit is not None and type(crit) in (float, int) and not isinstance(crit, bool):
        if float(crit) < NATIVE_CRITICAL_MULTIPLIER_FLOOR:
            errs.append(f"stagger_policy.CriticalMultiplier {crit} below native capability floor {NATIVE_CRITICAL_MULTIPLIER_FLOOR}")

    return errs


def validate_phase_flow_domain(flow_data: Dict[str, Any]) -> List[str]:
    """
    Enforces native phase flow bounds:
    - TransitionSeconds must be non-negative (>= 0.0).
    """
    errs = []
    if not isinstance(flow_data, dict):
        return ["phase_flow must be a dictionary"]
    ts = flow_data.get("TransitionSeconds")
    if ts is not None and type(ts) in (float, int) and not isinstance(ts, bool):
        if float(ts) < 0.0:
            errs.append(f"phase_flow.TransitionSeconds {ts} cannot be negative")
    return errs


def validate_fireball_domain(fire_data: Dict[str, Any]) -> List[str]:
    """
    Enforces native fireball cooldown and range bounds:
    - Cooldown min and max must be non-negative, and max >= min.
    - MinRange >= 0.0, MaxRange >= MinRange.
    """
    errs = []
    if not isinstance(fire_data, dict):
        return ["fireball must be a dictionary"]
    cd = fire_data.get("FireballCooldown")
    if isinstance(cd, list) and len(cd) == 2:
        c0, c1 = cd[0], cd[1]
        if type(c0) in (float, int) and not isinstance(c0, bool) and type(c1) in (float, int) and not isinstance(c1, bool):
            if float(c0) < 0.0:
                errs.append(f"fireball.FireballCooldown min {c0} cannot be negative")
            if float(c1) < float(c0):
                errs.append(f"fireball.FireballCooldown max {c1} is less than min {c0}")
    min_r = fire_data.get("FireballMinRange")
    max_r = fire_data.get("FireballMaxRange")
    if min_r is not None and type(min_r) in (float, int) and not isinstance(min_r, bool):
        if float(min_r) < 0.0:
            errs.append(f"fireball.FireballMinRange {min_r} cannot be negative")
    if min_r is not None and max_r is not None and type(min_r) in (float, int) and type(max_r) in (float, int) and not isinstance(min_r, bool) and not isinstance(max_r, bool):
        if float(max_r) < float(min_r):
            errs.append(f"fireball.FireballMaxRange {max_r} is less than MinRange {min_r}")
    return errs


def validate_phase_config_domain(phase_data: Dict[str, Any], idx: int = 0) -> List[str]:
    """
    Enforces native capability bounds from RPGBossPhaseAdapters.cpp:115-154:
    - EntryHealthFraction strictly above 0.0 and at most 1.0 (0.0 < fraction <= 1.0; 0.0 rejected).
    - SpeedMultiplier strictly positive (> 0.0) with finite float inverse.
    - RateMultiplier strictly positive (> 0.0) with finite float inverse.
    - AttackMultiplier at least NATIVE_DAMAGE_SCALE_FLOOR (1.0).
    """
    errs = []
    if not isinstance(phase_data, dict):
        return [f"phases[{idx}] must be a dictionary"]

    frac = phase_data.get("EntryHealthFraction")
    if frac is not None and type(frac) in (float, int) and not isinstance(frac, bool):
        if float(frac) <= 0.0 or float(frac) > 1.0:
            errs.append(f"phases[{idx}].EntryHealthFraction {frac} out of range; expected strictly above 0.0 and at most 1.0 (0.0 < fraction <= 1.0)")

    speed = phase_data.get("SpeedMultiplier")
    if speed is not None and type(speed) in (float, int) and not isinstance(speed, bool):
        if float(speed) <= 0.0:
            errs.append(f"phases[{idx}].SpeedMultiplier {speed} must be strictly positive (> 0.0)")
        elif not math.isfinite(1.0 / float(speed)):
            errs.append(f"phases[{idx}].SpeedMultiplier {speed} has non-finite inverse")

    rate = phase_data.get("RateMultiplier")
    if rate is not None and type(rate) in (float, int) and not isinstance(rate, bool):
        if float(rate) <= 0.0:
            errs.append(f"phases[{idx}].RateMultiplier {rate} must be strictly positive (> 0.0)")
        elif not math.isfinite(1.0 / float(rate)):
            errs.append(f"phases[{idx}].RateMultiplier {rate} has non-finite inverse")

    atk = phase_data.get("AttackMultiplier")
    if atk is not None and type(atk) in (float, int) and not isinstance(atk, bool):
        if float(atk) < NATIVE_DAMAGE_SCALE_FLOOR:
            errs.append(f"phases[{idx}].AttackMultiplier {atk} must be at least {NATIVE_DAMAGE_SCALE_FLOOR} (native damage scale floor)")

    return errs

# ---------------------------------------------------------------------------
# Bleed Status Policy Domain Validator (DD19 / RPGBossBleedAdapters.cpp)
# ---------------------------------------------------------------------------
# Copied exactly from UE 5.5 Core/Public/UObject/NameTypes.h:
# Line 168:
INVALID_OBJECTNAME_CHARACTERS = "\"' ,/.:|&!~\n\r\t@#(){}[]=;^%$`"
# Line 174:
INVALID_LONGPACKAGE_CHARACTERS = "\\:*?\"<>|' ,.&!~\n\r\t@#"

INVALID_OBJECTNAME_CHARS = set(INVALID_OBJECTNAME_CHARACTERS)
INVALID_LONGPACKAGE_CHARS = set(INVALID_LONGPACKAGE_CHARACTERS)


def validate_soft_path_structure(path_str: str) -> Tuple[bool, str]:
    """
    Validates structure of a soft object path as text (no registry query, no load).
    Mirrors RPGBossBleedAdapters.cpp:PathProblem:
    - Must start with '/'
    - Cannot contain whitespace or control characters (< 32)
    - Cannot name a sub-object (':')
    - Must have a package folder (last_slash > 0)
    - Must end in <package>.<asset> (dot > 0 and dot < len(leaf) - 1)
    - Package name and object name must follow engine text-only validation rules.
    Returns (True, "") or (False, reason_string).
    """
    if not isinstance(path_str, str) or not path_str or not path_str.startswith("/"):
        return False, "it must start with '/'"
    for c in path_str:
        if c.isspace() or ord(c) < 32:
            return False, "it contains whitespace or a control character"
        if c == ':':
            return False, "it names a sub-object"
    last_slash = path_str.rfind('/')
    leaf = path_str[last_slash + 1:]
    dot = leaf.find('.')
    if dot <= 0 or dot >= len(leaf) - 1:
        return False, "it must end in <package>.<asset>"
    if last_slash <= 0:
        return False, "it has no package folder"
    package = path_str[:last_slash + 1] + leaf[:dot]
    asset_name = leaf[dot + 1:]
    for c in package:
        if c in INVALID_LONGPACKAGE_CHARS:
            return False, f"package contains invalid character '{c}'"
    segments = package.split('/')
    for seg in segments[1:]:
        if not seg or seg == '.' or seg == '..':
            return False, "package contains invalid segment"
    for c in asset_name:
        if c in INVALID_OBJECTNAME_CHARS or c == '.':
            return False, f"object name contains invalid character '{c}'"
    return True, ""


def validate_bleed_domain(bleed_data: Dict[str, Any]) -> List[str]:
    """
    Enforces native capability bounds from RPGBossBleedAdapters.cpp: ValidateBleed:
    Checks run in this exact order:
    (1) EVERY scalar finite first: InitialThreshold, ThresholdIncrease, ThresholdMax, HpFraction, EffectHeight
    (2) The domains, in field order:
        - InitialThreshold > 0.0 (the first proc needs a buildup above zero)
        - ThresholdIncrease >= 0.0 (zero keeps a constant threshold)
        - ThresholdMax >= InitialThreshold (proc takes Min(Threshold + Increase, Max))
        - 0.0 <= HpFraction <= 1.0 (expected a fraction within 0 and 1)
        - EffectHeight is finite and SIGNED (no floor)
    (3) The two references, ProcEffect first, then ProcSound:
        - Required (not None, not empty): InvalidDependency.Missing
        - Structurally well-formed soft path: InvalidDependency.Malformed
    """
    errs = []
    if not isinstance(bleed_data, dict):
        return ["bleed must be a dictionary"]

    # (1) Every scalar finite first
    scalar_fields = [
        ("Bleed.InitialThreshold", bleed_data.get("InitialThreshold")),
        ("Bleed.ThresholdIncrease", bleed_data.get("ThresholdIncrease")),
        ("Bleed.ThresholdMax", bleed_data.get("ThresholdMax")),
        ("Bleed.HpFraction", bleed_data.get("HpFraction")),
        ("Bleed.EffectHeight", bleed_data.get("EffectHeight")),
    ]
    for field_path, val in scalar_fields:
        ok, _ = validate_finite_float(val, field_path)
        if not ok:
            errs.append(f"InvalidBleed.NotFinite: {field_path}={val}")
            return errs

    init_thresh = float(bleed_data["InitialThreshold"])
    thresh_inc = float(bleed_data["ThresholdIncrease"])
    thresh_max = float(bleed_data["ThresholdMax"])
    hp_frac = float(bleed_data["HpFraction"])
    eff_height = float(bleed_data["EffectHeight"])

    # (2) The domains, in field order
    if init_thresh <= 0.0:
        errs.append(f"InvalidBleed.NotPositive: Bleed.InitialThreshold={init_thresh}, the first proc needs a buildup above zero")
        return errs

    if thresh_inc < 0.0:
        errs.append(f"InvalidBleed.Negative: Bleed.ThresholdIncrease={thresh_inc}, expected 0 or more")
        return errs

    if thresh_max < init_thresh:
        errs.append(
            f"InvalidBleed.ThresholdMaxBelowInitial: Bleed.ThresholdMax={thresh_max} is below Bleed.InitialThreshold={init_thresh}, the native proc would lower the threshold"
        )
        return errs

    if hp_frac < 0.0 or hp_frac > 1.0:
        errs.append(f"InvalidBleed.FractionOutOfRange: Bleed.HpFraction={hp_frac}, expected a fraction within 0 and 1")
        return errs

    # (3) The two references, ProcEffect first, then ProcSound
    ref_fields = [
        ("Bleed.ProcEffect", bleed_data.get("ProcEffect")),
        ("Bleed.ProcSound", bleed_data.get("ProcSound")),
    ]
    for field_path, ref_val in ref_fields:
        if ref_val is None or ref_val == "":
            errs.append(f"InvalidDependency.Missing: {field_path} is required and is not set")
            return errs
        ref_str = str(ref_val.asset_path_name if hasattr(ref_val, "asset_path_name") else ref_val)
        ok, reason = validate_soft_path_structure(ref_str)
        if not ok:
            errs.append(f"InvalidDependency.Malformed: {field_path}={ref_str}, {reason}")
            return errs

    return errs


# ---------------------------------------------------------------------------
# Low Sweep Policy Domain Validator (DD20 / RPGBossLowSweepAdapters.cpp)
# ---------------------------------------------------------------------------
def validate_low_sweep_domain(low_sweep_data: Dict[str, Any]) -> List[str]:
    """
    Enforces native capability bounds from RPGBossLowSweepAdapters.cpp: ValidateLowSweep (DD20):
    Qualification: Pending DD20 live verification run by Codex.
    MoveId is SYNTACTIC IDENTITY ONLY (does not prove tracker resolution, timing or ability execution).
    Checks run in this exact order:
    (1) ALL SIX scalar floats finite first in declaration order:
        - Damage ("LowSweep.Damage")
        - Reach ("LowSweep.Reach")
        - InnerRadius ("LowSweep.InnerRadius")
        - BladeHeight ("LowSweep.BladeHeight")
        - SweepFromDegrees ("LowSweep.SweepFromDegrees")
        - SweepToDegrees ("LowSweep.SweepToDegrees")
        Failure token: "InvalidLowSweep.NotFinite: <Field>"
    (2) The domains in that exact order:
        - Damage >= 0.0 ("InvalidLowSweep.Negative: LowSweep.Damage")
        - Reach > 0.0 ("InvalidLowSweep.NotPositive: LowSweep.Reach")
        - InnerRadius >= 0.0 ("InvalidLowSweep.Negative: LowSweep.InnerRadius")
        - InnerRadius < Reach ("InvalidLowSweep.InnerNotBelowReach: LowSweep.InnerRadius")
        - BladeHeight > 0.0 ("InvalidLowSweep.NotPositive: LowSweep.BladeHeight")
        - -360.0 <= SweepFromDegrees <= 360.0 ("InvalidLowSweep.AngleOutOfRange: LowSweep.SweepFromDegrees")
        - -360.0 <= SweepToDegrees <= 360.0 ("InvalidLowSweep.AngleOutOfRange: LowSweep.SweepToDegrees")
    (3) MoveId syntactic validation:
        - Not None, not empty, not "None": "InvalidDependency.Missing: LowSweep.MoveId"
        - No whitespace or control character: "InvalidDependency.Malformed: LowSweep.MoveId"
    Note: bEnabled may be True or False; disabled records still validate completely.
    Equal and reversed angles, +-360, sub-1 reach/height (e.g. 0.5) are legal and accepted.
    """
    errs = []
    if not isinstance(low_sweep_data, dict):
        return ["low_sweep must be a dictionary"]

    # (1) All six scalars finite first in declaration order
    scalar_fields = [
        ("LowSweep.Damage", low_sweep_data.get("Damage")),
        ("LowSweep.Reach", low_sweep_data.get("Reach")),
        ("LowSweep.InnerRadius", low_sweep_data.get("InnerRadius")),
        ("LowSweep.BladeHeight", low_sweep_data.get("BladeHeight")),
        ("LowSweep.SweepFromDegrees", low_sweep_data.get("SweepFromDegrees")),
        ("LowSweep.SweepToDegrees", low_sweep_data.get("SweepToDegrees")),
    ]
    for field_name, val in scalar_fields:
        ok, _ = validate_finite_float(val, field_name)
        if not ok:
            errs.append(f"InvalidLowSweep.NotFinite: {field_name}")
            return errs

    damage = float(low_sweep_data["Damage"])
    reach = float(low_sweep_data["Reach"])
    inner_radius = float(low_sweep_data["InnerRadius"])
    blade_height = float(low_sweep_data["BladeHeight"])
    sweep_from = float(low_sweep_data["SweepFromDegrees"])
    sweep_to = float(low_sweep_data["SweepToDegrees"])

    # (2) Domains in declaration order
    if damage < 0.0:
        errs.append("InvalidLowSweep.Negative: LowSweep.Damage")
        return errs

    if reach <= 0.0:
        errs.append("InvalidLowSweep.NotPositive: LowSweep.Reach")
        return errs

    if inner_radius < 0.0:
        errs.append("InvalidLowSweep.Negative: LowSweep.InnerRadius")
        return errs

    if inner_radius >= reach:
        errs.append("InvalidLowSweep.InnerNotBelowReach: LowSweep.InnerRadius")
        return errs

    if blade_height <= 0.0:
        errs.append("InvalidLowSweep.NotPositive: LowSweep.BladeHeight")
        return errs

    if sweep_from < -360.0 or sweep_from > 360.0:
        errs.append("InvalidLowSweep.AngleOutOfRange: LowSweep.SweepFromDegrees")
        return errs

    if sweep_to < -360.0 or sweep_to > 360.0:
        errs.append("InvalidLowSweep.AngleOutOfRange: LowSweep.SweepToDegrees")
        return errs

    # (3) MoveId syntactic validation
    move_id = low_sweep_data.get("MoveId")
    if move_id is None or move_id == "" or move_id == "None":
        errs.append("InvalidDependency.Missing: LowSweep.MoveId")
        return errs

    move_id_str = str(move_id)
    for c in move_id_str:
        if c.isspace() or ord(c) < 32:
            errs.append("InvalidDependency.Malformed: LowSweep.MoveId")
            return errs

    return errs

MAX_AUTHORED_SHOCKWAVE_MAGNITUDE = 1.0e6


# ---------------------------------------------------------------------------
# Shockwave Policy Domain Validation (C262 / C263 / C264 DD21)
# ---------------------------------------------------------------------------
def validate_shockwave_domain(shockwave_data: Dict[str, Any]) -> List[str]:
    """
    Enforces native capability bounds from RPGBossShockwave.h/.cpp (DD21)
    per Claude C-262, C-263, and C-264 decisions:
    Explicit qualification: Pending DD21 live verification run by Codex.
    MoveId is SYNTACTIC IDENTITY ONLY (does not prove tracker resolution, timing or ability execution).
    Ceiling: RPGBossShockwaveAdapters::MaxAuthoredMagnitude = 1.0e6f (cm or cm/s, 10 km)
             on StartRadius, MaxRadius, Speed, Thickness, JumpClearance.
    Checks run in this exact order:
    (1) ALL SIX scalar floats finite first in declaration order:
        - Damage ("Shockwave.Damage")
        - StartRadius ("Shockwave.StartRadius")
        - MaxRadius ("Shockwave.MaxRadius")
        - Speed ("Shockwave.Speed")
        - Thickness ("Shockwave.Thickness")
        - JumpClearance ("Shockwave.JumpClearance")
        Failure token: "InvalidShockwave.NotFinite: <Field>"
    (2) The domains in that exact declaration order:
        - Damage >= 0.0 ("InvalidShockwave.Negative: Shockwave.Damage") (no ceiling: subtracted from health)
        - StartRadius >= 0.0 ("InvalidShockwave.Negative: Shockwave.StartRadius")
        - StartRadius <= 1.0e6 ("InvalidShockwave.AboveCeiling: Shockwave.StartRadius")
        - MaxRadius > 0.0 ("InvalidShockwave.NotPositive: Shockwave.MaxRadius")
        - MaxRadius <= 1.0e6 ("InvalidShockwave.AboveCeiling: Shockwave.MaxRadius")
        - MaxRadius > StartRadius ("InvalidShockwave.MaxNotAboveStart: Shockwave.MaxRadius")
        - Speed > 0.0 ("InvalidShockwave.NotPositive: Shockwave.Speed")
        - Speed <= 1.0e6 ("InvalidShockwave.AboveCeiling: Shockwave.Speed")
        - Thickness > 0.0 ("InvalidShockwave.NotPositive: Shockwave.Thickness")
        - Thickness <= 1.0e6 ("InvalidShockwave.AboveCeiling: Shockwave.Thickness")
        - JumpClearance > 0.0 ("InvalidShockwave.NotPositive: Shockwave.JumpClearance" - AMENDED by C-263)
        - JumpClearance <= 1.0e6 ("InvalidShockwave.AboveCeiling: Shockwave.JumpClearance")
    (3) MoveId syntactic validation:
        - Not None, not empty, not "None": "InvalidDependency.Missing: Shockwave.MoveId"
        - No whitespace or control character: "InvalidDependency.Malformed: Shockwave.MoveId"
    Note: bEnabled may be True or False; disabled records still validate completely.
    """
    errs = []
    if not isinstance(shockwave_data, dict):
        return ["shockwave must be a dictionary"]

    # (1) All six scalars finite first in declaration order
    scalar_fields = [
        ("Shockwave.Damage", shockwave_data.get("Damage")),
        ("Shockwave.StartRadius", shockwave_data.get("StartRadius")),
        ("Shockwave.MaxRadius", shockwave_data.get("MaxRadius")),
        ("Shockwave.Speed", shockwave_data.get("Speed")),
        ("Shockwave.Thickness", shockwave_data.get("Thickness")),
        ("Shockwave.JumpClearance", shockwave_data.get("JumpClearance")),
    ]
    for field_name, val in scalar_fields:
        ok, _ = validate_finite_float(val, field_name)
        if not ok:
            errs.append(f"InvalidShockwave.NotFinite: {field_name}")
            return errs

    damage = float(shockwave_data["Damage"])
    start_radius = float(shockwave_data["StartRadius"])
    max_radius = float(shockwave_data["MaxRadius"])
    speed = float(shockwave_data["Speed"])
    thickness = float(shockwave_data["Thickness"])
    jump_clearance = float(shockwave_data["JumpClearance"])

    # (2) Domains in declaration order
    if damage < 0.0:
        errs.append("InvalidShockwave.Negative: Shockwave.Damage")
        return errs

    if start_radius < 0.0:
        errs.append("InvalidShockwave.Negative: Shockwave.StartRadius")
        return errs
    if start_radius > MAX_AUTHORED_SHOCKWAVE_MAGNITUDE:
        errs.append("InvalidShockwave.AboveCeiling: Shockwave.StartRadius")
        return errs

    if max_radius <= 0.0:
        errs.append("InvalidShockwave.NotPositive: Shockwave.MaxRadius")
        return errs
    if max_radius > MAX_AUTHORED_SHOCKWAVE_MAGNITUDE:
        errs.append("InvalidShockwave.AboveCeiling: Shockwave.MaxRadius")
        return errs
    if max_radius <= start_radius:
        errs.append("InvalidShockwave.MaxNotAboveStart: Shockwave.MaxRadius")
        return errs

    if speed <= 0.0:
        errs.append("InvalidShockwave.NotPositive: Shockwave.Speed")
        return errs
    if speed > MAX_AUTHORED_SHOCKWAVE_MAGNITUDE:
        errs.append("InvalidShockwave.AboveCeiling: Shockwave.Speed")
        return errs

    if thickness <= 0.0:
        errs.append("InvalidShockwave.NotPositive: Shockwave.Thickness")
        return errs
    if thickness > MAX_AUTHORED_SHOCKWAVE_MAGNITUDE:
        errs.append("InvalidShockwave.AboveCeiling: Shockwave.Thickness")
        return errs

    # JumpClearance: finite and STRICTLY > 0 (AMENDED by Claude C-263)
    if jump_clearance <= 0.0:
        errs.append("InvalidShockwave.NotPositive: Shockwave.JumpClearance")
        return errs
    if jump_clearance > MAX_AUTHORED_SHOCKWAVE_MAGNITUDE:
        errs.append("InvalidShockwave.AboveCeiling: Shockwave.JumpClearance")
        return errs

    # (3) MoveId syntactic validation
    move_id = shockwave_data.get("MoveId")
    if move_id is None or move_id == "" or move_id == "None":
        errs.append("InvalidDependency.Missing: Shockwave.MoveId")
        return errs

    move_id_str = str(move_id)
    for c in move_id_str:
        if c.isspace() or ord(c) < 32:
            errs.append("InvalidDependency.Malformed: Shockwave.MoveId")
            return errs

    return errs


MAX_AUTHORED_HEAL_PUNISH_MAGNITUDE = 1.0e6


# ---------------------------------------------------------------------------
# HealPunish Policy Domain Validation (C-265 Lead Contract / DD22)
# ---------------------------------------------------------------------------
def validate_heal_punish_domain(heal_punish_data: Dict[str, Any]) -> List[str]:
    """
    Enforces authored record capability bounds for URPGBossHealPunish / FRPGHealPunishConfig
    per Claude C-265 definitive lead contract (DD22):
    Explicit qualification: Pending DD22 live verification run by Codex.
    Authored record contract, NOT native guards.
    Unresolved items: MoveId TEXT("A5") and player drinking montage soft path are hardcoded
    in RPGBossHealPunish.cpp (:22, :236) and are NOT part of the authored record.
    Ceiling: MaxAuthoredMagnitude = 1.0e6f (DD21 constant, same reasoning: radius-like and
             speed values <= 1e6 stay finite for any frame DeltaTime below 1e30 s).

    Checks run in this exact order:
    (1) ALL TEN floats finite first in header declaration order:
        - MinRange, MaxRange, Cooldown, Damage, FlightTime, MinSpeed, MaxSpeed,
          JavelinRadius, JavelinMaxRange, AimHeight.
        - Token: InvalidPunish.NotFinite: HealPunish.<FieldName>
    (2) Domains in header declaration order:
        - MinRange >= 0.0f (InvalidPunish.Negative), <= 1.0e6f (InvalidPunish.AboveCeiling)
        - MaxRange > 0.0f (InvalidPunish.NotPositive), <= 1.0e6f (InvalidPunish.AboveCeiling),
          > MinRange (InvalidPunish.MaxNotAboveMin)
        - Cooldown >= 0.0f (InvalidPunish.Negative), <= 1.0e6f (InvalidPunish.AboveCeiling)
        - Damage >= 0.0f (InvalidPunish.Negative), no ceiling
        - FlightTime >= 0.05f (InvalidPunish.BelowFlightTimeFloor, authored floor equal to editor
          metadata), <= 1.0e6f (InvalidPunish.AboveCeiling)
        - MinSpeed > 0.0f (InvalidPunish.NotPositive), <= 1.0e6f (InvalidPunish.AboveCeiling)
        - MaxSpeed > 0.0f (InvalidPunish.NotPositive), <= 1.0e6f (InvalidPunish.AboveCeiling)
        - MinSpeed <= MaxSpeed (InvalidPunish.MinSpeedAboveMax), equal is valid
        - JavelinRadius > 0.0f (InvalidPunish.NotPositive), <= 1.0e6f (InvalidPunish.AboveCeiling)
        - JavelinMaxRange > 0.0f (InvalidPunish.NotPositive), <= 1.0e6f (InvalidPunish.AboveCeiling)
    (3) SpawnSockets array:
        - At least one entry (empty array would silently use native fallback at
          RPGBossHealPunish.cpp:50 and hide default loss): InvalidDependency.Missing: HealPunish.SpawnSockets
        - Every entry not None/empty (InvalidDependency.Missing: HealPunish.SpawnSockets)
        - Every entry without whitespace or control characters (InvalidDependency.Malformed: HealPunish.SpawnSockets)
    (4) AimHeight finite (checked in step 1) and within [-1e6, 1e6] (signed):
        - InvalidPunish.BelowFloor: HealPunish.AimHeight
        - InvalidPunish.AboveCeiling: HealPunish.AimHeight
    (5) Booleans:
        - bEnabled, bRespondToHeal, bCancelJavelinsOnInterrupt accept both true and false.
    """
    errs = []
    if not isinstance(heal_punish_data, dict):
        return ["heal_punish must be a dictionary"]

    # (1) All ten floats finite first in header declaration order
    scalar_fields = [
        ("HealPunish.MinRange", heal_punish_data.get("MinRange")),
        ("HealPunish.MaxRange", heal_punish_data.get("MaxRange")),
        ("HealPunish.Cooldown", heal_punish_data.get("Cooldown")),
        ("HealPunish.Damage", heal_punish_data.get("Damage")),
        ("HealPunish.FlightTime", heal_punish_data.get("FlightTime")),
        ("HealPunish.MinSpeed", heal_punish_data.get("MinSpeed")),
        ("HealPunish.MaxSpeed", heal_punish_data.get("MaxSpeed")),
        ("HealPunish.JavelinRadius", heal_punish_data.get("JavelinRadius")),
        ("HealPunish.JavelinMaxRange", heal_punish_data.get("JavelinMaxRange")),
        ("HealPunish.AimHeight", heal_punish_data.get("AimHeight")),
    ]
    for field_name, val in scalar_fields:
        ok, _ = validate_finite_float(val, field_name)
        if not ok:
            errs.append(f"InvalidPunish.NotFinite: {field_name}")
            return errs

    min_range = float(heal_punish_data["MinRange"])
    max_range = float(heal_punish_data["MaxRange"])
    cooldown = float(heal_punish_data["Cooldown"])
    damage = float(heal_punish_data["Damage"])
    flight_time = float(heal_punish_data["FlightTime"])
    min_speed = float(heal_punish_data["MinSpeed"])
    max_speed = float(heal_punish_data["MaxSpeed"])
    javelin_radius = float(heal_punish_data["JavelinRadius"])
    javelin_max_range = float(heal_punish_data["JavelinMaxRange"])
    aim_height = float(heal_punish_data["AimHeight"])

    # (2) Domains in header declaration order
    if min_range < 0.0:
        errs.append("InvalidPunish.Negative: HealPunish.MinRange")
        return errs
    if min_range > MAX_AUTHORED_HEAL_PUNISH_MAGNITUDE:
        errs.append("InvalidPunish.AboveCeiling: HealPunish.MinRange")
        return errs

    if max_range <= 0.0:
        errs.append("InvalidPunish.NotPositive: HealPunish.MaxRange")
        return errs
    if max_range > MAX_AUTHORED_HEAL_PUNISH_MAGNITUDE:
        errs.append("InvalidPunish.AboveCeiling: HealPunish.MaxRange")
        return errs
    if max_range <= min_range:
        errs.append("InvalidPunish.MaxNotAboveMin: HealPunish.MaxRange")
        return errs

    if cooldown < 0.0:
        errs.append("InvalidPunish.Negative: HealPunish.Cooldown")
        return errs
    if cooldown > MAX_AUTHORED_HEAL_PUNISH_MAGNITUDE:
        errs.append("InvalidPunish.AboveCeiling: HealPunish.Cooldown")
        return errs

    # Damage >= 0 (no ceiling)
    if damage < 0.0:
        errs.append("InvalidPunish.Negative: HealPunish.Damage")
        return errs

    # FlightTime >= 0.05, <= 1e6
    if flight_time < 0.05:
        errs.append("InvalidPunish.BelowFlightTimeFloor: HealPunish.FlightTime")
        return errs
    if flight_time > MAX_AUTHORED_HEAL_PUNISH_MAGNITUDE:
        errs.append("InvalidPunish.AboveCeiling: HealPunish.FlightTime")
        return errs

    # MinSpeed > 0, <= 1e6
    if min_speed <= 0.0:
        errs.append("InvalidPunish.NotPositive: HealPunish.MinSpeed")
        return errs
    if min_speed > MAX_AUTHORED_HEAL_PUNISH_MAGNITUDE:
        errs.append("InvalidPunish.AboveCeiling: HealPunish.MinSpeed")
        return errs

    # MaxSpeed > 0, <= 1e6
    if max_speed <= 0.0:
        errs.append("InvalidPunish.NotPositive: HealPunish.MaxSpeed")
        return errs
    if max_speed > MAX_AUTHORED_HEAL_PUNISH_MAGNITUDE:
        errs.append("InvalidPunish.AboveCeiling: HealPunish.MaxSpeed")
        return errs

    # MinSpeed <= MaxSpeed (equal is valid)
    if min_speed > max_speed:
        errs.append("InvalidPunish.MinSpeedAboveMax: HealPunish.MinSpeed")
        return errs

    # JavelinRadius > 0, <= 1e6
    if javelin_radius <= 0.0:
        errs.append("InvalidPunish.NotPositive: HealPunish.JavelinRadius")
        return errs
    if javelin_radius > MAX_AUTHORED_HEAL_PUNISH_MAGNITUDE:
        errs.append("InvalidPunish.AboveCeiling: HealPunish.JavelinRadius")
        return errs

    # JavelinMaxRange > 0, <= 1e6
    if javelin_max_range <= 0.0:
        errs.append("InvalidPunish.NotPositive: HealPunish.JavelinMaxRange")
        return errs
    if javelin_max_range > MAX_AUTHORED_HEAL_PUNISH_MAGNITUDE:
        errs.append("InvalidPunish.AboveCeiling: HealPunish.JavelinMaxRange")
        return errs

    # (3) SpawnSockets: at least one entry, every entry not None/empty and without whitespace/control
    spawn_sockets = heal_punish_data.get("SpawnSockets")
    if not isinstance(spawn_sockets, list) or len(spawn_sockets) == 0:
        errs.append("InvalidDependency.Missing: HealPunish.SpawnSockets")
        return errs
    for sock in spawn_sockets:
        if sock is None or sock == "" or sock == "None":
            errs.append("InvalidDependency.Missing: HealPunish.SpawnSockets")
            return errs
        sock_str = str(sock)
        for c in sock_str:
            if c.isspace() or ord(c) < 32:
                errs.append("InvalidDependency.Malformed: HealPunish.SpawnSockets")
                return errs

    # (4) AimHeight finite (checked in step 1) and within [-1e6, 1e6]
    if aim_height < -MAX_AUTHORED_HEAL_PUNISH_MAGNITUDE:
        errs.append("InvalidPunish.BelowFloor: HealPunish.AimHeight")
        return errs
    if aim_height > MAX_AUTHORED_HEAL_PUNISH_MAGNITUDE:
        errs.append("InvalidPunish.AboveCeiling: HealPunish.AimHeight")
        return errs

    return errs


# ---------------------------------------------------------------------------
# Exact Native Parity Normalization & String Comparisons
# ---------------------------------------------------------------------------
def exact_native_normalize(text: str) -> str:
    """
    Exact parity with Unreal Engine 5.5 String.cpp.inl:971-974 TrimQuotesInline
    and RPGCombatRegistry::Normalize(const FString& Text):
        FString Normalize(const FString& Text) {
            return Text.TrimStartAndEnd().TrimQuotes().TrimStartAndEnd().ToLower();
        }
    In UE5.5, TrimQuotes trims at most ONE leading and ONE trailing double quote (")
    character. Repeated quotes like '""off""' leave '"off"'.
    Single quotes (') are preserved characters in native UE5 strings.
    Scope: ASCII parity. Lower() applies to standard ASCII space.
    """
    if not isinstance(text, str) or not text:
        return ""
    # 1. TrimStartAndEnd: strip whitespace from both ends
    t = text.strip()
    # 2. TrimQuotes: remove at most ONE leading and ONE trailing double quote
    start = 1 if t.startswith('"') else 0
    end = len(t) - (1 if len(t) > 1 and t.endswith('"') else 0)
    t = t[start:end]
    # 3. TrimStartAndEnd: strip whitespace again
    t = t.strip()
    # 4. ToLower: convert to lowercase (ASCII scope)
    return t.lower()


def exact_fname_equal(name1: str, name2: str) -> bool:
    """
    Exact parity with Unreal Engine FName equality (case-insensitive ASCII comparison).
    CRITICAL: In UE5, FName comparison does NOT strip whitespace.
    FName("  hello  ") != FName("hello").
    """
    if not isinstance(name1, str) or not isinstance(name2, str):
        return False
    return name1.lower() == name2.lower()


def exact_fname_in(name: str, collection: List[str]) -> bool:
    """Checks if an FName exists in a collection using case-insensitive FName equality."""
    for item in collection:
        if exact_fname_equal(name, item):
            return True
    return False


# ---------------------------------------------------------------------------
# Finite Numeric Validation (Anti-NaN, Anti-Infinity, Anti-Bool)
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Look Configuration Domain Validator (DD23 / RPGBossLookAdapters.cpp)
# ---------------------------------------------------------------------------
def validate_look_domain(look_data: Dict[str, Any]) -> List[str]:
    """
    Validates authored configuration domain for URPGBossLook / FRPGLookConfig.
    Enforces the definitive contract from Tech Lead Claude [C-269] / [C-270] and [C-275]:
    - Header authored fields: bEnabled, Body, Pieces, Sword, SwordSocket.
    - Zero numeric floats: no NotFinite checks or magnitude ceilings apply.
    - Settled DD23 points:
      (1) Returns first failure immediately, matching C++ ValidateLook.
      (2) Case-insensitive duplicate detection on Pieces paths (FSoftObjectPath equality).
      (3) No 1024 cap on SwordSocket; Pieces None/empty is valid (empty array).
      (4) SwordSocket "None" or empty is treated as Missing.
    - Validation order:
      (1) Body: required (InvalidDependency.Missing), well-formed (InvalidDependency.Malformed).
      (2) Pieces: every entry in index order: required (Missing), well-formed (Malformed),
          the message carries the index (Look.Pieces[i]); EMPTY array is VALID;
          duplicate path in the array is refused (InvalidDependency.Duplicate).
      (3) Sword: required (Missing), well-formed (Malformed).
      (4) SwordSocket: not None/empty (Missing), no whitespace/control (Malformed).
      bEnabled: bool (True or False), disabled records still validate completely.
    """
    if not isinstance(look_data, dict):
        return ["look configuration must be a dictionary"]

    # (1) Body: required then well-formed
    body_val = look_data.get("Body", look_data.get("body"))
    if body_val is None or (isinstance(body_val, str) and not body_val.strip()):
        return ["InvalidDependency.Missing: Look.Body soft path is required"]
    body_str = str(body_val)
    ok, reason = validate_soft_path_structure(body_str)
    if not ok:
        return [f"InvalidDependency.Malformed: Look.Body soft path is malformed: {reason}"]

    # (2) Pieces: list, empty valid, each entry in index order: Missing, Malformed, Duplicate
    pieces_val = look_data.get("Pieces", look_data.get("pieces"))
    if pieces_val is not None:
        seen_pieces = set()
        for idx, piece_elem in enumerate(pieces_val):
            if piece_elem is None or (isinstance(piece_elem, str) and not piece_elem.strip()):
                return [f"InvalidDependency.Missing: Look.Pieces[{idx}] soft path is required"]
            piece_str = str(piece_elem)
            ok, reason = validate_soft_path_structure(piece_str)
            if not ok:
                return [f"InvalidDependency.Malformed: Look.Pieces[{idx}] soft path is malformed: {reason}"]
            if piece_str.lower() in seen_pieces:
                return [f"InvalidDependency.Duplicate: Look.Pieces[{idx}] duplicate soft path {piece_str}"]
            seen_pieces.add(piece_str.lower())

    # (3) Sword: required then well-formed
    sword_val = look_data.get("Sword", look_data.get("sword"))
    if sword_val is None or (isinstance(sword_val, str) and not sword_val.strip()):
        return ["InvalidDependency.Missing: Look.Sword soft path is required"]
    sword_str = str(sword_val)
    ok, reason = validate_soft_path_structure(sword_str)
    if not ok:
        return [f"InvalidDependency.Malformed: Look.Sword soft path is malformed: {reason}"]

    # (4) SwordSocket: not None/empty (Missing), no whitespace or control character (Malformed)
    socket_val = look_data.get("SwordSocket", look_data.get("sword_socket", "HeavySwordSocket_R"))
    if socket_val is None or (isinstance(socket_val, str) and not socket_val.strip()) or str(socket_val).lower() == "none":
        return ["InvalidDependency.Missing: Look.SwordSocket is required"]
    socket_str = str(socket_val)
    if any(c.isspace() or ord(c) < 32 for c in socket_str):
        return ["InvalidDependency.Malformed: Look.SwordSocket contains whitespace or control"]

    return []


def validate_close_clip_swap_domain(close_data: Dict[str, Any]) -> List[str]:
    """
    Validates authored configuration domain for URPGBossCloseClipSwap / FRPGCloseClipSwapConfig.
    Enforces the definitive contract from Tech Lead Claude [C-275] & [C-276]:
    - Header authored fields: CloseAbilityClassName, AttackMontagesName, A1Montage, A3aMontage, A3bMontage.
    - Zero numeric fields: no NotFinite checks, no magnitude ceilings, no arithmetic audit.
    - No duplicate rule: three identical replacement montages are valid.
    - No _C suffix rule; no class/ability existence check offline.
    - Returns first failure token immediately matching C++ ValidateCloseClipSwap.
    - Validation order:
      (1) CloseAbilityClassName: not None/empty/case-insensitive 'none' (Missing),
          no whitespace or control characters (Malformed).
      (2) AttackMontagesName: not None/empty/case-insensitive 'none' (Missing),
          no whitespace or control characters (Malformed).
      (3) A1Montage: required (Missing) then well-formed (Malformed) with engine macros.
      (4) A3aMontage: required (Missing) then well-formed (Malformed) with engine macros.
      (5) A3bMontage: required (Missing) then well-formed (Malformed) with engine macros.
    """
    if not isinstance(close_data, dict):
        return ["close_clip_swap configuration must be a dictionary"]

    # (1) CloseAbilityClassName
    ability_val = close_data.get("CloseAbilityClassName", close_data.get("close_ability_class_name", "GA_GS_Boss_CloseAttack_C"))
    if ability_val is None or (isinstance(ability_val, str) and not ability_val.strip()) or str(ability_val).lower() == "none":
        return ["InvalidDependency.Missing: CloseClipSwap.CloseAbilityClassName is required"]
    ability_str = str(ability_val)
    if any(c.isspace() or ord(c) < 32 for c in ability_str):
        return ["InvalidDependency.Malformed: CloseClipSwap.CloseAbilityClassName contains whitespace or control"]

    # (2) AttackMontagesName
    montages_name_val = close_data.get("AttackMontagesName", close_data.get("attack_montages_name", "AttackMontages"))
    if montages_name_val is None or (isinstance(montages_name_val, str) and not montages_name_val.strip()) or str(montages_name_val).lower() == "none":
        return ["InvalidDependency.Missing: CloseClipSwap.AttackMontagesName is required"]
    montages_name_str = str(montages_name_val)
    if any(c.isspace() or ord(c) < 32 for c in montages_name_str):
        return ["InvalidDependency.Malformed: CloseClipSwap.AttackMontagesName contains whitespace or control"]

    # (3) A1Montage
    a1_val = close_data.get("A1Montage", close_data.get("a1_montage"))
    if a1_val is None or (isinstance(a1_val, str) and not a1_val.strip()):
        return ["InvalidDependency.Missing: CloseClipSwap.A1Montage is required and is not set"]
    a1_str = str(a1_val)
    ok, reason = validate_soft_path_structure(a1_str)
    if not ok:
        return [f"InvalidDependency.Malformed: CloseClipSwap.A1Montage={a1_str}, {reason}"]

    # (4) A3aMontage
    a3a_val = close_data.get("A3aMontage", close_data.get("a3a_montage"))
    if a3a_val is None or (isinstance(a3a_val, str) and not a3a_val.strip()):
        return ["InvalidDependency.Missing: CloseClipSwap.A3aMontage is required and is not set"]
    a3a_str = str(a3a_val)
    ok, reason = validate_soft_path_structure(a3a_str)
    if not ok:
        return [f"InvalidDependency.Malformed: CloseClipSwap.A3aMontage={a3a_str}, {reason}"]

    # (5) A3bMontage
    a3b_val = close_data.get("A3bMontage", close_data.get("a3b_montage"))
    if a3b_val is None or (isinstance(a3b_val, str) and not a3b_val.strip()):
        return ["InvalidDependency.Missing: CloseClipSwap.A3bMontage is required and is not set"]
    a3b_str = str(a3b_val)
    ok, reason = validate_soft_path_structure(a3b_str)
    if not ok:
        return [f"InvalidDependency.Malformed: CloseClipSwap.A3bMontage={a3b_str}, {reason}"]

    return []


def validate_death_domain(death_data: Dict[str, Any]) -> List[str]:
    """
    Validates authored configuration domain for URPGBossDeath / FRPGDeathConfig.
    Enforces the definitive contract from Tech Lead Claude [C-281], [C-284] & [C-286]:
    - Header authored fields (12):
        DeathMode, DeathClip, DeathMontage, PackDeathAbilityClassName,
        PackDeathMontagesName, PackPollSeconds, PackEndTimeMultiplier,
        HoldAtSeconds, DyingSeconds, BlendInSeconds, MaxClipRestarts, bGuardPackDeath.
    - Five scalars finite first in header order (PackPollSeconds, PackEndTimeMultiplier,
        HoldAtSeconds, DyingSeconds, BlendInSeconds).
    - Returns first failure token immediately matching C++ ValidateDeath.
    - Validation order:
        (1) Five floats finite first in header declaration order:
            PackPollSeconds, PackEndTimeMultiplier, HoldAtSeconds, DyingSeconds, BlendInSeconds.
            Token: "InvalidDeath.NotFinite: Death.<Field>"
        (2) DeathMode: must be PackMontage (0) or OwnClip (1).
            Token: "InvalidDeath.BadMode: Death.DeathMode"
        (3) Numeric ranges in header declaration order:
            - PackPollSeconds: > 0.0 ("InvalidDeath.NotPositive"), <= 1e6 ("InvalidDeath.AboveCeiling")
            - PackEndTimeMultiplier: >= 0.0 ("InvalidDeath.Negative"), <= 1e6 ("InvalidDeath.AboveCeiling") (0.0 legal OFF)
            - HoldAtSeconds: > 0.0 ("InvalidDeath.NotPositive"), <= 1e6 ("InvalidDeath.AboveCeiling")
            - DyingSeconds: > 0.0 ("InvalidDeath.NotPositive"), <= 1e6 ("InvalidDeath.AboveCeiling")
            - BlendInSeconds: >= 0.0 ("InvalidDeath.Negative"), <= 1e6 ("InvalidDeath.AboveCeiling") (0.0 legal)
            - MaxClipRestarts: >= 0 ("InvalidDeath.Negative"), <= 1000000 ("InvalidDeath.AboveCeiling") (C-284 ceiling)
        (4) FNames:
            - PackDeathAbilityClassName: not None/empty/case-insensitive 'none' ("InvalidDependency.Missing"),
                no whitespace or control characters ("InvalidDependency.Malformed")
            - PackDeathMontagesName: not None/empty/case-insensitive 'none' ("InvalidDependency.Missing"),
                no whitespace or control characters ("InvalidDependency.Malformed")
        (5) Soft object paths (required and well-formed in BOTH modes):
            - DeathClip: required ("InvalidDependency.Missing"), well-formed ("InvalidDependency.Malformed")
            - DeathMontage: required ("InvalidDependency.Missing"), well-formed ("InvalidDependency.Malformed")
    """
    errs = []
    if not isinstance(death_data, dict):
        return ["death must be a dictionary"]

    # (1) Every scalar finite first in header order
    poll_val = death_data.get("PackPollSeconds", death_data.get("pack_poll_seconds"))
    end_val = death_data.get("PackEndTimeMultiplier", death_data.get("pack_end_time_multiplier"))
    hold_val = death_data.get("HoldAtSeconds", death_data.get("hold_at_seconds"))
    dying_val = death_data.get("DyingSeconds", death_data.get("dying_seconds"))
    blend_val = death_data.get("BlendInSeconds", death_data.get("blend_in_seconds"))

    scalar_fields = [
        ("Death.PackPollSeconds", poll_val),
        ("Death.PackEndTimeMultiplier", end_val),
        ("Death.HoldAtSeconds", hold_val),
        ("Death.DyingSeconds", dying_val),
        ("Death.BlendInSeconds", blend_val),
    ]
    for field_path, val in scalar_fields:
        ok, _ = validate_finite_float(val, field_path)
        if not ok:
            errs.append(f"InvalidDeath.NotFinite: {field_path}")
            return errs

    # (2) Mode check
    death_mode = death_data.get("DeathMode", death_data.get("death_mode", "PackMontage"))
    if isinstance(death_mode, int):
        if death_mode not in (0, 1):
            errs.append("InvalidDeath.BadMode: Death.DeathMode")
            return errs
    elif isinstance(death_mode, str):
        if death_mode not in ("PackMontage", "OwnClip"):
            errs.append("InvalidDeath.BadMode: Death.DeathMode")
            return errs
    else:
        errs.append("InvalidDeath.BadMode: Death.DeathMode")
        return errs

    # (3) Domain ranges in header order
    pack_poll = float(poll_val if poll_val is not None else 0.1)
    if pack_poll <= 0.0:
        errs.append("InvalidDeath.NotPositive: Death.PackPollSeconds")
        return errs
    if pack_poll > 1.0e6:
        errs.append("InvalidDeath.AboveCeiling: Death.PackPollSeconds")
        return errs

    end_mult = float(end_val if end_val is not None else 1.0)
    if end_mult < 0.0:
        errs.append("InvalidDeath.Negative: Death.PackEndTimeMultiplier")
        return errs
    if end_mult > 1.0e6:
        errs.append("InvalidDeath.AboveCeiling: Death.PackEndTimeMultiplier")
        return errs

    hold_at = float(hold_val if hold_val is not None else 0.5)
    if hold_at <= 0.0:
        errs.append("InvalidDeath.NotPositive: Death.HoldAtSeconds")
        return errs
    if hold_at > 1.0e6:
        errs.append("InvalidDeath.AboveCeiling: Death.HoldAtSeconds")
        return errs

    dying = float(dying_val if dying_val is not None else 1.0)
    if dying <= 0.0:
        errs.append("InvalidDeath.NotPositive: Death.DyingSeconds")
        return errs
    if dying > 1.0e6:
        errs.append("InvalidDeath.AboveCeiling: Death.DyingSeconds")
        return errs

    blend_in = float(blend_val if blend_val is not None else 0.2)
    if blend_in < 0.0:
        errs.append("InvalidDeath.Negative: Death.BlendInSeconds")
        return errs
    if blend_in > 1.0e6:
        errs.append("InvalidDeath.AboveCeiling: Death.BlendInSeconds")
        return errs

    restarts_val = death_data.get("MaxClipRestarts", death_data.get("max_clip_restarts", 0))
    max_restarts = int(restarts_val if restarts_val is not None else 0)
    if max_restarts < 0:
        errs.append("InvalidDeath.Negative: Death.MaxClipRestarts")
        return errs
    if max_restarts > 1000000:
        errs.append("InvalidDeath.AboveCeiling: Death.MaxClipRestarts")
        return errs

    # (4) FNames
    ability_val = death_data.get("PackDeathAbilityClassName", death_data.get("pack_death_ability_class_name"))
    if ability_val is None or (isinstance(ability_val, str) and not ability_val.strip()) or str(ability_val).lower() == "none":
        errs.append("InvalidDependency.Missing: Death.PackDeathAbilityClassName")
        return errs
    ability_str = str(ability_val)
    if any(c.isspace() or ord(c) < 32 for c in ability_str):
        errs.append("InvalidDependency.Malformed: Death.PackDeathAbilityClassName")
        return errs

    montages_name_val = death_data.get("PackDeathMontagesName", death_data.get("pack_death_montages_name"))
    if montages_name_val is None or (isinstance(montages_name_val, str) and not montages_name_val.strip()) or str(montages_name_val).lower() == "none":
        errs.append("InvalidDependency.Missing: Death.PackDeathMontagesName")
        return errs
    montages_name_str = str(montages_name_val)
    if any(c.isspace() or ord(c) < 32 for c in montages_name_str):
        errs.append("InvalidDependency.Malformed: Death.PackDeathMontagesName")
        return errs

    # (5) Soft paths
    clip_val = death_data.get("DeathClip", death_data.get("death_clip"))
    montage_val = death_data.get("DeathMontage", death_data.get("death_montage"))
    ref_fields = [
        ("Death.DeathClip", clip_val),
        ("Death.DeathMontage", montage_val),
    ]
    for field_path, ref_val in ref_fields:
        if ref_val is None or ref_val == "":
            errs.append(f"InvalidDependency.Missing: {field_path} is required and is not set")
            return errs
        ref_str = str(ref_val.asset_path_name if hasattr(ref_val, "asset_path_name") else ref_val)
        ok, reason = validate_soft_path_structure(ref_str)
        if not ok:
            errs.append(f"InvalidDependency.Malformed: {field_path}={ref_str}, {reason}")
            return errs

    return []


def validate_finite_integer(val: Any, field_name: str, min_val: Optional[int] = None,
                            max_val: Optional[int] = None) -> Tuple[bool, str]:
    """
    Validates that a value is a strict, finite integer.
    Rejects booleans (which are subclasses of int in Python), floats, NaNs, and Infinities.
    """
    if isinstance(val, bool):
        return False, f"Field '{field_name}' must be an integer, got bool ({val})"
    if not isinstance(val, int):
        return False, f"Field '{field_name}' must be an integer, got {type(val).__name__} ({val})"
    if min_val is not None and val < min_val:
        return False, f"Field '{field_name}' value {val} is below minimum {min_val}"
    if max_val is not None and val > max_val:
        return False, f"Field '{field_name}' value {val} exceeds maximum {max_val}"
    return True, ""


def validate_finite_float(val: Any, field_name: str, min_val: Optional[float] = None,
                          max_val: Optional[float] = None) -> Tuple[bool, str]:
    """
    Validates that a value is a strict, finite float or int within IEEE 754 float32 range.
    Rejects booleans, NaNs, positive/negative infinities, and values overflowing float32.
    """
    if isinstance(val, bool):
        return False, f"Field '{field_name}' must be a numeric float, got bool ({val})"
    if not isinstance(val, (int, float)):
        return False, f"Field '{field_name}' must be numeric, got {type(val).__name__}"
    f_val = float(val)
    if math.isnan(f_val):
        return False, f"Field '{field_name}' is NaN"
    if math.isinf(f_val):
        return False, f"Field '{field_name}' is Infinity"
    if f_val > FLOAT32_MAX or f_val < FLOAT32_MIN:
        return False, f"Field '{field_name}' value {f_val} overflows 32-bit single-precision float range [{FLOAT32_MIN}, {FLOAT32_MAX}]"
    try:
        struct.pack('f', f_val)
    except OverflowError:
        return False, f"Field '{field_name}' value {f_val} overflows 32-bit single-precision float"
    if min_val is not None and f_val < min_val:
        return False, f"Field '{field_name}' value {f_val} is below minimum {min_val}"
    if max_val is not None and f_val > max_val:
        return False, f"Field '{field_name}' value {f_val} exceeds maximum {max_val}"
    return True, ""


# ---------------------------------------------------------------------------
# Strict Canonical Path & Traversal Validation
# ---------------------------------------------------------------------------
def validate_package_path(path: str, expected_root: str, allow_subdirs: bool = True) -> Tuple[bool, str]:
    """
    Validates that a package or asset path is strictly canonical and authorized:
    - Must start with expected_root
    - No path traversal ('..')
    - No double slashes ('//')
    - No backslashes ('\\')
    - No sub-object colons (':')
    - No whitespace
    - Strict alphanumeric / underscore naming pattern
    """
    if not isinstance(path, str) or not path:
        return False, "Path is empty or not a string"
    if not path.startswith(expected_root):
        return False, f"Path '{path}' does not start with authorized root '{expected_root}'"
    if ".." in path:
        return False, f"Path traversal ('..') rejected: '{path}'"
    if "//" in path:
        return False, f"Double slashes ('//') rejected: '{path}'"
    if "\\" in path:
        return False, f"Backslashes rejected: '{path}'"
    if ":" in path:
        return False, f"Sub-object colon (':') rejected: '{path}'"
    if any(ch.isspace() for ch in path):
        return False, f"Whitespace in package path rejected: '{path}'"

    # Strict pattern check
    if allow_subdirs:
        pattern = r"^/Game/OneBossFight/Data/[A-Za-z0-9_/]+$"
    else:
        escaped_root = re.escape(expected_root)
        pattern = rf"^{escaped_root}[A-Za-z0-9_]+$"

    if not re.match(pattern, path):
        return False, f"Path '{path}' contains invalid characters or structure"

    return True, ""


# ---------------------------------------------------------------------------
# Namespace Collision & Keyword Validation
# ---------------------------------------------------------------------------
def validate_build_namespace_keys(build_id: str, console_name: str, aliases: List[str],
                                  existing_names: Dict[str, str]) -> Tuple[bool, str, Dict[str, str]]:
    """
    Validates namespace keys for a build against collisions and reserved keywords.
    Mirrors C++ loop in RPGCombatCatalog.cpp:150-156 using exact_native_normalize.
    """
    if not isinstance(aliases, list):
        return False, f"Aliases for build '{build_id}' must be a list", existing_names

    keys_to_check = list(aliases) + [console_name, build_id]
    updated_names = dict(existing_names)

    for raw in keys_to_check:
        if not isinstance(raw, str):
            return False, f"Key token for build '{build_id}' must be a string; got {type(raw).__name__}", existing_names
        key = exact_native_normalize(raw)
        if not key:
            return False, f"Build '{build_id}' has empty key in Aliases/ConsoleName/BuildId", existing_names
        if key in RESERVED_KEYWORDS:
            return False, f"Build '{build_id}' uses reserved keyword '{key}'", existing_names
        if key in updated_names and not exact_fname_equal(updated_names[key], build_id):
            return False, (f"Namespace collision: Key '{key}' from build '{build_id}' "
                           f"collides with existing build '{updated_names[key]}'"), existing_names
        updated_names[key] = build_id

    return True, "", updated_names


# ---------------------------------------------------------------------------
# Pinned 3-Build Legacy Contract Validator
# ---------------------------------------------------------------------------
def validate_pinned_legacy_contract(builds: List[Dict[str, Any]],
                                    weapons: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validates that the source builds array strictly conforms to the pinned 3-build contract:
    - Exactly 3 legacy slots: 0 (Starter), 1 (Strength), 2 (Dex).
    - Exact matching ConsoleName, DisplayName, UiOrder, WeaponId.
      Slot 0: WeaponId = Starter, ExpectedStyle = SwordCombatStyle.
      Slot 1: WeaponId = Strength, ExpectedStyle = ClaymoreCombatStyle.
      Slot 2: WeaponId = Dex, ExpectedStyle = DualSwordCombatStyle (singular 'Sword').
    - Matching weapon StyleName for each legacy weapon.
    - No duplicate or out-of-range legacy slots.
    """
    errors: List[str] = []
    seen_slots: Set[int] = set()

    for b in builds:
        slot = b.get("LegacySlot", -1)
        if slot != -1:
            if slot < 0 or slot > 2:
                errors.append(f"Invalid LegacySlot {slot} on build '{b.get('BuildId')}' (must be 0, 1, 2, or -1)")
            elif slot in seen_slots:
                errors.append(f"Duplicate LegacySlot {slot} on build '{b.get('BuildId')}'")
            seen_slots.add(slot)

    if seen_slots != {0, 1, 2}:
        errors.append(f"Pinned 3-build contract requires exactly slots {{0, 1, 2}}; found {sorted(seen_slots)}")

    # Verify each pinned slot record
    for slot_idx, expected in PINNED_LEGACY_CONTRACT.items():
        matching = [b for b in builds if b.get("LegacySlot") == slot_idx]
        if len(matching) != 1:
            continue  # Already reported in seen_slots check
        b_entry = matching[0]

        if not exact_fname_equal(str(b_entry.get("BuildId", "")), expected["BuildId"]):
            errors.append(f"Slot {slot_idx} BuildId mismatch: '{b_entry.get('BuildId')}' != '{expected['BuildId']}'")
        if str(b_entry.get("ConsoleName", "")) != expected["ConsoleName"]:
            errors.append(f"Slot {slot_idx} ConsoleName mismatch: '{b_entry.get('ConsoleName')}' != '{expected['ConsoleName']}'")
        if str(b_entry.get("DisplayName", "")) != expected["DisplayName"]:
            errors.append(f"Slot {slot_idx} DisplayName mismatch: '{b_entry.get('DisplayName')}' != '{expected['DisplayName']}'")
        if b_entry.get("UiOrder") != expected["UiOrder"]:
            errors.append(f"Slot {slot_idx} UiOrder mismatch: {b_entry.get('UiOrder')} != {expected['UiOrder']}")
        if not exact_fname_equal(str(b_entry.get("WeaponId", "")), expected["WeaponId"]):
            errors.append(f"Slot {slot_idx} WeaponId mismatch: '{b_entry.get('WeaponId')}' != '{expected['WeaponId']}'")

        # Verify associated weapon style
        matching_w = [w for w in weapons if exact_fname_equal(str(w.get("WeaponId", "")), expected["WeaponId"])]
        if not matching_w:
            errors.append(f"Missing weapon for pinned slot {slot_idx} (WeaponId '{expected['WeaponId']}')")
        elif not exact_fname_equal(str(matching_w[0].get("StyleName", "")), expected["ExpectedStyle"]):
            errors.append(f"Slot {slot_idx} weapon StyleName mismatch: '{matching_w[0].get('StyleName')}' != '{expected['ExpectedStyle']}'")

    return (len(errors) == 0), errors


# ---------------------------------------------------------------------------
# Immutable Source Snapshot & Readback Verification
# ---------------------------------------------------------------------------
class SourceInventorySnapshot:
    """
    Immutable representation of all source assets and packages involved in an authoring operation.
    Performs deep recursive cloning upon initialization to prevent external mutation drift.
    """
    def __init__(self, catalog_path: str, schema_version: int,
                 weapons: List[Dict[str, Any]], builds: List[Dict[str, Any]],
                 package_dirty_states: Dict[str, bool]):
        self.catalog_path = str(catalog_path)
        self.schema_version = int(schema_version)
        self.weapons = copy.deepcopy(weapons)
        self.builds = copy.deepcopy(builds)
        self.package_dirty_states = copy.deepcopy(package_dirty_states)

    def compare_with(self, current: "SourceInventorySnapshot") -> Tuple[bool, List[str]]:
        """
        Deep comparison of two snapshots. Fails if any weapon, build, order, or package status drifted.
        """
        diffs: List[str] = []

        if self.catalog_path != current.catalog_path:
            diffs.append(f"Catalog path changed: '{self.catalog_path}' -> '{current.catalog_path}'")
        if self.schema_version != current.schema_version:
            diffs.append(f"SchemaVersion changed: {self.schema_version} -> {current.schema_version}")

        # Weapons Comparison
        if len(self.weapons) != len(current.weapons):
            diffs.append(f"Weapons count changed: {len(self.weapons)} -> {len(current.weapons)}")
        else:
            for idx, (w1, w2) in enumerate(zip(self.weapons, current.weapons)):
                if w1 != w2:
                    diffs.append(f"Weapon [{idx}] drifted: '{w1}' != '{w2}'")

        # Builds Comparison
        if len(self.builds) != len(current.builds):
            diffs.append(f"Builds count changed: {len(self.builds)} -> {len(current.builds)}")
        else:
            for idx, (b1, b2) in enumerate(zip(self.builds, current.builds)):
                if b1 != b2:
                    diffs.append(f"Build [{idx}] drifted: '{b1}' != '{b2}'")

        # Package Dirty Flags & Package Set Comparison
        all_pkgs = set(self.package_dirty_states.keys()) | set(current.package_dirty_states.keys())
        for pkg in sorted(all_pkgs):
            if pkg not in self.package_dirty_states:
                diffs.append(f"New untracked package appeared: '{pkg}'")
            elif pkg not in current.package_dirty_states:
                diffs.append(f"Tracked package missing from snapshot: '{pkg}'")
            else:
                was_dirty = self.package_dirty_states[pkg]
                now_dirty = current.package_dirty_states[pkg]
                if was_dirty != now_dirty:
                    diffs.append(f"Package dirty state changed for '{pkg}': {was_dirty} -> {now_dirty}")

        return (len(diffs) == 0), diffs


def verify_cloned_catalog_readback(original_builds: List[Dict[str, Any]],
                                   cloned_build_paths: List[str],
                                   new_build_path: str) -> Tuple[bool, List[str]]:
    """
    Verifies that the cloned catalog builds array contains all original builds in the exact same
    order, plus exactly one new reference pointing to the newly created custom build.
    """
    errors: List[str] = []
    expected_len = len(original_builds) + 1
    if len(cloned_build_paths) != expected_len:
        errors.append(f"Cloned builds length mismatch: got {len(cloned_build_paths)}, expected {expected_len}")
        return False, errors

    # Check original builds in same order
    for idx, orig in enumerate(original_builds):
        expected_path = orig.get("AssetPath", "")
        actual_path = cloned_build_paths[idx]
        if expected_path and not exact_fname_equal(expected_path, actual_path):
            errors.append(f"Build [{idx}] order/path mismatch: expected '{expected_path}', got '{actual_path}'")

    # Check last element is the new build
    last_path = cloned_build_paths[-1]
    if not exact_fname_equal(last_path, new_build_path):
        errors.append(f"Last build element mismatch: expected new build '{new_build_path}', got '{last_path}'")

    return (len(errors) == 0), errors


# ---------------------------------------------------------------------------
# Partial Operation Report Structure
# ---------------------------------------------------------------------------
class PartialOperationReport:
    """
    Structured record documenting partial creations upon error or interruption.
    Does NOT auto-delete assets and makes NO claim of transactional rollback.
    """
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.success = False
        self.created_packages: List[str] = []
        self.saved_packages: List[str] = []
        self.errors: List[str] = []

    def record_created(self, package_path: str):
        if package_path not in self.created_packages:
            self.created_packages.append(package_path)

    def record_saved(self, package_path: str):
        if package_path not in self.saved_packages:
            self.saved_packages.append(package_path)

    def record_error(self, error: str):
        self.errors.append(error)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation_name,
            "success": self.success,
            "created_packages": self.created_packages,
            "saved_packages": self.saved_packages,
            "errors": self.errors,
            "rollback_claimed": False,
            "auto_cleanup_performed": False,
            "note": "Partial packages remain on disk for inspection. No automatic deletion performed."
        }
