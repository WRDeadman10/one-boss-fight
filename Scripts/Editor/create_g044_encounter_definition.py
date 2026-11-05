"""Create one NEW opt-in encounter selection asset for G044. Never overwrites.

Claude runs this in the UE 5.5.4 Editor only after the referenced typed boss/player
definitions and a manifest receipt exist. No level or production default is changed.
"""
import hashlib
import json
import re
import uuid
import sys
from pathlib import Path

import unreal

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import ue_editor_values


PACKAGE_DIR = "/Game/OneBossFight/Data"
ASSET_NAME = "DA_Sevarog_G044_Encounter"
ASSET_PATH = PACKAGE_DIR + "/" + ASSET_NAME
BOSS_DEFINITION_PATH = "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_EmberWarden_Draft"
PLAYER_DEFINITION_PATH = "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft_V3"
PHASE_ID = "PhaseTwo"
MANIFEST_RECEIPT = Path(unreal.Paths.project_saved_dir()) / "G044" / "encounter_manifest.json"


def require(condition, message):
    if not condition:
        raise RuntimeError("[G044Asset] REFUSED: " + message)


def is_expected_class(asset, expected_class):
    return ue_editor_values.is_expected_class(asset, expected_class)


def ue_path(value):
    return ue_editor_values.ue_path(value)


def asset_object_path(package_path):
    return package_path + "." + package_path.rsplit("/", 1)[1]


def to_signed_int32(value):
    return value if value < 0x80000000 else value - 0x100000000


def new_guid():
    value = uuid.uuid4().int
    guid = unreal.Guid()
    for property_name, shift in (("a", 96), ("b", 64), ("c", 32), ("d", 0)):
        part = (value >> shift) & 0xFFFFFFFF
        guid.set_editor_property(property_name, to_signed_int32(part))
    return guid


def require_definition(path, definition_class, phase_required):
    definition = unreal.EditorAssetLibrary.load_asset(path)
    require(definition is not None, "missing required typed definition: " + path)
    require(is_expected_class(definition, definition_class), "wrong class at " + path)
    require(int(definition.get_editor_property("schema")) == 1, "definition schema is not 1: " + path)
    require(definition.get_editor_property("definition_id") is not None, "definition ID missing: " + path)
    require(len(definition.get_editor_property("fields")) > 0, "field manifest missing: " + path)
    skeleton_value = definition.get_editor_property("skeleton")
    # Lead fix: str() of a UE object is its repr, not a path; use the object path (or the soft path text).
    if hasattr(skeleton_value, "get_path_name"):
        skeleton_path = str(skeleton_value.get_path_name())
    elif hasattr(skeleton_value, "export_text"):
        skeleton_path = str(skeleton_value.export_text())
    else:
        skeleton_path = ""
    require(skeleton_path and unreal.EditorAssetLibrary.load_asset(skeleton_path) is not None,
            "definition skeleton is unresolved: " + path)
    animations = definition.get_editor_property("animations")
    require(len(animations) > 0, "animation dependencies missing: " + path)
    for animation_path in animations:
        resolved = unreal.EditorAssetLibrary.load_asset(ue_path(animation_path))
        require(resolved is not None, "unresolved animation dependency in " + path + ": " + ue_path(animation_path))
    if phase_required:
        phase_ids = [str(phase.get_editor_property("phase_id")) for phase in definition.get_editor_property("phases")]
        require(PHASE_ID in phase_ids, "boss definition has no selected phase " + PHASE_ID)
    return definition


def main():
    # All external prerequisites and the refuse-if-exists gate run before asset creation.
    require(not unreal.EditorAssetLibrary.does_asset_exist(ASSET_PATH),
            "target already exists; this script never overwrites it: " + ASSET_PATH)
    encounter_class = unreal.load_class(None, "/Script/OneBossFight.RPGBossEncounterDefinition")
    definition_class = unreal.load_class(None, "/Script/OneBossFight.RPGBossDefinition")
    require(encounter_class is not None and definition_class is not None, "OneBossFight reflected classes are unavailable")
    boss_definition = require_definition(BOSS_DEFINITION_PATH, definition_class, True)
    player_definition = require_definition(PLAYER_DEFINITION_PATH, definition_class, False)
    require(boss_definition.get_path_name() != player_definition.get_path_name(), "boss/player definitions must be distinct")

    require(MANIFEST_RECEIPT.is_file(), "canonical manifest receipt missing: " + str(MANIFEST_RECEIPT))
    receipt = json.loads(MANIFEST_RECEIPT.read_text(encoding="utf-8"))
    require(receipt.get("schema") == "onebossfight.encounter-manifest/v1", "manifest schema mismatch")
    require(receipt.get("boss_definition") == BOSS_DEFINITION_PATH, "manifest boss path mismatch")
    require(receipt.get("player_definition") == PLAYER_DEFINITION_PATH, "manifest player path mismatch")
    require(receipt.get("initial_boss_phase") == PHASE_ID, "manifest phase mismatch")
    manifest_hash = receipt.get("manifest_sha256", "")
    require(re.fullmatch(r"[0-9a-fA-F]{64}", manifest_hash) is not None, "manifest_sha256 must be sourced and 64 hex digits")
    canonical_payload = {key: value for key, value in receipt.items() if key != "manifest_sha256"}
    canonical_bytes = json.dumps(canonical_payload, ensure_ascii=False, sort_keys=True,
                                 separators=(",", ":"), allow_nan=False).encode("utf-8")
    require(hashlib.sha256(canonical_bytes).hexdigest() == manifest_hash,
            "manifest_sha256 does not match the canonical definition snapshot")

    encounter_id = new_guid()
    require(encounter_id.to_string() != "00000000-00000000-00000000-00000000", "could not create a valid encounter GUID")
    boss_ref = boss_definition   # lead fix: a TSoftObjectPtr<URPGBossDefinition> property takes the loaded object, not a SoftObjectPath
    player_ref = player_definition

    asset = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        ASSET_NAME, PACKAGE_DIR, encounter_class, unreal.DataAssetFactory())
    require(asset is not None and is_expected_class(asset, encounter_class), "new encounter asset creation failed")
    asset.set_editor_property("schema", 1)
    asset.set_editor_property("encounter_instance", encounter_id)
    asset.set_editor_property("stable_manifest_hash", manifest_hash)
    asset.set_editor_property("boss_slot", "Boss")
    asset.set_editor_property("player_slot", "Player")
    asset.set_editor_property("initial_boss_phase", PHASE_ID)
    asset.set_editor_property("boss_definition", boss_ref)
    asset.set_editor_property("player_definition", player_ref)

    # Assert every record value and dependency before the only save call.
    require(int(asset.get_editor_property("schema")) == 1, "schema readback mismatch")
    require(asset.get_editor_property("encounter_instance").to_string() == encounter_id.to_string(), "GUID readback mismatch")
    require(str(asset.get_editor_property("stable_manifest_hash")) == manifest_hash, "manifest hash readback mismatch")
    require(str(asset.get_editor_property("boss_slot")) == "Boss", "boss slot readback mismatch")
    require(str(asset.get_editor_property("player_slot")) == "Player", "player slot readback mismatch")
    require(str(asset.get_editor_property("initial_boss_phase")) == PHASE_ID, "phase readback mismatch")
    require(ue_path(asset.get_editor_property("boss_definition")) == ue_path(boss_ref), "boss reference readback mismatch")
    require(ue_path(asset.get_editor_property("player_definition")) == ue_path(player_ref), "player reference readback mismatch")
    require(asset.get_editor_property("boss_definition") != asset.get_editor_property("player_definition"), "record references are not distinct")

    require(unreal.EditorAssetLibrary.save_loaded_asset(asset), "save failed: " + ASSET_PATH)
    unreal.log("[G044Asset] CREATED " + ASSET_PATH + " (new asset only; map/default unchanged)")


main()
