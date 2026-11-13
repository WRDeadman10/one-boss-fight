"""BK-156..160 (C, implementer; X-2031): static census of status/receipt fields, success markers, terminal-status
paths and run binding in every C-1155 runner.

Source-only: every `.ps1` under Scripts/ containing `owner_token` is READ; no runner or child process is executed and
no lock, log, temp file or asset is touched. `classify_status()` is checked on synthetic runner text, then compared with
explicit tables frozen on 2026-11-11. Counts describe source text only - no runtime claims. Audit only; no production
edit; X-1991 remains open.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNERS = sorted(p for p in (ROOT / "Scripts").rglob("*.ps1")
                 if "owner_token" in p.read_text(encoding="utf-8-sig", errors="replace"))
KEY = re.compile(r"(?<![A-Z0-9_])([A-Z][A-Z0-9_]+)=(.?)")
NO_SAVE_CLAIM = (r"(?<![A-Z0-9_])(NO_ASSETS=1|NO_ASSET_SAVES=1|MAP_SAVED=0|NO_PACKAGES_SAVED=1|SAVED_ASSET_COUNT=0|"
                 r"NO_MAP_OR_OTHER_CONTENT_SAVES=1|SAVED_ASSETS=0)")
SAVE_MEASUREMENT = r"ContentAssetState|LastWriteTime|status --porcelain|SAVED_COUNT=0|saves=0|NO_SAVES|Get-ChildItem[^|\n]*Content"
VERDICT_KEYS = {"SUCCESS", "RESULT", "VERDICT", "OVERALL", "PASS", "OK"}


def _status_region(lines):
    """Lines from the status construction start to the last status write (Set-/Add-Content to a *status* file)."""
    writes = [i for i, l in enumerate(lines)
              if re.search(r"(Set|Add)-Content", l) and re.search(r"status", l, re.I) and "failure" not in l.lower()]
    if not writes:
        return None, None, ""
    end = max(writes)
    status_starts = [i for i in range(end + 1) if re.match(r"\s*\$status\s*=", lines[i])]
    result_starts = [i for i in range(end + 1) if re.match(r"\s*\$result\s*=", lines[i])]
    start = (status_starts or result_starts or [end])[-1]
    return start, end, "\n".join(lines[start:end + 1])


def classify_status(text):
    lines = text.splitlines()
    start, end, region = _status_region(lines)
    measured, literal = [], []
    for match in KEY.finditer(region):
        key, nxt = match.group(1), match.group(2)
        tail = region[match.end() - len(nxt):match.end() + 6]
        if nxt in ("$", "{") or re.match(r"'\s*\+", tail):
            measured.append(key)
        elif nxt and nxt not in ("`", "'", '"'):
            literal.append(key)
        else:
            measured.append(key)
    fin = max((i for i, l in enumerate(lines) if re.search(r"finally\s*\{\s*$", l)), default=len(lines))
    throws_after = [i for i in range(len(lines)) if end is not None and end < i < fin and re.search(r"\bthrow\b", lines[i])]
    first_throw = next((i for i, l in enumerate(lines) if re.search(r"\bthrow\b", l) and "ABORT" not in l and i > 0
                        and any("$created.Add" in x or "$createdLocks.Add" in x for x in lines[:i])), None)
    keys = set(measured) | set(literal)
    json_receipt = re.search(r"\$receipt\s*=\s*\[ordered\]@\{", text) is not None
    success_is_test_count = re.search(r"\$success\s*=\s*\(Select-String[^\n]*\)\.Count", text) is not None
    verdict_keys = keys & VERDICT_KEYS
    if success_is_test_count:
        verdict_keys.discard("SUCCESS")
    return {
        # BK-156 fields
        "status_file": end is not None or json_receipt,
        "json_receipt": json_receipt,
        "measured_keys": sorted(set(measured)),
        "literal_claims": sorted(set(k for k in literal if k != "DD27J")),
        "echoes_manifest_constant": "DD27J" in keys,
        # BK-157 markers
        "marker_checks": len(re.findall(r"-Pattern '|\.Contains\('", text)),
        "marker_mentions_run_id": re.search(r"-Pattern [^\n]*\$(token|run|runName|stamp)\b|\.Contains\([^\n]*\$(token|run)\b", text) is not None,
        # BK-158 terminal status
        "verdict_field": bool(verdict_keys) or (json_receipt and "verdict=" in text),
        "status_then_throw": bool(throws_after),
        "failure_status_in_catch": re.search(r"failure_status|receipt records the failure", text) is not None,
        "throw_before_status": first_throw is not None and end is not None and first_throw < end,
        # BK-159 binding
        "status_has_token": re.search(r"\$token", region) is not None,
        "status_has_child_pid": re.search(r"\$\w+\.Id\b", region) is not None,
        "status_has_command_id": "command_id" in region or "COMMAND" in region,
        "lock_record_has_command_id": re.search(r"command_id\s*=", text) is not None,
        "lock_record_has_pid": re.search(r"pid\s*=\s*\$PID", text) is not None,
        # BK-156 no-save claims vs any related measurement in the same script
        "no_save_claim": re.search(NO_SAVE_CLAIM, region) is not None,
        "save_measurement": re.search(SAVE_MEASUREMENT, text) is not None,
    }


CENSUS = {p.name: classify_status(p.read_text(encoding="utf-8-sig", errors="replace")) for p in RUNNERS}


def names(predicate):
    return sorted(n for n, c in CENSUS.items() if predicate(c))


IO = None


def io_census():
    """Read-only reuse of the BK-151..155 census (fixed vs per-run evidence folders)."""
    global IO
    if IO is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("io_census_bk156", Path(__file__).resolve().parent / "test_bk151_155_c1155_runner_io_census.py")
        IO = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(IO)
    return IO.CENSUS


# ---- frozen expected tables (2026-11-11) ----
VERDICT_RUNNERS = ["run_bk7_shipping_pipeline.ps1"]
FAILURE_STATUS = ["run_bk56_60_deferred_selection.ps1", "run_bk7_shipping_pipeline.ps1"]
NO_PID_IN_LOCK = ["run_c1252a_locked_validation.ps1", "run_c1253a_locked_validation.ps1",
                  "run_c1254a_transient_profile_check.ps1", "run_c1255_live_bridge_validation.ps1"]
STALE_TERMINAL_STATUS = sorted(["run_c1252a_locked_validation.ps1", "run_c1253a_locked_validation.ps1",
                                "run_c1255_live_bridge_validation.ps1", "run_c1256a_spawn_bridge_build_suite.ps1",
                                "run_c1257b_locked_build.ps1", "run_c1258a_locked_build.ps1", "run_c1262a_locked_build.ps1",
                                "run_c1269a_locked_validation.ps1", "run_c1274_area_effect_validation.ps1",
                                "run_c1274_channel_drain_validation.ps1"])
NO_SAVE_CLAIM_WITH_MEASUREMENT = sorted(["run_be_x26_x30_locked_validation.ps1", "run_bk56_60_deferred_selection.ps1",
                                         "run_c1257a_dry_run.ps1", "run_c1275a_locked_validation.ps1",
                                         "run_c1280_x26_locked_validation.ps1"])


class ClassifierSelfCheck(unittest.TestCase):
    def test_synthetic_runner(self):
        text = ("$created.Add($lock)\n& build\nif ($LASTEXITCODE -ne 0) { throw 'build failed' }\n"
                "$status = \"BUILD_EXIT=$buildExit`nSUCCESS=$ok`nNO_ASSETS=1`nDD27J=$manifest\"\n"
                "Set-Content -LiteralPath (Join-Path $evidence 'status.txt') -Value $status\n"
                "if (!$ok) { throw 'failed' }\n} finally {\n}\n")
        c = classify_status(text)
        self.assertEqual(c["literal_claims"], ["NO_ASSETS"])
        self.assertIn("BUILD_EXIT", c["measured_keys"])
        self.assertTrue(c["verdict_field"] and c["status_then_throw"] and c["throw_before_status"] and c["no_save_claim"])
        self.assertTrue(c["echoes_manifest_constant"])
        self.assertFalse(c["save_measurement"] or c["status_has_token"] or c["failure_status_in_catch"])
        bound = classify_status("$status = \"TOKEN=$token`nCHILD_PID=$($proc.Id)\"\nSet-Content $statusPath $status\n")
        self.assertTrue(bound["status_has_token"] and bound["status_has_child_pid"])
        self.assertTrue(classify_status("Set-Content (Join-Path $evidence 'failure_status.txt') $m\n")["failure_status_in_catch"])
        self.assertTrue(classify_status("if (Select-String -Path $log -Pattern \"RUN=$token\" -Quiet) { }\n")["marker_mentions_run_id"])


class Census(unittest.TestCase):
    def test_deterministic_and_complete(self):
        self.assertEqual(len(RUNNERS), 34)
        self.assertEqual(CENSUS, {p.name: classify_status(p.read_text(encoding="utf-8-sig", errors="replace")) for p in RUNNERS})
        self.assertEqual(names(lambda c: c["status_file"]), sorted(CENSUS))


class Bk156StatusFields(unittest.TestCase):
    def test_literal_claims(self):
        """29 runners write at least one status field whose value is a literal, not a measured variable (the DD27J
        manifest echo is excluded and counted separately: 25 runners)."""
        self.assertEqual(len(names(lambda c: c["literal_claims"])), 29)
        self.assertEqual(len(names(lambda c: c["echoes_manifest_constant"])), 25)
        self.assertEqual(sum(c["literal_claims"].count("NO_ASSETS") for c in CENSUS.values()), 18)

    def test_no_save_claims_without_measurement(self):
        """28 runners write a literal no-save/no-asset claim; only 5 contain any related check (content-state hash,
        save counter, or saves=0 marker). 23 assert it with nothing in the script that measures it."""
        claim = names(lambda c: c["no_save_claim"])
        self.assertEqual(len(claim), 28)
        self.assertEqual(names(lambda c: c["no_save_claim"] and c["save_measurement"]), NO_SAVE_CLAIM_WITH_MEASUREMENT)
        self.assertEqual(len(names(lambda c: c["no_save_claim"] and not c["save_measurement"])), 23)


class Bk157Markers(unittest.TestCase):
    def test_markers_are_not_correlated_with_the_run(self):
        """165 success/failure marker checks across 33 runners (bk7 uses exit codes only); none includes the run
        token or run id, so a marker cannot distinguish this run's output from an earlier run's."""
        self.assertEqual(sum(c["marker_checks"] for c in CENSUS.values()), 165)
        self.assertEqual(names(lambda c: c["marker_checks"] == 0), ["run_bk7_shipping_pipeline.ps1"])
        self.assertEqual(names(lambda c: c["marker_mentions_run_id"]), [])

    def test_markers_read_from_reused_folders(self):
        """18 marker-checking runners read logs in a FIXED evidence folder (BK-153), where an earlier run's log can
        remain if the child fails before rewriting it."""
        io = io_census()
        self.assertEqual(len(names(lambda c: c["marker_checks"] > 0)) - len(
            [n for n in names(lambda c: c["marker_checks"] > 0) if io[n]["evidence"] == "per_run"]), 18)


class Bk158TerminalStatus(unittest.TestCase):
    def test_verdict_and_failure_paths(self):
        """Only bk7 writes an overall verdict; c1252a/c1253a SUCCESS fields count passed tests. Only 2 write failure status."""
        self.assertEqual(names(lambda c: c["verdict_field"]), VERDICT_RUNNERS)
        self.assertEqual(names(lambda c: c["failure_status_in_catch"]), FAILURE_STATUS)

    def test_status_written_before_the_final_check(self):
        """32 runners write the status file and THEN may throw on a later check: none has an overall verdict, so the
        status alone does not say the run failed."""
        self.assertEqual(len(names(lambda c: c["status_then_throw"])), 32)
        self.assertEqual(len(names(lambda c: c["status_then_throw"] and not c["verdict_field"])), 32)

    def test_missing_or_stale_terminal_status(self):
        """25 runners can throw after taking locks but before writing any status, leaving no terminal record for
        that run; in 10 of them the evidence folder is FIXED, so the previous run's status file stays in place and
        reads as this run's result."""
        io = io_census()
        early = names(lambda c: c["throw_before_status"] and not c["failure_status_in_catch"])
        self.assertEqual(len(names(lambda c: c["throw_before_status"])), 25)
        stale = [n for n in early if io[n]["evidence"] == "fixed"]
        self.assertEqual(stale, STALE_TERMINAL_STATUS)


class Bk159RunBinding(unittest.TestCase):
    def test_status_is_not_bound_to_lock_or_process(self):
        """The lock record carries command_id (34) and the runner PID (30; 4 omit it), but no status file carries the
        run token, the command id or a child process id, so status, lock and launched process are not bound."""
        self.assertEqual(len(names(lambda c: c["lock_record_has_command_id"])), 34)
        self.assertEqual(names(lambda c: not c["lock_record_has_pid"]), NO_PID_IN_LOCK)
        for key in ("status_has_token", "status_has_command_id", "status_has_child_pid"):
            with self.subTest(key):
                self.assertEqual(names(lambda c, k=key: c[k]), [])


if __name__ == "__main__":
    unittest.main()
