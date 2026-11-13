"""BK-102 (C, implementer; X-2004): pure state-machine contract for a FUTURE Sevarog definition executor.

Contract only, not an executor. The module performs no I/O: no filesystem, no Unreal, no locks. A future editor-side
executor performs every real action (read the mailbox, create the C-1155 locks, copy the backup, save, read back,
restore, delete the locks) and reports each observation to this contract, which decides whether the next transition is
allowed. The binder module (bind_owner_approval) is injected by the caller, so planning goes through its issued-binding
capability check (forged dictionaries are refused there).

States and the only allowed transitions:
  INIT --start--> STARTED --plan_dry_run--> DRY_RUN_PLANNED            (a dry run ends here; no locks are ever taken)
  DRY_RUN_PLANNED --acquire_locks--> LOCKED                             (write only: explicit write + complete approval)
  LOCKED --verify_backup--> BACKED_UP --plan_write--> WRITE_PLANNED --record_save--> SAVED
  SAVED --readback(match)--> VERIFIED
  SAVED --readback(mismatch)--> RESTORE_REQUIRED --record_restore--> RESTORED | RESTORE_FAILED
  any state that holds a lock --release_locks--> RELEASED (terminal); a lock-free refusal ends in REFUSED.
Any failure after a lock is created moves to RELEASE_REQUIRED; release_locks() is the only way out, which models the
executor's try/finally (locks_to_release lists exactly the locks this run created).
C-1155 conventions (run_bk56_60_deferred_selection.ps1): both locks (repo-root ENGINE_LOCK.json and
Docs/BossCombatReview/Execution/ENGINE_LOCK.json), one 32-hex owner token, policy C-1155, release only on a token match.
"""
import copy
import re

LOCK_PATHS = ("ENGINE_LOCK.json", "Docs/BossCombatReview/Execution/ENGINE_LOCK.json")
TOKEN = re.compile(r"[0-9a-f]{32}")
HEX64 = re.compile(r"[0-9a-f]{64}")
HOLDS_LOCKS = {"LOCKED", "BACKED_UP", "WRITE_PLANNED", "SAVED", "VERIFIED", "RESTORE_REQUIRED", "RESTORED",
               "RESTORE_FAILED", "RELEASE_REQUIRED"}
# BK-194 (X-2042): the same backup-path contract as the planner (safe_backup_path) and the receipt validator
# (_safe_backup_path); kept local so injected test binders need no planner attribute. Parity is test-pinned.
BACKUP_PREFIX = "Docs/BossCombatReview/Execution/"


def _safe_backup_path(value):
    if not isinstance(value, str) or not value.startswith(BACKUP_PREFIX) or "\\" in value or ":" in value:
        return False
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        return False
    return all(part not in ("", ".", "..") for part in value.split("/"))


class ExecutorContract:
    def __init__(self, binder, party="C"):
        self.binder = binder
        self.party = party
        self.state = "INIT"
        self.history = ["INIT"]
        self.errors = []
        self.binding = None
        self.explicit_write = False
        self.token = None
        self.created_locks = []
        self.dry_snapshot = None
        self.dry_plan = None
        self.reviewed_writes = None
        self.reviewed_untouched_phase_rows = None
        self.reviewed_untouched_phase_snapshot = None
        self.locked_snapshot = None
        self.plan = None
        self.outcome = None

    # ------------------------------------------------------------------ helpers
    def _move(self, state):
        self.state = state
        self.history.append(state)

    def _refuse(self, message):
        """Refuse the requested step. Without locks the run ends REFUSED; with locks it must release them."""
        self.errors.append(message)
        self._move("RELEASE_REQUIRED" if self.created_locks else "REFUSED")
        return {"ok": False, "state": self.state, "errors": [message], "next": self.next_step()}

    def _wrong_state(self, step, expected):
        message = "%s is not allowed in state %s (expected %s)" % (step, self.state, " or ".join(expected))
        self.errors.append(message)
        return {"ok": False, "state": self.state, "errors": [message], "next": self.next_step()}

    def _ok(self):
        return {"ok": True, "state": self.state, "errors": [], "next": self.next_step()}

    def next_step(self):
        return {"INIT": "start", "STARTED": "plan_dry_run", "DRY_RUN_PLANNED": "acquire_locks" if self.explicit_write else "done",
                "LOCKED": "verify_backup", "BACKED_UP": "plan_write", "WRITE_PLANNED": "record_save", "SAVED": "readback",
                "VERIFIED": "release_locks", "RESTORE_REQUIRED": "record_restore", "RESTORED": "release_locks",
                "RESTORE_FAILED": "release_locks", "RELEASE_REQUIRED": "release_locks", "RELEASED": "done",
                "REFUSED": "done"}[self.state]

    @property
    def locks_to_release(self):
        return list(self.created_locks) if self.state in HOLDS_LOCKS else []

    # ------------------------------------------------------------------ transitions
    def start(self, binding, explicit_write=False):
        if self.state != "INIT":
            return self._wrong_state("start", ["INIT"])
        if binding is None or not hasattr(binding, "get"):
            return self._refuse("a binding from bind_owner_approval() is required")
        if binding.get("bound") is not True:
            return self._refuse("owner source is missing or malformed (binding not bound): %s" % "; ".join(binding.get("errors") or []))
        self.binding = binding
        self.explicit_write = explicit_write is True
        self._move("STARTED")
        return self._ok()

    def plan_dry_run(self, snapshot):
        if self.state != "STARTED":
            return self._wrong_state("plan_dry_run", ["STARTED"])
        plan = self.binder.plan_from_bound(self.binding, snapshot, {"operation": "in_place_update", "mode": "dry_run"})
        if not plan.get("accepted"):
            return self._refuse("dry-run plan refused: %s" % "; ".join(plan.get("errors") or []))
        self.dry_snapshot = copy.deepcopy(snapshot)
        self.dry_plan = copy.deepcopy(plan)
        self.reviewed_writes = tuple((w.get("field_path"), w.get("from"), w.get("to")) for w in plan.get("writes", []))
        self.reviewed_untouched_phase_rows = copy.deepcopy(plan.get("untouched_phase_rows"))
        self.reviewed_untouched_phase_snapshot = copy.deepcopy(plan.get("untouched_phase_snapshot"))
        self.plan = plan
        self._move("DRY_RUN_PLANNED")
        if not self.explicit_write:
            self.outcome = "DRY_RUN_ONLY"
        return self._ok()

    def acquire_locks(self, token, observed, created_paths):
        """Accept explicit atomic-create receipts plus readback records; token equality alone does not prove creation."""
        if self.state != "DRY_RUN_PLANNED":
            return self._wrong_state("acquire_locks", ["DRY_RUN_PLANNED"])
        if not isinstance(created_paths, (list, tuple, set)):
            return self._refuse("lock creation receipts must list only known lock paths")
        created_known = [path for path in created_paths if isinstance(path, str) and path in LOCK_PATHS]
        # Receipts identify this invocation's create attempts. The executor must still compare the current record's
        # token before deleting; keep every valid receipt visible so missing/garbled readback cannot strand a lock.
        self.created_locks = list(dict.fromkeys(created_known))
        if len(created_known) != len(created_paths) or len(set(created_known)) != len(created_known):
            return self._refuse("lock creation receipts contain unknown or duplicate paths")
        if not self.explicit_write:
            return self._refuse("write refused: explicit write opt-in was not given (dry-run is the default)")
        if not self.binding.get("approval_complete"):
            return self._refuse("write refused: owner approval is incomplete (X-1991 unresolved)")
        if not (isinstance(token, str) and TOKEN.fullmatch(token)):
            return self._refuse("lock identity failure: the run token must be 32 lowercase hex")
        observed = observed if isinstance(observed, dict) else {}
        records = {path: observed.get(path) for path in LOCK_PATHS}
        if len(self.created_locks) != len(LOCK_PATHS) or any(not isinstance(record, dict) or record.get("owner_token") != token
                                                             for record in records.values()):
            held = [path for path, record in records.items() if isinstance(record, dict) and record.get("owner_token") != token]
            reason = ("held by another owner: %s" % ", ".join(held)) if held else "a create did not succeed, lacks a receipt, or readback is missing"
            return self._refuse("lock acquisition failed (%s); both C-1155 locks under this run's token are required" % reason)
        bad = [path for path, record in records.items() if record.get("party") != self.party or record.get("policy") != "C-1155"]
        if bad:
            return self._refuse("lock identity failure: %s must be party %s with policy C-1155" % (", ".join(bad), self.party))
        self.token = token
        self._move("LOCKED")
        return self._ok()

    def verify_backup(self, snapshot, backup):
        """snapshot: readback taken under the locks; backup: {"path", "sha256"} of the copy the executor made."""
        if self.state != "LOCKED":
            return self._wrong_state("verify_backup", ["LOCKED"])
        before = snapshot.get("file_sha256") if isinstance(snapshot, dict) else None
        if not (isinstance(before, str) and HEX64.fullmatch(before)):
            return self._refuse("locked snapshot needs the asset file before-hash")
        if before != self.dry_snapshot.get("file_sha256"):
            return self._refuse("the asset changed between the dry run and the locked snapshot; re-run the dry run")
        if not (isinstance(backup, dict) and isinstance(backup.get("path"), str) and backup.get("path")
                and backup.get("sha256") == before):
            return self._refuse("backup mismatch: the backup sha256 must equal the asset before-hash")
        if not _safe_backup_path(backup.get("path")):
            return self._refuse("backup mismatch: the backup path must be a safe repo-relative path below %s" % BACKUP_PREFIX)
        self.locked_snapshot = copy.deepcopy(snapshot)
        self.backup = copy.deepcopy(backup)
        self._move("BACKED_UP")
        return self._ok()

    def plan_write(self):
        if self.state != "BACKED_UP":
            return self._wrong_state("plan_write", ["BACKED_UP"])
        context = {"operation": "in_place_update", "mode": "write", "explicit_write": True,
                   "locks": {"root_held": True, "execution_held": True, "owner_token": self.token}, "backup": self.backup}
        plan = self.binder.plan_from_bound(self.binding, self.locked_snapshot, context, allow_write=True)
        if not plan.get("accepted"):
            return self._refuse("write plan refused: %s" % "; ".join(plan.get("errors") or []))
        writes = tuple((w.get("field_path"), w.get("from"), w.get("to")) for w in plan.get("writes", []))
        if writes != self.reviewed_writes or plan.get("untouched_phase_rows") != self.reviewed_untouched_phase_rows \
                or plan.get("untouched_phase_snapshot") != self.reviewed_untouched_phase_snapshot:
            return self._refuse("write plan differs from the dry-run diff reviewed before lock acquisition")
        self.plan = plan
        self._move("WRITE_PLANNED")
        return self._ok()

    def record_save(self, saved):
        if self.state != "WRITE_PLANNED":
            return self._wrong_state("record_save", ["WRITE_PLANNED"])
        if saved is not True:
            # A failed save may have left a partial package: restore from the backup before releasing.
            self.errors.append("save failed")
            self._move("RESTORE_REQUIRED")
            return {"ok": False, "state": self.state, "errors": ["save failed"], "next": self.next_step()}
        self._move("SAVED")
        return self._ok()

    def readback(self, after_snapshot):
        if self.state != "SAVED":
            return self._wrong_state("readback", ["SAVED"])
        result = self.binder.PLANNER.verify_readback(self.plan, after_snapshot)
        if result.get("ok"):
            self._move("VERIFIED")
            return self._ok()
        self.errors.extend(result.get("errors") or ["readback mismatch"])
        self._move("RESTORE_REQUIRED")
        return {"ok": False, "state": self.state, "errors": result.get("errors") or ["readback mismatch"], "next": self.next_step()}

    def record_restore(self, restored_sha256):
        if self.state != "RESTORE_REQUIRED":
            return self._wrong_state("record_restore", ["RESTORE_REQUIRED"])
        if restored_sha256 == self.locked_snapshot.get("file_sha256"):
            self._move("RESTORED")
            return self._ok()
        self.errors.append("restore did not bring back the before-hash")
        self._move("RESTORE_FAILED")
        return {"ok": False, "state": self.state, "errors": ["restore did not bring back the before-hash"], "next": self.next_step()}

    def release_locks(self, released):
        """released: {lock path: True if this run's lock file was removed after a token match}. Always ends the run."""
        if self.state not in HOLDS_LOCKS:
            return self._wrong_state("release_locks", sorted(HOLDS_LOCKS))
        released = released if isinstance(released, dict) else {}
        retained = [path for path in self.created_locks if released.get(path) is not True]
        prior = self.state
        self._move("RELEASED")
        if retained:
            self.errors.append("locks retained after release: %s" % ", ".join(retained))
            self.outcome = "LOCK_RETAINED_NEEDS_OPERATOR"
        elif prior == "VERIFIED":
            self.outcome = "WRITTEN_AND_VERIFIED"
        elif prior == "RESTORED":
            self.outcome = "FAILED_RESTORED"
        elif prior == "RESTORE_FAILED":
            self.outcome = "FAILED_RESTORE_NEEDS_OPERATOR"
        else:
            self.outcome = "REFUSED_AFTER_LOCKS"
        return {"ok": not retained and prior == "VERIFIED", "state": self.state, "errors": list(self.errors), "outcome": self.outcome,
                "next": "done"}
