"""BQ-41..44 (Queue BQ batch 9; A15/A16): read-only readback of the SAVED Sevarog S6/S7/S8 card assets.

Run in UE Editor Python under the C-1155 lock (ENG, Lead-run). It loads each saved card under /Game/OneBossFight/Data/Sevarog,
reads its spec and compares the gameplay fields against the C-1277/C-1280 values recorded in C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md
(the same values author_sevarog_draft_cards.py writes). It never sets, saves, creates or deletes an asset: get_editor_property only.

Output: one "[SevarogCardReadback] FIELD ..." line per checked field, "CARD PASS|FAIL move=..." per card, and a terminal
"RESULT=PASS cards=3 saves=0" or "RESULT=FAIL ...". Any missing asset, missing field or mismatch is a FAIL (fail-closed).
Expected values are provisional ("tune after PIE"); a mismatch means "saved asset differs from the approved draft", not "wrong design".
"""
import math
import traceback

PREFIX = "[SevarogCardReadback] "
PACKAGE_DIR = "/Game/OneBossFight/Data/Sevarog"
TOLERANCE = 1.0e-4  # float fields are stored as float32

# Expected saved values (C-1277 S6/S7, C-1280 S8). Keys are the Python names of FRPGBossMoveCardSpec / nested struct fields.
EXPECTED = {
    "DA_Move_Sevarog_Ultimate_Swing_120fps_C1277": {  # S6 Ultimate Cleave
        "spec": {"move_id": "Move_Sevarog_Ultimate_Swing_120fps_C1277", "phase_id": "Phase_2",
                 "commit_seconds": 0.600, "active_start_seconds": 0.667, "active_end_seconds": 0.900,
                 "recovery_end_seconds": 2.603, "min_range_cm": 90.0, "max_range_cm": 150.0,
                 "front_cone_degrees": 360.0, "hp_damage": 65.0},
        "window_count": 1,
        "windows": [{"window_id": "Window_Move_Sevarog_Ultimate_Swing_120fps_C1277",
                     "hit_group": "HitGroup_ScytheBlade", "start_seconds": 0.667, "end_seconds": 0.900,
                     "socket_a": "weapon_r", "socket_b": "root_weapon_end_r", "radius_cm": 15.0,
                     "secondary": False, "ring": False, "grab": False, "baked_samples": []}],
        "area_effect": {"enabled": False},
        "channel_drain": {"enabled": False},
    },
    "DA_Move_Sevarog_Subjugation_C1277": {  # S7 AreaEffect and snare
        "spec": {"move_id": "Move_Sevarog_Subjugation_C1277", "phase_id": "Phase_1",
                 "commit_seconds": 0.733, "active_start_seconds": 0.800, "active_end_seconds": 0.867,
                 "recovery_end_seconds": 2.836, "min_range_cm": 300.0, "max_range_cm": 900.0,
                 "front_cone_degrees": 140.0, "hp_damage": 0.0},
        "additional_phase_ids": ["Phase_2"],
        "window_count": 0,
        "area_effect": {"enabled": True, "release_seconds": 0.800, "delay_seconds": 0.750, "radius_cm": 225.0,
                        "damage": 35.0, "snare_seconds": 2.50, "snare_speed_scale": 0.55},
        "channel_drain": {"enabled": False},
    },
    "DA_Move_Sevarog_Soul_Siphon_C1277": {  # S8 ChannelDrain
        "spec": {"move_id": "Move_Sevarog_Soul_Siphon_C1277", "phase_id": "Phase_2",
                 "commit_seconds": 0.200, "active_start_seconds": 0.267, "active_end_seconds": 1.267,
                 "recovery_end_seconds": 1.803, "min_range_cm": 220.0, "max_range_cm": 620.0,
                 "front_cone_degrees": 90.0, "hp_damage": 0.0},
        "window_count": 0,
        "area_effect": {"enabled": False},
        "channel_drain": {"enabled": True, "start_seconds": 0.267, "end_seconds": 1.267, "tick_interval_seconds": 0.200,
                          "tick_damage": 8.0, "heal_fraction": 0.50, "cone_range_cm": 650.0,
                          "cone_half_angle_degrees": 45.0, "track_facing_each_tick": False},
    },
}


def values_match(actual, expected):
    """Pure comparison used by the static contract test: names by string, bools exactly, numbers within TOLERANCE."""
    if isinstance(expected, (list, tuple)):
        try:
            actual_values = list(actual)
        except (TypeError, ValueError):
            return False
        return len(actual_values) == len(expected) and all(values_match(a, e) for a, e in zip(actual_values, expected))
    if isinstance(expected, bool):
        return isinstance(actual, bool) and actual == expected
    if isinstance(expected, (int, float)):
        try:
            number = float(actual)
        except (TypeError, ValueError):
            return False
        return math.isfinite(number) and abs(number - float(expected)) <= TOLERANCE
    return str(actual) == str(expected)


def check_fields(unreal, label, owner, expected, failures):
    for name, want in expected.items():
        try:
            got = owner.get_editor_property(name)
        except Exception as error:  # missing field = fail-closed
            failures.append("%s.%s unreadable (%s)" % (label, name, error))
            unreal.log_error(PREFIX + "FIELD %s.%s UNREADABLE" % (label, name))
            continue
        ok = values_match(got, want)
        unreal.log(PREFIX + "FIELD %s.%s expected=%r actual=%r match=%d" % (label, name, want, got, int(ok)))
        if not ok:
            failures.append("%s.%s expected %r got %r" % (label, name, want, got))


def check_card(unreal, asset_name, expected):
    failures = []
    path = "%s/%s.%s" % (PACKAGE_DIR, asset_name, asset_name)
    card = unreal.load_asset(path)
    if card is None:
        return ["asset missing: " + path]
    spec = card.get_editor_property("spec")
    check_fields(unreal, asset_name, spec, expected["spec"], failures)
    if "additional_phase_ids" in expected:
        got = [str(n) for n in spec.get_editor_property("additional_phase_ids")]
        ok = got == expected["additional_phase_ids"]
        unreal.log(PREFIX + "FIELD %s.additional_phase_ids expected=%r actual=%r match=%d" % (asset_name, expected["additional_phase_ids"], got, int(ok)))
        if not ok:
            failures.append("%s.additional_phase_ids expected %r got %r" % (asset_name, expected["additional_phase_ids"], got))
    windows = spec.get_editor_property("windows")
    expected_windows = expected.get("windows")
    expected_window_count = expected["window_count"]
    if len(windows) != expected_window_count:
        failures.append("%s.windows count expected %d got %d" % (asset_name, expected_window_count, len(windows)))
    if expected_windows is not None:
        if len(expected_windows) != expected_window_count:
            failures.append("%s.readback contract windows count differs from window_count" % asset_name)
        for index, (window, wanted) in enumerate(zip(windows, expected_windows)):
            check_fields(unreal, "%s.windows[%d]" % (asset_name, index), window, wanted, failures)
    check_fields(unreal, asset_name + ".area_effect", spec.get_editor_property("area_effect"), expected["area_effect"], failures)
    check_fields(unreal, asset_name + ".channel_drain", spec.get_editor_property("channel_drain"), expected["channel_drain"], failures)
    return failures


def main():
    import unreal  # Editor only; the contract test imports this module without Unreal
    all_failures = []
    for asset_name, expected in EXPECTED.items():
        failures = check_card(unreal, asset_name, expected)
        unreal.log(PREFIX + "CARD %s move=%s failures=%d" % ("PASS" if not failures else "FAIL", expected["spec"]["move_id"], len(failures)))
        all_failures.extend(failures)
    if all_failures:
        unreal.log_error(PREFIX + "RESULT=FAIL cards=%d failures=%d first=%s saves=0" % (len(EXPECTED), len(all_failures), all_failures[0]))
    else:
        unreal.log(PREFIX + "RESULT=PASS cards=%d saves=0" % len(EXPECTED))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        import unreal
        unreal.log_error(PREFIX + "RESULT=FAIL " + str(error))
        unreal.log_error(traceback.format_exc())
