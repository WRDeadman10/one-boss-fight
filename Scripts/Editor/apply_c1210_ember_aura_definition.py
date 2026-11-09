"""C-1210: author Ember's optional aura and refresh the selected G044 receipt."""
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


ROOT = Path(unreal.Paths.project_dir()).resolve()
SAVED = Path(unreal.Paths.project_saved_dir()).resolve()
BOSS_PATH = "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_EmberWarden_Draft"
PLAYER_PATH = "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft_V3"
SELECTION_PATH = "/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter"
EFFECT_PATH = "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_BoostLite_Authored"
OBJECT_PATHS = {p: p + "." + p.rsplit("/", 1)[-1] for p in (BOSS_PATH, PLAYER_PATH, SELECTION_PATH, EFFECT_PATH)}
RECEIPT = SAVED / "G044" / "encounter_manifest.json"
DD27J_EVIDENCE = "Docs/BossCombatReview/Execution/Claude/F3a/full2_raw.log"


def require(condition, message):
    if not condition:
        raise RuntimeError("[C1210EmberAura] REFUSED: " + message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_file(package_path):
    require(package_path.startswith("/Game/"), "non-project package path")
    path = (ROOT / "Content" / (package_path[len("/Game/"):] + ".uasset")).resolve(strict=True)
    path.relative_to(ROOT)
    return path


def package_files(package_path):
    primary = package_file(package_path)
    prefix = primary.stem + "."
    return [p for p in sorted(primary.parent.iterdir()) if p.is_file() and (p == primary or p.name.startswith(prefix))]


def canonical_hash(payload):
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def c1210_body_hash():
    mailbox = ROOT / "Documentation" / "TEAM_MAILBOX.md"
    text = mailbox.read_text(encoding="utf-8")
    start = text.find("### [C-1210]")
    require(start >= 0, "C-1210 acceptance is absent from the team mailbox")
    end = text.find("\n### [", start + 1)
    body = text[start:] if end < 0 else text[start:end]
    require("BOOST LITE AUTHORED ACCEPTED" in body and "NS_Boss_PhaseTwoAura_BoostLite_Authored" in body,
            "C-1210 acceptance text did not match expected asset")
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def main():
    require(RECEIPT.is_file(), "current G044 receipt is missing")
    require(RECEIPT.resolve().is_relative_to(SAVED), "receipt escaped Saved")
    definitions_class = unreal.load_class(None, "/Script/OneBossFight.RPGBossDefinition")
    selection_class = unreal.load_class(None, "/Script/OneBossFight.RPGBossEncounterDefinition")
    require(definitions_class is not None and selection_class is not None, "typed classes are unavailable")
    boss = unreal.EditorAssetLibrary.load_asset(BOSS_PATH)
    player = unreal.EditorAssetLibrary.load_asset(PLAYER_PATH)
    selection = unreal.EditorAssetLibrary.load_asset(SELECTION_PATH)
    effect = unreal.EditorAssetLibrary.load_asset(EFFECT_PATH)
    require(boss and player and selection and effect, "one or more allow-listed assets failed to load")
    require(ue_editor_values.is_expected_class(boss, definitions_class)
            and ue_editor_values.is_expected_class(player, definitions_class)
            and ue_editor_values.is_expected_class(selection, selection_class), "typed asset class mismatch")
    require(boss.get_path_name() == OBJECT_PATHS[BOSS_PATH]
            and player.get_path_name() == OBJECT_PATHS[PLAYER_PATH]
            and selection.get_path_name() == OBJECT_PATHS[SELECTION_PATH], "asset object path mismatch")
    require(ue_editor_values.ue_path(selection.get_editor_property("boss_definition")) == OBJECT_PATHS[BOSS_PATH]
            and ue_editor_values.ue_path(selection.get_editor_property("player_definition")) == OBJECT_PATHS[PLAYER_PATH],
            "selection definitions differ from the allow-listed drafts")

    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    old_payload = {key: value for key, value in receipt.items() if key != "manifest_sha256"}
    require(receipt.get("manifest_sha256") == canonical_hash(old_payload), "existing receipt digest is invalid")
    require(receipt.get("boss_definition") == BOSS_PATH and receipt.get("player_definition") == PLAYER_PATH,
            "receipt definition identities differ")
    require(str(selection.get_editor_property("stable_manifest_hash")) == receipt["manifest_sha256"],
            "selection hash does not match existing receipt")
    require(receipt.get("initial_boss_phase") == str(selection.get_editor_property("initial_boss_phase")),
            "receipt and selection phases differ")

    current_effect = boss.get_editor_property("phase_two_aura_effect")
    current_path = ue_editor_values.ue_path(current_effect)
    require(not current_path or current_path == OBJECT_PATHS[EFFECT_PATH],
            "refusing to replace a different authored boss aura: " + current_path)
    boss_row = receipt["definitions"]["boss"]
    fields = boss_row.get("fields")
    require(isinstance(fields, list), "boss provenance field list is invalid")
    matching = [f for f in fields if isinstance(f, dict) and f.get("field_path") == "PhaseTwoAuraEffect"]
    require(len(matching) <= 1, "duplicate PhaseTwoAuraEffect provenance rows")

    backup_root = SAVED / "G044" / "backups" / ("C1210_AURA_" + uuid.uuid4().hex)
    backup_root.resolve().relative_to(SAVED)
    sources = package_files(BOSS_PATH) + package_files(SELECTION_PATH) + [RECEIPT]
    backup_root.mkdir(parents=True, exist_ok=False)
    backup_rows = []
    try:
        for source in sources:
            relative = source.resolve().relative_to(ROOT)
            destination = backup_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            require(digest(source) == digest(destination), "backup hash mismatch: " + str(relative))
            backup_rows.append({"source": str(relative).replace("\\", "/"),
                                "backup": str(destination.relative_to(ROOT)).replace("\\", "/"),
                                "sha256": digest(source)})
        index = backup_root / "backup_index.json"
        index.write_text(json.dumps({"schema": "g044.c1210-backup/v1", "files": backup_rows}, sort_keys=True, indent=2) + "\n", encoding="utf-8")

        if not current_path:
            boss.set_editor_property("phase_two_aura_effect", effect)
            require(unreal.EditorAssetLibrary.save_loaded_asset(boss), "saving Ember boss definition failed")
        require(ue_editor_values.ue_path(boss.get_editor_property("phase_two_aura_effect")) == OBJECT_PATHS[EFFECT_PATH],
                "in-memory aura reference readback failed")

        witness_hash = c1210_body_hash()
        if not matching:
            fields.append({
                "field_path": "PhaseTwoAuraEffect",
                "value": OBJECT_PATHS[EFFECT_PATH],
                "type": "soft-object-path<UNiagaraSystem>",
                "units": "",
                "source_path": "Documentation/TEAM_MAILBOX.md#C-1210",
                "source_sha256": witness_hash,
                "source_site": "Claude Lead acceptance C-1210",
                "origin": "C-1210 accepted BoostLite_Authored candidate",
                "precedence": "approved Ember Warden presentation data override",
                "destination": "URPGBossDefinition.PhaseTwoAuraEffect",
                "first_read": "URPGPlayerMovesSubsystem::AttachBossDiagnostics",
                "witness": "saved Ember Warden draft and refreshed G044 receipt",
            })
        boss_row["phase_two_aura_effect"] = {"object_path": OBJECT_PATHS[EFFECT_PATH]}
        boss_row["source_provenance"]["asset_file_sha256"] = digest(package_file(BOSS_PATH))
        receipt["definitions"]["player"]["phase_two_aura_effect"] = None
        payload = {key: value for key, value in receipt.items() if key != "manifest_sha256"}
        new_hash = canonical_hash(payload)
        selection.set_editor_property("stable_manifest_hash", new_hash)
        require(str(selection.get_editor_property("stable_manifest_hash")) == new_hash, "selection in-memory hash mismatch")
        require(unreal.EditorAssetLibrary.save_loaded_asset(selection), "saving refreshed selection failed")
        require(str(selection.get_editor_property("stable_manifest_hash")) == new_hash, "selection saved hash mismatch")

        receipt["manifest_sha256"] = new_hash
        temp = RECEIPT.with_name(RECEIPT.name + ".C1210.tmp")
        require(not temp.exists(), "receipt temporary file already exists")
        temp.write_text(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        require(json.loads(temp.read_text(encoding="utf-8"))["manifest_sha256"] == new_hash, "temporary receipt readback mismatch")
        os.replace(str(temp), str(RECEIPT))

        reloaded_boss = unreal.EditorAssetLibrary.load_asset(BOSS_PATH)
        reloaded_selection = unreal.EditorAssetLibrary.load_asset(SELECTION_PATH)
        require(ue_editor_values.ue_path(reloaded_boss.get_editor_property("phase_two_aura_effect")) == OBJECT_PATHS[EFFECT_PATH],
                "fresh-load boss aura readback mismatch")
        require(str(reloaded_selection.get_editor_property("stable_manifest_hash")) == new_hash,
                "fresh-load selection hash mismatch")
        unreal.log("[C1210EmberAura] PASS aura=%s manifest=%s backups=%s" % (OBJECT_PATHS[EFFECT_PATH], new_hash, str(backup_root)))
    except Exception:
        unreal.log_error("[C1210EmberAura] FAILED; pre-mutation asset/selection/receipt backups retained at " + str(backup_root))
        raise


main()
