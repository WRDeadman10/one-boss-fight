#!/usr/bin/env python3
"""
bake_blade_path.py
==================
Unreal Engine Editor Python helper for baking component-space blade paths
at 120 Hz for sub-tick hit window sweep interpolation (KI-147 / F4c / A-308).

Read-only on animation and card assets. Extracts [BaseCS, TipCS] bone/socket
trajectories across active hit windows into deterministic JSON payloads.

Execution Modes:
1. Live Editor Mode (run via run_editor_script.ps1):
   - Loads UAnimSequence assets via unreal.EditorAssetLibrary.
   - Evaluates AnimPose in Component (WORLD) space at 1/120s plus window edges.
   - Reads socket_a ('weapon_r') and socket_b ('root_weapon_end_r').
2. Synthetic Arc Control (--synthetic-arc):
   - Runs 100% offline with zero engine dependency.
   - Evaluates closed-form analytical arc/thrust trajectory.
   - Produces deterministic test samples for offline authoring tests.

Safety Gates:
- REFUSES if requested sequence differs from card's declared Sequence.
- REFUSES if window end exceeds clip play length.
- Strictly read-only on assets. Emits JSON to stdout and optional --output-json.
"""

import sys
import os
import math
import json
import argparse
from typing import List, Dict, Any, Tuple, Optional

NOMINAL_RATE_HZ = 120.0
NOMINAL_DT = 1.0 / NOMINAL_RATE_HZ


def resolve_world_space_enum(unreal_mod: Any) -> Any:
    """Resolve EAnimPoseSpaces::World enum value from unreal reflection."""
    if hasattr(unreal_mod, "AnimPoseSpaces"):
        enum_cls = getattr(unreal_mod, "AnimPoseSpaces")
        if hasattr(enum_cls, "WORLD"):
            return getattr(enum_cls, "WORLD")
        if hasattr(enum_cls, "World"):
            return getattr(enum_cls, "World")
    return 1


def evaluate_pose_at_time(unreal_mod: Any, seq_asset: Any, time_sec: float) -> Any:
    """Evaluate FAnimPose at time using AnimPoseExtensions or sequence method."""
    eval_opts = None
    if hasattr(unreal_mod, "AnimPoseEvaluationOptions"):
        eval_opts = unreal_mod.AnimPoseEvaluationOptions()
        if hasattr(eval_opts, "b_should_retarget"):
            eval_opts.b_should_retarget = True
        if hasattr(eval_opts, "b_incorporate_root_motion_into_pose"):
            eval_opts.b_incorporate_root_motion_into_pose = True

    if hasattr(unreal_mod, "AnimPoseExtensions"):
        ext = unreal_mod.AnimPoseExtensions
        if hasattr(ext, "get_anim_pose_at_time"):
            try:
                return ext.get_anim_pose_at_time(seq_asset, time_sec, eval_opts)
            except TypeError:
                if hasattr(unreal_mod, "AnimPose"):
                    pose = unreal_mod.AnimPose()
                    ext.get_anim_pose_at_time(seq_asset, time_sec, eval_opts, pose)
                    return pose

    if hasattr(seq_asset, "get_anim_pose_at_time"):
        return seq_asset.get_anim_pose_at_time(time_sec, eval_opts)

    raise RuntimeError("Could not find working get_anim_pose_at_time reflection binding")


def get_bone_translation(unreal_mod: Any, pose: Any, bone_name: str) -> Tuple[float, float, float]:
    """Extract component-space bone translation (x, y, z) from pose."""
    world_space = resolve_world_space_enum(unreal_mod)
    if hasattr(pose, "get_bone_pose"):
        try:
            t = pose.get_bone_pose(bone_name, world_space)
            return (float(t.translation.x), float(t.translation.y), float(t.translation.z))
        except Exception:
            pass

    if hasattr(unreal_mod, "AnimPoseExtensions"):
        ext = unreal_mod.AnimPoseExtensions
        if hasattr(ext, "get_bone_pose"):
            try:
                t = ext.get_bone_pose(pose, bone_name, world_space)
                return (float(t.translation.x), float(t.translation.y), float(t.translation.z))
            except Exception:
                pass

    raise RuntimeError(f"Could not resolve component-space GetBonePose for '{bone_name}'")


def compute_sample_times(w_start: float, w_end: float, rate_hz: float = NOMINAL_RATE_HZ) -> List[float]:
    """
    Computes strictly ascending sample times:
    - Starts exactly at w_start.
    - Includes intermediate multiples of 1/rate_hz strictly inside (w_start, w_end).
    - Ends exactly at w_end.
    """
    if w_end <= w_start:
        raise ValueError(f"Invalid window span: Start ({w_start}) >= End ({w_end})")

    dt = 1.0 / rate_hz
    times = [round(w_start, 6)]

    # First intermediate multiple of dt strictly > w_start + epsilon
    first_k = math.ceil((w_start + 1e-6) / dt)
    curr_t = first_k * dt
    while curr_t < (w_end - 1e-6):
        times.append(round(curr_t, 6))
        curr_t += dt

    # Ensure w_end is the final sample
    if abs(times[-1] - w_end) > 1e-6:
        times.append(round(w_end, 6))

    # Deduplicate and sort
    sorted_unique = sorted(list(set(times)))
    return sorted_unique


def generate_synthetic_arc_samples(
    w_start: float,
    w_end: float,
    rate_hz: float = NOMINAL_RATE_HZ,
    is_thrust: bool = True
) -> List[Dict[str, Any]]:
    """
    Generates synthetic deterministic blade path samples for offline testing.
    Models an out-and-back thrust or swing arc with realistic Sevarog proportions:
    - Base starts around (115, 0, 100), apex reaches (12, 0, 100) (deep penetration).
    - Tip is extended along blade vector (+X / +Y, reach ~ 138.5 cm).
    """
    times = compute_sample_times(w_start, w_end, rate_hz)
    span = w_end - w_start
    samples = []

    for t in times:
        u = (t - w_start) / span  # 0.0 to 1.0
        # Parabolic bell curve: 0 at u=0 and u=1, apex=1 at u=0.5
        apex_factor = 4.0 * u * (1.0 - u)

        if is_thrust:
            # Base X: 120 cm at edges, 12 cm at apex
            base_x = 120.0 - (108.0 * apex_factor)
            base_y = 0.0
            base_z = 100.0 + (10.0 * apex_factor)

            # Tip X: extends forward
            tip_x = base_x - 65.0
            tip_y = base_y + 115.0
            tip_z = base_z + 20.0
        else:
            # Circular horizontal swing
            angle = (u - 0.5) * math.pi * 0.75  # sweep -67.5 to +67.5 deg
            radius = 140.0
            base_x = 30.0 + 20.0 * math.cos(angle)
            base_y = radius * 0.3 * math.sin(angle)
            base_z = 100.0

            tip_x = base_x + radius * math.cos(angle)
            tip_y = radius * math.sin(angle)
            tip_z = base_z + 10.0

        samples.append({
            "TimeSeconds": round(t, 6),
            "BaseCS": [round(base_x, 4), round(base_y, 4), round(base_z, 4)],
            "TipCS": [round(tip_x, 4), round(tip_y, 4), round(tip_z, 4)]
        })

    return samples


def bake_window_samples_live(
    unreal_mod: Any,
    seq_asset: Any,
    w_start: float,
    w_end: float,
    socket_a: str = "weapon_r",
    socket_b: str = "root_weapon_end_r",
    rate_hz: float = NOMINAL_RATE_HZ
) -> List[Dict[str, Any]]:
    """Samples live animation asset at 120 Hz plus window edges."""
    times = compute_sample_times(w_start, w_end, rate_hz)
    samples = []

    for t in times:
        pose = evaluate_pose_at_time(unreal_mod, seq_asset, t)
        base_cs = get_bone_translation(unreal_mod, pose, socket_a)
        tip_cs = get_bone_translation(unreal_mod, pose, socket_b)

        samples.append({
            "TimeSeconds": round(t, 6),
            "BaseCS": [round(base_cs[0], 4), round(base_cs[1], 4), round(base_cs[2], 4)],
            "TipCS": [round(tip_cs[0], 4), round(tip_cs[1], 4), round(tip_cs[2], 4)]
        })

    return samples


def get_clip_length(seq_asset: Any) -> Optional[float]:
    """Extract clip length in seconds from animation asset."""
    if hasattr(seq_asset, "get_play_length") and callable(getattr(seq_asset, "get_play_length")):
        return float(seq_asset.get_play_length())
    if hasattr(seq_asset, "sequence_length"):
        return float(seq_asset.sequence_length)
    if hasattr(seq_asset, "get_editor_property"):
        try:
            return float(seq_asset.get_editor_property("sequence_length"))
        except Exception:
            pass
    return None


def run_bake(
    card_data: Dict[str, Any],
    unreal_mod: Optional[Any] = None,
    requested_sequence: Optional[str] = None,
    synthetic_arc: bool = False,
    rate_hz: float = NOMINAL_RATE_HZ
) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Executes blade path baking for all windows in a MoveCard spec.
    Enforces all safety gates:
    - Sequence identity matching.
    - Window end <= clip length.
    - Monotonic, bounded samples.
    Returns (success, result_dict, log_lines).
    """
    logs = []
    move_id = card_data.get("MoveId", "UnknownMove")
    declared_seq = card_data.get("Sequence") or card_data.get("Montage")

    # Gate 1: Sequence identity check
    if requested_sequence and declared_seq:
        if requested_sequence != declared_seq:
            err = f"Sequence mismatch: requested sequence '{requested_sequence}' does not match card sequence '{declared_seq}'"
            logs.append(f"[BAKE_FATAL] {err}")
            return False, {}, logs

    active_seq_path = requested_sequence or declared_seq
    if not active_seq_path and not synthetic_arc:
        err = "No Sequence specified in card data and no --sequence argument passed."
        logs.append(f"[BAKE_FATAL] {err}")
        return False, {}, logs

    seq_asset = None
    clip_len = None

    if synthetic_arc:
        clip_len = float(card_data.get("ClipLengthSeconds", 1.5))
        logs.append(f"[BAKE_SYNTH] Using synthetic arc mode. ClipLength={clip_len:.4f}s")
    else:
        if not unreal_mod:
            try:
                import unreal  # type: ignore
                unreal_mod = unreal
            except ImportError:
                err = "Unreal module not available and --synthetic-arc flag was not specified."
                logs.append(f"[BAKE_FATAL] {err}")
                return False, {}, logs

        editor_asset_lib = getattr(unreal_mod, "EditorAssetLibrary", None)
        if not editor_asset_lib:
            err = "unreal.EditorAssetLibrary not found."
            logs.append(f"[BAKE_FATAL] {err}")
            return False, {}, logs

        seq_asset = editor_asset_lib.load_asset(active_seq_path)
        if not seq_asset:
            err = f"Could not load animation sequence asset at '{active_seq_path}'"
            logs.append(f"[BAKE_FATAL] {err}")
            return False, {}, logs

        clip_len = get_clip_length(seq_asset)
        if clip_len is None or clip_len <= 0.0:
            err = f"Failed to retrieve valid clip length for sequence '{active_seq_path}'"
            logs.append(f"[BAKE_FATAL] {err}")
            return False, {}, logs

        # Check declared clip length consistency if present
        card_clip_len = card_data.get("ClipLengthSeconds")
        if card_clip_len is not None and abs(float(card_clip_len) - clip_len) > 1e-3:
            logs.append(f"[BAKE_WARN] Card ClipLengthSeconds ({card_clip_len}) differs from asset clip length ({clip_len:.4f}s). Asset length authoritative.")

    windows = card_data.get("Windows", [])
    if not windows:
        err = f"Move card '{move_id}' has no windows to bake."
        logs.append(f"[BAKE_FATAL] {err}")
        return False, {}, logs

    baked_windows = []
    total_samples = 0

    for i, w in enumerate(windows):
        win_id = w.get("WindowId", f"Window_{i}")
        w_start = float(w["StartSeconds"])
        w_end = float(w["EndSeconds"])
        sock_a = w.get("SocketA", "weapon_r")
        sock_b = w.get("SocketB", "root_weapon_end_r")

        # Gate 2: Window end <= clip length
        if w_end > clip_len + 1e-4:
            err = f"Window '{win_id}' EndSeconds ({w_end:.4f}s) exceeds clip length ({clip_len:.4f}s). Refusing to bake."
            logs.append(f"[BAKE_FATAL] {err}")
            return False, {}, logs

        logs.append(f"[BAKE_START] MoveId='{move_id}' Window='{win_id}' Span=[{w_start:.4f}..{w_end:.4f}] Sockets=[{sock_a}, {sock_b}]")

        if synthetic_arc:
            samples = generate_synthetic_arc_samples(w_start, w_end, rate_hz=rate_hz)
        else:
            samples = bake_window_samples_live(
                unreal_mod=unreal_mod,
                seq_asset=seq_asset,
                w_start=w_start,
                w_end=w_end,
                socket_a=sock_a,
                socket_b=sock_b,
                rate_hz=rate_hz
            )

        total_samples += len(samples)
        logs.append(f"[BAKE_COMPLETE] Window='{win_id}' Samples={len(samples)} ApexBaseCS={samples[len(samples)//2]['BaseCS']}")

        baked_win = dict(w)
        baked_win["BakedClipLengthSeconds"] = round(clip_len, 4)
        baked_win["BakedSamples"] = samples
        baked_windows.append(baked_win)

    result_card = dict(card_data)
    result_card["ClipLengthSeconds"] = round(clip_len, 4)
    result_card["Windows"] = baked_windows

    logs.append(f"[BAKE_SUMMARY] Successfully baked {len(baked_windows)} window(s), {total_samples} total samples at {rate_hz} Hz.")
    return True, result_card, logs


def main():
    parser = argparse.ArgumentParser(description="Bake 120 Hz component-space blade paths for MoveCards.")
    parser.add_argument("--card-json", default=None, help="Path to input move card JSON file.")
    parser.add_argument("--sequence", default=None, help="Unreal sequence asset path to bake.")
    parser.add_argument("--output-json", default=None, help="Optional output JSON path.")
    parser.add_argument("--only-move", default=None, help="Filter to specific MoveId in card JSON.")
    parser.add_argument("--rate-hz", type=float, default=NOMINAL_RATE_HZ, help="Sampling frequency (default: 120 Hz).")
    parser.add_argument("--synthetic-arc", action="store_true", help="Generate synthetic arc samples offline (no engine).")
    args = parser.parse_args()

    cards_to_bake = []
    if args.card_json:
        if not os.path.isfile(args.card_json):
            print(f"[BAKE_FATAL] Input JSON file not found: '{args.card_json}'")
            sys.exit(1)
        with open(args.card_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            cards_to_bake = data.get("cards", [data]) if "cards" in data else [data]
        elif isinstance(data, list):
            cards_to_bake = data
        else:
            cards_to_bake = [data]
    elif args.sequence:
        cards_to_bake = [{
            "Schema": 1,
            "MoveId": "Move_Standalone_Bake",
            "FamilyId": "Family_01",
            "PhaseId": "Phase_1",
            "Sequence": args.sequence,
            "SlotName": "FullBody",
            "CommitSeconds": 0.2,
            "ActiveStartSeconds": 0.25,
            "ActiveEndSeconds": 0.3083,
            "RecoveryEndSeconds": 0.5,
            "PlayRate": 1.0,
            "ClipLengthSeconds": 1.5,
            "Windows": [{
                "WindowId": "Window_Bake_0",
                "HitGroup": "HitGroup_Blade",
                "StartSeconds": 0.25,
                "EndSeconds": 0.3083,
                "SocketA": "weapon_r",
                "SocketB": "root_weapon_end_r",
                "RadiusCm": 20.0
            }]
        }]
    else:
        print("[BAKE_FATAL] Must specify either --card-json or --sequence.")
        sys.exit(1)

    if args.only_move:
        cards_to_bake = [c for c in cards_to_bake if c.get("MoveId") == args.only_move]
        if not cards_to_bake:
            print(f"[BAKE_FATAL] No card matching MoveId '{args.only_move}' found.")
            sys.exit(1)

    baked_results = []
    for card in cards_to_bake:
        success, result, logs = run_bake(
            card_data=card,
            requested_sequence=args.sequence,
            synthetic_arc=args.synthetic_arc,
            rate_hz=args.rate_hz
        )
        for log in logs:
            print(log)
        if not success:
            sys.exit(1)
        baked_results.append(result)

    final_output = baked_results[0] if len(baked_results) == 1 else {"cards": baked_results}
    json_str = json.dumps(final_output, indent=2)

    print("\n[BAKE_JSON_PAYLOAD]")
    print(json_str)

    if args.output_json:
        out_dir = os.path.dirname(os.path.abspath(args.output_json))
        os.makedirs(out_dir, exist_ok=True)
        # Ensure pure CRLF on Windows
        crlf_json = json_str.replace("\r\n", "\n").replace("\n", "\r\n")
        with open(args.output_json, "wb") as f:
            f.write(crlf_json.encode("utf-8"))
        print(f"\n[BAKE_FILE] Written baked card JSON to '{args.output_json}'.")

    sys.exit(0)


if __name__ == "__main__":
    main()
