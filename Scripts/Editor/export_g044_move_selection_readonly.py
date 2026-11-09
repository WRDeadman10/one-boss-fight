"""Export serialized G044 boss move-selection inputs for read-only review.

Run under the Unreal Editor Python environment. It loads the selected encounter
and typed definitions for inspection, writes one exclusive JSON report below
Saved/G044, and does not modify project assets. Serialized records are not
evidence of runtime selection or execution.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import unreal

EDITOR_DIR = Path(__file__).resolve().parent
if str(EDITOR_DIR) not in sys.path:
    sys.path.insert(0, str(EDITOR_DIR))
import ue_editor_values


SELECTION_PACKAGE = "/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter"
SELECTION_CLASS = "/Script/OneBossFight.RPGBossEncounterDefinition"
DEFINITION_CLASS = "/Script/OneBossFight.RPGBossDefinition"
ATTACK_FIELDS = (
    "move_id", "montage_name", "fallback_montage_name", "montage_path",
    "optional_tracker_montage_path", "b_authored_windup", "commit_time",
    "active_start_time", "active_end_time", "recovery_end_time",
    "track_turn_rate", "b_branch_stage", "clip_path",
)
LOW_SWEEP_FIELDS = (
    "b_enabled", "move_id", "damage", "reach", "inner_radius",
    "blade_height", "sweep_from_degrees", "sweep_to_degrees",
)
PHASE_FIELDS = (
    "phase_id", "entry_health_fraction", "speed_multiplier",
    "rate_multiplier", "attack_multiplier",
)


def require(condition, message):
    if not condition:
        raise RuntimeError("[G044MoveSelectionReadback] REFUSED: " + message)


def prop(obj, name, where):
    try:
        return obj.get_editor_property(name)
    except Exception as exc:
        raise RuntimeError("[G044MoveSelectionReadback] REFUSED: unreadable %s.%s (%s)" % (where, name, exc))


def object_path(reference, where):
    path = ue_editor_values.ue_path(reference)
    require(path.startswith("/Game/") and "." in path, "%s is not a resolved /Game object path: %r" % (where, path))
    return path


def load_typed_asset(package_path, class_path, label):
    expected_class = unreal.load_class(None, class_path)
    require(expected_class is not None, "%s expected class is unavailable: %s" % (label, class_path))
    asset = unreal.EditorAssetLibrary.load_asset(package_path)
    require(asset is not None, "%s asset did not load: %s" % (label, package_path))
    require(ue_editor_values.is_expected_class(asset, expected_class),
            "%s has unexpected class %s" % (label, asset.get_class().get_path_name()))
    return asset


def struct_row(value, fields, where):
    result = {}
    for field in fields:
        result[field] = ue_editor_values.stable_value(prop(value, field, where), unreal, where + "." + field)
    return result


def collect():
    selection = load_typed_asset(SELECTION_PACKAGE, SELECTION_CLASS, "G044 selection")
    boss_path = object_path(prop(selection, "boss_definition", "selection"), "selection.boss_definition")
    boss = load_typed_asset(boss_path.split(".", 1)[0], DEFINITION_CLASS, "selected boss definition")
    require(str(boss.get_path_name()) == boss_path, "selected boss object path changed while loading")

    initial_phase = str(prop(selection, "initial_boss_phase", "selection"))
    tracker = prop(boss, "attack_tracker", "boss_definition")
    attacks = prop(tracker, "attacks", "boss_definition.attack_tracker")
    low_sweep = prop(boss, "low_sweep", "boss_definition")
    phases = prop(boss, "phases", "boss_definition")
    attack_rows = [struct_row(entry, ATTACK_FIELDS, "attack_tracker.attacks[%d]" % index)
                   for index, entry in enumerate(attacks)]
    phase_rows = [struct_row(entry, PHASE_FIELDS, "phases[%d]" % index)
                  for index, entry in enumerate(phases)]
    a4_rows = [row for row in attack_rows if str(row["move_id"]).strip() == "A4"]

    return {
        "schema": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "selection_object_path": str(selection.get_path_name()),
        "boss_definition_object_path": boss_path,
        "initial_boss_phase": initial_phase,
        "attack_tracker": {
            "enabled": bool(prop(tracker, "b_enabled", "attack_tracker")),
            "veto_illegal_starts": bool(prop(tracker, "b_veto_illegal_starts", "attack_tracker")),
            "branch_range_cm": float(prop(tracker, "branch_range", "attack_tracker")),
            "branch_cone_degrees": float(prop(tracker, "branch_cone_degrees", "attack_tracker")),
            "attacks": attack_rows,
            "a4_records": a4_rows,
            "a4_phase_range_fields": [],
        },
        "low_sweep": struct_row(low_sweep, LOW_SWEEP_FIELDS, "low_sweep"),
        "phase_records": phase_rows,
        "scope_note": ("These are serialized selection and definition values only; they are not evidence of runtime selection "
                       "or execution. Attack records have no per-move phase/range fields; branch range applies only to "
                       "branch selection, so phase/range gating must not be inferred from this export."),
    }


def write_report(payload):
    output_dir = Path(unreal.Paths.project_saved_dir()).resolve() / "G044"
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = output_dir / ("move_selection_readback_" + stamp + ".json")
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    # Exclusive creation preserves any existing inspection output.
    with output_path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(encoded)
    return output_path


report = collect()
output_path = write_report(report)
unreal.log("[G044MoveSelectionReadback] PASS output=%s selection=%s boss=%s phase=%s attack_rows=%d low_sweep=%s" % (
    str(output_path), report["selection_object_path"], report["boss_definition_object_path"],
    report["initial_boss_phase"], len(report["attack_tracker"]["attacks"]), report["low_sweep"]["move_id"]))
