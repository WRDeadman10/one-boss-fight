#!/usr/bin/env python3
"""
probe_reach.py
Synchronous read-only Unreal Engine editor Python probe for Sevarog attack reach.
Extracts component-space forward reach (+Y), lateral spread (X), and vertical range (Z)
for weapon_r (base) and root_weapon_end_r (tip) across candidate attack animations.

Modelled on probe_weapon_motion.py and Claude/F3b/probe_sevarog_mesh.py.
Uses accepted AnimPose WORLD (Component) API at 1/120s sampling rate.
Emits structured [REACH_*] log lines and writes a JSON summary.
"""

import sys
import os
import math
import json
import argparse
from typing import List, Dict, Any, Tuple, Optional

# Default sequence assets in ParagonSevarog
DEFAULT_SEQUENCES = [
    "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Slow",
    "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Medium",
    "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing2_Medium",
    "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing3_Slow",
    "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_FAST_v2",
    "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Speedburst",
]

# Proposed active windows [ActiveStartSeconds, ActiveEndSeconds]
PROPOSED_ACTIVE_WINDOWS = {
    "Swing1_Slow": [0.3500, 0.4917],
    "Swing1_Medium": [0.1500, 0.2667],
    "Swing2_Medium": [0.1917, 0.2667],
    "Swing3_Slow": [0.4750, 0.5333],
    "Swing1_FAST_v2": [0.1500, 0.3000],
    "Speedburst": [0.3000, 0.6000],
}

def resolve_world_space_enum(unreal_module: Any) -> Any:
    """Resolve EAnimPoseSpaces::World enum value from unreal reflection."""
    if hasattr(unreal_module, "AnimPoseSpaces"):
        enum_cls = getattr(unreal_module, "AnimPoseSpaces")
        if hasattr(enum_cls, "WORLD"):
            return getattr(enum_cls, "WORLD")
        if hasattr(enum_cls, "World"):
            return getattr(enum_cls, "World")
    return 1

def evaluate_pose_at_time(unreal_module: Any, seq_asset: Any, time: float) -> Any:
    """Evaluate FAnimPose at time using AnimPoseExtensions."""
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
                return ext.get_anim_pose_at_time(seq_asset, time, eval_opts)
            except TypeError:
                if hasattr(unreal_module, "AnimPose"):
                    pose = unreal_module.AnimPose()
                    ext.get_anim_pose_at_time(seq_asset, time, eval_opts, pose)
                    return pose

    if hasattr(seq_asset, "get_anim_pose_at_time"):
        return seq_asset.get_anim_pose_at_time(time, eval_opts)

    raise RuntimeError("Could not find working get_anim_pose_at_time reflection binding")

def get_bone_translation(unreal_module: Any, pose: Any, bone_name: str) -> Tuple[float, float, float]:
    """Extract component-space bone translation (x, y, z) from pose."""
    world_space = resolve_world_space_enum(unreal_module)
    if hasattr(pose, "get_bone_pose"):
        try:
            t = pose.get_bone_pose(bone_name, world_space)
            return (float(t.translation.x), float(t.translation.y), float(t.translation.z))
        except Exception:
            pass

    if hasattr(unreal_module, "AnimPoseExtensions"):
        ext = unreal_module.AnimPoseExtensions
        if hasattr(ext, "get_bone_pose"):
            try:
                t = ext.get_bone_pose(pose, bone_name, world_space)
                return (float(t.translation.x), float(t.translation.y), float(t.translation.z))
            except Exception:
                pass

    raise RuntimeError(f"Could not resolve component-space GetBonePose for '{bone_name}'")

def log_reach(unreal_module: Optional[Any], tag: str, payload: Any):
    """Log structured line with [REACH_*] tag."""
    msg = f"[REACH_{tag}] {json.dumps(payload, default=str)}"
    if unreal_module and hasattr(unreal_module, "log"):
        unreal_module.log(msg)
    else:
        print(msg)

def analyze_reach_samples(
    samples: List[Dict[str, Any]],
    active_window: Tuple[float, float]
) -> Dict[str, Any]:
    """
    Analyze time-series pose samples.
    Sevarog component space coordinate convention:
      Forward = +Y (depth toward target)
      Lateral = X (right +X, left -X)
      Vertical = Z (up +Z, down -Z)
    """
    if not samples:
        raise ValueError("Cannot analyze empty sample set")

    # Find max forward (+Y) for tip
    max_tip_sample = max(samples, key=lambda s: s["tip_rel"][1])
    # Find max forward (+Y) for base
    max_base_sample = max(samples, key=lambda s: s["base_rel"][1])

    w_start, w_end = active_window
    window_samples = [s for s in samples if w_start <= s["time"] <= w_end]

    # If window samples empty due to step boundary, fallback to closest
    if not window_samples:
        window_samples = [min(samples, key=lambda s: abs(s["time"] - w_start))]

    # For swept segment [base, tip], the envelope at any instant is bounded by base and tip
    w_min_y = min(min(s["base_rel"][1], s["tip_rel"][1]) for s in window_samples)
    w_max_y = max(max(s["base_rel"][1], s["tip_rel"][1]) for s in window_samples)
    w_min_x = min(min(s["base_rel"][0], s["tip_rel"][0]) for s in window_samples)
    w_max_x = max(max(s["base_rel"][0], s["tip_rel"][0]) for s in window_samples)
    w_min_z = min(min(s["base_rel"][2], s["tip_rel"][2]) for s in window_samples)
    w_max_z = max(max(s["base_rel"][2], s["tip_rel"][2]) for s in window_samples)

    return {
        "max_tip_forward": {
            "time": round(max_tip_sample["time"], 4),
            "forward_y": round(max_tip_sample["tip_rel"][1], 2),
            "lateral_x": round(max_tip_sample["tip_rel"][0], 2),
            "vertical_z": round(max_tip_sample["tip_rel"][2], 2),
        },
        "max_base_forward": {
            "time": round(max_base_sample["time"], 4),
            "forward_y": round(max_base_sample["base_rel"][1], 2),
            "lateral_x": round(max_base_sample["base_rel"][0], 2),
            "vertical_z": round(max_base_sample["base_rel"][2], 2),
        },
        "active_window_swept_envelope": {
            "window": [round(w_start, 4), round(w_end, 4)],
            "sample_count": len(window_samples),
            "forward_y_range": [round(w_min_y, 2), round(w_max_y, 2)],
            "lateral_x_range": [round(w_min_x, 2), round(w_max_x, 2)],
            "vertical_z_range": [round(w_min_z, 2), round(w_max_z, 2)],
            "peak_forward_in_window": round(w_max_y, 2),
            "lateral_half_width": round(max(abs(w_min_x), abs(w_max_x)), 2)
        }
    }

def probe_sequence(
    unreal_module: Any,
    seq_path: str,
    dt: float = 1.0 / 120.0
) -> Optional[Dict[str, Any]]:
    """Probe a single animation sequence asset."""
    seq_name = os.path.splitext(os.path.basename(seq_path))[0]
    
    seq_asset = None
    if hasattr(unreal_module, "load_asset"):
        seq_asset = unreal_module.load_asset(seq_path)

    if not seq_asset:
        log_reach(unreal_module, "WARNING", {"missing_asset": seq_path})
        return None

    seq_len = 0.0
    if hasattr(seq_asset, "get_editor_property"):
        seq_len = float(seq_asset.get_editor_property("sequence_length"))
    elif hasattr(seq_asset, "sequence_length"):
        seq_len = float(seq_asset.sequence_length)

    num_steps = int(math.ceil(seq_len / dt)) + 1
    log_reach(unreal_module, "SEQUENCE", {
        "sequence": seq_name,
        "path": seq_path,
        "length_seconds": round(seq_len, 4),
        "dt": round(dt, 6),
        "expected_steps": num_steps
    })

    samples = []
    for step in range(num_steps):
        t = min(step * dt, seq_len)
        try:
            pose = evaluate_pose_at_time(unreal_module, seq_asset, t)
            root_loc = get_bone_translation(unreal_module, pose, "root")
            base_loc = get_bone_translation(unreal_module, pose, "weapon_r")
            tip_loc = get_bone_translation(unreal_module, pose, "root_weapon_end_r")

            # Compute positions relative to root
            base_rel = (base_loc[0] - root_loc[0], base_loc[1] - root_loc[1], base_loc[2] - root_loc[2])
            tip_rel = (tip_loc[0] - root_loc[0], tip_loc[1] - root_loc[1], tip_loc[2] - root_loc[2])

            samples.append({
                "time": t,
                "base_rel": base_rel,
                "tip_rel": tip_rel
            })
        except Exception as e:
            log_reach(unreal_module, "ERROR", {"time": t, "error": str(e)})

    # Determine active window
    w_default = PROPOSED_ACTIVE_WINDOWS.get(seq_name, [seq_len * 0.25, seq_len * 0.50])
    analysis = analyze_reach_samples(samples, (w_default[0], w_default[1]))

    result = {
        "sequence_name": seq_name,
        "sequence_path": seq_path,
        "length_seconds": round(seq_len, 4),
        "sample_count": len(samples),
        **analysis
    }

    log_reach(unreal_module, "MAX_FORWARD", {
        "sequence": seq_name,
        "tip": analysis["max_tip_forward"],
        "base": analysis["max_base_forward"]
    })
    log_reach(unreal_module, "ACTIVE_WINDOW", {
        "sequence": seq_name,
        "envelope": analysis["active_window_swept_envelope"]
    })

    return result

def run_probe(
    unreal_module: Any,
    sequences: List[str] = DEFAULT_SEQUENCES,
    output_path: Optional[str] = None,
    dt: float = 1.0 / 120.0
) -> Dict[str, Any]:
    """Main probe entry point."""
    log_reach(unreal_module, "START", {
        "sequence_count": len(sequences),
        "dt": round(dt, 6),
        "coordinate_convention": "+Y forward, X lateral, +Z vertical"
    })

    results = []
    for seq_path in sequences:
        res = probe_sequence(unreal_module, seq_path, dt=dt)
        if res:
            results.append(res)

    summary = {
        "status": "SUCCESS",
        "probe_target": "Sevarog Weapon Reach",
        "coordinate_convention": "Component space: +Y forward, X lateral, +Z vertical",
        "measured_sequences": results
    }

    log_reach(unreal_module, "SUMMARY", {
        "successful_probes": len(results),
        "total_requested": len(sequences)
    })

    if output_path:
        out_p = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(out_p), exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        log_reach(unreal_module, "OUTPUT_SAVED", {"path": out_p})

    return summary

def main():
    parser = argparse.ArgumentParser(description="Sevarog Weapon Reach Probe")
    parser.add_argument("--output", type=str, default=None, help="Output JSON path")
    parser.add_argument("--dt", type=float, default=1.0 / 120.0, help="Sampling delta time (default 1/120s)")
    args = parser.parse_args()

    try:
        import unreal
    except ImportError:
        print("[REACH_ERROR] Unreal Engine python module not found. Run inside Unreal Editor.")
        sys.exit(1)

    run_probe(unreal, DEFAULT_SEQUENCES, output_path=args.output, dt=args.dt)

if __name__ == "__main__":
    main()
