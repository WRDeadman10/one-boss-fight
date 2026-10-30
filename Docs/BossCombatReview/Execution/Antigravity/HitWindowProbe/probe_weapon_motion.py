#!/usr/bin/env python3
"""
Hit-Window Extraction Probe (A-243)

Measures weapon motion and component-space tip velocity across Sevarog attack sequences
to provide empirical evidence for authored combat hit windows.

Engine API Reference (UE 5.5):
  1. AnimPose Spaces:
     Header: Engine/Source/Editor/AnimationBlueprintLibrary/Public/AnimPose.h:30-36
     enum class EAnimPoseSpaces : uint8 { Local, World };
     Note: EAnimPoseSpaces::World corresponds to Component Space.
  2. Bone Pose Retrieval (Component Space):
     Header: Engine/Source/Editor/AnimationBlueprintLibrary/Public/AnimPose.h:191
     UFUNCTION(BlueprintPure, meta = (ScriptMethod), Category = "Animation|Pose")
     static const FTransform& GetBonePose(
         UPARAM(ref) const FAnimPose& Pose,
         FName BoneName,
         EAnimPoseSpaces Space = EAnimPoseSpaces::Local);
     Python Bindings:
       unreal.AnimPoseExtensions.get_bone_pose(pose, bone_name, unreal.AnimPoseSpaces.WORLD)
       or pose.get_bone_pose(bone_name, space=unreal.AnimPoseSpaces.WORLD)
  3. AnimPose Evaluation:
     Header: Engine/Source/Editor/AnimationBlueprintLibrary/Public/AnimPose.h:286
     UFUNCTION(BlueprintCallable, meta = (ScriptMethod), Category = "Animation|Pose")
     static void GetAnimPoseAtTime(
         const UAnimSequenceBase* AnimationSequenceBase,
         double Time,
         FAnimPoseEvaluationOptions EvaluationOptions,
         FAnimPose& Pose);
     Python Binding:
       unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, time, eval_options) -> unreal.AnimPose
  4. Track Presence Query:
     Header: Engine/Source/Editor/AnimationBlueprintLibrary/Public/AnimationBlueprintLibrary.h:79
     static void GetAnimationTrackNames(const UAnimSequenceBase* AnimationSequenceBase, TArray<FName>& TrackNames);
     Python Binding:
       unreal.AnimationBlueprintLibrary.get_animation_track_names(seq) -> Array(Name)

Read-only, synchronous. Does not save or mark assets dirty.
"""

import sys
import os
import math
import json
import argparse
from typing import List, Dict, Any, Tuple, Optional

DEFAULT_SEVAROG_SEQUENCES = [
    "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Slow",
    "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Medium",
    "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing2_Medium",
    "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing3_Slow",
    "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Subjugation",
    "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Ultimate_Swing_120fps",
]

DEFAULT_BASE_BONE = "weapon_r"
DEFAULT_TIP_BONE = "root_weapon_end_r"
DEFAULT_DT = 1.0 / 120.0  # 120 Hz sampling (~0.008333 s)


def vector_distance(v1: Tuple[float, float, float], v2: Tuple[float, float, float]) -> float:
    """Euclidean distance in 3D (Unreal units = centimeters)."""
    return math.sqrt(
        (v2[0] - v1[0]) ** 2 +
        (v2[1] - v1[1]) ** 2 +
        (v2[2] - v1[2]) ** 2
    )


def compute_speed(
    pos_prev: Tuple[float, float, float],
    pos_curr: Tuple[float, float, float],
    dt: float
) -> float:
    """Compute scalar velocity in cm/s."""
    if dt <= 0.0:
        return 0.0
    return vector_distance(pos_prev, pos_curr) / dt


def extract_active_windows(
    samples: List[Dict[str, Any]],
    threshold_ratio: float = 0.5,
    min_samples: int = 3
) -> List[Dict[str, Any]]:
    """
    Extract contiguous intervals where tip_speed >= (threshold_ratio * peak_speed).
    Returns list of interval dictionaries with start_time, end_time, peak_speed, peak_time.
    """
    if not samples:
        return []

    peak_speed = max(s["tip_speed"] for s in samples)
    if peak_speed <= 0.0:
        return []

    cutoff = peak_speed * threshold_ratio
    windows = []
    current_window_samples = []

    for s in samples:
        if s["tip_speed"] >= cutoff:
            current_window_samples.append(s)
        else:
            if len(current_window_samples) >= min_samples:
                w_start = current_window_samples[0]["time"]
                w_end = current_window_samples[-1]["time"]
                w_peak = max(cs["tip_speed"] for cs in current_window_samples)
                w_peak_sample = next(cs for cs in current_window_samples if cs["tip_speed"] == w_peak)
                windows.append({
                    "start_time": round(w_start, 4),
                    "end_time": round(w_end, 4),
                    "duration": round(w_end - w_start, 4),
                    "peak_speed_cms": round(w_peak, 2),
                    "peak_time": round(w_peak_sample["time"], 4),
                    "sample_count": len(current_window_samples)
                })
            current_window_samples = []

    if len(current_window_samples) >= min_samples:
        w_start = current_window_samples[0]["time"]
        w_end = current_window_samples[-1]["time"]
        w_peak = max(cs["tip_speed"] for cs in current_window_samples)
        w_peak_sample = next(cs for cs in current_window_samples if cs["tip_speed"] == w_peak)
        windows.append({
            "start_time": round(w_start, 4),
            "end_time": round(w_end, 4),
            "duration": round(w_end - w_start, 4),
            "peak_speed_cms": round(w_peak, 2),
            "peak_time": round(w_peak_sample["time"], 4),
            "sample_count": len(current_window_samples)
        })

    windows.sort(key=lambda w: w["peak_speed_cms"], reverse=True)
    return windows


def resolve_world_space_enum(unreal_module: Any) -> Any:
    """Resolve EAnimPoseSpaces::World enum value from unreal reflection."""
    if hasattr(unreal_module, "AnimPoseSpaces"):
        enum_cls = getattr(unreal_module, "AnimPoseSpaces")
        if hasattr(enum_cls, "WORLD"):
            return getattr(enum_cls, "WORLD")
        if hasattr(enum_cls, "World"):
            return getattr(enum_cls, "World")
    return 1


def check_bone_track_presence(unreal_module: Any, seq_asset: Any, bone_names: List[str]) -> Dict[str, bool]:
    """Check if sequence asset contains an explicit animation track for each bone."""
    track_names = set()
    if hasattr(unreal_module, "AnimationBlueprintLibrary"):
        lib = unreal_module.AnimationBlueprintLibrary
        if hasattr(lib, "get_animation_track_names"):
            try:
                tracks = lib.get_animation_track_names(seq_asset)
                track_names = set(str(t) for t in tracks)
            except Exception:
                pass
    if not track_names and hasattr(seq_asset, "get_data_model"):
        try:
            model = seq_asset.get_data_model()
            if hasattr(model, "get_bone_track_names"):
                track_names = set(str(t) for t in model.get_bone_track_names())
        except Exception:
            pass

    return {b: (b in track_names) for b in bone_names}


def evaluate_pose_at_time(
    unreal_module: Any,
    seq_asset: Any,
    time: float
) -> Tuple[Any, str]:
    """
    Evaluate FAnimPose at time using UAnimPoseExtensions.
    Returns (pose_instance, method_used_name).
    """
    eval_opts = None
    if hasattr(unreal_module, "AnimPoseEvaluationOptions"):
        eval_opts = unreal_module.AnimPoseEvaluationOptions()
        if hasattr(eval_opts, "b_should_retarget"):
            eval_opts.b_should_retarget = True
        if hasattr(eval_opts, "b_incorporate_root_motion_into_pose"):
            eval_opts.b_incorporate_root_motion_into_pose = True

    if hasattr(unreal_module, "AnimPoseExtensions"):
        ext = unreal_module.AnimPoseExtensions
        if hasattr(ext, "get_anim_pose_at_time"):
            try:
                pose = ext.get_anim_pose_at_time(seq_asset, time, eval_opts)
                return pose, "AnimPoseExtensions.get_anim_pose_at_time"
            except TypeError:
                if hasattr(unreal_module, "AnimPose"):
                    pose = unreal_module.AnimPose()
                    ext.get_anim_pose_at_time(seq_asset, time, eval_opts, pose)
                    return pose, "AnimPoseExtensions.get_anim_pose_at_time(with_out_param)"

    if hasattr(seq_asset, "get_anim_pose_at_time"):
        pose = seq_asset.get_anim_pose_at_time(time, eval_opts)
        return pose, "AnimSequence.get_anim_pose_at_time"

    raise RuntimeError("UNKNOWN: Could not find working get_anim_pose_at_time reflection binding")


def get_bone_transform_component_space(
    unreal_module: Any,
    pose: Any,
    bone_name: str
) -> Tuple[Tuple[float, float, float], str]:
    """
    Extract bone transform in World/Component space from FAnimPose.
    Returns ((x, y, z), method_used_name).
    """
    world_space_enum = resolve_world_space_enum(unreal_module)

    if hasattr(pose, "get_bone_pose"):
        try:
            t = pose.get_bone_pose(bone_name, world_space_enum)
            return (float(t.translation.x), float(t.translation.y), float(t.translation.z)), "AnimPose.get_bone_pose(WORLD)"
        except Exception:
            pass

    if hasattr(unreal_module, "AnimPoseExtensions"):
        ext = unreal_module.AnimPoseExtensions
        if hasattr(ext, "get_bone_pose"):
            try:
                t = ext.get_bone_pose(pose, bone_name, world_space_enum)
                return (float(t.translation.x), float(t.translation.y), float(t.translation.z)), "AnimPoseExtensions.get_bone_pose(WORLD)"
            except Exception:
                pass

    raise RuntimeError(f"UNKNOWN: Could not resolve component-space GetBonePose for '{bone_name}'")


def sample_sequence_motion(
    unreal_module: Any,
    sequence_path: str,
    base_bone: str = DEFAULT_BASE_BONE,
    tip_bone: str = DEFAULT_TIP_BONE,
    dt: float = DEFAULT_DT
) -> Dict[str, Any]:
    """
    Sample bone positions in Component/World space and compute velocities across an AnimSequence.
    Compatible with unreal module or a mock module.
    """
    seq_asset = None
    if hasattr(unreal_module, "EditorAssetLibrary"):
        seq_asset = unreal_module.EditorAssetLibrary.load_asset(sequence_path)
    elif hasattr(unreal_module, "load_asset"):
        seq_asset = unreal_module.load_asset(sequence_path)

    if not seq_asset:
        raise ValueError(f"Failed to load animation asset at '{sequence_path}'")

    seq_len = 0.0
    if hasattr(unreal_module, "AnimationBlueprintLibrary"):
        lib = unreal_module.AnimationBlueprintLibrary
        if hasattr(lib, "get_sequence_length"):
            seq_len = float(lib.get_sequence_length(seq_asset))
    if seq_len <= 0.0 and hasattr(seq_asset, "get_editor_property"):
        seq_len = float(seq_asset.get_editor_property("sequence_length"))
    if seq_len <= 0.0:
        raise ValueError(f"Failed to retrieve valid sequence length for '{sequence_path}'")

    tracks = check_bone_track_presence(unreal_module, seq_asset, [base_bone, tip_bone])

    samples = []
    num_steps = int(math.ceil(seq_len / dt)) + 1
    prev_base = None
    prev_tip = None
    pose_method_used = None
    bone_method_used = None

    for i in range(num_steps):
        t = min(i * dt, seq_len)

        pose, p_method = evaluate_pose_at_time(unreal_module, seq_asset, t)
        pose_method_used = p_method

        base_pos, b_method = get_bone_transform_component_space(unreal_module, pose, base_bone)
        tip_pos, _ = get_bone_transform_component_space(unreal_module, pose, tip_bone)
        bone_method_used = b_method

        base_spd = 0.0
        tip_spd = 0.0
        if prev_base is not None and prev_tip is not None and dt > 0.0:
            base_spd = compute_speed(prev_base, base_pos, dt)
            tip_spd = compute_speed(prev_tip, tip_pos, dt)

        samples.append({
            "step": i,
            "time": round(t, 5),
            "base_pos": base_pos,
            "tip_pos": tip_pos,
            "base_speed": round(base_spd, 2),
            "tip_speed": round(tip_spd, 2)
        })

        prev_base = base_pos
        prev_tip = tip_pos

    peak_tip_spd = max(s["tip_speed"] for s in samples) if samples else 0.0
    peak_sample = next((s for s in samples if s["tip_speed"] == peak_tip_spd), None)
    peak_time = peak_sample["time"] if peak_sample else 0.0

    windows = extract_active_windows(samples, threshold_ratio=0.5)

    return {
        "sequence_path": sequence_path,
        "sequence_name": os.path.basename(sequence_path),
        "sequence_length": round(seq_len, 4),
        "sampling_dt": round(dt, 6),
        "sample_count": len(samples),
        "base_bone": base_bone,
        "tip_bone": tip_bone,
        "base_bone_has_track": tracks.get(base_bone, False),
        "tip_bone_has_track": tracks.get(tip_bone, False),
        "pose_eval_method": pose_method_used or "UNKNOWN",
        "bone_pose_method": bone_method_used or "UNKNOWN",
        "peak_tip_speed_cms": round(peak_tip_spd, 2),
        "peak_tip_time": round(peak_time, 4),
        "active_windows_50pct": windows,
        "samples": samples
    }


def run_probe(
    sequence_paths: Optional[List[str]] = None,
    base_bone: str = DEFAULT_BASE_BONE,
    tip_bone: str = DEFAULT_TIP_BONE,
    dt: float = DEFAULT_DT,
    output_json_path: Optional[str] = None
) -> int:
    """Execution entry point running inside Unreal Engine."""
    try:
        import unreal
    except ImportError:
        print("[PROBE_ERROR] 'unreal' Python module not available. Must run inside UE editor.")
        return 1

    targets = sequence_paths if sequence_paths else DEFAULT_SEVAROG_SEQUENCES
    results = []

    print("================================================================================")
    print(" SEVAROG WEAPON MOTION & HIT-WINDOW EXTRACTION PROBE (A-243)")
    print(" Space: EAnimPoseSpaces::World (Component Space, AnimPose.h:35)")
    print(f" Sampling Rate: {1.0 / dt:.1f} Hz (dt={dt:.6f}s)")
    print(f" Bones: Base='{base_bone}', Tip='{tip_bone}'")
    print(f" Sequences Count: {len(targets)}")
    print("================================================================================")

    for seq_path in targets:
        seq_name = os.path.basename(seq_path)
        print(f"\n[PROBE_START] sequence='{seq_name}' path='{seq_path}'")
        try:
            res = sample_sequence_motion(
                unreal,
                seq_path,
                base_bone=base_bone,
                tip_bone=tip_bone,
                dt=dt
            )
            results.append(res)

            print(f"[PROBE_API] pose_method='{res['pose_eval_method']}' bone_method='{res['bone_pose_method']}'")
            print(f"[PROBE_TRACKS] base_track({base_bone})={res['base_bone_has_track']} "
                  f"tip_track({tip_bone})={res['tip_bone_has_track']}")
            print(f"[PROBE_METRICS] length={res['sequence_length']}s samples={res['sample_count']} "
                  f"peak_tip_speed={res['peak_tip_speed_cms']} cm/s at t={res['peak_tip_time']}s")

            for idx, win in enumerate(res["active_windows_50pct"]):
                print(f"[PROBE_WINDOW] #{idx+1}: [{win['start_time']}s -> {win['end_time']}s] "
                      f"(duration={win['duration']}s, peak={win['peak_speed_cms']} cm/s at t={win['peak_time']}s)")

            top_samples = sorted(res["samples"], key=lambda s: s["tip_speed"], reverse=True)[:5]
            for ts in top_samples:
                print(f"  [TOP_SAMPLE] t={ts['time']:0.4f}s tip_spd={ts['tip_speed']:8.1f} cm/s "
                      f"base_spd={ts['base_speed']:8.1f} cm/s tip_pos={ts['tip_pos']}")

            print(f"[PROBE_END] sequence='{seq_name}' status=SUCCESS")
        except Exception as e:
            print(f"[PROBE_ERROR] sequence='{seq_name}' failed: {e}")

    if output_json_path:
        out_dir = os.path.dirname(os.path.abspath(output_json_path))
        os.makedirs(out_dir, exist_ok=True)
        summary_data = []
        for r in results:
            summary_data.append({
                "sequence_path": r["sequence_path"],
                "sequence_name": r["sequence_name"],
                "sequence_length": r["sequence_length"],
                "sampling_dt": r["sampling_dt"],
                "sample_count": r["sample_count"],
                "base_bone": r["base_bone"],
                "tip_bone": r["tip_bone"],
                "base_bone_has_track": r["base_bone_has_track"],
                "tip_bone_has_track": r["tip_bone_has_track"],
                "pose_eval_method": r["pose_eval_method"],
                "bone_pose_method": r["bone_pose_method"],
                "peak_tip_speed_cms": r["peak_tip_speed_cms"],
                "peak_tip_time": r["peak_tip_time"],
                "active_windows_50pct": r["active_windows_50pct"]
            })
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2)
        print(f"\n[PROBE_OUTPUT] Summary written to '{output_json_path}'")

    print("\n================================================================================")
    print(f" PROBE FINISHED: {len(results)} of {len(targets)} sequences sampled successfully.")
    print("================================================================================")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Probe weapon motion for Sevarog attack sequences.")
    parser.add_argument("--sequences", nargs="*", default=None, help="Sequence paths to analyze.")
    parser.add_argument("--base-bone", default=DEFAULT_BASE_BONE, help="Base bone name.")
    parser.add_argument("--tip-bone", default=DEFAULT_TIP_BONE, help="Tip bone name.")
    parser.add_argument("--dt", type=float, default=DEFAULT_DT, help="Sampling delta time.")
    parser.add_argument("--output-json", default=None, help="Optional output JSON summary path.")
    args = parser.parse_args()

    sys.exit(run_probe(
        sequence_paths=args.sequences,
        base_bone=args.base_bone,
        tip_bone=args.tip_bone,
        dt=args.dt,
        output_json_path=args.output_json
    ))


if __name__ == "__main__":
    main()
