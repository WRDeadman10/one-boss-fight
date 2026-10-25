"""
validate_move_sheets.py
Validates all machine-readable move sheets against Authoring Contract (Revision 03),
Codex D02 4-block architecture, and on-disk source files.

Tolerances and Thresholds Enforced:
-----------------------------------
1. FPS:
   - FPS_EXPECTED = 30 (exact integer match required).
2. Duration vs Sample Count:
   - DURATION_ROUNDING_TOLERANCE_S = 0.001 s (rounding tolerance for 30 fps sample intervals).
   - Rule: |elapsed_duration_s - round((samples - 1) / 30.0, 3)| <= 0.001 s.
3. Cross-Block Timing Discrepancies (Codex D02 / Claude C-98 Diagnostics):
   - ACTIVE_WINDOW_START_TOLERANCE_S = 0.050 s (50 ms threshold).
   - ACTIVE_WINDOW_END_TOLERANCE_S   = 0.050 s (50 ms threshold).
   - HEADING_COMMIT_TOLERANCE_S      = 0.050 s (50 ms threshold).
   - MONTAGE_DURATION_TOLERANCE_S    = 0.050 s (50 ms threshold).
   - Rule: Disagreements exceeding 0.050 s between declared intent, measured extraction,
     and engine timeline are recorded as architectural diagnostics.
4. Absent Kinematic Bounds (Codex D02 Strict Mandate):
   - ABSENT_BOUND_STRICT_NULL = True.
   - Rule: When has_measured_extraction is False (e.g. unauthored pack moves),
     bounds (max_root_excursion_cm, pelvis_z_range_cm, foot_z_range_cm, hand_r_max_reach_cm)
     MUST be null/None. Defaulting an absent bound to 0 or 0.0 is strictly REJECTED.
5. Kinematic Root Excursion for Boss Duel Moves:
   - BOSS_ROOT_EXCURSION_MAX_CM = 0.0000 cm (strict in-place motion).
   - PLAYER_RIPOSTE_ROOT_EXCURSION_CM = 90.00 cm (+/- 0.01 cm travel).
6. Source File Integrity:
   - Exact byte-for-byte SHA-256 match against on-disk files; exact byte size match.
"""
import os
import sys
import json
import hashlib
import copy

def find_repo_root():
    curr = os.path.dirname(os.path.abspath(__file__))
    while curr and os.path.dirname(curr) != curr:
        if os.path.exists(os.path.join(curr, "OneBossFight.uproject")):
            return curr
        curr = os.path.dirname(curr)
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", ".."))

ROOT_DIR = find_repo_root()
SHEETS_DIR = os.path.join(ROOT_DIR, "Docs", "BossCombatReview", "Execution", "Antigravity", "Evidence", "movesheets")

# --- Stated Tolerances ---
FPS_EXPECTED = 30
DURATION_ROUNDING_TOLERANCE_S = 0.001
ACTIVE_WINDOW_START_TOLERANCE_S = 0.050
ACTIVE_WINDOW_END_TOLERANCE_S = 0.050
HEADING_COMMIT_TOLERANCE_S = 0.050
MONTAGE_DURATION_TOLERANCE_S = 0.050
BOSS_ROOT_EXCURSION_MAX_CM = 0.0000
PLAYER_RIPOSTE_ROOT_EXCURSION_CM = 90.00

def get_sha256(filepath):
    if not os.path.exists(filepath):
        return None
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def validate_move_sheet(sheet, root_dir=ROOT_DIR):
    """
    Validates a single move sheet dictionary.
    Returns: (errors: list[str], diagnostics: list[str])
    """
    errors = []
    diagnostics = []
    
    schema_ver = sheet.get("schema_version")
    if schema_ver != "2.0":
        errors.append(f"Invalid schema version: {schema_ver} (expected '2.0')")
        
    for req_block in ("declared_intent", "measured_extraction", "engine_timeline", "approved_runtime"):
        if req_block not in sheet:
            errors.append(f"Missing required block: '{req_block}'")
            
    if errors:
        return errors, diagnostics
        
    dec = sheet["declared_intent"]
    meas = sheet["measured_extraction"]
    eng = sheet["engine_timeline"]
    app = sheet["approved_runtime"]
    clip_name = sheet.get("move_id", "")
    
    # 1. Declared Intent Block
    if dec.get("has_declared_intent"):
        s_file = dec.get("source_file")
        s_hash = dec.get("source_hash")
        if not s_file or not s_hash:
            errors.append("Declared intent true but missing source_file or source_hash")
        else:
            abs_s = os.path.join(root_dir, s_file.replace("/", os.sep))
            if not os.path.exists(abs_s):
                errors.append(f"Declared intent source file missing: {s_file}")
            else:
                disk_h = get_sha256(abs_s)
                if disk_h != s_hash:
                    errors.append(f"Declared intent SHA mismatch: disk={disk_h[:12]} vs sheet={s_hash[:12]}")
    else:
        if dec.get("source_file") is not None or dec.get("source_hash") is not None:
            errors.append("Declared intent false but source_file/source_hash is not null")
            
    # 2. Measured Extraction Block
    if meas.get("has_measured_extraction"):
        m_file = meas.get("source_file")
        m_hash = meas.get("source_hash")
        if not m_file or not m_hash:
            errors.append("Measured extraction true but missing source_file or source_hash")
        else:
            abs_m = os.path.join(root_dir, m_file.replace("/", os.sep))
            if not os.path.exists(abs_m):
                errors.append(f"Measured extraction source FBX missing: {m_file}")
            else:
                disk_mh = get_sha256(abs_m)
                if disk_mh != m_hash:
                    errors.append(f"Measured FBX SHA mismatch: disk={disk_mh[:12]} vs sheet={m_hash[:12]}")
                disk_sz = os.path.getsize(abs_m)
                if disk_sz != meas.get("byte_size"):
                    errors.append(f"Byte size mismatch: disk={disk_sz} vs sheet={meas.get('byte_size')}")
                    
        fps = meas.get("fps")
        if fps != FPS_EXPECTED:
            errors.append(f"Measured FPS not {FPS_EXPECTED}: got {fps}")
            
        samples = meas.get("samples", 0)
        dur = meas.get("elapsed_duration_s", 0.0)
        expected_dur = round((samples - 1) / float(FPS_EXPECTED), 3)
        if abs(round(dur, 3) - expected_dur) > DURATION_ROUNDING_TOLERANCE_S:
            errors.append(f"Duration calculation mismatch: {dur} s vs expected {expected_dur} s")
            
        conv = meas.get("frame_conventions", {})
        if conv.get("offset_rule") != "F_blender = F_metadata + 1":
            errors.append("Invalid frame offset rule")
            
        # Root motion check
        root_exc = meas.get("max_root_excursion_cm")
        if root_exc is not None:
            if clip_name == "AN_Riposte_Player_Front":
                if abs(root_exc - PLAYER_RIPOSTE_ROOT_EXCURSION_CM) > 0.01:
                    errors.append(f"Player riposte expected {PLAYER_RIPOSTE_ROOT_EXCURSION_CM} cm travel, got {root_exc}")
            else:
                if root_exc > BOSS_ROOT_EXCURSION_MAX_CM:
                    errors.append(f"Boss move non-zero root excursion: {root_exc} cm (expected {BOSS_ROOT_EXCURSION_MAX_CM} in-place)")
    else:
        # CODEX D02 MANDATE: Absent bounds must NEVER default to 0; they must be null
        for field in ("max_root_excursion_cm", "end_start_displacement_cm", "pelvis_z_range_cm", "foot_z_range_cm", "hand_r_max_reach_cm"):
            val = meas.get(field)
            if val is not None:
                errors.append(f"Codex D02 Violation: absent bound '{field}' is {val} instead of null")
                
    # 3. Engine Timeline Block
    if eng.get("has_engine_timeline"):
        e_file = eng.get("source_file")
        e_hash = eng.get("source_hash")
        if not e_file or not e_hash:
            errors.append("Engine timeline true but missing source_file or source_hash")
        else:
            abs_e = os.path.join(root_dir, e_file.replace("/", os.sep))
            if not os.path.exists(abs_e):
                errors.append(f"Engine timeline source file missing: {e_file}")
            else:
                disk_eh = get_sha256(abs_e)
                if disk_eh != e_hash:
                    errors.append(f"Engine timeline SHA mismatch: disk={disk_eh[:12]} vs sheet={e_hash[:12]}")
        if not eng.get("montage_name"):
            errors.append("Missing engine montage_name")
        if not eng.get("length_s") or eng.get("length_s") <= 0:
            errors.append(f"Invalid engine length_s: {eng.get('length_s')}")
            
    # 4. Approved Runtime Block
    if app.get("status") != "PENDING_ARCHITECTURE_GATE_APPROVAL":
        errors.append(f"Approved runtime status must be 'PENDING_ARCHITECTURE_GATE_APPROVAL', got '{app.get('status')}'")
        
    # 5. Cross-Block Disagreement Diagnostics (Codex D02 / Claude C-98)
    if dec.get("has_declared_intent") and eng.get("has_engine_timeline"):
        dec_start = dec.get("active_start_s")
        dec_end = dec.get("active_end_s")
        dmg_windows = eng.get("damage_windows", [])
        if dmg_windows:
            eng_start = dmg_windows[0].get("start_s")
            eng_end = dmg_windows[0].get("end_s")
            if dec_start is not None:
                diff_s = abs(dec_start - eng_start)
                if diff_s > ACTIVE_WINDOW_START_TOLERANCE_S:
                    diagnostics.append(f"DIAGNOSTIC: Active window start mismatch (declared={dec_start:.3f}s vs engine={eng_start:.3f}s, delta={diff_s:.3f}s > {ACTIVE_WINDOW_START_TOLERANCE_S:.3f}s)")
            if dec_end is not None:
                diff_e = abs(dec_end - eng_end)
                if diff_e > ACTIVE_WINDOW_END_TOLERANCE_S:
                    diagnostics.append(f"DIAGNOSTIC: Active window end mismatch (declared={dec_end:.3f}s vs engine={eng_end:.3f}s, delta={diff_e:.3f}s > {ACTIVE_WINDOW_END_TOLERANCE_S:.3f}s)")
                    
        # Heuristic: Heading commit time vs end of desired rotation window (tracker convention)
        dec_commit = dec.get("commit_time_s")
        rot_windows = eng.get("rotation_windows", [])
        if dec_commit is not None and rot_windows:
            eng_commit = rot_windows[0].get("end_s")
            diff_c = abs(dec_commit - eng_commit)
            if diff_c > HEADING_COMMIT_TOLERANCE_S:
                diagnostics.append(f"DIAGNOSTIC (Heuristic): Heading commit mismatch (declared={dec_commit:.3f}s vs engine_rotation={eng_commit:.3f}s, delta={diff_c:.3f}s > {HEADING_COMMIT_TOLERANCE_S:.3f}s)")
                
    if meas.get("has_measured_extraction") and eng.get("has_engine_timeline"):
        m_dur = meas.get("elapsed_duration_s")
        e_dur = eng.get("length_s")
        if m_dur is not None and e_dur is not None:
            dur_diff = abs(m_dur - e_dur)
            if dur_diff > MONTAGE_DURATION_TOLERANCE_S:
                diagnostics.append(f"DIAGNOSTIC: Duration mismatch (measured_fbx={m_dur:.3f}s vs engine_montage={e_dur:.3f}s, delta={dur_diff:.3f}s > {MONTAGE_DURATION_TOLERANCE_S:.3f}s)")

    return errors, diagnostics

def run_production_validation():
    files = [f for f in os.listdir(SHEETS_DIR) if f.endswith(".json")]
    print(f"Location: Repo Root = {ROOT_DIR}")
    print(f"Validating {len(files)} move sheets against AUTHORING_CONTRACT.md (Rev 03) and Codex D02...")
    print(f"Stated Tolerances: ActiveStart/End={ACTIVE_WINDOW_START_TOLERANCE_S}s, Commit={HEADING_COMMIT_TOLERANCE_S}s, Duration={MONTAGE_DURATION_TOLERANCE_S}s, FPS={FPS_EXPECTED}, AbsentBound=StrictNull\n")

    passed = 0
    failed = 0
    total_diagnostics = 0

    for fname in sorted(files):
        sheet_path = os.path.join(SHEETS_DIR, fname)
        with open(sheet_path, "r", encoding="utf-8") as fp:
            try:
                sheet = json.load(fp)
            except Exception as e:
                print(f"[FAIL] {fname}: Invalid JSON ({e})")
                failed += 1
                continue

        errors, diagnostics = validate_move_sheet(sheet, ROOT_DIR)
        
        if errors:
            print(f"[FAIL] {fname}: {', '.join(errors)}")
            failed += 1
        else:
            diag_str = f" ({len(diagnostics)} diagnostics)" if diagnostics else ""
            print(f"[PASS] {fname}{diag_str}")
            for d in diagnostics:
                print(f"       -> {d}")
                total_diagnostics += 1
            passed += 1

    print(f"\nProduction Validation Summary: {passed} PASSED, {failed} FAILED across {len(files)} move sheets ({total_diagnostics} documented diagnostics).")
    return failed == 0

def run_deliberate_rejection_tests():
    """
    Demonstrates validator rejection on deliberately inconsistent move sheets (Claude C-99 / C-101)
    and verifies the cross-block diagnostic reporting path.
    Tests 4 structural rejection modes and 1 cross-block diagnostic pass mode.
    """
    print("\n" + "=" * 80)
    print("DEMONSTRATION OF DELIBERATELY INCONSISTENT SHEET REJECTIONS & DIAGNOSTICS (Claude C-101)")
    print("=" * 80)
    
    # Load a valid baseline sheet to mutate for structural rejections
    sample_path = os.path.join(SHEETS_DIR, "GS_Attack01.json")
    with open(sample_path, "r", encoding="utf-8") as fp:
        baseline = json.load(fp)
        
    test_cases = [
        {
            "name": "TEST 1: Codex D02 Absent Bound Violation (max_root_excursion_cm defaulted to 0.0)",
            "mutation": lambda s: s["measured_extraction"].update({"max_root_excursion_cm": 0.0}),
            "expected_error": "Codex D02 Violation: absent bound 'max_root_excursion_cm' is 0.0 instead of null"
        },
        {
            "name": "TEST 2: Source Hash Corruption (tampered SHA-256)",
            "mutation": lambda s: s["engine_timeline"].update({"source_hash": "deadbeef" * 8}),
            "expected_error": "Engine timeline SHA mismatch"
        },
        {
            "name": "TEST 3: Missing Required Architecture Block (omitted approved_runtime)",
            "mutation": lambda s: s.pop("approved_runtime"),
            "expected_error": "Missing required block: 'approved_runtime'"
        },
        {
            "name": "TEST 4: Schema Version Discrepancy (invalid version '1.0')",
            "mutation": lambda s: s.update({"schema_version": "1.0"}),
            "expected_error": "Invalid schema version: 1.0 (expected '2.0')"
        }
    ]
    
    rejections_passed = 0
    for tc in test_cases:
        sheet_copy = copy.deepcopy(baseline)
        tc["mutation"](sheet_copy)
        errors, diags = validate_move_sheet(sheet_copy, ROOT_DIR)
        
        has_expected = any(tc["expected_error"] in err for err in errors)
        if errors and has_expected:
            print(f"[REJECTED AS EXPECTED] {tc['name']}")
            print(f"   Caught error: {errors[0]}")
            rejections_passed += 1
        else:
            print(f"[UNEXPECTED PASS / WRONG ERROR] {tc['name']}")
            print(f"   Errors returned: {errors}")
            
    print(f"\nRejection Test Summary: {rejections_passed} of {len(test_cases)} inconsistent sheets successfully REJECTED.")
    
    # --- TEST 5: Cross-Block Disagreement Diagnostic Path (Claude C-101) ---
    print("\n--- TEST 5: Cross-Block Disagreement Diagnostic Verification (Claude C-101) ---")
    a3a_path = os.path.join(SHEETS_DIR, "AN_Boss01_A3a_Combo1.json")
    with open(a3a_path, "r", encoding="utf-8") as fp:
        a3a_baseline = json.load(fp)
        
    a3a_mutated = copy.deepcopy(a3a_baseline)
    # Shift declared active window by +200 ms (0.400s -> 0.600s, 0.600s -> 0.800s) against engine montage (0.400s -> 0.600s)
    a3a_mutated["declared_intent"]["active_start_s"] += 0.200
    a3a_mutated["declared_intent"]["active_end_s"] += 0.200
    
    a3a_errors, a3a_diags = validate_move_sheet(a3a_mutated, ROOT_DIR)
    
    diag_test_passed = False
    if len(a3a_errors) == 0 and len(a3a_diags) == 2:
        start_diag = a3a_diags[0]
        end_diag = a3a_diags[1]
        if "declared=0.600s vs engine=0.400s, delta=0.200s > 0.050s" in start_diag and "declared=0.800s vs engine=0.600s, delta=0.200s > 0.050s" in end_diag:
            print("[DIAGNOSTIC REPORTED AS EXPECTED (STRUCTURAL PASS)]")
            print("   Test: Authored clip A3a declared active window shifted by +200 ms vs engine timeline")
            print("   Structural Errors: 0 (Sheet passed validation structurally; not failed)")
            print(f"   Reported Diagnostic 1: {start_diag}")
            print(f"   Reported Diagnostic 2: {end_diag}")
            diag_test_passed = True
        else:
            print(f"[FAIL] Unexpected diagnostic format: {a3a_diags}")
    else:
        print(f"[FAIL] Expected 0 errors and 2 diagnostics, got errors={a3a_errors}, diags={a3a_diags}")
        
    all_ok = (rejections_passed == len(test_cases)) and diag_test_passed
    return all_ok

if __name__ == "__main__":
    prod_ok = run_production_validation()
    rej_ok = run_deliberate_rejection_tests()
    
    if not prod_ok or not rej_ok:
        sys.exit(1)
    sys.exit(0)
