"""X-2047 / A-850 hotfix regressions (C, implementer) for the PROPOSED v2 receipt (sevarog_receipt_v2_proposal.py).

(1) artifacts[].sha256 is type-checked before comparison: JSON null and the string "None" are no longer equal.
(2) A CREATED backup with no cleanup attempt cannot be observed absent (it would report kept_evidence for a vanished
    copy); an absent readback after a FAILED copy stays valid.
Synthetic receipts only (fixtures from test_sevarog_receipt_v2_proposal.py); proposal-only; X-1991 remains open.
"""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("v2_fixtures_a850", HERE / "test_sevarog_receipt_v2_proposal.py")
T = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(T)
P = T.P


def errors(receipt):
    return P.validate_v2(receipt)["errors"]


class ArtifactHashTyping(unittest.TestCase):
    """abandoned_after_save expects one asset_needs_operator artifact whose sha256 is null (unknown current state)."""

    def base(self):
        r = T.scenario("abandoned_after_save")
        self.assertEqual(r["artifacts"], [{"kind": "asset_needs_operator", "path": P.ASSET_PATH, "sha256": None}])
        return r

    def test_null_hash_still_matches(self):
        self.assertEqual(errors(self.base()), [])

    def test_string_none_no_longer_matches_null(self):
        for spoof in ("None", "null", "", "none"):
            with self.subTest(spoof=spoof):
                r = self.base()
                r["artifacts"][0]["sha256"] = spoof
                self.assertFalse(P.validate_v2(r)["valid"])

    def test_string_none_survives_json_round_trip_as_a_string_and_is_refused(self):
        text = json.dumps(self.base()).replace('"sha256": null', '"sha256": "None"')
        self.assertIn('"sha256": "None"', text)
        self.assertFalse(P.validate_v2(json.loads(text))["valid"])

    def test_wrong_kinds_paths_and_hash_types_are_refused(self):
        for key, value in (("kind", "LOCK"), ("kind", 1), ("kind", None), ("path", None), ("path", 5),
                           ("sha256", 0), ("sha256", "A" * 64), ("sha256", "a" * 63), ("sha256", False), ("sha256", ["x"])):
            with self.subTest(key=key, value=value):
                r = self.base()
                r["artifacts"][0][key] = value
                self.assertFalse(P.validate_v2(r)["valid"])

    def test_real_hash_artifact_still_compares_exactly(self):
        r = T.scenario("backup_mismatch_retained")
        self.assertEqual(errors(r), [])
        r["artifacts"][0]["sha256"] = "f" * 64
        self.assertIn("artifacts must list exactly the derived operator leftovers", errors(r))

    def test_key_orders_null_and_hashes_without_coercion(self):
        a = {"kind": "backup", "path": "x", "sha256": None}
        b = {"kind": "backup", "path": "x", "sha256": "a" * 64}
        self.assertNotEqual(P._key(a), P._key(b))
        self.assertEqual(sorted([P._key(b), P._key(a)]), [P._key(a), P._key(b)])


class BackupStateConsistency(unittest.TestCase):
    def test_created_copy_observed_absent_without_cleanup_is_refused(self):
        record = T.copy_record(observed=T.BAD, result="created", cleanup=False, readback="absent", final="kept_evidence")
        r = T.scenario("backup_mismatch_retained", backup=record)
        self.assertIn("a created backup observed absent without a cleanup attempt is inconsistent", errors(r))

    def test_failed_copy_observed_absent_stays_valid(self):
        record = T.copy_record(observed=None, result="failed", cleanup=False, readback="absent")
        self.assertEqual(record["final_state"], "none")
        self.assertEqual(errors(T.scenario("backup_mismatch_retained", backup=record)), [])

    def test_created_copy_removed_after_cleanup_stays_valid(self):
        record = T.copy_record(observed=T.BAD, result="created", cleanup=True, readback="absent")
        self.assertEqual(record["final_state"], "removed")
        self.assertEqual(errors(T.scenario("backup_mismatch_retained", backup=record)), [])

    def test_created_copy_kept_without_readback_stays_valid(self):
        record = T.copy_record(observed=T.BAD, result="created", cleanup=False, readback="not_observed")
        self.assertEqual(record["final_state"], "kept_evidence")
        self.assertEqual(errors(T.scenario("backup_mismatch_retained", backup=record)), [])

    def test_inconsistent_state_refused_for_every_claimed_final_state(self):
        for final in P.FINAL_STATES:
            with self.subTest(final=final):
                record = T.copy_record(observed=T.BAD, result="created", cleanup=False, readback="absent", final=final)
                self.assertFalse(P.validate_v2(T.scenario("backup_mismatch_retained", backup=copy.deepcopy(record)))["valid"])


if __name__ == "__main__":
    unittest.main()
