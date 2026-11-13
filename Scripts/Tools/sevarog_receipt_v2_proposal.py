"""BK-132..135 (C, implementer; X-2017): PROPOSED v2 evidence schema for Sevarog executor receipts.

Proposal only. Nothing imports this module; the current v1 validator (validate_sevarog_executor_receipt.py), adapter,
executor contract and runner are unchanged. Pure Python: no filesystem, Unreal, process, network, asset or lock access.
A valid v2 receipt is not runtime proof and not write authorization; X-1991 remains the owner gate.

What v2 changes (rationale in Documentation/Boss/BK_131_135_RECEIPT_V2_SCHEMA_PROPOSAL.md):
  * history  - the executor contract's own state list (ExecutorContract.history) replaces v1 step names; every
               adjacent pair must be a contract transition, so the receipt cannot describe a run the contract forbids.
  * outcome  - derived from history + lock release (mirrors ExecutorContract.release_locks) and must match. Two
               outcomes v1 cannot express are added: REFUSED_BEFORE_LOCKS (lock-free refusal) and
               ABANDONED_NEEDS_OPERATOR (locks released while the asset may already be written).
  * refusal  - {stage, reason}: the state the run was refused or aborted in plus a closed reason code.
  * hashes   - three meanings kept apart (X-2019): source.sha256 = Owner mailbox body; asset.dry_run_sha256 = asset
               snapshot at the dry run; asset.locked_before_sha256 = snapshot under the locks. Equality of the last
               two is a concurrency check, never interchangeable provenance.
  * backup_attempt - the backup lifecycle as separate observations (X-2019/X-2020): attempted, copy_result,
               observed hash, verified, cleanup attempted, cleanup readback, and a final_state DERIVED from them.
               Removal is claimed only with an observed-absent readback; otherwise the state is retained or unknown.
  * restore  - restored_sha256 may be null after RESTORE_FAILED (readback unavailable, contract :195-203); the
               operator artifact then carries an unknown current hash, never the pre-restore after-hash (X-2021).
  * artifacts - the derived, bounded list of leftovers an operator must handle (retained locks, a retained or
               unknown backup copy, an asset whose current state may not match its before-hash).
  * locks    - acquisition order is an explicit per-lock create_order (1, 2), not the array index (X-2019); the
               proposal requires the repo-root lock first (as the runner does, run_bk56_60_deferred_selection.ps1
               :74-79). Release order is not constrained (each release is token-guarded; all attempted in finally).
"""
import re

SCHEMA_V2 = "onebossfight.sevarog-executor-receipt/v2"
ASSET_PATH = "/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_Draft"
MAILBOX_PATH = "Documentation/TEAM_MAILBOX.md"
LOCK_PATHS = ("ENGINE_LOCK.json", "Docs/BossCombatReview/Execution/ENGINE_LOCK.json")
EVIDENCE_PREFIX = "Docs/BossCombatReview/Execution/"
HEX32 = re.compile(r"[0-9a-f]{32}")
HEX64 = re.compile(r"[0-9a-f]{64}")
OWNER_ID = re.compile(r"(?:O|H)-[0-9]+")
MAX_HISTORY = 12
MAX_ARTIFACTS = 4

# Mirrors sevarog_executor_contract.py: _move targets in each transition, _refuse (:58), and release_locks from any
# lock-holding state (:27-28, :207).
HOLDS_LOCKS = ("LOCKED", "BACKED_UP", "WRITE_PLANNED", "SAVED", "VERIFIED", "RESTORE_REQUIRED", "RESTORED",
               "RESTORE_FAILED", "RELEASE_REQUIRED")
TRANSITIONS = {
    "INIT": {"STARTED", "REFUSED"},
    "STARTED": {"DRY_RUN_PLANNED", "REFUSED"},
    "DRY_RUN_PLANNED": {"LOCKED", "RELEASE_REQUIRED", "REFUSED"},
    "LOCKED": {"BACKED_UP", "RELEASE_REQUIRED", "RELEASED"},
    "BACKED_UP": {"WRITE_PLANNED", "RELEASE_REQUIRED", "RELEASED"},
    "WRITE_PLANNED": {"SAVED", "RESTORE_REQUIRED", "RELEASED"},
    "SAVED": {"VERIFIED", "RESTORE_REQUIRED", "RELEASED"},
    "RESTORE_REQUIRED": {"RESTORED", "RESTORE_FAILED", "RELEASED"},
    "VERIFIED": {"RELEASED"}, "RESTORED": {"RELEASED"}, "RESTORE_FAILED": {"RELEASED"}, "RELEASE_REQUIRED": {"RELEASED"},
}
TERMINALS = {"DRY_RUN_PLANNED", "RELEASED", "REFUSED"}
# Released early from these states, the asset may already be written: the contract calls it REFUSED_AFTER_LOCKS (:222-223).
ABANDON_STATES = {"WRITE_PLANNED", "SAVED", "RESTORE_REQUIRED"}
ABORT_STATES = {"LOCKED", "BACKED_UP"} | ABANDON_STATES

# Closed reason codes per refusal stage (contract anchors in the report, BK-131 table).
REASONS = {
    "INIT": {"BINDING_MISSING", "SOURCE_UNBOUND"},
    "STARTED": {"DRY_PLAN_REFUSED"},
    "DRY_RUN_PLANNED": {"CREATE_RECEIPTS_INVALID", "EXPLICIT_WRITE_MISSING", "APPROVAL_INCOMPLETE", "TOKEN_INVALID",
                        "ACQUISITION_FAILED", "LOCK_IDENTITY"},
    "LOCKED": {"BEFORE_HASH_MISSING", "ASSET_CHANGED", "BACKUP_MISMATCH"},
    "BACKED_UP": {"WRITE_PLAN_REFUSED", "WRITE_PLAN_DIVERGED"},
}
ABORTED = "EXECUTOR_ABORTED"
OUTCOMES_V2 = {"DRY_RUN_ONLY", "WRITTEN_AND_VERIFIED", "FAILED_RESTORED", "FAILED_RESTORE_NEEDS_OPERATOR",
               "REFUSED_AFTER_LOCKS", "LOCK_RETAINED_NEEDS_OPERATOR", "REFUSED_BEFORE_LOCKS", "ABANDONED_NEEDS_OPERATOR"}
COPY_RESULTS = {"created", "failed", "unknown"}
CLEANUP_READBACKS = {"absent", "present", "not_observed"}
FINAL_STATES = {"none", "kept_evidence", "removed", "retained", "unknown"}

TOP_KEYS = {"schema", "outcome", "source", "plan_sha256", "history", "refusal", "asset", "backup_attempt", "locks",
            "artifacts"}
SOURCE_KEYS = {"message_id", "sender", "path", "sha256"}
ASSET_KEYS = {"path", "dry_run_sha256", "locked_before_sha256", "after_sha256", "restored_sha256"}
BACKUP_KEYS = {"attempted", "copy_result", "path", "observed_sha256", "verified", "cleanup_attempted",
               "cleanup_readback", "final_state"}
LOCK_KEYS = {"path", "created", "create_order", "token", "readback_token", "party", "policy", "release_attempted",
             "release_token_match", "released"}
ARTIFACT_KEYS = {"kind", "path", "sha256"}


def _enum(value, allowed):
    """Type-guarded membership: a non-string (including unhashable) value is never a member (R1, X-2020)."""
    return isinstance(value, str) and value in allowed


def _hex64(value):
    return isinstance(value, str) and HEX64.fullmatch(value) is not None


def safe_evidence_path(value):
    """Repo-relative, forward slashes, below EVIDENCE_PREFIX, no empty/./.. segment, no drive, colon or control char."""
    if not isinstance(value, str) or not value.startswith(EVIDENCE_PREFIX) or "\\" in value or ":" in value:
        return False
    if any(ord(c) < 32 or ord(c) == 127 for c in value):
        return False
    return all(part not in ("", ".", "..") for part in value.split("/"))


def _shape(obj, keys, label, errors):
    if not isinstance(obj, dict):
        errors.append("%s must be an object" % label)
        return False
    if set(obj) != keys:
        errors.append("%s keys must be exactly %s" % (label, ", ".join(sorted(keys))))
        return False
    return True


def check_history(history, errors):
    """Return True when history is a contract-legal path from INIT to a terminal state."""
    if not (isinstance(history, list) and history and all(isinstance(s, str) for s in history)):
        errors.append("history must be a non-empty list of contract state names")
        return False
    if len(history) > MAX_HISTORY:
        errors.append("history is longer than any contract run (%d)" % MAX_HISTORY)
        return False
    if history[0] != "INIT":
        errors.append("history must start at INIT")
        return False
    for before, after in zip(history, history[1:]):
        if after not in TRANSITIONS.get(before, ()):
            errors.append("history has a transition the contract forbids: %s -> %s" % (before, after))
            return False
    if history[-1] not in TERMINALS:
        errors.append("history must end in DRY_RUN_PLANNED, RELEASED or REFUSED")
        return False
    return True


def refusal_stage(history):
    """(stage, aborted) for a refused or aborted run, else (None, False). History must already be legal."""
    if history[-1] == "REFUSED":
        return history[-2], False
    if "RELEASE_REQUIRED" in history:
        return history[history.index("RELEASE_REQUIRED") - 1], False
    if history[-1] == "RELEASED" and history[-2] in ABORT_STATES:
        return history[-2], True
    return None, False


def derive_outcome(history, any_retained):
    """Mirror of ExecutorContract.release_locks (:205-223) except early release after a possible write."""
    terminal = history[-1]
    if terminal == "DRY_RUN_PLANNED":
        return "DRY_RUN_ONLY"
    if terminal == "REFUSED":
        return "REFUSED_BEFORE_LOCKS"
    prior = history[-2]
    if any_retained:
        return "LOCK_RETAINED_NEEDS_OPERATOR"
    if prior in ABANDON_STATES:
        return "ABANDONED_NEEDS_OPERATOR"
    return {"VERIFIED": "WRITTEN_AND_VERIFIED", "RESTORED": "FAILED_RESTORED",
            "RESTORE_FAILED": "FAILED_RESTORE_NEEDS_OPERATOR"}.get(prior, "REFUSED_AFTER_LOCKS")


def _source(source, stage, errors):
    if not _shape(source, SOURCE_KEYS, "source", errors):
        return
    if stage == "INIT" and all(source[k] is None for k in SOURCE_KEYS):
        return  # refused at start: there may be no bound owner message to cite
    if source["sender"] != "Owner" or not (isinstance(source["message_id"], str) and OWNER_ID.fullmatch(source["message_id"])):
        errors.append("source must be an Owner O-<n>/H-<n> message")
    if source["path"] != MAILBOX_PATH or not _hex64(source["sha256"]):
        errors.append("source must name the team mailbox and a 64-hex body hash")


def _locks(locks, history, errors):
    """Return the list of retained lock paths (created and not released)."""
    if not (isinstance(locks, list) and len(locks) == 2):
        errors.append("locks must contain exactly two lock records")
        return []
    if [l.get("path") if isinstance(l, dict) else None for l in locks] != list(LOCK_PATHS):
        errors.append("locks must list both canonical paths in order")
        return []
    if not all(_shape(l, LOCK_KEYS, "locks[%d]" % i, errors) for i, l in enumerate(locks)):
        return []
    created = [l["created"] for l in locks]
    if not all(isinstance(c, bool) for c in created):
        errors.append("locks[].created must be boolean")
        return []
    orders = [l["create_order"] for l in locks]
    for i, (made, order) in enumerate(zip(created, orders)):
        if not made and order is not None:
            errors.append("locks[%d] was not created, so create_order must be null" % i)
        if made and not (type(order) is int and order in (1, 2)):
            errors.append("locks[%d].create_order must be 1 or 2" % i)
    made_orders = sorted(o for o, made in zip(orders, created) if made and type(o) is int)
    if made_orders != list(range(1, sum(created) + 1)):
        errors.append("create_order must number the created locks 1..n without gaps or repeats")
    elif any(created) and orders[0] != 1:
        errors.append("the repo-root lock must be created first (create_order 1), as the runner does")
    holds = any(state in HOLDS_LOCKS for state in history)
    if not holds and any(created):
        errors.append("a run that never held locks cannot record a created lock")
    if holds and not any(created):
        errors.append("a lock-holding run must record at least one created lock")
    locked = "LOCKED" in history
    if locked and not all(created):
        errors.append("a run that reached LOCKED created both locks")
    retained, tokens, parties = [], set(), set()
    for i, lock in enumerate(locks):
        flags = ("release_attempted", "release_token_match", "released")
        if not lock["created"]:
            if any(lock[k] is not None for k in ("token", "readback_token", "party", "policy")) or any(lock[k] is not False for k in flags):
                errors.append("locks[%d] was not created and cannot claim lock or release data" % i)
            continue
        if not all(isinstance(lock[k], bool) for k in flags):
            errors.append("locks[%d] release flags must be booleans" % i)
            continue
        if not (isinstance(lock["token"], str) and HEX32.fullmatch(lock["token"])):
            errors.append("locks[%d].token must be 32 lowercase hex" % i)
        tokens.add(lock["token"] if isinstance(lock["token"], str) else None)
        if locked:
            if lock["readback_token"] != lock["token"] or lock["party"] not in ("X", "C", "A") or lock["policy"] != "C-1155":
                errors.append("locks[%d] readback must match the run token, party and C-1155 policy" % i)
            parties.add(lock["party"] if isinstance(lock["party"], str) else None)
        else:  # refused during acquisition: readback may be missing or show another owner (contract :129-136)
            if lock["readback_token"] is not None and not (isinstance(lock["readback_token"], str) and HEX32.fullmatch(lock["readback_token"])):
                errors.append("locks[%d].readback_token must be null or 32 lowercase hex" % i)
            if lock["party"] not in (None, "X", "C", "A") or lock["policy"] not in (None, "C-1155"):
                errors.append("locks[%d] party/policy must be null or a team C-1155 identity" % i)
        if lock["release_attempted"] is not True:
            errors.append("locks[%d] was created, so release must be attempted (executor finally)" % i)
        if lock["released"] != lock["release_token_match"]:
            errors.append("locks[%d] is released exactly when its release token matched" % i)
        if lock["released"] is not True:
            retained.append(lock["path"])
    if len(tokens) > 1:
        errors.append("created locks must share one run token")
    if len(parties) > 1:
        errors.append("created locks must belong to one party")
    return retained


def _refusal(refusal, history, errors):
    stage, aborted = refusal_stage(history)
    if stage is None:
        if refusal is not None:
            errors.append("refusal must be null for a run that was not refused or aborted")
        return None, None
    if not _shape(refusal, {"stage", "reason"}, "refusal", errors):
        return stage, None
    if refusal["stage"] != stage:
        errors.append("refusal.stage must be %s (from history)" % stage)
    allowed = {ABORTED} if aborted else REASONS.get(stage, set())
    reason = refusal["reason"] if isinstance(refusal["reason"], str) else None
    if reason not in allowed:
        errors.append("refusal.reason must be one of %s at %s" % (", ".join(sorted(allowed)), stage))
        reason = None
    return stage, reason


def _asset(asset, history, stage, reason, errors):
    if not _shape(asset, ASSET_KEYS, "asset", errors):
        return None
    if asset["path"] != ASSET_PATH:
        errors.append("asset.path must identify the existing Sevarog draft")
    dry, before, after, restored = (asset[k] for k in ("dry_run_sha256", "locked_before_sha256", "after_sha256", "restored_sha256"))
    if "DRY_RUN_PLANNED" in history:
        if not _hex64(dry):
            errors.append("asset.dry_run_sha256 must be 64 hex once the dry run is planned")
    elif dry is not None:
        errors.append("asset.dry_run_sha256 must be null before the dry run")
    if "BACKED_UP" in history or reason in ("ASSET_CHANGED", "BACKUP_MISMATCH"):
        if not _hex64(before):
            errors.append("asset.locked_before_sha256 must be 64 hex once the locked snapshot was compared")
        elif reason == "ASSET_CHANGED" and before == dry:
            errors.append("ASSET_CHANGED requires the locked before-hash to differ from the dry-run hash")
        elif reason != "ASSET_CHANGED" and before != dry:
            errors.append("the locked before-hash must equal the dry-run hash when the run continued past it")
    elif not (stage == "LOCKED" and reason == ABORTED and (before is None or _hex64(before))) and before is not None:
        errors.append("asset.locked_before_sha256 must be null when no locked snapshot was compared")
    saved = "SAVED" in history
    if saved != _hex64(after) or (not saved and after is not None):
        errors.append("asset.after_sha256 is 64 hex exactly when the history contains SAVED")
    if "VERIFIED" in history and after == before:
        errors.append("a verified write must change the asset hash")
    if "RESTORED" in history:
        if not _hex64(restored) or restored != before:
            errors.append("RESTORED requires restored_sha256 to equal the locked before-hash")
    elif "RESTORE_FAILED" in history:
        # The contract records RESTORE_FAILED for any non-matching value, including no readback (C:195-203).
        if restored is not None and (not _hex64(restored) or restored == before):
            errors.append("RESTORE_FAILED requires restored_sha256 to be null (unknown) or a 64-hex hash other than the before-hash")
    elif restored is not None:
        errors.append("asset.restored_sha256 must be null when no restore was recorded")
    return asset


def backup_final_state(backup):
    """Derive the copy's final state from the observations; never asserts absence without an absent readback."""
    if backup.get("attempted") is not True:
        return "none"
    readback = backup.get("cleanup_readback")
    if backup.get("cleanup_attempted") is True:
        return {"absent": "removed", "present": "retained"}.get(readback, "unknown")
    if backup.get("copy_result") == "created":
        return "kept_evidence"
    if backup.get("copy_result") == "failed" and readback == "absent":
        return "none"  # a failed copy observed absent left nothing behind
    return "unknown"  # failed or unknown copy without an absent readback may have left a partial file


def _backup(backup, history, reason, asset, errors):
    """Return the backup record if its copy must be listed as an operator artifact."""
    reached = "LOCKED" in history
    if backup is None:
        if reached:
            errors.append("backup_attempt is required once the locks were held (attempted may be false)")
        return None
    if not reached:
        errors.append("backup_attempt must be null before the locks were held")
        return None
    if not _shape(backup, BACKUP_KEYS, "backup_attempt", errors):
        return None
    if not all(isinstance(backup[k], bool) for k in ("attempted", "verified", "cleanup_attempted")):
        errors.append("backup_attempt.attempted, verified and cleanup_attempted must be booleans")
        return None
    if not _enum(backup["cleanup_readback"], CLEANUP_READBACKS):
        errors.append("backup_attempt.cleanup_readback must be one of %s" % ", ".join(sorted(CLEANUP_READBACKS)))
        return None
    verified = "BACKED_UP" in history
    if backup["verified"] is not verified:
        errors.append("backup_attempt.verified must be %s (from history)" % verified)
    if not backup["attempted"]:
        if any(backup[k] is not None for k in ("copy_result", "path", "observed_sha256")) or backup["cleanup_attempted"] \
                or backup["cleanup_readback"] != "not_observed":
            errors.append("a backup that was not attempted cannot claim a copy, cleanup or readback")
        if verified or reason not in ("BEFORE_HASH_MISSING", ABORTED):
            errors.append("the backup may be skipped only for BEFORE_HASH_MISSING or an abort before BACKED_UP")
    else:
        if not _enum(backup["copy_result"], COPY_RESULTS):
            errors.append("backup_attempt.copy_result must be one of %s" % ", ".join(sorted(COPY_RESULTS)))
            return None
        if not safe_evidence_path(backup["path"]):
            errors.append("backup_attempt.path must be a safe path below %s" % EVIDENCE_PREFIX)
        observed = backup["observed_sha256"]
        if observed is not None and not _hex64(observed):
            errors.append("backup_attempt.observed_sha256 must be null (not read) or 64 hex")
        if backup["copy_result"] != "created" and observed is not None:
            errors.append("only a created copy can have an observed hash")
        before = asset.get("locked_before_sha256") if isinstance(asset, dict) else None
        if verified and (backup["copy_result"] != "created" or observed != before):
            errors.append("a verified backup is a created copy whose observed hash equals the locked before-hash")
        if verified and backup["cleanup_attempted"]:
            errors.append("a verified backup is the restore source and cannot be cleaned up by the run")
        if reason == "BACKUP_MISMATCH" and observed is not None and observed == before:
            errors.append("BACKUP_MISMATCH requires an observed backup hash that differs from the locked before-hash (or none)")
        if not backup["cleanup_attempted"] and backup["cleanup_readback"] == "present":
            errors.append("cleanup_readback 'present' is only meaningful after a cleanup attempt")
        if backup["copy_result"] == "created" and not backup["cleanup_attempted"] and backup["cleanup_readback"] == "absent":
            # A-850 / X-2047: a created copy that nobody tried to remove cannot be observed absent; reporting it as
            # kept evidence would hide a vanished backup. (An absent readback after a FAILED copy stays valid.)
            errors.append("a created backup observed absent without a cleanup attempt is inconsistent")
    derived = backup_final_state(backup)
    if not _enum(backup["final_state"], FINAL_STATES):
        errors.append("backup_attempt.final_state must be one of %s" % ", ".join(sorted(FINAL_STATES)))
    elif backup["final_state"] != derived:
        errors.append("backup_attempt.final_state must be %s (derived from the observations)" % derived)
    return backup if derived in ("retained", "unknown") else None


def expected_artifacts(history, retained, backup, asset):
    """Derived leftovers an operator must handle; the receipt must list exactly these (order-free)."""
    items = [{"kind": "lock", "path": path, "sha256": None} for path in retained]
    if backup is not None:
        current = backup.get("observed_sha256") if backup_final_state(backup) == "retained" else None
        items.append({"kind": "backup", "path": backup.get("path"), "sha256": current})
    terminal_prior = history[-2] if history[-1] == "RELEASED" else None
    if "RESTORE_FAILED" in history or terminal_prior in ABANDON_STATES:
        # Current asset state: only a post-restore readback identifies it; the pre-restore after-hash never does.
        sha = asset.get("restored_sha256") if isinstance(asset, dict) and "RESTORE_FAILED" in history else None
        items.append({"kind": "asset_needs_operator", "path": ASSET_PATH, "sha256": sha})
    return items


ARTIFACT_KINDS = {"lock", "backup", "asset_needs_operator"}


def _artifact_typed(item):
    """A-850 / X-2047: exact types before comparison - kind in ARTIFACT_KINDS, path a string, sha256 either JSON null
    (the permitted unknown state) or 64 lowercase hex. No str() coercion, so null and the string "None" differ."""
    return (_enum(item.get("kind"), ARTIFACT_KINDS) and isinstance(item.get("path"), str)
            and (item.get("sha256") is None or _hex64(item.get("sha256"))))


def _key(item):
    # Typed, total ordering key: null sorts before any hash and is never equal to a string.
    sha = item.get("sha256")
    return (item.get("kind"), item.get("path"), (0, "") if sha is None else (1, sha))


def validate_v2(receipt):
    """Return {valid, errors, derived_outcome, expected_artifacts}; validates claims only, performs no operation."""
    errors = []
    result = {"valid": False, "errors": errors, "derived_outcome": None, "expected_artifacts": None}
    if not _shape(receipt, TOP_KEYS, "receipt", errors):
        return result
    if receipt["schema"] != SCHEMA_V2:
        errors.append("receipt.schema must be %s (v1 receipts are never upgraded in place)" % SCHEMA_V2)
        return result
    history = receipt["history"]
    if not check_history(history, errors):
        return result
    stage, reason = _refusal(receipt["refusal"], history, errors)
    _source(receipt["source"], stage, errors)
    if "DRY_RUN_PLANNED" in history:
        if not _hex64(receipt["plan_sha256"]):
            errors.append("plan_sha256 must be 64 hex once the dry run is planned")
    elif receipt["plan_sha256"] is not None:
        errors.append("plan_sha256 must be null before the dry run")
    retained = _locks(receipt["locks"], history, errors)
    asset = _asset(receipt["asset"], history, stage, reason, errors)
    backup = _backup(receipt["backup_attempt"], history, reason, asset, errors)
    derived = derive_outcome(history, bool(retained))
    result["derived_outcome"] = derived
    if not isinstance(receipt["outcome"], str) or receipt["outcome"] not in OUTCOMES_V2:
        errors.append("receipt.outcome is not a v2 outcome")
    elif receipt["outcome"] != derived:
        errors.append("receipt.outcome must be %s (derived from history and lock release)" % derived)
    expected = expected_artifacts(history, retained, backup, asset)
    result["expected_artifacts"] = expected
    artifacts = receipt["artifacts"]
    if not (isinstance(artifacts, list) and len(artifacts) <= MAX_ARTIFACTS):
        errors.append("artifacts must be a list of at most %d records" % MAX_ARTIFACTS)
    elif not all(_shape(a, ARTIFACT_KEYS, "artifacts[%d]" % i, errors) for i, a in enumerate(artifacts)):
        pass
    elif not all(_artifact_typed(a) for a in artifacts):
        errors.append("artifacts need kind in %s, a string path and sha256 null or 64 lowercase hex"
                      % ", ".join(sorted(ARTIFACT_KINDS)))
    elif sorted(map(_key, artifacts)) != sorted(map(_key, expected)):
        errors.append("artifacts must list exactly the derived operator leftovers")
    result["valid"] = not errors
    return result
