"""Dry-run by default; create the opt-in Sevarog framework encounter only with --write."""
import hashlib
import json
import math
import os
import sys
import uuid
from pathlib import Path

import unreal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sevarog_o1_inputs import approved_float_matches, load_approved_values


PACKAGE_DIR = "/Game/OneBossFight/Data/Sevarog"
ASSET_NAME = "DA_Sevarog_Framework_Encounter"
ASSET_PATH = PACKAGE_DIR + "/" + ASSET_NAME
PHASE = "Phase_1"  # Native selector's authored first phase (RPGFrameworkBossCharacter.h).
BOSS_PATH = "/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_Draft"
PLAYER_PATH = "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft_V3"
PROFILE_PATH = "/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_FrameworkProfile_Draft"
WRITE = "--write" in sys.argv or os.environ.get("FRAMEWORK_ENCOUNTER_WRITE") == "1"
READBACK = "--readback" in sys.argv or os.environ.get("FRAMEWORK_ENCOUNTER_READBACK") == "1"


def require(ok, message):
    if not ok:
        raise RuntimeError("[FrameworkEncounterAuthor] REFUSED: " + message)


def path(obj):
    return obj.get_path_name() if obj else ""


def is_instance_of(obj, expected_class):
    actual_class = obj.get_class() if obj else None
    return bool(actual_class and (actual_class == expected_class or actual_class.is_child_of(expected_class)))


def finite_positive(value, label, allow_zero=False):
    require(not isinstance(value, bool), "%s must be numeric" % label)
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        require(False, "%s must be numeric" % label)
        return
    require(math.isfinite(number) and (number >= 0.0 if allow_zero else number > 0.0),
            "%s is invalid; refusing encounter write" % label)


def validate_boss_definition_for_write(boss):
    """Require the loaded definition to match the owner-approved O1 source manifest."""
    approved = load_approved_values(Path(__file__).resolve().parents[2])
    stats = boss.get_editor_property("stats")
    stat_fields = {
        "max_health": "Stats.MaxHealth", "max_posture": "Stats.MaxPosture",
        "posture_regen_delay": "Stats.PostureRegenDelay", "posture_regen_rate": "Stats.PostureRegenRate",
    }
    for property_name, field_path in stat_fields.items():
        actual = float(stats.get_editor_property(property_name))
        expected = float(approved[field_path])
        require(approved_float_matches(actual, expected),
                "%s must equal approved O1 value %s (got %s)" % (field_path, expected, actual))
    phases = list(boss.get_editor_property("phases"))
    matches = [phase for phase in phases if str(phase.get_editor_property("phase_id")) == PHASE]
    require(len(matches) == 1, "boss definition must contain exactly one Phase_1 before encounter write")
    phase = matches[0]
    phase_fields = {
        "entry_health_fraction": "Phases[Phase_1].EntryHealthFraction",
        "speed_multiplier": "Phases[Phase_1].SpeedMultiplier",
        "rate_multiplier": "Phases[Phase_1].RateMultiplier",
        "attack_multiplier": "Phases[Phase_1].AttackMultiplier",
    }
    for property_name, field_path in phase_fields.items():
        actual = float(phase.get_editor_property(property_name))
        expected = float(approved[field_path])
        require(approved_float_matches(actual, expected),
                "%s must equal approved O1 value %s (got %s)" % (field_path, expected, actual))


def new_guid():
    value = uuid.uuid4().int
    words = [(value >> shift) & 0xFFFFFFFF for shift in (96, 64, 32, 0)]
    guid = unreal.Guid()
    for name, word in zip(("a", "b", "c", "d"), words):
        guid.set_editor_property(name, word if word < 0x80000000 else word - 0x100000000)
    return guid


def read_persisted(asset, manifest_hash, boss, player, profile):
    persisted = {
        "path": path(asset),
        "stable_manifest_hash": str(asset.get_editor_property("stable_manifest_hash")),
        "boss_slot": str(asset.get_editor_property("boss_slot")),
        "player_slot": str(asset.get_editor_property("player_slot")),
        "initial_boss_phase": str(asset.get_editor_property("initial_boss_phase")),
        "boss_phase_ids": [str(item.get_editor_property("phase_id")) for item in boss.get_editor_property("phases")],
        "boss_definition": path(asset.get_editor_property("boss_definition")),
        "player_definition": path(asset.get_editor_property("player_definition")),
        "use_framework_boss": bool(asset.get_editor_property("use_framework_boss")),
        "framework_boss_profile": path(asset.get_editor_property("framework_boss_profile")),
        "encounter_instance": str(asset.get_editor_property("encounter_instance")),
    }
    require(persisted["path"] == ASSET_PATH + "." + ASSET_NAME, "saved asset path readback mismatch")
    require(persisted["stable_manifest_hash"] == manifest_hash, "saved asset hash readback mismatch")
    require(persisted["boss_slot"] == "Boss" and persisted["player_slot"] == "Player", "saved slot readback mismatch")
    require(persisted["initial_boss_phase"] == PHASE, "saved phase readback mismatch")
    require(PHASE in persisted["boss_phase_ids"], "boss definition does not contain the selected initial phase")
    require(persisted["boss_definition"] == path(boss) and persisted["player_definition"] == path(player), "saved definition readback mismatch")
    require(persisted["use_framework_boss"] and persisted["framework_boss_profile"] == path(profile), "saved framework profile readback mismatch")
    require(persisted["encounter_instance"] not in ("", "00000000-00000000-00000000-00000000"), "saved GUID readback invalid")
    return persisted


def write_field_manifest(values, manifest_hash, persisted=None):
    evidence_dir = os.environ.get("SEVAROG_O1_EVIDENCE_DIR")
    require(bool(evidence_dir), "SEVAROG_O1_EVIDENCE_DIR is required for write/readback evidence")
    os.makedirs(evidence_dir, exist_ok=True)
    record = {
        "schema": "onebossfight.sevarog-o1-field-manifest/v1",
        "decision": "O1", "source_manifest": "Scripts/Editor/sevarog_o1_inputs.json",
        "values": values, "encounter_path": ASSET_PATH, "stable_manifest_hash": manifest_hash,
        "readback": persisted,
    }
    target = os.path.join(evidence_dir, "field_manifest.json")
    temp = target + ".tmp"
    with open(temp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, sort_keys=True, indent=2, allow_nan=False)
        handle.write("\n")
    os.replace(temp, target)


def main():
    boss_class = unreal.load_class(None, "/Script/OneBossFight.RPGBossDefinition")
    profile_class = unreal.load_class(None, "/Script/OneBossFight.RPGBossFrameworkProfile")
    encounter_class = unreal.load_class(None, "/Script/OneBossFight.RPGBossEncounterDefinition")
    require(all((boss_class, profile_class, encounter_class)), "required reflected classes unavailable")
    boss = unreal.EditorAssetLibrary.load_asset(BOSS_PATH)
    player = unreal.EditorAssetLibrary.load_asset(PLAYER_PATH)
    profile = unreal.EditorAssetLibrary.load_asset(PROFILE_PATH)
    require(is_instance_of(boss, boss_class), "typed Sevarog boss definition unavailable")
    require(is_instance_of(player, boss_class), "typed Hero V3 player definition unavailable")
    require(is_instance_of(profile, profile_class), "framework profile unavailable")
    require(path(boss) != path(player), "boss and player definitions must be distinct")
    validate_boss_definition_for_write(boss)
    # Compiler membership is the canonical, sorted JSON snapshot of immutable selection fields;
    # random EncounterInstance is intentionally omitted so regenerating an instance does not alter membership.
    payload = {
        "schema": 1, "boss_slot": "Boss", "player_slot": "Player", "initial_boss_phase": PHASE,
        "boss_definition": BOSS_PATH, "player_definition": PLAYER_PATH,
        "use_framework_boss": True, "framework_boss_profile": PROFILE_PATH,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    manifest_hash = hashlib.sha256(canonical).hexdigest()
    receipt = dict(payload, encounter_instance=str(uuid.uuid4()), stable_manifest_hash=manifest_hash,
                   canonical_selection_json=canonical.decode("utf-8"), mode="readback" if READBACK else ("write" if WRITE else "dry_run"))
    if READBACK:
        asset = unreal.EditorAssetLibrary.load_asset(ASSET_PATH)
        require(is_instance_of(asset, encounter_class), "saved encounter asset unavailable for reload")
        persisted = read_persisted(asset, manifest_hash, boss, player, profile)
        write_field_manifest(load_approved_values(Path(__file__).resolve().parents[2]), manifest_hash, persisted)
        unreal.log("[FrameworkEncounterAuthor] READBACK " + json.dumps(persisted, sort_keys=True))
        return
    if not WRITE:
        unreal.log("[FrameworkEncounterAuthor] DRY_RUN " + json.dumps(receipt, sort_keys=True))
        return
    asset = unreal.EditorAssetLibrary.load_asset(ASSET_PATH)
    if asset:
        require(is_instance_of(asset, encounter_class), "existing target has wrong class; refusing replacement")
        guid_value = str(asset.get_editor_property("encounter_instance"))
        require(guid_value not in ("", "00000000-00000000-00000000-00000000"),
                "existing encounter GUID invalid; refusing to replace referenced asset")
    else:
        asset = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            ASSET_NAME, PACKAGE_DIR, encounter_class, unreal.DataAssetFactory())
        guid_value = ""
    require(is_instance_of(asset, encounter_class), "asset creation failed")
    guid = asset.get_editor_property("encounter_instance") if guid_value else new_guid()
    asset.set_editor_property("schema", 1)
    asset.set_editor_property("encounter_instance", guid)
    asset.set_editor_property("stable_manifest_hash", manifest_hash)
    asset.set_editor_property("boss_slot", "Boss")
    asset.set_editor_property("player_slot", "Player")
    asset.set_editor_property("initial_boss_phase", PHASE)
    asset.set_editor_property("boss_definition", boss)
    asset.set_editor_property("player_definition", player)
    asset.set_editor_property("use_framework_boss", True)
    asset.set_editor_property("framework_boss_profile", profile)
    require(str(asset.get_editor_property("stable_manifest_hash")) == manifest_hash, "hash readback mismatch")
    require(str(asset.get_editor_property("encounter_instance")) not in ("", "00000000-00000000-00000000-00000000"), "GUID readback invalid")
    require(path(asset.get_editor_property("boss_definition")) == path(boss), "boss reference readback mismatch")
    require(path(asset.get_editor_property("player_definition")) == path(player), "player reference readback mismatch")
    require(asset.get_editor_property("use_framework_boss") is True, "framework opt-in readback mismatch")
    require(path(asset.get_editor_property("framework_boss_profile")) == path(profile), "profile readback mismatch")
    require(unreal.EditorAssetLibrary.save_loaded_asset(asset), "asset save failed")
    persisted = read_persisted(asset, manifest_hash, boss, player, profile)
    write_field_manifest(load_approved_values(Path(__file__).resolve().parents[2]), manifest_hash, persisted)
    unreal.log("[FrameworkEncounterAuthor] WRITTEN " + ASSET_PATH + " hash=" + manifest_hash)


main()
