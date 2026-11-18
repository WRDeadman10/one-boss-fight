"""BT-81: Read-only receipt and log marker validator for Greystone visual smoke.

Per Lead directives [X-2588], [X-2589], [X-2590], and [X-2591], this validator enforces:
1. Exact task name, run token, map path, and result/acceptance binding.
2. Mandatory four-way source hashes (runner, driver, retarget_cpp, moves_cpp) exactly
   matched against expected hashes for all accepted receipts.
3. Mandatory expected_token exactly matched for all accepted receipts.
4. Mandatory, non-empty, readable editor log text for all accepted receipts.
5. All six boolean criteria and matching observations (exact pawn, meshes, anim classes).
6. Continuous log monitoring evidence and GetMainAnimBP error counts (must be 0).
7. Real CVar readback verification ('0') on cleanup.
8. Separation of machine evidence from Owner visual art evaluation (never promotes to passed).
9. Exact parsing of RESULT outcome (no permissive startswith/prefix matching).
10. Strict key/value attribute parsing: rejects duplicate keys, empty payloads, or missing
    required attributes on POSSESSED_PAWN, SOURCE_MESH, VISIBLE_MESH, CLEANUP, etc.
11. Rejection of missing, duplicate, or conflicting log markers and mismatched JSON/log evidence.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

EXPECTED_TASK = "BT-79: Greystone opt-in PIE visual smoke driver"
EXPECTED_MAP = "/Game/OneBossFight/Maps/L_SevarogArena"
EXPECTED_PAWN_CLASS = "BP_GreystoneERPlayer_C"
EXPECTED_PAWN_PATH = "/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer.BP_GreystoneERPlayer_C"
SOURCE_MESH_NAME = "CharacterMesh0"
VISIBLE_COMPONENT_NAME = "GreystoneRuntimeVisual"

ALLOWED_SOURCE_MESH_PATHS = (
    "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin_Simple.SKM_CombatMannequin_Simple",
    "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin.SKM_CombatMannequin",
)
EXPECTED_SOURCE_ANIM_CLASS = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/ABP_CombatCharacter.ABP_CombatCharacter_C"
EXPECTED_VISIBLE_MESH = "/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone.Greystone"
EXPECTED_VISIBLE_ANIM_CLASS = "/Game/OneBossFight/Player/Greystone/ABP_Greystone_RuntimeRetarget.ABP_Greystone_RuntimeRetarget_C"

HEX_HASH_REGEX = re.compile(r"^[0-9a-fA-F]{64}$")
MARKER_PREFIX = "[GreystoneVisualSmoke] "
REQUIRED_HASH_KEYS = ("runner", "driver", "retarget_cpp", "moves_cpp")


def parse_kv_attributes(text: str, marker_name: str) -> Tuple[Dict[str, str], List[str]]:
    """Parses whitespace-delimited key=value pairs from a log marker line.

    Per [X-2591]: rejects duplicate attribute keys instead of overwriting,
    and rejects empty payloads or malformed tokens.
    """
    attrs: Dict[str, str] = {}
    attr_errors: List[str] = []
    tokens = text.strip().split()
    if not tokens:
        attr_errors.append(f"log marker '{marker_name}' payload is empty")
        return attrs, attr_errors

    for tok in tokens:
        if "=" not in tok:
            attr_errors.append(f"log marker '{marker_name}' contains token without '=': '{tok}'")
            continue
        k, v = tok.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            attr_errors.append(f"log marker '{marker_name}' contains empty attribute key in '{tok}'")
            continue
        if k in attrs:
            attr_errors.append(f"log marker '{marker_name}' contains duplicate attribute '{k}' (first='{attrs[k]}', second='{v}')")
            continue
        attrs[k] = v
    return attrs, attr_errors


def validate_greystone_smoke_receipt(
    receipt: Dict[str, Any],
    log_text: Optional[str] = None,
    expected_token: Optional[str] = None,
    expected_hashes: Optional[Dict[str, str]] = None,
) -> List[str]:
    """Validates Greystone visual smoke receipt JSON and optional log markers.

    Returns a list of refusal reasons (empty list = valid).
    Per [X-2589], [X-2590], [X-2591]:
    - accepted receipts MANDATE non-empty log_text, expected_token, and expected_hashes.
    - RESULT outcome in log markers is parsed with exact equality.
    - SOURCE_MESH and VISIBLE_MESH key/value attributes are parsed and verified against
      exact allowed paths and receipt observations.
    - Empty payloads and duplicate attributes in log markers are strictly rejected.
    """
    errors: List[str] = []

    # 1. Structural and task binding checks
    if not isinstance(receipt, dict):
        return ["receipt root must be a JSON object"]

    if receipt.get("task") != EXPECTED_TASK:
        errors.append(f"task mismatch: expected '{EXPECTED_TASK}', got '{receipt.get('task')}'")

    token = receipt.get("run_token")
    if not token or not isinstance(token, str):
        errors.append("run_token missing or not a non-empty string")

    if receipt.get("map") != EXPECTED_MAP:
        errors.append(f"map mismatch: expected '{EXPECTED_MAP}', got '{receipt.get('map')}'")

    result = receipt.get("result")
    if result not in ("PASS", "FAIL"):
        errors.append(f"result must be PASS or FAIL, got '{result}'")

    accepted = receipt.get("accepted")
    if not isinstance(accepted, bool):
        errors.append(f"accepted must be boolean, got '{accepted}'")

    if not isinstance(receipt.get("timestamp_utc"), (int, float)) or receipt.get("timestamp_utc", 0) <= 0:
        errors.append("timestamp_utc must be a positive number")

    # Per [X-2589]: expected_token and expected_hashes are mandatory for acceptance
    if accepted is True:
        if not expected_token or not isinstance(expected_token, str):
            errors.append("expected_token is mandatory for accepted receipts")
        elif token != expected_token:
            errors.append(f"run_token mismatch: expected '{expected_token}', got '{token}'")

        if not expected_hashes or not isinstance(expected_hashes, dict):
            errors.append("expected_hashes is mandatory for accepted receipts")
        else:
            for key in REQUIRED_HASH_KEYS:
                if not expected_hashes.get(key):
                    errors.append(f"expected_hashes missing mandatory key '{key}'")

        if log_text is None:
            errors.append("accepted receipt requires valid readable editor log text for cross-validation")
        elif not isinstance(log_text, str) or not log_text.strip():
            errors.append("editor log text is empty; accepted receipts require continuous log evidence")
    elif expected_token and token and token != expected_token:
        errors.append(f"run_token mismatch: expected '{expected_token}', got '{token}'")

    # 2. Four-way source hashes validation
    source_hashes = receipt.get("source_hashes")
    if not isinstance(source_hashes, dict):
        errors.append("source_hashes missing or not a JSON object")
    else:
        for key in REQUIRED_HASH_KEYS:
            val = source_hashes.get(key)
            if not val or not isinstance(val, str) or not HEX_HASH_REGEX.match(val):
                errors.append(f"source_hashes.{key} missing or not a valid 64-char hex SHA256")
            elif expected_hashes and key in expected_hashes and val != expected_hashes[key]:
                errors.append(f"source_hashes.{key} mismatch: expected '{expected_hashes[key]}', got '{val}'")

    # 3. Criteria validation
    criteria = receipt.get("criteria")
    if not isinstance(criteria, dict):
        errors.append("criteria missing or not a JSON object")
    else:
        req_criteria = (
            "exact_pawn_possessed",
            "source_mesh_hidden",
            "runtime_visual_visible",
            "log_monitored_continuous",
            "zero_get_main_anim_bp_errors",
            "cvar_restored_zero",
        )
        for crit in req_criteria:
            val = criteria.get(crit)
            if not isinstance(val, bool):
                errors.append(f"criteria.{crit} must be boolean, got '{val}'")

        all_criteria_met = all(criteria.get(c) is True for c in req_criteria)
        if accepted is True:
            if result != "PASS":
                errors.append("accepted is True but result is not PASS")
            if not all_criteria_met:
                unmet = [c for c in req_criteria if criteria.get(c) is not True]
                errors.append(f"accepted is True but criteria unmet: {unmet}")
        elif accepted is False:
            if result == "PASS" and all_criteria_met:
                errors.append("accepted is False but result is PASS and all criteria are True (contradictory)")

    # 4. Observations validation
    observations = receipt.get("observations")
    if not isinstance(observations, dict):
        errors.append("observations missing or not a JSON object")
    else:
        if observations.get("requested_cvar") != "rpg.GreystonePlayerTestPawn=1":
            errors.append(f"observations.requested_cvar must be 'rpg.GreystonePlayerTestPawn=1', got '{observations.get('requested_cvar')}'")

        # Possessed pawn
        pawn_obs = observations.get("possessed_pawn", {})
        if not isinstance(pawn_obs, dict):
            errors.append("observations.possessed_pawn must be an object")
        else:
            if pawn_obs.get("class") != EXPECTED_PAWN_CLASS:
                errors.append(f"observations.possessed_pawn.class mismatch: expected '{EXPECTED_PAWN_CLASS}', got '{pawn_obs.get('class')}'")
            if pawn_obs.get("path") != EXPECTED_PAWN_PATH:
                errors.append(f"observations.possessed_pawn.path mismatch: expected '{EXPECTED_PAWN_PATH}', got '{pawn_obs.get('path')}'")

        # Source mesh
        src_obs = observations.get("source_mesh", {})
        if not isinstance(src_obs, dict):
            errors.append("observations.source_mesh must be an object")
        else:
            if src_obs.get("component_name") != SOURCE_MESH_NAME:
                errors.append(f"observations.source_mesh.component_name mismatch: expected '{SOURCE_MESH_NAME}', got '{src_obs.get('component_name')}'")
            if src_obs.get("hidden_in_game") is not True:
                errors.append("observations.source_mesh.hidden_in_game must be True")
            if src_obs.get("mesh_asset_path") not in ALLOWED_SOURCE_MESH_PATHS:
                errors.append(f"observations.source_mesh.mesh_asset_path not in allowed: '{src_obs.get('mesh_asset_path')}'")
            if src_obs.get("anim_class_path") != EXPECTED_SOURCE_ANIM_CLASS:
                errors.append(f"observations.source_mesh.anim_class_path mismatch: expected '{EXPECTED_SOURCE_ANIM_CLASS}', got '{src_obs.get('anim_class_path')}'")
            tick_opt = str(src_obs.get("tick_option", "")).upper().replace("_", "")
            if "ALWAYSTICKPOSEANDREFRESHBONES" not in tick_opt:
                errors.append(f"observations.source_mesh.tick_option must contain AlwaysTickPoseAndRefreshBones, got '{src_obs.get('tick_option')}'")

        # Visible mesh
        vis_obs = observations.get("visible_mesh", {})
        if not isinstance(vis_obs, dict):
            errors.append("observations.visible_mesh must be an object")
        else:
            if vis_obs.get("component_name") != VISIBLE_COMPONENT_NAME:
                errors.append(f"observations.visible_mesh.component_name mismatch: expected '{VISIBLE_COMPONENT_NAME}', got '{vis_obs.get('component_name')}'")
            if vis_obs.get("hidden_in_game") is not False:
                errors.append("observations.visible_mesh.hidden_in_game must be False")
            if vis_obs.get("visible") is not True:
                errors.append("observations.visible_mesh.visible must be True")
            if vis_obs.get("mesh_asset_path") != EXPECTED_VISIBLE_MESH:
                errors.append(f"observations.visible_mesh.mesh_asset_path mismatch: expected '{EXPECTED_VISIBLE_MESH}', got '{vis_obs.get('mesh_asset_path')}'")
            if vis_obs.get("anim_class_path") != EXPECTED_VISIBLE_ANIM_CLASS:
                errors.append(f"observations.visible_mesh.anim_class_path mismatch: expected '{EXPECTED_VISIBLE_ANIM_CLASS}', got '{vis_obs.get('anim_class_path')}'")
            if vis_obs.get("parent_component") != SOURCE_MESH_NAME:
                errors.append(f"observations.visible_mesh.parent_component mismatch: expected '{SOURCE_MESH_NAME}', got '{vis_obs.get('parent_component')}'")

        # Log monitored
        log_obs = observations.get("log_monitored", {})
        if not isinstance(log_obs, dict):
            errors.append("observations.log_monitored must be an object")
        else:
            if not log_obs.get("path"):
                errors.append("observations.log_monitored.path missing")
            if not isinstance(log_obs.get("total_bytes_read"), int) or log_obs.get("total_bytes_read", 0) <= 0:
                errors.append("observations.log_monitored.total_bytes_read must be a positive integer")
            if not isinstance(log_obs.get("read_count"), int) or log_obs.get("read_count", 0) <= 0:
                errors.append("observations.log_monitored.read_count must be a positive integer")

        # GetMainAnimBP errors
        err_count = observations.get("get_main_anim_bp_errors")
        if not isinstance(err_count, int) or err_count < 0:
            errors.append(f"observations.get_main_anim_bp_errors must be a non-negative int, got '{err_count}'")
        elif accepted is True and err_count != 0:
            errors.append(f"accepted is True but get_main_anim_bp_errors is {err_count} (must be 0)")

        # Cleanup & real readback verification
        cleanup_obs = observations.get("cleanup", {})
        if not isinstance(cleanup_obs, dict):
            errors.append("observations.cleanup must be an object")
        else:
            if cleanup_obs.get("cvar_restored_to_zero") is not True:
                errors.append("observations.cleanup.cvar_restored_to_zero must be True")
            if cleanup_obs.get("cvar_readback_value") != "0":
                errors.append(f"observations.cleanup.cvar_readback_value must be '0', got '{cleanup_obs.get('cvar_readback_value')}'")

    # 5. Visual art judgment separation (owner-only, never promoted)
    art_obs = receipt.get("visual_art_judgment")
    if not isinstance(art_obs, dict):
        errors.append("visual_art_judgment must be a JSON object")
    else:
        status = art_obs.get("status")
        if status != "PENDING_OWNER_INSPECTION":
            errors.append(f"visual_art_judgment.status must be 'PENDING_OWNER_INSPECTION', got '{status}' (cannot be auto-passed)")
        if art_obs.get("scope") != "Owner visual art inspection only":
            errors.append(f"visual_art_judgment.scope must be 'Owner visual art inspection only', got '{art_obs.get('scope')}'")

    # 6. Log Marker Consistency and Anti-Spoofing
    if log_text is not None and log_text.strip():
        log_errors = validate_log_markers(log_text, receipt)
        errors.extend(log_errors)

    return errors


def validate_log_markers(log_text: str, receipt: Dict[str, Any]) -> List[str]:
    """Validates raw log text markers against receipt, enforcing uniqueness and consistency.

    Per [X-2590] and [X-2591]:
    - Distinguishes missing (None) from empty payload ("").
    - Parses key/value attributes, rejecting duplicate keys or empty attributes.
    - Compares every emitted attribute (component, hidden, visible, mesh, anim, tick, parent)
      exactly against receipt observations and declared allowed paths.
    """
    errors: List[str] = []
    lines = [line.strip() for line in log_text.splitlines() if MARKER_PREFIX in line]

    def extract_single_marker(prefix: str) -> Optional[str]:
        matching = [l for l in lines if l.startswith(MARKER_PREFIX + prefix)]
        if len(matching) == 0:
            errors.append(f"missing mandatory log marker: '{prefix}'")
            return None
        if len(matching) > 1:
            errors.append(f"duplicate log marker detected ({len(matching)} occurrences): '{prefix}'")
            return None
        raw_val = matching[0][len(MARKER_PREFIX + prefix):]
        return raw_val.strip()

    # 1. RUN_TOKEN
    token_val = extract_single_marker("RUN_TOKEN=")
    if token_val is not None:
        if not token_val:
            errors.append("log marker RUN_TOKEN= payload is empty")
        elif token_val != receipt.get("run_token"):
            errors.append(f"log marker RUN_TOKEN mismatch: log '{token_val}' != receipt '{receipt.get('run_token')}'")

    # 2. MAP
    map_val = extract_single_marker("MAP=")
    if map_val is not None:
        if not map_val:
            errors.append("log marker MAP= payload is empty")
        elif map_val != EXPECTED_MAP:
            errors.append(f"log marker MAP mismatch: expected '{EXPECTED_MAP}', got '{map_val}'")

    # 3. POSSESSED_PAWN (key/value parsed per [X-2590] and [X-2591])
    pawn_val = extract_single_marker("POSSESSED_PAWN ")
    if pawn_val is not None:
        pawn_attrs, attr_errs = parse_kv_attributes(pawn_val, "POSSESSED_PAWN")
        errors.extend(attr_errs)
        pawn_obs = receipt.get("observations", {}).get("possessed_pawn", {})
        log_pawn_cls = pawn_attrs.get("class")
        log_pawn_path = pawn_attrs.get("path")
        if not log_pawn_cls:
            errors.append("log marker POSSESSED_PAWN missing required 'class' attribute")
        elif log_pawn_cls != EXPECTED_PAWN_CLASS or log_pawn_cls != pawn_obs.get("class"):
            errors.append(f"log marker POSSESSED_PAWN class mismatch: log '{log_pawn_cls}' != expected '{EXPECTED_PAWN_CLASS}' or receipt '{pawn_obs.get('class')}'")
        if not log_pawn_path:
            errors.append("log marker POSSESSED_PAWN missing required 'path' attribute")
        elif log_pawn_path != EXPECTED_PAWN_PATH or log_pawn_path != pawn_obs.get("path"):
            errors.append(f"log marker POSSESSED_PAWN path mismatch: log '{log_pawn_path}' != expected '{EXPECTED_PAWN_PATH}' or receipt '{pawn_obs.get('path')}'")

    # 4. SOURCE_MESH (key/value parsed per [X-2590] and [X-2591])
    src_val = extract_single_marker("SOURCE_MESH ")
    if src_val is not None:
        src_attrs, attr_errs = parse_kv_attributes(src_val, "SOURCE_MESH")
        errors.extend(attr_errs)
        src_obs = receipt.get("observations", {}).get("source_mesh", {})

        # Component name
        comp = src_attrs.get("component")
        if not comp:
            errors.append("log marker SOURCE_MESH missing required 'component' attribute")
        elif comp != SOURCE_MESH_NAME or comp != src_obs.get("component_name"):
            errors.append(f"log marker SOURCE_MESH component mismatch: log '{comp}' != expected '{SOURCE_MESH_NAME}' or receipt '{src_obs.get('component_name')}'")

        # Hidden state
        hidden = src_attrs.get("hidden")
        expected_hidden = "1" if src_obs.get("hidden_in_game") is True else "0"
        if not hidden:
            errors.append("log marker SOURCE_MESH missing required 'hidden' attribute")
        elif hidden != "1" or hidden != expected_hidden:
            errors.append(f"log marker SOURCE_MESH hidden mismatch: log '{hidden}' != '1' or receipt '{expected_hidden}'")

        # Mesh asset path
        mesh = src_attrs.get("mesh")
        if not mesh:
            errors.append("log marker SOURCE_MESH missing required 'mesh' attribute")
        elif mesh not in ALLOWED_SOURCE_MESH_PATHS or mesh != src_obs.get("mesh_asset_path"):
            errors.append(f"log marker SOURCE_MESH mesh mismatch: log '{mesh}' != allowed or receipt '{src_obs.get('mesh_asset_path')}'")

        # Anim class path
        anim = src_attrs.get("anim")
        if not anim:
            errors.append("log marker SOURCE_MESH missing required 'anim' attribute")
        elif anim != EXPECTED_SOURCE_ANIM_CLASS or anim != src_obs.get("anim_class_path"):
            errors.append(f"log marker SOURCE_MESH anim mismatch: log '{anim}' != expected '{EXPECTED_SOURCE_ANIM_CLASS}' or receipt '{src_obs.get('anim_class_path')}'")

        # Tick option
        tick = src_attrs.get("tick")
        if not tick:
            errors.append("log marker SOURCE_MESH missing required 'tick' attribute")
        elif "ALWAYSTICKPOSEANDREFRESHBONES" not in tick.upper().replace("_", "") or tick != src_obs.get("tick_option"):
            errors.append(f"log marker SOURCE_MESH tick mismatch: log '{tick}' != receipt '{src_obs.get('tick_option')}'")

    # 5. VISIBLE_MESH (key/value parsed per [X-2590] and [X-2591])
    vis_val = extract_single_marker("VISIBLE_MESH ")
    if vis_val is not None:
        vis_attrs, attr_errs = parse_kv_attributes(vis_val, "VISIBLE_MESH")
        errors.extend(attr_errs)
        vis_obs = receipt.get("observations", {}).get("visible_mesh", {})

        # Component name
        comp = vis_attrs.get("component")
        if not comp:
            errors.append("log marker VISIBLE_MESH missing required 'component' attribute")
        elif comp != VISIBLE_COMPONENT_NAME or comp != vis_obs.get("component_name"):
            errors.append(f"log marker VISIBLE_MESH component mismatch: log '{comp}' != expected '{VISIBLE_COMPONENT_NAME}' or receipt '{vis_obs.get('component_name')}'")

        # Visible state
        visible = vis_attrs.get("visible")
        expected_vis = "1" if vis_obs.get("visible") is True else "0"
        if not visible:
            errors.append("log marker VISIBLE_MESH missing required 'visible' attribute")
        elif visible != "1" or visible != expected_vis:
            errors.append(f"log marker VISIBLE_MESH visible mismatch: log '{visible}' != '1' or receipt '{expected_vis}'")

        # Mesh asset path
        mesh = vis_attrs.get("mesh")
        if not mesh:
            errors.append("log marker VISIBLE_MESH missing required 'mesh' attribute")
        elif mesh != EXPECTED_VISIBLE_MESH or mesh != vis_obs.get("mesh_asset_path"):
            errors.append(f"log marker VISIBLE_MESH mesh mismatch: log '{mesh}' != expected '{EXPECTED_VISIBLE_MESH}' or receipt '{vis_obs.get('mesh_asset_path')}'")

        # Anim class path
        anim = vis_attrs.get("anim")
        if not anim:
            errors.append("log marker VISIBLE_MESH missing required 'anim' attribute")
        elif anim != EXPECTED_VISIBLE_ANIM_CLASS or anim != vis_obs.get("anim_class_path"):
            errors.append(f"log marker VISIBLE_MESH anim mismatch: log '{anim}' != expected '{EXPECTED_VISIBLE_ANIM_CLASS}' or receipt '{vis_obs.get('anim_class_path')}'")

        # Parent component
        parent = vis_attrs.get("parent")
        if not parent:
            errors.append("log marker VISIBLE_MESH missing required 'parent' attribute")
        elif parent != SOURCE_MESH_NAME or parent != vis_obs.get("parent_component"):
            errors.append(f"log marker VISIBLE_MESH parent mismatch: log '{parent}' != expected '{SOURCE_MESH_NAME}' or receipt '{vis_obs.get('parent_component')}'")

    # 6. LOG_MONITORED
    mon_val = extract_single_marker("LOG_MONITORED ")
    if mon_val is not None:
        mon_attrs, attr_errs = parse_kv_attributes(mon_val, "LOG_MONITORED")
        errors.extend(attr_errs)
        if mon_attrs.get("continuous") != "1":
            errors.append(f"log marker LOG_MONITORED indicates continuous!=1: '{mon_val}'")

    # 7. GET_MAIN_ANIM_BP_ERRORS count=
    err_val = extract_single_marker("GET_MAIN_ANIM_BP_ERRORS count=")
    if err_val is not None:
        if not err_val:
            errors.append("log marker GET_MAIN_ANIM_BP_ERRORS count= payload is empty")
        else:
            try:
                count = int(err_val)
                obs_count = receipt.get("observations", {}).get("get_main_anim_bp_errors")
                if count != obs_count:
                    errors.append(f"log marker error count ({count}) != receipt error count ({obs_count})")
            except ValueError:
                errors.append(f"invalid error count in log marker: '{err_val}'")

    # 8. CLEANUP
    clean_val = extract_single_marker("CLEANUP ")
    if clean_val is not None:
        clean_attrs, attr_errs = parse_kv_attributes(clean_val, "CLEANUP")
        errors.extend(attr_errs)
        if clean_attrs.get("cvar_restored") != "1" or clean_attrs.get("readback_value") != "0":
            errors.append(f"log marker CLEANUP indicates incomplete restoration: '{clean_val}'")

    # 9. VISUAL_ART_JUDGMENT
    art_val = extract_single_marker("VISUAL_ART_JUDGMENT ")
    if art_val is not None:
        art_attrs, attr_errs = parse_kv_attributes(art_val, "VISUAL_ART_JUDGMENT")
        errors.extend(attr_errs)
        if art_attrs.get("status") != "PENDING_OWNER_INSPECTION" or art_attrs.get("owner_only") != "1":
            errors.append(f"log marker VISUAL_ART_JUDGMENT mismatch: '{art_val}'")

    # 10. RESULT (exact parsing per [X-2589])
    res_val = extract_single_marker("RESULT=")
    if res_val is not None:
        if not res_val:
            errors.append("log marker RESULT= payload is empty")
        else:
            match = re.match(r"^(PASS|FAIL)(?:\s+reason=(.*))?$", res_val.strip())
            if not match:
                errors.append(f"log marker RESULT has invalid format: '{res_val}'")
            else:
                log_outcome = match.group(1)
                receipt_res = receipt.get("result", "")
                if log_outcome != receipt_res:
                    errors.append(f"log marker RESULT outcome mismatch: log '{log_outcome}' != receipt '{receipt_res}'")

    return errors


def generate_negative_test_cases() -> Dict[str, Dict[str, Any]]:
    """Returns a dictionary of named invalid receipts for offline test verification."""
    valid_base = {
        "task": EXPECTED_TASK,
        "run_token": "a1b2c3d4e5f60718",
        "result": "PASS",
        "accepted": True,
        "map": EXPECTED_MAP,
        "source_hashes": {
            "runner": "11" * 32,
            "driver": "22" * 32,
            "retarget_cpp": "33" * 32,
            "moves_cpp": "44" * 32,
        },
        "criteria": {
            "exact_pawn_possessed": True,
            "source_mesh_hidden": True,
            "runtime_visual_visible": True,
            "log_monitored_continuous": True,
            "zero_get_main_anim_bp_errors": True,
            "cvar_restored_zero": True,
        },
        "observations": {
            "requested_cvar": "rpg.GreystonePlayerTestPawn=1",
            "possessed_pawn": {"class": EXPECTED_PAWN_CLASS, "path": EXPECTED_PAWN_PATH},
            "source_mesh": {
                "component_name": SOURCE_MESH_NAME,
                "hidden_in_game": True,
                "mesh_asset_path": ALLOWED_SOURCE_MESH_PATHS[0],
                "anim_class_path": EXPECTED_SOURCE_ANIM_CLASS,
                "tick_option": "AlwaysTickPoseAndRefreshBones",
            },
            "visible_mesh": {
                "component_name": VISIBLE_COMPONENT_NAME,
                "hidden_in_game": False,
                "visible": True,
                "mesh_asset_path": EXPECTED_VISIBLE_MESH,
                "anim_class_path": EXPECTED_VISIBLE_ANIM_CLASS,
                "parent_component": SOURCE_MESH_NAME,
            },
            "log_monitored": {
                "path": "Saved/Logs/editor.log",
                "total_bytes_read": 1024,
                "read_count": 5,
            },
            "get_main_anim_bp_errors": 0,
            "cleanup": {
                "cvar_restored_to_zero": True,
                "cvar_readback_value": "0",
            },
        },
        "visual_art_judgment": {
            "status": "PENDING_OWNER_INSPECTION",
            "scope": "Owner visual art inspection only",
            "note": "Machine-readable smoke only.",
        },
        "failure": "",
        "timestamp_utc": 1700000000.0,
    }

    cases: Dict[str, Dict[str, Any]] = {}

    # Case 1: Bad token
    c1 = json.loads(json.dumps(valid_base))
    c1["run_token"] = "WRONG_TOKEN"
    cases["token_mismatch"] = c1

    # Case 2: Bad map
    c2 = json.loads(json.dumps(valid_base))
    c2["map"] = "/Game/Maps/WrongMap"
    cases["map_mismatch"] = c2

    # Case 3: Source hash missing or invalid
    c3 = json.loads(json.dumps(valid_base))
    c3["source_hashes"]["moves_cpp"] = "not_a_valid_hash"
    cases["invalid_source_hash"] = c3

    # Case 4: Criteria failure (unmet criterion with accepted=True)
    c4 = json.loads(json.dumps(valid_base))
    c4["criteria"]["cvar_restored_zero"] = False
    cases["unmet_criteria_with_accepted_true"] = c4

    # Case 5: Unverified CVar readback
    c5 = json.loads(json.dumps(valid_base))
    c5["observations"]["cleanup"]["cvar_readback_value"] = "1"
    cases["cvar_readback_nonzero"] = c5

    # Case 6: Attempted auto-promotion of visual art judgment
    c6 = json.loads(json.dumps(valid_base))
    c6["visual_art_judgment"]["status"] = "PASS"
    cases["visual_art_auto_promoted"] = c6

    # Case 7: Accepted receipt without log text
    cases["accepted_missing_log"] = json.loads(json.dumps(valid_base))

    # Case 8: Accepted receipt without expected token
    cases["accepted_missing_expected_token"] = json.loads(json.dumps(valid_base))

    # Case 9: Accepted receipt without expected hashes
    cases["accepted_missing_expected_hashes"] = json.loads(json.dumps(valid_base))

    return cases


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Greystone visual smoke receipt and log markers.")
    parser.add_argument("receipt", help="Path to receipt.json")
    parser.add_argument("log", nargs="?", default=None, help="Path to editor.log")
    parser.add_argument("--token", dest="token", default=None, help="Expected run token")
    parser.add_argument("--hashes", dest="hashes", default=None, help="Expected hashes JSON file or string")
    args = parser.parse_args()

    receipt_file = Path(args.receipt)
    if not receipt_file.is_file():
        print(f"ERROR: receipt file not found: {receipt_file}")
        return 1

    try:
        receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: failed to parse receipt JSON: {exc}")
        return 1

    # Per [X-2589]: fail if CLI log arg is supplied but absent/unreadable
    log_text: Optional[str] = None
    if args.log:
        log_path = Path(args.log)
        if not log_path.is_file():
            print(f"ERROR: editor log file not found or unreadable: {log_path}")
            return 1
        try:
            log_text = log_path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            print(f"ERROR: failed to read editor log file: {exc}")
            return 1

    expected_hashes: Optional[Dict[str, str]] = None
    if args.hashes:
        hashes_path = Path(args.hashes)
        if hashes_path.is_file():
            try:
                expected_hashes = json.loads(hashes_path.read_text(encoding="utf-8"))
            except Exception as exc:
                print(f"ERROR: failed to parse expected hashes JSON file: {exc}")
                return 1
        else:
            try:
                expected_hashes = json.loads(args.hashes)
            except Exception as exc:
                print(f"ERROR: failed to parse expected hashes JSON string: {exc}")
                return 1

    errors = validate_greystone_smoke_receipt(
        receipt,
        log_text=log_text,
        expected_token=args.token,
        expected_hashes=expected_hashes,
    )

    if errors:
        print("FAIL: Greystone visual smoke receipt validation failed:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"PASS: Greystone visual smoke receipt valid (token={receipt.get('run_token')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
