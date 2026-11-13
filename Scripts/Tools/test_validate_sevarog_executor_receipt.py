"""BK-113..114: synthetic fixtures for the future executor receipt validator."""
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("validate_sevarog_executor_receipt", HERE / "validate_sevarog_executor_receipt.py")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)
BEFORE, AFTER, PLAN, REPLY = "a" * 64, "b" * 64, "c" * 64, "d" * 64
TOKEN = "0123456789abcdef0123456789abcdef"


def source():
    return {"message_id": "O-77", "sender": "Owner", "path": V.MAILBOX_PATH, "sha256": REPLY}


def lock(path, released=True, release_match=True):
    return {"path": path, "token": TOKEN, "created": True, "readback_token": TOKEN, "party": "X", "policy": "C-1155",
            "release_attempted": True, "release_token_match": release_match, "released": released}


def receipt(outcome="DRY_RUN_ONLY"):
    base = {"schema": V.SCHEMA, "outcome": outcome,
            "source": source(), "plan_sha256": PLAN,
            "asset": {"path": V.ASSET_PATH, "before_sha256": None, "backup_path": None, "backup_sha256": None,
                      "after_sha256": None, "restored_sha256": None},
            "locks": [{"path": p, "token": None, "created": False, "readback_token": None, "party": None,
                       "policy": None, "release_attempted": False, "release_token_match": False, "released": False}
                      for p in V.LOCK_PATHS],
            "steps": list(V.DRY_STEPS)}
    if outcome == "DRY_RUN_ONLY":
        return base
    base.update(source=source(), locks=[lock(p) for p in V.LOCK_PATHS])
    base["asset"].update(before_sha256=BEFORE,
                          backup_path="Docs/BossCombatReview/Execution/Codex/Run_synthetic/asset.uasset",
                          backup_sha256=BEFORE, after_sha256=AFTER)
    if outcome == "WRITTEN_AND_VERIFIED":
        base["steps"] = list(V.WRITE_STEPS)
    elif outcome == "FAILED_RESTORED":
        base["asset"]["restored_sha256"] = BEFORE
        base["steps"] = list(V.RESTORED_STEPS)
    elif outcome == "LOCK_RETAINED_NEEDS_OPERATOR":
        base["locks"][1] = lock(V.LOCK_PATHS[1], released=False, release_match=False)
        base["steps"] = list(V.RETAINED_STEPS)
    elif outcome == "FAILED_RESTORE_NEEDS_OPERATOR":
        base["asset"]["restored_sha256"] = "e" * 64
        base["steps"] = list(V.RESTORE_FAILED_STEPS)
    elif outcome == "REFUSED_AFTER_LOCKS":
        base["locks"][1] = {"path": V.LOCK_PATHS[1], "token": None, "created": False, "readback_token": None,
                            "party": None, "policy": None, "release_attempted": False,
                            "release_token_match": False, "released": False}
        base["asset"].update(before_sha256=BEFORE, backup_path=None, backup_sha256=None, after_sha256=None)
        base["steps"] = list(V.REFUSED_STEPS[0])
    return base


class ReceiptTests(unittest.TestCase):
    def valid(self, case):
        result = V.validate_receipt(case)
        self.assertTrue(result["valid"], result["errors"])

    def invalid(self, case, message):
        result = V.validate_receipt(case)
        self.assertFalse(result["valid"])
        self.assertTrue(any(message in error for error in result["errors"]), result["errors"])

    def test_valid_dry_run_has_no_write_claims(self):
        self.valid(receipt())

    def test_valid_verified_write_binds_source_backup_locks_and_readback(self):
        self.valid(receipt("WRITTEN_AND_VERIFIED"))

    def test_valid_restored_failure_and_retained_lock_outcomes(self):
        self.valid(receipt("FAILED_RESTORED"))
        self.valid(receipt("FAILED_RESTORE_NEEDS_OPERATOR"))
        self.valid(receipt("LOCK_RETAINED_NEEDS_OPERATOR"))
        self.valid(receipt("REFUSED_AFTER_LOCKS"))

    def test_unknown_or_missing_keys_fail_closed(self):
        case = receipt(); case["unexpected"] = True
        self.invalid(case, "receipt keys")
        case = receipt(); del case["plan_sha256"]
        self.invalid(case, "receipt keys")

    def test_unhashable_outcome_is_refused_without_exception(self):
        case = receipt(); case["outcome"] = []
        self.invalid(case, "outcome is not supported")

    def test_hash_and_source_tampering_fail(self):
        case = receipt("WRITTEN_AND_VERIFIED"); case["source"]["sha256"] = "x" * 64
        self.invalid(case, "source.sha256")
        case = receipt("WRITTEN_AND_VERIFIED"); case["asset"]["backup_sha256"] = AFTER
        self.invalid(case, "backup_sha256")

    def test_lock_duplicates_wrong_token_and_bad_release_flags_fail(self):
        case = receipt("WRITTEN_AND_VERIFIED"); case["locks"][1] = dict(case["locks"][0])
        self.invalid(case, "canonical paths")
        case = receipt("WRITTEN_AND_VERIFIED"); case["locks"][0]["readback_token"] = "e" * 32
        self.invalid(case, "readback token")
        case = receipt("WRITTEN_AND_VERIFIED"); case["locks"][0]["released"] = False
        self.invalid(case, "requires both locks released")
        case = receipt("WRITTEN_AND_VERIFIED"); case["locks"][0]["token"] = case["locks"][0]["readback_token"] = "f" * 32
        self.invalid(case, "share one C-1155 run token")
        case = receipt("WRITTEN_AND_VERIFIED"); case["locks"][1]["party"] = "C"
        self.invalid(case, "belong to one party")
        case = receipt("LOCK_RETAINED_NEEDS_OPERATOR"); case["locks"][0]["release_attempted"] = False
        self.invalid(case, "released lock requires an attempted release")

    def test_reordered_or_duplicate_steps_fail(self):
        case = receipt("WRITTEN_AND_VERIFIED"); case["steps"][2:4] = reversed(case["steps"][2:4])
        self.invalid(case, "ordered sequence")
        case = receipt(); case["steps"].append("dry_run")
        self.invalid(case, "ordered sequence")

    def test_outcome_data_mismatches_fail(self):
        case = receipt("FAILED_RESTORED"); case["asset"]["restored_sha256"] = AFTER
        self.invalid(case, "restored_sha256 to equal")
        case = receipt("FAILED_RESTORED"); case["asset"]["after_sha256"] = BEFORE
        self.invalid(case, "post-save asset hash")
        case = receipt("LOCK_RETAINED_NEEDS_OPERATOR"); case["locks"] = [lock(p) for p in V.LOCK_PATHS]
        self.invalid(case, "at least one retained lock")
        case = receipt("FAILED_RESTORE_NEEDS_OPERATOR"); case["asset"]["restored_sha256"] = BEFORE
        self.invalid(case, "mismatched restored hash")

    def test_backup_path_and_dry_source_are_bound(self):
        for path in ("C:/x.uasset", "../../x.uasset", "/tmp/x.uasset", "\\\\server\\share\\x.uasset",
                     "Docs/BossCombatReview/Execution/../x.uasset"):
            case = receipt("WRITTEN_AND_VERIFIED"); case["asset"]["backup_path"] = path
            self.invalid(case, "safe repo-relative path")
        case = receipt(); case["source"] = {"message_id": None, "sender": None, "path": None, "sha256": None}
        self.invalid(case, "source.sender must be Owner")

    def test_refusal_with_non_list_locks_fails_without_exception(self):
        for value in (None, 3, "locks"):
            case = receipt("REFUSED_AFTER_LOCKS"); case["locks"] = value
            result = V.validate_receipt(case)
            self.assertFalse(result["valid"])
            self.assertTrue(any("locks must contain exactly two" in error for error in result["errors"]))

    def test_refusal_receipts_follow_their_stage_and_preserve_backup_evidence(self):
        for steps in V.REFUSED_STEPS:
            case = receipt("REFUSED_AFTER_LOCKS")
            if steps != V.REFUSED_STEPS[0]:
                case["locks"] = [lock(p) for p in V.LOCK_PATHS]
            case["steps"] = list(steps)
            if "backup_verified" in steps:
                case["asset"].update(backup_path="Docs/BossCombatReview/Execution/Codex/Run_synthetic/asset.uasset",
                                     backup_sha256=BEFORE)
            self.valid(case)
        case = receipt("REFUSED_AFTER_LOCKS"); case["steps"] = list(V.REFUSED_STEPS[3])
        case["asset"].update(backup_path="../../escape.uasset", backup_sha256=BEFORE)
        self.invalid(case, "safe backup matching before_sha256")

    def test_validator_has_no_filesystem_or_process_access(self):
        source_text = (HERE / "validate_sevarog_executor_receipt.py").read_text(encoding="utf-8")
        for forbidden in ("import unreal", "open(", "read_text", "write_text", "subprocess", "Path(", "unlink("):
            self.assertNotIn(forbidden, source_text)


if __name__ == "__main__":
    unittest.main()
