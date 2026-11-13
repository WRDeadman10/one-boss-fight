"""BK-126..129 (C, implementer; X-2014): adversarial tests for refusal/restore receipts and the receipt-source adapter.

New file; validate_sevarog_executor_receipt.py, bind_receipt_source.py, the binder, executor contract, author and
runner are not modified. Defenses that hold are ordinary tests. Gaps R1-R4 (C-1320) were fixed by the lead in X-2016
and are now regressions, with R5 added. Synthetic inputs only; no file, Unreal,
asset, lock or process access beyond test discovery. Receipt validity is not runtime proof or write authorization;
X-1991 is still open.
"""
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, HERE / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


F = load("receipt_fixtures_bk126", "test_validate_sevarog_executor_receipt.py")
V = F.V
S = load("bind_receipt_source_bk126", "bind_receipt_source.py")
B = load("bind_owner_approval_bk126", "bind_owner_approval.py")
BEFORE, AFTER = F.BEFORE, F.AFTER
BACKUP = "Docs/BossCombatReview/Execution/Codex/Run_synthetic/asset.uasset"
PARTIAL, VERIFIED, BACKUP_REFUSED, PLAN_REFUSED = V.REFUSED_STEPS


def not_created(path):
    return {"path": path, "token": None, "created": False, "readback_token": None, "party": None, "policy": None,
            "release_attempted": False, "release_token_match": False, "released": False}


def refusal(steps=PARTIAL, created=(True, False), before=BEFORE, backup_path=None, backup_sha=None):
    r = F.receipt("REFUSED_AFTER_LOCKS")
    r["steps"] = list(steps)
    r["locks"] = [F.lock(p) if made else not_created(p) for p, made in zip(V.LOCK_PATHS, created)]
    r["asset"].update(before_sha256=before, backup_path=backup_path, backup_sha256=backup_sha)
    return r


def errors(receipt):
    return V.validate_receipt(receipt)["errors"]


class Bk126PartialLockStep(unittest.TestCase):
    """BK-126: the partial-acquisition refusal must show exactly the one lock this run created, released."""

    def test_partial_step_accepts_exactly_one_created_released_lock(self):
        # X-2042/BK-195: acquisition is root first, so only the root lock may be the single created lock.
        self.assertEqual(errors(refusal(created=(True, False))), [])
        self.assertIn("partial lock acquisition must have created the root lock first (execution lock without root)",
                      errors(refusal(created=(False, True))))

    def test_partial_step_refuses_two_or_zero_created_locks(self):
        self.assertIn("partial lock acquisition refusal requires exactly one created lock", errors(refusal(created=(True, True))))
        self.assertIn("REFUSED_AFTER_LOCKS requires at least one lock created by this run", errors(refusal(created=(False, False))))

    def test_post_acquisition_steps_refuse_a_single_created_lock(self):
        for steps in (VERIFIED, BACKUP_REFUSED):
            with self.subTest(steps=steps[-2]):
                self.assertIn("post-acquisition refusal requires both locks created", errors(refusal(steps=steps)))
                self.assertEqual(errors(refusal(steps=steps, created=(True, True))), [])

    def test_created_lock_release_claim_mutations_are_refused(self):
        mutations = {
            "not attempted": dict(release_attempted=False),
            "token mismatch": dict(release_token_match=False, released=False),
            "kept": dict(released=False),
            "released without match": dict(release_token_match=False),
            "readback differs": dict(readback_token="f" * 32),
            "foreign policy": dict(policy="C-9999"),
            "unknown party": dict(party="Z"),
            "non-bool flag": dict(released="yes"),
        }
        for label, change in mutations.items():
            with self.subTest(label):
                r = refusal()
                r["locks"][0].update(change)
                self.assertNotEqual(errors(r), [])

    def test_uncreated_lock_cannot_claim_lock_or_release_data(self):
        for key, value in (("token", F.TOKEN), ("readback_token", F.TOKEN), ("party", "X"), ("policy", "C-1155"),
                           ("release_attempted", True), ("release_token_match", True), ("released", True), ("created", None)):
            with self.subTest(key=key):
                r = refusal()
                r["locks"][1][key] = value
                self.assertNotEqual(errors(r), [])

    def test_two_created_refusal_locks_share_token_and_party(self):
        r = refusal(steps=VERIFIED, created=(True, True))
        r["locks"][1]["token"] = r["locks"][1]["readback_token"] = "f" * 32
        self.assertIn("created refusal locks must share one run token", errors(r))
        r = refusal(steps=VERIFIED, created=(True, True))
        r["locks"][1]["party"] = "C"
        self.assertIn("created refusal locks must belong to one party", errors(r))


class Bk127RefusalStageAsset(unittest.TestCase):
    """BK-127: before/backup evidence must match what each refusal stage could have produced."""

    def test_before_backup_stages_accept_null_or_hex_before_and_no_backup(self):
        for steps in (PARTIAL, VERIFIED, BACKUP_REFUSED):
            created = (True, False) if steps is PARTIAL else (True, True)
            for before in (None, BEFORE):
                with self.subTest(stage=steps[-2], before=before):
                    self.assertEqual(errors(refusal(steps=steps, created=created, before=before)), [])

    def test_before_backup_stages_refuse_backup_claims(self):
        for steps in (PARTIAL, VERIFIED, BACKUP_REFUSED):
            created = (True, False) if steps is PARTIAL else (True, True)
            for path, sha in ((BACKUP, None), (None, BEFORE), (BACKUP, BEFORE)):
                with self.subTest(stage=steps[-2], path=path, sha=sha):
                    self.assertIn("REFUSED_AFTER_LOCKS cannot claim backup data before backup_verified",
                                  errors(refusal(steps=steps, created=created, backup_path=path, backup_sha=sha)))

    def test_malformed_before_hash_is_refused_at_every_stage(self):
        for steps in V.REFUSED_STEPS:
            created = (True, False) if steps is PARTIAL else (True, True)
            for bad in ("A" * 64, "a" * 63, 7, ["a" * 64]):
                with self.subTest(stage=steps[-2], bad=bad):
                    r = refusal(steps=steps, created=created, before=bad,
                                backup_path=BACKUP if steps is PLAN_REFUSED else None,
                                backup_sha=bad if steps is PLAN_REFUSED else None)
                    self.assertNotEqual(errors(r), [])

    def test_write_plan_refusal_requires_the_verified_backup(self):
        ok = refusal(steps=PLAN_REFUSED, created=(True, True), backup_path=BACKUP, backup_sha=BEFORE)
        self.assertEqual(errors(ok), [])
        for label, kwargs in (("no before", dict(before=None)), ("no path", dict(backup_path=None)),
                              ("no backup hash", dict(backup_sha=None)), ("hash differs", dict(backup_sha="e" * 64)),
                              ("absolute path", dict(backup_path="C:/x.uasset")),
                              ("traversal", dict(backup_path="Docs/BossCombatReview/Execution/../x.uasset")),
                              ("outside evidence tree", dict(backup_path="Content/x.uasset"))):
            with self.subTest(label):
                args = dict(steps=PLAN_REFUSED, created=(True, True), backup_path=BACKUP, backup_sha=BEFORE)
                args.update(kwargs)
                self.assertIn("REFUSED_AFTER_LOCKS after backup verification requires a safe backup matching before_sha256",
                              errors(refusal(**args)))

    def test_no_refusal_stage_may_claim_save_readback_or_restore(self):
        for steps in V.REFUSED_STEPS:
            created = (True, False) if steps is PARTIAL else (True, True)
            for key in ("after_sha256", "restored_sha256"):
                with self.subTest(stage=steps[-2], key=key):
                    r = refusal(steps=steps, created=created, backup_path=BACKUP if steps is PLAN_REFUSED else None,
                                backup_sha=BEFORE if steps is PLAN_REFUSED else None)
                    r["asset"][key] = AFTER
                    self.assertIn("REFUSED_AFTER_LOCKS cannot claim a save, readback, or restore", errors(r))

    def test_refusal_steps_cannot_be_mixed_or_extended(self):
        for label, steps in (("partial + verified", PARTIAL[:4] + ("locks_verified",) + PARTIAL[4:]),
                             ("write step appended", PLAN_REFUSED[:-1] + ("save", "locks_released")),
                             ("missing release", VERIFIED[:-1]), ("dry steps", V.DRY_STEPS)):
            with self.subTest(label):
                self.assertIn("steps do not match the required ordered sequence for REFUSED_AFTER_LOCKS",
                              errors(refusal(steps=steps, created=(True, True))))


class Bk128RestoreFailure(unittest.TestCase):
    """BK-128: restore-failed outcomes need a valid, mismatched restore hash and the right lock state."""

    def retained_restore(self):
        r = F.receipt("LOCK_RETAINED_NEEDS_OPERATOR")
        r["steps"] = list(V.RETAINED_RESTORE_STEPS)
        r["asset"]["restored_sha256"] = "e" * 64
        return r

    def test_valid_forms(self):
        self.assertEqual(errors(F.receipt("FAILED_RESTORE_NEEDS_OPERATOR")), [])
        self.assertEqual(errors(self.retained_restore()), [])
        r = F.receipt("FAILED_RESTORE_NEEDS_OPERATOR"); r["asset"]["restored_sha256"] = AFTER  # restore left the bad save
        self.assertEqual(errors(r), [])

    def test_restore_hash_matching_before_missing_or_malformed_is_refused(self):
        for make, needle in ((lambda: F.receipt("FAILED_RESTORE_NEEDS_OPERATOR"), "FAILED_RESTORE_NEEDS_OPERATOR requires a valid mismatched restored hash"),
                             (self.retained_restore, "retained-lock restore failure requires a valid mismatched restored hash")):
            for bad in (BEFORE, None, "E" * 64, 5):
                with self.subTest(needle=needle[:20], bad=bad):
                    r = make(); r["asset"]["restored_sha256"] = bad
                    self.assertIn(needle, errors(r))

    def test_retained_without_restore_steps_cannot_claim_a_restore_hash(self):
        r = F.receipt("LOCK_RETAINED_NEEDS_OPERATOR"); r["asset"]["restored_sha256"] = "e" * 64
        self.assertIn("restored_sha256 is only valid for a restore outcome", errors(r))

    def test_restore_failed_outcome_requires_both_locks_released(self):
        for index in (0, 1):
            with self.subTest(index=index):
                r = F.receipt("FAILED_RESTORE_NEEDS_OPERATOR")
                r["locks"][index] = F.lock(V.LOCK_PATHS[index], released=False, release_match=False)
                self.assertIn("FAILED_RESTORE_NEEDS_OPERATOR requires both locks released after token match", errors(r))

    def test_retained_restore_lock_mutations(self):
        r = self.retained_restore(); r["locks"][1] = F.lock(V.LOCK_PATHS[1])
        self.assertIn("operator-required outcome needs at least one retained lock", errors(r))
        r = self.retained_restore(); r["locks"][1]["release_attempted"] = False
        self.assertIn("retained lock must record a release attempt", errors(r))
        r = self.retained_restore(); r["locks"][1]["release_token_match"] = True
        self.assertIn("a lock with a matching release token must be marked released", errors(r))
        r = self.retained_restore(); r["locks"][0]["release_attempted"] = False
        self.assertIn("a released lock requires an attempted release with a matching token", errors(r))
        r = self.retained_restore(); r["asset"]["after_sha256"] = BEFORE
        self.assertIn("post-save asset hash must differ from before_sha256", errors(r))

    def test_restore_steps_cannot_cross_outcomes(self):
        r = F.receipt("FAILED_RESTORE_NEEDS_OPERATOR"); r["steps"] = list(V.RETAINED_RESTORE_STEPS)
        self.assertNotEqual(errors(r), [])
        r = self.retained_restore(); r["steps"] = list(V.RESTORE_FAILED_STEPS)
        self.assertNotEqual(errors(r), [])
        r = F.receipt("FAILED_RESTORED"); r["steps"] = list(V.RESTORE_FAILED_STEPS)
        self.assertNotEqual(errors(r), [])


BODY = "Health 1500 yes."
RAW = "### [O-77] Owner -> Codex, 2026-11-12 09:00\n%s\n### [X-2015] Codex -> Claude\nack\n" % BODY


def bound_receipt():
    import hashlib
    r = F.receipt("WRITTEN_AND_VERIFIED")
    r["source"]["sha256"] = hashlib.sha256(BODY.encode("utf-8")).hexdigest()
    return r


def bind(validate=V.validate_receipt, extract=B.extract_owner_block, raw=RAW, rec=None):
    return S.bind_receipt_source(raw, bound_receipt() if rec is None else rec, validate, extract)


class Bk129InjectedReturnTypes(unittest.TestCase):
    """BK-129: malformed injected validator/extractor results fail closed."""

    def test_real_dependencies_bind(self):
        self.assertTrue(bind()["bound"], bind()["errors"])

    def test_non_object_or_non_true_validator_results_fail_closed(self):
        for value in (None, [], "valid", True, 1, {"valid": 1}, {"valid": "True"}, {"valid": False},
                      {"valid": False, "errors": "bad"}, {"valid": False, "errors": None}, {}):
            with self.subTest(value=value):
                result = bind(validate=lambda _r, v=value: v)
                self.assertFalse(result["bound"])
                self.assertIsNone(result["derived_source"])

    def test_extractor_bad_returns_fail_closed(self):
        for value in (None, b"Health 1500 yes.", 7, ["Health"], {"body": BODY}):
            with self.subTest(value=value):
                self.assertFalse(bind(extract=lambda _t, _i, _e, v=value: v)["bound"])

    def test_extractor_that_reports_an_error_but_returns_a_body_fails_closed(self):
        def noisy(_text, _id, errs):
            errs.append("duplicate")
            return BODY
        self.assertFalse(bind(extract=noisy)["bound"])

    def test_extractor_returning_a_different_body_fails_on_hash(self):
        result = bind(extract=lambda *_a: BODY + " (edited)")
        self.assertFalse(result["bound"])
        self.assertTrue(any("source.sha256" in e for e in result["errors"]))

    def test_valid_result_for_a_receipt_without_a_source_object_fails_closed(self):
        for rec in ("receipt", {"source": "O-77"}, {"source": None}, {}):
            with self.subTest(rec=rec):
                self.assertFalse(bind(validate=lambda _r: {"valid": True, "errors": []}, rec=rec)["bound"])


class Bk126To129HotfixRegressions(unittest.TestCase):
    """Gaps R1-R4 from C-1320, fixed by the lead in X-2016, plus R5 (X-2016); each former gap is now a passing regression."""

    def test_gap_r1_refusal_with_non_list_locks_is_invalid_not_an_exception(self):
        """R1 (validate_sevarog_executor_receipt.py:174): for REFUSED_AFTER_LOCKS the created-lock count iterates
        receipt.get("locks", []); the key always exists (TOP_KEYS), so locks=None or locks=3 raised TypeError before
        _locks could report "locks must contain exactly two lock records". Fixed (X-2016): count only a list."""
        for bad in (None, 3):
            r = refusal()
            r["locks"] = bad
            self.assertFalse(V.validate_receipt(r)["valid"])

    def test_gap_r2_adapter_fails_closed_when_source_lacks_message_id(self):
        """R2 (bind_receipt_source.py:56): after an injected validator says valid, claimed["message_id"] is indexed
        directly; a source object without that key (an extractor that returns a body for id None) raises KeyError.
        Fixed (X-2016): the exact source shape is checked before indexing."""
        result = bind(validate=lambda _r: {"valid": True, "errors": []}, extract=lambda *_a: BODY,
                      rec={"source": {"sender": "Owner"}})
        self.assertFalse(result["bound"])

    def test_gap_r3_raising_dependencies_fail_closed(self):
        """R3 (bind_receipt_source.py:35 and :50): an exception from the injected validator or extractor propagates
        out of bind_receipt_source, so the caller gets no {bound: False} evidence record. Fixed (X-2016): either
        exception now returns bound=False."""
        def boom(*_a):
            raise RuntimeError("dependency failure")
        for kwargs in (dict(validate=boom), dict(extract=boom)):
            self.assertFalse(bind(**kwargs)["bound"])

    def test_gap_r4_unencodable_body_fails_closed(self):
        """R4 (bind_receipt_source.py:57): the body is hashed with body.encode("utf-8"); a body containing a lone
        surrogate (text decoded with surrogateescape, or a crafted string) raises UnicodeEncodeError. Fixed (X-2016): such a
        body is refused instead of raising."""
        raw = RAW.replace(BODY, BODY + "\udc80")
        self.assertFalse(bind(raw=raw)["bound"])

    def test_r5_valid_flag_with_reported_errors_does_not_bind(self):
        """R5 (my C-1320 edge, fixed in X-2016): a validator result {valid: True} binds only with an empty errors
        list; non-empty, missing or non-list errors must refuse before extraction."""
        def extract(*_a):
            raise AssertionError("extractor must not run")
        for value in ({"valid": True, "errors": ["tampered"]}, {"valid": True}, {"valid": True, "errors": None},
                      {"valid": True, "errors": ()}, {"valid": True, "errors": "x"}):
            with self.subTest(value=value):
                result = bind(validate=lambda _r, v=value: v, extract=extract)
                self.assertFalse(result["bound"])
                self.assertIsNone(result["derived_source"])
        self.assertTrue(bind(validate=lambda _r: {"valid": True, "errors": []})["bound"])


if __name__ == "__main__":
    unittest.main()
