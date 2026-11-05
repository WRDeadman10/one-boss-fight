"""Lead-run, backed-up G044 parity correction. Never run from Codex.

Updates the existing authorized boss draft from 1500 to legacy parity 2000,
rebuilds its canonical receipt, and refreshes the existing selection asset hash.
Preflights identities and old hashes, creates byte-for-byte backups, and
verifies each in-memory/readback value before saving the corresponding asset.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import uuid

import unreal

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import ue_editor_values


BOSS_PATH = "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_EmberWarden_Draft"
PLAYER_PATH = "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft_V3"
SELECTION_PATH = "/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter"
PHASE = "PhaseTwo"
DD27J_EVIDENCE = "Docs/BossCombatReview/Execution/Claude/F3a/full2_raw.log"
SAVED_DIR = Path(unreal.Paths.project_saved_dir()).resolve()
PROJECT_ROOT = Path(unreal.Paths.project_dir()).resolve()
RECEIPT_PATH = SAVED_DIR / "G044" / "encounter_manifest.json"
FIELDS = (
    "schema", "definition_id", "presentation_id", "stats", "encounter_policy",
    "stagger_policy", "phase_flow", "fireball", "phase_dependencies", "stagger_profile",
    "dormant_wake", "bleed", "low_sweep", "shockwave", "heal_punish", "look",
    "close_clip_swap", "death", "attack_tracker", "phases", "skeleton", "animations", "fields",
)


def require(condition, message):
    if not condition:
        raise RuntimeError("[G044Health] REFUSED: " + message)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ue_path(value):
    return ue_editor_values.ue_path(value)


def package_file(package_path):
    require(package_path.startswith("/Game/"), "asset is outside /Game: " + package_path)
    path = (PROJECT_ROOT / "Content" / (package_path[len("/Game/"):] + ".uasset")).resolve(strict=True)
    path.relative_to(PROJECT_ROOT)
    return path


def package_files(package_path):
    primary = package_file(package_path)
    # Back up the package and any Unreal sidecar files without globbing into a
    # neighboring asset whose name merely shares a prefix.
    stem_prefix = primary.stem + "."
    return sorted(path for path in primary.parent.iterdir()
                  if path.is_file() and (path == primary or path.name.startswith(stem_prefix)))


def canonical_hash(payload):
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def snapshot_definition(path, definition_class):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    require(asset is not None and ue_editor_values.is_expected_class(asset, definition_class),
            "typed definition missing or wrong class: " + path)
    row = {"asset_path": asset.get_path_name()}
    for field in FIELDS:
        # Lead fix (C-847): the helper signature is stable_value(value, unreal_module, where); passing the path as the
        # second argument made unreal.Array unrecognised, unlike the proven write_g044_manifest_receipt.py.
        row[field] = ue_editor_values.stable_value(asset.get_editor_property(field), unreal, path + "." + field)
    native_tracker = ue_editor_values.stable_value(
        unreal.get_default_object(definition_class).get_editor_property("attack_tracker"), unreal,
        "URPGBossDefinition native AttackTracker default")
    tracker_provenance = (
        "native default (effective reflected value matches class default; serialized presence is not distinguished)"
        if row["attack_tracker"] == native_tracker else "saved draft value")
    row["attack_tracker_provenance"] = tracker_provenance
    row["attack_tracker_field_provenance"] = {
        name: tracker_provenance
        for name in ("attacks", "b_enabled", "b_veto_illegal_starts", "branch_range", "branch_cone_degrees")
    }
    require(row["schema"] == 1 and row["definition_id"] and row["presentation_id"],
            "definition schema or identity invalid: " + path)
    if path == BOSS_PATH:
        require(row["phases"], "boss phase list missing")
        phase_ids = [str(phase.get_editor_property("phase_id")) for phase in asset.get_editor_property("phases")]
        require(PHASE in phase_ids, "selected phase is absent from boss definition")
    require(row["skeleton"] and row["animations"] and row["fields"],
            "skeleton, animations, or provenance fields missing: " + path)
    package = package_file(path)
    evidence_path = (PROJECT_ROOT / DD27J_EVIDENCE).resolve(strict=True)
    evidence_path.relative_to(PROJECT_ROOT)
    row["source_provenance"] = {
        "asset_file_sha256": sha256(package),
        "dd27j_evidence_path": DD27J_EVIDENCE,
        "dd27j_evidence_sha256": sha256(evidence_path),
        "attack_tracker_fields": row["attack_tracker_field_provenance"],
    }
    return asset, row


def make_receipt(boss, player):
    payload = {
        "schema": "onebossfight.encounter-manifest/v1",
        "provenance_mode": "saved-draft-package-v1",
        "boss_definition": BOSS_PATH,
        "player_definition": PLAYER_PATH,
        "initial_boss_phase": PHASE,
        "definitions": {"boss": boss, "player": player},
    }
    receipt = dict(payload)
    receipt["manifest_sha256"] = canonical_hash(payload)
    return receipt


def backup_sources(backup_root, paths):
    backup_root.mkdir(parents=True, exist_ok=False)
    rows = []
    for source in paths:
        relative = source.resolve().relative_to(PROJECT_ROOT)
        destination = backup_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        source_hash, backup_hash = sha256(source), sha256(destination)
        require(source_hash == backup_hash, "backup verification failed: " + str(relative))
        rows.append({"source": str(relative).replace("\\", "/"),
                     "backup": str(destination.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                     "sha256": source_hash})
    index = backup_root / "backup_index.json"
    index.write_text(json.dumps({"schema": "g044.health-backup/v1", "files": rows},
                                sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return rows


def main():
    require(RECEIPT_PATH.is_file(), "current G044 manifest receipt is missing")
    require(RECEIPT_PATH.resolve().is_relative_to(SAVED_DIR), "manifest receipt escaped Saved")
    definition_class = unreal.load_class(None, "/Script/OneBossFight.RPGBossDefinition")
    selection_class = unreal.load_class(None, "/Script/OneBossFight.RPGBossEncounterDefinition")
    require(definition_class is not None and selection_class is not None, "reflected classes unavailable")
    boss, _ = snapshot_definition(BOSS_PATH, definition_class)
    player, _ = snapshot_definition(PLAYER_PATH, definition_class)
    selection = unreal.EditorAssetLibrary.load_asset(SELECTION_PATH)
    require(selection is not None and ue_editor_values.is_expected_class(selection, selection_class),
            "existing G044 selection asset is missing or wrong class")
    stats = boss.get_editor_property("stats")
    old_health = float(stats.get_editor_property("max_health"))
    require(old_health == 1500.0, "boss Stats.MaxHealth expected exactly 1500.0, got %.9g" % old_health)
    current_receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    require(current_receipt.get("schema") == "onebossfight.encounter-manifest/v1", "current receipt schema mismatch")
    old_manifest_hash = str(current_receipt.get("manifest_sha256", ""))
    old_payload = {key: value for key, value in current_receipt.items() if key != "manifest_sha256"}
    require(old_manifest_hash == canonical_hash(old_payload), "current receipt digest is invalid")
    require(current_receipt.get("boss_definition") == BOSS_PATH and current_receipt.get("player_definition") == PLAYER_PATH
            and current_receipt.get("initial_boss_phase") == PHASE, "current receipt identities/phase mismatch")
    require(float(current_receipt["definitions"]["boss"]["stats"]["max_health"]) == old_health,
            "current receipt boss health does not match the 1500.0 draft value")
    require(current_receipt["definitions"]["boss"]["source_provenance"]["asset_file_sha256"] == sha256(package_file(BOSS_PATH)),
            "current boss package hash does not match receipt")
    require(current_receipt["definitions"]["player"]["source_provenance"]["asset_file_sha256"] == sha256(package_file(PLAYER_PATH)),
            "current player package hash does not match receipt")
    old_player_hash = sha256(package_file(PLAYER_PATH))
    old_selection_hash = str(selection.get_editor_property("stable_manifest_hash"))
    require(old_selection_hash == old_manifest_hash, "selection hash does not match current receipt")
    require(ue_path(selection.get_editor_property("boss_definition")) == ue_path(boss), "selection boss reference changed")
    require(ue_path(selection.get_editor_property("player_definition")) == ue_path(player), "selection player reference changed")
    require(str(selection.get_editor_property("initial_boss_phase")) == PHASE, "selection phase changed")

    backup_root = SAVED_DIR / "G044" / "backups" / ("C840_D2_" + uuid.uuid4().hex)
    backup_root.resolve().relative_to(SAVED_DIR)
    all_sources = []
    for package in (BOSS_PATH, PLAYER_PATH, SELECTION_PATH):
        all_sources.extend(package_files(package))
    all_sources.append(RECEIPT_PATH)
    backups = backup_sources(backup_root, all_sources)
    require(len(backups) == len(all_sources), "backup manifest did not cover every source file")

    # All source identity, health, receipt, selection, and backup assertions
    # above run before the first package save.
    stats.set_editor_property("max_health", 2000.0)
    boss.set_editor_property("stats", stats)
    new_health = float(boss.get_editor_property("stats").get_editor_property("max_health"))
    require(new_health == 2000.0, "in-memory boss Stats.MaxHealth readback mismatch")
    phase_ids = [str(phase.get_editor_property("phase_id")) for phase in boss.get_editor_property("phases")]
    require(PHASE in phase_ids, "boss phase list changed before save")

    require(unreal.EditorAssetLibrary.save_loaded_asset(boss), "saving the corrected boss draft failed")
    saved_boss_hash = sha256(package_file(BOSS_PATH))
    _, boss_row = snapshot_definition(BOSS_PATH, definition_class)
    _, player_row = snapshot_definition(PLAYER_PATH, definition_class)
    require(float(boss.get_editor_property("stats").get_editor_property("max_health")) == 2000.0,
            "saved boss health readback mismatch")
    new_receipt = make_receipt(boss_row, player_row)
    new_manifest_hash = new_receipt["manifest_sha256"]
    require(float(new_receipt["definitions"]["boss"]["stats"]["max_health"]) == 2000.0,
            "new receipt health value mismatch")
    selection.set_editor_property("stable_manifest_hash", new_manifest_hash)
    require(str(selection.get_editor_property("stable_manifest_hash")) == new_manifest_hash,
            "selection hash in-memory readback mismatch")
    require(ue_path(selection.get_editor_property("boss_definition")) == ue_path(boss)
            and ue_path(selection.get_editor_property("player_definition")) == ue_path(player),
            "selection references changed during health update")

    require(unreal.EditorAssetLibrary.save_loaded_asset(selection), "saving refreshed G044 selection failed")
    saved_selection_hash = sha256(package_file(SELECTION_PATH))
    require(str(selection.get_editor_property("stable_manifest_hash")) == new_manifest_hash,
            "saved selection manifest hash readback mismatch")
    require(sha256(package_file(PLAYER_PATH)) == old_player_hash,
            "player definition package changed during the boss health update")
    require(ue_path(selection.get_editor_property("boss_definition")) == ue_path(boss)
            and ue_path(selection.get_editor_property("player_definition")) == ue_path(player)
            and str(selection.get_editor_property("initial_boss_phase")) == PHASE,
            "saved selection references or phase changed")
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = RECEIPT_PATH.with_name(RECEIPT_PATH.name + ".C840_D2.tmp")
    require(not temp_path.exists(), "receipt temporary path already exists; preserve it")
    temp_path.write_text(json.dumps(new_receipt, ensure_ascii=False, sort_keys=True, indent=2,
                                    allow_nan=False) + "\n", encoding="utf-8")
    require(json.loads(temp_path.read_text(encoding="utf-8"))["manifest_sha256"] == new_manifest_hash,
            "new receipt file readback mismatch")
    os.replace(str(temp_path), str(RECEIPT_PATH))

    unreal.log("[G044Health] PASS boss=%s Stats.MaxHealth %.1f -> %.1f" % (BOSS_PATH, old_health, new_health))
    old_hash_by_source = {row["source"]: row["sha256"] for row in backups}
    boss_rel = "Content/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_EmberWarden_Draft.uasset"
    selection_rel = "Content/OneBossFight/Data/DA_Sevarog_G044_Encounter.uasset"
    unreal.log("[G044Health] HASH boss_package old=%s new=%s" % (old_hash_by_source[boss_rel], saved_boss_hash))
    unreal.log("[G044Health] HASH manifest old=%s new=%s" % (old_manifest_hash, new_manifest_hash))
    unreal.log("[G044Health] HASH player_package unchanged=%s" % old_player_hash)
    unreal.log("[G044Health] HASH selection_package old=%s new=%s" % (old_hash_by_source[selection_rel], saved_selection_hash))
    unreal.log("[G044Health] BACKUP root=%s files=%d index_sha256=%s" %
                (str(backup_root), len(backups), sha256(backup_root / "backup_index.json")))
    unreal.log("[G044Health] UPDATED selection=%s stable_manifest_hash=%s" % (SELECTION_PATH, new_manifest_hash))


main()
