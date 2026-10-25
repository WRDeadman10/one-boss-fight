"""
validate_move_sheets.py
Validates all machine-readable move sheets against the Authoring Contract and on-disk files.
"""
import os
import json
import hashlib

ROOT_DIR = os.path.abspath(".")
SHEETS_DIR = os.path.join(ROOT_DIR, "Docs", "BossCombatReview", "Execution", "Antigravity", "Evidence", "movesheets")

def get_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

files = [f for f in os.listdir(SHEETS_DIR) if f.endswith(".json")]
print(f"Validating {len(files)} move sheets against AUTHORING_CONTRACT.md...")

passed = 0
failed = 0

for fname in sorted(files):
    sheet_path = os.path.join(SHEETS_DIR, fname)
    with open(sheet_path, "r", encoding="utf-8") as fp:
        try:
            sheet = json.load(fp)
        except Exception as e:
            print(f"[FAIL] {fname}: Invalid JSON ({e})")
            failed += 1
            continue

    clip_name = sheet.get("clip_name")
    fbx_rel_path = sheet.get("source_asset", {}).get("fbx_path")
    fbx_abs_path = os.path.join(ROOT_DIR, fbx_rel_path.replace("/", os.sep))
    
    errors = []
    
    # 1. File existence & hash check
    if not os.path.exists(fbx_abs_path):
        errors.append(f"Source FBX missing: {fbx_abs_path}")
    else:
        disk_sha = get_sha256(fbx_abs_path)
        sheet_sha = sheet["source_asset"].get("sha256")
        if disk_sha != sheet_sha:
            errors.append(f"SHA-256 mismatch: disk={disk_sha[:12]} vs sheet={sheet_sha[:12]}")
            
        disk_sz = os.path.getsize(fbx_abs_path)
        sheet_sz = sheet["source_asset"].get("byte_size")
        if disk_sz != sheet_sz:
            errors.append(f"Byte size mismatch: disk={disk_sz} vs sheet={sheet_sz}")
            
    # 2. Timing & Framing
    fps = sheet.get("timing_and_framing", {}).get("fps")
    if fps != 30:
        errors.append(f"Non-compliant FPS: {fps} (expected 30)")
        
    samples = sheet.get("timing_and_framing", {}).get("samples", 0)
    dur = sheet.get("timing_and_framing", {}).get("elapsed_duration_s", 0.0)
    expected_dur = round((samples - 1) / 30.0, 3)
    if round(dur, 3) != expected_dur:
        errors.append(f"Elapsed duration mismatch: sheet={dur} vs expected={expected_dur}")
        
    # 3. Root motion compliance
    root_exc = sheet.get("offline_kinematic_bounds", {}).get("max_root_excursion_cm", 0.0)
    if clip_name == "AN_Riposte_Player_Front":
        if abs(root_exc - 90.0) > 0.01:
            errors.append(f"Player riposte expected 90.00 cm travel, got {root_exc}")
    else:
        if root_exc != 0.0:
            errors.append(f"Boss move non-zero root excursion: {root_exc} (expected 0.0000 in-place)")
            
    # 4. Conventions check
    offset_rule = sheet.get("timing_and_framing", {}).get("frame_conventions", {}).get("offset_rule")
    if offset_rule != "F_blender = F_metadata + 1":
        errors.append("Invalid frame offset convention")
        
    if errors:
        print(f"[FAIL] {fname}: {', '.join(errors)}")
        failed += 1
    else:
        print(f"[PASS] {fname} ({samples} smp, {dur:.3f} s, root={root_exc:.2f} cm)")
        passed += 1

print(f"\nValidation Summary: {passed} PASSED, {failed} FAILED across {len(files)} move sheets.")
if failed > 0:
    exit(1)
