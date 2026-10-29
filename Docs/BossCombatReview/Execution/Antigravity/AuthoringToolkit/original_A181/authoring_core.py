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
"""

import copy
import math
import re
from typing import Dict, List, Tuple, Any, Optional, Set

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
    Mirrors Unreal Engine 5.5 PyGenUtil::PythonizePropertyName:
    1. If boolean and starts with 'b' + uppercase letter, strip the 'b'.
    2. Convert CamelCase/PascalCase to snake_case lowercase.
    """
    if is_bool and len(name) > 1 and name[0] == 'b' and name[1].isupper():
        name = name[1:]
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


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
    "phases": (NATIVE_PHASE_CONFIG_FIELDS, PHASE_CONFIG_NATIVE_TO_PY, PHASE_CONFIG_PY_TO_NATIVE),
    "fields": (NATIVE_PARITY_FIELD_FIELDS, PARITY_FIELD_NATIVE_TO_PY, PARITY_FIELD_PY_TO_NATIVE),
}


def map_native_dict_to_python_keys(native_dict: Dict[str, Any], fields_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translates native C++ CamelCase JSON property names to generated UE5.5 Python snake_case
    property names, stripping boolean 'b' prefixes per PyGenUtil::PythonizePropertyName.
    Converts list cooldowns into explicit 2-float elements.
    """
    py_dict = {}
    for native_k, val in native_dict.items():
        is_bool = (fields_spec.get(native_k) is bool)
        py_k = pythonize_property_name(native_k, is_bool=is_bool)
        if fields_spec.get(native_k) is list and native_k == "FireballCooldown" and isinstance(val, (list, tuple)):
            py_dict[py_k] = [float(x) for x in val]
        else:
            py_dict[py_k] = copy.deepcopy(val)
    return py_dict


def extract_canonical_primitives(struct_obj: Any, fields_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reads back actual scalar, vector, and soft path properties from an Unreal Python struct
    wrapper or dictionary, converting them to canonical JSON primitives keyed by the native
    C++ CamelCase property names.
    """
    canonical = {}
    for native_k, expected_type in fields_spec.items():
        is_bool = (expected_type is bool)
        py_k = pythonize_property_name(native_k, is_bool=is_bool)

        raw_val = None
        if isinstance(struct_obj, dict):
            if py_k in struct_obj:
                raw_val = struct_obj[py_k]
            elif native_k in struct_obj:
                raw_val = struct_obj[native_k]
            else:
                raise KeyError(f"Missing property '{py_k}' in struct dictionary")
        elif hasattr(struct_obj, py_k):
            raw_val = getattr(struct_obj, py_k)
        elif hasattr(struct_obj, native_k):
            raw_val = getattr(struct_obj, native_k)
        else:
            raise AttributeError(f"Struct wrapper missing attribute '{py_k}'")

        if expected_type is float:
            canonical[native_k] = float(raw_val)
        elif expected_type is int:
            canonical[native_k] = int(raw_val)
        elif expected_type is bool:
            canonical[native_k] = bool(raw_val)
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
            else:
                canonical[native_k] = list(raw_val)
    return canonical


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
    Validates that a value is a strict, finite float or int.
    Rejects booleans, NaNs, positive/negative infinities.
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
