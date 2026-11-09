"""Write one canonical receipt from Claude-authorized saved definition drafts.

Read-only with respect to Content packages. It refuses overwrite and hashes the
exact selected definition paths, phase and reflected authored definition values.
"""
import hashlib
import json
from pathlib import Path
import sys

import unreal

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import ue_editor_values


PROJECT_ROOT = Path(unreal.Paths.project_dir()).resolve()
BOSS_PATH = "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_EmberWarden_Draft"
PLAYER_PATH = "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft_V3"
PHASE = "PhaseTwo"
OUT_PATH = Path(unreal.Paths.project_saved_dir()) / "G044" / "encounter_manifest.json"
DD27J_EVIDENCE = "Docs/BossCombatReview/Execution/Claude/F3a/full2_raw.log"
FIELDS = (
    "schema", "definition_id", "presentation_id", "phase_two_aura_effect", "stats", "encounter_policy",
    "stagger_policy", "phase_flow", "fireball", "phase_dependencies", "stagger_profile",
    "dormant_wake", "bleed", "low_sweep", "shockwave", "heal_punish", "look",
    "close_clip_swap", "death", "attack_tracker", "phases", "skeleton", "animations", "fields",
)


def require(condition, message):
    if not condition:
        raise RuntimeError("[G044Manifest] REFUSED: " + message)


def stable_value(value, where):
    return ue_editor_values.stable_value(value, unreal, where)


def is_expected_class(asset, expected_class):
    return ue_editor_values.is_expected_class(asset, expected_class)


def snapshot_definition(path, definition_class):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    require(asset is not None and is_expected_class(asset, definition_class), "typed definition missing/wrong class: " + path)
    row = {"asset_path": asset.get_path_name()}
    for field in FIELDS:
        row[field] = stable_value(asset.get_editor_property(field), path + "." + field)
    native_attack_tracker = stable_value(
        unreal.get_default_object(definition_class).get_editor_property("attack_tracker"),
        "URPGBossDefinition native AttackTracker default")
    row["attack_tracker_provenance"] = (
        "native default (effective reflected value matches class default; serialized presence is not distinguished)"
        if row["attack_tracker"] == native_attack_tracker else "saved draft value")
    row["attack_tracker_field_provenance"] = {
        name: row["attack_tracker_provenance"]
        for name in ("attacks", "b_enabled", "b_veto_illegal_starts", "branch_range", "branch_cone_degrees")
    }
    require(row["schema"] == 1, "definition schema is not 1: " + path)
    require(row["definition_id"] and row["presentation_id"], "definition identity missing: " + path)
    # Lead fix: only the boss needs phase records; the hero draft legitimately has none (seen once arrays serialized).
    if path == BOSS_PATH:
        require(row["phases"], "phase list is empty: " + path)
    if path == BOSS_PATH:
        phase_ids = [str(phase.get_editor_property("phase_id")) for phase in asset.get_editor_property("phases")]
        require(PHASE in phase_ids, "selected initial boss phase is not listed in the boss definition: " + PHASE)
    require(row["skeleton"] and row["animations"], "animation dependencies missing: " + path)
    require(row["fields"], "provenance fields missing: " + path)
    package = (PROJECT_ROOT / "Content" / (path[len("/Game/"):] + ".uasset")).resolve(strict=True)
    package.relative_to(PROJECT_ROOT)
    evidence = (PROJECT_ROOT / DD27J_EVIDENCE).resolve(strict=True)
    evidence.relative_to(PROJECT_ROOT)
    row["source_provenance"] = {
        "asset_file_sha256": hashlib.sha256(package.read_bytes()).hexdigest(),
        "dd27j_evidence_path": DD27J_EVIDENCE,
        "dd27j_evidence_sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
        "attack_tracker_fields": row["attack_tracker_field_provenance"],
    }
    return row


def main():
    require(not OUT_PATH.exists(), "receipt already exists; preserve it and use a new reviewed output path")
    definition_class = unreal.load_class(None, "/Script/OneBossFight.RPGBossDefinition")
    require(definition_class is not None, "URPGBossDefinition class unavailable")
    definitions = {
        "boss": snapshot_definition(BOSS_PATH, definition_class),
        "player": snapshot_definition(PLAYER_PATH, definition_class),
    }
    require(definitions["boss"]["asset_path"] != definitions["player"]["asset_path"],
            "boss and player must be distinct definition assets")
    payload = {
        "schema": "onebossfight.encounter-manifest/v1",
        "provenance_mode": "saved-draft-package-v1",
        "boss_definition": BOSS_PATH,
        "player_definition": PLAYER_PATH,
        "initial_boss_phase": PHASE,
        "definitions": definitions,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    receipt = dict(payload)
    receipt["manifest_sha256"] = hashlib.sha256(canonical).hexdigest()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "xb") as stream:
        stream.write((json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8"))
    unreal.log("[G044Manifest] PASS path=%s manifest_sha256=%s" % (str(OUT_PATH), receipt["manifest_sha256"]))


main()
