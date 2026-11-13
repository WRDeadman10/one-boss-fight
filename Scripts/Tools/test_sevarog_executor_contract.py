"""BK-103 (C, implementer; X-2004): synthetic transition tests for sevarog_executor_contract.py.

The real binder and planner modules are used with synthetic mailbox text, envelopes and snapshots. No filesystem
writes, no Unreal, no assets, no locks: every "observation" (lock records, backup hash, save result, readback) is an
in-memory value the test hands to the contract.
"""
import copy
import hashlib
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


B = load("bind_owner_approval")
C = load("sevarog_executor_contract")

REPLY = ("Health 1500 yes.\nPosture 100 yes, poise maps to posture.\nRegen delay 4 seconds.\nRegen rate 10 per second.\n"
         "Keep Phase_1 as the phase id.\nThreshold 0.6 yes.\nSpeed multiplier 1.1.\nAttack multiplier 1.0.\nRate multiplier 1.0 is fine.")
FULL = [
    ("Stats.MaxHealth", "APPROVE_CANDIDATE", 1500.0, "Health 1500 yes."),
    ("Stats.MaxPosture", "APPROVE_CANDIDATE", 100.0, "Posture 100 yes, poise maps to posture."),
    ("Stats.PostureRegenDelay", "APPROVE_VALUE", 4.0, "Regen delay 4 seconds."),
    ("Stats.PostureRegenRate", "APPROVE_VALUE", 10.0, "Regen rate 10 per second."),
    ("Phases[Phase_1].PhaseId", "APPROVE_CANDIDATE", "Phase_1", "Keep Phase_1 as the phase id."),
    ("Phases[Phase_1].EntryHealthFraction", "APPROVE_CANDIDATE", 0.6, "Threshold 0.6 yes."),
    ("Phases[Phase_1].SpeedMultiplier", "APPROVE_VALUE", 1.1, "Speed multiplier 1.1."),
    ("Phases[Phase_1].AttackMultiplier", "APPROVE_CANDIDATE", 1.0, "Attack multiplier 1.0."),
    ("Phases[Phase_1].RateMultiplier", "APPROVE_CANDIDATE", 1.0, "Rate multiplier 1.0 is fine."),
]
BEFORE, AFTER, TOKEN = "a" * 64, "b" * 64, "0123456789abcdef0123456789abcdef"


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def binding(reply=REPLY, decisions=FULL):
    raw = "### [O-77] Owner -> Codex, 2026-11-12 09:00\n%s\n\n### [X-2005] Codex -> Claude\nack\n" % reply
    envelope = {"schema": B.ENVELOPE.SCHEMA, "envelope_state": "OWNER_DECISION_RECORD", "production_manifest": False,
                "authoring_authorized": False, "request_reference": "X-1991",
                "owner_message": {"message_id": "O-77", "sender": "Owner", "path": "Documentation/TEAM_MAILBOX.md",
                                  "reply_text": reply, "reply_sha256": sha(reply)},
                "decisions": [{"field_path": f, "decision": d, "value": v, "quote": q} for f, d, v, q in decisions]}
    return B.bind_owner_approval(raw, "O-77", envelope)


def snapshot(file_sha256=BEFORE):
    return {"asset_path": B.PLANNER.ASSET_PATH, "exists": True, "file_sha256": file_sha256,
            "stats": {"max_health": 0.0, "max_posture": 0.0, "posture_regen_delay": 0.0, "posture_regen_rate": 0.0},
            "phases": [{"phase_id": "Phase_1", "entry_health_fraction": 0.0, "speed_multiplier": 1.0, "rate_multiplier": 1.0, "attack_multiplier": 1.0}],
            "fields": []}


def lock(token=TOKEN, party="C", policy="C-1155"):
    return {"agent": "Claude", "party": party, "owner_token": token, "policy": policy, "task": "synthetic"}


def both_locks(**override):
    observed = {path: lock() for path in C.LOCK_PATHS}
    observed.update(override)
    return observed


def saved_after(plan):
    after = snapshot(AFTER)
    for write in plan["writes"]:
        group, prop = write["target"].split(".", 1)
        if group == "stats":
            after["stats"][prop] = write["to"]
        else:
            after["phases"][0][prop] = write["to"]
    after["fields"] = copy.deepcopy(plan["field_records"])
    return after


def to_backed_up(contract):
    assert contract.start(binding(), explicit_write=True)["ok"]
    assert contract.plan_dry_run(snapshot())["ok"]
    assert contract.acquire_locks(TOKEN, both_locks(), list(C.LOCK_PATHS))["ok"]
    assert contract.verify_backup(snapshot(), {"path": "Docs/BossCombatReview/Execution/Claude/backup/DA_Boss_Sevarog_Draft.before.uasset", "sha256": BEFORE})["ok"]


class ContractTests(unittest.TestCase):
    def new(self):
        return C.ExecutorContract(B, party="C")

    # --- dry run is the default ---
    def test_dry_run_takes_no_locks_and_cannot_write(self):
        contract = self.new()
        self.assertTrue(contract.start(binding())["ok"])
        self.assertTrue(contract.plan_dry_run(snapshot())["ok"])
        self.assertEqual((contract.state, contract.outcome, contract.next_step()), ("DRY_RUN_PLANNED", "DRY_RUN_ONLY", "done"))
        refused = contract.acquire_locks(TOKEN, both_locks(), [])
        self.assertFalse(refused["ok"])
        self.assertIn("explicit write opt-in", refused["errors"][0])
        self.assertEqual((contract.state, contract.locks_to_release), ("REFUSED", []))

    # --- source ---
    def test_missing_or_malformed_source_is_refused(self):
        for bad in (None, "O-77", 42):
            with self.subTest(bad=bad):
                contract = self.new()
                self.assertFalse(contract.start(bad, explicit_write=True)["ok"])
                self.assertEqual(contract.state, "REFUSED")
        unbound = binding(reply=REPLY.replace("1500", "1600"))  # envelope quotes no longer match the reply
        contract = self.new()
        self.assertFalse(contract.start(unbound, explicit_write=True)["ok"])

    def test_forged_binding_dictionary_is_refused_at_planning(self):
        forged = {"bound": True, "approval_complete": True, "envelope_result": {"valid": True}, "owner_source": {"message_id": "O-1"}}
        contract = self.new()
        self.assertTrue(contract.start(forged, explicit_write=True)["ok"])
        refused = contract.plan_dry_run(snapshot())
        self.assertFalse(refused["ok"])
        self.assertIn("bind_owner_approval() is required", refused["errors"][0])
        self.assertEqual(contract.state, "REFUSED")

    def test_incomplete_approval_never_reaches_a_write(self):
        reply = REPLY.replace("Rate multiplier 1.0 is fine.", "Rate multiplier: undecided.")
        rows = [r if r[0] != "Phases[Phase_1].RateMultiplier" else (r[0], "UNRESOLVED", None, None) for r in FULL]
        contract = self.new()
        self.assertTrue(contract.start(binding(reply, rows), explicit_write=True)["ok"])
        refused = contract.plan_dry_run(snapshot())
        self.assertFalse(refused["ok"])
        self.assertEqual(contract.state, "REFUSED")
        self.assertEqual(contract.locks_to_release, [])

    # --- locks ---
    def test_lock_acquisition_failures_release_only_this_runs_locks(self):
        cases = {
            "second create failed": (both_locks(**{C.LOCK_PATHS[1]: None}), [C.LOCK_PATHS[0]], "a create did not succeed"),
            "other owner holds one": (both_locks(**{C.LOCK_PATHS[0]: lock(token="f" * 32)}), [C.LOCK_PATHS[1]], "held by another owner"),
            "wrong party": (both_locks(**{C.LOCK_PATHS[1]: lock(party="X")}), list(C.LOCK_PATHS), "party C"),
            "wrong policy": (both_locks(**{C.LOCK_PATHS[0]: lock(policy="none")}), list(C.LOCK_PATHS), "policy C-1155"),
            "nothing created": ({}, [], "a create did not succeed"),
        }
        for label, (observed, expected_release, needle) in cases.items():
            with self.subTest(label):
                contract = self.new()
                contract.start(binding(), explicit_write=True)
                contract.plan_dry_run(snapshot())
                created = (expected_release if label in ("second create failed", "other owner holds one")
                           else ([] if label == "nothing created" else list(C.LOCK_PATHS)))
                result = contract.acquire_locks(TOKEN, observed, created)
                self.assertFalse(result["ok"])
                self.assertIn(needle, result["errors"][0])
                self.assertEqual(contract.locks_to_release, expected_release)
                self.assertEqual(contract.state, "RELEASE_REQUIRED" if expected_release else "REFUSED")

    def test_bad_run_token_is_refused_before_any_lock_is_claimed(self):
        contract = self.new()
        contract.start(binding(), explicit_write=True)
        contract.plan_dry_run(snapshot())
        self.assertFalse(contract.acquire_locks("not-a-token", both_locks(), [])["ok"])
        self.assertEqual(contract.locks_to_release, [])

    def test_existing_same_token_record_without_create_receipt_is_not_released(self):
        contract = self.new()
        contract.start(binding(), explicit_write=True)
        contract.plan_dry_run(snapshot())
        result = contract.acquire_locks(TOKEN, both_locks(), [C.LOCK_PATHS[0]])
        self.assertFalse(result["ok"])
        self.assertIn("lacks a receipt", result["errors"][0])
        self.assertEqual(contract.locks_to_release, [C.LOCK_PATHS[0]])

    def test_malformed_lock_creation_receipts_are_refused(self):
        contract = self.new()
        contract.start(binding(), explicit_write=True)
        contract.plan_dry_run(snapshot())
        result = contract.acquire_locks(TOKEN, both_locks(), [{"path": C.LOCK_PATHS[0]}])
        self.assertFalse(result["ok"])
        self.assertEqual(contract.locks_to_release, [])

    def test_malformed_extra_receipt_does_not_drop_cleanup_for_a_valid_created_lock(self):
        contract = self.new()
        contract.start(binding(), explicit_write=True)
        contract.plan_dry_run(snapshot())
        result = contract.acquire_locks(TOKEN, both_locks(), [C.LOCK_PATHS[0], "unknown.lock"])
        self.assertFalse(result["ok"])
        self.assertEqual(contract.state, "RELEASE_REQUIRED")
        self.assertEqual(contract.locks_to_release, [C.LOCK_PATHS[0]])

    # --- backup ---
    def test_backup_mismatch_or_changed_asset_requires_release(self):
        for label, locked_snapshot, backup in (("backup hash", snapshot(), {"path": "b.uasset", "sha256": "c" * 64}),
                                               ("no backup", snapshot(), {}),
                                               ("asset changed", snapshot("d" * 64), {"path": "b.uasset", "sha256": "d" * 64})):
            with self.subTest(label):
                contract = self.new()
                contract.start(binding(), explicit_write=True)
                contract.plan_dry_run(snapshot())
                contract.acquire_locks(TOKEN, both_locks(), list(C.LOCK_PATHS))
                self.assertFalse(contract.verify_backup(locked_snapshot, backup)["ok"])
                self.assertEqual((contract.state, contract.next_step()), ("RELEASE_REQUIRED", "release_locks"))
                done = contract.release_locks({path: True for path in C.LOCK_PATHS})
                self.assertEqual((done["state"], done["outcome"]), ("RELEASED", "REFUSED_AFTER_LOCKS"))

    # --- success ---
    def test_successful_save_and_readback(self):
        contract = self.new()
        to_backed_up(contract)
        self.assertTrue(contract.plan_write()["ok"])
        self.assertTrue(contract.record_save(True)["ok"])
        self.assertTrue(contract.readback(saved_after(contract.plan))["ok"])
        done = contract.release_locks({path: True for path in C.LOCK_PATHS})
        self.assertTrue(done["ok"])
        self.assertEqual(done["outcome"], "WRITTEN_AND_VERIFIED")
        self.assertEqual(contract.history, ["INIT", "STARTED", "DRY_RUN_PLANNED", "LOCKED", "BACKED_UP", "WRITE_PLANNED", "SAVED", "VERIFIED", "RELEASED"])

    # --- failure paths ---
    def test_readback_mismatch_restores_then_releases(self):
        contract = self.new()
        to_backed_up(contract)
        contract.plan_write()
        contract.record_save(True)
        bad = saved_after(contract.plan)
        bad["stats"]["max_health"] = 0.0
        self.assertFalse(contract.readback(bad)["ok"])
        self.assertEqual(contract.next_step(), "record_restore")
        self.assertTrue(contract.record_restore(BEFORE)["ok"])
        done = contract.release_locks({path: True for path in C.LOCK_PATHS})
        self.assertEqual(done["outcome"], "FAILED_RESTORED")

    def test_failed_restore_and_failed_save(self):
        contract = self.new()
        to_backed_up(contract)
        contract.plan_write()
        self.assertFalse(contract.record_save(False)["ok"])
        self.assertEqual(contract.state, "RESTORE_REQUIRED")
        self.assertFalse(contract.record_restore("e" * 64)["ok"])
        self.assertEqual(contract.next_step(), "release_locks")
        self.assertEqual(contract.release_locks({path: True for path in C.LOCK_PATHS})["outcome"], "FAILED_RESTORE_NEEDS_OPERATOR")

    def test_lock_release_is_guaranteed_and_retention_is_reported(self):
        contract = self.new()
        to_backed_up(contract)
        done = contract.release_locks({C.LOCK_PATHS[0]: True})
        self.assertEqual((done["state"], done["outcome"]), ("RELEASED", "LOCK_RETAINED_NEEDS_OPERATOR"))
        self.assertIn(C.LOCK_PATHS[1], done["errors"][-1])

    # --- ordering ---
    def test_out_of_order_steps_are_refused_without_moving(self):
        contract = self.new()
        for step, args in (("plan_write", ()), ("readback", ({},)), ("record_restore", (BEFORE,)), ("release_locks", ({},)),
                           ("verify_backup", ({}, {})), ("acquire_locks", (TOKEN, {}, []))):
            with self.subTest(step):
                result = getattr(contract, step)(*args)
                self.assertFalse(result["ok"])
                self.assertEqual(contract.state, "INIT")
        self.assertTrue(contract.start(binding(), explicit_write=True)["ok"])
        self.assertFalse(contract.start(binding(), explicit_write=True)["ok"])
        self.assertEqual(contract.state, "STARTED")

    # --- purity ---
    def test_contract_module_is_pure(self):
        import ast
        tree = ast.parse((HERE / "sevarog_executor_contract.py").read_text(encoding="utf-8"))
        imports = {alias.name for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
                   for alias in node.names} | {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertEqual(imports - {None}, {"copy", "re"}, "the contract imports only copy/re (no os, pathlib, shutil, subprocess, unreal)")
        banned = {"open", "remove", "unlink", "rmdir", "rmtree", "rename", "replace", "write_text", "write_bytes", "copy", "copyfile",
                  "move", "Popen", "run", "system", "exec", "eval", "__import__"}
        called = {node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", None)
                  for node in ast.walk(tree) if isinstance(node, ast.Call)}
        self.assertEqual(called & banned, set())


if __name__ == "__main__":
    unittest.main()
