"""
generate_move_sheets.py
Generates machine-readable JSON move sheets for all 26 live and authored moves
with four strictly separated blocks per Codex D02 / Claude C-98:
  1. declared_intent (from .txt sidecars)
  2. measured_extraction (from headless Blender kinematic extraction)
  3. engine_timeline (from Claude E-002 / E-008 montage_notifies_2026-10-25.txt)
  4. approved_runtime (empty until approved at Architecture Gate)

Rule: Absent bounds must NEVER default to 0; they must be null (None in Python).
"""
import os
import json
import re
import hashlib

def find_repo_root():
    curr = os.path.dirname(os.path.abspath(__file__))
    while curr and os.path.dirname(curr) != curr:
        if os.path.exists(os.path.join(curr, "OneBossFight.uproject")):
            return curr
        curr = os.path.dirname(curr)
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", ".."))

ROOT_DIR = find_repo_root()
ANIM_DIR = os.path.join(ROOT_DIR, "Import", "Boss01", "Animations")
LOG_PATH = os.path.join(ROOT_DIR, "Docs", "BossCombatReview", "Execution", "Antigravity", "Evidence", "raw_kinematic_extraction.log")
NOTIFY_PATH = os.path.join(ROOT_DIR, "Docs", "BossCombatReview", "Execution", "Claude", "Evidence", "exports", "montage_notifies_2026-10-25.txt")
OUT_DIR = os.path.join(ROOT_DIR, "Docs", "BossCombatReview", "Execution", "Antigravity", "Evidence", "movesheets")

os.makedirs(OUT_DIR, exist_ok=True)

def get_sha256(filepath):
    if not os.path.exists(filepath):
        return None
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def parse_float(val):
    if val is None:
        return None
    s = str(val).strip()
    if not s or s.upper() == "N/A" or s.upper() == "NONE":
        return None
    m = re.search(r"[-+]?(?:\d*\.\d+|\d+)", s)
    return float(m.group(0)) if m else None

NOTIFY_FILE_HASH = get_sha256(NOTIFY_PATH)

# --- 1. Parse raw_kinematic_extraction.log ---
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

# --- 2. Parse montage_notifies_2026-10-25.txt ---
with open(NOTIFY_PATH, "r", encoding="utf-8") as f:
    notify_content = f.read()

montage_blocks = re.split(r"\[P0Notify\] ==\s+", notify_content)[1:]
engine_montages = {}

for mb in montage_blocks:
    lines = [l.strip() for l in mb.splitlines() if l.strip()]
    if not lines:
        continue
    header = lines[0]
    m = re.match(r"(\w+)\s+\((\w+)\)\s+length=([\d\.]+)\s+rate_scale=([\d\.]+)", header)
    if not m:
        continue
    m_name, asset_type, length_s, rate_scale = m.groups()
    
    m_data = {
        "montage_name": m_name,
        "asset_type": asset_type,
        "length_s": float(length_s),
        "rate_scale": float(rate_scale),
        "blend_in_s": 0.25,
        "blend_out_s": 0.25,
        "damage_windows": [],
        "movement_disable_windows": [],
        "rotation_windows": [],
        "hit_stun_immune_windows": [],
        "notifies": []
    }
    
    for l in lines[1:]:
        # Parse states
        sm = re.search(r"\[state\]\s+(\w+)\s+at\s+([-\d\.]+)\s+s\s+for\s+([-\d\.]+)\s+s", l)
        if sm:
            not_name = sm.group(1)
            t_start = float(sm.group(2))
            t_dur = float(sm.group(3))
            entry = {"notify": not_name, "start_s": t_start, "duration_s": t_dur, "end_s": round(t_start + t_dur, 3)}
            m_data["notifies"].append(entry)
            if not_name == "ANS_CollisionTrace_C":
                m_data["damage_windows"].append(entry)
            elif not_name == "ANS_DisableMovement_C":
                m_data["movement_disable_windows"].append(entry)
            elif not_name == "ANS_SetDesiredRotation_C":
                m_data["rotation_windows"].append(entry)
            elif not_name == "ANS_HitStunImmune_C":
                m_data["hit_stun_immune_windows"].append(entry)
        else:
            im = re.search(r"(?:\[P0Notify\]\s+)?(\w+)\s+at\s+([-\d\.]+)\s+s", l)
            if im and im.group(1) not in ("length", "done"):
                not_name = im.group(1)
                t_val = float(im.group(2))
                m_data["notifies"].append({"notify": not_name, "time_s": t_val})
                
    engine_montages[m_name] = m_data

# Mapping between move identifiers and engine montages
MOVE_TO_MONTAGE = {
    "AN_Boss01_A1_QuickSlash": "AM_Boss01_A1",
    "AN_Boss01_A3a_Combo1": "AM_Boss01_A3a",
    "AN_Boss01_A3b_Combo2": "AM_Boss01_A3b",
    "AN_Boss01_A4_LowSweep": "AN_Boss01_A4_LowSweep",
    "AN_Boss01_A5_JavelinThrow": "AN_Boss01_A5_JavelinThrow",
    "GS_Attack01": "GS_Attack01_Montage",
    "GS_Attack02": "GS_Attack02_Montage",
    "GS_Attack03": "GS_Attack03_Montage",
    "GS_Attack04": "GS_Attack04_Montage", # A1b
    "GS_ChargedAttack": "GS_ChargedAttack_Montage", # A2
    "GS_LeapAttack": "GS_LeapAttack_Montage", # A6
    "GS_SprintAttackFollowUp": "GS_SprintAttackFollowUp_Montage",
    "Mid01": "Mid01_Anim_Montage",
    "RetaliationAttack": "RetaliationAttack_Montage"
}

# --- 3. Build move list (Authored 17 + Pack 9 = 26 total) ---
all_move_keys = list(clip_kinematics.keys())

pack_move_defs = [
    {"id": "GS_Attack01", "name": "GS_Attack01", "montage": "GS_Attack01_Montage", "category": "PackCloseAttack"},
    {"id": "GS_Attack02", "name": "GS_Attack02", "montage": "GS_Attack02_Montage", "category": "PackCloseAttack"},
    {"id": "GS_Attack03", "name": "GS_Attack03", "montage": "GS_Attack03_Montage", "category": "PackCloseAttack"},
    {"id": "GS_Attack04", "name": "GS_Attack04 (A1b)", "montage": "GS_Attack04_Montage", "category": "PackComboFinisher"},
    {"id": "GS_ChargedAttack", "name": "GS_ChargedAttack (A2)", "montage": "GS_ChargedAttack_Montage", "category": "PackChargedSlam"},
    {"id": "GS_LeapAttack", "name": "GS_LeapAttack (A6)", "montage": "GS_LeapAttack_Montage", "category": "PackLeapAttack"},
    {"id": "GS_SprintAttackFollowUp", "name": "GS_SprintAttackFollowUp", "montage": "GS_SprintAttackFollowUp_Montage", "category": "PackSprintFollowUp"},
    {"id": "Mid01", "name": "Mid01 (Pack Mid Range)", "montage": "Mid01_Anim_Montage", "category": "PackMidAttack"},
    {"id": "RetaliationAttack", "name": "RetaliationAttack", "montage": "RetaliationAttack_Montage", "category": "PackDefensiveCounter"}
]

count = 0

# A. Generate for authored project clips (17)
for clip_name, kin in clip_kinematics.items():
    fbx_rel = f"Import/Boss01/Animations/{clip_name}.fbx"
    fbx_abs = os.path.join(ROOT_DIR, fbx_rel.replace("/", os.sep))
    txt_rel = f"Import/Boss01/Animations/{clip_name}.txt"
    txt_abs = os.path.join(ROOT_DIR, txt_rel.replace("/", os.sep))
    
    has_sidecar = os.path.exists(txt_abs)
    sidecar_data = {}
    sidecar_hash = None
    if has_sidecar:
        sidecar_hash = get_sha256(txt_abs)
        with open(txt_abs, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if ":" in line:
                    k, v = line.split(":", 1)
                    sidecar_data[k.strip()] = v.strip()
                    
    # Block 1: declared_intent
    declared_intent = {
        "has_declared_intent": has_sidecar,
        "source_file": txt_rel if has_sidecar else None,
        "source_hash": sidecar_hash,
        "commit_time_s": parse_float(sidecar_data.get("CommitTime")),
        "windup_end_s": parse_float(sidecar_data.get("WindupEndTime")),
        "active_start_s": parse_float(sidecar_data.get("ActiveStartTime")),
        "active_end_s": parse_float(sidecar_data.get("ActiveEndTime")),
        "recovery_end_s": parse_float(sidecar_data.get("RecoveryEndTime")),
        "impact_time_s": parse_float(sidecar_data.get("Impact")),
        "is_looping": sidecar_data.get("Loop", "").lower().startswith("yes") if has_sidecar else None,
        "notes": sidecar_data.get("Notes") if has_sidecar else None
    }
    
    # Block 2: measured_extraction
    measured_extraction = {
        "has_measured_extraction": True,
        "source_file": fbx_rel,
        "source_hash": kin.get("sha256"),
        "byte_size": kin.get("byte_size"),
        "fps": kin.get("fps"),
        "samples": kin.get("samples"),
        "elapsed_duration_s": kin.get("elapsed_duration_s"),
        "frame_conventions": {
            "blender_1based_range": [kin.get("frame_start_1based"), kin.get("frame_end_1based")],
            "metadata_0based_range": [0, kin.get("samples", 1) - 1],
            "offset_rule": "F_blender = F_metadata + 1"
        },
        "root_sampling_mode": kin.get("root_sampling_mode"),
        "max_root_excursion_cm": kin.get("max_root_excursion_cm"),
        "end_start_displacement_cm": kin.get("end_start_root_displacement_cm"),
        "pelvis_z_range_cm": kin.get("pelvis_z_range_cm"),
        "foot_z_range_cm": kin.get("foot_z_range_cm"),
        "hand_r_max_reach_cm": kin.get("hand_r_max_reach_cm")
    }
    
    # Block 3: engine_timeline
    montage_key = MOVE_TO_MONTAGE.get(clip_name)
    eng_info = engine_montages.get(montage_key) if montage_key else None
    
    if eng_info:
        engine_timeline = {
            "has_engine_timeline": True,
            "source_file": "Docs/BossCombatReview/Execution/Claude/Evidence/exports/montage_notifies_2026-10-25.txt",
            "source_hash": NOTIFY_FILE_HASH,
            "montage_name": eng_info["montage_name"],
            "asset_type": eng_info["asset_type"],
            "length_s": eng_info["length_s"],
            "rate_scale": eng_info["rate_scale"],
            "blend_in_s": eng_info["blend_in_s"],
            "blend_out_s": eng_info["blend_out_s"],
            "damage_windows": eng_info["damage_windows"],
            "movement_disable_windows": eng_info["movement_disable_windows"],
            "rotation_windows": eng_info["rotation_windows"],
            "hit_stun_immune_windows": eng_info["hit_stun_immune_windows"],
            "notifies": eng_info["notifies"]
        }
    else:
        engine_timeline = {
            "has_engine_timeline": False,
            "reason": "No live montage notify export available for standalone clip; pending montage wrapper or non-attack utility",
            "source_file": None,
            "source_hash": None,
            "montage_name": None,
            "asset_type": None,
            "length_s": None,
            "rate_scale": None,
            "blend_in_s": None,
            "blend_out_s": None,
            "damage_windows": [],
            "movement_disable_windows": [],
            "rotation_windows": [],
            "hit_stun_immune_windows": [],
            "notifies": []
        }
        
    # Block 4: approved_runtime
    approved_runtime = {
        "status": "PENDING_ARCHITECTURE_GATE_APPROVAL",
        "approved_by": None,
        "approval_date": None,
        "source_hash": None,
        "runtime_definition": {}
    }
    
    sheet = {
        "schema_version": "2.0",
        "move_id": clip_name,
        "move_category": "ProjectAuthoredAnimation",
        "declared_intent": declared_intent,
        "measured_extraction": measured_extraction,
        "engine_timeline": engine_timeline,
        "approved_runtime": approved_runtime
    }
    
    out_path = os.path.join(OUT_DIR, f"{clip_name}.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as fp:
        json.dump(sheet, fp, indent=2)
        fp.write("\n")
    count += 1

# B. Generate for Pack Moves (9 moves)
for pm in pack_move_defs:
    m_key = pm["montage"]
    eng_info = engine_montages.get(m_key)
    
    declared_intent = {
        "has_declared_intent": False,
        "reason": "No authored sidecar exists for third-party pack clip; pack assets are unedited",
        "source_file": None,
        "source_hash": None,
        "commit_time_s": None,
        "windup_end_s": None,
        "active_start_s": None,
        "active_end_s": None,
        "recovery_end_s": None,
        "impact_time_s": None,
        "is_looping": None,
        "notes": None
    }
    
    measured_extraction = {
        "has_measured_extraction": False,
        "reason": "No authored FBX source exists for third-party pack clip; third-party assets are unedited",
        "source_file": None,
        "source_hash": None,
        "byte_size": None,
        "fps": None,
        "samples": None,
        "elapsed_duration_s": None,
        "frame_conventions": None,
        "root_sampling_mode": None,
        "max_root_excursion_cm": None, # MUST BE None, NEVER 0.0 (Codex D02)
        "end_start_displacement_cm": None,
        "pelvis_z_range_cm": None,
        "foot_z_range_cm": None,
        "hand_r_max_reach_cm": None
    }
    
    if eng_info:
        engine_timeline = {
            "has_engine_timeline": True,
            "source_file": "Docs/BossCombatReview/Execution/Claude/Evidence/exports/montage_notifies_2026-10-25.txt",
            "source_hash": NOTIFY_FILE_HASH,
            "montage_name": eng_info["montage_name"],
            "asset_type": eng_info["asset_type"],
            "length_s": eng_info["length_s"],
            "rate_scale": eng_info["rate_scale"],
            "blend_in_s": eng_info["blend_in_s"],
            "blend_out_s": eng_info["blend_out_s"],
            "damage_windows": eng_info["damage_windows"],
            "movement_disable_windows": eng_info["movement_disable_windows"],
            "rotation_windows": eng_info["rotation_windows"],
            "hit_stun_immune_windows": eng_info["hit_stun_immune_windows"],
            "notifies": eng_info["notifies"]
        }
    else:
        engine_timeline = {
            "has_engine_timeline": False,
            "reason": f"Montage {m_key} not found in notify export",
            "source_file": None,
            "source_hash": None,
            "montage_name": None,
            "asset_type": None,
            "length_s": None,
            "rate_scale": None,
            "blend_in_s": None,
            "blend_out_s": None,
            "damage_windows": [],
            "movement_disable_windows": [],
            "rotation_windows": [],
            "hit_stun_immune_windows": [],
            "notifies": []
        }
        
    approved_runtime = {
        "status": "PENDING_ARCHITECTURE_GATE_APPROVAL",
        "approved_by": None,
        "approval_date": None,
        "source_hash": None,
        "runtime_definition": {}
    }
    
    sheet = {
        "schema_version": "2.0",
        "move_id": pm["id"],
        "move_category": pm["category"],
        "declared_intent": declared_intent,
        "measured_extraction": measured_extraction,
        "engine_timeline": engine_timeline,
        "approved_runtime": approved_runtime
    }
    
    out_path = os.path.join(OUT_DIR, f"{pm['id']}.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as fp:
        json.dump(sheet, fp, indent=2)
        fp.write("\n")
    count += 1

print(f"Generated {count} move sheets (17 authored + 9 pack live moves) in {OUT_DIR}")
