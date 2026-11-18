"""BT-102: Read-only Unreal Editor probe for G-06 roll montage properties.

Inspects saved asset properties for:
  1. Pack mannequin quick-roll montage:
     /Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage
  2. Greystone _Grey quick-roll montage:
     /Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage_Grey
  3. Isolated _RM candidate quick-roll montage:
     /Game/OneBossFight/Player/Greystone/RootMotion/Montages/quick/Dodge_Small_Forward_Roll_Montage_Grey_RM
  4. Child player Blueprint component defaults:
     /Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer -> URPGDodgeTiming

Reads montage play length, rate scale, blend-in/out times, composite sections, slot tracks,
and all FAnimSegment fields (anim_reference, anim_start_time, anim_end_time, anim_play_rate,
start_pos, looping_count) plus referenced sequence root-motion flags and extracted root travel.

Strictly non-mutating on assets/config: performs zero asset creations, saves, modifications,
or deletions, and zero config modifications. Writes only an evidence JSON file to the Saved/ directory.
Fails closed if any asset or required property is missing. Missing optional properties and extraction
errors are explicitly recorded as null/error dictionaries, never substituted with fabricated values.
"""
from __future__ import annotations

import json
import os
import time
import traceback

import unreal

PREFIX = "[G06RollProbe] "

PACK_MANNEQUIN_QUICK_MONTAGE = (
    "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage"
)
GREY_QUICK_MONTAGE = (
    "/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage_Grey"
)
RM_CANDIDATE_QUICK_MONTAGE = (
    "/Game/OneBossFight/Player/Greystone/RootMotion/Montages/quick/Dodge_Small_Forward_Roll_Montage_Grey_RM"
)
CHILD_BP_PATH = "/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer"

MONTAGES_TO_INSPECT = (
    ("pack_mannequin", PACK_MANNEQUIN_QUICK_MONTAGE),
    ("greystone_grey", GREY_QUICK_MONTAGE),
    ("greystone_rm_candidate", RM_CANDIDATE_QUICK_MONTAGE),
)


def log(msg: str) -> None:
    unreal.log(PREFIX + str(msg))


def log_error(msg: str) -> None:
    unreal.log_error(PREFIX + str(msg))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def get_prop(obj: object, name_snake: str, name_pascal: str | None = None) -> object:
    """Read an editor property trying snake_case first, then PascalCase; fails closed if neither exists."""
    names_to_try = [name_snake]
    if name_pascal and name_pascal != name_snake:
        names_to_try.append(name_pascal)
    for n in names_to_try:
        try:
            return obj.get_editor_property(n)
        except Exception:
            continue
    raise AttributeError(f"Object {obj} has neither property '{name_snake}' nor '{name_pascal}'")


def get_prop_strict(obj: object, name_snake: str, name_pascal: str | None = None) -> tuple[object, str | None]:
    """Read an editor property; returns (value, None) on success or (None, error_string) on failure without fabricating values."""
    try:
        val = get_prop(obj, name_snake, name_pascal)
        return val, None
    except Exception as exc:
        return None, str(exc)


def format_asset_path(obj: object) -> str | None:
    if obj is None:
        return None
    if hasattr(obj, "get_path_name"):
        return str(obj.get_path_name())
    return str(obj)


def inspect_anim_segment(segment: object) -> dict:
    """Inspect an FAnimSegment struct with fail-closed requirements and explicit null/error records."""
    anim_ref = get_prop(segment, "anim_reference", "AnimReference")
    start_time = float(get_prop(segment, "anim_start_time", "AnimStartTime"))
    end_time = float(get_prop(segment, "anim_end_time", "AnimEndTime"))
    play_rate = float(get_prop(segment, "anim_play_rate", "AnimPlayRate"))

    start_pos_val, start_pos_err = get_prop_strict(segment, "start_pos", "StartPos")
    looping_count_val, looping_count_err = get_prop_strict(segment, "looping_count", "LoopingCount")

    seq_info = None
    if anim_ref is not None:
        seq_path = format_asset_path(anim_ref)
        enable_rm = bool(get_prop(anim_ref, "enable_root_motion", "bEnableRootMotion"))
        root_lock = str(get_prop(anim_ref, "root_motion_root_lock", "RootMotionRootLock"))
        force_lock = bool(get_prop(anim_ref, "force_root_lock", "bForceRootLock"))
        play_len = float(anim_ref.get_play_length()) if hasattr(anim_ref, "get_play_length") else None

        sampled_frames_val, sampled_frames_err = get_prop_strict(
            anim_ref, "number_of_sampled_frames", "NumberOfSampledFrames"
        )

        raw_displacement_cm = None
        extraction_error = None
        if hasattr(anim_ref, "extract_root_motion") and play_len is not None:
            try:
                delta = anim_ref.extract_root_motion(0.0, play_len, False)
                dx = delta.translation.x
                dy = delta.translation.y
                raw_displacement_cm = float((dx * dx + dy * dy) ** 0.5)
            except Exception as exc:
                extraction_error = repr(exc)
                log_error(f"extract_root_motion failed for {seq_path}: {extraction_error}")
        else:
            extraction_error = "extract_root_motion method missing or play_len is null"

        seq_info = {
            "path": seq_path,
            "play_length": play_len,
            "enable_root_motion": enable_rm,
            "root_motion_root_lock": root_lock,
            "force_root_lock": force_lock,
            "number_of_sampled_frames": sampled_frames_val if sampled_frames_err is None else None,
            "number_of_sampled_frames_error": sampled_frames_err,
            "raw_root_xy_displacement_cm": raw_displacement_cm,
            "extraction_error": extraction_error,
        }

    return {
        "anim_reference_path": format_asset_path(anim_ref),
        "anim_start_time": start_time,
        "anim_end_time": end_time,
        "anim_play_rate": play_rate,
        "start_pos": float(start_pos_val) if start_pos_val is not None else None,
        "start_pos_error": start_pos_err,
        "looping_count": int(looping_count_val) if looping_count_val is not None else None,
        "looping_count_error": looping_count_err,
        "referenced_sequence": seq_info,
    }


def inspect_montage(label: str, path: str) -> dict:
    """Inspect an AnimMontage asset, failing closed on missing assets/properties."""
    eal = unreal.EditorAssetLibrary
    require(eal.does_asset_exist(path), f"required montage does not exist: {path}")
    montage = unreal.load_asset(path)
    require(montage is not None, f"could not load montage: {path}")
    require(
        montage.get_class().get_name() == "AnimMontage",
        f"asset {path} is not an AnimMontage (got {montage.get_class().get_name()})",
    )

    play_length = float(montage.get_play_length())
    sequence_length = float(get_prop(montage, "sequence_length", "SequenceLength"))
    rate_scale = float(get_prop(montage, "rate_scale", "RateScale"))

    # Blend In
    blend_in_struct = get_prop(montage, "blend_in", "BlendIn")
    blend_in_time = float(get_prop(blend_in_struct, "blend_time", "BlendTime"))
    blend_in_opt = str(get_prop(blend_in_struct, "blend_option", "BlendOption"))

    # Blend Out
    blend_out_struct = get_prop(montage, "blend_out", "BlendOut")
    blend_out_time = float(get_prop(blend_out_struct, "blend_time", "BlendTime"))
    blend_out_opt = str(get_prop(blend_out_struct, "blend_option", "BlendOption"))

    blend_out_trigger = float(get_prop(montage, "blend_out_trigger_time", "BlendOutTriggerTime"))

    # Composite Sections
    sections_list = []
    comp_sections = get_prop(montage, "composite_sections", "CompositeSections")
    for sec in comp_sections:
        sec_name = str(get_prop(sec, "section_name", "SectionName"))
        sec_time = float(get_prop(sec, "time", "Time"))
        sections_list.append({"section_name": sec_name, "time": sec_time})

    # Slot Tracks and Anim Segments
    slot_tracks_list = []
    slot_tracks = get_prop(montage, "slot_anim_tracks", "SlotAnimTracks")
    for track in slot_tracks:
        slot_name = str(get_prop(track, "slot_name", "SlotName"))
        anim_track = get_prop(track, "anim_track", "AnimTrack")
        segments = get_prop(anim_track, "anim_segments", "AnimSegments")
        seg_records = [inspect_anim_segment(seg) for seg in segments]
        slot_tracks_list.append({"slot_name": slot_name, "segments": seg_records})

    skeleton_obj = get_prop(montage, "skeleton", "Skeleton")
    skeleton_path = format_asset_path(skeleton_obj)

    record = {
        "label": label,
        "path": path,
        "skeleton": skeleton_path,
        "play_length": play_length,
        "sequence_length": sequence_length,
        "rate_scale": rate_scale,
        "blend_in": {"blend_time": blend_in_time, "blend_option": blend_in_opt},
        "blend_out": {"blend_time": blend_out_time, "blend_option": blend_out_opt},
        "blend_out_trigger_time": blend_out_trigger,
        "composite_sections": sections_list,
        "slot_anim_tracks": slot_tracks_list,
    }

    log(
        f"MONTAGE label={label} name={montage.get_name()} len={play_length:.4f} rate_scale={rate_scale:.3f} "
        f"blend_in={blend_in_time:.3f} blend_out={blend_out_time:.3f} trigger={blend_out_trigger:.4f} "
        f"tracks={len(slot_tracks_list)} sections={len(sections_list)}"
    )
    return record


def inspect_child_blueprint(path: str) -> dict:
    """Inspect BP_GreystoneERPlayer's saved URPGDodgeTiming component defaults."""
    eal = unreal.EditorAssetLibrary
    require(eal.does_asset_exist(path), f"child Blueprint missing: {path}")
    bp = unreal.load_asset(path)
    require(bp is not None, f"could not load child Blueprint: {path}")

    subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    lib = unreal.SubobjectDataBlueprintFunctionLibrary
    timing_component = None

    if subsystem and lib:
        handles = subsystem.k2_gather_subobject_data_for_blueprint(bp)
        for handle in handles:
            obj = lib.get_object(lib.get_data(handle))
            if obj is not None and obj.get_class().get_name() == "RPGDodgeTiming":
                require(timing_component is None, "multiple URPGDodgeTiming components found on child BP")
                timing_component = obj

    if timing_component is None:
        cls = bp.generated_class()
        if cls:
            cdo = unreal.get_default_object(cls)
            if cdo:
                try:
                    timing_component = cdo.get_component_by_class(unreal.RPGDodgeTiming)
                except Exception:
                    pass

    require(timing_component is not None, f"child BP {path} has no URPGDodgeTiming component defaults")

    quick_montage = format_asset_path(get_prop(timing_component, "quick_montage", "QuickMontage"))
    quick_rate = float(get_prop(timing_component, "quick_play_rate", "QuickPlayRate"))
    full_montage = format_asset_path(get_prop(timing_component, "full_montage", "FullMontage"))
    full_rate = float(get_prop(timing_component, "full_play_rate", "FullPlayRate"))

    backstep_montage = format_asset_path(get_prop(timing_component, "backstep_montage", "BackstepMontage"))
    backstep_rate = float(get_prop(timing_component, "backstep_play_rate", "BackstepPlayRate"))

    record = {
        "blueprint_path": path,
        "timing_component_class": timing_component.get_class().get_name(),
        "source_boundary_note": "Values reflect saved Blueprint component defaults; they do not observe C++ constructor defaults or runtime ApplyClip ability map rewrites.",
        "quick_montage": quick_montage,
        "quick_play_rate": quick_rate,
        "full_montage": full_montage,
        "full_play_rate": full_rate,
        "backstep_montage": backstep_montage,
        "backstep_play_rate": backstep_rate,
    }

    log(
        f"CHILD_BP path={path} QuickMontage={quick_montage} QuickPlayRate={quick_rate:.3f} "
        f"FullMontage={full_montage} FullPlayRate={full_rate:.3f}"
    )
    return record


def main() -> None:
    log("BEGIN G-06 roll montage property probe (read-only; zero asset/config mutations)")
    montage_records = []
    for label, path in MONTAGES_TO_INSPECT:
        record = inspect_montage(label, path)
        montage_records.append(record)

    child_record = inspect_child_blueprint(CHILD_BP_PATH)

    property_errors = []
    extraction_errors = []
    total_segments = 0

    expected_montage_count = len(MONTAGES_TO_INSPECT)
    if len(montage_records) != expected_montage_count:
        property_errors.append(f"montage_count_mismatch:expected={expected_montage_count}:actual={len(montage_records)}")

    for m in montage_records:
        montage_seg_count = 0
        tracks = m.get("slot_anim_tracks", [])
        if not tracks:
            property_errors.append(f"{m['label']}:missing_slot_anim_tracks")
        for t in tracks:
            segments = t.get("segments", [])
            for s in segments:
                total_segments += 1
                montage_seg_count += 1
                if s.get("start_pos") is None or s.get("start_pos_error") is not None:
                    property_errors.append(f"{m['label']}:start_pos_error={s.get('start_pos_error')}")
                if s.get("looping_count") is None or s.get("looping_count_error") is not None:
                    property_errors.append(f"{m['label']}:looping_count_error={s.get('looping_count_error')}")
                seq = s.get("referenced_sequence")
                if seq is not None:
                    if seq.get("number_of_sampled_frames_error") is not None:
                        property_errors.append(f"{m['label']}:sampled_frames_error={seq.get('number_of_sampled_frames_error')}")
                    if seq.get("extraction_error") is not None or seq.get("raw_root_xy_displacement_cm") is None:
                        extraction_errors.append(f"{m['label']}:{seq.get('path')}:{seq.get('extraction_error')}")
                else:
                    extraction_errors.append(f"{m['label']}:missing_referenced_sequence")
        if montage_seg_count == 0:
            property_errors.append(f"{m['label']}:has_zero_anim_segments")

    if total_segments == 0:
        property_errors.append("zero_total_anim_segments_across_all_montages")

    # Inspect child Blueprint component defaults
    if not child_record.get("quick_montage"):
        property_errors.append("child_blueprint:quick_montage_missing_or_empty")
    if child_record.get("quick_play_rate") is None or child_record.get("quick_play_rate") <= 0.0:
        property_errors.append("child_blueprint:quick_play_rate_invalid")
    if not child_record.get("full_montage"):
        property_errors.append("child_blueprint:full_montage_missing_or_empty")
    if child_record.get("full_play_rate") is None or child_record.get("full_play_rate") <= 0.0:
        property_errors.append("child_blueprint:full_play_rate_invalid")
    if child_record.get("timing_component_class") != "RPGDodgeTiming":
        property_errors.append("child_blueprint:timing_component_class_not_RPGDodgeTiming")

    all_errors = extraction_errors + property_errors
    outcome = "PASS" if not all_errors else "PARTIAL"

    output_payload = {
        "schema_version": 1,
        "task": "BT-102",
        "probe": "probe_g06_roll_montages.py",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "outcome": outcome,
        "total_segments": total_segments,
        "extraction_errors": extraction_errors,
        "property_errors": property_errors,
        "non_mutating_invariants": {
            "zero_asset_creations": True,
            "zero_asset_saves": True,
            "zero_asset_deletions": True,
            "zero_config_modifications": True,
            "evidence_json_written_to_saved": True,
        },
        "montages": montage_records,
        "child_blueprint": child_record,
    }

    saved_dir = unreal.Paths.project_saved_dir()
    manifest_path = os.path.join(saved_dir, f"G06RollMontageProbe_{time.strftime('%Y%m%d_%H%M%S')}.json")
    with open(manifest_path, "w", encoding="utf-8") as handle:
        json.dump(output_payload, handle, indent=2)

    log(f"OUTPUT_MANIFEST {manifest_path}")
    if outcome == "PASS":
        log(f"RESULT=PASS montages={len(montage_records)} child_bp=1 total_segments={total_segments} root_extractions_ok={total_segments} properties_ok={total_segments}")
    else:
        log(f"RESULT=PARTIAL montages={len(montage_records)} child_bp=1 total_segments={total_segments} total_errors={len(all_errors)} extraction_errors={len(extraction_errors)} property_errors={len(property_errors)} error_details={'; '.join(all_errors)}")



try:
    main()
except Exception as error:
    log_error(f"RESULT=FAIL error={error!r}")
    traceback.print_exc()
finally:
    try:
        unreal.SystemLibrary.execute_console_command(None, "Quit")
    except Exception:
        pass
