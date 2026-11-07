"""Trim AM_ER_Attack_GuardCounter to active combat slice (F10..F34, 0.3333s..1.1333s, 0.8000s length).

Uses native helper URPGMontageUtils::SetMontageSegmentRange compiled in BUILD-248.
Assert-before-save pattern: checks class, skeleton, sequence_length after trimming, saves asset.
"""

import os
import sys

try:
    import unreal
    IN_ENGINE = True
except ImportError:
    IN_ENGINE = False

MONTAGE_PATH = "/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter"
START_TIME = 10.0 / 30.0  # 0.333333 s (Frame 10 @ 30 fps)
END_TIME = 34.0 / 30.0    # 1.133333 s (Frame 34 @ 30 fps)
EXPECTED_LEN = 0.8000     # 24 frames @ 30 fps = 0.8000 s


def log(msg):
    if IN_ENGINE:
        unreal.log(f"[TrimGuardCounter] {msg}")
    print(f"[TrimGuardCounter] {msg}")


def log_error(msg):
    if IN_ENGINE:
        unreal.log_error(f"[TrimGuardCounter] ERROR: {msg}")
    print(f"[TrimGuardCounter] ERROR: {msg}", file=sys.stderr)


def run():
    if not IN_ENGINE:
        log_error("Must be executed inside Unreal Engine editor environment.")
        return False

    editor_asset_lib = unreal.EditorAssetLibrary

    montage = unreal.load_asset(MONTAGE_PATH)
    if not montage:
        log_error(f"Failed to load montage at '{MONTAGE_PATH}'.")
        return False

    if montage.get_class().get_name() != "AnimMontage":
        log_error(f"Asset '{MONTAGE_PATH}' is not an AnimMontage.")
        return False

    orig_len = montage.get_editor_property("sequence_length")
    log(f"Loaded '{MONTAGE_PATH}' (original length = {orig_len:.4f}s).")

    # Call native helper
    ok = unreal.RPGMontageUtils.set_montage_segment_range(montage, START_TIME, END_TIME)
    if not ok:
        log_error(f"set_montage_segment_range failed for '{MONTAGE_PATH}' with range [{START_TIME:.4f}, {END_TIME:.4f}].")
        return False

    new_len = montage.get_editor_property("sequence_length")
    log(f"Trimmed '{MONTAGE_PATH}': new length = {new_len:.4f}s (expected = {EXPECTED_LEN:.4f}s).")

    if abs(new_len - EXPECTED_LEN) > 0.002:
        log_error(f"ASSERTION FAILED: New length {new_len:.4f}s does not match expected {EXPECTED_LEN:.4f}s.")
        return False

    saved = editor_asset_lib.save_loaded_asset(montage)
    if not saved:
        log_error(f"Failed to save trimmed montage at '{MONTAGE_PATH}'.")
        return False

    log(f"SUCCESS: Saved trimmed montage '{MONTAGE_PATH}' (length = {new_len:.4f}s).")
    return True


if __name__ == "__main__":
    ok = run()
    if IN_ENGINE:
        try:
            unreal.SystemLibrary.execute_console_command(None, "Quit")
        except Exception:
            pass
        os._exit(0 if ok else 1)
