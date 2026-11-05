"""Lead-run, backed-up batch correction for Claude's C-850 D5 audit.

Do not run from Codex. The script reads the independently checked-in native
default table, refuses any changed mismatch set, updates all approved known
mismatches in one pass, and refreshes the manifest and selection digest.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import uuid

import unreal

EDITOR_DIR = Path(__file__).resolve().parent
TOOLS_DIR = EDITOR_DIR.parent / "Tools"
if str(EDITOR_DIR) not in sys.path:
    sys.path.insert(0, str(EDITOR_DIR))
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
import ue_editor_values
import compare_manifest_to_legacy_defaults as d5_audit

BOSS_PATH = "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_EmberWarden_Draft"
PLAYER_PATH = "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft_V3"
SELECTION_PATH = "/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter"
PHASE = "PhaseTwo"
DD27J_EVIDENCE = "Docs/BossCombatReview/Execution/Claude/F3a/full2_raw.log"
SAVED_DIR = Path(unreal.Paths.project_saved_dir()).resolve()
PROJECT_ROOT = Path(unreal.Paths.project_dir()).resolve()
RECEIPT_PATH = SAVED_DIR / "G044" / "encounter_manifest.json"
DEFAULTS_PATH = PROJECT_ROOT / "Scripts" / "Tools" / "legacy_defaults_g044.json"
FIELDS = (
    "schema", "definition_id", "presentation_id", "stats", "encounter_policy",
    "stagger_policy", "phase_flow", "fireball", "phase_dependencies", "stagger_profile",
    "dormant_wake", "bleed", "low_sweep", "shockwave", "heal_punish", "look",
    "close_clip_swap", "death", "attack_tracker", "phases", "skeleton", "animations", "fields",
)
EXPECTED_PATHS = {
    "definitions.boss.death.blend_in_seconds",
    "definitions.boss.death.death_mode",
    "definitions.boss.death.dying_seconds",
    "definitions.boss.death.guard_pack_death",
    "definitions.boss.death.hold_at_seconds",
    "definitions.boss.death.max_clip_restarts",
    "definitions.boss.death.pack_death_ability_class_name",
    "definitions.boss.death.pack_end_time_multiplier",
    "definitions.boss.death.pack_poll_seconds",
    "definitions.boss.phases[PhaseTwo].entry_health_fraction",
    "definitions.boss.phases[PhaseTwo].rate_multiplier",
    "definitions.boss.phases[PhaseTwo].speed_multiplier",
    "definitions.boss.stats.max_posture",
    "definitions.boss.stats.posture_regen_delay",
    "definitions.boss.stats.posture_regen_rate",
}


def require(condition, message):
    if not condition:
        raise RuntimeError("[G044D5] REFUSED: " + message)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_hash(payload):
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def package_file(package_path):
    require(package_path.startswith("/Game/"), "asset is outside /Game: " + package_path)
    path = (PROJECT_ROOT / "Content" / (package_path[len("/Game/"):] + ".uasset")).resolve(strict=True)
    path.relative_to(PROJECT_ROOT)
    return path


def package_files(package_path):
    primary = package_file(package_path)
    stem_prefix = primary.stem + "."
    return sorted(path for path in primary.parent.iterdir()
                  if path.is_file() and (path == primary or path.name.startswith(stem_prefix)))


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
    index.write_text(json.dumps({"schema": "g044.d5-backup/v1", "files": rows},
                                sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return rows


def snapshot_definition(path, definition_class):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    require(asset is not None and ue_editor_values.is_expected_class(asset, definition_class),
            "typed definition missing or wrong class: " + path)
    row = {"asset_path": asset.get_path_name()}
    for field in FIELDS:
        row[field] = ue_editor_values.stable_value(
            asset.get_editor_property(field), unreal, path + "." + field)
    native_tracker = ue_editor_values.stable_value(
        unreal.get_default_object(definition_class).get_editor_property("attack_tracker"),
        unreal, "URPGBossDefinition native AttackTracker default")
    tracker_provenance = (
        "native default (effective reflected value matches class default; serialized presence is not distinguished)"
        if row["attack_tracker"] == native_tracker else "saved draft value")
    row["attack_tracker_provenance"] = tracker_provenance
    row["attack_tracker_field_provenance"] = {
        name: tracker_provenance
        for name in ("attacks", "b_enabled", "b_veto_illegal_starts", "branch_range", "branch_cone_degrees")
    }
    evidence_path = (PROJECT_ROOT / DD27J_EVIDENCE).resolve(strict=True)
    evidence_path.relative_to(PROJECT_ROOT)
    row["source_provenance"] = {
        "asset_file_sha256": sha256(package_file(path)),
        "dd27j_evidence_path": DD27J_EVIDENCE,
        "dd27j_evidence_sha256": sha256(evidence_path),
        "attack_tracker_fields": row["attack_tracker_field_provenance"],
    }
    require(row["schema"] == 1 and row["definition_id"] and row["presentation_id"],
            "definition schema/identity mismatch: " + path)
    require(row["skeleton"] and row["animations"] and row["fields"],
            "skeleton, animations, or source field rows missing: " + path)
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


def set_config_value(asset, group, field, value):
    config = asset.get_editor_property(group)
    config.set_editor_property(field, value)
    asset.set_editor_property(group, config)


def apply_update(boss, path, value):
    prefix = "definitions.boss."
    require(path.startswith(prefix), "only boss fields are authorized for mutation: " + path)
    rest = path[len(prefix):]
    if rest.startswith("phases["):
        phase_id, field = rest[len("phases["):].split("].", 1)
        phases = list(boss.get_editor_property("phases"))
        matches = [phase for phase in phases
                   if str(phase.get_editor_property("phase_id")) == phase_id]
        require(len(matches) == 1, "phase is missing or duplicated: " + phase_id)
        matches[0].set_editor_property(field, value)
        boss.set_editor_property("phases", phases)
        return
    group, field = rest.split(".", 1)
    require("." not in field, "nested field requires explicit mapping: " + path)
    if path == "definitions.boss.death.death_mode":
        enum_name = "OWN_CLIP" if value == "OwnClip" else None
        require(enum_name is not None, "unsupported audited death mode: " + str(value))
        value = getattr(unreal.RPGBossDeathMode, enum_name)  # lead fix (C-852): UE Python drops the E prefix of UENUMs (C-791)
    set_config_value(boss, group, field, value)


def read_update(boss, path):
    prefix = "definitions.boss."
    rest = path[len(prefix):]
    if rest.startswith("phases["):
        phase_id, field = rest[len("phases["):].split("].", 1)
        matches = [phase for phase in boss.get_editor_property("phases")
                   if str(phase.get_editor_property("phase_id")) == phase_id]
        require(len(matches) == 1, "phase is missing or duplicated during readback: " + phase_id)
        return matches[0].get_editor_property(field)
    group, field = rest.split(".", 1)
    return boss.get_editor_property(group).get_editor_property(field)


def main():
    require(RECEIPT_PATH.is_file(), "current manifest receipt is missing")
    require(RECEIPT_PATH.resolve().is_relative_to(SAVED_DIR), "manifest escaped Saved")
    definition_class = unreal.load_class(None, "/Script/OneBossFight.RPGBossDefinition")
    selection_class = unreal.load_class(None, "/Script/OneBossFight.RPGBossEncounterDefinition")
    require(definition_class is not None and selection_class is not None, "reflected classes unavailable")
    boss, _ = snapshot_definition(BOSS_PATH, definition_class)
    player, _ = snapshot_definition(PLAYER_PATH, definition_class)
    selection = unreal.EditorAssetLibrary.load_asset(SELECTION_PATH)
    require(selection is not None and ue_editor_values.is_expected_class(selection, selection_class),
            "existing G044 selection asset is missing or wrong class")

    current = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    require(current.get("schema") == "onebossfight.encounter-manifest/v1", "receipt schema mismatch")
    old_hash = str(current.get("manifest_sha256", ""))
    old_payload = {key: value for key, value in current.items() if key != "manifest_sha256"}
    require(old_hash == canonical_hash(old_payload), "current manifest hash is invalid")
    require(current.get("boss_definition") == BOSS_PATH and current.get("player_definition") == PLAYER_PATH
            and current.get("initial_boss_phase") == PHASE, "manifest identity or selected phase changed")
    require(current["definitions"]["boss"] == snapshot_definition(BOSS_PATH, definition_class)[1],
            "boss package no longer matches the current manifest")
    require(current["definitions"]["player"] == snapshot_definition(PLAYER_PATH, definition_class)[1],
            "player package no longer matches the current manifest")
    require(ue_editor_values.ue_path(selection.get_editor_property("boss_definition")) == ue_editor_values.ue_path(boss)
            and ue_editor_values.ue_path(selection.get_editor_property("player_definition")) == ue_editor_values.ue_path(player),
            "selection definition references changed")
    require(str(selection.get_editor_property("initial_boss_phase")) == PHASE, "selection phase changed")
    require(str(selection.get_editor_property("stable_manifest_hash")) == old_hash,
            "selection digest does not match the current manifest")

    table = json.loads(DEFAULTS_PATH.read_text(encoding="utf-8"))
    rows = d5_audit.audit(current, table, PROJECT_ROOT)
    mismatches = {row["path"]: row for row in rows if row["status"] == "MISMATCH"}
    require(set(mismatches) == EXPECTED_PATHS,
            "mismatch set differs from the reviewed D5 expected sheet; no write performed")
    for path in sorted(mismatches):
        require(type(mismatches[path].get("legacy_value")) in (bool, int, float, str),
                "D5 only writes scalar/enum native defaults: " + path)
        require("object_path" not in mismatches[path], "reference update requires a separate review: " + path)

    old_player_hash = sha256(package_file(PLAYER_PATH))
    old_selection_hash = sha256(package_file(SELECTION_PATH))
    backup_root = SAVED_DIR / "G044" / "backups" / ("C850_D5_" + uuid.uuid4().hex)
    backup_root.resolve().relative_to(SAVED_DIR)
    sources = []
    for package in (BOSS_PATH, PLAYER_PATH, SELECTION_PATH):
        sources.extend(package_files(package))
    sources.append(RECEIPT_PATH)
    backups = backup_sources(backup_root, sources)
    require(len(backups) == len(sources), "backup index did not cover every source")

    # All identity, digest, source-citation, mismatch-set, and backup assertions precede writes.
    for path, row in mismatches.items():
        apply_update(boss, path, row["legacy_value"])
        actual = ue_editor_values.stable_value(read_update(boss, path), unreal, path)
        require(d5_audit._equal(actual, row["legacy_value"]), "in-memory readback mismatch: " + path)
    require(unreal.EditorAssetLibrary.save_loaded_asset(boss), "saving corrected boss draft failed")
    boss, boss_row = snapshot_definition(BOSS_PATH, definition_class)
    _, player_row = snapshot_definition(PLAYER_PATH, definition_class)
    new_receipt = make_receipt(boss_row, player_row)
    for path, row in mismatches.items():
        value = d5_audit.typed_fields(new_receipt)[path]
        require(d5_audit._equal(value, row["legacy_value"]), "saved readback mismatch: " + path)

    new_hash = new_receipt["manifest_sha256"]
    selection.set_editor_property("stable_manifest_hash", new_hash)
    require(str(selection.get_editor_property("stable_manifest_hash")) == new_hash,
            "selection digest in-memory readback mismatch")
    require(unreal.EditorAssetLibrary.save_loaded_asset(selection), "saving refreshed selection failed")
    require(str(selection.get_editor_property("stable_manifest_hash")) == new_hash,
            "selection digest saved readback mismatch")
    require(sha256(package_file(PLAYER_PATH)) == old_player_hash,
            "player package changed during boss-only D5 update")
    temp_path = RECEIPT_PATH.with_name(RECEIPT_PATH.name + ".C850_D5.tmp")
    require(not temp_path.exists(), "manifest temp path already exists; preserve it")
    temp_path.write_text(json.dumps(new_receipt, ensure_ascii=False, sort_keys=True,
                                    indent=2, allow_nan=False) + "\n", encoding="utf-8")
    require(json.loads(temp_path.read_text(encoding="utf-8"))["manifest_sha256"] == new_hash,
            "new manifest readback mismatch")
    os.replace(str(temp_path), str(RECEIPT_PATH))
    require(str(selection.get_editor_property("stable_manifest_hash")) == new_hash,
            "selection/manifest digest mismatch after receipt write")

    old_by_source = {row["source"]: row["sha256"] for row in backups}
    unreal.log("[G044D5] PASS changed_fields=%d old_manifest=%s new_manifest=%s" %
               (len(mismatches), old_hash, new_hash))
    unreal.log("[G044D5] HASH boss_package old=%s new=%s" %
               (old_by_source[str(package_file(BOSS_PATH).relative_to(PROJECT_ROOT)).replace("\\", "/")],
                sha256(package_file(BOSS_PATH))))
    unreal.log("[G044D5] HASH player_package unchanged=%s" % old_player_hash)
    unreal.log("[G044D5] HASH selection_package old=%s new=%s" %
               (old_by_source[str(package_file(SELECTION_PATH).relative_to(PROJECT_ROOT)).replace("\\", "/")],
                sha256(package_file(SELECTION_PATH))))
    unreal.log("[G044D5] HASH manifest old=%s new=%s" % (old_hash, new_hash))
    unreal.log("[G044D5] BACKUP root=%s files=%d index_sha256=%s" %
               (str(backup_root), len(backups), sha256(backup_root / "backup_index.json")))


main()
