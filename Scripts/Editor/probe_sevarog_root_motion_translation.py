"""
Read-only probe measuring root-bone (and pelvis) translation over the length of targeted Sevarog animation sequences.

Authority: Claude Lead Directive [C-1240] / C-1240a (2026-11-10).
Purpose:
  Determine whether targeted Paragon Sevarog sequences contain actual root-bone displacement
  (enabling Option (a): enabling root motion on duplicated project copies)
  or whether root bone is stationary at origin while locomotion is in-place
  (enabling Option (b): reusable data-driven move displacement add-on module).

Targeted Sequences:
  - Speedburst
  - Swing3_Slow
  - Ultimate_Swing_120fps
  - Subjugation
  - Swing1_Medium

Discipline:
  - Strictly read-only; saves zero assets.
  - Fail-safe: all Unreal API calls are guarded and print 'n/a' on failure.
  - Confirmed 5.5 API: unreal.AnimationLibrary.get_bone_pose_for_time(asset, bone_name, time, extract_root_motion).
"""

import math
import unreal

AL = getattr(unreal, "AnimationLibrary", None)
SEVAROG_ROOT = "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations"

TARGET_SEQUENCES = [
    "Speedburst",
    "Swing3_Slow",
    "Ultimate_Swing_120fps",
    "Subjugation",
    "Swing1_Medium",
]


def log(msg):
    unreal.log(f"[SevarogRootProbe] {msg}")


def sample_bone_transform(asset, bone_name, time_sec):
    """Samples bone transform at given time using AnimationLibrary.get_bone_pose_for_time."""
    if AL is None:
        return None, "n/a (AnimationLibrary missing)"
    if not hasattr(AL, "get_bone_pose_for_time"):
        return None, "n/a (get_bone_pose_for_time missing)"

    try:
        tr = AL.get_bone_pose_for_time(asset, bone_name, float(time_sec), False)
        return tr, None
    except Exception as ex:
        return None, f"n/a ({type(ex).__name__}: {ex})"


def format_vec(v):
    if v is None:
        return "n/a"
    return f"({v.x:.2f}, {v.y:.2f}, {v.z:.2f})"


def probe_sequence_root_translation(seq_name):
    path = f"{SEVAROG_ROOT}/{seq_name}"
    s = unreal.EditorAssetLibrary.load_asset(path)
    if s is None:
        log(f"SEQUENCE {seq_name}: MISSING at {path}")
        return

    try:
        length = float(s.get_play_length())
    except Exception as ex:
        log(f"SEQUENCE {seq_name}: play_length=n/a ({type(ex).__name__})")
        return

    # Check tracks if available
    track_names = []
    if AL is not None and hasattr(AL, "get_animation_track_names"):
        try:
            track_names = list(AL.get_animation_track_names(s))
        except Exception:
            track_names = []

    has_root = "root" in track_names if track_names else True
    has_pelvis = "pelvis" in track_names if track_names else True

    # Sample root bone at t=0.0 and t=length
    tr_root_0, err_root_0 = sample_bone_transform(s, "root", 0.0)
    tr_root_end, err_root_end = sample_bone_transform(s, "root", length)

    # Sample pelvis bone at t=0.0 and t=length for diagnostic reference
    tr_pelvis_0, err_pelvis_0 = sample_bone_transform(s, "pelvis", 0.0)
    tr_pelvis_end, err_pelvis_end = sample_bone_transform(s, "pelvis", length)

    # Calculate root delta
    if tr_root_0 is not None and tr_root_end is not None:
        t0 = tr_root_0.translation
        tEnd = tr_root_end.translation
        dx = tEnd.x - t0.x
        dy = tEnd.y - t0.y
        dz = tEnd.z - t0.z
        dist_2d = math.sqrt(dx * dx + dy * dy)
        dist_3d = math.sqrt(dx * dx + dy * dy + dz * dz)
        root_summary = (
            f"root_t0={format_vec(t0)} root_tEnd={format_vec(tEnd)} "
            f"delta=({dx:.2f}, {dy:.2f}, {dz:.2f}) dist_2d={dist_2d:.2f}cm dist_3d={dist_3d:.2f}cm"
        )
    else:
        root_summary = f"root=n/a (t0:{err_root_0}, tEnd:{err_root_end})"

    # Calculate pelvis delta
    if tr_pelvis_0 is not None and tr_pelvis_end is not None:
        p0 = tr_pelvis_0.translation
        pEnd = tr_pelvis_end.translation
        pdx = pEnd.x - p0.x
        pdy = pEnd.y - p0.y
        pdz = pEnd.z - p0.z
        p_dist_2d = math.sqrt(pdx * pdx + pdy * pdy)
        p_dist_3d = math.sqrt(pdx * pdx + pdy * pdy + pdz * pdz)
        pelvis_summary = (
            f"pelvis_t0={format_vec(p0)} pelvis_tEnd={format_vec(pEnd)} "
            f"pelvis_delta=({pdx:.2f}, {pdy:.2f}, {pdz:.2f}) pelvis_dist_2d={p_dist_2d:.2f}cm"
        )
    else:
        pelvis_summary = f"pelvis=n/a (t0:{err_pelvis_0}, tEnd:{err_pelvis_end})"

    log(
        f"SEQUENCE {seq_name}: length={length:.6f}s "
        f"tracks_checked={len(track_names)} (has_root={has_root}, has_pelvis={has_pelvis}) | "
        f"{root_summary} | {pelvis_summary}"
    )


def main():
    log("Starting read-only Sevarog root-bone translation probe (C-1240a)...")
    if AL is None or not hasattr(AL, "get_bone_pose_for_time"):
        log("WARNING: unreal.AnimationLibrary.get_bone_pose_for_time not available in this environment")

    for seq in TARGET_SEQUENCES:
        probe_sequence_root_translation(seq)

    log("Sevarog root-bone translation probe complete.")


if __name__ == "__main__":
    main()
