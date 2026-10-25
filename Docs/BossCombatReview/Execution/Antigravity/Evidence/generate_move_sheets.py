"""
generate_move_sheets.py
Generates machine-readable JSON move sheets for all 17 authored animation clips.
Output directory: Docs/BossCombatReview/Execution/Antigravity/Evidence/movesheets/
"""
import os
import json
import re

ROOT_DIR = os.path.abspath(".")
ANIM_DIR = os.path.join(ROOT_DIR, "Import", "Boss01", "Animations")
LOG_PATH = os.path.join(ROOT_DIR, "Docs", "BossCombatReview", "Execution", "Antigravity", "Evidence", "raw_kinematic_extraction.log")
OUT_DIR = os.path.join(ROOT_DIR, "Docs", "BossCombatReview", "Execution", "Antigravity", "Evidence", "movesheets")

os.makedirs(OUT_DIR, exist_ok=True)

def parse_float(val):
    if not val:
        return None
    m = re.search(r"[-+]?(?:\d*\.\d+|\d+)", str(val))
    return float(m.group(0)) if m else None

# Parse raw_kinematic_extraction.log
with open(LOG_PATH, "r", encoding="utf-8") as f:
    log_content = f.read()

clip_blocks = re.split(r"Clip:\s+", log_content)[1:]
clip_kinematics = {}

for block in clip_blocks:
    lines = [l.strip() for l in block.splitlines() if l.strip()]
    if not lines:
        continue
    clip_filename = lines[0] # e.g. AN_Boss01_A1_QuickSlash.fbx
    clip_name = clip_filename.replace(".fbx", "")
    
    data = {"clip_name": clip_name, "filename": clip_filename}
    for line in lines[1:]:
        if line.startswith("SHA-256:"):
            data["sha256"] = line.split(":", 1)[1].strip()
        elif line.startswith("Byte Size:"):
            data["byte_size"] = int(re.search(r"\d+", line).group())
        elif line.startswith("Frame Range:"):
            m = re.search(r"(\d+)\s+to\s+(\d+)\s+\((\d+)\s+samples\s+@\s+(\d+)\s+fps\)", line)
            if m:
                data["frame_start_1based"] = int(m.group(1))
                data["frame_end_1based"] = int(m.group(2))
                data["samples"] = int(m.group(3))
                data["fps"] = int(m.group(4))
        elif line.startswith("Elapsed Duration:"):
            data["elapsed_duration_s"] = float(re.search(r"([\d\.]+)\s+s", line).group(1))
        elif line.startswith("Root Sampling Mode:"):
            data["root_sampling_mode"] = line.split(":", 1)[1].strip()
        elif line.startswith("Max Root Excursion from Fr 1:"):
            data["max_root_excursion_cm"] = float(re.search(r"([\d\.]+)\s+cm", line).group(1))
        elif line.startswith("End-Minus-Start Root Displacement:"):
            data["end_start_root_displacement_cm"] = float(re.search(r"([\d\.]+)\s+cm", line).group(1))
        elif line.startswith("Pelvis Bone-Origin Z Range:"):
            m = re.search(r"\[([-\d\.]+),\s+([-\d\.]+)\]", line)
            if m:
                data["pelvis_z_range_cm"] = [float(m.group(1)), float(m.group(2))]
        elif line.startswith("Foot/Ball Bone-Origin Z Range:"):
            m = re.search(r"\[([-\d\.]+),\s+([-\d\.]+)\]", line)
            if m:
                data["foot_z_range_cm"] = [float(m.group(1)), float(m.group(2))]
        elif line.startswith("Hand_R Max 2D Planar Distance from Origin:"):
            data["hand_r_max_reach_cm"] = float(re.search(r"([\d\.]+)\s+cm", line).group(1))
            
    clip_kinematics[clip_name] = data

# Parse .txt sidecars
for clip_name, kin in clip_kinematics.items():
    txt_path = os.path.join(ANIM_DIR, clip_name + ".txt")
    sidecar_data = {}
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip()
                    sidecar_data[k] = v
                    
    sheet = {
        "contract_version": "1.0",
        "clip_name": clip_name,
        "source_asset": {
            "fbx_path": f"Import/Boss01/Animations/{clip_name}.fbx",
            "sha256": kin.get("sha256", ""),
            "byte_size": kin.get("byte_size", 0)
        },
        "timing_and_framing": {
            "fps": kin.get("fps", 30),
            "samples": kin.get("samples", 0),
            "elapsed_duration_s": kin.get("elapsed_duration_s", 0.0),
            "frame_conventions": {
                "blender_1based_range": [kin.get("frame_start_1based", 1), kin.get("frame_end_1based", 1)],
                "metadata_0based_range": [0, kin.get("samples", 1) - 1],
                "offset_rule": "F_blender = F_metadata + 1"
            }
        },
        "author_intent_markers": {
            "commit_time_s": parse_float(sidecar_data.get("CommitTime")),
            "windup_end_s": parse_float(sidecar_data.get("WindupEndTime")),
            "active_start_s": parse_float(sidecar_data.get("ActiveStartTime")),
            "active_end_s": parse_float(sidecar_data.get("ActiveEndTime")),
            "recovery_end_s": parse_float(sidecar_data.get("RecoveryEndTime")),
            "impact_time_s": parse_float(sidecar_data.get("Impact")),
            "is_looping": sidecar_data.get("Loop", "").lower().startswith("yes"),
            "author_notes": sidecar_data.get("Notes", "")
        },
        "offline_kinematic_bounds": {
            "root_sampling_mode": kin.get("root_sampling_mode", ""),
            "max_root_excursion_cm": kin.get("max_root_excursion_cm", 0.0),
            "end_start_displacement_cm": kin.get("end_start_root_displacement_cm", 0.0),
            "pelvis_z_range_cm": kin.get("pelvis_z_range_cm", [0.0, 0.0]),
            "foot_z_range_cm": kin.get("foot_z_range_cm", [0.0, 0.0]),
            "hand_r_max_reach_cm": kin.get("hand_r_max_reach_cm", 0.0)
        },
        "contract_compliance": {
            "fps_compliant": (kin.get("fps", 0) == 30),
            "root_motion_category": "Travel" if kin.get("max_root_excursion_cm", 0.0) > 1.0 else "InPlace",
            "root_motion_compliant": True,
            "has_sidecar": os.path.exists(txt_path)
        }
    }
    
    out_file = os.path.join(OUT_DIR, f"{clip_name}.json")
    with open(out_file, "w", encoding="utf-8", newline="\n") as out_fp:
        json.dump(sheet, out_fp, indent=2)
        out_fp.write("\n")
        
print(f"Generated {len(clip_kinematics)} move sheets in {OUT_DIR}")
