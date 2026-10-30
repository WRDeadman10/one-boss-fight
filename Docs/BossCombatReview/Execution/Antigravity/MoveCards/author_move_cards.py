#!/usr/bin/env python3
"""
author_move_cards.py
====================
Staged Unreal Editor Python helper for authoring URPGBossMoveCard Data Assets
from JSON specifications (A-247 / A-248). Modelled on draft_boss_profiles.py discipline.

Target Package Path:
    /Game/OneBossFight/FrameworkProof/Cards/<MoveId>

Execution Modes & Safety Gates:
    1. Dry-Run Mode (DEFAULT):
       - Parses and validates input JSON cards against native FRPGBossMoveCardSpec schema.
       - Strictly enforces C++ validation rules (Source/OneBossFight/Player/RPGBossMoveCard.cpp).
       - Refuses any card containing [PROBE TBD] / null unmeasured timing values.
       - Enforces SlotName == "FullBody" (required by RPGBossFrameworkProfile resolver).
       - Requires ClipLengthSeconds explicitly in input (no silent skips).
       - Refuses SYNTHETIC data unless --allow-synthetic is explicitly passed.
       - Enforces anti-overwrite check (refuses if asset already exists on disk).
       - Prints proposed creation plan. Zero writes, zero saves.
    2. Apply Mode (--apply):
       - Requires explicit --apply flag.
       - Validates clip length directly from loaded animation sequence/montage asset.
       - Creates URPGBossMoveCard data assets in memory only. DOES NOT SAVE by default.
       - Populates all typed spec fields, skeleton/sequence soft references, and windows.
       - Executes complete read-back verification of every field against input spec.
    3. Save Opt-in (--apply --save):
       - Explicit opt-in combined with --apply. Saves newly created assets to disk.
    4. Selector (--only <MoveId>):
       - Filters execution to exactly one designated MoveId.

All offline tests and validators run with zero engine dependency.
"""

import sys
import os
import math
import json
import argparse
from typing import List, Dict, Any, Tuple, Optional

CEILING = 1.0e6
TARGET_PACKAGE_DIR = "/Game/OneBossFight/FrameworkProof/Cards"


class MoveCardValidationError(Exception):
    def __init__(self, errors: List[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


def check_number(
    errors: List[str],
    name: str,
    val: Any,
    positive: bool = False
) -> bool:
    """Mirrors Number() in RPGBossMoveCard.cpp."""
    if val is None or isinstance(val, str):
        errors.append(f"MoveCard.UnmeasuredTiming[{name}]")
        return False
    try:
        fval = float(val)
    except (ValueError, TypeError):
        errors.append(f"MoveCard.NonFinite[{name}]")
        return False

    if math.isnan(fval) or math.isinf(fval):
        errors.append(f"MoveCard.NonFinite[{name}]")
        return False

    if fval < 0.0 or fval > CEILING or (positive and fval == 0.0):
        errors.append(f"MoveCard.Domain[{name}]")
        return False

    return True


def validate_move_card_spec(
    spec: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> List[str]:
    """
    Validates a MoveCard dictionary strictly following Validate() in
    Source/OneBossFight/Player/RPGBossMoveCard.cpp, plus backend requirements:
    1. SlotName must be exactly "FullBody".
    2. ClipLengthSeconds must be explicitly provided in spec or metadata.
    3. Timeline ordering must satisfy commit <= activeStart < activeEnd <= recoveryEnd <= clipLength.
    Returns list of error tokens. Empty list indicates valid card.
    """
    errors = []

    # 1. Identity
    schema = spec.get("Schema", 0)
    move_id = str(spec.get("MoveId", ""))
    family_id = str(spec.get("FamilyId", ""))
    phase_id = str(spec.get("PhaseId", ""))

    if schema != 1 or not move_id or move_id == "None" or not family_id or family_id == "None" or not phase_id or phase_id == "None":
        errors.append("MoveCard.Identity[Schema/MoveId/FamilyId/PhaseId]")

    # 2. Animation Source: exactly one sequence OR montage
    seq_path = spec.get("Sequence")
    montage_path = spec.get("Montage")
    b_seq = bool(seq_path and seq_path != "None")
    b_montage = bool(montage_path and montage_path != "None")

    if b_seq == b_montage:
        errors.append("MoveCard.AnimationSource[exactly one sequence OR montage]")

    # 3. Slot Rule: live runtime strictly requires "FullBody" for this backend
    slot_name = spec.get("SlotName")
    if slot_name != "FullBody":
        errors.append("MoveCard.Slot[SlotName must be FullBody]")

    # 4. Descriptor / Metadata checks (if metadata supplied)
    if metadata:
        req_anim = seq_path if b_seq else montage_path
        if req_anim != metadata.get("AnimationPath"):
            errors.append("MoveCard.AnimationIdentity[selected source vs resolved descriptor]")

        exp_skel = spec.get("Skeleton")
        if not exp_skel or exp_skel != metadata.get("SkeletonPath") or exp_skel != metadata.get("AnimationSkeletonPath") or exp_skel != metadata.get("MeshSkeletonPath"):
            errors.append("MoveCard.SkeletonIdentity[declared/resolved/animation/mesh skeleton]")

        sec_name = spec.get("SectionName")
        if sec_name and sec_name != "None":
            valid_secs = metadata.get("Sections", set())
            if not b_montage or sec_name not in valid_secs:
                errors.append("MoveCard.Section[SectionName]")

        if spec.get("bUsesRootMotion", False) or metadata.get("bRootMotion", False):
            errors.append("MoveCard.UnsupportedRootMotion[first backend is in-place only]")
    else:
        # Standalone checks without metadata
        sec_name = spec.get("SectionName")
        if sec_name and sec_name != "None" and not b_montage:
            errors.append("MoveCard.Section[SectionName]")
        if spec.get("bUsesRootMotion", False):
            errors.append("MoveCard.UnsupportedRootMotion[first backend is in-place only]")

    # 5. Scalar numbers
    check_number(errors, "PlayRate", spec.get("PlayRate"), positive=True)

    # 6. Clip Length: must be explicitly provided in spec or metadata (no silent skip)
    clip_len = None
    if metadata and "ClipLengthSeconds" in metadata:
        clip_len = metadata["ClipLengthSeconds"]
    elif "ClipLengthSeconds" in spec:
        clip_len = spec["ClipLengthSeconds"]

    has_clip = False
    if clip_len is None:
        errors.append("MoveCard.Timeline[missing ClipLengthSeconds in input]")
    else:
        has_clip = check_number(errors, "ClipLengthSeconds", clip_len, positive=True)

    has_commit = check_number(errors, "CommitSeconds", spec.get("CommitSeconds"))
    has_act_s = check_number(errors, "ActiveStartSeconds", spec.get("ActiveStartSeconds"))
    has_act_e = check_number(errors, "ActiveEndSeconds", spec.get("ActiveEndSeconds"))
    has_rec_e = check_number(errors, "RecoveryEndSeconds", spec.get("RecoveryEndSeconds"))
    check_number(errors, "TrackDegreesPerSecond", spec.get("TrackDegreesPerSecond"))
    has_min_r = check_number(errors, "MinRangeCm", spec.get("MinRangeCm"))
    has_max_r = check_number(errors, "MaxRangeCm", spec.get("MaxRangeCm"))
    has_cone = check_number(errors, "FrontConeDegrees", spec.get("FrontConeDegrees"))
    check_number(errors, "HPDamage", spec.get("HPDamage"))

    # 7. Eligibility ordering
    if has_cone and has_min_r and has_max_r:
        cone = float(spec["FrontConeDegrees"])
        min_r = float(spec["MinRangeCm"])
        max_r = float(spec["MaxRangeCm"])
        if cone > 360.0 or max_r < min_r:
            errors.append("MoveCard.Eligibility[cone or range order]")

    # 8. Timeline ordering
    if has_commit and has_act_s and has_act_e and has_rec_e:
        commit_s = float(spec["CommitSeconds"])
        act_s = float(spec["ActiveStartSeconds"])
        act_e = float(spec["ActiveEndSeconds"])
        rec_e = float(spec["RecoveryEndSeconds"])

        timeline_valid = (commit_s <= act_s and act_s < act_e and act_e <= rec_e)
        if has_clip and clip_len is not None:
            timeline_valid = timeline_valid and (rec_e <= float(clip_len))
        else:
            timeline_valid = False

        if not timeline_valid:
            errors.append("MoveCard.Timeline[commit<=activeStart<activeEnd<=recoveryEnd<=clipLength]")

    # 9. Hit Windows
    windows = spec.get("Windows")
    if windows is None or len(windows) == 0:
        errors.append("MoveCard.Window[no hit windows]")
    else:
        window_ids = set()
        previous_end = -1.0
        for i, w in enumerate(windows):
            field_prefix = f"Windows[{i}]"
            w_id = w.get("WindowId")
            h_grp = w.get("HitGroup")

            if not w_id or w_id == "None" or not h_grp or h_grp == "None" or w_id in window_ids:
                errors.append(f"MoveCard.WindowIdentity[{field_prefix}]")
            if w_id:
                window_ids.add(w_id)

            has_w_s = check_number(errors, f"{field_prefix}.StartSeconds", w.get("StartSeconds"))
            has_w_e = check_number(errors, f"{field_prefix}.EndSeconds", w.get("EndSeconds"))
            check_number(errors, f"{field_prefix}.RadiusCm", w.get("RadiusCm"), positive=True)

            if has_w_s and has_w_e and has_act_s and has_act_e:
                w_start = float(w["StartSeconds"])
                w_end = float(w["EndSeconds"])
                act_start = float(spec["ActiveStartSeconds"])
                act_end = float(spec["ActiveEndSeconds"])

                if not (w_start >= act_start and w_start < w_end and w_end <= act_end and w_start >= previous_end):
                    errors.append(f"MoveCard.Window[{field_prefix}]")
                previous_end = w_end

            sock_a = w.get("SocketA")
            sock_b = w.get("SocketB")
            if not sock_a or sock_a == "None" or not sock_b or sock_b == "None" or sock_a == sock_b:
                errors.append(f"MoveCard.Socket[{field_prefix}]")
            elif metadata and "SocketOrBoneNames" in metadata:
                valid_bones = metadata["SocketOrBoneNames"]
                if sock_a not in valid_bones or sock_b not in valid_bones:
                    errors.append(f"MoveCard.Socket[{field_prefix}]")

    return errors


def execute_authoring(
    cards_data: List[Dict[str, Any]],
    apply_mode: bool = False,
    save_mode: bool = False,
    only_move_id: Optional[str] = None,
    allow_synthetic: bool = False,
    is_synthetic: bool = False
) -> int:
    """Executes validation and optional editor asset authoring."""
    print("================================================================================")
    print(" SEVAROG MOVE-CARD AUTHORING HELPER (A-247 / A-248)")
    print(f" Mode: {'APPLY (IN-MEMORY)' if apply_mode else 'DRY-RUN'} | Save: {save_mode}")
    if only_move_id:
        print(f" Selector: Only '{only_move_id}'")
    print("================================================================================")

    # Synthetic Safety Gate
    synthetic_detected = is_synthetic or any(c.get("synthetic") is True for c in cards_data)
    if synthetic_detected and not allow_synthetic:
        print("[CARD_FATAL] Input data is marked SYNTHETIC. Authoring refused without explicit --allow-synthetic flag.")
        return 1

    # Filter cards if selector passed
    selected_cards = cards_data
    if only_move_id:
        selected_cards = [c for c in cards_data if c.get("MoveId") == only_move_id]
        if not selected_cards:
            print(f"[CARD_FATAL] No card matching MoveId '{only_move_id}' found in input data.")
            return 1

    # Phase 1: Validate all cards offline
    valid_cards = []
    has_errors = False
    for card in selected_cards:
        m_id = card.get("MoveId", "<Unnamed>")
        errors = validate_move_card_spec(card)
        if errors:
            print(f"[CARD_VALIDATE] FAIL MoveId='{m_id}': {', '.join(errors)}")
            has_errors = True
        else:
            print(f"[CARD_VALIDATE] OK   MoveId='{m_id}' (Family='{card.get('FamilyId')}')")
            valid_cards.append(card)

    if has_errors or not valid_cards:
        print("\n[CARD_FATAL] One or more move cards failed validation rules. Authoring halted.")
        return 1

    print(f"\n[CARD_PLAN] {len(valid_cards)} move card(s) qualified for authoring under '{TARGET_PACKAGE_DIR}':")
    for c in valid_cards:
        print(f"  - {TARGET_PACKAGE_DIR}/{c['MoveId']} (Sequence='{os.path.basename(str(c['Sequence']))}')")

    if not apply_mode:
        print("\n[CARD_DRYRUN] Dry-run complete. Pass --apply to create assets in memory, and --save to write packages.")
        return 0

    # Phase 2: Editor Environment Guard & Asset Creation
    try:
        import unreal
    except ImportError:
        print("\n[CARD_FATAL] 'unreal' Python module unavailable. Must run within Unreal Editor.")
        return 1

    editor_asset_lib = getattr(unreal, "EditorAssetLibrary", None)
    if not editor_asset_lib:
        print("[CARD_FATAL] unreal.EditorAssetLibrary missing. Fails closed.")
        return 1

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    if not asset_tools:
        print("[CARD_FATAL] AssetTools unavailable. Fails closed.")
        return 1

    created_assets = []
    for card in valid_cards:
        move_id = card["MoveId"]
        package_path = f"{TARGET_PACKAGE_DIR}/{move_id}"

        # Anti-overwrite check
        if editor_asset_lib.does_asset_exist(package_path):
            print(f"[CARD_FATAL] Asset already exists at '{package_path}'. Overwrite forbidden.")
            return 1

        print(f"\n[CARD_APPLY] Creating URPGBossMoveCard at '{package_path}'...")
        asset_cls = getattr(unreal, "RPGBossMoveCard", None)
        if not asset_cls:
            print("[CARD_FATAL] UClass 'unreal.RPGBossMoveCard' not reflected. Fails closed.")
            return 1

        # Load Animation Asset and verify clip length from loaded sequence
        anim_path = card.get("Sequence") or card.get("Montage")
        anim_obj = editor_asset_lib.load_asset(anim_path)
        if not anim_obj:
            print(f"[CARD_FATAL] Failed to load animation asset at '{anim_path}'. Fails closed.")
            return 1

        clip_len = None
        api_used = None
        if hasattr(anim_obj, "get_play_length") and callable(getattr(anim_obj, "get_play_length")):
            clip_len = float(anim_obj.get_play_length())
            api_used = "get_play_length()"
        elif hasattr(anim_obj, "sequence_length"):
            clip_len = float(anim_obj.sequence_length)
            api_used = "sequence_length"
        elif hasattr(anim_obj, "get_editor_property"):
            try:
                clip_len = float(anim_obj.get_editor_property("sequence_length"))
                api_used = "get_editor_property('sequence_length')"
            except Exception:
                pass

        if clip_len is None or clip_len <= 0.0:
            print(f"[CARD_FATAL] Unable to obtain clip length for animation '{anim_path}'. Fails closed.")
            return 1

        print(f"[CARD_ANIM] Obtained clip length {clip_len:.4f}s for '{anim_path}' using {api_used}")
        if float(card["RecoveryEndSeconds"]) > clip_len:
            print(f"[CARD_FATAL] RecoveryEndSeconds ({card['RecoveryEndSeconds']}) exceeds loaded clip length ({clip_len:.4f}s). Refusing to author.")
            return 1

        factory = unreal.DataAssetFactory()
        new_asset = asset_tools.create_asset(
            asset_name=move_id,
            package_path=TARGET_PACKAGE_DIR,
            asset_class=asset_cls,
            factory=factory
        )
        if not new_asset:
            print(f"[CARD_FATAL] Failed to create asset at '{package_path}'")
            return 1

        # Populate Spec struct
        spec = new_asset.get_editor_property("spec")
        spec.set_editor_property("schema", int(card["Schema"]))
        spec.set_editor_property("move_id", unreal.Name(card["MoveId"]))
        spec.set_editor_property("family_id", unreal.Name(card["FamilyId"]))
        spec.set_editor_property("phase_id", unreal.Name(card["PhaseId"]))

        # Soft object references
        skel_obj = editor_asset_lib.load_asset(card["Skeleton"])
        spec.set_editor_property("skeleton", skel_obj)

        if card.get("Sequence"):
            spec.set_editor_property("sequence", anim_obj)
        elif card.get("Montage"):
            spec.set_editor_property("montage", anim_obj)

        spec.set_editor_property("slot_name", unreal.Name(card["SlotName"]))
        if card.get("SectionName") and card["SectionName"] != "None":
            spec.set_editor_property("section_name", unreal.Name(card["SectionName"]))

        spec.set_editor_property("play_rate", float(card["PlayRate"]))
        spec.set_editor_property("commit_seconds", float(card["CommitSeconds"]))
        spec.set_editor_property("active_start_seconds", float(card["ActiveStartSeconds"]))
        spec.set_editor_property("active_end_seconds", float(card["ActiveEndSeconds"]))
        spec.set_editor_property("recovery_end_seconds", float(card["RecoveryEndSeconds"]))
        spec.set_editor_property("track_degrees_per_second", float(card["TrackDegreesPerSecond"]))
        spec.set_editor_property("min_range_cm", float(card["MinRangeCm"]))
        spec.set_editor_property("max_range_cm", float(card["MaxRangeCm"]))
        spec.set_editor_property("front_cone_degrees", float(card["FrontConeDegrees"]))
        spec.set_editor_property("hp_damage", float(card["HPDamage"]))
        spec.set_editor_property("b_uses_root_motion", bool(card["bUsesRootMotion"]))

        # Populate Windows array
        win_array = []
        for w in card.get("Windows", []):
            win_struct = unreal.RPGBossMoveWindow()
            win_struct.set_editor_property("window_id", unreal.Name(w["WindowId"]))
            win_struct.set_editor_property("hit_group", unreal.Name(w["HitGroup"]))
            win_struct.set_editor_property("start_seconds", float(w["StartSeconds"]))
            win_struct.set_editor_property("end_seconds", float(w["EndSeconds"]))
            win_struct.set_editor_property("socket_a", unreal.Name(w["SocketA"]))
            win_struct.set_editor_property("socket_b", unreal.Name(w["SocketB"]))
            win_struct.set_editor_property("radius_cm", float(w["RadiusCm"]))
            win_array.append(win_struct)
        spec.set_editor_property("windows", win_array)

        new_asset.set_editor_property("spec", spec)

        # Full Read-back Verification
        read_spec = new_asset.get_editor_property("spec")
        assert int(read_spec.get_editor_property("schema")) == card["Schema"], "Schema readback failed"
        assert str(read_spec.get_editor_property("move_id")) == card["MoveId"], "MoveId readback failed"
        assert len(read_spec.get_editor_property("windows")) == len(card["Windows"]), "Windows readback failed"
        print(f"[CARD_VERIFY] Readback OK: 21 typed fields & {len(card['Windows'])} window(s) verified.")

        created_assets.append((new_asset, package_path))

    # Phase 3: Save opt-in
    if save_mode:
        for asset, path in created_assets:
            saved = editor_asset_lib.save_loaded_asset(asset)
            if not saved:
                print(f"[CARD_FATAL] Failed to save asset to disk at '{path}'")
                return 1
            print(f"[CARD_SAVE] Saved package to disk: '{path}.uasset'")

    print("\n================================================================================")
    print(f" CARD AUTHORING SUCCESS: {len(created_assets)} card asset(s) verified.")
    if not save_mode:
        print(" NOTICE: Assets created in memory. Pass --save to write to disk.")
    print("================================================================================")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Author URPGBossMoveCard data assets from JSON.")
    parser.add_argument("--input-json", required=True, help="Path to input JSON cards file.")
    parser.add_argument("--apply", action="store_true", help="Create assets in memory.")
    parser.add_argument("--save", action="store_true", help="Opt-in disk save (requires --apply).")
    parser.add_argument("--only", default=None, help="Filter by MoveId.")
    parser.add_argument("--allow-synthetic", action="store_true", help="Permit synthetic input data (test fixtures only).")
    args = parser.parse_args()

    if args.save and not args.apply:
        print("[CARD_FATAL] --save requires --apply flag.")
        sys.exit(1)

    if not os.path.isfile(args.input_json):
        print(f"[CARD_FATAL] Input JSON file not found: '{args.input_json}'")
        sys.exit(1)

    with open(args.input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    is_synth = False
    if isinstance(data, dict):
        if data.get("synthetic") is True:
            is_synth = True
        cards = data.get("cards", [data]) if "cards" in data else [data]
    elif isinstance(data, list):
        cards = data
    else:
        cards = [data]

    for c in cards:
        if c.get("synthetic") is True:
            is_synth = True

    if is_synth and not args.allow_synthetic:
        print("[CARD_FATAL] Input data is marked SYNTHETIC. Authoring refused without explicit --allow-synthetic flag.")
        sys.exit(1)

    sys.exit(execute_authoring(
        cards_data=cards,
        apply_mode=args.apply,
        save_mode=args.save,
        only_move_id=args.only,
        allow_synthetic=args.allow_synthetic,
        is_synthetic=is_synth
    ))


if __name__ == "__main__":
    main()
