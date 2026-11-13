"""BK-88 (C, implementer; X-1999): synthetic tests for validate_owner_approval_envelope.py.

Synthetic replies and temp files only. No real owner answer to X-1991 exists; nothing here approves project data.
"""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("validate_owner_approval_envelope", HERE / "validate_owner_approval_envelope.py")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)

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


def envelope(reply=REPLY, decisions=FULL, message_id="O-77", sender="Owner"):
    return {
        "schema": V.SCHEMA, "envelope_state": "OWNER_DECISION_RECORD", "production_manifest": False,
        "authoring_authorized": False, "request_reference": "X-1991",
        "owner_message": {"message_id": message_id, "sender": sender, "path": "Documentation/TEAM_MAILBOX.md",
                          "reply_text": reply, "reply_sha256": hashlib.sha256(reply.encode("utf-8")).hexdigest()},
        "decisions": [{"field_path": f, "decision": d, "value": v, "quote": q} for f, d, v, q in decisions],
    }


def replace(field, **change):
    rows = []
    for f, d, v, q in FULL:
        if f == field:
            d, v, q = change.get("decision", d), change.get("value", v), change.get("quote", q)
        rows.append((f, d, v, q))
    return rows


class EnvelopeTests(unittest.TestCase):
    def assertRefused(self, env, needle, **kwargs):
        result = V.validate(env, **kwargs)
        self.assertFalse(result["valid"])
        self.assertEqual(result["approved_for_review"], [], "an invalid envelope must not list approvals")
        self.assertTrue(any(needle in e for e in result["errors"]), (needle, result["errors"]))

    # --- positive ---
    def test_full_explicit_decisions_are_valid_and_listed_for_review(self):
        result = V.validate(envelope())
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(len(result["approved_for_review"]), 9)
        self.assertEqual((result["rejected"], result["unresolved"]), ([], []))

    def test_unanswered_field_stays_unresolved_and_is_not_inferred(self):
        reply = REPLY.replace("Rate multiplier 1.0 is fine.", "Rate multiplier: not sure yet.")
        result = V.validate(envelope(reply=reply, decisions=replace("Phases[Phase_1].RateMultiplier", decision="UNRESOLVED", value=None, quote=None)))
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["unresolved"], ["Phases[Phase_1].RateMultiplier"])
        self.assertNotIn("Phases[Phase_1].RateMultiplier", [a["field_path"] for a in result["approved_for_review"]])

    def test_rejected_candidate_is_recorded(self):
        reply = REPLY.replace("Health 1500 yes.", "No, health 1500 is too high.")
        result = V.validate(envelope(reply=reply, decisions=replace("Stats.MaxHealth", decision="REJECT", value=None, quote="No, health 1500 is too high.")))
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["rejected"], ["Stats.MaxHealth"])

    # --- partial / duplicate / extra ---
    def test_partial_duplicate_and_extra_decisions_are_refused(self):
        self.assertRefused(envelope(decisions=FULL[:-1]), "partial envelope refused")
        self.assertRefused(envelope(decisions=FULL + [FULL[0]]), "duplicate decision refused")
        self.assertRefused(envelope(decisions=FULL + [("Owner.Approval", "APPROVE_VALUE", 1.0, "Health 1500 yes")]), "extra/unknown field refused")

    def test_unresolved_with_a_value_or_quote_is_refused(self):
        self.assertRefused(envelope(decisions=replace("Stats.MaxHealth", decision="UNRESOLVED", value=1500.0, quote=None)), "never infer")
        self.assertRefused(envelope(decisions=replace("Stats.MaxHealth", decision="UNRESOLVED", value=None, quote="Health 1500 yes")), "never infer")

    # --- ambiguous / conflicting ---
    def test_ambiguous_selection_cannot_approve(self):
        reply = REPLY.replace("Regen delay 4 seconds.", "Regen delay 4 or 6 seconds.")
        self.assertRefused(envelope(reply=reply, decisions=replace("Stats.PostureRegenDelay", quote="Regen delay 4 or 6 seconds.")), "ambiguous quote")
        reply = REPLY.replace("Threshold 0.6 yes.", "Threshold 0.6?")
        self.assertRefused(envelope(reply=reply, decisions=replace("Phases[Phase_1].EntryHealthFraction", quote="Threshold 0.6?")), "ambiguous quote")
        reply = REPLY.replace("Health 1500 yes.", "Health 1500 if signed off later.")
        self.assertRefused(envelope(reply=reply, decisions=replace("Stats.MaxHealth", quote="Health 1500 if signed off later.")), "ambiguous quote")

    def test_quote_with_several_numbers_is_refused(self):
        reply = REPLY + "\nRegen delay 4 then 5."
        self.assertRefused(envelope(reply=reply, decisions=replace("Stats.PostureRegenDelay", quote="Regen delay 4 then 5.")), "several numbers")

    def test_conflicting_or_mislabelled_selections_are_refused(self):
        reply = REPLY.replace("Health 1500 yes.", "Health 1500 no.")
        self.assertRefused(envelope(reply=reply, decisions=replace("Stats.MaxHealth", quote="Health 1500 no.")), "conflicting approval")
        self.assertRefused(envelope(decisions=replace("Stats.PostureRegenDelay", decision="APPROVE_CANDIDATE")), "differs from the X-1991 candidate")
        self.assertRefused(envelope(decisions=replace("Stats.MaxHealth", decision="APPROVE_VALUE")), "equals the candidate")
        self.assertRefused(envelope(decisions=replace("Stats.MaxHealth", value=1600.0)), "does not appear in the quote")
        self.assertRefused(envelope(decisions=replace("Stats.MaxHealth", quote="Posture 100 yes, poise maps to posture.")), "does not name the field")
        reply = REPLY.replace("Health 1500 yes.", "Unhealthy 1500 yes.")
        self.assertRefused(envelope(reply=reply, decisions=replace("Stats.MaxHealth", quote="Unhealthy 1500 yes.")), "does not name the field")

    def test_reject_rules(self):
        self.assertRefused(envelope(decisions=replace("Stats.MaxHealth", decision="REJECT", value=1500.0)), "REJECT must have value null")
        self.assertRefused(envelope(decisions=replace("Stats.MaxHealth", decision="REJECT", value=None)), "no rejection word")

    # --- citation integrity / sender ---
    def test_tampered_reply_or_quote_not_in_reply_is_refused(self):
        env = envelope(); env["owner_message"]["reply_text"] += " Also health 9000."
        self.assertRefused(env, "does not match reply_text")
        self.assertRefused(envelope(decisions=replace("Stats.MaxHealth", quote="Health 1500 approved")), "complete non-empty reply line")

    def test_wrong_sender_or_reference_is_refused(self):
        self.assertRefused(envelope(sender="Codex"), "sender must be exactly 'Owner'")
        for bad_id in ("X-1991", "C-1309", "A-842", "O-", "owner"):
            with self.subTest(bad_id):
                self.assertRefused(envelope(message_id=bad_id), "message_id must be an owner id")
        env = envelope(); env["request_reference"] = "X-1990"
        self.assertRefused(env, "request_reference must be X-1991")
        env = envelope(); env["owner_message"]["path"] = "Documentation/fabricated-owner-reply.md"
        self.assertRefused(env, "path must be Documentation/TEAM_MAILBOX.md")

    # --- ranges / non-finite ---
    def test_native_ranges_and_nonfinite_values_are_refused(self):
        cases = [
            ("Phases[Phase_1].EntryHealthFraction", 1.2, "Threshold 1.2 yes", "outside the native range"),
            ("Phases[Phase_1].EntryHealthFraction", 0.0, "Threshold 0 yes", "outside the native range"),
            ("Stats.MaxHealth", 1.0, "Health 1 yes", "outside the native range"),
            ("Stats.PostureRegenDelay", -2.0, "Regen delay -2 seconds", "outside the native range"),
            ("Phases[Phase_1].SpeedMultiplier", 0.0, "Speed multiplier 0", "outside the native range"),
        ]
        for field, value, quote, needle in cases:
            with self.subTest(field=field, value=value):
                decision = "APPROVE_VALUE"
                line = quote + "."
                self.assertRefused(envelope(reply=REPLY + "\n" + line, decisions=replace(field, decision=decision, value=value, quote=line)), needle)
        for bad in (float("nan"), float("inf"), True, "1500"):
            with self.subTest(bad=bad):
                self.assertRefused(envelope(decisions=replace("Stats.MaxHealth", value=bad)), "finite number")

    def test_zero_regen_delay_is_inside_the_native_range(self):
        reply = REPLY.replace("Regen delay 4 seconds.", "Regen delay 0 seconds.")
        result = V.validate(envelope(reply=reply, decisions=replace("Stats.PostureRegenDelay", value=0.0, quote="Regen delay 0 seconds.")))
        self.assertTrue(result["valid"], result["errors"])

    # --- flags / schema ---
    def test_envelope_never_claims_manifest_or_authorization(self):
        for key, value, needle in (("production_manifest", True, "never a production manifest"),
                                   ("authoring_authorized", True, "never authorizes authoring"),
                                   ("envelope_state", "APPROVED", "OWNER_DECISION_RECORD"),
                                   ("schema", "other/v1", "schema must be")):
            with self.subTest(key):
                env = envelope(); env[key] = value
                self.assertRefused(env, needle)
        env = envelope(); env["approved"] = True
        self.assertRefused(env, "unknown top-level keys refused")

    # --- CLI strict JSON ---
    def test_cli_refuses_duplicate_keys_and_nonfinite_constants(self):
        good = json.dumps(envelope())
        dup = good.replace('"production_manifest": false', '"production_manifest": true, "production_manifest": false', 1)
        nan = good.replace('"value": 1500.0', '"value": NaN', 1)
        with tempfile.TemporaryDirectory() as tmp:
            for name, text, code in (("good.json", good, 0), ("dup.json", dup, 1), ("nan.json", nan, 1)):
                path = Path(tmp) / name
                path.write_text(text, encoding="utf-8")
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(V.main([str(path)]), code, name)

    # --- source verification ---
    def test_verify_source_requires_the_reply_under_the_owner_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Documentation").mkdir()
            mailbox = root / "Documentation/TEAM_MAILBOX.md"
            mailbox.write_text("### [X-1991] Codex -> Owner, 2026-11-11 14:53\nquestion\n\n### [O-77] Owner -> Codex, 2026-11-12 09:00\n"
                               + REPLY + "\n\n### [X-2001] Codex -> Claude, 2026-11-12 09:05\nack\n", encoding="utf-8")
            self.assertTrue(V.validate(envelope(), root=root, verify_source=True)["valid"])
            self.assertRefused(envelope(message_id="O-78"), "no '### [O-78] Owner", root=root, verify_source=True)
            mailbox.write_text("### [O-77] Owner -> Codex, 2026-11-12 09:00\nsomething else\n\n### [X-2001] Codex -> Claude\n" + REPLY + "\n", encoding="utf-8")
            self.assertRefused(envelope(), "does not exactly match the complete owner message", root=root, verify_source=True)

    def test_quote_must_be_a_complete_line_and_source_reply_must_be_complete(self):
        self.assertRefused(envelope(decisions=replace("Stats.MaxHealth", quote="Health 1500")), "complete non-empty reply line")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / "Documentation").mkdir()
            mailbox = root / "Documentation/TEAM_MAILBOX.md"
            mailbox.write_text("### [O-77] Owner -> Codex\n" + REPLY + "\nMore context: reject the health value.\n", encoding="utf-8")
            self.assertRefused(envelope(), "does not exactly match the complete owner message", root=root, verify_source=True)

    def test_malformed_unhashable_decision_field_fails_closed(self):
        env = envelope(); env["decisions"][0]["field_path"] = ["Stats", "MaxHealth"]
        result = V.validate(env)
        self.assertFalse(result["valid"])
        self.assertEqual(result["approved_for_review"], [])
        self.assertTrue(any("extra/unknown field" in error for error in result["errors"]))

    def test_source_symlink_cannot_escape_selected_root(self):
        with tempfile.TemporaryDirectory() as root_tmp, tempfile.TemporaryDirectory() as outside_tmp:
            root, outside = Path(root_tmp), Path(outside_tmp)
            (root / "Documentation").mkdir()
            outside_mailbox = outside / "mail.txt"
            outside_mailbox.write_text("### [O-77] Owner -> Codex\n" + REPLY + "\n", encoding="utf-8")
            link = root / "Documentation/TEAM_MAILBOX.md"
            try:
                os.symlink(outside_mailbox, link)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable")
            result = V.validate(envelope(), root=root, verify_source=True)
            self.assertFalse(result["valid"])
            self.assertTrue(any("outside the repository root" in error for error in result["errors"]))

    # --- output contract ---
    def test_output_is_only_a_validation_result(self):
        result = V.validate(envelope())
        self.assertEqual(set(result), {"valid", "errors", "approved_for_review", "rejected", "unresolved"})
        source = (HERE / "validate_owner_approval_envelope.py").read_text(encoding="utf-8")
        for forbidden in ("write_text", "write_bytes", "open(", "subprocess", "import unreal", "unlink", "mkdir", "dump("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
