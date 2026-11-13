"""BK-92/93 (C, implementer; X-2002): PROPOSAL-ONLY planner for an in-place Sevarog definition repair.

Design input for lead review. This module is pure Python: it never imports Unreal, never reads or writes assets, never
touches locks, and never executes a step. It turns (a validated owner approval envelope result, a synthetic readback
snapshot of the existing DA_Boss_Sevarog_Draft, a run context) into either a refusal or a data-only plan, and checks a
synthetic after-readback against that plan. An editor-side executor (NOT part of this batch) would carry the plan out.

Target (reflected, RPGEncounterBinding.h): URPGBossDefinition (:352) with
  Stats (:361)  FRPGBossStatsConfig (:26)  -> max_health, max_posture, posture_regen_delay, posture_regen_rate
  Phases (:381) TArray<FRPGPhaseConfig> (:322) -> phase_id, entry_health_fraction, speed_multiplier, rate_multiplier, attack_multiplier
  Fields (:385) TArray<FRPGParityField> (:334) -> one provenance record per written field path
Field paths: Stats.* (RPGBossStatsAdapters.h:41-44), Phases[Phase_1].* (RPGBossPhaseAdapters.cpp:102).
Native ranges: RPGBossStatsAdapters.cpp:74/:84 (+ floor RPGBossStatsAdapters.h:38), RPGBossPhaseAdapters.cpp:122/:131.

Safety boundary: in place only (the referenced asset is preserved; create, replace, delete and recreate are refused);
every value must come from a valid, complete envelope (no default is ever supplied); a write needs both C-1155 locks
under one token and a backup whose hash equals the asset file's before-hash; the plan ends with a readback that compares
every saved property and releases the locks on every path.
"""
import copy
import math
import re

ASSET_PATH = "/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_Draft"
PHASE_ID = "Phase_1"
STATS = {  # field path -> (reflected property, low, low_inclusive)
    "Stats.MaxHealth": ("max_health", 1.0, False),
    "Stats.MaxPosture": ("max_posture", 0.0, False),
    "Stats.PostureRegenDelay": ("posture_regen_delay", 0.0, True),
    "Stats.PostureRegenRate": ("posture_regen_rate", 0.0, True),
}
PHASE = {  # field path -> (reflected property, low, low_inclusive, high)
    "Phases[Phase_1].EntryHealthFraction": ("entry_health_fraction", 0.0, False, 1.0),
    "Phases[Phase_1].SpeedMultiplier": ("speed_multiplier", 0.0, False, None),
    "Phases[Phase_1].RateMultiplier": ("rate_multiplier", 0.0, False, None),
    "Phases[Phase_1].AttackMultiplier": ("attack_multiplier", 0.0, False, None),
}
PHASE_ID_FIELD = "Phases[Phase_1].PhaseId"
REQUIRED = set(STATS) | set(PHASE) | {PHASE_ID_FIELD}
FLOAT_TOLERANCE = 1e-5  # the properties are float32
STEPS_WRITE = ("verify_locks", "verify_backup", "load_existing_asset", "apply_stats", "apply_phase_1",
               "upsert_field_records", "save_in_place", "readback_verify", "release_locks")
STEPS_DRY = ("load_existing_asset", "diff_only", "release_nothing")


# BK-193/194 (X-2042): one contract shared with the executor lock acquisition (sevarog_executor_contract.TOKEN) and the
# receipt validator (validate_sevarog_executor_receipt._safe_backup_path); parity is pinned by test_bk191_195_*.
OWNER_TOKEN = re.compile(r"[0-9a-f]{32}")
BACKUP_PREFIX = "Docs/BossCombatReview/Execution/"


def safe_backup_path(value):
    """Repo-relative backup path below BACKUP_PREFIX: no backslash, colon, control char, or empty/./.. segment."""
    if not isinstance(value, str) or not value.startswith(BACKUP_PREFIX) or "\\" in value or ":" in value:
        return False
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        return False
    return all(part not in ("", ".", "..") for part in value.split("/"))


def _finite(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except (OverflowError, TypeError, ValueError):
        return False


def _finite_in_range(value, low, low_inclusive, high=None):
    if not _finite(value):
        return False
    if value < low or (value == low and not low_inclusive):
        return False
    return high is None or value <= high


def _approved_values(envelope_result, errors):
    """Field path -> approved value, only from a valid and complete envelope result (no defaults)."""
    if not isinstance(envelope_result, dict) or envelope_result.get("valid") is not True:
        errors.append("owner approval envelope is absent or invalid")
        return {}
    unresolved = envelope_result.get("unresolved")
    rejected = envelope_result.get("rejected")
    approvals = envelope_result.get("approved_for_review")
    if not isinstance(unresolved, list) or not isinstance(rejected, list) or not isinstance(approvals, list):
        errors.append("envelope result lists are malformed")
        return {}
    if unresolved:
        errors.append("envelope has unresolved fields: %s" % ", ".join(map(str, unresolved)))
    if rejected:
        errors.append("envelope rejects fields without an approved alternative: %s" % ", ".join(map(str, rejected)))
    values = {}
    for entry in approvals:
        field = entry.get("field_path") if isinstance(entry, dict) else None
        if not isinstance(field, str) or field not in REQUIRED:
            errors.append("approval has an unknown or malformed field path: %r" % (field,))
            continue
        decision = entry.get("decision")
        if decision not in ("APPROVE_CANDIDATE", "APPROVE_VALUE"):
            errors.append("%s does not carry an approval decision" % field)
            continue
        if field in values:
            errors.append("duplicate approval for %s" % field)
        values[field] = entry.get("value")
    missing, extra = REQUIRED - set(values), set(values) - REQUIRED
    if missing:
        errors.append("partial approval refused; missing: %s" % ", ".join(sorted(missing)))
    if extra:
        errors.append("approval for unknown fields refused: %s" % ", ".join(sorted(str(e) for e in extra)))
    for field, (_, low, inclusive) in STATS.items():
        if field in values and not _finite_in_range(values[field], low, inclusive):
            errors.append("%s value %r is not finite or outside the native range" % (field, values[field]))
    for field, (_, low, inclusive, high) in PHASE.items():
        if field in values and not _finite_in_range(values[field], low, inclusive, high):
            errors.append("%s value %r is not finite or outside the native range" % (field, values[field]))
    if PHASE_ID_FIELD in values and values[PHASE_ID_FIELD] != PHASE_ID:
        errors.append("%s must be %s" % (PHASE_ID_FIELD, PHASE_ID))
    return values


def plan_repair(envelope_result, snapshot, context, owner_source=None):
    """Return {"accepted", "errors", "mode", "steps", "writes", "field_records", "before_sha256"}; never executes."""
    errors = []
    plan = {"accepted": False, "errors": errors, "mode": None, "steps": [], "writes": [], "field_records": [], "before_sha256": None}
    values = _approved_values(envelope_result, errors)

    # Existing asset only: in-place update of the referenced draft.
    if not isinstance(snapshot, dict):
        errors.append("asset readback snapshot is required")
        return plan
    if snapshot.get("asset_path") != ASSET_PATH:
        errors.append("target must be %s" % ASSET_PATH)
    if snapshot.get("exists") is not True:
        errors.append("the draft must already exist; creating a definition is out of scope (in-place repair only)")
    before = snapshot.get("file_sha256")
    if not (isinstance(before, str) and len(before) == 64 and all(c in "0123456789abcdef" for c in before)):
        errors.append("snapshot needs the asset file's before-hash (64 lowercase hex)")
    phases = snapshot.get("phases")
    if not isinstance(phases, list):
        errors.append("snapshot phases must be a list")
        phases = []
    phase_rows = [p for p in phases if isinstance(p, dict) and p.get("phase_id") == PHASE_ID]
    if len(phase_rows) > 1:
        errors.append("snapshot has %d Phase_1 rows; ambiguous in-place target refused" % len(phase_rows))

    # Run context.
    if not isinstance(context, dict):
        errors.append("run context is required")
        return plan
    operation, mode = context.get("operation"), context.get("mode")
    if operation != "in_place_update":
        errors.append("operation %r refused; only in_place_update is allowed (no create/replace/delete/recreate)" % operation)
    if mode not in ("dry_run", "write"):
        errors.append("mode must be dry_run or write")
    if mode == "write":
        locks = context.get("locks") or {}
        if not isinstance(locks, dict):
            locks = {}
        token = locks.get("owner_token")
        if not (locks.get("root_held") is True and locks.get("execution_held") is True and isinstance(token, str) and token):
            errors.append("write needs both C-1155 locks held under one owner token")
        elif not OWNER_TOKEN.fullmatch(token):
            errors.append("write owner token must be 32 lowercase hex (the executor lock-acquisition contract)")
        backup = context.get("backup") or {}
        if not isinstance(backup, dict):
            backup = {}
        if not backup.get("path"):
            errors.append("write needs a file backup of the draft before any change")
        else:
            if not safe_backup_path(backup.get("path")):
                errors.append("backup path must be a safe repo-relative path below %s" % BACKUP_PREFIX)
            if backup.get("sha256") != before:
                errors.append("backup sha256 must equal the asset file's before-hash")
        if context.get("explicit_write") is not True:
            errors.append("write needs an explicit write flag (never implied)")
    if not (isinstance(owner_source, dict) and owner_source.get("sender") == "Owner"
            and isinstance(owner_source.get("message_id"), str) and re.fullmatch(r"(?:O|H)-[0-9]+", owner_source["message_id"])
            and isinstance(owner_source.get("reply_sha256"), str)
            and re.fullmatch(r"[0-9a-f]{64}", owner_source["reply_sha256"])
            and owner_source.get("path") == "Documentation/TEAM_MAILBOX.md"):
        errors.append("owner source must be a verified Owner message id, mailbox path, and reply SHA-256")
    if not isinstance(snapshot.get("stats"), dict):
        errors.append("snapshot stats must be an object")
    if not isinstance(snapshot.get("fields", []), list):
        errors.append("snapshot fields must be a list")

    if errors:
        return plan

    writes = []
    for field, (prop, _, _) in STATS.items():
        writes.append({"field_path": field, "target": "stats." + prop, "from": (snapshot.get("stats") or {}).get(prop), "to": float(values[field])})
    row_action = "update_existing_row" if phase_rows else "append_row"
    writes.append({"field_path": PHASE_ID_FIELD, "target": "phases[Phase_1].phase_id",
                   "from": PHASE_ID if phase_rows else None, "to": PHASE_ID, "row_action": row_action})
    for field, (prop, _, _, _) in PHASE.items():
        current = phase_rows[0].get(prop) if phase_rows else None
        writes.append({"field_path": field, "target": "phases[Phase_1]." + prop, "from": current, "to": float(values[field]), "row_action": row_action})
    source = owner_source or {}
    records = [{"field_path": w["field_path"], "value": str(w["to"]) if w["field_path"] == PHASE_ID_FIELD else repr(w["to"]),
                "type": "name" if w["field_path"] == PHASE_ID_FIELD else "float", "origin": "OwnerApproval",
                "precedence": "typed-record", "source_path": "Documentation/TEAM_MAILBOX.md",
                "source_site": source.get("message_id"), "source_sha256": source.get("reply_sha256")} for w in writes]
    plan.update(accepted=True, mode=mode, writes=writes, field_records=records, before_sha256=before,
                steps=list(STEPS_WRITE if mode == "write" else STEPS_DRY),
                untouched_phase_rows=[p.get("phase_id") for p in phases if isinstance(p, dict) and p.get("phase_id") != PHASE_ID],
                untouched_phase_snapshot=[copy.deepcopy(p) for p in phases if isinstance(p, dict) and p.get("phase_id") != PHASE_ID])
    return plan


def verify_readback(plan, after):
    """Compare a synthetic after-save readback with the plan. Any mismatch => restore from backup, then release locks."""
    errors = []
    if not plan.get("accepted") or plan.get("mode") != "write":
        return {"ok": False, "errors": ["readback applies only to an accepted write plan"], "next": "release_locks"}
    if not isinstance(after, dict):
        return {"ok": False, "errors": ["after-readback snapshot is required"], "next": "restore_backup_then_release_locks"}
    if not isinstance(plan.get("writes"), list) or not isinstance(after.get("stats"), dict) \
            or not isinstance(after.get("phases"), list) or not isinstance(after.get("fields"), list):
        return {"ok": False, "errors": ["after-readback structures are malformed"], "next": "restore_backup_then_release_locks"}
    if after.get("asset_path") != ASSET_PATH:
        errors.append("asset path changed (the asset must be preserved in place)")
    if after.get("exists") is not True:
        errors.append("after-readback must show the saved asset exists (exists is True)")
    after_hash = after.get("file_sha256")
    if not (isinstance(after_hash, str) and re.fullmatch(r"[0-9a-f]{64}", after_hash)):
        errors.append("after-readback needs the saved file's hash (64 lowercase hex)")
    elif after_hash == plan.get("before_sha256"):
        errors.append("file hash unchanged: the save did not happen")
    rows = [p for p in after.get("phases") or [] if isinstance(p, dict) and p.get("phase_id") == PHASE_ID]
    if len(rows) != 1:
        errors.append("after-readback must have exactly one Phase_1 row, found %d" % len(rows))
    others = [p.get("phase_id") for p in after.get("phases") or [] if isinstance(p, dict) and p.get("phase_id") != PHASE_ID]
    if others != plan.get("untouched_phase_rows"):
        errors.append("other phase rows changed: %s -> %s" % (plan.get("untouched_phase_rows"), others))
    other_rows = [p for p in after.get("phases") or [] if isinstance(p, dict) and p.get("phase_id") != PHASE_ID]
    if "untouched_phase_snapshot" not in plan or other_rows != plan.get("untouched_phase_snapshot"):
        errors.append("other phase rows differ from the reviewed snapshot (complete rows are compared, not only phase_id)")
    for write in plan["writes"]:
        group, prop = write["target"].split(".", 1)
        actual = (after.get("stats") or {}).get(prop) if group == "stats" else (rows[0].get(prop) if len(rows) == 1 else None)
        if prop == "phase_id":
            if actual != PHASE_ID:
                errors.append("%s saved %r, expected %r" % (write["field_path"], actual, PHASE_ID))
        elif not _finite(actual) or abs(float(actual) - write["to"]) > FLOAT_TOLERANCE:
            errors.append("%s saved %r, expected %r" % (write["field_path"], actual, write["to"]))
    expected_records = {r.get("field_path"): r for r in plan.get("field_records", []) if isinstance(r, dict)}
    recorded = {r.get("field_path"): r for r in after["fields"] if isinstance(r, dict)}
    missing = sorted(set(expected_records) - set(recorded))
    if missing:
        errors.append("field provenance records missing after save: %s" % ", ".join(missing))
    for field, expected in expected_records.items():
        actual_record = recorded.get(field)
        if actual_record and any(actual_record.get(key) != expected.get(key) for key in
                                 ("value", "type", "origin", "precedence", "source_path", "source_site", "source_sha256")):
            errors.append("field provenance record mismatches the approved source for %s" % field)
    return {"ok": not errors, "errors": errors, "next": "release_locks" if not errors else "restore_backup_then_release_locks"}
