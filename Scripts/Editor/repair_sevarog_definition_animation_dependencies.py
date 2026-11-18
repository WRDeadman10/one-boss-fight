"""BT-18: validate profile animation refs, then narrowly author definition dependencies."""
import json
import os
import sys
import traceback
from pathlib import Path

import unreal

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import ue_editor_values

PREFIX = "[BT18SevarogDependencies] "
DEFINITION = "/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_Draft.DA_Boss_Sevarog_Draft"
PROFILE = "/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_FrameworkProfile_Draft.DA_Boss_Sevarog_FrameworkProfile_Draft"
ROOT = "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/"
EXPECTED = (
    ROOT + "Swing1_Medium.Swing1_Medium",
    ROOT + "Swing2_Medium.Swing2_Medium",
    ROOT + "Swing3_Slow.Swing3_Slow",
    ROOT + "Speedburst.Speedburst",
    ROOT + "Ultimate_Swing_120fps.Ultimate_Swing_120fps",
    ROOT + "Subjugation.Subjugation",
    ROOT + "Soul_Siphon.Soul_Siphon",
)
FIELDS = (
    "schema", "definition_id", "presentation_id", "phase_two_aura_effect", "stats",
    "encounter_policy", "parry_slow_motion", "stagger_policy", "phase_flow", "fireball",
    "phase_dependencies", "stagger_profile", "dormant_wake", "bleed", "low_sweep",
    "shockwave", "heal_punish", "look", "close_clip_swap", "death", "attack_tracker",
    "use_montage_notify_timings", "phases", "skeleton", "animations", "fields",
)


def log(text):
    unreal.log(PREFIX + str(text))


def load(path):
    value = unreal.load_asset(path)
    if value is None:
        raise RuntimeError("asset did not load: " + path)
    return value


def ref_path(value):
    path = ue_editor_values.ue_path(value)
    if not path:
        raise RuntimeError("soft reference has no stable object path")
    return path


def inspect_profile():
    definition = load(DEFINITION)
    profile = load(PROFILE)
    skeleton_path = ref_path(definition.get_editor_property("skeleton"))
    skeleton = load(skeleton_path)
    cards = list(profile.get_editor_property("cards") or [])
    if not cards:
        raise RuntimeError("saved framework profile has no cards")
    card_rows = []
    paths = []
    for entry in cards:
        card_path = ref_path(entry.get_editor_property("card"))
        card = load(card_path)
        spec = card.get_editor_property("spec")
        sequence_path = ref_path(spec.get_editor_property("sequence"))
        sequence = load(sequence_path)
        sequence_skeleton = sequence.get_editor_property("skeleton")
        sequence_skeleton_path = ref_path(sequence_skeleton)
        if sequence_skeleton_path != skeleton_path:
            raise RuntimeError("card sequence skeleton mismatch: %s -> %s" %
                               (sequence_path, sequence_skeleton_path))
        if not sequence_path.startswith(ROOT):
            raise RuntimeError("sequence outside Sevarog animation package: " + sequence_path)
        card_rows.append({"card": card_path, "sequence": sequence_path,
                          "skeleton": sequence_skeleton_path})
        paths.append(sequence_path)
    if len(paths) != len(set(paths)):
        raise RuntimeError("profile contains duplicate sequence references")
    if set(paths) != set(EXPECTED):
        raise RuntimeError("saved profile sequence set differs from reviewed seven-path allowlist: " +
                           json.dumps(sorted(paths)))
    return definition, profile, skeleton_path, card_rows, paths


def snapshot_non_target(definition):
    result = {}
    for name in FIELDS:
        if name == "animations":
            continue
        value = definition.get_editor_property(name)
        result[name] = ue_editor_values.stable_value(value, unreal, "definition." + name)
    return result


def main():
    action = os.environ.get("BT18_ACTION", "inspect").strip().lower()
    receipt_path = Path(os.environ["BT18_RECEIPT"])
    if action == "inspect":
        definition, profile, skeleton_path, card_rows, paths = inspect_profile()
        payload = {"stage": "inspect", "complete": True, "definition": DEFINITION,
                   "profile": PROFILE, "definition_skeleton": skeleton_path,
                   "profile_cards": card_rows, "animation_paths": paths,
                   "definition_hash_prewrite": os.environ.get("BT18_ASSET_HASH", "")}
        receipt_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        log("INSPECT_PASS cards=%d sequences=%d" % (len(card_rows), len(paths)))
    elif action == "write":
        definition, profile, skeleton_path, card_rows, paths = inspect_profile()
        before = snapshot_non_target(definition)
        loaded = [load(path) for path in paths]
        definition.set_editor_property("animations", loaded)
        if not unreal.EditorAssetLibrary.save_loaded_asset(definition):
            raise RuntimeError("save_loaded_asset returned false")
        payload = {"stage": "write", "complete": True, "definition": DEFINITION,
                   "profile": PROFILE, "animation_paths": paths,
                   "non_target_snapshot": before}
        receipt_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        log("WRITE_PASS animations=%d" % len(paths))
    elif action == "verify":
        definition, profile, skeleton_path, card_rows, paths = inspect_profile()
        current = [ref_path(value) for value in list(definition.get_editor_property("animations") or [])]
        if current != paths:
            raise RuntimeError("definition animations do not exactly match active profile order")
        for path in current:
            sequence = load(path)
            if ref_path(sequence.get_editor_property("skeleton")) != skeleton_path:
                raise RuntimeError("definition animation has mismatched skeleton: " + path)
        expected_snapshot = json.loads(Path(os.environ["BT18_WRITE_RECEIPT"]).read_text(encoding="utf-8"))
        before = expected_snapshot.get("non_target_snapshot")
        after = snapshot_non_target(definition)
        if not isinstance(before, dict) or after != before:
            raise RuntimeError("a non-target definition field changed across save/reload")
        payload = {"stage": "verify", "complete": True, "definition": DEFINITION,
                   "profile": PROFILE, "definition_skeleton": skeleton_path,
                   "profile_cards": card_rows, "animation_paths": current,
                   "animation_count": len(current), "all_skeletons_match": True,
                   "non_target_fields_preserved": True}
        receipt_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        log("VERIFY_PASS animations=%d non_target_fields=preserved" % len(current))
    else:
        raise RuntimeError("unsupported BT18_ACTION: " + action)


try:
    main()
except Exception as error:
    log("FAIL " + repr(error))
    log(traceback.format_exc())
    raise
finally:
    try:
        unreal.SystemLibrary.execute_console_command(None, "Quit")
    except Exception as error:
        log("QUIT_REQUEST_FAILED " + repr(error))
