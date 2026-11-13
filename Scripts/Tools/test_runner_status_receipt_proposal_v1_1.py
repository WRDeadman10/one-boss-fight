"""BK-171..175 (C, implementer; X-2034): tests for the PROPOSED runner status receipt v1.1
(runner_status_receipt_proposal_v1_1.py). v1 and its tests are unchanged (Antigravity is reviewing them).

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
SPEC = importlib.util.spec_from_file_location("runner_status_receipt_proposal_v1_1", HERE / "runner_status_receipt_proposal_v1_1.py")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)
TOKEN = "0123456789abcdef0123456789abcdef"
EVIDENCE = "Docs/BossCombatReview/Execution/Codex/BK_X/Run_20261111_120000_" + TOKEN


def process(role, pid, start, finish, termination="exited", exit_code=0, fresh=True):
    return {"role": role, "pid": pid, "started_utc": start, "finished_utc": finish, "termination": termination,
            "exit_code": exit_code if termination == "exited" else None,
            "log": {"path": EVIDENCE + "/" + role + ".log", "sha256": "a" * 64, "written_after_start": fresh}}


def receipt(outcome="PASS"):
    r = {
        "schema": V.SCHEMA,
        "runner": {"script": "Scripts/Editor/run_bk_x_locked_build.ps1", "command_id": "BK_X.locked-build-suite"},
        "run": {"run_token": TOKEN, "started_utc": "2026-11-11T12:00:00Z", "finished_utc": "2026-11-11T12:10:00Z",
                "evidence_dir": EVIDENCE},
        "lock": {"token": TOKEN, "policy": "C-1155", "party": "X", "created": list(V.LOCK_PATHS),
                 "released": list(V.LOCK_PATHS), "retained": []},
        "processes": [process("build", 4101, "2026-11-11T12:00:10Z", "2026-11-11T12:05:00Z"),
                      process("suite", 4102, "2026-11-11T12:05:10.5Z", "2026-11-11T12:09:00.1234567Z")],
        "fields": [{"key": "BUILD_EXIT", "kind": "measured", "value": 0, "source": "build"},
                   {"key": "SUITE_PASSED", "kind": "measured", "value": 506, "source": "suite"},
                   {"key": "NO_ASSETS", "kind": "unmeasured", "value": True, "source": None}],
        "pass_claims": ["BUILD_EXIT", "SUITE_PASSED"],
        "outcome": outcome, "failure": None, "needs_operator": False,
    }
    if outcome != "PASS":
        r["failure"] = {"stage": "full suite", "message": "SUITE_FAILED=3"}
        r["processes"][1]["exit_code"] = 1
        r["pass_claims"] = []
    return r


def errors(r, required=()):
    return V.validate_receipt(r, required)["errors"]


def valid(r, required=()):
    return V.validate_receipt(r, required)["valid"]


class Baseline(unittest.TestCase):
    def test_valid_forms(self):
        self.assertEqual(errors(receipt()), [])
        self.assertEqual(errors(receipt("FAIL")), [])
        r = receipt("INCOMPLETE")
        r["lock"].update(released=[V.LOCK_PATHS[0]], retained=[V.LOCK_PATHS[1]])
        r["needs_operator"] = True
        self.assertEqual(errors(r), [])
        r = receipt(); r["processes"][1].update(termination="killed_marker", exit_code=None)
        self.assertEqual(errors(r), [])

    def test_schema_is_v1_1_and_v1_receipts_are_refused(self):
        self.assertEqual(V.SCHEMA, "onebossfight.runner-status-receipt/v1.1")
        r = receipt(); r["schema"] = "onebossfight.runner-status-receipt/v1"
        self.assertFalse(valid(r))
        r = receipt(); del r["pass_claims"]
        self.assertFalse(valid(r))


class Bk171CalendarTimestamps(unittest.TestCase):
    def test_parser(self):
        accepted = ("2026-11-11T12:00:00Z", "2028-02-29T00:00:00Z", "2026-11-11T12:00:00.1234567Z", "2026-12-31T23:59:59.9Z")
        refused = ("2026-02-30T12:00:00Z", "2027-02-29T00:00:00Z", "2026-11-11T24:00:00Z", "2026-11-11T12:60:00Z",
                   "2026-12-31T23:59:60Z", "2026-13-01T00:00:00Z", "2026-11-11T12:00:00.12345678Z",
                   "2026-11-11T12:00:00+00:00", "2026-11-11 12:00:00Z", "2026-11-11T12:00:00z", "", None, 20261111, [])
        for value in accepted:
            with self.subTest(accepted=value):
                self.assertIsNotNone(V.parse_utc(value))
        for value in refused:
            with self.subTest(refused=value):
                self.assertIsNone(V.parse_utc(value))

    def test_ordering_uses_parsed_times_not_strings(self):
        """'...12:05:10.5Z' sorts BEFORE '...12:05:10Z' as a string ('.' < 'Z') but is later in time; v1.1 compares
        parsed values, so a process starting at 12:05:10.5 after a run start of 12:05:10 is inside the window."""
        self.assertLess("2026-11-11T12:05:10.5Z", "2026-11-11T12:05:10Z")  # the string trap
        r = receipt(); r["run"]["started_utc"] = "2026-11-11T12:05:10Z"
        r["processes"] = r["processes"][1:]; r["fields"] = r["fields"][1:]; r["pass_claims"] = ["SUITE_PASSED"]
        self.assertEqual(errors(r), [])
        r["processes"][0]["started_utc"] = "2026-11-11T12:05:09.9999999Z"
        self.assertIn("processes[0] must start and finish inside the run window", errors(r))
        self.assertLess(V.parse_utc("2026-11-11T12:00:00Z"), V.parse_utc("2026-11-11T12:00:00.0000001Z"))

    def test_calendar_invalid_times_are_refused_everywhere(self):
        for label, change in (("run start", lambda r: r["run"].update(started_utc="2026-02-30T12:00:00Z")),
                              ("run finish", lambda r: r["run"].update(finished_utc="2026-11-11T24:00:00Z")),
                              ("process start", lambda r: r["processes"][0].update(started_utc="2026-11-31T12:00:10Z")),
                              ("process finish", lambda r: r["processes"][0].update(finished_utc="2026-11-11T12:05:60Z"))):
            with self.subTest(label):
                r = receipt(); change(r)
                self.assertFalse(valid(r))


class Bk172PassClaims(unittest.TestCase):
    def test_pass_requires_declared_measured_claims(self):
        for label, claims, needle in ((("empty"), [], "PASS requires a non-empty list of unique pass_claims"),
                                      ("missing key", None, "PASS requires a non-empty list of unique pass_claims"),
                                      ("not a list", "BUILD_EXIT", "PASS requires a non-empty list of unique pass_claims"),
                                      ("repeated", ["BUILD_EXIT", "BUILD_EXIT"], "PASS requires a non-empty list of unique pass_claims"),
                                      ("unmeasured claim", ["BUILD_EXIT", "NO_ASSETS"], "PASS requires measured fields: NO_ASSETS"),
                                      ("absent claim", ["BUILD_EXIT", "SAVED_COUNT"], "PASS requires measured fields: SAVED_COUNT")):
            with self.subTest(label):
                r = receipt(); r["pass_claims"] = claims
                self.assertIn(needle, errors(r))

    def test_caller_required_keys_add_to_the_declared_set(self):
        self.assertTrue(valid(receipt(), required=("SUITE_PASSED",)))
        self.assertIn("PASS requires measured fields: NO_ASSETS", errors(receipt(), required=("NO_ASSETS",)))

    def test_non_pass_receipts_may_have_empty_claims_but_must_be_a_list(self):
        self.assertTrue(valid(receipt("FAIL")))
        r = receipt("FAIL"); r["pass_claims"] = None
        self.assertIn("pass_claims must be a list of keys", errors(r))


class Bk173Identities(unittest.TestCase):
    def test_duplicate_pid_role_and_log_are_refused(self):
        r = receipt(); r["processes"][1]["pid"] = 4101
        self.assertIn("processes[1].pid 4101 is already used by another process in this run", errors(r))
        r = receipt(); r["processes"][1]["log"]["path"] = r["processes"][0]["log"]["path"]
        self.assertIn("processes[1].log.path is shared with another process", errors(r))
        r = receipt(); r["processes"][1]["role"] = "build"
        self.assertTrue(any("role 'build' is repeated" in e for e in errors(r)))

    def test_measured_source_must_be_a_started_process(self):
        r = receipt("FAIL")
        r["processes"][1] = {"role": "suite", "pid": None, "started_utc": None, "finished_utc": None,
                             "termination": "not_started", "exit_code": None, "log": None}
        self.assertIn("fields[1] is measured from a process that never started", errors(r))

    def test_not_started_processes_do_not_consume_pids(self):
        r = receipt("FAIL")
        r["processes"].append({"role": "pie", "pid": None, "started_utc": None, "finished_utc": None,
                               "termination": "not_started", "exit_code": None, "log": None})
        self.assertEqual(errors(r), [])


class Bk174Contradictions(unittest.TestCase):
    def test_contradictory_terminal_process_lock_combinations(self):
        cases = []
        r = receipt(); r["processes"][0]["exit_code"] = 1; cases.append(("PASS with a failed process", r))
        r = receipt(); r["processes"][1].update(termination="killed_timeout", exit_code=None); cases.append(("PASS after timeout kill", r))
        r = receipt(); r["processes"][1].update(termination="killed_marker", exit_code=None)
        r["processes"][1]["log"]["written_after_start"] = False; cases.append(("PASS after a marker kill on a stale log", r))
        r = receipt("FAIL"); r["processes"][1].update(termination="killed_marker", exit_code=None, log=None); cases.append(("marker kill with no log", r))
        r = receipt(); r["fields"] = r["fields"][:1] + r["fields"][2:]; r["pass_claims"] = ["BUILD_EXIT"]
        r["processes"][1]["log"]["written_after_start"] = False; cases.append(("PASS with an unused stale log", r))
        r = receipt(); r["lock"].update(released=[V.LOCK_PATHS[0]], retained=[V.LOCK_PATHS[1]]); r["needs_operator"] = True
        cases.append(("PASS with a retained lock", r))
        r = receipt(); r["needs_operator"] = True; cases.append(("operator flag on a clean PASS", r))
        r = receipt(); r["failure"] = {"stage": "x", "message": "y"}; cases.append(("PASS with a failure record", r))
        r = receipt("INCOMPLETE"); r["failure"] = None; cases.append(("INCOMPLETE without a failure record", r))
        r = receipt(); r["processes"][0].update(termination="exited", exit_code=None); cases.append(("exited without exit code", r))
        r = receipt(); r["processes"][0]["exit_code"] = True; cases.append(("exit code as a boolean", r))
        for label, r in cases:
            with self.subTest(label):
                self.assertFalse(valid(r), label)

    def test_contradiction_messages_are_specific(self):
        r = receipt(); r["lock"].update(released=[V.LOCK_PATHS[0]], retained=[V.LOCK_PATHS[1]]); r["needs_operator"] = True
        self.assertIn("PASS is impossible while a lock is retained; report INCOMPLETE with needs_operator", errors(r))
        r = receipt(); r["processes"][1].update(termination="killed_marker", exit_code=None, log=None)
        self.assertIn("processes[1] was killed on a marker, so its log must exist and be proven fresh", errors(r))


class FailClosed(unittest.TestCase):
    def test_every_key_with_bad_values_is_invalid_not_an_exception(self):
        bad_values = (None, [], {}, "", "x", 0, -1, True, 1.5, math.nan, [None], {"k": []}, "2026-02-30T12:00:00Z")
        base = receipt()
        paths = [((), k) for k in base] + [(("run",), k) for k in base["run"]] + [(("lock",), k) for k in base["lock"]] \
            + [(("processes", 1), k) for k in base["processes"][1]] + [(("processes", 1, "log"), k) for k in base["processes"][1]["log"]] \
            + [(("fields", 1), k) for k in base["fields"][1]]
        checked, still_valid = 0, []
        for parents, key in paths:
            for value in bad_values:
                r = copy.deepcopy(base)
                parent = r
                for p in parents:
                    parent = parent[p]
                if type(parent[key]) is type(value) and parent[key] == value:
                    continue
                parent[key] = copy.deepcopy(value)
                checked += 1
                try:
                    verdict = V.validate_receipt(r)
                except Exception as exc:  # noqa: BLE001 - "never raises" is the property under test
                    self.fail("%s.%s=%r raised %s: %s" % (parents, key, value, type(exc).__name__, exc))
                if verdict["valid"]:
                    still_valid.append((parents, key, repr(value)))
        self.assertGreater(checked, 400)
        self.assertEqual(sorted(still_valid), sorted(ALLOWED_STILL_VALID))

    def test_module_is_pure(self):
        tree = ast.parse((HERE / "runner_status_receipt_proposal_v1_1.py").read_text(encoding="utf-8"))
        imports = {a.name for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) for a in n.names}
        self.assertEqual(imports, {"json", "math", "re", "datetime", "timezone"})
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        self.assertEqual(names & {"open", "__file__", "exec", "eval", "__import__", "now", "utcnow"}, set())


# Mutations of the PASS fixture that legitimately stay valid (any typed scalar measured value; a sha256 that is null).
ALLOWED_STILL_VALID = [
    (("fields", 1), "value", "-1"), (("fields", 1), "value", "0"), (("fields", 1), "value", "''"),
    (("fields", 1), "value", "'x'"), (("fields", 1), "value", "True"), (("fields", 1), "value", "'2026-02-30T12:00:00Z'"),
    (("processes", 1, "log"), "sha256", "None"),
]


if __name__ == "__main__":
    unittest.main()
