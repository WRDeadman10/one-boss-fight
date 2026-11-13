"""X-2058 (C, implementer): regressions for A-854 BUG-1..5 and the whitespace-parity note in
validate_pending_definition_inputs.py and validate_owner_approval_envelope.py.

Synthetic inputs only. The CLI NaN case patches the file read (no file written); the two --verify-source cases use a
throwaway OS temp directory exactly like the existing envelope suite. No project file, lock, log, asset or Unreal is
touched; nothing here approves project data. X-1991 remains open.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, HERE / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PF = load("pending_fixtures_x2058", "test_validate_pending_definition_inputs.py")
P = PF.V
EF = load("envelope_fixtures_x2058", "test_validate_owner_approval_envelope.py")
E = EF.V


def pending_errors(manifest):
    return P.validate(manifest, P.DEFAULT_ROOT, False)["errors"]


class Bug1StrictJsonCli(unittest.TestCase):
    def run_cli(self, text):
        out = io.StringIO()
        with mock.patch.object(P.Path, "read_text", return_value=text), contextlib.redirect_stdout(out):
            code = P.main(["virtual_manifest.json"])
        return code, out.getvalue()

    def test_nan_or_infinity_anywhere_exits_nonzero(self):
        base = json.dumps(PF.manifest())
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant):
                text = base.replace('"PENDING"', '"PENDING", "definition_target": %s' % constant, 1)
                code, out = self.run_cli(text)
                self.assertEqual(code, 1)
                self.assertIn("non-finite JSON constant refused", out)

    def test_clean_manifest_still_exits_zero(self):
        code, out = self.run_cli(json.dumps(PF.manifest()))
        self.assertEqual(code, 0, out)

    def test_duplicate_keys_still_refused(self):
        code, out = self.run_cli('{"schema": "a", "schema": "b"}')
        self.assertEqual(code, 1)
        self.assertIn("duplicate JSON key", out)


class Bug2NativeRanges(unittest.TestCase):
    EDGES = {  # field -> (refused values, accepted values)
        "Stats.MaxHealth": ([-5.0, 0.0, 1.0], [1.0001, 1500.0]),
        "Stats.MaxPosture": ([-1.0, 0.0], [0.5, 100.0]),
        "Stats.PostureRegenDelay": ([-0.1], [0.0, 6.0]),
        "Stats.PostureRegenRate": ([-0.1], [0.0, 13.0]),
        "Phases[Phase_1].EntryHealthFraction": ([0.0, -0.2, 1.0001, 2.0], [0.0001, 0.6, 1.0]),
        "Phases[Phase_1].SpeedMultiplier": ([0.0, -1.0], [0.1, 1.0]),
        "Phases[Phase_1].RateMultiplier": ([0.0, -1.0], [0.1, 1.0]),
        "Phases[Phase_1].AttackMultiplier": ([0.0, -1.0], [0.1, 1.0]),
    }

    def manifest_with(self, field, value, as_candidate):
        m = PF.manifest()
        row = PF.find(m, field)
        if as_candidate:
            row.update(status="OWNER_DECISION_REQUIRED", value=None, candidate=value, candidate_note="edge")
        else:
            row.pop("candidate", None)
            row.pop("candidate_note", None)
            row.update(status="SOURCE_BACKED_AWAITING_OWNER", value=value)
        return m

    def test_valued_rows_and_candidates_obey_native_ranges(self):
        for field, (refused, accepted) in self.EDGES.items():
            for as_candidate in (False, True):
                for value in refused:
                    with self.subTest(field=field, value=value, candidate=as_candidate):
                        errs = pending_errors(self.manifest_with(field, value, as_candidate))
                        self.assertTrue(any("outside the native range" in e for e in errs), errs)
                for value in accepted:
                    with self.subTest(field=field, value=value, candidate=as_candidate, ok=True):
                        self.assertEqual(pending_errors(self.manifest_with(field, value, as_candidate)), [])

    def test_negative_max_health_reproduction(self):
        errs = pending_errors(self.manifest_with("Stats.MaxHealth", -5.0, False))
        self.assertIn("row 5 (Stats.MaxHealth): value -5.0 is outside the native range for Stats.MaxHealth",
                      [e for e in errs if "MaxHealth" in e] or errs)

    def test_phase_id_must_be_phase_1(self):
        m = PF.manifest()
        PF.find(m, "Phases[Phase_1].PhaseId")["value"] = "Phase_10"
        self.assertTrue(any("value must be Phase_1" in e for e in pending_errors(m)))

    def test_range_table_parity_with_the_envelope(self):
        for field, (low, inclusive, high) in P.NATIVE_RANGES.items():
            with self.subTest(field=field):
                kind, _candidate, e_low, e_inclusive, e_high, _aliases = E.FIELDS[field]
                self.assertEqual((kind, low, inclusive, high), ("float", e_low, e_inclusive, e_high))
        self.assertEqual(set(P.NATIVE_RANGES) | {P.PHASE_ID_FIELD}, set(E.FIELDS))


class X2062X2064MalformedRowValues(unittest.TestCase):
    """Unhashable or wrongly typed row values must give a normal invalid result, never an exception."""

    def assert_invalid(self, manifest):
        try:
            result = P.validate(manifest, P.DEFAULT_ROOT, False)
        except Exception as exc:  # noqa: BLE001 - "never raises" is the property under test
            self.fail("validate raised %s: %s" % (type(exc).__name__, exc))
        self.assertFalse(result["valid"])
        return result["errors"]

    def test_x2062_unhashable_field_path_on_float_value_and_candidate(self):
        m = PF.manifest()
        PF.find(m, "Stats.MaxHealth")["field_path"] = ["Owner", "Approval"]  # valued float row
        self.assert_invalid(m)
        m = PF.manifest()
        PF.find(m, "Phases[Phase_1].SpeedMultiplier")["field_path"] = ["Owner", "Approval"]  # candidate row
        self.assert_invalid(m)

    def test_x2064_unhashable_status(self):
        m = PF.manifest()
        PF.find(m, "Stats.MaxHealth")["status"] = ["PENDING"]
        errors = self.assert_invalid(m)
        self.assertTrue(any("status" in e and "refused" in e for e in errors), errors)

    def test_every_row_key_with_malformed_values_never_raises(self):
        bad = ([], ["x"], {}, {"k": []}, None, 1.5, True, "", "PENDING")
        for field in ("Stats.MaxHealth", "Phases[Phase_1].PhaseId", "Phases[Phase_1].SpeedMultiplier"):
            for key in list(PF.find(PF.manifest(), field)):
                for value in bad:
                    with self.subTest(field=field, key=key, value=value):
                        m = PF.manifest()
                        PF.find(m, field)[key] = value
                        try:
                            P.validate(m, P.DEFAULT_ROOT, False)
                        except Exception as exc:  # noqa: BLE001
                            self.fail("%s.%s=%r raised %s" % (field, key, value, type(exc).__name__))


class Bug3PhaseIdTokenIdentity(unittest.TestCase):
    def phase_env(self, line):
        reply = EF.REPLY.replace("Keep Phase_1 as the phase id.", line)
        return EF.envelope(reply=reply, decisions=EF.replace("Phases[Phase_1].PhaseId", quote=line))

    def test_phase_10_does_not_approve_phase_1(self):
        for line in ("Phase id: Phase_10", "Phase id: Phase 12", "Phase id: XPhase_1", "Phase id: Phase_1x"):
            with self.subTest(line=line):
                result = E.validate(self.phase_env(line))
                self.assertFalse(result["valid"])
                self.assertTrue(any("as a whole token" in e for e in result["errors"]), result["errors"])

    def test_exact_token_forms_still_approve(self):
        for line in ("Phase id: Phase_1", "Keep phase 1 as the phase id.", "Phase id is Phase_1."):
            with self.subTest(line=line):
                self.assertTrue(E.validate(self.phase_env(line))["valid"], E.validate(self.phase_env(line))["errors"])


class Bug4QuoteReuse(unittest.TestCase):
    def test_one_line_cannot_approve_two_fields(self):
        reply = EF.REPLY.replace("Regen rate 10 per second.", "Rate 1.0.").replace("Rate multiplier 1.0 is fine.", "")
        decisions = [row for row in EF.FULL if row[0] not in ("Stats.PostureRegenRate", "Phases[Phase_1].RateMultiplier")]
        decisions += [("Stats.PostureRegenRate", "APPROVE_VALUE", 1.0, "Rate 1.0."),
                      ("Phases[Phase_1].RateMultiplier", "APPROVE_CANDIDATE", 1.0, "Rate 1.0.")]
        result = E.validate(EF.envelope(reply=reply.strip(), decisions=decisions))
        self.assertFalse(result["valid"])
        self.assertEqual(result["approved_for_review"], [])
        self.assertTrue(any("one quote approves several fields" in e for e in result["errors"]), result["errors"])

    def test_distinct_lines_still_valid(self):
        self.assertTrue(E.validate(EF.envelope())["valid"])

    def test_unhashable_field_path_does_not_crash_the_reuse_check(self):
        env = EF.envelope()
        env["decisions"][0]["field_path"] = ["Stats.MaxHealth"]
        self.assertFalse(E.validate(env)["valid"])


class Bug5AndWhitespaceSourceVerification(unittest.TestCase):
    def verify(self, mailbox_text, env):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Documentation").mkdir()
            (root / "Documentation" / "TEAM_MAILBOX.md").write_text(mailbox_text, encoding="utf-8")
            return E.validate(env, root=root, verify_source=True)

    def block(self, mid="O-77"):
        return "### [%s] Owner -> Codex, 2026-11-12 09:00\n%s\n\n" % (mid, EF.REPLY)

    def test_single_owner_block_still_verifies(self):
        result = self.verify(self.block() + "### [X-2001] Codex -> Claude\nack\n", EF.envelope())
        self.assertTrue(result["valid"], result["errors"])

    def test_duplicate_owner_message_id_is_refused(self):
        text = self.block() + self.block() + "### [X-2001] Codex -> Claude\nack\n"
        result = self.verify(text, EF.envelope())
        self.assertFalse(result["valid"])
        self.assertTrue(any("duplicate owner message refused" in e for e in result["errors"]), result["errors"])

    def test_id_reused_by_a_non_owner_header_is_also_refused(self):
        text = self.block() + "### [O-77] Codex -> Owner, 2026-11-12 09:05\nforged\n\n"
        self.assertFalse(self.verify(text, EF.envelope())["valid"])

    def test_padded_reply_with_matching_hash_is_refused(self):
        padded = "  " + EF.REPLY + "\n"
        env = EF.envelope(reply=padded)
        self.assertEqual(env["owner_message"]["reply_sha256"], hashlib.sha256(padded.encode("utf-8")).hexdigest())
        result = self.verify(self.block() + "### [X-2001] Codex -> Claude\nack\n", env)
        self.assertFalse(result["valid"])
        self.assertTrue(any("no padding" in e for e in result["errors"]), result["errors"])


if __name__ == "__main__":
    unittest.main()
