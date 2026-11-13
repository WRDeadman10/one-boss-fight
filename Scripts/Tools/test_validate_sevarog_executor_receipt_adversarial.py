"""BK-116..119 (C, implementer; X-2009/X-2010): adversarial audit of validate_sevarog_executor_receipt.py.

New file; the validator is not modified in this batch. Defenses that hold are ordinary tests. Confirmed gaps are pinned
as regression tests, each with a precise rule in its docstring, for the lead's hotfix cycle. Synthetic receipts
only (fixtures from the existing receipt test module); no files, Unreal, assets or locks. Receipt validity is not
runtime proof or write authorization.
"""
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("receipt_fixtures", HERE / "test_validate_sevarog_executor_receipt.py")
F = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(F)
V = F.V


def valid(receipt):
    return V.validate_receipt(receipt)["valid"]


class HeldDefenses(unittest.TestCase):
    def test_unhashable_and_malformed_top_level_values_are_invalid_not_exceptions(self):
        # X-2010/X-2011 case kept here: an unhashable outcome returns invalid instead of raising TypeError.
        for key, value in (("outcome", []), ("outcome", {}), ("schema", []), ("steps", {}), ("steps", None),
                           ("source", "O-77"), ("locks", "both"), ("asset", [])):
            with self.subTest(key=key, value=value):
                receipt = F.receipt("WRITTEN_AND_VERIFIED")
                receipt[key] = value
                self.assertFalse(valid(receipt))

    def test_malformed_nested_records_are_invalid(self):
        cases = []
        r = F.receipt("WRITTEN_AND_VERIFIED"); r["locks"] = [r["locks"][0], "x"]; cases.append(("lock record string", r))
        r = F.receipt("WRITTEN_AND_VERIFIED"); r["locks"][0]["path"] = ["x"]; cases.append(("unhashable lock path", r))
        r = F.receipt("WRITTEN_AND_VERIFIED"); r["locks"] = r["locks"][::-1]; cases.append(("lock paths reversed", r))
        r = F.receipt("WRITTEN_AND_VERIFIED"); r["locks"] = r["locks"][:1]; cases.append(("one lock", r))
        r = F.receipt("WRITTEN_AND_VERIFIED"); r["locks"][0]["extra"] = 1; cases.append(("extra lock key", r))
        r = F.receipt("WRITTEN_AND_VERIFIED"); del r["asset"]["after_sha256"]; cases.append(("missing asset key", r))
        r = F.receipt("WRITTEN_AND_VERIFIED"); r["source"]["sha256"] = r["source"]["sha256"].upper(); cases.append(("uppercase source hash", r))
        for label, receipt in cases:
            with self.subTest(label):
                self.assertFalse(valid(receipt))

    def test_boolean_and_token_type_edges_are_invalid(self):
        for key, value in (("created", 1), ("released", 1), ("release_attempted", "yes"), ("token", True), ("token", 32 * "G")):
            with self.subTest(key=key, value=value):
                receipt = F.receipt("WRITTEN_AND_VERIFIED")
                receipt["locks"][0][key] = value
                if key == "token":
                    receipt["locks"][0]["readback_token"] = value
                self.assertFalse(valid(receipt))

    def test_impossible_or_missing_hashes_per_outcome_are_invalid(self):
        cases = []
        r = F.receipt("WRITTEN_AND_VERIFIED"); r["asset"]["after_sha256"] = r["asset"]["before_sha256"]; cases.append(("after equals before", r))
        r = F.receipt("WRITTEN_AND_VERIFIED"); r["asset"]["backup_sha256"] = "c" * 64; cases.append(("backup differs", r))
        r = F.receipt("WRITTEN_AND_VERIFIED"); r["asset"]["restored_sha256"] = r["asset"]["before_sha256"]; cases.append(("restore claim on success", r))
        r = F.receipt("FAILED_RESTORED"); r["asset"]["restored_sha256"] = None; cases.append(("restored missing", r))
        r = F.receipt("FAILED_RESTORED"); r["asset"]["restored_sha256"] = "d" * 64; cases.append(("restored wrong", r))
        r = F.receipt("WRITTEN_AND_VERIFIED"); r["plan_sha256"] = None; cases.append(("plan hash missing", r))
        r = F.receipt("LOCK_RETAINED_NEEDS_OPERATOR"); r["locks"][1] = F.lock(V.LOCK_PATHS[1]); cases.append(("retained but all released", r))
        r = F.receipt("WRITTEN_AND_VERIFIED"); r["locks"][1] = F.lock(V.LOCK_PATHS[1], released=False, release_match=False); cases.append(("success with a retained lock", r))
        r = F.receipt("WRITTEN_AND_VERIFIED"); r["locks"][0]["readback_token"] = "e" * 32; cases.append(("readback token mismatch", r))
        r = F.receipt("WRITTEN_AND_VERIFIED"); r["locks"][0]["release_token_match"] = True; r["locks"][0]["released"] = False; cases.append(("matched but not released", r))
        r = F.receipt("WRITTEN_AND_VERIFIED"); r["source"] = {"message_id": None, "sender": None, "path": None, "sha256": None}; cases.append(("write without source", r))
        r = F.receipt("WRITTEN_AND_VERIFIED"); r["source"]["message_id"] = "X-1991"; cases.append(("agent source id", r))
        for label, receipt in cases:
            with self.subTest(label):
                self.assertFalse(valid(receipt))

    def test_reordered_duplicated_or_cross_outcome_steps_are_invalid(self):
        cases = []
        r = F.receipt("WRITTEN_AND_VERIFIED"); r["steps"] = r["steps"] + ["locks_released"]; cases.append(("duplicated", r))
        r = F.receipt("WRITTEN_AND_VERIFIED"); s = r["steps"]; s[2], s[3] = s[3], s[2]; cases.append(("reordered", r))
        r = F.receipt("WRITTEN_AND_VERIFIED"); r["steps"] = list(V.RESTORED_STEPS); cases.append(("restored steps on success", r))
        r = F.receipt("WRITTEN_AND_VERIFIED"); r["steps"] = r["steps"][:-1]; cases.append(("missing release step", r))
        r = F.receipt("WRITTEN_AND_VERIFIED"); r["steps"][0] = 7; cases.append(("non-string step", r))
        for label, receipt in cases:
            with self.subTest(label):
                self.assertFalse(valid(receipt))

    def test_dry_run_cannot_claim_writes_or_locks(self):
        cases = []
        r = F.receipt(); r["asset"]["after_sha256"] = "b" * 64; cases.append(("after hash", r))
        r = F.receipt(); r["asset"]["backup_path"] = "b.uasset"; cases.append(("backup path", r))
        r = F.receipt(); r["locks"][0]["created"] = True; cases.append(("created lock", r))
        r = F.receipt(); r["locks"][1]["token"] = "0" * 32; cases.append(("lock token", r))
        r = F.receipt(); r["steps"] = list(V.WRITE_STEPS); cases.append(("write steps", r))
        for label, receipt in cases:
            with self.subTest(label):
                self.assertFalse(valid(receipt))


class HotfixRegressions(unittest.TestCase):
    """Findings from C-1316; each former gap must now be rejected or represented by a valid receipt form."""

    def test_gap_g1_both_locks_must_share_one_token(self):
        """G1: C-1155 takes both locks under ONE owner token (runner :17-58, contract acquire_locks); _locks checks each
        record's token shape and create/readback match but never that the two records carry the same token."""
        receipt = F.receipt("WRITTEN_AND_VERIFIED")
        receipt["locks"][1]["token"] = receipt["locks"][1]["readback_token"] = "f" * 32
        self.assertFalse(valid(receipt))

    def test_gap_g2_both_locks_must_share_one_party(self):
        """G2: one run is one party; _locks accepts any of X/C/A per record independently, so X + C passes."""
        receipt = F.receipt("WRITTEN_AND_VERIFIED")
        receipt["locks"][1]["party"] = "C"
        self.assertFalse(valid(receipt))

    def test_gap_g3_released_lock_needs_a_release_attempt(self):
        """G3: under LOCK_RETAINED_NEEDS_OPERATOR a lock may be released=True, release_token_match=True with
        release_attempted=False - released without an attempt is impossible; only the success outcomes require all three."""
        receipt = F.receipt("LOCK_RETAINED_NEEDS_OPERATOR")
        receipt["locks"][0]["release_attempted"] = False
        self.assertFalse(valid(receipt))

    def test_gap_g4_backup_path_must_be_repo_relative(self):
        """G4: asset.backup_path only needs to be a non-empty string; absolute (C:/...) and traversal (../..) paths pass.
        The backup must live under the run's repo-relative evidence folder."""
        for bad in ("C:/x.uasset", "../../x.uasset", "/tmp/x.uasset", "\\\\server\\share\\x.uasset"):
            receipt = F.receipt("WRITTEN_AND_VERIFIED")
            receipt["asset"]["backup_path"] = bad
            self.assertFalse(valid(receipt), bad)

    def test_gap_g5_every_contract_outcome_has_a_receipt_form(self):
        """G5: sevarog_executor_contract.py ends runs as REFUSED_AFTER_LOCKS and FAILED_RESTORE_NEEDS_OPERATOR too, but
        OUTCOMES has no form for them, so those runs - the ones an operator most needs evidence for - cannot produce a
        valid receipt. Schema extension needed (with their own ordered step lists)."""
        self.assertTrue({"REFUSED_AFTER_LOCKS", "FAILED_RESTORE_NEEDS_OPERATOR"} <= V.OUTCOMES)
        self.assertTrue(valid(F.receipt("REFUSED_AFTER_LOCKS")))
        self.assertTrue(valid(F.receipt("FAILED_RESTORE_NEEDS_OPERATOR")))

    def test_gap_g6_dry_run_that_claims_a_mailbox_read_needs_the_bound_source(self):
        """G6: DRY_STEPS begins with mailbox_read and the executor binds the owner message before the dry run (BK-104),
        yet a DRY_RUN_ONLY receipt with an all-null source is accepted; the step claims evidence the receipt omits."""
        receipt = F.receipt("DRY_RUN_ONLY")
        receipt["source"] = {"message_id": None, "sender": None, "path": None, "sha256": None}
        self.assertFalse(valid(receipt))


if __name__ == "__main__":
    unittest.main()
