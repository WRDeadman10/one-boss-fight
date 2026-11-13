"""BK-151..155 (C, implementer; X-2030): static census of environment, child-process, output-path and exit handling in
every C-1155 runner.

Text-only: every `.ps1` under Scripts/ containing `owner_token` is READ; no runner or child process is executed and no
lock, temp file, log or asset is touched. `classify_io()` is checked on synthetic runner text, then its per-runner
results are compared with explicit tables frozen on 2026-11-11, so any runner edit surfaces for re-review. Counts
describe source text only - no runtime claims. Audit only; no production edit; X-1991 remains open.
"""
import re
import unittest
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNERS = sorted(p for p in (ROOT / "Scripts").rglob("*.ps1")
                 if "owner_token" in p.read_text(encoding="utf-8-sig", errors="replace"))


def _has(pattern, text):
    return re.search(pattern, text, re.M) is not None


def classify_io(text):
    evidence = re.search(r"^\s*\$evidence\s*=\s*(.+)$", text, re.M)
    evidence_expr = evidence.group(1) if evidence else ""
    per_run = _has(r"yyyyMMdd_HHmmss|\$run\b|\$runName|\$stamp", evidence_expr) or (
        "$evidenceRoot" in evidence_expr and _has(r"^\s*\$runName\s*=.*yyyyMMdd_HHmmss", text))
    fixed_dir = None
    if not per_run:
        literal = re.search(r"'([^']*Execution\\Codex\\[^']+)'", evidence_expr)
        fixed_dir = literal.group(1).split("\\")[-1] if literal else None
    poll = _has(r"AddMinutes|AddSeconds", text) and _has(r"Select-String[^\n]*-Quiet|\.Contains\(\$ExpectedMarker\)", text)
    env_write = _has(r"\$env:\w+\s*=|SetEnvironmentVariable|Remove-Item Env:", text)
    env_saved = _has(r"=\s*\$env:\w+|GetEnvironmentVariable", text)
    return {
        # BK-151 environment and working directory
        "root": "param_resolved" if _has(r"^\s*param\s*\(", text) and _has(r"Resolve-Path", text) else "literal",
        "engine_literal": _has(r"'C:\\Program Files\\Epic Games\\UE_5\.5", text),
        "set_location": _has(r"^\s*Set-Location\b", text),
        "restores_location": _has(r"Pop-Location|Set-Location[^\n]*\$(old|prev|saved)", text),
        "env": "none" if not env_write else ("restores_prior" if env_saved else "clears_without_saving"),
        "tool_from_path": _has(r"Get-Command python", text),
        # BK-152 child-process construction
        "call_operator": _has(r"^\s*(\$\w+\s*=\s*)?&\s", text),
        "start_process": _has(r"Start-Process", text),
        "execcmds_embedded_quotes": _has(r"ExecCmds=\\?\"|-ExecCmds=\"", text) and _has(r"Start-Process", text),
        "caller_params": _has(r"^\s*param\s*\(", text),
        "assigns_automatic_args": _has(r"^\s*\$args\s*=", text),
        # BK-153 output paths
        "evidence": "per_run" if per_run else "fixed",
        "fixed_dir": fixed_dir,
        "evidence_exists_abort": _has(r"Test-Path[^\n]*\$evidence[^\n]*throw", text),
        "new_item_force": _has(r"New-Item[^\n]*-Force", text),
        # BK-154 timeout, cancellation, exit codes
        "unbounded_wait": _has(r"Start-Process[^\n]*-Wait\b", text),
        "poll_deadline": poll,
        "lastexitcode": _has(r"\$LASTEXITCODE", text),
        "proc_exitcode": _has(r"\$\w+\.ExitCode", text),
        "log_removed_before_launch": _has(r"Remove-Item[^\n]*\$(log|editorLog|pieLog|LogPath)\b", text),
    }


CENSUS = {p.name: classify_io(p.read_text(encoding="utf-8-sig", errors="replace")) for p in RUNNERS}


def names(predicate):
    return sorted(n for n, c in CENSUS.items() if predicate(c))


def shared_fixed_dirs():
    groups = defaultdict(list)
    for name, c in CENSUS.items():
        if c["fixed_dir"]:
            groups[c["fixed_dir"]].append(name)
    return {d: sorted(v) for d, v in groups.items() if len(v) > 1}


# ---- frozen expected tables (2026-11-11) ----
PARAM_RUNNERS = ["run_bk56_60_deferred_selection.ps1", "run_bk7_shipping_pipeline.ps1"]
SET_LOCATION = sorted(["run_be_x26_x30_locked_validation.ps1", "run_be_x31_x35_locked_build.ps1", "run_be_x36_x40_locked_build.ps1",
                       "run_bf_x01_x05_locked_build.ps1", "run_bf_x11_x15_locked_build.ps1", "run_bf_x16_x20_locked_build.ps1",
                       "run_bk2_x26_locked_validation.ps1", "run_bk56_60_deferred_selection.ps1", "run_c1280_x26_locked_validation.ps1"])
ENV_CLEARS_WITHOUT_SAVING = sorted(["run_c1252a_locked_validation.ps1", "run_c1253a_locked_validation.ps1",
                                    "run_c1254a_transient_profile_check.ps1", "run_c1256a_live_self_test.ps1", "run_c1258a_live_self_test.ps1",
                                    "run_c1262a_live_diagnostic.ps1", "run_c1265b_clip_trace.ps1"])
EMBEDDED_QUOTE_EXECCMDS = sorted(["run_bk2_x26_locked_validation.ps1", "run_bk56_60_deferred_selection.ps1",
                                  "run_c1256a_live_self_test.ps1", "run_c1257a_author.ps1", "run_c1257a_dry_run.ps1",
                                  "run_c1258a_live_self_test.ps1", "run_c1262a_live_diagnostic.ps1", "run_c1265b_clip_trace.ps1",
                                  "run_c1275a_locked_validation.ps1"])
UNBOUNDED_WAIT = sorted(["run_be_x26_x30_locked_validation.ps1", "run_c1274_s6_locked_dryrun.ps1", "run_c1280_x26_locked_validation.ps1"])
FIXED_EVIDENCE = sorted(["run_c1252a_locked_validation.ps1", "run_c1253a_locked_validation.ps1", "run_c1254a_transient_profile_check.ps1",
                         "run_c1255_live_bridge_validation.ps1", "run_c1256a_live_self_test.ps1", "run_c1256a_spawn_bridge_build_suite.ps1",
                         "run_c1257a_author.ps1", "run_c1257a_dry_run.ps1", "run_c1257b_locked_build.ps1", "run_c1258a_live_self_test.ps1",
                         "run_c1258a_locked_build.ps1", "run_c1262a_live_diagnostic.ps1", "run_c1262a_locked_build.ps1",
                         "run_c1265b_clip_trace.ps1", "run_c1269a_locked_validation.ps1", "run_c1274_area_effect_validation.ps1",
                         "run_c1274_channel_drain_validation.ps1", "run_c1274_s6_locked_dryrun.ps1"])
EXISTS_ABORT = sorted(["run_bk56_60_deferred_selection.ps1", "run_bk7_shipping_pipeline.ps1", "run_c1275a_locked_validation.ps1"])
SHARED_DIRS = {"C1256A_SPAWN_BRIDGE": ["run_c1256a_live_self_test.ps1", "run_c1256a_spawn_bridge_build_suite.ps1"],
               "C1258A_RANGE_RETRY": ["run_c1258a_live_self_test.ps1", "run_c1258a_locked_build.ps1"],
               "C1262A_SEVAROG_DIAG": ["run_c1262a_live_diagnostic.ps1", "run_c1262a_locked_build.ps1"]}
STALE_LOG_RISK = sorted(["run_c1256a_live_self_test.ps1", "run_c1257a_author.ps1", "run_c1257a_dry_run.ps1",
                         "run_c1258a_live_self_test.ps1", "run_c1262a_live_diagnostic.ps1", "run_c1265b_clip_trace.ps1"])


class ClassifierSelfCheck(unittest.TestCase):
    def test_synthetic_runners(self):
        base = ("$ErrorActionPreference = 'Stop'\n$root = 'C:\\UnrealProject\\OneBossFight'\n"
                "$engine = 'C:\\Program Files\\Epic Games\\UE_5.5\\Engine'\n")
        per_run = base + "$evidence = Join-Path $root ('Docs\\BossCombatReview\\Execution\\Codex\\X\\Run_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss'))\n"
        fixed = base + "$evidence = Join-Path $root 'Docs\\BossCombatReview\\Execution\\Codex\\FIXED_DIR'\n"
        c = classify_io(per_run + "& $tool a b\n$x = $LASTEXITCODE\n")
        self.assertEqual((c["evidence"], c["root"], c["env"], c["call_operator"], c["lastexitcode"]), ("per_run", "literal", "none", True, True))
        c = classify_io(fixed)
        self.assertEqual((c["evidence"], c["fixed_dir"]), ("fixed", "FIXED_DIR"))
        self.assertEqual(classify_io(base + "Remove-Item Env:\\A -ErrorAction SilentlyContinue\n")["env"], "clears_without_saving")
        self.assertEqual(classify_io(base + "$old = $env:A\n$env:A = '1'\n")["env"], "restores_prior")
        self.assertTrue(classify_io("param(\n[string]$R)\n$R = (Resolve-Path $R).Path\n")["root"] == "param_resolved")
        launch = "$execCmd = '-ExecCmds=\"py x\"'\n$proc = Start-Process -FilePath $e -PassThru -ArgumentList @($p,$execCmd)\n"
        self.assertTrue(classify_io(launch)["execcmds_embedded_quotes"])
        self.assertTrue(classify_io("$proc = Start-Process -FilePath $e -ArgumentList $a -PassThru -Wait\n")["unbounded_wait"])
        poll = launch + "$deadline = [DateTime]::UtcNow.AddMinutes(5)\nif (Select-String -Path $log -Pattern 'OK' -Quiet) { break }\n"
        self.assertTrue(classify_io(poll)["poll_deadline"])
        self.assertFalse(classify_io(poll)["log_removed_before_launch"])
        self.assertTrue(classify_io("Remove-Item -LiteralPath $log -ErrorAction SilentlyContinue\n" + poll)["log_removed_before_launch"])
        self.assertTrue(classify_io("$args = @(1,2)\n")["assigns_automatic_args"])
        self.assertTrue(classify_io("if (Test-Path -LiteralPath $evidence) { throw 'x' }\n")["evidence_exists_abort"])


class Census(unittest.TestCase):
    def test_deterministic_and_complete(self):
        self.assertEqual(len(RUNNERS), 34)
        self.assertEqual(CENSUS, {p.name: classify_io(p.read_text(encoding="utf-8-sig", errors="replace")) for p in RUNNERS})


class Bk151EnvironmentAndCwd(unittest.TestCase):
    def test_roots_and_engine_paths(self):
        """32 runners hardcode the project root; 2 take it as a param resolved with Resolve-Path. All 34 hardcode the
        UE 5.5 install path (as a literal or a param default)."""
        self.assertEqual(names(lambda c: c["root"] == "param_resolved"), PARAM_RUNNERS)
        self.assertEqual(len(names(lambda c: c["engine_literal"])), 34)

    def test_working_directory_changes_are_not_restored(self):
        """9 runners Set-Location to the project root and none restores the caller's location (no Pop-Location)."""
        self.assertEqual(names(lambda c: c["set_location"]), SET_LOCATION)
        self.assertEqual(names(lambda c: c["restores_location"]), [])

    def test_environment_mutation(self):
        """11 runners change process env vars: 4 save and restore prior values; 7 remove them in finally without
        saving, which erases a value the caller had set before the run."""
        self.assertEqual(names(lambda c: c["env"] == "clears_without_saving"), ENV_CLEARS_WITHOUT_SAVING)
        self.assertEqual(len(names(lambda c: c["env"] == "restores_prior")), 4)
        self.assertEqual(len(names(lambda c: c["env"] == "none")), 23)

    def test_tools_resolved_from_path(self):
        self.assertEqual(names(lambda c: c["tool_from_path"]), PARAM_RUNNERS)


class Bk152ChildProcess(unittest.TestCase):
    def test_launch_styles(self):
        """27 runners use the call operator (&, per-token argument passing); 12 use Start-Process; both counts include
        runners that use both."""
        self.assertEqual(len(names(lambda c: c["call_operator"])), 27)
        self.assertEqual(len(names(lambda c: c["start_process"])), 12)

    def test_quoting_and_inputs(self):
        """9 Start-Process runners pass an -ExecCmds element with EMBEDDED double quotes inside an -ArgumentList array:
        Windows PowerShell joins array elements with spaces without quoting them, so correctness depends on those
        embedded quotes and on space-free short paths. 2 runners take caller params (EngineRoot/ProjectRoot) that
        flow into executable paths. 1 runner assigns PowerShell's automatic $args variable as its argument list."""
        self.assertEqual(names(lambda c: c["execcmds_embedded_quotes"]), EMBEDDED_QUOTE_EXECCMDS)
        self.assertEqual(names(lambda c: c["caller_params"]), PARAM_RUNNERS)
        self.assertEqual(names(lambda c: c["assigns_automatic_args"]), ["run_c1274_s6_locked_dryrun.ps1"])


class Bk153OutputPaths(unittest.TestCase):
    def test_per_run_vs_fixed_evidence(self):
        """16 runners write to a per-run timestamped folder; 18 reuse a fixed folder, so each run overwrites the
        previous run's same-named evidence files."""
        self.assertEqual(names(lambda c: c["evidence"] == "fixed"), FIXED_EVIDENCE)
        self.assertEqual(len(names(lambda c: c["evidence"] == "per_run")), 16)

    def test_collision_guards(self):
        """Only 3 runners abort if the evidence folder already exists; 33 create it with New-Item -Force (merge).
        13 per-run runners therefore rely on a 1-second timestamp alone."""
        self.assertEqual(names(lambda c: c["evidence_exists_abort"]), EXISTS_ABORT)
        self.assertEqual(len(names(lambda c: c["new_item_force"])), 33)
        self.assertEqual(len(names(lambda c: c["evidence"] == "per_run" and not c["evidence_exists_abort"])), 13)

    def test_fixed_folders_shared_between_runners(self):
        """3 fixed folders are each written by 2 different runners (build + live pairs)."""
        self.assertEqual(shared_fixed_dirs(), SHARED_DIRS)


class Bk154TimeoutAndExit(unittest.TestCase):
    def test_timeouts(self):
        """9 runners poll a launched editor against a deadline and kill it on timeout; 3 use Start-Process -Wait with
        no timeout; no call-operator (&) step in any runner has a timeout."""
        self.assertEqual(len(names(lambda c: c["poll_deadline"])), 9)
        self.assertEqual(names(lambda c: c["unbounded_wait"]), UNBOUNDED_WAIT)

    def test_exit_codes(self):
        self.assertEqual(len(names(lambda c: c["lastexitcode"])), 27)
        self.assertEqual(len(names(lambda c: c["proc_exitcode"])), 5)

    def test_stale_log_marker_risk(self):
        """6 polling runners write their editor log into a FIXED evidence folder and never delete the old log before
        launch; the poll starts 2 s after launch, so a previous run's log containing the success marker can end the
        wait (and the run is judged from that text) before the new editor rewrites the log. Results are tied to a
        log path, not to the launched process."""
        risky = names(lambda c: c["poll_deadline"] and c["evidence"] == "fixed" and not c["log_removed_before_launch"])
        self.assertEqual(risky, STALE_LOG_RISK)
        self.assertEqual(names(lambda c: c["log_removed_before_launch"]), [])


if __name__ == "__main__":
    unittest.main()
