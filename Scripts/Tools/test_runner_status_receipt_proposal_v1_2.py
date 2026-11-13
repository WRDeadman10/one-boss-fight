"""BK-176..180 (C, implementer; X-2038): tests for the PROPOSED runner status receipt v1.2
(runner_status_receipt_proposal_v1_2.py). v1 and v1.1 are unchanged (Antigravity's read-only audit continues).

Synthetic receipts only; no runner, process, lock, log, asset or Unreal access. A valid receipt is not runtime proof
or write authorization; X-1991 remains open.
"""
import ast
import copy
import importlib.util
import math
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("runner_status_receipt_proposal_v1_2", HERE / "runner_status_receipt_proposal_v1_2.py")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)
TOKEN = "0123456789abcdef0123456789abcdef"
EVIDENCE = "Docs/BossCombatReview/Execution/Codex/BK_X/Run_20261111_120000_" + TOKEN


def process(role, pid, start, finish, termination="exited", exit_code=0, fresh=True, sha="a" * 64):
    return {"role": role, "pid": pid, "started_utc": start, "finished_utc": finish, "termination": termination,
            "exit_code": exit_code if termination == "exited" else None,
            "log": {"path": EVIDENCE + "/" + role + ".log", "sha256": sha, "written_after_start": fresh}}


def receipt(outcome="PASS"):
    """PASS: clean run. FAIL: every process ended, suite exited 1, locks released. INCOMPLETE: suite timed out."""
    r = {
        "schema": V.SCHEMA,
        "runner": {"script": "Scripts/Editor/run_bk_x_locked_build.ps1", "command_id": "BK_X.locked-build-suite"},
        "run": {"run_token": TOKEN, "started_utc": "2026-11-11T12:00:00Z", "finished_utc": "2026-11-11T12:10:00Z",
                "evidence_dir": EVIDENCE},
        "lock": {"token": TOKEN, "policy": "C-1155", "party": "X", "created": list(V.LOCK_PATHS),
                 "released": list(V.LOCK_PATHS), "retained": []},
        "processes": [process("build", 4101, "2026-11-11T12:00:10Z", "2026-11-11T12:05:00Z"),
                      process("suite", 4102, "2026-11-11T12:05:10Z", "2026-11-11T12:09:00Z", sha="b" * 64)],
        "fields": [{"key": "BUILD_EXIT", "kind": "measured", "value": 0, "source": "build"},
                   {"key": "SUITE_PASSED", "kind": "measured", "value": 506, "source": "suite"},
                   {"key": "NO_ASSETS", "kind": "unmeasured", "value": True, "source": None}],
        "pass_claims": ["BUILD_EXIT", "SUITE_PASSED"],
        "outcome": outcome, "failure": None, "needs_operator": False,
    }
    if outcome == "FAIL":
        r["processes"][1]["exit_code"] = 1
        r["failure"] = {"stage": "full suite", "message": "SUITE_FAILED=3"}
        r["pass_claims"] = []
    elif outcome == "INCOMPLETE":
        r["processes"][1].update(termination="killed_timeout", exit_code=None)
        r["fields"] = [f for f in r["fields"] if f["key"] != "SUITE_PASSED"]
        r["failure"] = {"stage": "full suite", "message": "editor timeout after 30 min"}
        r["pass_claims"] = []
    return r


def errors(r, required=()):
    return V.validate_receipt(r, required)["errors"]


def valid(r, required=()):
    return V.validate_receipt(r, required)["valid"]


class Baseline(unittest.TestCase):
    def test_three_valid_outcomes_and_schema(self):
        for outcome in ("PASS", "FAIL", "INCOMPLETE"):
            with self.subTest(outcome):
                self.assertEqual(errors(receipt(outcome)), [])
        self.assertEqual(V.SCHEMA, "onebossfight.runner-status-receipt/v1.2")
        r = receipt(); r["schema"] = "onebossfight.runner-status-receipt/v1.1"
        self.assertFalse(valid(r))


class Bk176NonPassClaims(unittest.TestCase):
    def test_non_pass_claims_must_be_unique_upper_snake(self):
        needle = "pass_claims must be a list of unique UPPER_SNAKE keys"
        for outcome in ("FAIL", "INCOMPLETE"):
            for claims in (["dup", "dup"], [""], ["bad\nkey"], ["lower"], ["A B"], ["BUILD_EXIT", "BUILD_EXIT"], [1], None, "BUILD_EXIT"):
                with self.subTest(outcome=outcome, claims=claims):
                    r = receipt(outcome); r["pass_claims"] = claims
                    self.assertIn(needle, errors(r))
            r = receipt(outcome); r["pass_claims"] = ["BUILD_EXIT", "SUITE_PASSED"]
            self.assertTrue(valid(r), "non-PASS may still list (unproven) claims")


class Bk177FailVsIncomplete(unittest.TestCase):
    def test_retained_lock_forces_incomplete(self):
        r = receipt("FAIL"); r["lock"].update(released=[V.LOCK_PATHS[0]], retained=[V.LOCK_PATHS[1]]); r["needs_operator"] = True
        self.assertIn("FAIL is not allowed when a lock was retained; report INCOMPLETE", errors(r))
        r["outcome"] = "INCOMPLETE"
        self.assertTrue(valid(r))

    def test_timeout_unstarted_or_no_process_forces_incomplete(self):
        r = receipt("INCOMPLETE"); r["outcome"] = "FAIL"
        self.assertIn("FAIL is not allowed when a process timed out or never started; report INCOMPLETE", errors(r))
        r = receipt("FAIL"); r["processes"] = []; r["fields"] = r["fields"][2:]
        self.assertIn("FAIL is not allowed when no process ran; report INCOMPLETE", errors(r))
        r["outcome"] = "INCOMPLETE"
        self.assertTrue(valid(r))
        r = receipt("FAIL")
        r["processes"][1] = {"role": "suite", "pid": None, "started_utc": None, "finished_utc": None,
                             "termination": "not_started", "exit_code": None, "log": None}
        r["fields"] = [f for f in r["fields"] if f["key"] != "SUITE_PASSED"]
        self.assertTrue(any("FAIL is not allowed when a process timed out or never started" in e for e in errors(r)))

    def test_incomplete_without_a_reason_must_be_fail(self):
        r = receipt("FAIL"); r["outcome"] = "INCOMPLETE"
        self.assertTrue(any(e.startswith("INCOMPLETE requires a retained lock") for e in errors(r)))

    def test_operator_flag_tracks_retained_locks_only(self):
        r = receipt("INCOMPLETE"); r["needs_operator"] = True
        self.assertIn("needs_operator must be true exactly when a lock was retained", errors(r))


class Bk178LogFilePaths(unittest.TestCase):
    def test_log_paths_must_be_files(self):
        needle = "processes[1].log.path must be a file (name.ext, no trailing '/') inside run.evidence_dir"
        for bad in (EVIDENCE + "/suite/", EVIDENCE + "/suite", EVIDENCE + "/", EVIDENCE + "/.log", EVIDENCE + "/sub/../suite.log",
                    EVIDENCE + "/suite.log/", "Docs/BossCombatReview/Execution/Codex/OTHER/suite.log", EVIDENCE + "\\suite.log"):
            with self.subTest(bad=bad):
                r = receipt(); r["processes"][1]["log"]["path"] = bad
                self.assertIn(needle, errors(r))
        r = receipt(); r["processes"][1]["log"]["path"] = EVIDENCE + "/logs/suite_stdout.v2.txt"
        self.assertTrue(valid(r))

    def test_duplicate_log_paths_are_case_insensitive(self):
        r = receipt(); r["processes"][1]["log"]["path"] = EVIDENCE + "/BUILD.LOG"
        self.assertIn("processes[1].log.path is shared with another process (Windows paths compare case-insensitively)", errors(r))


class Bk179LogDigests(unittest.TestCase):
    def test_measured_and_pass_logs_need_a_digest(self):
        r = receipt(); r["processes"][1]["log"]["sha256"] = None
        found = errors(r)
        self.assertIn("fields[1] is measured from a log without a valid sha256", found)
        self.assertIn("PASS requires every process log to carry a valid sha256 ('suite' does not)", found)
        r = receipt("FAIL"); r["processes"][1]["log"]["sha256"] = None
        self.assertIn("fields[1] is measured from a log without a valid sha256", errors(r))

    def test_unhashed_log_allowed_only_off_pass_and_unused(self):
        r = receipt("INCOMPLETE"); r["processes"][1]["log"]["sha256"] = None  # timed-out suite, no field uses its log
        self.assertTrue(valid(r))
        r = receipt(); r["fields"] = r["fields"][:1] + r["fields"][2:]; r["pass_claims"] = ["BUILD_EXIT"]
        r["processes"][1]["log"]["sha256"] = None  # unused log, but PASS
        self.assertIn("PASS requires every process log to carry a valid sha256 ('suite' does not)", errors(r))


# Mutations that legitimately stay valid, per fixture (each reviewed against the exact values that kept it valid):
#   fields[i].value      any typed scalar (string, int, bool; null only for unmeasured/config fields)
#   fields[i].key        renamed to another valid UPPER_SNAKE key that is not a PASS claim
#   *.log.sha256         replaced by another valid 64-hex digest
#   runner.command_id, failure.stage, failure.message   any non-empty single-line string
#   fields               [] on FAIL/INCOMPLETE (a failed run may report no fields)
#   processes[i].exit_code   -1 (Windows codes can surface negative); 0 on FAIL (the run failed a marker check)
#   INCOMPLETE suite (timed out, no field uses it): log may be null, unhashed or not fresh, and its role renamed
COMMON = {"fields[0].value", "fields[1].value", "fields[2].value", "runner.command_id", "processes[1].log.sha256"}
ALLOWED_STILL_VALID = {
    "PASS": COMMON | {"fields[2].key"},
    "FAIL": COMMON | {"fields[0].key", "fields[1].key", "fields[2].key", "fields", "failure.stage", "failure.message",
                      "processes[0].exit_code", "processes[1].exit_code"},
    "INCOMPLETE": (COMMON - {"fields[2].value"}) | {"fields[0].key", "fields[1].key", "fields", "failure.stage",
                                                   "failure.message", "processes[0].exit_code", "processes[1].log",
                                                   "processes[1].log.written_after_start", "processes[1].role"},
}
BAD_VALUES = (None, [], {}, "", "x", "X_Y", 0, -1, True, False, 1.5, math.nan, [None], {"k": []},
              "2026-02-30T12:00:00Z", "a" * 64, EVIDENCE + "/dir/")


def paths(r):
    for key in r:
        yield key, (), key
    for section in ("runner", "run", "lock", "failure"):
        if isinstance(r[section], dict):
            for key in r[section]:
                yield "%s.%s" % (section, key), (section,), key
    for name in ("created", "released", "retained", ):
        for i in range(len(r["lock"][name])):
            yield "lock.%s[%d]" % (name, i), ("lock", name), i
    for i, proc in enumerate(r["processes"]):
        for key in proc:
            yield "processes[%d].%s" % (i, key), ("processes", i), key
        if isinstance(proc["log"], dict):
            for key in proc["log"]:
                yield "processes[%d].log.%s" % (i, key), ("processes", i, "log"), key
    for i, field in enumerate(r["fields"]):
        for key in field:
            yield "fields[%d].%s" % (i, key), ("fields", i), key
    for i in range(len(r["pass_claims"])):
        yield "pass_claims[%d]" % i, ("pass_claims",), i


class Bk180Fuzz(unittest.TestCase):
    def test_every_outcome_every_nested_field_fails_closed(self):
        total = 0
        for outcome in ("PASS", "FAIL", "INCOMPLETE"):
            base = receipt(outcome)
            still_valid = set()
            for label, parents, key in list(paths(base)):
                for value in BAD_VALUES:
                    r = copy.deepcopy(base)
                    parent = r
                    for p in parents:
                        parent = parent[p]
                    if type(parent[key]) is type(value) and parent[key] == value:
                        continue
                    parent[key] = copy.deepcopy(value)
                    total += 1
                    try:
                        verdict = V.validate_receipt(r)
                    except Exception as exc:  # noqa: BLE001 - "never raises" is the property under test
                        self.fail("%s %s=%r raised %s: %s" % (outcome, label, value, type(exc).__name__, exc))
                    if verdict["valid"]:
                        still_valid.add(label)
            with self.subTest(outcome):
                self.assertEqual(still_valid, ALLOWED_STILL_VALID[outcome])
        self.assertGreater(total, 2500)

    def test_module_is_pure(self):
        tree = ast.parse((HERE / "runner_status_receipt_proposal_v1_2.py").read_text(encoding="utf-8"))
        imports = {a.name for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) for a in n.names}
        self.assertEqual(imports, {"json", "math", "re", "datetime", "timezone"})
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        self.assertEqual(names & {"open", "__file__", "exec", "eval", "__import__", "now", "utcnow"}, set())


if __name__ == "__main__":
    unittest.main()
