"""BK-191..195 (C, implementer; X-2042): regressions for the A-848 fail-open edges in the Sevarog repair planner,
executor contract and receipt validator, plus cross-module parity of the shared rules.

Synthetic inputs only (fixtures from the existing planner/contract/receipt test modules); no executor, lock, asset,
Unreal or filesystem effect. Non-write/read-only proposal behaviour and every existing gate are preserved; X-1991
still blocks authoring.
"""
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


PT = load("planner_fixtures_bk191", "test_plan_sevarog_definition_repair.py")
P = PT.P
CA = load("contract_adversarial_bk191", "test_sevarog_executor_contract_adversarial.py")  # has locked()
CT = CA.F  # contract fixtures (snapshot, BEFORE) used by CA.locked()
C = load("contract_bk191", "sevarog_executor_contract.py")
RF = load("receipt_fixtures_bk191", "test_validate_sevarog_executor_receipt.py")
V = RF.V
TOKEN = "0123456789abcdef0123456789abcdef"
SAFE = "Docs/BossCombatReview/Execution/Claude/backup/DA_Boss_Sevarog_Draft.before.uasset"


def write_plan(**ctx):
    return P.plan_repair(PT.envelope_result(), PT.snapshot(), PT.context(**ctx), PT.SOURCE)


class Bk191ReadbackExistsAndHash(unittest.TestCase):
    def setUp(self):
        self.plan = write_plan()
        self.assertTrue(self.plan["accepted"], self.plan["errors"])

    def test_good_readback_still_passes(self):
        self.assertTrue(P.verify_readback(self.plan, PT.saved_after(self.plan))["ok"])

    def test_missing_or_false_exists_is_refused(self):
        for value in (False, None, "true", 1):
            with self.subTest(exists=value):
                after = PT.saved_after(self.plan, exists=value)
                result = P.verify_readback(self.plan, after)
                self.assertFalse(result["ok"])
                self.assertIn("after-readback must show the saved asset exists (exists is True)", result["errors"])
                self.assertEqual(result["next"], "restore_backup_then_release_locks")
        after = PT.saved_after(self.plan); del after["exists"]
        self.assertFalse(P.verify_readback(self.plan, after)["ok"])

    def test_missing_or_malformed_after_hash_is_refused(self):
        for value in (None, "", "A" * 64, "a" * 63, 7, ["a" * 64]):
            with self.subTest(file_sha256=value):
                result = P.verify_readback(self.plan, PT.saved_after(self.plan, file_sha256=value))
                self.assertFalse(result["ok"])
                self.assertIn("after-readback needs the saved file's hash (64 lowercase hex)", result["errors"])


class Bk192CompleteUntouchedRows(unittest.TestCase):
    def setUp(self):
        self.plan = write_plan()

    def test_plan_records_a_deep_copy_of_untouched_rows(self):
        snap = PT.snapshot()
        plan = P.plan_repair(PT.envelope_result(), snap, PT.context(), PT.SOURCE)
        others = [p for p in snap["phases"] if p.get("phase_id") != P.PHASE_ID]
        self.assertEqual(plan["untouched_phase_snapshot"], others)
        others[0]["speed_multiplier"] = 99.0
        self.assertNotEqual(plan["untouched_phase_snapshot"], others, "the plan must copy, not alias, the rows")

    def test_changed_value_in_an_untouched_row_is_refused(self):
        after = PT.saved_after(self.plan)
        other = next(p for p in after["phases"] if p.get("phase_id") != P.PHASE_ID)
        other["speed_multiplier"] = (other.get("speed_multiplier") or 1.0) + 0.5  # same phase_id, different value
        result = P.verify_readback(self.plan, after)
        self.assertFalse(result["ok"])
        self.assertIn("other phase rows differ from the reviewed snapshot (complete rows are compared, not only phase_id)",
                      result["errors"])

    def test_plan_without_snapshot_fails_closed(self):
        plan = copy.deepcopy(self.plan); del plan["untouched_phase_snapshot"]
        self.assertFalse(P.verify_readback(plan, PT.saved_after(plan))["ok"])

    def test_contract_refuses_a_write_plan_whose_untouched_rows_differ_from_the_dry_run(self):
        contract = CA.locked()
        contract.reviewed_untouched_phase_snapshot = [{"phase_id": "Phase_2", "speed_multiplier": 123.0}]
        locked_snapshot = CT.snapshot()
        contract.verify_backup(locked_snapshot, {"path": SAFE, "sha256": CT.BEFORE})
        result = contract.plan_write()
        self.assertFalse(result["ok"])
        self.assertIn("write plan differs from the dry-run diff reviewed before lock acquisition", result["errors"][0])


class Bk193OwnerTokenContract(unittest.TestCase):
    def test_write_plan_token_must_be_32_lowercase_hex(self):
        for token in ("t0k3n", "tok", TOKEN.upper(), TOKEN[:-1], TOKEN + "0", " " + TOKEN[1:], "g" * 32):
            with self.subTest(token=token):
                plan = write_plan(locks={"root_held": True, "execution_held": True, "owner_token": token})
                self.assertFalse(plan["accepted"])
                self.assertIn("write owner token must be 32 lowercase hex (the executor lock-acquisition contract)", plan["errors"])
        self.assertTrue(write_plan(locks={"root_held": True, "execution_held": True, "owner_token": TOKEN})["accepted"])

    def test_dry_run_needs_no_token(self):
        plan = P.plan_repair(PT.envelope_result(), PT.snapshot(), PT.context(mode="dry_run", locks=None, backup=None,
                                                                             explicit_write=None), PT.SOURCE)
        self.assertTrue(plan["accepted"], plan["errors"])

    def test_token_rule_parity_with_executor_lock_acquisition(self):
        for token in (TOKEN, TOKEN.upper(), "t0k3n", "f" * 32, "f" * 31, "", "x" * 32):
            with self.subTest(token=token):
                self.assertEqual(P.OWNER_TOKEN.fullmatch(token) is not None, C.TOKEN.fullmatch(token) is not None)


class Bk194BackupPathContract(unittest.TestCase):
    PATHS = (SAFE, "Docs/BossCombatReview/Execution/x.uasset", "backup/DA.uasset", "C:/Temp/x.uasset",
             "Docs/BossCombatReview/Execution/../x.uasset", "Docs\\BossCombatReview\\Execution\\x.uasset",
             "Docs/BossCombatReview/Execution//x.uasset", "Docs/BossCombatReview/Execution/./x.uasset",
             "Docs/BossCombatReview/Execution/x\x00.uasset", "/Docs/BossCombatReview/Execution/x.uasset", "", None, 5)

    def test_three_modules_agree(self):
        for path in self.PATHS:
            with self.subTest(path=path):
                verdicts = {P.safe_backup_path(path), C._safe_backup_path(path), V._safe_backup_path(path)}
                self.assertEqual(len(verdicts), 1, path)
        self.assertEqual((P.BACKUP_PREFIX, C.BACKUP_PREFIX), (V.BACKUP_PREFIX, V.BACKUP_PREFIX))

    def test_planner_refuses_unsafe_backup_and_still_reports_hash_mismatch(self):
        plan = write_plan(backup={"path": "backup/x.uasset", "sha256": "d" * 64})
        self.assertIn("backup path must be a safe repo-relative path below Docs/BossCombatReview/Execution/", plan["errors"])
        self.assertIn("backup sha256 must equal the asset file's before-hash", plan["errors"])

    def test_contract_refuses_unsafe_backup_path(self):
        for path in ("backup/x.uasset", "C:/x.uasset", "Docs/BossCombatReview/Execution/../x.uasset"):
            with self.subTest(path=path):
                contract = CA.locked()
                result = contract.verify_backup(CT.snapshot(), {"path": path, "sha256": CT.BEFORE})
                self.assertFalse(result["ok"])
                self.assertIn("backup path must be a safe repo-relative path", result["errors"][0])


class Bk195RefusalLockOrder(unittest.TestCase):
    def refusal(self, created):
        r = RF.receipt("REFUSED_AFTER_LOCKS")
        r["locks"] = [RF.lock(p) if made else {"path": p, "token": None, "created": False, "readback_token": None,
                                                "party": None, "policy": None, "release_attempted": False,
                                                "release_token_match": False, "released": False}
                      for p, made in zip(V.LOCK_PATHS, created)]
        return r

    def test_execution_lock_without_root_is_refused(self):
        verdict = V.validate_receipt(self.refusal((False, True)))
        self.assertFalse(verdict["valid"])
        self.assertIn("partial lock acquisition must have created the root lock first (execution lock without root)",
                      verdict["errors"])

    def test_root_only_partial_is_still_valid(self):
        self.assertTrue(V.validate_receipt(self.refusal((True, False)))["valid"])

    def test_parity_with_v2_proposal_lock_order(self):
        v2 = load("v2_bk191", "sevarog_receipt_v2_proposal.py")
        self.assertEqual(v2.LOCK_PATHS, V.LOCK_PATHS)
        self.assertEqual(V.LOCK_PATHS[0], "ENGINE_LOCK.json")  # root first, as the runner and v2 create_order require


if __name__ == "__main__":
    unittest.main()
