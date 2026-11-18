"""Author the approved O1 Stats/Phase_1 values and truthful draft provenance.

Dry is the default. Write/readback are only exposed by the C-1155 locked runner.
O1 values receive OwnerDecision rows; every other required BossCore path is a
DraftPreimage row tied to the exact backed-up package and reflected value.
"""
import hashlib
import json
import math
import os
import re
import sys
from functools import lru_cache
from pathlib import Path
import unreal


BOSS_PATH = "/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_Draft"
PHASE_ID = "Phase_1"
WRITE = os.environ.get("BK56_AUTHOR_PHASE_WRITE") == "1"
READBACK = os.environ.get("BK56_AUTHOR_PHASE_READBACK") == "1"
INPUTS = {
    "entry_health_fraction": "Phases[Phase_1].EntryHealthFraction",
    "speed_multiplier": "Phases[Phase_1].SpeedMultiplier",
    "rate_multiplier": "Phases[Phase_1].RateMultiplier",
    "attack_multiplier": "Phases[Phase_1].AttackMultiplier",
}
STATS = {
    "max_health": "Stats.MaxHealth",
    "max_posture": "Stats.MaxPosture",
    "posture_regen_delay": "Stats.PostureRegenDelay",
    "posture_regen_rate": "Stats.PostureRegenRate",
}
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / "Scripts" / "Tools"))
from sevarog_o1_inputs import approved_float_matches, load_approved_values
from sevarog_boss_core_required_fields import extract_required_paths


def require(ok, message):
    if not ok:
        raise RuntimeError("[BK56Phase] REFUSED: " + message)


def phase_values(phase):
    return {field: float(phase.get_editor_property(field)) for field in INPUTS}


def validate_values(values):
    fraction = values["entry_health_fraction"]
    require(math.isfinite(fraction) and 0.0 < fraction <= 1.0,
            "EntryHealthFraction must be finite and in (0,1]")
    for field in ("speed_multiplier", "rate_multiplier", "attack_multiplier"):
        value = values[field]
        require(math.isfinite(value) and value > 0.0, "%s must be finite and positive" % field)


def approved_inputs():
    approved = load_approved_values(REPO)
    stats = {field: float(approved[path]) for field, path in STATS.items()}
    phase = {field: float(approved[path]) for field, path in INPUTS.items()}
    validate_values(phase)
    return approved, stats, phase


def snake(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def resolve_reflected_property_name(target, prop_name):
    # Determine candidates in canonical preference order
    if prop_name.startswith("b") and len(prop_name) > 1 and prop_name[1].isupper():
        # For b-prefixed bool: stripped-b snake_case first, then unstripped snake_case, then raw
        candidates = [
            snake(prop_name[1:]),
            snake(prop_name),
            prop_name[1:],
            prop_name,
        ]
    else:
        # Non-b property: snake_case first, exact-case fallback
        candidates = [
            snake(prop_name),
            prop_name,
        ]

    # Deduplicate candidates preserving order
    unique_candidates = []
    for c in candidates:
        if c not in unique_candidates:
            unique_candidates.append(c)

    getter = getattr(target, "get_editor_property", None)

    # Test in canonical preference order; return the first matching canonical candidate
    for c in unique_candidates:
        try:
            if callable(getter):
                target.get_editor_property(c)
            else:
                getattr(target, c)
            return c
        except Exception:
            continue

    # Fail closed if none of the candidate names can be resolved
    require(False,
            "Failed to resolve reflected property for '%s' on %s (tried candidates=%s)" %
            (prop_name, type(target).__name__, unique_candidates))


def get_reflected_property(target, prop_name):
    attr = resolve_reflected_property_name(target, prop_name)
    getter = getattr(target, "get_editor_property", None)
    if callable(getter):
        return target.get_editor_property(attr)
    return getattr(target, attr)


def resolve_reflected_value(boss, path):
    if path.startswith("Phases[Phase_1]."):
        phases = list(boss.get_editor_property("phases"))
        rows = [row for row in phases if str(row.get_editor_property("phase_id")) == PHASE_ID]
        require(len(rows) == 1, "expected exactly one Phase_1 while capturing %s" % path)
        prop = path.split("].", 1)[1]
        return get_reflected_property(rows[0], prop)
    group, prop = path.split(".", 1)
    config = get_reflected_property(boss, group)
    return get_reflected_property(config, prop)


def stable_value(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        require(math.isfinite(value), "draft preimage contains a non-finite value")
        return format(value, ".9g")
    if isinstance(value, (list, tuple)):
        return json.dumps([stable_value(item) for item in value], ensure_ascii=False, separators=(",", ":"))
    getter = getattr(value, "get_path_name", None)
    if callable(getter):
        try:
            path = str(getter()).strip()
            if path:
                return path
        except Exception:
            pass
    exporter = getattr(value, "export_text", None)
    if callable(exporter):
        try:
            text = str(exporter()).strip()
            if text:
                return re.sub(r"\s*\(0x[0-9a-fA-F]+\)", "", text)
        except Exception:
            pass
    formatter = getattr(value, "to_string", None)
    if callable(formatter):
        try:
            text = str(formatter()).strip()
            if text:
                return re.sub(r"\s*\(0x[0-9a-fA-F]+\)", "", text)
        except Exception:
            pass
    raw = str(value).strip()
    return re.sub(r"\s*\(0x[0-9a-fA-F]+\)", "", raw)


def type_name(value):
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int) and not isinstance(value, bool):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, (list, tuple)):
        return "array"
    return type(value).__name__


def evidence_context():
    evidence = os.environ.get("SEVAROG_O1_EVIDENCE_DIR")
    require(evidence, "locked runner evidence directory is required")
    run_dir = Path(evidence).resolve()
    base_evidence_dir = (REPO / "Saved" / "B_SEVAROG_O1").resolve()
    require(run_dir.parent == base_evidence_dir,
            "run directory must be a direct child of Saved/B_SEVAROG_O1")
    require(re.fullmatch(r"Run_[A-Za-z0-9_-]+", run_dir.name) is not None,
            "run directory name malformed")
    manifest_path = (run_dir / "rollback_manifest.json").resolve()
    require(manifest_path.is_file() and manifest_path.parent == run_dir,
            "rollback manifest missing or misplaced: %s" % manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    expected_rel = Path("Content/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_Draft.uasset")
    expected_source = (REPO / expected_rel).resolve()
    expected_backup_dir = (run_dir / "rollback_files").resolve()
    expected_backup = (expected_backup_dir / "DA_Boss_Sevarog_Draft.uasset").resolve()
    rows = []
    for row in manifest.get("backups", []):
        src = Path(row.get("source", "")).resolve()
        bak = Path(row.get("backup", "")).resolve()
        if src == expected_source and bak == expected_backup and bak.is_relative_to(expected_backup_dir):
            rows.append(row)
    require(len(rows) == 1, "rollback manifest must identify exactly one Sevarog draft package backup")
    row = rows[0]
    backup = Path(row["backup"]).resolve(strict=True)
    digest = hashlib.sha256(backup.read_bytes()).hexdigest()
    require(digest.lower() == str(row.get("sha256", "")).lower(), "draft preimage backup hash mismatch")
    owner_manifest = REPO / "Scripts" / "Editor" / "sevarog_o1_inputs.json"
    owner_hash = hashlib.sha256(owner_manifest.read_bytes()).hexdigest()
    return run_dir, run_dir.name, str(expected_rel).replace("\\", "/"), digest, owner_hash


@lru_cache(maxsize=8)
def verified_preimage_hash(run_id):
    require(re.fullmatch(r"Run_[A-Za-z0-9_-]+", run_id) is not None,
            "preimage witness run id malformed")
    witness_dir = (REPO / "Saved" / "B_SEVAROG_O1" / run_id).resolve()
    base_evidence_dir = (REPO / "Saved" / "B_SEVAROG_O1").resolve()
    require(witness_dir.parent == base_evidence_dir,
            "witness run directory must be a direct child of Saved/B_SEVAROG_O1")
    manifest_path = (witness_dir / "rollback_manifest.json").resolve()
    require(manifest_path.is_file() and manifest_path.parent == witness_dir,
            "preimage witness rollback receipt is missing or misplaced: " + run_id)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    expected_rel = Path("Content/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_Draft.uasset")
    expected_source = (REPO / expected_rel).resolve()
    expected_backup_dir = (witness_dir / "rollback_files").resolve()
    expected_backup = (expected_backup_dir / "DA_Boss_Sevarog_Draft.uasset").resolve()
    rows = []
    for row in manifest.get("backups", []):
        src = Path(row.get("source", "")).resolve()
        bak = Path(row.get("backup", "")).resolve()
        if src == expected_source and bak == expected_backup and bak.is_relative_to(expected_backup_dir):
            rows.append(row)
    require(len(rows) == 1, "preimage witness receipt has no unique Sevarog backup: " + run_id)
    row = rows[0]
    backup = Path(row["backup"]).resolve(strict=True)
    digest = hashlib.sha256(backup.read_bytes()).hexdigest()
    require(digest.lower() == str(row.get("sha256", "")).lower(),
            "preimage witness backup hash mismatch: " + run_id)
    return digest


def make_row(field_path, value, source_path, source_hash, source_site, origin,
             precedence, destination, first_read, witness, units="reflected value; no unit conversion"):
    row_class = getattr(unreal, "RPGParityField", None)
    require(row_class is not None, "FRPGParityField reflection is unavailable")
    row = row_class()
    values = {
        "field_path": field_path,
        "value": stable_value(value),
        "type": type_name(value),
        "units": units,
        "source_path": source_path,
        "source_sha256": source_hash,
        "source_site": source_site,
        "origin": origin,
        "precedence": precedence,
        "destination": destination,
        "first_read": first_read,
        "witness": witness,
    }
    for name, item in values.items():
        row.set_editor_property(name, item)
    return row


def field_rows(boss, approved, approved_stats, approved_phase, package_path,
               preimage_hash, owner_hash, run_id):
    required = extract_required_paths(REPO)
    require(len(required) == 115, "BossCore required path count changed: %d" % len(required))
    owner_values = {path: float(value) for path, value in approved.items()}
    owner_paths = set(owner_values)
    require(owner_paths.issubset(required), "O1-approved paths are not a subset of BossCore requirements")
    result = []
    for path in sorted(required):
        if path in owner_paths:
            value = owner_values[path]
            if path.startswith("Stats."):
                prop = path.split(".", 1)[1]
                destination = "FRPGParticipantConfig.Stats.%s" % prop
                first_read = "RPGCombatHydration::CompileParticipantImpl Stats validation"
                unit = {"Stats.MaxHealth": "health points", "Stats.MaxPosture": "posture points",
                        "Stats.PostureRegenDelay": "seconds", "Stats.PostureRegenRate": "posture points/second"}[path]
            else:
                prop = path.rsplit(".", 1)[1]
                dest = {"EntryHealthFraction": "PhaseTwoHealthFraction", "SpeedMultiplier": "MovementScale",
                        "RateMultiplier": "AttackRateScale", "AttackMultiplier": "DamageScale"}[prop]
                destination = "URPGBossPhases.%s" % dest
                first_read = "RPGBossPhasesClusterAdapters::ConfigurePhasesCluster"
                unit = "ratio"
            result.append(make_row(
                path, value, "Scripts/Editor/sevarog_o1_inputs.json", owner_hash,
                "Documentation/DECISIONS.md: O1 / X-1991 Sevarog values approved (C-1619)",
                "OwnerDecision", "owner-approved O1 value controls this typed input",
                destination, first_read,
                "%s locked stage readback matched the O1-approved value" % run_id, unit))
            continue

        current = resolve_reflected_value(boss, path)
        prop_path = path
        group, _, prop = path.partition(".")
        destination = "FRPGParticipantConfig.%s.%s" % (snake(group), snake(prop))
        result.append(make_row(
            path, current, package_path, preimage_hash, prop_path, "DraftPreimage",
            "records the saved draft value only; no owner approval; O1 overrides only its eight paths",
            destination, "RPGCombatHydration::CompileParticipantImpl then FRPGHydrationPreflight path membership",
            run_id))
    return result


def row_snapshot(row):
    names = ("field_path", "value", "type", "units", "source_path", "source_sha256", "source_site",
             "origin", "precedence", "destination", "first_read", "witness")
    return {name: str(row.get_editor_property(name)) for name in names}


def write_plan_receipt(run_dir, run_id, rows, preimage_hash, owner_hash):
    snapshots = [row_snapshot(row) for row in rows]
    draft_hashes = {item["source_sha256"].lower() for item in snapshots
                    if item["origin"] == "DraftPreimage"}
    if len(draft_hashes) == 1:
        preimage_hash = next(iter(draft_hashes))
    owner_hashes = {item["source_sha256"].lower() for item in snapshots
                    if item["origin"] == "OwnerDecision"}
    if len(owner_hashes) == 1:
        owner_hash = next(iter(owner_hashes))
    receipt = {
        "schema": "onebossfight.sevarog-o1-field-plan/v1",
        "run": run_id,
        "asset": BOSS_PATH,
        "required_path_count": len(rows),
        "draft_preimage_package_sha256": preimage_hash,
        "owner_o1_manifest_sha256": owner_hash,
        "rows": snapshots,
        "limitation": "DraftPreimage rows record observed existing values only; they are not owner approval.",
    }
    target = run_dir / "field_manifest_plan.json"
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(target)
    lines = [
        "# Sevarog O1 / DraftPreimage field manifest",
        "",
        "Run: `%s`" % run_id,
        "",
        "Draft package preimage SHA-256: `%s`" % preimage_hash,
        "",
        "Owner O1 manifest SHA-256: `%s`" % owner_hash,
        "",
        "DraftPreimage rows document the saved draft values seen by the locked Editor stage. They are not owner approval.",
        "",
        "| Field path | Reflected value | Origin | Type | Source SHA-256 |",
        "|---|---|---|---|---|",
    ]
    for item in snapshots:
        def cell(value):
            return str(value).replace("|", "\\|").replace("\n", " ")
        lines.append("| `%s` | `%s` | %s | `%s` | `%s` |" % (
            cell(item["field_path"]), cell(item["value"]), cell(item["origin"]),
            cell(item["type"]), cell(item["source_sha256"])))
    md_path = run_dir / "field_manifest_plan.md"
    md_temp = md_path.with_suffix(".md.tmp")
    md_temp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    md_temp.replace(md_path)


def main():
    approved, expected_stats, expected_phase = approved_inputs()
    run_dir, run_id, package_path, preimage_hash, owner_hash = evidence_context()
    boss = unreal.EditorAssetLibrary.load_asset(BOSS_PATH)
    require(boss is not None, "Sevarog draft boss definition is unavailable")
    phases = list(boss.get_editor_property("phases"))
    ids = [str(item.get_editor_property("phase_id")) for item in phases]
    if PHASE_ID in ids:
        require(ids.count(PHASE_ID) == 1, "Phase_1 is duplicated")
        phase = phases[ids.index(PHASE_ID)]
    else:
        require(WRITE, "required Phase_1 row is absent; explicit locked write is required")
        phase_class = getattr(unreal, "RPGPhaseConfig", None)
        require(phase_class is not None, "FRPGPhaseConfig reflection is unavailable")
        phase = phase_class()
        phase.set_editor_property("phase_id", PHASE_ID)
        phases.append(phase)
        # Make the new row visible to the read-only reflection capture. This only
        # changes the in-memory object; the locked write stage performs the save.
        boss.set_editor_property("phases", phases)
    stats = boss.get_editor_property("stats")
    current_stats = {key: float(stats.get_editor_property(key)) for key in STATS}
    current_phase = phase_values(phase) if PHASE_ID in ids else {}
    values_match = (all(approved_float_matches(current_stats[key], value)
                        for key, value in expected_stats.items())
                    and PHASE_ID in ids
                    and all(approved_float_matches(current_phase[key], value)
                            for key, value in expected_phase.items()))
    current_rows = list(boss.get_editor_property("fields"))

    if current_rows:
        require(len(current_rows) == 115, "existing Fields count is %d, expected 115; refusing replacement" % len(current_rows))
        # On readback/re-run, the original manifest's hashes and witness are retained; every
        # preimage Value must still equal the current reflected field value.
        by_path = {str(row.get_editor_property("field_path")): row for row in current_rows}
        require(len(by_path) == len(current_rows), "existing Fields contains duplicate paths")
        required = extract_required_paths(REPO)
        require(set(by_path) == set(required), "existing Fields path set differs from BossCore requirements")
        for path in required - set(approved):
            row = by_path[path]
            require(str(row.get_editor_property("origin")) == "DraftPreimage",
                    "non-O1 field has wrong provenance origin: " + path)
            require(str(row.get_editor_property("source_path")) == package_path,
                    "preimage source path mismatch: " + path)
            require(re.fullmatch(r"[0-9a-fA-F]{64}", str(row.get_editor_property("source_sha256"))) is not None,
                    "preimage source hash malformed: " + path)
            witness = str(row.get_editor_property("witness"))
            require(re.fullmatch(r"Run_[A-Za-z0-9_-]+", witness) is not None,
                    "preimage witness run id malformed: " + path)
            require(str(row.get_editor_property("source_sha256")).lower() == verified_preimage_hash(witness).lower(),
                    "preimage hash does not match the witnessed package backup: " + path)
            require(str(row.get_editor_property("value")) == stable_value(resolve_reflected_value(boss, path)),
                    "current draft value differs from captured preimage for " + path)
        for path in set(approved):
            row = by_path[path]
            require(str(row.get_editor_property("origin")) == "OwnerDecision",
                    "O1 field has wrong provenance origin: " + path)
            require(str(row.get_editor_property("source_path")) == "Scripts/Editor/sevarog_o1_inputs.json",
                    "O1 source path mismatch: " + path)
            require(str(row.get_editor_property("source_sha256")).lower() == owner_hash.lower(),
                    "O1 source manifest hash mismatch: " + path)
            require(approved_float_matches(float(row.get_editor_property("value")), approved[path]),
                    "O1 field metadata value mismatch: " + path)
        expected_rows = current_rows
    else:
        expected_rows = field_rows(boss, approved, expected_stats, expected_phase,
                                   package_path, preimage_hash, owner_hash, run_id)

    if READBACK:
        require(values_match, "readback Stats/Phase_1 values do not match O1")
        require(len(current_rows) == 115, "readback field count is not 115")
        required = extract_required_paths(REPO)
        by_path = {str(row.get_editor_property("field_path")): row for row in current_rows}
        require(set(by_path) == set(required), "readback field path set differs from BossCore requirements")
        for path in required:
            row = by_path[path]
            for name in ("type", "source_path", "source_sha256", "source_site", "origin", "precedence",
                         "destination", "first_read", "witness", "units"):
                require(bool(str(row.get_editor_property(name)).strip()),
                        "readback row lacks %s: %s" % (name, path))
            require(re.fullmatch(r"[0-9a-fA-F]{64}", str(row.get_editor_property("source_sha256"))) is not None,
                    "readback row source hash malformed: " + path)
            if path not in approved:
                require(str(row.get_editor_property("value")) == stable_value(resolve_reflected_value(boss, path)),
                        "readback preimage value changed: " + path)
        unreal.log("[BK56Phase] READBACK_PASS boss=%s stats=%s phase=%s fields=%d required_paths=%d" %
                   (BOSS_PATH, expected_stats, expected_phase, len(current_rows), len(required)))
        write_plan_receipt(run_dir, run_id, current_rows, preimage_hash, owner_hash)
        return

    if not WRITE:
        write_plan_receipt(run_dir, run_id, expected_rows, preimage_hash, owner_hash)
        unreal.log("[BK56Phase] DRY_RUN boss=%s stats_match=%s phase_present=%s field_count=%d planned_field_count=%d required_paths=%d saves=0" %
                   (BOSS_PATH, values_match, PHASE_ID in ids, len(current_rows), len(expected_rows), len(extract_required_paths(REPO))))
        return

    if values_match and len(current_rows) == 115:
        write_plan_receipt(run_dir, run_id, current_rows, preimage_hash, owner_hash)
        unreal.log("[BK56Phase] RESULT ALREADY_CURRENT boss=%s stats=%s phase=%s fields=%d saves=0" %
                   (BOSS_PATH, expected_stats, expected_phase, len(current_rows)))
        return

    if not values_match:
        for field, value in expected_stats.items():
            stats.set_editor_property(field, value)
        boss.set_editor_property("stats", stats)
        phase.set_editor_property("phase_id", PHASE_ID)
        for field, value in expected_phase.items():
            phase.set_editor_property(field, value)
        boss.set_editor_property("phases", phases)
    if not current_rows:
        boss.set_editor_property("fields", expected_rows)
    elif not values_match:
        require(False, "existing manifest cannot be reconciled with changed O1 values; preserving asset")
    require(unreal.EditorAssetLibrary.save_loaded_asset(boss), "saving O1 Stats/Phase_1/Fields failed")
    saved = unreal.EditorAssetLibrary.load_asset(BOSS_PATH)
    require(saved is not None, "saved asset could not be reloaded")
    require(len(list(saved.get_editor_property("fields"))) == 115, "post-save manifest count is not 115")
    write_plan_receipt(run_dir, run_id, list(saved.get_editor_property("fields")), preimage_hash, owner_hash)
    unreal.log("[BK56Phase] O1_AUTHORED boss=%s stats=%s phase=%s fields=115 source_preimage_sha256=%s" %
               (BOSS_PATH, expected_stats, expected_phase, preimage_hash))


if __name__ == "__main__":
    main()
