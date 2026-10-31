#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
validate_weapon_config.py
=========================
Pure Python offline validator for Track C3 "New Weapon" configuration.
Validates the scriptable portion of a new weapon authoring specification:
1. Operation mode: "new_weapon" (appends rows for a brand-new style) vs
   "update_existing_style" (updates numbers for an existing style).
2. Existing rows check: Prevents duplicate row shadowing on existing styles
   via [Weapon.Config.StyleAlreadyHasRows[<style>]] unless mode is "update_existing_style".
3. Identity & Catalog metadata (mirrors Source/OneBossFight/Player/RPGCombatCatalog.h:13-71).
4. Attack table tuning rows (mirrors Source/OneBossFight/Player/RPGWeaponAttackTable.h:15-53
   and Source/OneBossFight/Player/RPGWeaponAttackTable.cpp:37-77).
5. Attack kind domain rules (mirrors Source/OneBossFight/Player/RPGAttackKind.h:10-35).
6. Pack combat style existence & enemy style rejection (mirrors Content/AdvancedARPGCombat/).
7. Asset existence checking (optional asset_exists set/callable for live engine or offline disk checking).

PIE Verification Seam:
Row presence in DA_WeaponAttacks is verified via unattended PIE driver:
  -InjectRow "0.5:<Style>:<Kind>"
The F10 debug hook reads DA_WeaponAttacks by style name; 'attack_row ... found=1' proves
the row exists and returns tuned numbers without requiring pack animation equip blueprints.

Zero Unreal Engine imports; callable headlessly in pure python (-I).
"""

import math
import os
import re

# Allowed ERPGAttackKind tokens (Source/OneBossFight/Player/RPGAttackKind.h:10-35)
VALID_ATTACK_KINDS = {
    "Light",
    "Strong",
    "Charged",
    "JumpLight",
    "JumpHeavy",
    "Knockdown",
}

# Required attack kinds for full combat archetype (mirrors DA_WeaponAttacks Claymore rows)
REQUIRED_ATTACK_KINDS = {
    "Light",
    "Strong",
    "Charged",
    "JumpLight",
    "JumpHeavy",
    "Knockdown",
}

# Default offline existing rows: C++ defaults of RPGWeaponAttackTable.cpp FillDefaults
# (Claymore, Sword, DualSword, Twinblade x 6 attack kinds)
DEFAULT_EXISTING_ROWS = {
    (style, kind)
    for style in ("ClaymoreCombatStyle", "SwordCombatStyle", "DualSwordCombatStyle", "TwinbladeCombatStyle")
    for kind in ("Light", "Strong", "Charged", "JumpLight", "JumpHeavy", "Knockdown")
}

# Offline fallback dictionary of known player pack combat styles in Content/AdvancedARPGCombat/
# Note: For runtime editor utility, asset existence is verified dynamically via does_asset_exist.
KNOWN_PACK_COMBAT_STYLES = {
    "ClaymoreCombatStyle": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Claymore/ClaymoreCombatStyle.ClaymoreCombatStyle",
    "DualSwordCombatStyle": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/DualSwords/DualSwordCombatStyle.DualSwordCombatStyle",
    "PolearmCombatStyle": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Polearms/PolearmCombatStyle.PolearmCombatStyle",
    "SwordAndShieldCombatStyle": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Sword/SwordAndShieldCombatStyle.SwordAndShieldCombatStyle",
    "SwordCombatStyle": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Sword/SwordCombatStyle.SwordCombatStyle",
    "TwinbladeCombatStyle": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Twinblades/TwinbladeCombatStyle.TwinbladeCombatStyle",
    "UnarmedCombatStyle": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Unarmed/UnarmedCombatStyle.UnarmedCombatStyle",
}


def _is_finite_number(val):
    return isinstance(val, (int, float)) and not math.isnan(val) and not math.isinf(val)


def _validate_asset_path(path_str):
    """Validates soft object path: must start with /Game/ and contain Package.Asset format."""
    if not isinstance(path_str, str) or not path_str.startswith("/Game/"):
        return False
    parts = path_str.split("/")
    if len(parts) < 3:
        return False
    leaf = parts[-1]
    if "." not in leaf:
        return False
    pkg, asset = leaf.split(".", 1)
    return bool(pkg and asset)


def _check_asset_exists(path_str, asset_exists):
    """Checks whether path exists in asset_exists container (set, dict, list) or callable."""
    if asset_exists is None:
        return True
    if callable(asset_exists):
        return bool(asset_exists(path_str))
    if path_str in asset_exists:
        return True
    # Strip package.asset suffix to check bare package path
    base = path_str.split(".")[0] if "." in path_str else path_str
    if base in asset_exists:
        return True
    leaf = base.split("/")[-1]
    return f"{base}.{leaf}" in asset_exists or f"{base}.{leaf}_C" in asset_exists


def validate_weapon_config(cfg, existing_context=None, asset_exists=None, existing_rows=None):
    """
    Validates a new weapon or weapon tuning configuration dictionary.

    Args:
        cfg (dict): The weapon configuration to validate.
        existing_context (dict, optional): Context containing existing weapon_ids, 'asset_exists', or 'existing_rows'.
        asset_exists (set|callable, optional): Set of existing asset paths or callable f(path)->bool.
        existing_rows (set[tuple[str, str]], optional): Set of (style_name, kind) existing in DA_WeaponAttacks.

    Returns:
        list[str]: List of failure messages starting with failure tokens. Empty list on success.
    """
    errors = []

    if not isinstance(cfg, dict):
        return ["[Weapon.Config.Structure] Configuration root must be a JSON object"]

    # Resolve mode: "new_weapon" (default) or "update_existing_style"
    mode = cfg.get("mode", "new_weapon")
    if not isinstance(mode, str) or mode not in ("new_weapon", "update_existing_style"):
        errors.append(f"[Weapon.Config.Mode] Invalid mode '{mode}'. Must be 'new_weapon' or 'update_existing_style'")
        mode = "new_weapon"

    # Resolve asset_exists container from explicit arg or existing_context dict
    known_assets = asset_exists
    if known_assets is None and isinstance(existing_context, dict):
        known_assets = existing_context.get("asset_exists")

    # Resolve existing_rows set from explicit arg or existing_context dict
    current_existing_rows = existing_rows
    if current_existing_rows is None and isinstance(existing_context, dict):
        current_existing_rows = existing_context.get("existing_rows")
    if current_existing_rows is None:
        current_existing_rows = DEFAULT_EXISTING_ROWS

    styles_with_rows = {s for s, _ in current_existing_rows}

    # 1. Identity & Naming (RPGCombatCatalog.h:16,23)
    weapon_id = cfg.get("weapon_id")
    if not weapon_id or not isinstance(weapon_id, str) or not weapon_id.strip() or weapon_id == "None":
        errors.append("[Weapon.Config.Identity] weapon_id must be a non-empty string and not 'None'")

    style_name = cfg.get("style_name")
    if not style_name or not isinstance(style_name, str) or not style_name.strip() or style_name == "None":
        errors.append("[Weapon.Config.Identity] style_name must be a non-empty string and not 'None'")

    hud_word = cfg.get("hud_weapon_word")
    if not hud_word or not isinstance(hud_word, str) or not hud_word.strip() or len(hud_word) > 32:
        errors.append("[Weapon.Config.Identity] hud_weapon_word must be a non-empty string of length <= 32")

    # 2. Enemy / Boss Combat Style Rejection
    if style_name and ("Enemy" in style_name or "Boss" in style_name):
        errors.append(f"[Weapon.Config.EnemyCombatStyle] Player weapon cannot use enemy or boss combat style '{style_name}'")

    # 3. Mode Semantics & Style Collision Check (RPGWeaponAttackTable.cpp:80-92)
    # Find(Weapon, Kind) returns the first matching row; appending rows to an existing style shadows/breaks tuning.
    if mode == "new_weapon":
        if style_name and style_name in styles_with_rows:
            errors.append(
                f"[Weapon.Config.StyleAlreadyHasRows[{style_name}]] Style '{style_name}' already has rows in DA_WeaponAttacks; use mode 'update_existing_style' to edit existing numbers"
            )

    # 4. Pack Combat Style Validation
    style_asset_path = cfg.get("style_asset_path")
    if style_name and not ("Enemy" in style_name or "Boss" in style_name):
        if known_assets is not None:
            # Check style_asset_path exists in real assets set
            if not style_asset_path or not _check_asset_exists(style_asset_path, known_assets):
                errors.append(f"[Weapon.Config.UnknownCombatStyle] style_asset_path '{style_asset_path}' does not exist in pack combat style assets")
        else:
            # Offline default fallback check
            if style_name not in KNOWN_PACK_COMBAT_STYLES:
                errors.append(f"[Weapon.Config.UnknownCombatStyle] style_name '{style_name}' does not match any known pack combat style asset")

    # 5. Asset Paths Syntax & Physical Existence (RPGCombatCatalog.h:18-22)
    path_keys = ["style_asset_path", "item_path", "item_base_class", "actor_class", "ability_class"]
    for pk in path_keys:
        p_val = cfg.get(pk)
        if not _validate_asset_path(p_val):
            errors.append(f"[Weapon.Config.Path] {pk} must be a valid Unreal asset path starting with /Game/ and containing Package.Asset: '{p_val}'")
        elif known_assets is not None:
            if not _check_asset_exists(p_val, known_assets):
                errors.append(f"[Weapon.Config.PathMissing[{p_val}]] Asset path does not exist on disk: '{p_val}'")

    # Verify style_asset_path matches style_name
    if style_name and style_asset_path and _validate_asset_path(style_asset_path):
        leaf_pkg = style_asset_path.split("/")[-1].split(".")[0]
        if leaf_pkg != style_name:
            errors.append(f"[Weapon.Config.Path] style_asset_path package name '{leaf_pkg}' does not match style_name '{style_name}'")

    # 6. Build Definition (RPGCombatCatalog.h:34-45, RPGCombatCatalog.cpp:29-39)
    build = cfg.get("build")
    if not isinstance(build, dict):
        errors.append("[Weapon.Config.Build] 'build' block must be a JSON object")
    else:
        build_id = build.get("build_id")
        if not build_id or not isinstance(build_id, str) or not build_id.strip() or build_id == "None":
            errors.append("[Weapon.Config.Build] build.build_id must be a non-empty string and not 'None'")

        console_name = build.get("console_name")
        if not console_name or not isinstance(console_name, str) or not console_name.strip() or " " in console_name:
            errors.append("[Weapon.Config.Build] build.console_name must be a non-empty string without whitespace")

        ui_order = build.get("ui_order")
        if not isinstance(ui_order, int) or ui_order < 0:
            errors.append("[Weapon.Config.Build] build.ui_order must be an integer >= 0")

        display_name = build.get("display_name")
        if not display_name or not isinstance(display_name, str) or not display_name.strip():
            errors.append("[Weapon.Config.Build] build.display_name must be a non-empty string")

    # 7. Attack Rows Validation (RPGWeaponAttackTable.h:15-53, RPGAttackKind.h:10-35)
    attack_rows = cfg.get("attack_rows")
    if not isinstance(attack_rows, list) or len(attack_rows) == 0:
        errors.append("[Weapon.Config.AttackCoverage] attack_rows must be a non-empty array of attack row definitions")
    else:
        seen_kinds = set()
        for i, row in enumerate(attack_rows):
            if not isinstance(row, dict):
                errors.append(f"[Weapon.Config.Structure] attack_rows[{i}] must be an object")
                continue

            kind = row.get("kind")
            if not kind or not isinstance(kind, str):
                errors.append(f"[Weapon.Config.InvalidAttackKind] attack_rows[{i}] missing or invalid 'kind'")
                continue

            if kind not in VALID_ATTACK_KINDS:
                errors.append(f"[Weapon.Config.InvalidAttackKind] attack_rows[{i}] has invalid kind '{kind}'. Valid kinds: {sorted(list(VALID_ATTACK_KINDS))}")
                continue

            if kind in seen_kinds:
                errors.append(f"[Weapon.Config.AttackCoverage] duplicate attack kind '{kind}' in attack_rows")
            seen_kinds.add(kind)

            # In update_existing_style mode, every kind in the config must already exist in existing_rows
            if mode == "update_existing_style":
                if (style_name, kind) not in current_existing_rows:
                    errors.append(f"[Weapon.Config.UnknownUpdateKind] Style '{style_name}' has no existing row for kind '{kind}'")

            # Posture Damage (RPGWeaponAttackTable.h:28 ClampMin = 0.0)
            posture = row.get("posture_damage")
            if not _is_finite_number(posture) or posture < 0.0:
                errors.append(f"[Weapon.Config.AttackDomain] attack_rows[{i}] ({kind}) posture_damage must be finite >= 0.0 (got {posture})")

            # Stamina Cost (RPGWeaponAttackTable.h:32, negative = pack default 15.0, positive = custom)
            stamina = row.get("stamina_cost")
            if not _is_finite_number(stamina) or (stamina < 0.0 and stamina != -1.0) or stamina == 0.0:
                errors.append(f"[Weapon.Config.AttackDomain] attack_rows[{i}] ({kind}) stamina_cost must be -1.0 or positive > 0.0 (got {stamina})")

            # Bleed Buildup (RPGWeaponAttackTable.h:36 ClampMin = 0.0)
            bleed = row.get("bleed_buildup")
            if not _is_finite_number(bleed) or bleed < 0.0:
                errors.append(f"[Weapon.Config.AttackDomain] attack_rows[{i}] ({kind}) bleed_buildup must be finite >= 0.0 (got {bleed})")

            # Health Damage Multiplier (RPGWeaponAttackTable.h:40 ClampMin = 0.0, strictly positive)
            mult = row.get("health_damage_multiplier")
            if not _is_finite_number(mult) or mult <= 0.0:
                errors.append(f"[Weapon.Config.AttackDomain] attack_rows[{i}] ({kind}) health_damage_multiplier must be finite > 0.0 (got {mult})")

            # Hyperarmor Window (RPGWeaponAttackTable.h:44-52)
            ha_start = row.get("hyperarmor_start")
            ha_end = row.get("hyperarmor_end")
            if not _is_finite_number(ha_start) or not _is_finite_number(ha_end):
                errors.append(f"[Weapon.Config.HyperArmor] attack_rows[{i}] ({kind}) hyperarmor_start and hyperarmor_end must be finite numbers")
            else:
                if ha_start < 0.0:
                    if ha_end >= 0.0:
                        errors.append(f"[Weapon.Config.HyperArmor] attack_rows[{i}] ({kind}) hyperarmor_start is negative ({ha_start}) but hyperarmor_end is non-negative ({ha_end})")
                else:
                    if ha_end <= ha_start:
                        errors.append(f"[Weapon.Config.HyperArmor] attack_rows[{i}] ({kind}) hyperarmor window requires start < end (got start={ha_start}, end={ha_end})")

        # In new_weapon mode, check required attack kinds coverage
        if mode == "new_weapon":
            missing_required = REQUIRED_ATTACK_KINDS - seen_kinds
            if missing_required:
                errors.append(f"[Weapon.Config.AttackCoverage] attack_rows missing required archetype kinds: {sorted(list(missing_required))}")

    return errors
