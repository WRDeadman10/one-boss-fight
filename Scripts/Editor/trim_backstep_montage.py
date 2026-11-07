"""Trim AM_ER_Backstep_Back to accepted R7 range (15f @ 30fps = 0.4667s) per C-978.

Also reads back and asserts AM_ER_Attack_GuardCounter length is 0.8000s.
"""

import os
import sys

try:
    import unreal
    IN_ENGINE = True
except ImportError:
    IN_ENGINE = False

BACKSTEP_MONTAGE = "/Game/OneBossFight/Player/Animations/AM_ER_Backstep_Back"
BACKSTEP_SEQ = "/Game/OneBossFight/Player/Animations/AN_ER_Backstep_Back"
GUARD_COUNTER_MONTAGE = "/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter"

TARGET_BACKSTEP_START = 0.0
TARGET_BACKSTEP_END = 14.0 / 30.0  # 15 frames (F0..F14) = 0.4667s
EXPECTED_BACKSTEP_LEN = 0.4667

EXPECTED_GUARD_COUNTER_LEN = 0.8000


def log(msg):
    if IN_ENGINE:
        unreal.log(f"[TrimBackstep] {msg}")
    print(f"[TrimBackstep] {msg}")


def log_error(msg):
    if IN_ENGINE:
        unreal.log_error(f"[TrimBackstep] ERROR: {msg}")
    print(f"[TrimBackstep] ERROR: {msg}", file=sys.stderr)


def run():
    if not IN_ENGINE:
        log_error("Must be executed inside Unreal Engine editor environment.")
        return False

    editor_asset_lib = unreal.EditorAssetLibrary

    # 1. Inspect AN_ER_Backstep_Back
    seq = unreal.load_asset(BACKSTEP_SEQ)
    if seq:
        seq_len = seq.get_editor_property("sequence_length")
        log(f"Source sequence '{BACKSTEP_SEQ}' length = {seq_len:.4f}s.")

    # 2. Trim AM_ER_Backstep_Back
    bs_montage = unreal.load_asset(BACKSTEP_MONTAGE)
    if not bs_montage:
        log_error(f"Failed to load '{BACKSTEP_MONTAGE}'.")
        return False

    bs_orig_len = bs_montage.get_editor_property("sequence_length")
    log(f"Loaded '{BACKSTEP_MONTAGE}' (original length = {bs_orig_len:.4f}s).")

    ok = unreal.RPGMontageUtils.set_montage_segment_range(bs_montage, TARGET_BACKSTEP_START, TARGET_BACKSTEP_END)
    if not ok:
        log_error(f"set_montage_segment_range failed for '{BACKSTEP_MONTAGE}'.")
        return False

    bs_new_len = bs_montage.get_editor_property("sequence_length")
    log(f"Trimmed '{BACKSTEP_MONTAGE}': new length = {bs_new_len:.4f}s (expected = {EXPECTED_BACKSTEP_LEN:.4f}s).")

    if abs(bs_new_len - EXPECTED_BACKSTEP_LEN) > 0.002:
        log_error(f"ASSERTION FAILED: Backstep montage length {bs_new_len:.4f}s does not match {EXPECTED_BACKSTEP_LEN:.4f}s.")
        return False

    saved = editor_asset_lib.save_loaded_asset(bs_montage)
    if not saved:
        log_error(f"Failed to save '{BACKSTEP_MONTAGE}'.")
        return False

    log(f"SUCCESS: Saved trimmed montage '{BACKSTEP_MONTAGE}' (length = {bs_new_len:.4f}s).")

    # 3. Verify GuardCounter montage length
    gc_montage = unreal.load_asset(GUARD_COUNTER_MONTAGE)
    if not gc_montage:
        log_error(f"Failed to load '{GUARD_COUNTER_MONTAGE}'.")
        return False

    gc_len = gc_montage.get_editor_property("sequence_length")
    log(f"Readback '{GUARD_COUNTER_MONTAGE}' length = {gc_len:.4f}s (expected = {EXPECTED_GUARD_COUNTER_LEN:.4f}s).")

    if abs(gc_len - EXPECTED_GUARD_COUNTER_LEN) > 0.002:
        log_error(f"ASSERTION FAILED: GuardCounter montage length {gc_len:.4f}s does not match {EXPECTED_GUARD_COUNTER_LEN:.4f}s.")
        return False

    log(f"READBACK VERIFIED: AM_ER_Attack_GuardCounter = {gc_len:.4f}s, AM_ER_Backstep_Back = {bs_new_len:.4f}s.")
    return True


if __name__ == "__main__":
    ok = run()
    if IN_ENGINE:
        try:
            unreal.SystemLibrary.execute_console_command(None, "Quit")
        except Exception:
            pass
        os._exit(0 if ok else 1)
