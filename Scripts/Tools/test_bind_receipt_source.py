"""BK-124 (C, implementer; X-2012, X-2013): synthetic tests for bind_receipt_source.py.

Synthetic mailbox text and receipts only (receipt fixtures from the existing receipt test module); no files, Unreal,
processes, network, assets or locks. A bound result proves text binding only - not runtime events or authorization.
"""
import ast
import contextlib
import copy
import hashlib
import importlib.util
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, HERE / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


S = load("bind_receipt_source", "bind_receipt_source.py")
F = load("receipt_fixtures", "test_validate_sevarog_executor_receipt.py")
B = load("bind_owner_approval", "bind_owner_approval.py")
BODY = "Health 1500 yes.\nThreshold 0.6 yes."
OUTCOMES = ("DRY_RUN_ONLY", "WRITTEN_AND_VERIFIED", "FAILED_RESTORED", "FAILED_RESTORE_NEEDS_OPERATOR",
            "REFUSED_AFTER_LOCKS", "LOCK_RETAINED_NEEDS_OPERATOR")


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def mailbox(body=BODY, owner_id="O-77", sender="Owner", tail="\n### [X-2013] Codex -> Claude, 2026-11-12 09:05\nack\n"):
    return ("### [X-1991] Codex -> Owner, 2026-11-11 14:53\nDecision needed.\n\n"
            "### [%s] %s -> Codex, 2026-11-12 09:00\n%s\n%s" % (owner_id, sender, body, tail))


def receipt(outcome="WRITTEN_AND_VERIFIED", body=BODY, message_id="O-77"):
    r = F.receipt(outcome)
    r["source"] = {"message_id": message_id, "sender": "Owner", "path": S.MAILBOX_PATH, "sha256": sha(body)}
    return r


def bind(raw, rec):
    """The caller (future executor) injects the binder's and validator's own rule functions."""
    return S.bind_receipt_source(raw, rec, F.V.validate_receipt, B.extract_owner_block)


class ReceiptSourceTests(unittest.TestCase):
    def refused(self, needle, raw=None, rec=None):
        result = bind(mailbox() if raw is None else raw, receipt() if rec is None else rec)
        self.assertFalse(result["bound"])
        self.assertEqual(result["proves"], "text-binding-only")
        self.assertTrue(any(needle in e for e in result["errors"]), (needle, result["errors"]))

    def test_every_outcome_binds_to_a_matching_owner_block(self):
        for outcome in OUTCOMES:
            with self.subTest(outcome):
                self.assertTrue(F.V.validate_receipt(receipt(outcome))["valid"], outcome)
                result = bind(mailbox(), receipt(outcome))
                self.assertTrue(result["bound"], result["errors"])
                self.assertEqual(result["derived_source"], receipt(outcome)["source"])
                self.assertEqual(result["proves"], "text-binding-only")

    def test_altered_body_or_receipt_hash_is_refused(self):
        self.refused("source.sha256", raw=mailbox(body=BODY.replace("1500", "1600")))
        rec = receipt(); rec["source"]["sha256"] = sha(BODY + " ")
        self.refused("source.sha256", rec=rec)
        self.refused("source.sha256", rec=receipt(body="Health 1500 yes."))  # receipt hashed only part of the message

    def test_wrong_or_repeated_id_is_refused(self):
        self.refused("no block with id O-78", rec=receipt(message_id="O-78"))
        repeated = mailbox() + "### [O-77] Owner -> Codex, 2026-11-12 09:10\nRevised.\n"
        self.refused("duplicate blocks with id O-77", raw=repeated)

    def test_truncated_or_empty_block_is_refused(self):
        self.refused("possibly truncated", raw="### [O-77] Owner -> Codex, 2026-11-12 09:00\n" + BODY)
        self.refused("empty body", raw="### [O-77] Owner -> Codex, 2026-11-12 09:00\n\n### [X-2013] Codex -> Claude\nack\n")
        self.refused("raw mailbox text is required", raw="")

    def test_agent_authored_source_is_refused(self):
        self.refused("not Owner", raw=mailbox(sender="Codex"))
        rec = receipt(); rec["source"]["message_id"] = "X-1991"
        self.refused("receipt:", rec=rec)  # the receipt validator already refuses an agent id

    def test_malformed_receipt_is_refused_before_any_source_check(self):
        for mutate in (lambda r: r.update(outcome=[]), lambda r: r.pop("source"), lambda r: r.update(source="O-77"),
                       lambda r: r["source"].update(path="Docs/x.md")):
            with self.subTest(mutate=mutate):
                rec = receipt()
                mutate(rec)
                result = bind(mailbox(), rec)
                self.assertFalse(result["bound"])
                self.assertIsNone(result["derived_source"])
        self.assertFalse(bind(mailbox(), "receipt")["bound"])

    def test_receipt_and_text_are_not_mutated(self):
        rec, raw = receipt(), mailbox()
        before = copy.deepcopy(rec)
        bind(raw, rec)
        self.assertEqual(rec, before)

    def test_cleanly_cut_final_block_is_an_explicit_limit(self):
        """Documented limit (X-2013): a final block cut at a line end is indistinguishable from a complete one; the
        binding is still exact for the text given, so the caller must pass the whole mailbox file."""
        cut = "### [O-77] Owner -> Codex, 2026-11-12 09:00\nHealth 1500 yes.\n"
        self.assertTrue(bind(cut, receipt(body="Health 1500 yes."))["bound"])
        self.assertFalse(bind(cut, receipt())["bound"])  # but it never binds the full message's hash

    def test_rule_functions_must_be_injected(self):
        for args in ((None, B.extract_owner_block), (F.V.validate_receipt, None), ("x", "y")):
            with self.subTest(args=args):
                result = S.bind_receipt_source(mailbox(), receipt(), *args)
                self.assertFalse(result["bound"])
                self.assertIn("injected callables", result["errors"][0])
        with self.assertRaises(TypeError):
            S.bind_receipt_source(mailbox(), receipt())  # no hidden default loader

    def test_malformed_validator_results_fail_closed(self):
        for bad_result in (None, "valid", [], {"valid": False, "errors": "not-a-list"}):
            result = S.bind_receipt_source(mailbox(), receipt(), lambda _r, value=bad_result: value,
                                           B.extract_owner_block)
            self.assertFalse(result["bound"])
            self.assertIsNone(result["derived_source"])
            self.assertTrue(result["errors"])
        result = S.bind_receipt_source(mailbox(), "not-a-receipt", lambda _r: {"valid": True, "errors": []},
                                       B.extract_owner_block)
        self.assertFalse(result["bound"])
        self.assertIn("missing an object source", result["errors"][0])

    def test_malicious_or_raising_dependencies_fail_closed(self):
        accepted = lambda _r: {"valid": True, "errors": []}
        self.assertFalse(S.bind_receipt_source(mailbox(), {"source": {"sender": "Owner"}}, accepted,
                                               lambda *_a: BODY)["bound"])
        for inconsistent in ({"valid": True, "errors": ["rejected field"]}, {"valid": True, "errors": None}):
            result = S.bind_receipt_source(mailbox(), receipt(), lambda _r, v=inconsistent: v, B.extract_owner_block)
            self.assertFalse(result["bound"])
            self.assertIsNone(result["derived_source"])
        def boom(*_args):
            raise RuntimeError("synthetic failure")
        for validate, extract in ((boom, B.extract_owner_block), (F.V.validate_receipt, boom)):
            result = S.bind_receipt_source(mailbox(), receipt(), validate, extract)
            self.assertFalse(result["bound"])
            self.assertTrue(any("raised RuntimeError" in error for error in result["errors"]))

    def test_unencodable_owner_body_fails_closed(self):
        raw = mailbox(body=BODY + "\udc80")
        result = bind(raw, receipt())
        self.assertFalse(result["bound"])
        self.assertIn("not valid UTF-8 text", result["errors"][0])

    def test_module_source_has_no_io_or_loader(self):
        tree = ast.parse((HERE / "bind_receipt_source.py").read_text(encoding="utf-8"))
        imports = {alias.name for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names}
        self.assertEqual(imports, {"hashlib"})
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        self.assertEqual(names & {"__file__", "open", "importlib", "Path", "exec", "eval", "__import__"}, set())
        for node in tree.body:  # import time: only the docstring, the import, constants and the function definition
            self.assertIsInstance(node, (ast.Expr, ast.Import, ast.Assign, ast.FunctionDef), ast.dump(node)[:80])
            if isinstance(node, ast.Assign):
                self.assertIsInstance(node.value, (ast.Constant, ast.Tuple), ast.dump(node)[:80])

    def test_runtime_call_touches_no_filesystem(self):
        def refuse(*_args, **_kwargs):
            raise AssertionError("filesystem access during bind_receipt_source")
        targets = ("builtins.open", "io.open", "os.open", "os.stat", "os.listdir", "os.scandir",
                   "pathlib.Path.open", "pathlib.Path.read_text", "pathlib.Path.read_bytes", "pathlib.Path.exists")
        rec, raw = receipt(), mailbox()
        with contextlib.ExitStack() as stack:
            for target in targets:
                stack.enter_context(mock.patch(target, refuse))
            bound = bind(raw, rec)
            refused = bind(raw.replace("1500", "1600"), rec)
        self.assertTrue(bound["bound"], bound["errors"])
        self.assertFalse(refused["bound"])

if __name__ == "__main__":
    unittest.main()
