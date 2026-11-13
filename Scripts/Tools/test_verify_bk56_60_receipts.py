"""BK-69 (C, implementer; X-1993): synthetic fixtures for verify_bk56_60_receipts.py. Temp folders only; no engine or asset reads."""
import importlib.util
import io
import contextlib
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("verify_bk56_60_receipts", HERE / "verify_bk56_60_receipts.py")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)

HASH = "cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec"
SUCCESS = {
    "BUILD_EXIT": "0", "SUITE_EXIT": "0", "SUITE_STARTED": "511", "SUITE_PASSED": "511", "SUITE_FAILED": "0",
    "DD27J": HASH, "FOCUSED_CONTRACTS_EXIT": "0", "PY_COMPILE_EXIT": "0", "PIE_EXIT": "0",
    "PHASE_PREREQUISITE": "PASS", "ASSET_READBACK": "PASS", "PIE_ORDER_VALID": "True",
    "HEALTH_BASELINE_AFTER_PACK_STYLE_READY": "True", "TEST_START_APIS_ABSENT": "True",
    "CONTENT_DELTA_ONLY_EXPECTED_ASSETS": "True", "DEFERRED_PIE": "PASS", "NO_MAP_OR_OTHER_CONTENT_SAVES": "1",
}
REFUSAL_LOG = "[SevarogLive] DEFERRED_TICK_RESULT route=selected-framework-production-tick outcome=ActivationRefused reason=x test_start_calls=0 saves=0\n"

DEF = "/Game/OneBossFight/Data/Sevarog/DA_Sevarog_Framework_Encounter"
DHASH = "e9aa9641" + "0" * 56


def good_log(outcome="TimeCap activeState=Active", decisions=((1, "Move_Sevarog_Swing1_Medium"), (2, "Move_Sevarog_Swing3_Slow")),
             order=None, extra="", definition=DEF + ".DA_Sevarog_Framework_Encounter", dhash=DHASH):
    """Source-shaped deferred PIE log (marker text copied from the emitting source lines named in the verifier)."""
    markers = {
        "pack": "LogPython: [SevarogLive] PACK_STYLE_READY component=BP_CombatComponent_C style=SwordCombatStyle targetHealthWrite=after_style",
        "init": "LogTemp: Display: [FrameworkProof] selected_route_initialized route=data profile=DA_Boss_Sevarog_FrameworkProfile_Draft generation=1 targetHealthAfterPackStyle=800 testStartApis=0",
        "native": "LogTemp: Display: [EncounterActivation] deferred_selected route=data definition=%s hash=%s bossSlot=Boss playerSlot=Player generation=1" % (definition, DHASH),
        "driver": "LogPython: [SevarogLive] DEFERRED_SELECTION route=framework definition=%s hash=%s pack_isolated_before_spawn=1 framework_spawn_before_selection=1 selector_flag=1 test_start_calls=0" % (DEF, dhash),
        "spawn": "LogPython: [SevarogLive] SPAWN PASS actor=RPGFrameworkBossCharacter_0 initialPlayerDistanceCm=160.0",
        "monitor": "LogPython: [SevarogLive] DEFERRED_TICK_MONITOR route=selected-framework-production-tick selector_trigger=none test_start_calls=0 saves=0 time_cap_seconds=45",
        "result": "LogPython: [SevarogLive] DEFERRED_TICK_RESULT route=selected-framework-production-tick outcome=%s phase=Phase_1 polls=900 elapsed=45.010 saves=0" % outcome,
    }
    decision_lines = []
    for seq, card in decisions:
        decision_lines.append("LogTemp: Display: [CARD_DECISION] seq=%d attack=%d card=%s score=1.1 rangeCm=110 phase=Phase_1" % (seq, seq, card))
        decision_lines.append("LogTemp: Display: [FrameworkProof] decision attack=%d chosen=%s score=1.1 range=110 phase=Phase_1 seq=%d" % (seq, card, seq))
    names = order or ["pack", "init", "native", "driver", "decisions", "spawn", "monitor", "result"]
    body = []
    for name in names:
        body.extend(decision_lines if name == "decisions" else [markers[name]])
    return "\n".join(body) + "\n" + extra


def kv(fields):
    return "".join("%s=%s\n" % item for item in fields.items())


class Bundle:
    def __init__(self, **files):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)
        for name, body in files.items():
            if body is not None:
                (self.path / name.replace("__", ".")).write_text(body, encoding="utf-8")

    def __enter__(self):
        return self.path

    def __exit__(self, *exc):
        self.tmp.cleanup()


def success_bundle(status=None, pie="PIE_EXIT=0\n", locks="LOCKS_RELEASED=2\n", log="__good__", failure=None):
    log = good_log() if log == "__good__" else log
    return Bundle(status__txt=kv(status or SUCCESS), pie_exit__txt=pie, lock_result__txt=locks,
                  deferred_pie__log=log, failure_status__txt=failure)


def failure_bundle(stage="deferred PIE", error="Deferred production Tick PIE markers/order check failed.", pie_field="1",
                   pie_file="PIE_EXIT=1\n", locks="LOCKS_RELEASED=2\n", log=REFUSAL_LOG, raw=None):
    body = raw if raw is not None else "STAGE=%s\nERROR=%s\nPIE_EXIT=%s\n" % (stage, error, pie_field)
    return Bundle(failure_status__txt=body, pie_exit__txt=pie_file, lock_result__txt=locks, deferred_pie__log=log)


class ReceiptVerifierTests(unittest.TestCase):
    def outcome(self, bundle):
        with bundle as folder:
            return V.verify_bundle(folder)

    # --- positive ---
    def test_complete_success_receipt_proves_live_route(self):
        r = self.outcome(success_bundle())
        self.assertEqual((r["outcome"], r["live_route"], r["errors"]), ("SUCCESS", "PASS", []))

    def test_refusal_with_crash_exit_is_a_wellformed_failure_never_a_pass(self):
        r = self.outcome(failure_bundle())
        self.assertEqual((r["outcome"], r["live_route"]), ("FAILURE", "NOT_PROVEN"), r["errors"])

    def test_pre_pie_exception_without_pie_exit_is_a_wellformed_failure(self):
        r = self.outcome(failure_bundle(stage="Development build", error="Development build failed.", pie_field="", pie_file=None, log=None))
        self.assertEqual(r["outcome"], "FAILURE", r["errors"])

    def test_lock_acquisition_failure_may_release_zero_locks(self):
        r = self.outcome(failure_bundle(stage="lock acquisition", error="lock held", pie_field="", pie_file=None, locks="LOCKS_RELEASED=0\n", log=None))
        self.assertEqual(r["outcome"], "FAILURE", r["errors"])

    def test_multiline_error_message_is_accepted(self):
        raw = "STAGE=deferred PIE\nERROR=first line\nsecond line of the exception\nPIE_EXIT=1\n"
        r = self.outcome(failure_bundle(raw=raw))
        self.assertEqual(r["outcome"], "FAILURE", r["errors"])

    # --- success rules ---
    def test_success_with_crash_exit_is_rejected(self):
        status = dict(SUCCESS, PIE_EXIT="1")
        r = self.outcome(success_bundle(status=status, pie="PIE_EXIT=1\n"))
        self.assertEqual(r["outcome"], "INVALID")
        self.assertTrue(any("PIE_EXIT must be 0" in e for e in r["errors"]))

    def test_success_missing_field_and_nonzero_build_are_rejected(self):
        status = dict(SUCCESS, BUILD_EXIT="6")
        del status["DEFERRED_PIE"]
        r = self.outcome(success_bundle(status=status))
        self.assertEqual(r["outcome"], "INVALID")
        self.assertTrue(any("missing fields: DEFERRED_PIE" in e for e in r["errors"]))
        self.assertTrue(any("BUILD_EXIT must be 0" in e for e in r["errors"]))

    def test_success_suite_mismatch_and_bad_hash_and_false_flag_are_rejected(self):
        status = dict(SUCCESS, SUITE_PASSED="510", DD27J="nothex", TEST_START_APIS_ABSENT="False")
        r = self.outcome(success_bundle(status=status))
        joined = " | ".join(r["errors"])
        self.assertEqual(r["outcome"], "INVALID")
        for needle in ("SUITE_PASSED (510) must equal", "DD27J must be", "TEST_START_APIS_ABSENT must be True"):
            self.assertIn(needle, joined)

    def test_success_needs_both_locks_and_matching_pie_exit_file(self):
        self.assertEqual(self.outcome(success_bundle(locks="LOCKS_RELEASED=1\n"))["outcome"], "INVALID")
        self.assertEqual(self.outcome(success_bundle(locks=None))["outcome"], "INVALID")
        self.assertEqual(self.outcome(success_bundle(pie=None))["outcome"], "INVALID")
        self.assertEqual(self.outcome(success_bundle(pie="PIE_EXIT=3\n"))["outcome"], "INVALID")

    # --- contradictions ---
    def test_success_and_failure_together_is_invalid(self):
        r = self.outcome(success_bundle(failure="STAGE=deferred PIE\nERROR=x\nPIE_EXIT=1\n"))
        self.assertEqual(r["outcome"], "INVALID")
        self.assertIn("both status.txt", r["errors"][0])

    def test_success_next_to_refusal_marker_is_invalid(self):
        r = self.outcome(success_bundle(log=REFUSAL_LOG))
        self.assertEqual((r["outcome"], r["live_route"]), ("INVALID", "NOT_PROVEN"))

    def test_failure_cannot_claim_deferred_pie_pass(self):
        raw = "STAGE=deferred PIE\nERROR=x\nPIE_EXIT=1\nDEFERRED_PIE=PASS\n"
        r = self.outcome(failure_bundle(raw=raw))
        self.assertEqual(r["outcome"], "INVALID")
        self.assertTrue(any("DEFERRED_PIE=PASS" in e for e in r["errors"]))

    def test_neither_receipt_is_invalid(self):
        self.assertEqual(self.outcome(Bundle(lock_result__txt="LOCKS_RELEASED=2\n"))["outcome"], "INVALID")

    # --- malformed failure receipts ---
    def test_failure_rules(self):
        cases = {
            "unknown stage": failure_bundle(stage="mystery"),
            "empty error": failure_bundle(error=""),
            "non-integer pie exit": failure_bundle(pie_field="crashed"),
            "pie exit mismatch": failure_bundle(pie_field="0"),
            "pre-PIE stage with pie_exit.txt": failure_bundle(stage="Development build", pie_field="", pie_file="PIE_EXIT=0\n", log=None),
            "missing lock record": failure_bundle(locks=None),
            "lock count out of range": failure_bundle(locks="LOCKS_RELEASED=5\n"),
            "duplicate key": failure_bundle(raw="STAGE=deferred PIE\nSTAGE=deferred PIE\nERROR=x\nPIE_EXIT=1\n"),
            "missing STAGE": failure_bundle(raw="ERROR=x\nPIE_EXIT=1\n"),
        }
        for label, bundle in cases.items():
            with self.subTest(label):
                self.assertEqual(self.outcome(bundle)["outcome"], "INVALID")

    def test_malformed_success_line_is_invalid(self):
        with Bundle(status__txt=kv(SUCCESS) + "garbage without equals\n", pie_exit__txt="PIE_EXIT=0\n", lock_result__txt="LOCKS_RELEASED=2\n") as folder:
            self.assertEqual(V.verify_bundle(folder)["outcome"], "INVALID")

    # --- CLI and read-only contract ---
    def test_cli_exit_codes(self):
        for bundle, code in ((success_bundle(), 0), (failure_bundle(), 1), (failure_bundle(stage="mystery"), 2)):
            with bundle as folder, contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(V.main([str(folder), "--json"]), code)

    def test_verifier_is_read_only(self):
        source = (HERE / "verify_bk56_60_receipts.py").read_text(encoding="utf-8")
        for forbidden in ("write_text", "open(", "subprocess", "import unreal", "unlink", "remove(", "rename"):
            self.assertNotIn(forbidden, source)


class PieLogCrossCheckTests(unittest.TestCase):
    """BK-74: a purported SUCCESS must be backed by a source-shaped selected-route log."""

    def outcome(self, log):
        with success_bundle(log=log) as folder:
            return V.verify_bundle(folder)

    def assertInvalid(self, log, needle):
        r = self.outcome(log)
        self.assertEqual((r["outcome"], r["live_route"]), ("INVALID", "NOT_PROVEN"), r["errors"])
        self.assertTrue(any(needle in e for e in r["errors"]), (needle, r["errors"]))

    def test_time_cap_with_production_decisions_is_a_success(self):
        r = self.outcome(good_log())
        self.assertEqual((r["outcome"], r["live_route"], r["errors"]), ("SUCCESS", "PASS", []))

    def test_boss_defeated_with_one_decision_is_a_success(self):
        r = self.outcome(good_log(outcome="BossDefeated", decisions=((1, "Move_Sevarog_Swing1_Medium"),)))
        self.assertEqual(r["outcome"], "SUCCESS", r["errors"])

    def test_definition_path_forms_are_equivalent(self):
        self.assertEqual(self.outcome(good_log(definition=DEF))["outcome"], "SUCCESS")

    def test_missing_log_fails_closed(self):
        self.assertInvalid(None, "deferred_pie.log is missing")

    def test_time_cap_without_a_decision_is_not_a_success(self):
        self.assertInvalid(good_log(decisions=()), "no production selector decision")

    def test_result_marker_alone_is_not_a_success(self):
        self.assertInvalid("LogPython: [SevarogLive] DEFERRED_TICK_RESULT route=selected-framework-production-tick outcome=TimeCap activeState=Active phase=Phase_1 polls=1 elapsed=45 saves=0\n",
                           "missing marker: PACK_STYLE_READY")

    def test_refusal_log_is_not_a_success(self):
        self.assertInvalid(REFUSAL_LOG, "refusal marker")

    def test_each_missing_marker_is_rejected(self):
        for name, label in (("pack", "PACK_STYLE_READY"), ("init", "selected_route_initialized"), ("native", "deferred_selected"),
                            ("driver", "DEFERRED_SELECTION"), ("spawn", "SPAWN PASS"), ("monitor", "DEFERRED_TICK_MONITOR"),
                            ("result", "DEFERRED_TICK_RESULT")):
            order = [n for n in ["pack", "init", "native", "driver", "decisions", "spawn", "monitor", "result"] if n != name]
            with self.subTest(name):
                self.assertInvalid(good_log(order=order), "missing marker: " + label)

    def test_duplicate_marker_is_rejected(self):
        self.assertInvalid(good_log(order=["pack", "init", "native", "driver", "decisions", "spawn", "monitor", "monitor", "result"]),
                           "duplicate marker: DEFERRED_TICK_MONITOR")

    def test_source_order_spawn_before_activation_is_rejected(self):
        # Deferred activation is synchronous in spawn_live_boss; navigation passes on a later tick (BK-71).
        self.assertInvalid(good_log(order=["pack", "init", "spawn", "native", "driver", "decisions", "monitor", "result"]),
                           "out-of-order markers")

    def test_route_identity_hash_mismatch_is_rejected(self):
        self.assertInvalid(good_log(dhash="f" * 64), "route identity mismatch: hash")

    def test_terminal_outcomes_that_cannot_prove_success(self):
        cases = {"Succeeded": "reachable only on the test route", "Failed": "cannot prove", "ActivationRefused": "cannot prove",
                 "TimeCap activeState=NotInitialized": "activeState=Active"}
        for outcome, needle in cases.items():
            with self.subTest(outcome):
                self.assertInvalid(good_log(outcome=outcome), needle)

    def test_decision_outside_the_selected_window_or_untraced_is_rejected(self):
        early = good_log(order=["pack", "init", "decisions", "native", "driver", "spawn", "monitor", "result"])
        self.assertInvalid(early, "precedes deferred_selected")
        late = good_log(order=["pack", "init", "native", "driver", "spawn", "monitor", "result", "decisions"])
        self.assertInvalid(late, "follows the terminal result")
        untraced = good_log().replace("[FrameworkProof] decision attack=2 chosen=Move_Sevarog_Swing3_Slow", "[FrameworkProof] other attack=2")
        self.assertInvalid(untraced, "no matching [FrameworkProof] decision trace")

    def test_duplicate_decision_seq_is_rejected(self):
        self.assertInvalid(good_log(decisions=((1, "Move_Sevarog_Swing1_Medium"), (1, "Move_Sevarog_Swing1_Medium"))), "duplicate decision seq")

    def test_test_start_or_save_evidence_is_rejected(self):
        self.assertInvalid(good_log(extra="LogTemp: Display: [FrameworkProof] autonomous_test_selection move=X phase=Phase_1 generation=1 index=0 score=1\n"),
                           "test-start evidence")
        self.assertInvalid(good_log(extra="LogPython: [SevarogLive] something saves=1\n"), "save evidence")

    def test_failure_classification_is_unchanged(self):
        with failure_bundle() as folder:
            self.assertEqual(V.verify_bundle(folder)["outcome"], "FAILURE")


if __name__ == "__main__":
    unittest.main()
