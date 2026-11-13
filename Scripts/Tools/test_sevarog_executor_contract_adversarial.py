"""BK-106..109 (C, implementer; X-2005): adversarial audit of sevarog_executor_contract.py.

New file; the contract itself is not modified in this batch. Defenses that hold are ordinary tests; confirmed gaps are
pinned as expectedFailure (test-first) for the lead to fix. Synthetic inputs only: fixtures come from the existing
contract test module; no filesystem writes, Unreal, assets or real locks.
"""
import copy
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("contract_fixtures", HERE / "test_sevarog_executor_contract.py")
F = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(F)
C, B = F.C, F.B
TOKEN, BEFORE = F.TOKEN, F.BEFORE
ALL = list(C.LOCK_PATHS)
BACKUP = {"path": "Docs/BossCombatReview/Execution/Claude/backup/DA_Boss_Sevarog_Draft.before.uasset", "sha256": BEFORE}


def planned(explicit=True):
    contract = C.ExecutorContract(B, party="C")
    assert contract.start(F.binding(), explicit_write=explicit)["ok"]
    assert contract.plan_dry_run(F.snapshot())["ok"]
    return contract


def locked():
    contract = planned()
    assert contract.acquire_locks(TOKEN, F.both_locks(), ALL)["ok"]
    return contract


class HeldDefenses(unittest.TestCase):
    """BK-106/107/108 probes the contract already survives."""

    def test_receipt_shapes_are_refused(self):
        for receipts in ("ENGINE_LOCK.json", None, 7, {"ENGINE_LOCK.json": 1}, ALL + ["Saved/ENGINE_LOCK.json"], ALL + [ALL[0]], [ALL[0], 3]):
            with self.subTest(receipts=receipts):
                contract = planned()
                self.assertFalse(contract.acquire_locks(TOKEN, F.both_locks(), receipts)["ok"])

    def test_token_case_party_and_policy_mismatches_are_refused(self):
        cases = {"uppercase record token": F.both_locks(**{ALL[0]: F.lock(token=TOKEN.upper())}),
                 "foreign party": F.both_locks(**{ALL[1]: F.lock(party="A")}),
                 "missing policy": F.both_locks(**{ALL[0]: {k: v for k, v in F.lock().items() if k != "policy"}})}
        for label, observed in cases.items():
            with self.subTest(label):
                self.assertFalse(planned().acquire_locks(TOKEN, observed, ALL)["ok"])

    def test_same_token_without_receipt_is_never_released(self):
        contract = planned()
        contract.acquire_locks(TOKEN, F.both_locks(), [ALL[0]])  # path 1 carries the token but has no create receipt
        self.assertEqual(contract.locks_to_release, [ALL[0]])

    def test_changed_or_malformed_snapshot_and_backup_are_refused(self):
        for label, snapshot, backup in (("changed hash", F.snapshot("d" * 64), dict(BACKUP, sha256="d" * 64)),
                                        ("uppercase hash", F.snapshot(BEFORE.upper()), dict(BACKUP, sha256=BEFORE.upper())),
                                        ("snapshot not a dict", "snapshot", BACKUP),
                                        ("backup hash mismatch", F.snapshot(), dict(BACKUP, sha256="c" * 64)),
                                        ("backup empty path", F.snapshot(), dict(BACKUP, path="")),
                                        ("backup not a dict", F.snapshot(), "b.uasset")):
            with self.subTest(label):
                contract = locked()
                self.assertFalse(contract.verify_backup(snapshot, backup)["ok"])
                self.assertEqual(contract.state, "RELEASE_REQUIRED")
                self.assertEqual(contract.locks_to_release, ALL)

    def test_repeated_and_terminal_transitions_do_not_move(self):
        contract = locked()
        self.assertFalse(contract.acquire_locks(TOKEN, F.both_locks(), ALL)["ok"])  # repeat
        self.assertEqual(contract.state, "LOCKED")
        contract.release_locks({path: True for path in ALL})
        for step, args in (("release_locks", ({},)), ("plan_write", ()), ("record_restore", (BEFORE,)), ("start", (F.binding(),))):
            with self.subTest(step):
                self.assertFalse(getattr(contract, step)(*args)["ok"])
                self.assertEqual(contract.state, "RELEASED")
        self.assertEqual(contract.locks_to_release, [])

    def test_refused_run_without_locks_lists_nothing_to_release(self):
        contract = C.ExecutorContract(B)
        contract.start(None)
        self.assertEqual((contract.state, contract.locks_to_release), ("REFUSED", []))
        self.assertFalse(contract.release_locks({})["ok"])


class RegressionTests(unittest.TestCase):
    """Regressions for the gaps found in BK-106..108 and closed by Lead review."""

    def test_early_refusal_still_releases_receipted_locks(self):
        # If the executor already created both locks, a refusal for missing explicit write, incomplete approval or a
        # bad token must still list them for release; today state is REFUSED with an empty release list (lock leak).
        contract = planned(explicit=False)
        contract.acquire_locks(TOKEN, F.both_locks(), ALL)
        self.assertEqual((contract.state, contract.locks_to_release), ("RELEASE_REQUIRED", ALL))

    def test_bad_token_after_creation_receipts_still_requires_cleanup(self):
        contract = planned()
        malformed = "bad-token"
        observed = {path: F.lock(token=malformed) for path in ALL}
        result = contract.acquire_locks(malformed, observed, ALL)
        self.assertFalse(result["ok"])
        self.assertEqual((contract.state, contract.locks_to_release), ("RELEASE_REQUIRED", ALL))

    def test_receipted_lock_with_unreadable_record_is_released(self):
        # A lock this run created (receipt present) whose readback is garbled or missing must still be released (the
        # executor deletes only on a token match); today it is dropped from the release list (lock leak).
        contract = planned()
        observed = F.both_locks(); observed[ALL[1]] = "garbled"
        contract.acquire_locks(TOKEN, observed, ALL)
        self.assertEqual(contract.locks_to_release, ALL)

    def test_snapshots_are_copied_not_aliased(self):
        contract = locked()
        snapshot = F.snapshot()
        contract.verify_backup(snapshot, BACKUP)
        snapshot["file_sha256"] = "e" * 64
        snapshot["phases"][0]["phase_id"] = "Phase_9"
        self.assertEqual((contract.locked_snapshot["file_sha256"], contract.locked_snapshot["phases"][0]["phase_id"]), (BEFORE, "Phase_1"))

    def test_write_plan_must_match_the_reviewed_dry_run(self):
        # Same file hash but a locked snapshot reporting different current values: the executed writes would differ
        # from the diff the lead reviewed in the dry run. plan_write should refuse when (field, from, to) differ.
        contract = locked()
        locked_snapshot = F.snapshot()
        locked_snapshot["stats"]["max_health"] = 999.0
        contract.verify_backup(locked_snapshot, BACKUP)
        self.assertFalse(contract.plan_write()["ok"])

    def test_backup_path_must_be_a_string(self):
        contract = locked()
        self.assertFalse(contract.verify_backup(F.snapshot(), dict(BACKUP, path=["backup.uasset"]))["ok"])


if __name__ == "__main__":
    unittest.main()
