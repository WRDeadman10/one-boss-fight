"""Trim AM_ER_Attack_Air_Light and AM_ER_Attack_Air_Heavy_Plunge to accepted combat slices per C-979.

- AN_ER_Attack_Air_Light: source is 1.4000s; accepted slice is F18..F35 (0.6000s..1.1667s, 0.5667s length / 18f).
- AN_ER_Attack_Air_Heavy_Plunge: source is 1.4000s; accepted slice is F12..F38 (0.4000s..1.2667s, 0.8667s length / 27f).
"""

import os
import sys

try:
    import unreal
    IN_ENGINE = True
except ImportError:
    IN_ENGINE = False

AIR_LIGHT_MONTAGE = "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Light"
AIR_LIGHT_SEQ = "/Game/OneBossFight/Player/Animations/AN_ER_Attack_Air_Light"
LIGHT_START = 18.0 / 30.0  # 0.6000 s (Frame 18 @ 30 fps)
LIGHT_END = 35.0 / 30.0    # 1.1667 s (Frame 35 @ 30 fps)
EXPECTED_LIGHT_LEN = 0.5667

AIR_HEAVY_MONTAGE = "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Heavy_Plunge"
AIR_HEAVY_SEQ = "/Game/OneBossFight/Player/Animations/AN_ER_Attack_Air_Heavy_Plunge"
HEAVY_START = 12.0 / 30.0  # 0.4000 s (Frame 12 @ 30 fps)
HEAVY_END = 38.0 / 30.0    # 1.2667 s (Frame 38 @ 30 fps)
EXPECTED_HEAVY_LEN = 0.8667


def log(msg):
    if IN_ENGINE:
        unreal.log(f"[TrimAirMontages] {msg}")
    print(f"[TrimAirMontages] {msg}")


def log_error(msg):
    if IN_ENGINE:
        unreal.log_error(f"[TrimAirMontages] ERROR: {msg}")
    print(f"[TrimAirMontages] ERROR: {msg}", file=sys.stderr)


def run():
    if not IN_ENGINE:
        log_error("Must be executed inside Unreal Engine editor environment.")
        return False

    editor_asset_lib = unreal.EditorAssetLibrary

    # 1. Air Light
    light_seq = unreal.load_asset(AIR_LIGHT_SEQ)
    light_seq_len = light_seq.get_editor_property("sequence_length") if light_seq else 0.0
    log(f"AN_ER_Attack_Air_Light length = {light_seq_len:.4f}s.")

    light_m = unreal.load_asset(AIR_LIGHT_MONTAGE)
    if not light_m:
        log_error(f"Failed to load '{AIR_LIGHT_MONTAGE}'.")
        return False

    orig_light_len = light_m.get_editor_property("sequence_length")
    log(f"Loaded '{AIR_LIGHT_MONTAGE}' (original length = {orig_light_len:.4f}s).")

    ok = unreal.RPGMontageUtils.set_montage_segment_range(light_m, LIGHT_START, LIGHT_END)
    if not ok:
        log_error(f"set_montage_segment_range failed for '{AIR_LIGHT_MONTAGE}'.")
        return False

    new_light_len = light_m.get_editor_property("sequence_length")
    log(f"Trimmed '{AIR_LIGHT_MONTAGE}': new length = {new_light_len:.4f}s (slice = [{LIGHT_START:.4f}, {LIGHT_END:.4f}], expected = {EXPECTED_LIGHT_LEN:.4f}s).")

    if abs(new_light_len - EXPECTED_LIGHT_LEN) > 0.002:
        log_error(f"ASSERTION FAILED: Air Light length {new_light_len:.4f}s does not match {EXPECTED_LIGHT_LEN:.4f}s.")
        return False

    if not editor_asset_lib.save_loaded_asset(light_m):
        log_error(f"Failed to save '{AIR_LIGHT_MONTAGE}'.")
        return False
    log(f"SUCCESS: Saved trimmed montage '{AIR_LIGHT_MONTAGE}'.")

    # 2. Air Heavy Plunge
    heavy_seq = unreal.load_asset(AIR_HEAVY_SEQ)
    heavy_seq_len = heavy_seq.get_editor_property("sequence_length") if heavy_seq else 0.0
    log(f"AN_ER_Attack_Air_Heavy_Plunge length = {heavy_seq_len:.4f}s.")

    heavy_m = unreal.load_asset(AIR_HEAVY_MONTAGE)
    if not heavy_m:
        log_error(f"Failed to load '{AIR_HEAVY_MONTAGE}'.")
        return False

    orig_heavy_len = heavy_m.get_editor_property("sequence_length")
    log(f"Loaded '{AIR_HEAVY_MONTAGE}' (original length = {orig_heavy_len:.4f}s).")

    ok = unreal.RPGMontageUtils.set_montage_segment_range(heavy_m, HEAVY_START, HEAVY_END)
    if not ok:
        log_error(f"set_montage_segment_range failed for '{AIR_HEAVY_MONTAGE}'.")
        return False

    new_heavy_len = heavy_m.get_editor_property("sequence_length")
    log(f"Trimmed '{AIR_HEAVY_MONTAGE}': new length = {new_heavy_len:.4f}s (slice = [{HEAVY_START:.4f}, {HEAVY_END:.4f}], expected = {EXPECTED_HEAVY_LEN:.4f}s).")

    if abs(new_heavy_len - EXPECTED_HEAVY_LEN) > 0.002:
        log_error(f"ASSERTION FAILED: Air Heavy length {new_heavy_len:.4f}s does not match {EXPECTED_HEAVY_LEN:.4f}s.")
        return False

    if not editor_asset_lib.save_loaded_asset(heavy_m):
        log_error(f"Failed to save '{AIR_HEAVY_MONTAGE}'.")
        return False
    log(f"SUCCESS: Saved trimmed montage '{AIR_HEAVY_MONTAGE}'.")

    # Summary
    log(f"TRIM AIR MONTAGES COMPLETE:")
    log(f"  AN_ER_Attack_Air_Light: length={light_seq_len:.4f}s, slice=[{LIGHT_START:.4f}..{LIGHT_END:.4f}], AM_ER_Attack_Air_Light={new_light_len:.4f}s")
    log(f"  AN_ER_Attack_Air_Heavy_Plunge: length={heavy_seq_len:.4f}s, slice=[{HEAVY_START:.4f}..{HEAVY_END:.4f}], AM_ER_Attack_Air_Heavy_Plunge={new_heavy_len:.4f}s")
    return True


if __name__ == "__main__":
    ok = run()
    if IN_ENGINE:
        try:
            unreal.SystemLibrary.execute_console_command(None, "Quit")
        except Exception:
            pass
        os._exit(0 if ok else 1)
