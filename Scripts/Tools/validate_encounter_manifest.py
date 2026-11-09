#!/usr/bin/env python3
"""Validate the canonical G044 membership receipt without Unreal or file writes."""
import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path


SCHEMA = "onebossfight.encounter-manifest/v1"
REQUIRED_FIELDS = {
    "schema", "definition_id", "presentation_id", "phase_two_aura_effect", "stats", "encounter_policy",
    "stagger_policy", "phase_flow", "fireball", "phase_dependencies", "stagger_profile",
    "dormant_wake", "bleed", "low_sweep", "shockwave", "heal_punish", "look",
    "close_clip_swap", "death", "phases", "skeleton", "animations", "fields",
}
REQUIRED_PROVENANCE = {
    "field_path", "type", "source_path", "source_sha256", "source_site",
    "origin", "precedence", "destination", "first_read", "witness",
}
DRAFT_ROOT_FIELDS = {
    "schema", "provenance_mode", "boss_definition", "player_definition",
    "initial_boss_phase", "definitions", "manifest_sha256",
}
ATTACK_TRACKER_KEYS = {
    "attacks", "branch_cone_degrees", "branch_range", "enabled", "veto_illegal_starts",
}
ATTACK_TIMING_KEYS = {
    "move_id", "montage_name", "fallback_montage_name", "montage_path", "authored_windup",
    "commit_time", "active_start_time", "active_end_time", "recovery_end_time",
    "track_turn_rate", "branch_stage", "clip_path",
}
ATTACK_TRACKER_FIELD_KEYS = {
    "attacks", "b_enabled", "b_veto_illegal_starts", "branch_range", "branch_cone_degrees",
}
TRACKER_PROVENANCE_VALUES = (
    "native default (effective reflected value matches class default; serialized presence is not distinguished)",
    "saved draft value",
)
PARRY_SLOW_MOTION_FIELDS = {
    "perfect_enabled": ("ParrySlowMotion.bPerfectEnabled", bool),
    "perfect_scale": ("ParrySlowMotion.PerfectScale", (int, float)),
    "perfect_seconds": ("ParrySlowMotion.PerfectSeconds", (int, float)),
    "normal_enabled": ("ParrySlowMotion.bNormalEnabled", bool),
    "normal_scale": ("ParrySlowMotion.NormalScale", (int, float)),
    "normal_seconds": ("ParrySlowMotion.NormalSeconds", (int, float)),
    "cooldown_seconds": ("ParrySlowMotion.CooldownSeconds", (int, float)),
}


def _validate_optional_parry_slow_motion(row, role, seen_fields, errors):
    group_paths = {path for path, _value_type in PARRY_SLOW_MOTION_FIELDS.values()}
    present_paths = group_paths & seen_fields
    if "parry_slow_motion" not in row:
        if present_paths:
            errors.append(role + " parry_slow_motion provenance must be absent or contain all seven fields")
        return
    group = row["parry_slow_motion"]
    if not isinstance(group, dict) or set(group) != set(PARRY_SLOW_MOTION_FIELDS):
        errors.append(role + " parry_slow_motion must contain exactly the seven supported fields")
        return
    if present_paths != group_paths:
        errors.append(role + " parry_slow_motion provenance must contain all seven fields when the optional group is present")
    valid_values = True
    for key, (_path, value_type) in PARRY_SLOW_MOTION_FIELDS.items():
        value = group.get(key)
        if value_type is bool:
            if type(value) is not bool:
                errors.append(role + " parry_slow_motion." + key + " must be boolean")
                valid_values = False
        elif type(value) not in value_type or not math.isfinite(value):
            errors.append(role + " parry_slow_motion." + key + " must be a finite number")
            valid_values = False
    if not valid_values:
        return
    if not (0.05 <= group["perfect_scale"] <= 1.0) or (group["perfect_enabled"] and group["perfect_scale"] >= 1.0):
        errors.append(role + " parry_slow_motion.perfect_scale is outside the native runtime range")
    if not (0.0 < group["perfect_seconds"] <= 5.0):
        errors.append(role + " parry_slow_motion.perfect_seconds is outside the native runtime range")
    if not (0.05 <= group["normal_scale"] <= 1.0) or (group["normal_enabled"] and group["normal_scale"] >= 1.0):
        errors.append(role + " parry_slow_motion.normal_scale is outside the native runtime range")
    if not (0.0 < group["normal_seconds"] <= 5.0):
        errors.append(role + " parry_slow_motion.normal_seconds is outside the native runtime range")
    if not (0.0 <= group["cooldown_seconds"] <= 30.0):
        errors.append(role + " parry_slow_motion.cooldown_seconds is outside the native runtime range")


def canonical_payload(receipt):
    return {key: value for key, value in receipt.items() if key != "manifest_sha256"}


def canonical_sha256(payload):
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _validate_attack_tracker(row, role, errors, draft_provenance_mode):
    required_row_keys = {"attack_tracker", "attack_tracker_provenance", "attack_tracker_field_provenance"}
    if draft_provenance_mode:
        missing = sorted(required_row_keys - set(row))
        extra = sorted(set(row) - REQUIRED_FIELDS - {"asset_path", "source_provenance"} - required_row_keys)
        if missing:
            errors.append(role + " snapshot missing attack tracker provenance: " + ", ".join(missing))
        if extra:
            errors.append(role + " snapshot has unknown keys: " + ", ".join(extra))
    if not (required_row_keys & set(row)):
        return

    tracker = row.get("attack_tracker")
    if not isinstance(tracker, dict):
        errors.append(role + " attack_tracker must be an object")
    else:
        if set(tracker) != ATTACK_TRACKER_KEYS:
            errors.append(role + " attack_tracker must contain exactly " + ", ".join(sorted(ATTACK_TRACKER_KEYS)))
        attacks = tracker.get("attacks")
        if not isinstance(attacks, list):
            errors.append(role + " attack_tracker.attacks must be an array")
        else:
            for index, attack in enumerate(attacks):
                where = role + " attack_tracker.attacks[" + str(index) + "]"
                if not isinstance(attack, dict):
                    errors.append(where + " must be an object")
                    continue
                if set(attack) != ATTACK_TIMING_KEYS:
                    errors.append(where + " must contain exactly the authored timing fields")
                    continue
                for key in ("move_id", "montage_name", "fallback_montage_name", "montage_path", "clip_path"):
                    if not isinstance(attack.get(key), str):
                        errors.append(where + "." + key + " must be text")
                for key in ("authored_windup", "branch_stage"):
                    if type(attack.get(key)) is not bool:
                        errors.append(where + "." + key + " must be boolean")
                for key in ("commit_time", "active_start_time", "active_end_time", "recovery_end_time", "track_turn_rate"):
                    if not _finite_number(attack.get(key)):
                        errors.append(where + "." + key + " must be a finite number")

        for key in ("branch_range", "branch_cone_degrees"):
            if not _finite_number(tracker.get(key)):
                errors.append(role + " attack_tracker." + key + " must be a finite number")
        for key in ("enabled", "veto_illegal_starts"):
            if type(tracker.get(key)) is not bool:
                errors.append(role + " attack_tracker." + key + " must be boolean")

    tracker_provenance = row.get("attack_tracker_provenance")
    if tracker_provenance not in TRACKER_PROVENANCE_VALUES:
        errors.append(role + " attack_tracker_provenance has an unsupported value")
    field_provenance = row.get("attack_tracker_field_provenance")
    if not isinstance(field_provenance, dict) or set(field_provenance) != ATTACK_TRACKER_FIELD_KEYS:
        errors.append(role + " attack_tracker_field_provenance must contain exactly " + ", ".join(sorted(ATTACK_TRACKER_FIELD_KEYS)))
    elif any(value not in TRACKER_PROVENANCE_VALUES or value != tracker_provenance
             for value in field_provenance.values()):
        errors.append(role + " attack_tracker_field_provenance values must match the supported tracker provenance")


def validate(receipt, source_snapshots_dir=None, project_root=None):
    errors = []
    if not isinstance(receipt, dict):
        return ["receipt root must be an object"]
    if receipt.get("schema") != SCHEMA:
        errors.append("schema must be " + SCHEMA)
    source_snapshot_hash = receipt.get("source_snapshot_sha256")
    draft_provenance_mode = receipt.get("provenance_mode") == "saved-draft-package-v1"
    if draft_provenance_mode and set(receipt) != DRAFT_ROOT_FIELDS:
        errors.append("saved-draft receipt must contain exactly " + ", ".join(sorted(DRAFT_ROOT_FIELDS)))
    if source_snapshot_hash is not None:
        if not isinstance(source_snapshot_hash, str) or re.fullmatch(r"[0-9a-f]{64}", source_snapshot_hash) is None:
            errors.append("source_snapshot_sha256 must be 64 lowercase hexadecimal characters")
        elif source_snapshots_dir is not None:
            snapshots_dir = Path(source_snapshots_dir)
            snapshots = sorted(snapshots_dir.glob("encounter_sources_*.json")) if snapshots_dir.is_dir() else []
            if not snapshots:
                errors.append("no timestamped Editor source snapshots exist under " + str(snapshots_dir))
            else:
                try:
                    newest_hash = hashlib.sha256(snapshots[-1].read_bytes()).hexdigest()
                    if newest_hash != source_snapshot_hash:
                        errors.append("source_snapshot_sha256 does not match newest snapshot " + snapshots[-1].name)
                except OSError as exc:
                    errors.append("cannot read newest source snapshot: " + str(exc))
    elif not draft_provenance_mode:
        errors.append("source_snapshot_sha256 is required unless provenance_mode is saved-draft-package-v1")
    if not isinstance(receipt.get("initial_boss_phase"), str) or not receipt.get("initial_boss_phase"):
        errors.append("initial_boss_phase is required")
    definitions = receipt.get("definitions")
    if not isinstance(definitions, dict) or set(definitions) != {"boss", "player"}:
        errors.append("definitions must contain exactly boss and player")
    else:
        paths = []
        for role in ("boss", "player"):
            row = definitions[role]
            if not isinstance(row, dict):
                errors.append(role + " definition snapshot must be an object")
                continue
            path = row.get("asset_path")
            if not isinstance(path, str) or not path.startswith("/Game/"):
                errors.append(role + " asset_path must be a /Game object path")
            else:
                paths.append(path)
            missing = sorted(REQUIRED_FIELDS - set(row))
            if missing:
                errors.append(role + " snapshot missing fields: " + ", ".join(missing))
            if row.get("schema") != 1:
                errors.append(role + " definition schema must equal 1")
            if not isinstance(row.get("definition_id"), str) or not row.get("definition_id"):
                errors.append(role + " definition_id is required")
            if not isinstance(row.get("presentation_id"), str) or not row.get("presentation_id"):
                errors.append(role + " presentation_id is required")
            if role == "boss" and not row.get("phases"):   # lead fix: the hero (target-only) definition has no phase records
                errors.append(role + " phases must be nonempty")
            if not row.get("skeleton") or not row.get("animations"):
                errors.append(role + " skeleton and animations are required")
            fields = row.get("fields")
            seen_fields = set()
            if not isinstance(fields, list) or not fields:
                errors.append(role + " provenance fields must be a nonempty array")
            else:
                for index, field in enumerate(fields):
                    where = role + " fields[" + str(index) + "]"
                    if not isinstance(field, dict):
                        errors.append(where + " must be an object")
                        continue
                    missing_provenance = sorted(REQUIRED_PROVENANCE - set(field))
                    if missing_provenance:
                        errors.append(where + " missing provenance: " + ", ".join(missing_provenance))
                        continue
                    field_path = field.get("field_path")
                    if not isinstance(field_path, str) or not field_path:
                        errors.append(where + " field_path is required")
                    elif field_path in seen_fields:
                        errors.append(where + " duplicates field_path " + field_path)
                    else:
                        seen_fields.add(field_path)
                    if re.fullmatch(r"[0-9a-f]{64}", str(field.get("source_sha256"))) is None:
                        errors.append(where + " source_sha256 must be 64 lowercase hexadecimal characters")
                    if any(not isinstance(field.get(key), str) or not field[key] for key in REQUIRED_PROVENANCE - {"source_sha256"}):
                        errors.append(where + " provenance values must be nonempty strings")
            _validate_optional_parry_slow_motion(row, role, seen_fields, errors)
            aura = row.get("phase_two_aura_effect")
            if aura not in (None, ""):
                if not isinstance(aura, dict) or not isinstance(aura.get("object_path"), str) or not aura["object_path"].startswith("/Game/"):
                    errors.append(role + " phase_two_aura_effect must be null or a /Game soft object path")
                elif "PhaseTwoAuraEffect" not in seen_fields:
                    errors.append(role + " PhaseTwoAuraEffect requires a matching provenance field")
            if draft_provenance_mode:
                _validate_attack_tracker(row, role, errors, draft_provenance_mode)
                provenance = row.get("source_provenance")
                required_source = {"asset_file_sha256", "dd27j_evidence_path", "dd27j_evidence_sha256", "attack_tracker_fields"}
                if not isinstance(provenance, dict) or set(provenance) != required_source:
                    errors.append(role + " source_provenance must contain exactly " + ", ".join(sorted(required_source)))
                else:
                    if provenance.get("attack_tracker_fields") != row.get("attack_tracker_field_provenance"):
                        errors.append(role + " source_provenance.attack_tracker_fields must match attack_tracker_field_provenance")
                    if re.fullmatch(r"[0-9a-f]{64}", str(provenance.get("asset_file_sha256", ""))) is None:
                        errors.append(role + " asset_file_sha256 must be 64 lowercase hexadecimal characters")
                    if re.fullmatch(r"[0-9a-f]{64}", str(provenance.get("dd27j_evidence_sha256", ""))) is None:
                        errors.append(role + " dd27j_evidence_sha256 must be 64 lowercase hexadecimal characters")
                    evidence_path = provenance.get("dd27j_evidence_path")
                    if (not isinstance(evidence_path, str) or not evidence_path or
                            Path(evidence_path).is_absolute() or ".." in Path(evidence_path).parts):
                        errors.append(role + " dd27j_evidence_path must be a safe project-relative path")
                    if project_root is not None:
                        try:
                            root = Path(project_root).resolve(strict=True)
                            asset_path = row.get("asset_path")
                            if not isinstance(asset_path, str) or not asset_path.startswith("/Game/"):
                                raise ValueError("asset_path is not a /Game object path")
                            package = asset_path.split(".", 1)[0]
                            package_file = (root / "Content" / (package[len("/Game/"):] + ".uasset")).resolve(strict=True)
                            package_file.relative_to(root)
                            if hashlib.sha256(package_file.read_bytes()).hexdigest() != provenance.get("asset_file_sha256"):
                                errors.append(role + " asset_file_sha256 does not match " + str(package_file))
                            if isinstance(evidence_path, str):
                                evidence_file = (root / Path(evidence_path)).resolve(strict=True)
                                evidence_file.relative_to(root)
                                if hashlib.sha256(evidence_file.read_bytes()).hexdigest() != provenance.get("dd27j_evidence_sha256"):
                                    errors.append(role + " dd27j_evidence_sha256 does not match " + evidence_path)
                        except (OSError, ValueError) as exc:
                            errors.append(role + " source provenance file check failed: " + str(exc))
        if len(paths) == 2 and paths[0] == paths[1]:
            errors.append("boss and player definition assets must be distinct")
        for role, key in (("boss", "boss_definition"), ("player", "player_definition")):
            snapshot_path = definitions[role].get("asset_path") if isinstance(definitions.get(role), dict) else None
            # The root fields are package paths; the readback snapshots cite full object paths.
            snapshot_package = snapshot_path.split(".", 1)[0] if isinstance(snapshot_path, str) else None
            if snapshot_package is not None and receipt.get(key) != snapshot_package:
                errors.append(key + " does not match its definition snapshot")
    digest = receipt.get("manifest_sha256")
    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        errors.append("manifest_sha256 must be 64 lowercase hexadecimal characters")
    else:
        try:
            actual = canonical_sha256(canonical_payload(receipt))
            if digest != actual:
                errors.append("manifest_sha256 does not match canonical payload (actual " + actual + ")")
        except (TypeError, ValueError) as exc:
            errors.append("payload cannot be canonically serialized: " + str(exc))
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path, help="G044 encounter manifest receipt JSON")
    parser.add_argument("--source-snapshots", type=Path,
                        help="legacy receipt mode: directory containing encounter_sources_*.json")
    parser.add_argument("--project-root", type=Path,
                        help="project root used to verify draft package/evidence hashes (default: inferred from Saved/G044 receipt path)")
    args = parser.parse_args(argv)
    try:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        return 2
    project_root = args.project_root
    if project_root is None:
        try:
            project_root = args.receipt.resolve().parents[2]
        except IndexError:
            project_root = None
    snapshots_dir = args.source_snapshots
    if "source_snapshot_sha256" in receipt and snapshots_dir is None:
        snapshots_dir = args.receipt.parent / "source_snapshots"
    errors = validate(receipt, source_snapshots_dir=snapshots_dir, project_root=project_root)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        return 1
    print("PASS: " + str(args.receipt) + " sha256=" + receipt["manifest_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
