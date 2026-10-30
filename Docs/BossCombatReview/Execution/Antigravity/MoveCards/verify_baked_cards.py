#!/usr/bin/env python3
"""
verify_baked_cards.py
=====================
Unreal Engine Editor Python synchronous verifier for MoveCard baked blade paths
(Orders A-310 / A-312 / C-427).

Evaluates live AnimPose in Component (WORLD) space at 3 critical timestamps:
  1. Window Start (first sample)
  2. Apex Sample (minimum BaseCS.X for forward thrusts / maximum forward Tip reach)
  3. Window End (last sample)
Compares live socket translations (SocketA, SocketB) against stored BakedSamples.

Emits structured [BAKE_CHECK] log lines per card/window with PASS/FAIL.
Default drift tolerance: 2.0 cm (design value, proposed).
Exits non-zero (exit code 1) with [BAKE_FATAL] if any drift exceeds tolerance,
or if a window required by --require-baked has empty BakedSamples.

Execution Modes:
1. Editor Mode (default):
   - Scans /Game/OneBossFight/FrameworkProof/Cards/ for URPGBossMoveCard assets.
   - Evaluates live AnimSequence via unreal reflection (read-only on assets).
2. JSON / Standalone Mode (--card-json):
   - Inspects JSON card file for offline CI / test workflows.
3. Safe Tamper Check (--test-tamper-apex <delta_cm>):
   - Injects a synthetic delta at the apex check in memory without modifying assets on disk.
   - Proves fail-closed detection live in engine.
"""

import sys
import os
import math
import json
import argparse
from typing import List, Dict, Any, Tuple, Optional

DEFAULT_CARDS_PACKAGE_DIR = "/Game/OneBossFight/FrameworkProof/Cards"
DEFAULT_TOLERANCE_CM = 2.0


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


def find_apex_sample_index(samples: List[Dict[str, Any]]) -> int:
    """
    Identifies the apex sample in a window using maximum forward (+Y) reach of TipCS,
    or maximum tip speed (inter-sample displacement / dt).
    Restricts search to interior samples [1 .. n-2] so apex does not duplicate Start/End.
    """
    if not samples:
        return 0
    n = len(samples)
    if n <= 2:
        return 0

    interior_indices = list(range(1, n - 1))

    # Priority 1: Maximum forward (+Y) distance of TipCS
    best_y_idx = max(interior_indices, key=lambda i: samples[i]["TipCS"][1])
    tip_y_range = max(samples[i]["TipCS"][1] for i in interior_indices) - min(samples[i]["TipCS"][1] for i in interior_indices)

    if tip_y_range > 1.0:
        return best_y_idx

    # Priority 2: Maximum tip velocity relative to adjacent samples
    def tip_speed(i: int) -> float:
        prev_s = samples[i - 1]
        curr_s = samples[i]
        dt = max(1e-5, curr_s["TimeSeconds"] - prev_s["TimeSeconds"])
        dist = math.sqrt(sum((c - p) ** 2 for c, p in zip(curr_s["TipCS"], prev_s["TipCS"])))
        return dist / dt

    return max(interior_indices, key=tip_speed)


def extract_sample_data(raw_sample: Any) -> Dict[str, Any]:
    """Normalizes sample from either UObject property or JSON dict."""
    if isinstance(raw_sample, dict):
        return {
            "TimeSeconds": float(raw_sample["TimeSeconds"]),
            "BaseCS": [float(v) for v in raw_sample["BaseCS"]],
            "TipCS": [float(v) for v in raw_sample["TipCS"]]
        }
    # UObject (RPGBakedBladeSample)
    t_sec = float(raw_sample.get_editor_property("time_seconds"))
    b_vec = raw_sample.get_editor_property("base_cs")
    t_vec = raw_sample.get_editor_property("tip_cs")
    return {
        "TimeSeconds": t_sec,
        "BaseCS": [float(b_vec.x), float(b_vec.y), float(b_vec.z)],
        "TipCS": [float(t_vec.x), float(t_vec.y), float(t_vec.z)]
    }


def verify_card_window_spot_checks(
    unreal_mod: Any,
    seq_asset: Any,
    move_id: str,
    window_data: Dict[str, Any],
    tolerance_cm: float = DEFAULT_TOLERANCE_CM,
    tamper_delta_cm: float = 0.0
) -> Tuple[bool, List[str]]:
    """
    Executes live AnimPose spot-checks at Start, Apex, and End.
    Returns (all_passed, log_lines).
    """
    logs = []
    win_id = window_data.get("WindowId", "Window_Unknown")
    sock_a = window_data.get("SocketA", "weapon_r")
    sock_b = window_data.get("SocketB", "root_weapon_end_r")
    raw_samples = window_data.get("BakedSamples", [])

    if not raw_samples:
        logs.append(f"[BAKE_CHECK] MoveId={move_id} WindowId={win_id} Status=SKIP Reason='No baked samples'")
        return True, logs

    samples = [extract_sample_data(s) for s in raw_samples]
    if len(samples) < 2:
        logs.append(f"[BAKE_CHECK] MoveId={move_id} WindowId={win_id} Status=FAIL Error='Insufficient samples ({len(samples)} < 2)'")
        return False, logs

    # Always evaluate 4 checkpoints: Start (0), Mid (n // 2), Apex (max +Y reach / speed), End (n - 1)
    mid_idx = len(samples) // 2
    apex_idx = find_apex_sample_index(samples)
    checkpoints = [
        ("Start", 0),
        ("Mid", mid_idx),
        ("Apex", apex_idx),
        ("End", len(samples) - 1)
    ]

    all_passed = True

    for check_name, s_idx in checkpoints:
        s = samples[s_idx]
        t = s["TimeSeconds"]

        # Evaluate live pose
        pose = evaluate_pose_at_time(unreal_mod, seq_asset, t)
        base_live = get_bone_translation(unreal_mod, pose, sock_a)
        tip_live = get_bone_translation(unreal_mod, pose, sock_b)

        # In-memory tamper check injection (applied to forward +Y axis of TipCS)
        if check_name == "Apex" and abs(tamper_delta_cm) > 1e-4:
            tip_live = (tip_live[0], tip_live[1] + tamper_delta_cm, tip_live[2])

        base_drift = math.sqrt(sum((l - b) ** 2 for l, b in zip(base_live, s["BaseCS"])))
        tip_drift = math.sqrt(sum((l - b) ** 2 for l, b in zip(tip_live, s["TipCS"])))
        max_drift = max(base_drift, tip_drift)

        passed = max_drift <= tolerance_cm
        status_str = "PASS" if passed else "FAIL"

        log_msg = (
            f"[BAKE_CHECK] MoveId={move_id} WindowId={win_id} Check={check_name} SampleIdx={s_idx} "
            f"Time={t:.4f}s BaseDriftCm={base_drift:.3f} TipDriftCm={tip_drift:.3f} "
            f"MaxDriftCm={max_drift:.3f} ToleranceCm={tolerance_cm:.1f} Status={status_str}"
        )
        logs.append(log_msg)

        if not passed:
            all_passed = False
            logs.append(
                f"[BAKE_FATAL] Stale baked path detected for MoveId='{move_id}' Window='{win_id}' Check='{check_name}': "
                f"drift {max_drift:.3f} cm exceeds tolerance {tolerance_cm:.1f} cm."
            )

    return all_passed, logs


def run_verification(
    unreal_mod: Optional[Any] = None,
    package_dir: str = DEFAULT_CARDS_PACKAGE_DIR,
    card_json_path: Optional[str] = None,
    require_baked_moves: Optional[List[str]] = None,
    tolerance_cm: float = DEFAULT_TOLERANCE_CM,
    tamper_delta_cm: float = 0.0,
    only_move: Optional[str] = None
) -> Tuple[bool, List[str]]:
    """
    Orchestrates live AnimPose spot-checks across all cards.
    Returns (success, log_lines).
    """
    logs = []
    require_set = set(require_baked_moves or [])
    checked_moves = set()
    total_checks = 0
    total_failures = 0

    if not unreal_mod:
        try:
            import unreal  # type: ignore
            unreal_mod = unreal
        except ImportError:
            logs.append("[BAKE_FATAL] Unreal engine module not available.")
            return False, logs

    cards_to_check = []

    if card_json_path:
        # Load from JSON file (offline / fixture mode)
        if not os.path.isfile(card_json_path):
            logs.append(f"[BAKE_FATAL] Card JSON file not found: '{card_json_path}'")
            return False, logs
        with open(card_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cards = data.get("cards", [data]) if isinstance(data, dict) else data
        for c in cards:
            cards_to_check.append({
                "MoveId": c.get("MoveId", "UnknownMove"),
                "Sequence": c.get("Sequence") or c.get("Montage"),
                "Windows": c.get("Windows", [])
            })
    else:
        # Live Unreal Asset Discovery
        editor_asset_lib = getattr(unreal_mod, "EditorAssetLibrary", None)
        if not editor_asset_lib:
            logs.append("[BAKE_FATAL] unreal.EditorAssetLibrary not found.")
            return False, logs

        asset_paths = editor_asset_lib.list_assets(package_dir, recursive=False)
        if not asset_paths:
            logs.append(f"[BAKE_WARN] No assets found under package directory '{package_dir}'.")

        for a_path in asset_paths:
            asset = editor_asset_lib.load_asset(a_path)
            if not asset or not hasattr(asset, "get_editor_property"):
                continue
            try:
                spec = asset.get_editor_property("spec")
            except Exception:
                continue

            move_id = str(spec.get_editor_property("move_id"))
            seq_obj = None
            try:
                seq_obj = spec.get_editor_property("sequence")
            except Exception:
                pass
            if not seq_obj:
                try:
                    seq_obj = spec.get_editor_property("montage")
                except Exception:
                    pass

            raw_wins = list(spec.get_editor_property("windows"))
            win_data = []
            for w in raw_wins:
                w_id = str(w.get_editor_property("window_id"))
                s_a = str(w.get_editor_property("socket_a"))
                s_b = str(w.get_editor_property("socket_b"))
                b_samples = list(w.get_editor_property("baked_samples")) if hasattr(w, "baked_samples") or hasattr(w, "get_editor_property") else []
                win_data.append({
                    "WindowId": w_id,
                    "SocketA": s_a,
                    "SocketB": s_b,
                    "BakedSamples": b_samples
                })

            cards_to_check.append({
                "MoveId": move_id,
                "SequenceAsset": seq_obj,
                "Windows": win_data
            })

    if only_move:
        cards_to_check = [c for c in cards_to_check if c["MoveId"] == only_move]

    logs.append(f"[BAKE_VERIFY] Starting live spot-check across {len(cards_to_check)} card(s). Tolerance={tolerance_cm:.1f} cm.")

    for c in cards_to_check:
        move_id = c["MoveId"]
        checked_moves.add(move_id)
        windows = c.get("Windows", [])

        # Check --require-baked requirement
        if move_id in require_set:
            has_baked = any(len(w.get("BakedSamples", [])) > 0 for w in windows)
            if not has_baked:
                logs.append(f"[BAKE_FATAL] MoveId='{move_id}' has NO baked samples but is listed in --require-baked.")
                total_failures += 1
                continue

        # Load Sequence asset if in JSON mode
        seq_asset = c.get("SequenceAsset")
        if not seq_asset:
            seq_path = c.get("Sequence")
            if not seq_path:
                logs.append(f"[BAKE_WARN] MoveId='{move_id}' has no Sequence asset assigned. Skipping.")
                continue
            editor_asset_lib = getattr(unreal_mod, "EditorAssetLibrary", None)
            if editor_asset_lib:
                seq_asset = editor_asset_lib.load_asset(seq_path)

        if not seq_asset:
            logs.append(f"[BAKE_FATAL] MoveId='{move_id}' unable to load sequence asset.")
            total_failures += 1
            continue

        for w in windows:
            if w.get("BakedSamples"):
                total_checks += 1
            ok, check_logs = verify_card_window_spot_checks(
                unreal_mod=unreal_mod,
                seq_asset=seq_asset,
                move_id=move_id,
                window_data=w,
                tolerance_cm=tolerance_cm,
                tamper_delta_cm=tamper_delta_cm
            )
            logs.extend(check_logs)
            if not ok:
                total_failures += 1

    # Check if any required moves were completely missing
    missing_required = require_set - checked_moves
    if missing_required:
        for m in missing_required:
            logs.append(f"[BAKE_FATAL] Required baked card '{m}' was not found in package directory.")
            total_failures += 1

    success = (total_failures == 0)
    if success:
        logs.append(f"[BAKE_SUMMARY] PASS: {total_checks} window(s) verified within {tolerance_cm:.1f} cm live pose tolerance (0 errors).")
    else:
        logs.append(f"[BAKE_SUMMARY] FAIL: {total_failures} failure(s) detected during baked blade path spot-check.")

    return success, logs


def main():
    parser = argparse.ArgumentParser(description="Live AnimPose spot-check verifier for baked MoveCards.")
    parser.add_argument("--package-dir", default=DEFAULT_CARDS_PACKAGE_DIR, help="Package path containing card assets.")
    parser.add_argument("--card-json", default=None, help="Optional card JSON path for offline inspection.")
    parser.add_argument("--require-baked", default=None, help="Comma-separated MoveIds that must have non-empty baked samples.")
    parser.add_argument("--tolerance-cm", type=float, default=DEFAULT_TOLERANCE_CM, help="Maximum allowed drift in cm (default: 2.0).")
    parser.add_argument("--only-move", default=None, help="Filter to specific MoveId.")
    parser.add_argument("--test-tamper-apex", type=float, default=0.0, help="In-memory test drift (cm) injected into apex check to test failure path.")
    args = parser.parse_args()

    req_moves = [m.strip() for m in args.require_baked.split(",")] if args.require_baked else None

    success, logs = run_verification(
        package_dir=args.package_dir,
        card_json_path=args.card_json,
        require_baked_moves=req_moves,
        tolerance_cm=args.tolerance_cm,
        tamper_delta_cm=args.test_tamper_apex,
        only_move=args.only_move
    )

    for line in logs:
        print(line)

    if not success:
        # Note: Consumers running under Unreal's -ExecutePythonScript must grep for '[BAKE_FATAL]'
        # because the editor process wrapper may report exit code 0 even after sys.exit(1).
        # We explicitly raise RuntimeError so the editor engine log surfaces a full Python traceback error line.
        raise RuntimeError("Baked blade path verification failed with [BAKE_FATAL]. See log above for details.")

    sys.exit(0)


if __name__ == "__main__":
    main()
