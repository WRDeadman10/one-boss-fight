"""BK-135 (C, implementer; X-2017, reworked for X-2019..X-2021): synthetic tests for the PROPOSED v2 receipt schema (sevarog_receipt_v2_proposal.py).

Synthetic receipts only. The real ExecutorContract is driven with a stub binder (no files, Unreal, assets or locks) to
check that v2 history/outcome rules match the contract. The v1 validator is imported read-only for compatibility checks.
A valid v2 receipt is not runtime proof or write authorization; X-1991 remains open.
"""
import ast
import copy
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, HERE / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


P = load("sevarog_receipt_v2_proposal", "sevarog_receipt_v2_proposal.py")
C = load("sevarog_executor_contract_v2test", "sevarog_executor_contract.py")
F = load("receipt_fixtures_v2test", "test_validate_sevarog_executor_receipt.py")
V1 = F.V
DRY, AFTER, BAD, PLAN, REPLY = "a" * 64, "b" * 64, "e" * 64, "c" * 64, "d" * 64
TOKEN, OTHER = "0123456789abcdef0123456789abcdef", "f" * 32
BACKUP = "Docs/BossCombatReview/Execution/Claude/Run_synthetic/asset.uasset"
SRC = {"message_id": "O-77", "sender": "Owner", "path": P.MAILBOX_PATH, "sha256": REPLY}
NULL_SRC = {k: None for k in P.SOURCE_KEYS}
AUTO = object()
SKIPPED = {"attempted": False, "copy_result": None, "path": None, "observed_sha256": None, "verified": False,
           "cleanup_attempted": False, "cleanup_readback": "not_observed", "final_state": "none"}


def copy_record(observed=DRY, verified=False, result="created", cleanup=False, readback="not_observed", final=None):
    record = {"attempted": True, "copy_result": result, "path": BACKUP, "observed_sha256": observed, "verified": verified,
              "cleanup_attempted": cleanup, "cleanup_readback": readback, "final_state": None}
    record["final_state"] = final if final is not None else P.backup_final_state(record)
    return record


def H(*tail):
    return ["INIT", "STARTED", "DRY_RUN_PLANNED", *tail]


WRITE = ("LOCKED", "BACKED_UP", "WRITE_PLANNED", "SAVED")


def make(history, refusal=None, created=None, released=None, before=DRY, after=AFTER, restored=None, backup=AUTO,
         source=SRC, outcome=None, artifacts=None):
    holds = any(s in P.HOLDS_LOCKS for s in history)
    created = created if created is not None else ((True, True) if holds else (False, False))
    released = released if released is not None else created
    locks = []
    for index, (path, made, rel) in enumerate(zip(P.LOCK_PATHS, created, released)):
        if made:
            locks.append({"path": path, "created": True, "create_order": index + 1, "token": TOKEN, "readback_token": TOKEN, "party": "X",
                          "policy": "C-1155", "release_attempted": True, "release_token_match": rel, "released": rel})
        else:
            locks.append({"path": path, "created": False, "create_order": None, "token": None, "readback_token": None, "party": None,
                          "policy": None, "release_attempted": False, "release_token_match": False, "released": False})
    reason = refusal["reason"] if refusal else None
    compared = "BACKED_UP" in history or reason in ("ASSET_CHANGED", "BACKUP_MISMATCH")
    asset = {"path": P.ASSET_PATH, "dry_run_sha256": DRY if "DRY_RUN_PLANNED" in history else None,
             "locked_before_sha256": before if compared else None, "after_sha256": after if "SAVED" in history else None,
             "restored_sha256": restored}
    if backup is AUTO:
        backup = copy_record(observed=before, verified="BACKED_UP" in history) if "LOCKED" in history else None
    receipt = {"schema": P.SCHEMA_V2, "outcome": None, "source": copy.deepcopy(source),
               "plan_sha256": PLAN if "DRY_RUN_PLANNED" in history else None, "history": list(history),
               "refusal": copy.deepcopy(refusal), "asset": asset, "backup_attempt": copy.deepcopy(backup), "locks": locks,
               "artifacts": None}
    retained = [p for p, made, rel in zip(P.LOCK_PATHS, created, released) if made and not rel]
    receipt["outcome"] = outcome or P.derive_outcome(history, bool(retained))
    kept = backup if isinstance(backup, dict) and backup.get("final_state") in ("retained", "unknown") else None
    receipt["artifacts"] = artifacts if artifacts is not None else P.expected_artifacts(history, retained, kept, asset)
    return receipt


SCENARIOS = {
    "dry_run": dict(history=H()),
    "written": dict(history=H(*WRITE, "VERIFIED", "RELEASED")),
    "readback_failed_restored": dict(history=H(*WRITE, "RESTORE_REQUIRED", "RESTORED", "RELEASED"), restored=DRY),
    "save_failed_restored": dict(history=H("LOCKED", "BACKED_UP", "WRITE_PLANNED", "RESTORE_REQUIRED", "RESTORED", "RELEASED"), restored=DRY),
    "restore_failed": dict(history=H(*WRITE, "RESTORE_REQUIRED", "RESTORE_FAILED", "RELEASED"), restored=BAD),
    "retained_after_write": dict(history=H(*WRITE, "VERIFIED", "RELEASED"), released=(True, False)),
    "retained_after_restore_failed": dict(history=H(*WRITE, "RESTORE_REQUIRED", "RESTORE_FAILED", "RELEASED"), restored=BAD, released=(False, True)),
    "refused_at_start": dict(history=["INIT", "REFUSED"], refusal={"stage": "INIT", "reason": "SOURCE_UNBOUND"}, source=NULL_SRC),
    "refused_dry_plan": dict(history=["INIT", "STARTED", "REFUSED"], refusal={"stage": "STARTED", "reason": "DRY_PLAN_REFUSED"}),
    "refused_no_lock_created": dict(history=H("REFUSED"), refusal={"stage": "DRY_RUN_PLANNED", "reason": "ACQUISITION_FAILED"}),
    "partial_lock": dict(history=H("RELEASE_REQUIRED", "RELEASED"), created=(True, False), refusal={"stage": "DRY_RUN_PLANNED", "reason": "ACQUISITION_FAILED"}),
    "approval_incomplete_two_created": dict(history=H("RELEASE_REQUIRED", "RELEASED"), refusal={"stage": "DRY_RUN_PLANNED", "reason": "APPROVAL_INCOMPLETE"}),
    "before_hash_missing": dict(history=H("LOCKED", "RELEASE_REQUIRED", "RELEASED"), refusal={"stage": "LOCKED", "reason": "BEFORE_HASH_MISSING"}, backup=SKIPPED),
    "asset_changed": dict(history=H("LOCKED", "RELEASE_REQUIRED", "RELEASED"), refusal={"stage": "LOCKED", "reason": "ASSET_CHANGED"}, before=BAD,
                          backup=copy_record(observed=BAD, cleanup=True, readback="absent")),
    "backup_mismatch_retained": dict(history=H("LOCKED", "RELEASE_REQUIRED", "RELEASED"), refusal={"stage": "LOCKED", "reason": "BACKUP_MISMATCH"},
                                     backup=copy_record(observed=BAD, cleanup=True, readback="present")),
    "write_plan_diverged": dict(history=H("LOCKED", "BACKED_UP", "RELEASE_REQUIRED", "RELEASED"), refusal={"stage": "BACKED_UP", "reason": "WRITE_PLAN_DIVERGED"}),
    "aborted_locked": dict(history=H("LOCKED", "RELEASED"), refusal={"stage": "LOCKED", "reason": "EXECUTOR_ABORTED"}, backup=SKIPPED),
    "abandoned_after_save": dict(history=H(*WRITE, "RELEASED"), refusal={"stage": "SAVED", "reason": "EXECUTOR_ABORTED"}),
}
OUTCOME_OF = {
    "dry_run": "DRY_RUN_ONLY", "written": "WRITTEN_AND_VERIFIED", "readback_failed_restored": "FAILED_RESTORED",
    "save_failed_restored": "FAILED_RESTORED", "restore_failed": "FAILED_RESTORE_NEEDS_OPERATOR",
    "retained_after_write": "LOCK_RETAINED_NEEDS_OPERATOR", "retained_after_restore_failed": "LOCK_RETAINED_NEEDS_OPERATOR",
    "refused_at_start": "REFUSED_BEFORE_LOCKS", "refused_dry_plan": "REFUSED_BEFORE_LOCKS",
    "refused_no_lock_created": "REFUSED_BEFORE_LOCKS", "partial_lock": "REFUSED_AFTER_LOCKS",
    "approval_incomplete_two_created": "REFUSED_AFTER_LOCKS", "before_hash_missing": "REFUSED_AFTER_LOCKS",
    "asset_changed": "REFUSED_AFTER_LOCKS", "backup_mismatch_retained": "REFUSED_AFTER_LOCKS",
    "write_plan_diverged": "REFUSED_AFTER_LOCKS", "aborted_locked": "REFUSED_AFTER_LOCKS",
    "abandoned_after_save": "ABANDONED_NEEDS_OPERATOR",
}


def scenario(name, **override):
    args = dict(SCENARIOS[name])
    args.update(override)
    return make(**args)


def errors(receipt):
    return P.validate_v2(receipt)["errors"]


class ValidForms(unittest.TestCase):
    def test_every_scenario_is_valid_with_the_expected_outcome(self):
        self.assertEqual(set(SCENARIOS), set(OUTCOME_OF))
        for name in SCENARIOS:
            with self.subTest(name):
                result = P.validate_v2(scenario(name))
                self.assertTrue(result["valid"], result["errors"])
                self.assertEqual(result["derived_outcome"], OUTCOME_OF[name])

    def test_every_v2_outcome_is_reachable(self):
        self.assertEqual(set(OUTCOME_OF.values()), P.OUTCOMES_V2)


class Bk131HistoryAndOutcome(unittest.TestCase):
    def test_illegal_histories_are_refused(self):
        self.assertTrue(P.validate_v2(make(H()))["valid"])
        for label, history in (("skip dry run", ["INIT", "STARTED", "LOCKED", "RELEASED"]),
                               ("save without backup", H("LOCKED", "WRITE_PLANNED", "SAVED", "VERIFIED", "RELEASED")),
                               ("verified then restore", H(*WRITE, "VERIFIED", "RESTORE_REQUIRED")),
                               ("not from INIT", ["STARTED", "DRY_RUN_PLANNED"]),
                               ("non-terminal end", H("LOCKED")), ("too long", H(*WRITE, "VERIFIED", "RELEASED") * 2),
                               ("empty", []), ("non-string", ["INIT", 3]), ("refused from LOCKED", H("LOCKED", "REFUSED"))):
            with self.subTest(label):
                r = make(H()); r["history"] = history
                self.assertFalse(P.validate_v2(r)["valid"])

    def test_claimed_outcome_must_equal_the_derived_one(self):
        for name, wrong in (("written", "FAILED_RESTORED"), ("abandoned_after_save", "REFUSED_AFTER_LOCKS"),
                            ("retained_after_write", "WRITTEN_AND_VERIFIED"), ("refused_no_lock_created", "REFUSED_AFTER_LOCKS"),
                            ("dry_run", "BOGUS"), ("dry_run", ["DRY_RUN_ONLY"])):
            with self.subTest(name=name, wrong=wrong):
                r = scenario(name); r["outcome"] = wrong
                self.assertFalse(P.validate_v2(r)["valid"])

    def test_refusal_record_must_match_the_history(self):
        cases = [("written", {"stage": "LOCKED", "reason": "ASSET_CHANGED"}),  # success cannot carry a refusal
                 ("partial_lock", None), ("partial_lock", {"stage": "LOCKED", "reason": "ACQUISITION_FAILED"}),
                 ("partial_lock", {"stage": "DRY_RUN_PLANNED", "reason": "ASSET_CHANGED"}),
                 ("aborted_locked", {"stage": "LOCKED", "reason": "BEFORE_HASH_MISSING"}),
                 ("asset_changed", {"stage": "LOCKED", "reason": "EXECUTOR_ABORTED"}),
                 ("refused_dry_plan", {"stage": "STARTED", "reason": 5}), ("refused_dry_plan", {"stage": "STARTED"})]
        for name, refusal in cases:
            with self.subTest(name=name, refusal=refusal):
                r = scenario(name); r["refusal"] = refusal
                self.assertFalse(P.validate_v2(r)["valid"])


class Bk132AssetHashes(unittest.TestCase):
    def test_dry_and_locked_hashes_are_separate_and_staged(self):
        r = scenario("dry_run"); r["asset"]["locked_before_sha256"] = DRY
        self.assertIn("asset.locked_before_sha256 must be null when no locked snapshot was compared", errors(r))
        r = scenario("dry_run"); r["asset"]["dry_run_sha256"] = None
        self.assertIn("asset.dry_run_sha256 must be 64 hex once the dry run is planned", errors(r))
        r = scenario("refused_dry_plan"); r["asset"]["dry_run_sha256"] = DRY
        self.assertIn("asset.dry_run_sha256 must be null before the dry run", errors(r))
        r = scenario("partial_lock"); r["asset"]["locked_before_sha256"] = DRY
        self.assertIn("asset.locked_before_sha256 must be null when no locked snapshot was compared", errors(r))

    def test_locked_hash_relation_to_dry_hash(self):
        self.assertIn("the locked before-hash must equal the dry-run hash when the run continued past it",
                      errors(scenario("written", before=BAD, after=AFTER)))
        self.assertIn("ASSET_CHANGED requires the locked before-hash to differ from the dry-run hash",
                      errors(scenario("asset_changed", before=DRY, backup=copy_record(observed=DRY, cleanup=True, readback="absent"))))
        self.assertIn("the locked before-hash must equal the dry-run hash when the run continued past it",
                      errors(scenario("backup_mismatch_retained", before=AFTER)))

    def test_after_and_restored_hashes_follow_history(self):
        r = scenario("save_failed_restored"); r["asset"]["after_sha256"] = AFTER  # save never happened
        self.assertIn("asset.after_sha256 is 64 hex exactly when the history contains SAVED", errors(r))
        self.assertIn("a verified write must change the asset hash", errors(scenario("written", after=DRY)))
        self.assertIn("RESTORED requires restored_sha256 to equal the locked before-hash", errors(scenario("readback_failed_restored", restored=BAD)))
        needle = "RESTORE_FAILED requires restored_sha256 to be null (unknown) or a 64-hex hash other than the before-hash"
        self.assertIn(needle, errors(scenario("restore_failed", restored=DRY)))
        self.assertIn(needle, errors(scenario("restore_failed", restored="E" * 64)))
        self.assertIn("asset.restored_sha256 must be null when no restore was recorded", errors(scenario("written", restored=DRY)))
        self.assertIn("RESTORED requires restored_sha256 to equal the locked before-hash", errors(scenario("readback_failed_restored", restored=None)))

    def test_r3_restore_failed_with_unknown_readback_is_truthful(self):
        """R3 (X-2021): the contract records RESTORE_FAILED for record_restore(None) (C:195-203); v2 must accept a null
        restored hash and must not reuse the pre-restore after-hash as current asset evidence."""
        for name in ("restore_failed", "retained_after_restore_failed"):
            with self.subTest(name):
                r = scenario(name, restored=None)
                result = P.validate_v2(r)
                self.assertTrue(result["valid"], result["errors"])
                asset_items = [a for a in result["expected_artifacts"] if a["kind"] == "asset_needs_operator"]
                self.assertEqual(asset_items, [{"kind": "asset_needs_operator", "path": P.ASSET_PATH, "sha256": None}])
                r["artifacts"] = [a if a["kind"] != "asset_needs_operator" else dict(a, sha256=AFTER) for a in r["artifacts"]]
                self.assertIn("artifacts must list exactly the derived operator leftovers", errors(r))
        contract = drive(("write", "lock", "backup", "plan", "save", "readback_bad", "restore_none", "release"))
        self.assertEqual(contract.outcome, "FAILED_RESTORE_NEEDS_OPERATOR")


class Bk133BackupAndArtifacts(unittest.TestCase):
    def test_backup_presence_follows_the_stage(self):
        needle = "backup_attempt is required once the locks were held (attempted may be false)"
        self.assertIn(needle, errors(scenario("written", backup=None)))
        self.assertIn(needle, errors(scenario("before_hash_missing", backup=None)))
        self.assertIn("backup_attempt must be null before the locks were held", errors(scenario("partial_lock", backup=SKIPPED)))
        self.assertIn("the backup may be skipped only for BEFORE_HASH_MISSING or an abort before BACKED_UP",
                      errors(scenario("asset_changed", backup=SKIPPED)))
        self.assertTrue(P.validate_v2(scenario("before_hash_missing", backup=copy_record(observed=None)))["valid"])

    def test_r1_malformed_enum_and_flag_types_fail_closed_without_exceptions(self):
        """R1 (X-2020): enum fields were checked with a bare `in SET`; an unhashable value raised TypeError."""
        for key in ("copy_result", "cleanup_readback", "final_state", "attempted", "verified", "cleanup_attempted",
                    "path", "observed_sha256"):
            for value in ([], {}, 1.5, None, "bogus"):
                with self.subTest(key=key, value=value):
                    r = scenario("backup_mismatch_retained")
                    r["backup_attempt"][key] = value
                    if key == "observed_sha256" and value is None:
                        continue  # null observed hash is a valid "not read" observation here
                    self.assertFalse(P.validate_v2(r)["valid"])
        for key in ("create_order",):
            for value in ([], {}, True, "1", 0, 3):
                with self.subTest(key=key, value=value):
                    r = scenario("written"); r["locks"][0][key] = value
                    self.assertFalse(P.validate_v2(r)["valid"])

    def test_r2_final_state_is_derived_and_removal_needs_an_absent_readback(self):
        """R2 (X-2020): a deletion claim without an observed-absent readback is refused; no-copy and removed differ."""
        cases = [  # (copy_result, cleanup_attempted, cleanup_readback) -> derived final_state
            (("created", False, "not_observed"), "kept_evidence"),
            (("created", True, "absent"), "removed"),
            (("created", True, "present"), "retained"),
            (("created", True, "not_observed"), "unknown"),
            (("failed", False, "absent"), "none"),
            (("failed", False, "not_observed"), "unknown"),
            (("unknown", False, "not_observed"), "unknown"),
            (("unknown", True, "absent"), "removed"),
        ]
        for (result, cleanup, readback), final in cases:
            with self.subTest(result=result, cleanup=cleanup, readback=readback):
                observed = BAD if result == "created" else None
                record = copy_record(observed=observed, result=result, cleanup=cleanup, readback=readback)
                self.assertEqual(record["final_state"], final)
                r = scenario("backup_mismatch_retained", backup=record)
                self.assertTrue(P.validate_v2(r)["valid"], errors(r))
                kinds = [a["kind"] for a in r["artifacts"]]
                self.assertEqual("backup" in kinds, final in ("retained", "unknown"))
                for other in P.FINAL_STATES - {final}:
                    claimed = dict(record, final_state=other)
                    self.assertIn("backup_attempt.final_state must be %s (derived from the observations)" % final,
                                  errors(scenario("backup_mismatch_retained", backup=claimed)))
        unobserved = copy_record(observed=BAD, cleanup=True, readback="not_observed", final="removed")
        self.assertIn("backup_attempt.final_state must be unknown (derived from the observations)",
                      errors(scenario("asset_changed", backup=unobserved)))
        self.assertNotEqual(SKIPPED["final_state"], copy_record(cleanup=True, readback="absent")["final_state"],
                            "no copy and a removed copy are different observations")

    def test_backup_record_rules(self):
        verified = dict(observed=DRY, verified=True)
        for label, record, needle in (
                ("unsafe path", dict(copy_record(**verified), path="C:/x.uasset"), "backup_attempt.path must be a safe path"),
                ("traversal", dict(copy_record(**verified), path="Docs/BossCombatReview/Execution/../x"), "backup_attempt.path must be a safe path"),
                ("outside evidence", dict(copy_record(**verified), path="Saved/x.uasset"), "backup_attempt.path must be a safe path"),
                ("bad hash", copy_record(observed="A" * 64, verified=True), "backup_attempt.observed_sha256 must be null"),
                ("verified flag", copy_record(observed=DRY, verified=False), "backup_attempt.verified must be True"),
                ("verified hash differs", copy_record(observed=BAD, verified=True), "a verified backup is a created copy whose observed hash"),
                ("verified unread", copy_record(observed=None, verified=True), "a verified backup is a created copy whose observed hash"),
                ("verified cleaned", copy_record(observed=DRY, verified=True, cleanup=True, readback="absent"), "cannot be cleaned up"),
                ("failed copy with hash", copy_record(observed=DRY, verified=True, result="failed"), "only a created copy can have an observed hash"),
                ("present without cleanup", copy_record(observed=DRY, verified=True, readback="present", final="kept_evidence"), "only meaningful after a cleanup attempt"),
                ("skipped with a path", dict(SKIPPED, path=BACKUP), "a backup that was not attempted cannot claim")):
            with self.subTest(label):
                found = errors(scenario("written", backup=record))
                self.assertTrue(any(needle in e for e in found), found)
        r = scenario("backup_mismatch_retained", backup=copy_record(observed=DRY, cleanup=True, readback="present"))
        self.assertIn("BACKUP_MISMATCH requires an observed backup hash that differs from the locked before-hash (or none)", errors(r))

    def test_artifacts_are_exactly_the_derived_leftovers(self):
        self.assertEqual(scenario("written")["artifacts"], [])
        self.assertEqual(sorted(a["kind"] for a in scenario("retained_after_restore_failed")["artifacts"]), ["asset_needs_operator", "lock"])
        self.assertEqual(scenario("backup_mismatch_retained")["artifacts"], [{"kind": "backup", "path": BACKUP, "sha256": BAD}])
        self.assertEqual(scenario("abandoned_after_save")["artifacts"], [{"kind": "asset_needs_operator", "path": P.ASSET_PATH, "sha256": None}])
        self.assertEqual(scenario("restore_failed")["artifacts"], [{"kind": "asset_needs_operator", "path": P.ASSET_PATH, "sha256": BAD}])
        unknown = scenario("backup_mismatch_retained", backup=copy_record(observed=BAD, cleanup=True, readback="not_observed"))
        self.assertEqual(unknown["artifacts"], [{"kind": "backup", "path": BACKUP, "sha256": None}])
        for name, artifacts in (("retained_after_write", []), ("written", [{"kind": "lock", "path": P.LOCK_PATHS[0], "sha256": None}]),
                                ("restore_failed", []), ("backup_mismatch_retained", "x"),
                                ("written", [{"kind": "lock"}]), ("written", [{}] * 5)):
            with self.subTest(name=name, artifacts=artifacts):
                r = scenario(name); r["artifacts"] = artifacts
                self.assertFalse(P.validate_v2(r)["valid"])
        r = scenario("retained_after_restore_failed"); r["artifacts"].reverse()
        self.assertTrue(P.validate_v2(r)["valid"], "artifact order is not significant")


class Bk134LockOrder(unittest.TestCase):
    def test_acquisition_order_is_explicit_not_the_array_index(self):
        """X-2019: order comes from create_order, not from the canonical array position; root must be first."""
        root_first = "the repo-root lock must be created first (create_order 1), as the runner does"
        r = scenario("partial_lock", created=(False, True)); r["locks"][1]["create_order"] = 1  # only execution created
        self.assertIn(root_first, errors(r))
        r = scenario("written"); r["locks"][0]["create_order"], r["locks"][1]["create_order"] = 2, 1
        self.assertIn(root_first, errors(r))
        r = scenario("written"); r["locks"][1]["create_order"] = 1
        self.assertIn("create_order must number the created locks 1..n without gaps or repeats", errors(r))
        r = scenario("partial_lock"); r["locks"][0]["create_order"] = 2
        self.assertIn("create_order must number the created locks 1..n without gaps or repeats", errors(r))
        r = scenario("partial_lock"); r["locks"][1]["create_order"] = 2
        self.assertIn("locks[1] was not created, so create_order must be null", errors(r))

    def test_locked_runs_need_both_matching_locks_and_refusals_may_show_foreign_readback(self):
        self.assertIn("a run that reached LOCKED created both locks", errors(scenario("aborted_locked", created=(True, False))))
        r = scenario("written"); r["locks"][1]["readback_token"] = OTHER
        self.assertIn("locks[1] readback must match the run token, party and C-1155 policy", errors(r))
        r = scenario("approval_incomplete_two_created"); r["locks"][1].update(readback_token=OTHER, party=None, policy=None)
        self.assertTrue(P.validate_v2(r)["valid"], errors(r))
        r = scenario("approval_incomplete_two_created"); r["locks"][1]["party"] = "Z"
        self.assertIn("locks[1] party/policy must be null or a team C-1155 identity", errors(r))

    def test_release_is_attempted_for_every_created_lock_in_any_order(self):
        r = scenario("written"); r["locks"][0]["release_attempted"] = False
        self.assertIn("locks[0] was created, so release must be attempted (executor finally)", errors(r))
        r = scenario("written"); r["locks"][0]["release_token_match"] = False
        self.assertIn("locks[0] is released exactly when its release token matched", errors(r))
        self.assertNotIn("release_order", P.LOCK_KEYS, "release order is deliberately not recorded or constrained")

    def test_lock_free_runs_cannot_claim_locks_and_lock_runs_must(self):
        self.assertIn("a run that never held locks cannot record a created lock", errors(scenario("refused_no_lock_created", created=(True, False))))
        self.assertIn("a lock-holding run must record at least one created lock", errors(scenario("partial_lock", created=(False, False))))
        r = scenario("approval_incomplete_two_created"); r["locks"][1]["token"] = OTHER
        self.assertIn("created locks must share one run token", errors(r))
        r = scenario("written"); r["locks"][1]["party"] = "C"
        self.assertIn("created locks must belong to one party", errors(r))


class StubPlanner:
    @staticmethod
    def verify_readback(_plan, after):
        return {"ok": after.get("ok") is True, "errors": [] if after.get("ok") is True else ["mismatch"]}


class StubBinder:
    PLANNER = StubPlanner

    @staticmethod
    def plan_from_bound(_binding, _snapshot, _context, allow_write=False):
        return {"accepted": True, "writes": [{"field_path": "Health", "from": 1, "to": 2}], "untouched_phase_rows": []}


def drive(steps):
    contract = C.ExecutorContract(StubBinder(), party="X")
    explicit = steps[0] != "dry"
    contract.start({"bound": True, "approval_complete": True}, explicit_write=explicit)
    contract.plan_dry_run({"file_sha256": DRY})
    observed = {p: {"owner_token": TOKEN, "party": "X", "policy": "C-1155"} for p in C.LOCK_PATHS}
    for step in steps[1:]:
        if step == "lock":
            contract.acquire_locks(TOKEN, observed, list(C.LOCK_PATHS))
        elif step == "lock_partial":
            contract.acquire_locks(TOKEN, {C.LOCK_PATHS[0]: observed[C.LOCK_PATHS[0]]}, [C.LOCK_PATHS[0]])
        elif step == "backup":
            contract.verify_backup({"file_sha256": DRY}, {"path": BACKUP, "sha256": DRY})
        elif step == "backup_bad":
            contract.verify_backup({"file_sha256": DRY}, {"path": BACKUP, "sha256": BAD})
        elif step == "plan":
            contract.plan_write()
        elif step in ("save", "save_failed"):
            contract.record_save(step == "save")
        elif step in ("readback_ok", "readback_bad"):
            contract.readback({"ok": step == "readback_ok"})
        elif step in ("restore_ok", "restore_bad", "restore_none"):
            contract.record_restore({"restore_ok": DRY, "restore_bad": BAD, "restore_none": None}[step])
        elif step in ("release", "release_root_only"):
            contract.release_locks({p: (step == "release" or p == C.LOCK_PATHS[0]) for p in C.LOCK_PATHS})
    return contract


class Bk135ContractCompatibility(unittest.TestCase):
    RUNS = {
        ("write", "lock", "backup", "plan", "save", "readback_ok", "release"): "WRITTEN_AND_VERIFIED",
        ("write", "lock", "backup", "plan", "save", "readback_bad", "restore_ok", "release"): "FAILED_RESTORED",
        ("write", "lock", "backup", "plan", "save_failed", "restore_ok", "release"): "FAILED_RESTORED",
        ("write", "lock", "backup", "plan", "save", "readback_bad", "restore_bad", "release"): "FAILED_RESTORE_NEEDS_OPERATOR",
        ("write", "lock", "backup", "plan", "save", "readback_ok", "release_root_only"): "LOCK_RETAINED_NEEDS_OPERATOR",
        ("write", "lock_partial", "release"): "REFUSED_AFTER_LOCKS",
        ("write", "lock", "backup_bad", "release"): "REFUSED_AFTER_LOCKS",
        ("dry",): "DRY_RUN_ONLY",
    }

    def test_contract_histories_are_legal_and_outcomes_agree(self):
        for steps, outcome in self.RUNS.items():
            with self.subTest(steps=steps):
                contract = drive(steps)
                self.assertTrue(P.check_history(contract.history, []), contract.history)
                retained = outcome == "LOCK_RETAINED_NEEDS_OPERATOR"  # the release_root_only run keeps one lock
                self.assertEqual(contract.outcome, outcome)
                self.assertEqual(P.derive_outcome(contract.history, retained), outcome)

    def test_divergence_release_after_save_is_abandoned_not_refused(self):
        """Deliberate v2 difference (BK-131 finding A6): the contract labels an early release from SAVED as
        REFUSED_AFTER_LOCKS (:207, :222-223) although the asset is already written; v2 derives ABANDONED_NEEDS_OPERATOR."""
        contract = drive(("write", "lock", "backup", "plan", "save", "release"))
        self.assertEqual(contract.outcome, "REFUSED_AFTER_LOCKS")
        self.assertEqual(P.derive_outcome(contract.history, False), "ABANDONED_NEEDS_OPERATOR")

    def test_constants_match_the_contract_and_v1(self):
        self.assertEqual(set(P.HOLDS_LOCKS), C.HOLDS_LOCKS)
        self.assertEqual(P.LOCK_PATHS, C.LOCK_PATHS)
        self.assertEqual(P.LOCK_PATHS, V1.LOCK_PATHS)
        self.assertEqual((P.ASSET_PATH, P.MAILBOX_PATH, P.EVIDENCE_PREFIX), (V1.ASSET_PATH, V1.MAILBOX_PATH, V1.BACKUP_PREFIX))
        self.assertTrue(V1.OUTCOMES < P.OUTCOMES_V2)
        self.assertEqual(P.OUTCOMES_V2 - V1.OUTCOMES, {"REFUSED_BEFORE_LOCKS", "ABANDONED_NEEDS_OPERATOR"})

    def test_schemas_are_disjoint_and_never_upgraded_in_place(self):
        for outcome in V1.OUTCOMES:
            with self.subTest(outcome):
                self.assertFalse(P.validate_v2(F.receipt(outcome))["valid"])
        for name in SCENARIOS:
            with self.subTest(name):
                self.assertFalse(V1.validate_receipt(scenario(name))["valid"])
        r = scenario("written"); r["schema"] = V1.SCHEMA
        self.assertIn("v1 receipts are never upgraded in place", " ".join(errors(r)))


class Purity(unittest.TestCase):
    def test_malformed_top_level_is_invalid_not_an_exception(self):
        for bad in (None, [], "x", {}, {k: None for k in P.TOP_KEYS}):
            with self.subTest(bad=bad):
                self.assertFalse(P.validate_v2(bad)["valid"])
        for key in P.TOP_KEYS - {"schema"}:
            for value in (None, [], {}, 3, "x"):
                with self.subTest(key=key, value=value):
                    r = scenario("retained_after_restore_failed"); r[key] = value
                    if key == "refusal" and value is None:
                        continue  # null refusal is the valid form here
                    self.assertFalse(P.validate_v2(r)["valid"])

    def test_input_not_mutated(self):
        r = scenario("backup_mismatch_retained")
        before = copy.deepcopy(r)
        P.validate_v2(r)
        self.assertEqual(r, before)

    def test_module_has_no_io(self):
        tree = ast.parse((HERE / "sevarog_receipt_v2_proposal.py").read_text(encoding="utf-8"))
        imports = {a.name for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) for a in n.names}
        self.assertEqual(imports, {"re"})
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        self.assertEqual(names & {"open", "__file__", "exec", "eval", "__import__"}, set())


if __name__ == "__main__":
    unittest.main()
