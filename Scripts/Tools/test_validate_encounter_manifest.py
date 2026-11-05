import copy
import hashlib
import json
import unittest
from pathlib import Path

from validate_encounter_manifest import REQUIRED_FIELDS, canonical_sha256, validate


def definition(role, path):
    row = {field: {} for field in REQUIRED_FIELDS}
    row.update({
        "asset_path": path,
        "schema": 1,
        "definition_id": role.title(),
        "presentation_id": role.title() + "Presentation",
        "phases": [{"phase_id": "PhaseOne"}],
        "skeleton": {"object_path": "/Game/Test/Skeleton.Skeleton"},
        "animations": [{"object_path": "/Game/Test/Animation.Animation"}],
        "fields": [{
            "field_path": "Stats.MaxHealth", "type": "float", "source_path": "RPGEncounterBinding.h:24",
            "source_sha256": "a" * 64, "source_site": "URPGBossDefinition.Stats.MaxHealth",
            "origin": "pack editor readback", "precedence": "definition source",
            "destination": "Stats.MaxHealth", "first_read": "RPGCombatHydration::CompileParticipant",
            "witness": "Editor CDO snapshot plus reviewed pack source",
        }],
    })
    return row


def receipt():
    boss = definition("boss", "/Game/Test/DA_Boss.DA_Boss")
    player = definition("player", "/Game/Test/DA_Player.DA_Player")
    payload = {
        "schema": "onebossfight.encounter-manifest/v1",
        "source_snapshot_sha256": hashlib.sha256(b"canonical test source snapshot").hexdigest(),
        # Top-level membership paths are package paths; snapshots cite object paths.
        "boss_definition": boss["asset_path"].split(".", 1)[0],
        "player_definition": player["asset_path"].split(".", 1)[0],
        "initial_boss_phase": "PhaseOne",
        "definitions": {"boss": boss, "player": player},
    }
    payload["manifest_sha256"] = canonical_sha256(payload)
    return payload


def d2_receipt():
    fixture = (Path(__file__).resolve().parents[2] /
               "Docs/BossCombatReview/Execution/Claude/C840_D2_HEALTH/manifest/encounter_manifest_after.json")
    return json.loads(fixture.read_text(encoding="utf-8"))


def resign(value):
    value["manifest_sha256"] = canonical_sha256({k: v for k, v in value.items() if k != "manifest_sha256"})
    return value


class EncounterManifestTests(unittest.TestCase):
    def test_valid_canonical_receipt_passes(self):
        self.assertEqual(validate(receipt()), [])

    def test_actual_d2_saved_draft_receipt_passes(self):
        self.assertEqual(validate(d2_receipt()), [])

    def test_d2_attack_tracker_missing_key_fails_after_resigning(self):
        value = d2_receipt()
        del value["definitions"]["boss"]["attack_tracker"]["attacks"]
        resign(value)
        self.assertTrue(any("attack_tracker must contain exactly" in error for error in validate(value)))

    def test_d2_attack_tracker_unknown_key_fails_after_resigning(self):
        value = d2_receipt()
        value["definitions"]["boss"]["attack_tracker"]["unexpected"] = True
        resign(value)
        self.assertTrue(any("attack_tracker must contain exactly" in error for error in validate(value)))

    def test_d2_tracker_field_provenance_missing_key_fails(self):
        value = d2_receipt()
        del value["definitions"]["boss"]["attack_tracker_field_provenance"]["branch_range"]
        resign(value)
        self.assertTrue(any("attack_tracker_field_provenance must contain exactly" in error
                            for error in validate(value)))

    def test_d2_source_provenance_unknown_key_fails(self):
        value = d2_receipt()
        value["definitions"]["boss"]["source_provenance"]["unexpected"] = "not allowed"
        resign(value)
        self.assertTrue(any("source_provenance must contain exactly" in error for error in validate(value)))

    def test_payload_mutation_invalidates_digest(self):
        value = receipt()
        value["definitions"]["boss"]["stats"] = {"max_health": 999}
        self.assertTrue(any("does not match canonical payload" in e for e in validate(value)))

    def test_definition_identity_path_mismatch_fails(self):
        value = receipt()
        value["boss_definition"] = "/Game/Test/Other"
        self.assertTrue(any("does not match its definition snapshot" in e for e in validate(value)))

    def test_missing_provenance_fields_fail(self):
        value = receipt()
        del value["definitions"]["player"]["fields"]
        value["manifest_sha256"] = canonical_sha256({k: v for k, v in value.items() if k != "manifest_sha256"})
        self.assertTrue(any("snapshot missing fields" in e for e in validate(value)))

    def test_source_snapshot_hash_is_required_without_draft_provenance_mode(self):
        value = receipt()
        del value["source_snapshot_sha256"]
        value["manifest_sha256"] = canonical_sha256({k: v for k, v in value.items() if k != "manifest_sha256"})
        self.assertTrue(any("source_snapshot_sha256 is required" in e for e in validate(value)))

    def test_incomplete_field_provenance_fails(self):
        value = receipt()
        del value["definitions"]["boss"]["fields"][0]["source_site"]
        value["manifest_sha256"] = canonical_sha256({k: v for k, v in value.items() if k != "manifest_sha256"})
        self.assertTrue(any("missing provenance" in e for e in validate(value)))

    def test_duplicate_definition_paths_fail_even_with_new_digest(self):
        value = receipt()
        value["definitions"]["player"]["asset_path"] = value["definitions"]["boss"]["asset_path"]
        value["player_definition"] = value["boss_definition"]
        value["manifest_sha256"] = canonical_sha256({k: v for k, v in value.items() if k != "manifest_sha256"})
        self.assertTrue(any("must be distinct" in e for e in validate(value)))


if __name__ == "__main__":
    unittest.main()
