"""BK-98 (C, implementer; X-2003): synthetic tests for bind_owner_approval.py.

Synthetic mailbox text and envelopes only; no files, Unreal, assets or locks. No real owner answer to X-1991 exists.
"""
import copy
import hashlib
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("bind_owner_approval", HERE / "bind_owner_approval.py")
B = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(B)

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


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def mailbox(reply=REPLY, owner_id="O-77", sender="Owner", trailing="\n### [X-2004] Codex -> Claude, 2026-11-12 09:05\nack\n"):
    return ("### [X-1991] Codex -> Owner, 2026-11-11 14:53\nDecision needed.\n\n"
            "### [%s] %s -> Codex, 2026-11-12 09:00\n%s\n%s" % (owner_id, sender, reply, trailing))


def envelope(reply=REPLY, decisions=FULL, message_id="O-77", reply_hash=None):
    return {"schema": B.ENVELOPE.SCHEMA, "envelope_state": "OWNER_DECISION_RECORD", "production_manifest": False,
            "authoring_authorized": False, "request_reference": "X-1991",
            "owner_message": {"message_id": message_id, "sender": "Owner", "path": "Documentation/TEAM_MAILBOX.md",
                              "reply_text": reply, "reply_sha256": reply_hash or sha(reply)},
            "decisions": [{"field_path": f, "decision": d, "value": v, "quote": q} for f, d, v, q in decisions]}


def snapshot():
    return {"asset_path": B.PLANNER.ASSET_PATH, "exists": True, "file_sha256": "a" * 64,
            "stats": {"max_health": 0.0, "max_posture": 0.0, "posture_regen_delay": 0.0, "posture_regen_rate": 0.0},
            "phases": [{"phase_id": "Phase_1", "entry_health_fraction": 0.0, "speed_multiplier": 1.0, "rate_multiplier": 1.0, "attack_multiplier": 1.0}],
            "fields": []}


def write_context():
    return {"operation": "in_place_update", "mode": "write", "explicit_write": True,
            "locks": {"root_held": True, "execution_held": True, "owner_token": "0123456789abcdef0123456789abcdef"},
            "backup": {"path": "Docs/BossCombatReview/Execution/Claude/backup/DA_Boss_Sevarog_Draft.before.uasset", "sha256": "a" * 64}}


class BindingTests(unittest.TestCase):
    def refused(self, needle, raw=None, message_id="O-77", env=None):
        result = B.bind_owner_approval(mailbox() if raw is None else raw, message_id, envelope() if env is None else env)
        self.assertFalse(result["bound"])
        self.assertIsNone(result["owner_source"], "no owner_source may be derived from a refused binding")
        self.assertFalse(result["write_permitted"])
        self.assertTrue(any(needle in e for e in result["errors"]), (needle, result["errors"]))

    # --- positive ---
    def test_complete_owner_message_binds_and_derives_source_internally(self):
        result = B.bind_owner_approval(mailbox(), "O-77", envelope())
        self.assertTrue(result["bound"], result["errors"])
        self.assertTrue(result["approval_complete"])
        self.assertFalse(result["write_permitted"], "binding never authorizes writing")
        self.assertEqual(result["owner_source"], {"sender": "Owner", "message_id": "O-77", "reply_sha256": sha(REPLY),
                                                  "path": "Documentation/TEAM_MAILBOX.md"})

    def test_single_block_input_and_final_block_with_newline_bind(self):
        block = "### [O-77] Owner -> Codex, 2026-11-12 09:00\n" + REPLY + "\n"
        self.assertTrue(B.bind_owner_approval(block, "O-77", envelope())["bound"])
        self.assertTrue(B.bind_owner_approval(mailbox(trailing=""), "O-77", envelope())["bound"])

    # --- identity / body / hash ---
    def test_mismatched_ids_are_refused(self):
        self.refused("envelope names message 'O-77' but the bound block is 'O-78'", raw=mailbox(owner_id="O-78"), message_id="O-78")
        self.refused("no block with id O-79", message_id="O-79")
        self.refused("message_id must be an owner id", message_id="X-1991")

    def test_altered_body_or_hash_is_refused(self):
        self.refused("not exactly the complete owner message body", raw=mailbox(reply=REPLY.replace("1500", "1600")))
        self.refused("not exactly the complete owner message body", env=envelope(reply=REPLY.split("\n", 1)[1]))
        self.refused("does not equal the hash", env=envelope(reply_hash="0" * 64))
        padded = REPLY + "\n"
        self.refused("not exactly the complete owner message body", env=envelope(reply=padded))

    def test_duplicate_truncated_or_non_owner_blocks_are_refused(self):
        twice = mailbox() + "### [O-77] Owner -> Codex, 2026-11-12 09:10\nRevised.\n"
        self.refused("duplicate blocks with id O-77", raw=twice)
        truncated = "### [O-77] Owner -> Codex, 2026-11-12 09:00\n" + REPLY  # no final newline, no following header
        self.refused("possibly truncated", raw=truncated)
        self.refused("is from 'Codex', not Owner", raw=mailbox(sender="Codex"))
        self.refused("empty body", raw="### [O-77] Owner -> Codex, 2026-11-12 09:00\n\n### [X-2004] Codex -> Claude\nack\n")
        self.refused("raw mailbox text is required", raw=" ")

    def test_malformed_metadata_is_refused(self):
        env = envelope(); env["owner_message"]["path"] = "Docs/other.md"
        self.refused("path must be Documentation/TEAM_MAILBOX.md", env=env)
        env = envelope(); env["owner_message"] = "O-77"
        self.refused("owner_message must be an object", env=env)
        env = envelope(); env["authoring_authorized"] = True
        self.refused("envelope:", env=env)

    # --- approval completeness ---
    def test_partial_or_unresolved_approval_binds_but_is_not_complete(self):
        reply = REPLY.replace("Rate multiplier 1.0 is fine.", "Rate multiplier: undecided.")
        rows = [r if r[0] != "Phases[Phase_1].RateMultiplier" else (r[0], "UNRESOLVED", None, None) for r in FULL]
        result = B.bind_owner_approval(mailbox(reply=reply), "O-77", envelope(reply=reply, decisions=rows))
        self.assertTrue(result["bound"], result["errors"])
        self.assertFalse(result["approval_complete"])
        self.refused("partial envelope refused", env=envelope(decisions=FULL[:-1]))

    # --- planner handoff ---
    def test_planner_handoff_is_dry_run_by_default(self):
        binding = B.bind_owner_approval(mailbox(), "O-77", envelope())
        plan = B.plan_from_bound(binding, snapshot(), {"operation": "in_place_update"})
        self.assertTrue(plan["accepted"], plan["errors"])
        self.assertEqual(plan["mode"], "dry_run")
        self.assertNotIn("save_in_place", plan["steps"])
        self.assertEqual({r["source_site"] for r in plan["field_records"]}, {"O-77"})

    def test_write_needs_complete_approval_and_explicit_allow_write(self):
        binding = B.bind_owner_approval(mailbox(), "O-77", envelope())
        refused = B.plan_from_bound(binding, snapshot(), write_context())
        self.assertFalse(refused["accepted"])
        self.assertIn("allow_write=True was not given", refused["errors"][0])
        accepted = B.plan_from_bound(binding, snapshot(), write_context(), allow_write=True)
        self.assertTrue(accepted["accepted"], accepted["errors"])
        partial_reply = REPLY.replace("Rate multiplier 1.0 is fine.", "Rate multiplier: undecided.")
        partial_rows = [r if r[0] != "Phases[Phase_1].RateMultiplier"
                        else (r[0], "UNRESOLVED", None, None) for r in FULL]
        incomplete = B.bind_owner_approval(mailbox(reply=partial_reply), "O-77",
                                           envelope(reply=partial_reply, decisions=partial_rows))
        self.assertIn("X-1991 unresolved", B.plan_from_bound(incomplete, snapshot(), write_context(), allow_write=True)["errors"][0])

    def test_planner_handoff_refuses_unbound_or_forged_bindings(self):
        self.assertFalse(B.plan_from_bound(None, snapshot(), {})["accepted"])
        forged = {"bound": True, "approval_complete": True, "envelope_result": {"valid": True},
                  "owner_source": {"sender": "Owner", "message_id": "O-1", "reply_sha256": "a" * 64,
                                   "path": "Documentation/TEAM_MAILBOX.md"}}
        self.assertFalse(B.plan_from_bound(forged, snapshot(), {})["accepted"])
        forged_object = B._BoundApproval()  # correct nominal type, but not issued by the binder
        self.assertFalse(B.plan_from_bound(forged_object, snapshot(), {})["accepted"])
        binding = B.bind_owner_approval(mailbox(), "O-77", envelope())
        self.assertFalse(hasattr(binding, "__setitem__"))
        self.assertFalse(B.plan_from_bound(dict(binding, approval_complete=False), snapshot(), {})["accepted"])
        exposed_source = binding["owner_source"]
        exposed_source["message_id"] = "O-999"
        plan = B.plan_from_bound(binding, snapshot(), {"operation": "in_place_update"})
        self.assertTrue(plan["accepted"], plan["errors"])
        self.assertEqual({r["source_site"] for r in plan["field_records"]}, {"O-77"})

    # --- contract ---
    def test_adapter_is_pure(self):
        source = (HERE / "bind_owner_approval.py").read_text(encoding="utf-8")
        for forbidden in ("import unreal", "open(", "write_text", "write_bytes", "read_text", "subprocess", "ENGINE_LOCK", "unlink"):
            self.assertNotIn(forbidden, source)
        import inspect
        # The source is derived internally: neither entry point accepts a caller-supplied owner_source.
        self.assertEqual(list(inspect.signature(B.bind_owner_approval).parameters), ["raw_text", "message_id", "envelope"])
        self.assertEqual(list(inspect.signature(B.plan_from_bound).parameters), ["binding", "snapshot", "context", "allow_write"])


if __name__ == "__main__":
    unittest.main()
