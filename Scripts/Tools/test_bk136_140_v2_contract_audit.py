"""BK-136..139 (C, implementer; X-2022): audit of the PROPOSED v2 receipt schema against the real ExecutorContract.

New file; sevarog_receipt_v2_proposal.py, its tests/report and all production code are unchanged and only imported.
The real ExecutorContract is explored with a stub binder (no files, Unreal, assets or locks). Proposal-only: a valid
v2 receipt is not runtime proof or write authorization; X-1991 remains open.

BK-136  explore every reachable contract state with every action/input variant; compare observed edges to TRANSITIONS.
BK-137  enumerate every _refuse call site (AST) and every refusal observed while exploring; map each to a legal
        v2 (stage, reason) and check the resulting receipt is representable.
BK-138  enumerate every legal v2 history (bounded) and check terminal/outcome/artifact consistency, with and without
        a retained lock.
BK-139  malformed nested values for every record key: no exception, fail closed.
"""
import ast
import copy
import importlib.util
import itertools
import math
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, HERE / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


T = load("v2_tests_bk136", "test_sevarog_receipt_v2_proposal.py")  # read-only reuse of the v2 receipt builder
P, C = T.P, T.C
DRY, BAD, TOKEN = T.DRY, T.BAD, T.TOKEN
LOCKS = C.LOCK_PATHS
OWN = {"owner_token": TOKEN, "party": "X", "policy": "C-1155"}


class Binder:
    """Stub: snapshot markers decide plan acceptance and divergence; readback is ok when after['ok'] is True."""

    class PLANNER:
        @staticmethod
        def verify_readback(_plan, after):
            ok = isinstance(after, dict) and after.get("ok") is True
            return {"ok": ok, "errors": [] if ok else ["mismatch"]}

    @staticmethod
    def plan_from_bound(_binding, snapshot, context, allow_write=False):
        snapshot = snapshot if isinstance(snapshot, dict) else {}
        if snapshot.get("refuse_dry") and context.get("mode") == "dry_run":
            return {"accepted": False, "errors": ["synthetic dry refusal"]}
        if snapshot.get("refuse_write") and allow_write:
            return {"accepted": False, "errors": ["synthetic write refusal"]}
        to = 3 if (allow_write and snapshot.get("diverge")) else 2
        return {"accepted": True, "writes": [{"field_path": "Health", "from": 1, "to": to}], "untouched_phase_rows": []}


BOUND = {"bound": True, "approval_complete": True}
ACTIONS = {
    "start": [("start", (BOUND,), {"explicit_write": True}), ("start", (BOUND,), {"explicit_write": False}),
              ("start", ({"bound": True, "approval_complete": False},), {"explicit_write": True}),
              ("start", (None,), {}), ("start", ({"bound": False, "errors": ["x"]},), {})],
    "plan_dry_run": [("plan_dry_run", ({"file_sha256": DRY},), {}), ("plan_dry_run", ({"file_sha256": DRY, "refuse_dry": True},), {})],
    "acquire_locks": [("acquire_locks", (TOKEN, {p: OWN for p in LOCKS}, list(LOCKS)), {}),
                      ("acquire_locks", (TOKEN, {LOCKS[0]: OWN}, [LOCKS[0]]), {}),
                      ("acquire_locks", (TOKEN, {p: dict(OWN, owner_token="f" * 32) for p in LOCKS}, []), {}),
                      ("acquire_locks", (TOKEN, {}, "not-a-list"), {}),
                      ("acquire_locks", (TOKEN, {}, [LOCKS[0], LOCKS[0]]), {}),
                      ("acquire_locks", ("BAD", {}, list(LOCKS)), {}),
                      ("acquire_locks", (TOKEN, {p: dict(OWN, party="C") for p in LOCKS}, list(LOCKS)), {})],
    "verify_backup": [("verify_backup", ({"file_sha256": DRY}, {"path": T.BACKUP, "sha256": DRY}), {}),
                      ("verify_backup", ({"file_sha256": DRY, "refuse_write": True}, {"path": T.BACKUP, "sha256": DRY}), {}),
                      ("verify_backup", ({"file_sha256": DRY, "diverge": True}, {"path": T.BACKUP, "sha256": DRY}), {}),
                      ("verify_backup", ({}, {"path": T.BACKUP, "sha256": DRY}), {}),
                      ("verify_backup", ({"file_sha256": BAD}, {"path": T.BACKUP, "sha256": BAD}), {}),
                      ("verify_backup", ({"file_sha256": DRY}, {"path": T.BACKUP, "sha256": BAD}), {})],
    "plan_write": [("plan_write", (), {})],
    "record_save": [("record_save", (True,), {}), ("record_save", (False,), {})],
    "readback": [("readback", ({"ok": True},), {}), ("readback", ({"ok": False},), {})],
    "record_restore": [("record_restore", (DRY,), {}), ("record_restore", (BAD,), {}), ("record_restore", (None,), {})],
    "release_locks": [("release_locks", ({p: True for p in LOCKS},), {}), ("release_locks", ({LOCKS[0]: True},), {}),
                      ("release_locks", ({},), {})],
}
VARIANTS = [v for group in ACTIONS.values() for v in group]

# BK-137: every _refuse message prefix -> (stage, v2 reason). Stage = contract state when the refusal happened.
REFUSAL_MAP = (
    ("a binding from bind_owner_approval() is required", "INIT", "BINDING_MISSING"),
    ("owner source is missing or malformed", "INIT", "SOURCE_UNBOUND"),
    ("dry-run plan refused", "STARTED", "DRY_PLAN_REFUSED"),
    ("lock creation receipts must list only known lock paths", "DRY_RUN_PLANNED", "CREATE_RECEIPTS_INVALID"),
    ("lock creation receipts contain unknown or duplicate paths", "DRY_RUN_PLANNED", "CREATE_RECEIPTS_INVALID"),
    ("write refused: explicit write opt-in was not given", "DRY_RUN_PLANNED", "EXPLICIT_WRITE_MISSING"),
    ("write refused: owner approval is incomplete", "DRY_RUN_PLANNED", "APPROVAL_INCOMPLETE"),
    ("lock identity failure: the run token must be 32 lowercase hex", "DRY_RUN_PLANNED", "TOKEN_INVALID"),
    ("lock acquisition failed", "DRY_RUN_PLANNED", "ACQUISITION_FAILED"),
    ("lock identity failure: ", "DRY_RUN_PLANNED", "LOCK_IDENTITY"),  # after the token prefix above (first match wins)
    ("locked snapshot needs the asset file before-hash", "LOCKED", "BEFORE_HASH_MISSING"),
    ("the asset changed between the dry run and the locked snapshot", "LOCKED", "ASSET_CHANGED"),
    ("backup mismatch", "LOCKED", "BACKUP_MISMATCH"),
    ("write plan refused", "BACKED_UP", "WRITE_PLAN_REFUSED"),
    ("write plan differs from the dry-run diff", "BACKED_UP", "WRITE_PLAN_DIVERGED"),
)


def classify(message):
    for prefix, stage, reason in REFUSAL_MAP:
        if message.startswith(prefix):
            return stage, reason
    return None


def explore(max_depth=12):
    """Breadth-first over (contract, action variant); returns observed edges, refusals and terminal runs."""
    start = C.ExecutorContract(Binder(), party="X")
    frontier, edges, refusals, terminals, seen = [start], set(), set(), [], set()
    for _depth in range(max_depth):
        nxt = []
        for contract in frontier:
            for method, args, kwargs in VARIANTS:
                trial = copy.deepcopy(contract)
                before_state, before_len = trial.state, len(trial.history)
                result = getattr(trial, method)(*copy.deepcopy(args), **copy.deepcopy(kwargs))
                if len(trial.history) == before_len:
                    continue  # wrong state: no transition
                edges.add((before_state, trial.state))
                if trial.state in ("REFUSED", "RELEASE_REQUIRED"):
                    refusals.add((before_state, trial.errors[-1]))
                # Include every input the contract keeps, so distinct futures are never merged.
                key = (tuple(trial.history), tuple(trial.created_locks), trial.explicit_write, trial.outcome,
                       repr(trial.binding), repr(trial.locked_snapshot))
                if key in seen:
                    continue
                seen.add(key)
                if trial.state in ("RELEASED", "REFUSED") or (trial.state == "DRY_RUN_PLANNED" and not trial.explicit_write):
                    terminals.append(trial)
                if trial.state not in ("RELEASED", "REFUSED"):
                    nxt.append(trial)
                del result
        frontier = nxt
        if not frontier:
            break
    return edges, refusals, terminals


EDGES, REFUSALS, TERMINALS = explore()
V2_EDGES = {(a, b) for a, targets in P.TRANSITIONS.items() for b in targets}


class Bk136TransitionAudit(unittest.TestCase):
    def test_exploration_is_exhaustive_and_finite(self):
        self.assertGreater(len(TERMINALS), 20)
        self.assertTrue(all(len(t.history) <= P.MAX_HISTORY for t in TERMINALS))

    def test_every_observed_contract_edge_is_in_transitions(self):
        self.assertEqual(EDGES - V2_EDGES, set(), "contract edges missing from TRANSITIONS")

    def test_every_transitions_edge_is_observed_in_the_contract(self):
        self.assertEqual(V2_EDGES - EDGES, set(), "TRANSITIONS edges the contract never takes")

    def test_every_contract_terminal_history_is_legal(self):
        for contract in TERMINALS:
            with self.subTest(history=contract.history):
                self.assertTrue(P.check_history(list(contract.history), []), contract.history)


class Bk137RefusalSites(unittest.TestCase):
    def refuse_messages_in_source(self):
        tree = ast.parse((HERE / "sevarog_executor_contract.py").read_text(encoding="utf-8"))
        sites = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "_refuse":
                arg = node.args[0]
                text = arg.left.value if isinstance(arg, ast.BinOp) else arg.value
                sites.append((node.lineno, text))
        return sites

    def test_every_source_refusal_site_maps_to_a_legal_stage_reason(self):
        sites = self.refuse_messages_in_source()
        self.assertEqual(len(sites), 16)  # X-2042/BK-194 added the backup-path refusal (maps to BACKUP_MISMATCH)
        for lineno, text in sites:
            with self.subTest(line=lineno):
                mapped = classify(text)
                self.assertIsNotNone(mapped, text)
                stage, reason = mapped
                self.assertIn(reason, P.REASONS[stage])

    def test_every_observed_refusal_maps_to_its_stage_and_a_legal_reason(self):
        observed_reasons = set()
        for stage, message in REFUSALS:
            with self.subTest(stage=stage, message=message[:50]):
                mapped = classify(message)
                self.assertIsNotNone(mapped, message)
                self.assertEqual(mapped[0], stage)
                self.assertIn(mapped[1], P.REASONS[stage])
                observed_reasons.add(mapped[1])
        self.assertEqual(observed_reasons, set().union(*P.REASONS.values()), "every v2 reason code is reachable")

    def test_every_refused_or_released_run_maps_to_the_receipt_refusal_stage(self):
        for contract in TERMINALS:
            stage, aborted = P.refusal_stage(list(contract.history))
            refused = any(s in ("REFUSED", "RELEASE_REQUIRED") for s in contract.history)
            with self.subTest(history=contract.history):
                if refused:
                    self.assertFalse(aborted)
                    self.assertEqual(classify(contract.errors[-1] if contract.state == "REFUSED" else
                                              next(e for e in contract.errors if classify(e)))[0], stage)

    def test_finding_f1_token_invalid_with_created_locks_has_no_valid_receipt(self):
        """F1: _refuse at contract :126 (TOKEN_INVALID) runs after created_locks is recorded (:118), so the run ends
        RELEASE_REQUIRED -> RELEASED holding locks whose token is not 32-hex. v2 requires every created lock token to
        be 32-hex, so this contract-reachable run cannot produce a valid v2 receipt. Lead decision: allow a null or
        malformed token for TOKEN_INVALID refusals, or require the executor to validate the token before creating."""
        contract = C.ExecutorContract(Binder(), party="X")
        contract.start(BOUND, explicit_write=True)
        contract.plan_dry_run({"file_sha256": DRY})
        contract.acquire_locks("BAD", {}, list(LOCKS))
        contract.release_locks({p: True for p in LOCKS})
        self.assertEqual(contract.history[-2:], ["RELEASE_REQUIRED", "RELEASED"])
        receipt = T.make(list(contract.history), refusal={"stage": "DRY_RUN_PLANNED", "reason": "TOKEN_INVALID"})
        for lock in receipt["locks"]:
            lock["token"] = "BAD"
        self.assertIn("locks[0].token must be 32 lowercase hex", P.validate_v2(receipt)["errors"])


class Bk137LeadDecisionF1(unittest.TestCase):
    def test_f1_decision_b_no_lock_token_invalid_receipt_validates(self):
        """Lead decision F1 = (b) (X-2023): the executor validates its token BEFORE any lock create and, if invalid,
        calls acquire_locks with created_paths=[]; the contract then refuses lock-free at :126 (state REFUSED), and that
        receipt is valid v2 with the strict 32-hex lock rule unchanged."""
        contract = C.ExecutorContract(Binder(), party="X")
        contract.start(BOUND, explicit_write=True)
        contract.plan_dry_run({"file_sha256": DRY})
        result = contract.acquire_locks("BAD", {}, [])
        self.assertEqual(result["state"], "REFUSED")
        self.assertEqual(classify(contract.errors[-1]), ("DRY_RUN_PLANNED", "TOKEN_INVALID"))
        receipt = T.make(list(contract.history), refusal={"stage": "DRY_RUN_PLANNED", "reason": "TOKEN_INVALID"})
        verdict = P.validate_v2(receipt)
        self.assertTrue(verdict["valid"], verdict["errors"])
        self.assertEqual(verdict["derived_outcome"], "REFUSED_BEFORE_LOCKS")
        self.assertTrue(all(lock["created"] is False and lock["token"] is None for lock in receipt["locks"]))

    def test_f1_decision_b_keeps_the_strict_lock_token_rule(self):
        """The created-lock invalid-token run stays rejected; v2 lock identity is not weakened (X-2023)."""
        receipt = T.make(T.H("RELEASE_REQUIRED", "RELEASED"), refusal={"stage": "DRY_RUN_PLANNED", "reason": "TOKEN_INVALID"})
        for bad in ("BAD", None, "A" * 32, "0" * 31):
            with self.subTest(token=bad):
                r = copy.deepcopy(receipt)
                for lock in r["locks"]:
                    lock["token"] = bad
                self.assertFalse(P.validate_v2(r)["valid"])


class Bk137ContractOutcomeFinding(unittest.TestCase):
    def test_finding_f2_lock_free_refusal_outcome_is_none_or_stale_dry_run(self):
        """F2: the contract never sets an outcome for a lock-free refusal (state REFUSED): it stays None, or stays
        DRY_RUN_ONLY when a dry-run-mode contract (:105-106) is later refused at acquire_locks with nothing created.
        v2 derives REFUSED_BEFORE_LOCKS from the history instead, so a future executor must not copy contract.outcome
        into a receipt for REFUSED runs."""
        refused = [c for c in TERMINALS if c.state == "REFUSED"]
        self.assertEqual({c.outcome for c in refused}, {None, "DRY_RUN_ONLY"})
        for contract in refused:
            self.assertEqual(P.derive_outcome(list(contract.history), False), "REFUSED_BEFORE_LOCKS")


def legal_histories():
    out, stack = [], [["INIT"]]
    while stack:
        history = stack.pop()
        if history[-1] in P.TERMINALS:
            out.append(history)
        if len(history) < P.MAX_HISTORY:
            for nxt in sorted(P.TRANSITIONS.get(history[-1], ())):
                stack.append(history + [nxt])
    return sorted(out)


def receipt_for(history, retain):
    """A canonical valid v2 receipt for any legal history (using the BK-135 builder)."""
    stage, aborted = P.refusal_stage(history)
    refusal = None
    kwargs = {}
    if stage is not None:
        reason = P.ABORTED if aborted else sorted(P.REASONS[stage])[0]
        if stage == "LOCKED" and not aborted:
            reason = "BEFORE_HASH_MISSING"
        refusal = {"stage": stage, "reason": reason}
        if stage == "LOCKED" and "BACKED_UP" not in history:
            kwargs["backup"] = T.SKIPPED
    if "RESTORED" in history:
        kwargs["restored"] = DRY
    elif "RESTORE_FAILED" in history:
        kwargs["restored"] = BAD
    holds = any(s in P.HOLDS_LOCKS for s in history)
    if holds:
        kwargs["created"] = (True, True)
        kwargs["released"] = (True, False) if retain else (True, True)
    return T.make(history, refusal=refusal, **kwargs)


HISTORIES = legal_histories()


class Bk138BoundedHistories(unittest.TestCase):
    def test_enumeration_is_bounded_and_deterministic(self):
        self.assertEqual(HISTORIES, legal_histories())
        self.assertEqual(len(HISTORIES), len({tuple(h) for h in HISTORIES}))
        self.assertTrue(all(len(h) <= P.MAX_HISTORY for h in HISTORIES))
        observed = {tuple(c.history) for c in TERMINALS}
        self.assertEqual({tuple(h) for h in HISTORIES} - observed, set(), "every legal history is contract-reachable")

    def test_every_legal_history_has_a_valid_consistent_receipt(self):
        for history, retain in itertools.product(HISTORIES, (False, True)):
            holds = any(s in P.HOLDS_LOCKS for s in history)
            if retain and not holds:
                continue
            with self.subTest(history=history, retain=retain):
                receipt = receipt_for(history, retain)
                result = P.validate_v2(receipt)
                self.assertTrue(result["valid"], result["errors"])
                outcome, terminal, prior = result["derived_outcome"], history[-1], history[-2] if len(history) > 1 else None
                kinds = sorted(a["kind"] for a in result["expected_artifacts"])
                self.assertEqual(terminal == "REFUSED", outcome == "REFUSED_BEFORE_LOCKS")
                self.assertEqual(terminal == "DRY_RUN_PLANNED", outcome == "DRY_RUN_ONLY")
                self.assertEqual(retain, outcome == "LOCK_RETAINED_NEEDS_OPERATOR")
                if not retain and terminal == "RELEASED":
                    self.assertEqual(outcome == "WRITTEN_AND_VERIFIED", prior == "VERIFIED")
                    self.assertEqual(outcome == "ABANDONED_NEEDS_OPERATOR", prior in P.ABANDON_STATES)
                self.assertEqual("lock" in kinds, retain)
                self.assertEqual("asset_needs_operator" in kinds,
                                 "RESTORE_FAILED" in history or (terminal == "RELEASED" and prior in P.ABANDON_STATES))
                self.assertEqual(sorted(a["kind"] for a in receipt["artifacts"]), kinds)

    def test_contract_outcomes_agree_with_v2_except_the_abandoned_divergence(self):
        for contract in TERMINALS:
            if contract.state == "DRY_RUN_PLANNED":
                continue
            retained = contract.outcome == "LOCK_RETAINED_NEEDS_OPERATOR"
            derived = P.derive_outcome(list(contract.history), retained)
            with self.subTest(history=contract.history, outcome=contract.outcome):
                if derived == "ABANDONED_NEEDS_OPERATOR":
                    self.assertEqual(contract.outcome, "REFUSED_AFTER_LOCKS")  # documented A6 divergence
                elif contract.state == "REFUSED":
                    self.assertEqual(derived, "REFUSED_BEFORE_LOCKS")  # contract leaves outcome unset or DRY_RUN_ONLY
                else:
                    self.assertEqual(derived, contract.outcome)


BAD_VALUES = (None, [], {}, (), 1.5, -1, 0, True, False, "", "x", "A" * 64, math.nan, math.inf, [None], {"k": []})
RECORD_SCENARIOS = ("written", "retained_after_restore_failed", "backup_mismatch_retained", "partial_lock",
                    "refused_at_start", "abandoned_after_save")


def record_paths(receipt):
    """(label, getter-parent, key) for every key of every nested record."""
    for key in receipt:
        yield key, receipt, key
    for record in ("source", "asset", "backup_attempt", "refusal"):
        if isinstance(receipt[record], dict):
            for key in receipt[record]:
                yield "%s.%s" % (record, key), receipt[record], key
    for index, lock in enumerate(receipt["locks"]):
        for key in lock:
            yield "locks[%d].%s" % (index, key), lock, key
    for index, item in enumerate(receipt["artifacts"]):
        for key in item:
            yield "artifacts[%d].%s" % (index, key), item, key
    for index in range(len(receipt["history"])):
        yield "history[%d]" % index, receipt["history"], index


class Bk139MalformedNestedValues(unittest.TestCase):
    def test_no_exception_and_fail_closed_for_every_nested_key(self):
        still_valid, checked = [], 0
        for name in RECORD_SCENARIOS:
            base = T.scenario(name)
            labels = [label for label, _p, _k in record_paths(base)]
            for label, value in itertools.product(labels, BAD_VALUES):
                receipt = copy.deepcopy(base)
                parent, key = next((p, k) for lab, p, k in record_paths(receipt) if lab == label)
                original = parent[key]
                if type(original) is type(value) and original == value:
                    continue
                parent[key] = copy.deepcopy(value)
                checked += 1
                try:
                    result = P.validate_v2(receipt)
                except Exception as exc:  # noqa: BLE001 - the contract under test is "never raises"
                    self.fail("%s %s=%r raised %s: %s" % (name, label, value, type(exc).__name__, exc))
                if result["valid"]:
                    still_valid.append((name, label, value))
        self.assertGreater(checked, 1500)
        self.assertEqual(still_valid, ALLOWED_STILL_VALID, still_valid)


# Mutations that legitimately leave a receipt valid (documented in the BK-140 report): a refusal during lock
# acquisition may have no lock-file readback (contract :129-133), so readback_token/party/policy may be null there.
ALLOWED_STILL_VALID = [("partial_lock", "locks[0].readback_token", None), ("partial_lock", "locks[0].party", None),
                       ("partial_lock", "locks[0].policy", None)]


if __name__ == "__main__":
    unittest.main()
