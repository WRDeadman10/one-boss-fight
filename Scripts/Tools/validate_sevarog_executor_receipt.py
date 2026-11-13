"""BK-112: pure schema validator for future Sevarog executor receipts; validates claims, performs no operations."""
import re

SCHEMA = "onebossfight.sevarog-executor-receipt/v1"
ASSET_PATH = "/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_Draft"
MAILBOX_PATH = "Documentation/TEAM_MAILBOX.md"
LOCK_PATHS = ("ENGINE_LOCK.json", "Docs/BossCombatReview/Execution/ENGINE_LOCK.json")
HEX32 = re.compile(r"[0-9a-f]{32}")
HEX64 = re.compile(r"[0-9a-f]{64}")
OUTCOMES = {"DRY_RUN_ONLY", "WRITTEN_AND_VERIFIED", "FAILED_RESTORED", "FAILED_RESTORE_NEEDS_OPERATOR",
            "REFUSED_AFTER_LOCKS", "LOCK_RETAINED_NEEDS_OPERATOR"}
TOP_KEYS = {"schema", "outcome", "source", "plan_sha256", "asset", "locks", "steps"}
SOURCE_KEYS = {"message_id", "sender", "path", "sha256"}
ASSET_KEYS = {"path", "before_sha256", "backup_path", "backup_sha256", "after_sha256", "restored_sha256"}
LOCK_KEYS = {"path", "token", "created", "readback_token", "party", "policy", "release_attempted",
             "release_token_match", "released"}

DRY_STEPS = ("mailbox_read", "dry_run")
WRITE_STEPS = ("mailbox_read", "dry_run", "locks_created", "backup_verified", "write_plan", "save",
               "readback_verified", "locks_released")
RESTORED_STEPS = ("mailbox_read", "dry_run", "locks_created", "backup_verified", "write_plan", "save",
                  "readback_failed", "restore_verified", "locks_released")
RETAINED_STEPS = ("mailbox_read", "dry_run", "locks_created", "backup_verified", "write_plan", "save",
                  "readback_verified", "lock_release_failed")
RETAINED_RESTORE_STEPS = ("mailbox_read", "dry_run", "locks_created", "backup_verified", "write_plan", "save",
                          "readback_failed", "restore_failed", "lock_release_failed")
RESTORE_FAILED_STEPS = ("mailbox_read", "dry_run", "locks_created", "backup_verified", "write_plan", "save",
                        "readback_failed", "restore_failed", "locks_released")
REFUSED_STEPS = (
    ("mailbox_read", "dry_run", "locks_acquisition_attempted", "locks_acquisition_partial", "refused_after_locks", "locks_released"),
    ("mailbox_read", "dry_run", "locks_acquisition_attempted", "locks_verified", "refused_after_locks", "locks_released"),
    ("mailbox_read", "dry_run", "locks_acquisition_attempted", "locks_verified", "backup_refused", "locks_released"),
    ("mailbox_read", "dry_run", "locks_acquisition_attempted", "locks_verified", "backup_verified", "write_plan_refused", "locks_released"),
)
BACKUP_PREFIX = "Docs/BossCombatReview/Execution/"


def _hash(value):
    return isinstance(value, str) and HEX64.fullmatch(value) is not None


def _safe_backup_path(value):
    if not isinstance(value, str) or not value.startswith(BACKUP_PREFIX) or "\\" in value or ":" in value:
        return False
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        return False
    parts = value.split("/")
    return all(part not in ("", ".", "..") for part in parts)


def _shape(obj, keys, label, errors):
    if not isinstance(obj, dict):
        errors.append("%s must be an object" % label)
        return False
    if set(obj) != keys:
        errors.append("%s keys must be exactly %s" % (label, ", ".join(sorted(keys))))
        return False
    return True


def _source(source, required, errors):
    if not _shape(source, SOURCE_KEYS, "source", errors):
        return False
    empty = all(source[k] is None for k in SOURCE_KEYS)
    if empty and not required:
        return False
    if source.get("sender") != "Owner":
        errors.append("source.sender must be Owner")
    if not (isinstance(source.get("message_id"), str) and re.fullmatch(r"(?:O|H)-[0-9]+", source["message_id"])):
        errors.append("source.message_id must be an Owner O-<n> or H-<n> id")
    if source.get("path") != MAILBOX_PATH:
        errors.append("source.path must identify the team mailbox")
    if not _hash(source.get("sha256")):
        errors.append("source.sha256 must be 64 lowercase hex")
    return True


def _locks(locks, outcome, errors):
    if not isinstance(locks, list) or len(locks) != 2:
        errors.append("locks must contain exactly two lock records")
        return
    if [item.get("path") if isinstance(item, dict) else None for item in locks] != list(LOCK_PATHS):
        errors.append("locks must contain both canonical paths exactly once and in order")
    for index, lock in enumerate(locks):
        if not _shape(lock, LOCK_KEYS, "locks[%d]" % index, errors):
            continue
        if outcome == "DRY_RUN_ONLY":
            if any(lock.get(k) is not None for k in ("token", "readback_token", "party", "policy")) or any(
                lock.get(k) is not False for k in ("created", "release_attempted", "release_token_match", "released")):
                errors.append("dry-run receipt must show no locks acquired or released")
            continue
        if not all(isinstance(lock.get(k), bool) for k in ("release_attempted", "release_token_match", "released")):
            errors.append("locks[%d] release flags must be booleans" % index)
        if outcome == "REFUSED_AFTER_LOCKS" and lock.get("created") is not True:
            if lock.get("created") is not False or any(lock.get(k) is not None for k in ("token", "readback_token", "party", "policy")) or any(
                lock.get(k) is not False for k in ("release_attempted", "release_token_match", "released")):
                errors.append("a lock not created by this run cannot claim lock or release data")
            continue
        token = lock.get("token")
        if not (isinstance(token, str) and HEX32.fullmatch(token)):
            errors.append("locks[%d].token must be 32 lowercase hex" % index)
        if lock.get("released") is True and not (lock.get("release_attempted") is True and lock.get("release_token_match") is True):
            errors.append("a released lock requires an attempted release with a matching token")
        if lock.get("release_token_match") is True and lock.get("released") is not True:
            errors.append("a lock with a matching release token must be marked released")
        if lock.get("created") is not True:
            errors.append("locks[%d].created must be true" % index)
        if lock.get("readback_token") != token:
            errors.append("locks[%d] readback token must match its create token" % index)
        if lock.get("party") not in ("X", "C", "A") or lock.get("policy") != "C-1155":
            errors.append("locks[%d] party/policy must identify a team C-1155 lock" % index)
        if outcome in ("WRITTEN_AND_VERIFIED", "FAILED_RESTORED", "FAILED_RESTORE_NEEDS_OPERATOR") and not all(
            lock.get(k) is True for k in ("release_attempted", "release_token_match", "released")):
            errors.append("%s requires both locks released after token match" % outcome)
        if outcome == "REFUSED_AFTER_LOCKS" and not all(
            lock.get(k) is True for k in ("release_attempted", "release_token_match", "released")):
            errors.append("REFUSED_AFTER_LOCKS requires every created lock released after token match")
        if outcome == "LOCK_RETAINED_NEEDS_OPERATOR" and lock.get("released") is not True and lock.get("release_attempted") is not True:
            errors.append("retained lock must record a release attempt")
        if outcome == "LOCK_RETAINED_NEEDS_OPERATOR" and lock.get("released") is True and lock.get("release_token_match") is not True:
            errors.append("released lock must record a matching token")
    created = [lock for lock in locks if isinstance(lock, dict) and lock.get("created") is True]
    if outcome not in ("REFUSED_AFTER_LOCKS", "DRY_RUN_ONLY"):
        if len(created) != 2:
            errors.append("write outcomes require exactly two created locks")
        tokens = {lock.get("token") for lock in created if isinstance(lock.get("token"), str)}
        parties = {lock.get("party") for lock in created if isinstance(lock.get("party"), str)}
        if len(tokens) != 1:
            errors.append("both locks must share one C-1155 run token")
        if len(parties) != 1:
            errors.append("both locks must belong to one party")
    elif outcome == "REFUSED_AFTER_LOCKS":
        if len(created) < 1:
            errors.append("REFUSED_AFTER_LOCKS requires at least one lock created by this run")
        tokens = {lock.get("token") for lock in created if isinstance(lock.get("token"), str)}
        parties = {lock.get("party") for lock in created if isinstance(lock.get("party"), str)}
        if len(tokens) != 1:
            errors.append("created refusal locks must share one run token")
        if len(parties) != 1:
            errors.append("created refusal locks must belong to one party")
    if outcome == "LOCK_RETAINED_NEEDS_OPERATOR" and all(isinstance(lock, dict) and lock.get("released") is True for lock in locks):
        errors.append("operator-required outcome needs at least one retained lock")


def validate_receipt(receipt):
    """Return {valid, errors}; no I/O, source lookup, Unreal, or lock operation."""
    errors = []
    if not _shape(receipt, TOP_KEYS, "receipt", errors):
        return {"valid": False, "errors": errors}
    outcome = receipt.get("outcome")
    if receipt.get("schema") != SCHEMA:
        errors.append("receipt.schema is not supported")
    if not isinstance(outcome, str) or outcome not in OUTCOMES:
        errors.append("receipt.outcome is not supported")
        return {"valid": False, "errors": errors}
    source_required = True
    _source(receipt.get("source"), source_required, errors)
    plan_hash = receipt.get("plan_sha256")
    if not _hash(plan_hash):
        errors.append("plan_sha256 must be 64 lowercase hex")
    asset = receipt.get("asset")
    if _shape(asset, ASSET_KEYS, "asset", errors):
        if asset.get("path") != ASSET_PATH:
            errors.append("asset.path must identify the existing Sevarog draft")
        steps = tuple(receipt.get("steps")) if isinstance(receipt.get("steps"), list) and all(
            isinstance(s, str) for s in receipt["steps"]) else ()
        expected_steps = {"DRY_RUN_ONLY": (DRY_STEPS,), "WRITTEN_AND_VERIFIED": (WRITE_STEPS,),
                          "FAILED_RESTORED": (RESTORED_STEPS,), "FAILED_RESTORE_NEEDS_OPERATOR": (RESTORE_FAILED_STEPS,),
                          "REFUSED_AFTER_LOCKS": REFUSED_STEPS,
                          "LOCK_RETAINED_NEEDS_OPERATOR": (RETAINED_STEPS, RETAINED_RESTORE_STEPS)}[outcome]
        if steps not in expected_steps:
            errors.append("steps do not match the required ordered sequence for %s" % outcome)
        if outcome == "REFUSED_AFTER_LOCKS":
            lock_records = receipt.get("locks")
            created_count = sum(1 for item in lock_records if isinstance(item, dict) and item.get("created") is True) if isinstance(lock_records, list) else 0
            if steps == REFUSED_STEPS[0] and created_count != 1:
                errors.append("partial lock acquisition refusal requires exactly one created lock")
            elif steps == REFUSED_STEPS[0] and isinstance(lock_records, list) and len(lock_records) == 2 \
                    and all(isinstance(item, dict) for item in lock_records) \
                    and lock_records[1].get("created") is True and lock_records[0].get("created") is not True:
                # BK-195 (X-2042): acquisition is root first (runner :74-79), so a lone execution lock is impossible
                errors.append("partial lock acquisition must have created the root lock first (execution lock without root)")
            elif steps != REFUSED_STEPS[0] and steps in REFUSED_STEPS and created_count != 2:
                errors.append("post-acquisition refusal requires both locks created")
        if outcome == "DRY_RUN_ONLY":
            if any(asset.get(k) is not None for k in ("before_sha256", "backup_path", "backup_sha256", "after_sha256", "restored_sha256")):
                errors.append("dry-run receipt must not claim a backup, write, readback, or restore")
        elif outcome == "REFUSED_AFTER_LOCKS":
            if asset.get("before_sha256") is not None and not _hash(asset.get("before_sha256")):
                errors.append("refusal before-hash must be null or 64 lowercase hex")
            backed_up = "backup_verified" in steps
            if backed_up:
                if not _hash(asset.get("before_sha256")) or not _safe_backup_path(asset.get("backup_path")) or asset.get("backup_sha256") != asset.get("before_sha256"):
                    errors.append("REFUSED_AFTER_LOCKS after backup verification requires a safe backup matching before_sha256")
            elif asset.get("backup_path") is not None or asset.get("backup_sha256") is not None:
                errors.append("REFUSED_AFTER_LOCKS cannot claim backup data before backup_verified")
            if asset.get("after_sha256") is not None or asset.get("restored_sha256") is not None:
                errors.append("REFUSED_AFTER_LOCKS cannot claim a save, readback, or restore")
        else:
            before = asset.get("before_sha256")
            if not _hash(before):
                errors.append("asset.before_sha256 must be 64 lowercase hex")
            if not _safe_backup_path(asset.get("backup_path")):
                errors.append("asset.backup_path must be a safe repo-relative path below %s" % BACKUP_PREFIX)
            if asset.get("backup_sha256") != before:
                errors.append("asset.backup_sha256 must equal before_sha256")
            if not _hash(asset.get("after_sha256")):
                errors.append("asset.after_sha256 must be 64 lowercase hex")
            if outcome in ("WRITTEN_AND_VERIFIED", "FAILED_RESTORED", "FAILED_RESTORE_NEEDS_OPERATOR", "LOCK_RETAINED_NEEDS_OPERATOR") and asset.get("after_sha256") == before:
                errors.append("post-save asset hash must differ from before_sha256")
            if outcome == "FAILED_RESTORED":
                if not _hash(asset.get("restored_sha256")) or asset.get("restored_sha256") != before:
                    errors.append("FAILED_RESTORED requires restored_sha256 to equal before_sha256")
            elif outcome == "FAILED_RESTORE_NEEDS_OPERATOR":
                if not _hash(asset.get("restored_sha256")) or asset.get("restored_sha256") == before:
                    errors.append("FAILED_RESTORE_NEEDS_OPERATOR requires a valid mismatched restored hash")
            elif outcome == "LOCK_RETAINED_NEEDS_OPERATOR" and steps == RETAINED_RESTORE_STEPS:
                if not _hash(asset.get("restored_sha256")) or asset.get("restored_sha256") == before:
                    errors.append("retained-lock restore failure requires a valid mismatched restored hash")
            elif asset.get("restored_sha256") is not None:
                errors.append("restored_sha256 is only valid for a restore outcome")
    _locks(receipt.get("locks"), outcome, errors)
    if not isinstance(receipt.get("steps"), list) or not all(isinstance(s, str) for s in receipt["steps"]):
        errors.append("steps must be a list of strings")
    return {"valid": not errors, "errors": errors}
