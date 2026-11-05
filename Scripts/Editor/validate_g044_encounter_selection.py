"""Read-only validation command for the opt-in G044 encounter selection.

Run in the UE Editor after the selection, typed definitions and manifest exist.
This script loads assets for inspection only; it never changes or saves packages.
"""
import importlib.util
import json
import re
from pathlib import Path
import sys

import unreal

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import ue_editor_values


ROOT = Path(unreal.Paths.project_dir())
PACKAGE_PATH = "/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter"
MANIFEST_PATH = Path(unreal.Paths.project_saved_dir()) / "G044" / "encounter_manifest.json"
ZERO_GUID = "00000000-00000000-00000000-00000000"
ERRORS = []


def is_expected_class(asset, expected_class):
    return ue_editor_values.is_expected_class(asset, expected_class)


def issue(field, message):
    ERRORS.append("%s: %s" % (field, message))


def value(obj, property_name, field):
    try:
        return obj.get_editor_property(property_name)
    except Exception as exc:
        issue(field, "unreadable (%s)" % exc)
        return None


def as_object_path(reference):
    text = ue_editor_values.ue_path(reference)
    return text if "." in text else ""


def load_typed_definition(reference, expected_class, role):
    object_path = as_object_path(reference)
    if not object_path:
        issue("selection.%s_definition" % role, "must be a resolved object path, got %r" % str(reference))
        return None, ""
    package_path = object_path.split(".", 1)[0]  # C-791: package path and object path are distinct.
    asset = unreal.EditorAssetLibrary.load_asset(package_path)
    if asset is None:
        issue("selection.%s_definition" % role, "unresolved package %s" % package_path)
        return None, object_path
    actual_object_path = str(asset.get_path_name())
    if actual_object_path != object_path:
        issue("selection.%s_definition" % role, "object path %s does not match loaded %s" % (object_path, actual_object_path))
    if not is_expected_class(asset, expected_class):
        issue("selection.%s_definition" % role, "wrong class %s" % asset.get_class().get_path_name())
        return None, actual_object_path

    prefix = "definitions.%s." % role
    if int(value(asset, "schema", prefix + "schema") or 0) != 1:
        issue(prefix + "schema", "must equal 1")
    for prop in ("definition_id", "presentation_id"):
        if not str(value(asset, prop, prefix + prop) or "").strip():
            issue(prefix + prop, "must be nonempty")
    phases = value(asset, "phases", prefix + "phases") or []
    if not phases and "player" not in prefix:   # lead fix: the hero (target-only) definition has no phase records
        issue(prefix + "phases", "must be nonempty")
    skeleton = as_object_path(value(asset, "skeleton", prefix + "skeleton"))
    if not skeleton:
        issue(prefix + "skeleton", "must resolve to an object path")
    elif unreal.EditorAssetLibrary.load_asset(skeleton.split(".", 1)[0]) is None:
        issue(prefix + "skeleton", "unresolved object path %s" % skeleton)
    animations = value(asset, "animations", prefix + "animations") or []
    if not animations:
        issue(prefix + "animations", "must be nonempty")
    for index, animation in enumerate(animations):
        path = as_object_path(animation)
        if not path or unreal.EditorAssetLibrary.load_asset(path.split(".", 1)[0]) is None:
            issue("%sanimations[%d]" % (prefix, index), "unresolved object path %r" % str(animation))
    fields = value(asset, "fields", prefix + "fields") or []
    if not fields:
        issue(prefix + "fields", "provenance manifest must be nonempty")
    return asset, actual_object_path


def main():
    phase = ""
    manifest_hash = ""
    boss_object_path = ""
    player_object_path = ""
    selection_class = unreal.load_class(None, "/Script/OneBossFight.RPGBossEncounterDefinition")
    definition_class = unreal.load_class(None, "/Script/OneBossFight.RPGBossDefinition")
    if selection_class is None:
        issue("selection.class", "URPGBossEncounterDefinition is unavailable")
    if definition_class is None:
        issue("definitions.class", "URPGBossDefinition is unavailable")
    if selection_class is None or definition_class is None:
        raise RuntimeError("[G044SelectionValidation] REFUSED: " + " | ".join(ERRORS))

    selection = unreal.EditorAssetLibrary.load_asset(PACKAGE_PATH)
    if selection is None:
        issue("selection.asset", "missing package %s" % PACKAGE_PATH)
    elif not is_expected_class(selection, selection_class):
        issue("selection.asset", "wrong class %s" % selection.get_class().get_path_name())
    else:
        if int(value(selection, "schema", "selection.schema") or 0) != 1:
            issue("selection.schema", "must equal 1")
        guid = value(selection, "encounter_instance", "selection.encounter_instance")
        # Lead fix: str() of unreal.Guid is its repr; build the text from the four 32-bit parts (8-8-8-8 hex).
        guid_text = ue_editor_values.guid_text(guid)
        if guid is None or guid_text in ("", ZERO_GUID) or re.fullmatch(r"(?:[0-9a-fA-F]{8}-){3}[0-9a-fA-F]{8}", guid_text) is None:
            issue("selection.encounter_instance", "must be a valid nonzero GUID")
        phase = str(value(selection, "initial_boss_phase", "selection.initial_boss_phase") or "").strip()
        if not phase:
            issue("selection.initial_boss_phase", "must be nonempty")
        boss_slot = str(value(selection, "boss_slot", "selection.boss_slot") or "").strip()
        player_slot = str(value(selection, "player_slot", "selection.player_slot") or "").strip()
        if not boss_slot:
            issue("selection.boss_slot", "must be nonempty")
        if not player_slot:
            issue("selection.player_slot", "must be nonempty")
        if boss_slot and boss_slot == player_slot:
            issue("selection.player_slot", "must differ from selection.boss_slot")
        manifest_hash = str(value(selection, "stable_manifest_hash", "selection.stable_manifest_hash") or "")
        if re.fullmatch(r"[0-9a-fA-F]{64}", manifest_hash) is None:
            issue("selection.stable_manifest_hash", "must be exactly 64 hexadecimal characters")
        boss, boss_object_path = load_typed_definition(value(selection, "boss_definition", "selection.boss_definition"), definition_class, "boss")
        player, player_object_path = load_typed_definition(value(selection, "player_definition", "selection.player_definition"), definition_class, "player")
        if boss_object_path and boss_object_path == player_object_path:
            issue("selection.player_definition", "boss and player definitions must be distinct")
        if boss is not None and phase:
            phases = value(boss, "phases", "definitions.boss.phases") or []
            phase_ids = [str(value(item, "phase_id", "definitions.boss.phases[].phase_id")) for item in phases]
            if phase not in phase_ids:
                issue("selection.initial_boss_phase", "phase %s is absent from the boss definition" % phase)

    receipt = None
    try:
        receipt = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        issue("manifest.receipt", "unreadable %s (%s)" % (MANIFEST_PATH, exc))
    if receipt is not None:
        validator_path = ROOT / "Scripts" / "Tools" / "validate_encounter_manifest.py"
        spec = importlib.util.spec_from_file_location("g044_manifest_validator", str(validator_path))
        if spec is None or spec.loader is None:
            issue("manifest.validator", "could not load %s" % validator_path)
        else:
            validator = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(validator)
            for error in validator.validate(receipt, project_root=ROOT):
                issue("manifest.receipt", error)
        for key, expected in (("boss_definition", boss_object_path), ("player_definition", player_object_path)):
            actual = str(receipt.get(key, ""))
            # Receipt root paths are package paths; selected references are object paths.
            if expected and actual != expected.split(".", 1)[0]:
                issue("manifest." + key, "package path %s does not match selected object %s" % (actual, expected))
            role = "boss" if key == "boss_definition" else "player"
            receipt_definitions = receipt.get("definitions")
            snapshot = receipt_definitions.get(role, {}) if isinstance(receipt_definitions, dict) else {}
            if expected and str(snapshot.get("asset_path", "")) != expected:
                issue("manifest.definitions.%s.asset_path" % role, "does not match selected object %s" % expected)
        if str(receipt.get("initial_boss_phase", "")) != phase:
            issue("manifest.initial_boss_phase", "does not match selection.initial_boss_phase")
        if str(receipt.get("manifest_sha256", "")) != manifest_hash:
            issue("manifest.manifest_sha256", "does not match selection.stable_manifest_hash")

    if ERRORS:
        for error in ERRORS:
            unreal.log_error("[G044SelectionValidation] FAIL field=%s" % error)
        raise RuntimeError("[G044SelectionValidation] REFUSED with %d field error(s)" % len(ERRORS))
    unreal.log("[G044SelectionValidation] PASS selection=%s boss=%s player=%s phase=%s manifest_sha256=%s" % (
        str(selection.get_path_name()), boss_object_path, player_object_path, phase, manifest_hash))


main()
