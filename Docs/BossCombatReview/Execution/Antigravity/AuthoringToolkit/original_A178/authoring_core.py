#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
authoring_core.py
=================
Pure Python shared validation core and invariant enforcement library for OneBossFight
authoring tools (AG-CONTENT04).

Design Invariants:
    1. Zero Unreal Dependencies: This module uses standard library only and contains no
       import of the 'unreal' module or Unreal Engine C++ APIs at module level.
    2. Exact Native Normalization: Matches Unreal Engine 5.5 String.cpp.inl TrimQuotesInline
       and RPGCombatRegistry::Normalize (FString::TrimQuotes trims double quotes only;
       single quotes are preserved).
    3. Strict FName Semantics: Case-insensitive ASCII comparison without whitespace stripping.
    4. Canonical Paths: Rejects path traversal, double slashes, backslashes, colons, and
       non-canonical segments.
    5. Immutable Snapshot Comparison: Deep value-by-value comparison of source catalog
       inventories, property dictionaries, and package dirty flags.
    6. Fail-Closed Error Reporting: All domain and path errors halt processing with explicit
       diagnostics. Partial operations report exact created packages without rollback claims.
"""

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

# Pinned 3-Build Legacy Compatibility Contract (Source: RPGCombatCatalog.cpp:158-172)
PINNED_LEGACY_CONTRACT = {
    0: {
        "BuildId": "Starter",
        "ConsoleName": "Starter",
        "DisplayName": "Starter",
        "UiOrder": 0,
        "WeaponId": "Sword",
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
        "ExpectedStyle": "DualSwordsCombatStyle"
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
# Exact Native Parity Normalization & String Comparisons
# ---------------------------------------------------------------------------
def exact_native_normalize(text: str) -> str:
    """
    Exact parity with Unreal Engine 5.5 String.cpp.inl:971-974 TrimQuotesInline
    and RPGCombatRegistry::Normalize(const FString& Text):
        FString Normalize(const FString& Text) {
            return Text.TrimStartAndEnd().TrimQuotes().TrimStartAndEnd().ToLower();
        }
    In UE5, TrimQuotes trims double quotes (") from both ends independently (not paired!).
    Single quotes (') are preserved characters in native UE5 strings.
    """
    if not isinstance(text, str) or not text:
        return ""
    # 1. TrimStartAndEnd: strip whitespace from both ends
    t = text.strip()
    # 2. TrimQuotes: strip double quotes (") from both ends independently
    t = t.strip('"')
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
        # Asset directly inside root
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
    Used for fail-closed comparison before and after mutation.
    """
    def __init__(self, catalog_path: str, schema_version: int,
                 weapons: List[Dict[str, Any]], builds: List[Dict[str, Any]],
                 package_dirty_states: Dict[str, bool]):
        self.catalog_path = str(catalog_path)
        self.schema_version = int(schema_version)
        self.weapons = [dict(w) for w in weapons]
        self.builds = [dict(b) for b in builds]
        self.package_dirty_states = dict(package_dirty_states)

    def compare_with(self, current: "SourceInventorySnapshot") -> Tuple[bool, List[str]]:
        """
        Deep comparison of two snapshots. Fails if any weapon, build, order, or dirty state changed.
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
                for k in w1.keys() | w2.keys():
                    if w1.get(k) != w2.get(k):
                        diffs.append(f"Weapon [{idx}] field '{k}' drifted: '{w1.get(k)}' != '{w2.get(k)}'")

        # Builds Comparison
        if len(self.builds) != len(current.builds):
            diffs.append(f"Builds count changed: {len(self.builds)} -> {len(current.builds)}")
        else:
            for idx, (b1, b2) in enumerate(zip(self.builds, current.builds)):
                for k in b1.keys() | b2.keys():
                    if b1.get(k) != b2.get(k):
                        diffs.append(f"Build [{idx}] field '{k}' drifted: '{b1.get(k)}' != '{b2.get(k)}'")

        # Package Dirty Flags Comparison
        for pkg, was_dirty in self.package_dirty_states.items():
            now_dirty = current.package_dirty_states.get(pkg, False)
            if not was_dirty and now_dirty:
                diffs.append(f"Source package became dirty during operation: '{pkg}'")

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
