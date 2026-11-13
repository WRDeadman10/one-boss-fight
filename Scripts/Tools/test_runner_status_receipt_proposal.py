"""BK-166/169 (C, implementer; X-2033): tests for the PROPOSED runner status receipt (runner_status_receipt_proposal.py)
and the BK-166 risk ranking computed from the earlier source censuses.

Synthetic receipts only; the census modules are imported read-only (they read runner source as text). No runner,
process, lock, log, asset or Unreal access. A valid receipt is not runtime proof or write authorization; X-1991 open.
"""
import ast
import copy
import importlib.util
import json
import math
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, HERE / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


R = load("runner_status_receipt_proposal", "runner_status_receipt_proposal.py")
TOKEN = "0123456789abcdef0123456789abcdef"
EVIDENCE = "Docs/BossCombatReview/Execution/Codex/BK_X/Run_20261111_120000_" + TOKEN


def process(role, start="2026-11-11T12:00:10Z", finish="2026-11-11T12:05:00Z", termination="exited", exit_code=0, fresh=True):
    return {"role": role, "pid": 4242, "started_utc": start, "finished_utc": finish, "termination": termination,
            "exit_code": exit_code if termination == "exited" else None,
            "log": {"path": EVIDENCE + "/" + role + ".log", "sha256": "a" * 64, "written_after_start": fresh}}


def receipt(outcome="PASS"):
    r = {
        "schema": R.SCHEMA,
        "runner": {"script": "Scripts/Editor/run_bk_x_locked_build.ps1", "command_id": "BK_X.locked-build-suite"},
        "run": {"run_token": TOKEN, "started_utc": "2026-11-11T12:00:00Z", "finished_utc": "2026-11-11T12:10:00Z",
                "evidence_dir": EVIDENCE},
        "lock": {"token": TOKEN, "policy": "C-1155", "party": "X", "created": list(R.LOCK_PATHS),
                 "released": list(R.LOCK_PATHS), "retained": []},
        "processes": [process("build"), process("suite", "2026-11-11T12:05:10Z", "2026-11-11T12:09:00Z")],
        "fields": [{"key": "BUILD_EXIT", "kind": "measured", "value": 0, "source": "build"},
                   {"key": "SUITE_PASSED", "kind": "measured", "value": 506, "source": "suite"},
                   {"key": "DD27J", "kind": "config", "value": "c" * 64, "source": None},
                   {"key": "NO_ASSETS", "kind": "unmeasured", "value": True, "source": None}],
        "outcome": outcome, "failure": None, "needs_operator": False,
    }
    if outcome != "PASS":
        r["failure"] = {"stage": "full suite", "message": "SUITE_FAILED=3"}
        r["processes"][1]["exit_code"] = 1
    return r


def errors(r, required=()):
    return R.validate_receipt(r, required)["errors"]


def valid(r, required=()):
    return R.validate_receipt(r, required)["valid"]


class ValidForms(unittest.TestCase):
    def test_pass_fail_incomplete_and_marker_kill(self):
        self.assertEqual(errors(receipt()), [])
        self.assertEqual(errors(receipt("FAIL")), [])
        r = receipt("INCOMPLETE")
        r["lock"].update(released=[R.LOCK_PATHS[0]], retained=[R.LOCK_PATHS[1]])
        r["needs_operator"] = True
        self.assertEqual(errors(r), [])
        r = receipt()
        r["processes"][1].update(termination="killed_marker", exit_code=None)  # killed after a FRESH success marker
        self.assertEqual(errors(r), [])
        r = receipt("FAIL")
        r["lock"].update(created=[R.LOCK_PATHS[0]], released=[R.LOCK_PATHS[0]])  # partial acquisition, root first
        self.assertEqual(errors(r), [])

    def test_required_measured_keys(self):
        self.assertTrue(valid(receipt(), required=("BUILD_EXIT", "SUITE_PASSED")))


class TerminalOutcome(unittest.TestCase):
    def test_contradictory_outcomes_are_refused(self):
        cases = []
        r = receipt(); r["failure"] = {"stage": "x", "message": "y"}; cases.append(("PASS with failure", r))
        r = receipt("FAIL"); r["failure"] = None; cases.append(("FAIL without failure", r))
        r = receipt(); r["processes"][1].update(termination="killed_timeout", exit_code=None); cases.append(("PASS after timeout", r))
        r = receipt(); r["processes"][0]["exit_code"] = 2; cases.append(("PASS with nonzero exit", r))
        r = receipt(); r["processes"][1] = {"role": "suite", "pid": None, "started_utc": None, "finished_utc": None,
                                            "termination": "not_started", "exit_code": None, "log": None}
        cases.append(("PASS with a process not started", r))
        r = receipt(); r["processes"] = []; r["fields"] = r["fields"][2:]; cases.append(("PASS with no process", r))
        r = receipt("FAIL"); r["failure"]["message"] = "line1\nline2"; cases.append(("multi-line failure message", r))
        r = receipt(); r["outcome"] = "pass"; cases.append(("lowercase outcome", r))
        for label, r in cases:
            with self.subTest(label):
                self.assertFalse(valid(r))

    def test_unmeasured_fields_never_satisfy_required_claims(self):
        """BK-156: a no-save claim written as a literal cannot stand in for a measured one."""
        self.assertIn("PASS requires measured fields: NO_ASSETS", errors(receipt(), required=("NO_ASSETS",)))
        r = receipt()
        r["fields"][3].update(kind="measured", source="suite")
        self.assertTrue(valid(r, required=("NO_ASSETS",)))


class IdentityAndFreshness(unittest.TestCase):
    def test_run_token_binding_is_exact(self):
        for label, change in (("uppercase lock token", lambda r: r["lock"].update(token=TOKEN.upper())),
                              ("different lock token", lambda r: r["lock"].update(token="f" * 32)),
                              ("bad run token", lambda r: r["run"].update(run_token="xyz")),
                              ("folder without token", lambda r: r["run"].update(evidence_dir="Docs/BossCombatReview/Execution/Codex/FIXED"))):
            with self.subTest(label):
                r = receipt(); change(r)
                self.assertFalse(valid(r))

    def test_stale_or_misplaced_evidence_is_refused(self):
        cases = []
        r = receipt(); r["processes"][1]["log"]["written_after_start"] = False; cases.append(("stale log", r))
        r = receipt(); r["processes"][1]["log"]["path"] = "Docs/BossCombatReview/Execution/Codex/FIXED/suite.log"; cases.append(("log outside run folder", r))
        r = receipt(); r["processes"][1]["log"] = None; cases.append(("measured with no log", r))
        r = receipt(); r["processes"][0]["started_utc"] = "2026-11-11T11:59:00Z"; cases.append(("process before run", r))
        r = receipt(); r["run"]["finished_utc"] = "2026-11-11T11:00:00Z"; cases.append(("run ends before start", r))
        r = receipt(); r["fields"][0]["source"] = "editor"; cases.append(("unknown source role", r))
        r = receipt(); r["run"]["evidence_dir"] = "C:/Temp/" + TOKEN; cases.append(("absolute folder", r))
        r = receipt(); r["run"]["evidence_dir"] = "Docs/BossCombatReview/Execution/../" + TOKEN; cases.append(("traversal", r))
        for label, r in cases:
            with self.subTest(label):
                self.assertFalse(valid(r))


class KeysAndTypes(unittest.TestCase):
    def test_duplicate_keys_are_refused(self):
        r = receipt(); r["fields"].append(dict(r["fields"][0]))
        self.assertIn("fields[4].key BUILD_EXIT is duplicated", errors(r))
        r = receipt(); r["processes"].append(process("build"))
        self.assertTrue(any("role 'build' is repeated" in e for e in errors(r)))
        text = json.dumps(receipt())[:-1] + ', "outcome": "FAIL"}'
        parsed, problems = R.parse_receipt_text(text)
        self.assertIsNone(parsed)
        self.assertIn("duplicate JSON key 'outcome'", problems[0])

    def test_ill_typed_values_are_refused(self):
        for label, change in (
                ("bool as string", lambda r: r["fields"][3].update(value="True")),
                ("float value", lambda r: r["fields"][1].update(value=506.0)),
                ("nan value", lambda r: r["fields"][1].update(value=math.nan)),
                ("list value", lambda r: r["fields"][1].update(value=[506])),
                ("multi-line value", lambda r: r["fields"][2].update(value="a\nB=1")),
                ("lowercase key", lambda r: r["fields"][2].update(key="dd27j")),
                ("pid string", lambda r: r["processes"][0].update(pid="4242")),
                ("pid bool", lambda r: r["processes"][0].update(pid=True)),
                ("exit code bool", lambda r: r["processes"][0].update(exit_code=False)),
                ("needs_operator int", lambda r: r.update(needs_operator=0)),
                ("fresh flag string", lambda r: r["processes"][0]["log"].update(written_after_start="yes")),
                ("measured null", lambda r: r["fields"][0].update(value=None)),
                ("config with source", lambda r: r["fields"][2].update(source="build"))):
            with self.subTest(label):
                r = receipt(); change(r)
                self.assertFalse(valid(r))
        self.assertTrue(valid(receipt()))  # bool True as a value is a real boolean, accepted
        for spelling in ("True", "false", " TRUE "):
            r = receipt(); r["fields"][3]["value"] = spelling
            self.assertIn("fields[3].value spells a boolean as a string; use a JSON boolean", errors(r))

    def test_strict_json_parsing(self):
        parsed, problems = R.parse_receipt_text(json.dumps(receipt()))
        self.assertEqual(problems, [])
        self.assertTrue(valid(parsed))
        for bad in ('{"a": NaN}', '{"a": Infinity}', "not json", "", 5):
            with self.subTest(bad=bad):
                self.assertIsNone(R.parse_receipt_text(bad)[0])


class LockRelease(unittest.TestCase):
    def test_per_lock_release_must_add_up(self):
        cases = []
        r = receipt(); r["lock"]["released"] = [R.LOCK_PATHS[0]]; cases.append(("a created lock unaccounted", r))
        r = receipt(); r["lock"]["retained"] = [R.LOCK_PATHS[0]]; cases.append(("released and retained", r))
        r = receipt(); r["lock"]["created"] = list(reversed(R.LOCK_PATHS)); r["lock"]["released"] = list(reversed(R.LOCK_PATHS))
        cases.append(("execution lock first", r))
        r = receipt(); r["lock"].update(created=[R.LOCK_PATHS[1]], released=[R.LOCK_PATHS[1]]); cases.append(("execution only", r))
        r = receipt(); r["lock"].update(created=[], released=[]); cases.append(("no lock", r))
        r = receipt(); r["lock"].update(released=[R.LOCK_PATHS[0]], retained=[R.LOCK_PATHS[1]]); cases.append(("retained without operator flag", r))
        r = receipt(); r["needs_operator"] = True; cases.append(("operator flag without retained lock", r))
        r = receipt(); r["lock"]["policy"] = "C-9999"; cases.append(("foreign policy", r))
        for label, r in cases:
            with self.subTest(label):
                self.assertFalse(valid(r))


class FailClosed(unittest.TestCase):
    def test_every_key_with_bad_values_is_invalid_not_an_exception(self):
        bad_values = (None, [], {}, "", "x", 0, -1, True, 1.5, math.nan, [None], {"k": []})
        checked = 0
        base = receipt("INCOMPLETE")
        paths = [((), k) for k in base] + [(("run",), k) for k in base["run"]] + [(("lock",), k) for k in base["lock"]] \
            + [(("runner",), k) for k in base["runner"]] + [(("processes", 0), k) for k in base["processes"][0]] \
            + [(("fields", 0), k) for k in base["fields"][0]] + [(("failure",), k) for k in base["failure"]]
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
                    verdict = R.validate_receipt(r)
                except Exception as exc:  # noqa: BLE001 - "never raises" is the property under test
                    self.fail("%s.%s=%r raised %s" % (parents, key, value, type(exc).__name__))
                if verdict["valid"]:
                    self.assertIn((parents, key, repr(value)), ALLOWED_STILL_VALID, (parents, key, value))
        self.assertGreater(checked, 400)

    def test_module_is_pure(self):
        tree = ast.parse((HERE / "runner_status_receipt_proposal.py").read_text(encoding="utf-8"))
        imports = {a.name for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) for a in n.names}
        self.assertEqual(imports, {"json", "math", "re"})
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        self.assertEqual(names & {"open", "__file__", "exec", "eval", "__import__"}, set())


# Mutations of the INCOMPLETE fixture that legitimately stay valid.
ALLOWED_STILL_VALID = {
    ((), "fields", "[]"),  # an INCOMPLETE run may have produced no fields
    (("fields", 0), "value", "-1"), (("fields", 0), "value", "''"), (("fields", 0), "value", "'x'"),
    (("fields", 0), "value", "True"),  # a measured value may be any typed scalar
    (("processes", 0), "exit_code", "-1"),  # Windows exit codes can surface as negative integers
    (("failure",), "stage", "'x'"), (("failure",), "message", "'x'"),
    (("runner",), "command_id", "'x'"),
}


class Bk166RiskRanking(unittest.TestCase):
    """BK-166: rank runners by stale-success likelihood x consequence, from the census modules (source-only)."""

    WEIGHTS = {"stale_terminal_status": 5, "stale_log_marker": 5, "unmeasured_no_save_claim": 3,
               "lock_release_bypass": 2, "status_without_verdict": 1, "false_lock_evidence": 1}

    def scores(self):
        io = load("io_rank", "test_bk151_155_c1155_runner_io_census.py")
        st = load("status_rank", "test_bk156_160_c1155_runner_status_census.py")
        lk = load("lock_rank", "test_bk146_150_c1155_runner_census.py")
        result = {}
        for name in st.CENSUS:
            s, i, l = st.CENSUS[name], io.CENSUS[name], lk.CENSUS[name]
            flags = {
                "stale_terminal_status": s["throw_before_status"] and not s["failure_status_in_catch"] and i["evidence"] == "fixed",
                "stale_log_marker": i["poll_deadline"] and i["evidence"] == "fixed" and not i["log_removed_before_launch"],
                "unmeasured_no_save_claim": s["no_save_claim"] and not s["save_measurement"],
                "lock_release_bypass": l["kill_before_release"] or l["unguarded_remove_before_release"],
                "status_without_verdict": s["status_then_throw"] and not s["verdict_field"],
                "false_lock_evidence": l["evidence"] != "per_lock",
            }
            result[name] = (sum(self.WEIGHTS[k] for k, v in flags.items() if v), sorted(k for k, v in flags.items() if v))
        return result

    def test_ranking_is_deterministic_and_top_risks_are_frozen(self):
        scores = self.scores()
        ranked = sorted(scores.items(), key=lambda item: (-item[1][0], item[0]))
        self.assertEqual(len(ranked), 34)
        self.assertEqual([(n, s) for n, (s, _f) in ranked[:6]], TOP_SIX)
        self.assertEqual(min(s for s, _f in scores.values()), 3)  # every runner carries at least two minor risks


TOP_SIX = [
    ("run_c1256a_live_self_test.ps1", 12), ("run_c1258a_live_self_test.ps1", 12), ("run_c1262a_live_diagnostic.ps1", 12),
    ("run_c1265b_clip_trace.ps1", 12), ("run_c1257b_locked_build.ps1", 10), ("run_c1258a_locked_build.ps1", 10),
]


if __name__ == "__main__":
    unittest.main()
