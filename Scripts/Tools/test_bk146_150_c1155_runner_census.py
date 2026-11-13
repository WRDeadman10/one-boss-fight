"""BK-146..150 (C, implementer; X-2029): static census of the C-1155 lock code in every runner script.

Source-only: every `.ps1` under Scripts/ that contains `owner_token` is READ as text; nothing is executed and no lock
or temp file is created, read or deleted. Each census is computed by `classify()` and compared with an explicit
expected table, so any runner change surfaces as a test failure to re-review. Counts describe source text only - not
runtime behavior. Audit only; no production edit; X-1991 remains open.

BK-146 finally ordering: statements before the lock-release loop that can throw and skip release.
BK-147 post-create readback of the lock (token/party/policy) before the main work.
BK-148 temp-file cleanup where a lock is promoted from a temp file with File.Move.
BK-149 release evidence accuracy: per-lock vs aggregate vs none; mismatch/catch warnings.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNERS = sorted(p for p in (ROOT / "Scripts").rglob("*.ps1")
                 if "owner_token" in p.read_text(encoding="utf-8-sig", errors="replace"))


def classify(path):
    return classify_text(path.read_text(encoding="utf-8-sig", errors="replace"))


def classify_text(source):
    lines = source.splitlines()
    text = "\n".join(lines)
    var = re.search(r"\$(\w+)\.Add\(\$lock\)", text).group(1)
    loop = next(i for i, l in enumerate(lines) if re.search(r"foreach \(\$lock in \$%s\)" % var, l))
    fin = next(i for i in range(loop, -1, -1) if re.search(r"finally\s*\{\s*$", lines[i]))
    pre = [l.strip() for l in lines[fin + 1:loop] if l.strip()]
    release_loop = "\n".join(lines[loop:loop + 8])
    after_loop = "\n".join(lines[loop:])
    first_create = next(i for i, l in enumerate(lines) if "FileMode]::CreateNew" in l)
    lock_reads = [i for i, l in enumerate(lines) if re.search(r"Get-Content[^\n]*\$lock\b", l)]

    def unguarded(statement, pattern):
        return re.search(pattern, statement) is not None and not statement.startswith("try") \
            and "-ErrorAction SilentlyContinue" not in statement

    temp_add = next((i for i, l in enumerate(lines) if "$temps.Add($temp)" in l), None)
    return {
        "lock_var": var,
        "finally_line": fin + 1,
        "loop_line": loop + 1,
        # BK-146
        "kill_before_release": any(unguarded(s, r"\.Kill\(\)") for s in pre),
        "unguarded_remove_before_release": any(unguarded(s, r"Remove-Item -LiteralPath") for s in pre),
        "guarded_env_before_release": any("Env:\\" in s and "-ErrorAction SilentlyContinue" in s for s in pre)
        or any("SetEnvironmentVariable" in s for s in pre),
        # BK-147
        "readback_after_create": any(i > first_create and i < fin for i in lock_reads),
        # BK-148
        "temp_move": "File]::Move" in text,
        "temp_tracked_before_create": temp_add is not None and temp_add < first_create + 1,
        "temp_cleanup_in_finally": any(re.search(r"Remove-Item[^\n]*\$temp\b", s) for s in pre),
        # BK-149
        "evidence": ("created_count" if re.search(r"LOCKS_RELEASED=(?:'\s*\+\s*|\$\()\$%s\.Count" % var, after_loop)
                     else "per_lock" if re.search(r"release_token_match|RETAINED_|TOKEN_MATCH", after_loop) else "none"),
        "catch_warns": re.search(r"catch\s*\{\s*Write-Warning", release_loop) is not None,
        "mismatch_warns": re.search(r"-c?ne \$token|\}\s*else\s*\{\s*Write-Warning", release_loop) is not None,
        "case_sensitive_compare": re.search(r"owner_token -ceq \$token", release_loop) is not None,
    }


CENSUS = {p.name: classify(p) for p in RUNNERS}


def names(predicate):
    return sorted(n for n, c in CENSUS.items() if predicate(c))


# ---- expected tables (frozen from the source on 2026-11-11; update deliberately when a runner is fixed) ----
KILL_BEFORE_RELEASE = sorted([
    "run_be_x26_x30_locked_validation.ps1", "run_bk2_x26_locked_validation.ps1", "run_bk56_60_deferred_selection.ps1",
    "run_c1256a_live_self_test.ps1", "run_c1257a_author.ps1", "run_c1257a_dry_run.ps1", "run_c1258a_live_self_test.ps1",
    "run_c1262a_live_diagnostic.ps1", "run_c1265b_clip_trace.ps1", "run_c1274_s6_locked_dryrun.ps1",
    "run_c1275a_locked_validation.ps1", "run_c1280_x26_locked_validation.ps1"])
UNGUARDED_TEMP_REMOVE_BEFORE_RELEASE = sorted([
    "run_bf_x11_x15_locked_build.ps1", "run_bf_x16_x20_locked_build.ps1", "run_bk7_shipping_pipeline.ps1"])
TEMP_MOVE = sorted(UNGUARDED_TEMP_REMOVE_BEFORE_RELEASE + ["run_bk56_60_deferred_selection.ps1"])
NO_RELEASE_EVIDENCE = sorted([
    "run_bk7_shipping_pipeline.ps1", "run_c1252a_locked_validation.ps1", "run_c1253a_locked_validation.ps1",
    "run_c1254a_transient_profile_check.ps1", "run_c1255_live_bridge_validation.ps1"])


def synthetic(pre="", evidence="", compare="-eq", mismatch="", temp=False, readback=""):
    """A minimal synthetic runner (text only, never written to disk) for checking the classifier itself."""
    temp_lines = ("$temps = [System.Collections.Generic.List[string]]::new()\n" if temp else "")
    create = ("        $temp = $lock + '.' + $token + '.tmp'\n        $temps.Add($temp)\n"
              "        $stream = [System.IO.File]::Open($temp,[System.IO.FileMode]::CreateNew)\n"
              "        [System.IO.File]::Move($temp,$lock)\n" if temp else
              "        $stream = [System.IO.File]::Open($lock,[System.IO.FileMode]::CreateNew)\n")
    return ("$ErrorActionPreference = 'Stop'\n$token = [guid]::NewGuid().ToString('N')\n" + temp_lines +
            "$created = [System.Collections.Generic.List[string]]::new()\ntry {\n    foreach ($lock in $locks) {\n" + create +
            "        $created.Add($lock)\n    }\n" + readback + "    Do-Work\n} finally {\n" + pre +
            "    foreach ($lock in $created) {\n        if (Test-Path -LiteralPath $lock) {\n"
            "            try { $current = Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json; if ($current.owner_token "
            + compare + " $token) { Remove-Item -LiteralPath $lock -Force }" + mismatch + " }\n"
            "            catch { Write-Warning 'x' }\n        }\n    }\n" + evidence + "}\n")


class ClassifierSelfCheck(unittest.TestCase):
    def test_classifier_detects_each_class_on_synthetic_runners(self):
        base = classify_text(synthetic())
        self.assertFalse(base["kill_before_release"] or base["unguarded_remove_before_release"] or base["readback_after_create"])
        self.assertEqual(base["evidence"], "none")
        self.assertTrue(base["catch_warns"])
        kill = "    if ($proc -and -not $proc.HasExited) { $proc.Kill(); $proc.WaitForExit() }\n"
        self.assertTrue(classify_text(synthetic(pre=kill))["kill_before_release"])
        self.assertFalse(classify_text(synthetic(pre="    try { $proc.Kill() } catch { Write-Warning 'k' }\n"))["kill_before_release"])
        env = "    Remove-Item Env:\\X -ErrorAction SilentlyContinue\n"
        guarded = classify_text(synthetic(pre=env))
        self.assertTrue(guarded["guarded_env_before_release"])
        self.assertFalse(guarded["unguarded_remove_before_release"])
        temp_pre = "    foreach ($temp in $temps) { if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force } }\n"
        temp = classify_text(synthetic(pre=temp_pre, temp=True))
        self.assertTrue(temp["temp_move"] and temp["temp_tracked_before_create"] and temp["temp_cleanup_in_finally"])
        self.assertTrue(temp["unguarded_remove_before_release"])
        self.assertEqual(classify_text(synthetic(evidence="    ('LOCKS_RELEASED=' + $created.Count) | Set-Content x\n"))["evidence"], "created_count")
        self.assertEqual(classify_text(synthetic(evidence='    "LOCKS_RELEASED=$($created.Count)" | Set-Content x\n'))["evidence"], "created_count")
        self.assertEqual(classify_text(synthetic(evidence="    'release_token_match=1' | Set-Content x\n"))["evidence"], "per_lock")
        self.assertTrue(classify_text(synthetic(compare="-ceq"))["case_sensitive_compare"])
        self.assertTrue(classify_text(synthetic(mismatch=" else { Write-Warning 'mismatch' }"))["mismatch_warns"])
        self.assertTrue(classify_text(synthetic(readback="    $rb = Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json\n"))["readback_after_create"])


class Census(unittest.TestCase):
    def test_census_is_deterministic_and_complete(self):
        self.assertEqual(len(RUNNERS), 34)
        self.assertEqual(CENSUS, {p.name: classify(p) for p in RUNNERS})
        self.assertEqual({c["lock_var"] for c in CENSUS.values()}, {"created", "createdLocks"})
        for name, c in CENSUS.items():
            with self.subTest(name):
                self.assertLess(c["finally_line"], c["loop_line"])


class Bk146FinallyOrdering(unittest.TestCase):
    def test_unguarded_kill_before_lock_release(self):
        """12 runners call `$proc.Kill(); $proc.WaitForExit()` unguarded in finally BEFORE the lock loop: if Kill or
        WaitForExit throws, finally exits and every created lock is retained (risk class: release-bypass)."""
        self.assertEqual(names(lambda c: c["kill_before_release"]), KILL_BEFORE_RELEASE)

    def test_unguarded_temp_remove_before_lock_release(self):
        """3 runners remove temp files with an unguarded `Remove-Item -Force` before the lock loop; all runners set
        $ErrorActionPreference='Stop', so a failed delete (file in use, access denied) skips lock release."""
        self.assertEqual(names(lambda c: c["unguarded_remove_before_release"]), UNGUARDED_TEMP_REMOVE_BEFORE_RELEASE)

    def test_release_first_runners(self):
        """The remaining 19 runners have no throwing statement before the lock loop (release first, or only guarded
        env-var restores with -ErrorAction SilentlyContinue / SetEnvironmentVariable)."""
        risky = set(KILL_BEFORE_RELEASE) | set(UNGUARDED_TEMP_REMOVE_BEFORE_RELEASE)
        safe = names(lambda c: not c["kill_before_release"] and not c["unguarded_remove_before_release"])
        self.assertEqual(len(safe), 19)
        self.assertEqual(set(safe) | risky, set(CENSUS))
        self.assertEqual(set(safe) & risky, set())

    def test_every_runner_sets_error_action_stop(self):
        for path in RUNNERS:
            with self.subTest(path.name):
                self.assertRegex(path.read_text(encoding="utf-8-sig", errors="replace"), r"\$ErrorActionPreference\s*=\s*'Stop'")


class Bk147Readback(unittest.TestCase):
    def test_no_runner_reads_a_lock_back_after_create(self):
        """0 of 34 runners read a created lock (Get-Content $lock) between the first CreateNew and finally; the only
        lock reads are the release-time ownership checks. v2 readback_token/party/policy has no runner source."""
        self.assertEqual(names(lambda c: c["readback_after_create"]), [])


class Bk148TempCleanup(unittest.TestCase):
    def test_temp_move_runners(self):
        self.assertEqual(names(lambda c: c["temp_move"]), TEMP_MOVE)

    def test_temp_tracking_and_cleanup(self):
        """3 of 4 temp+Move runners record the temp path BEFORE CreateNew and delete leftovers in finally (unguarded,
        see BK-146); run_bk56_60 tracks no temp path, so a failed Move leaves `<lock>.<token>.tmp` behind (BK-142 L1)."""
        self.assertEqual(names(lambda c: c["temp_tracked_before_create"]), UNGUARDED_TEMP_REMOVE_BEFORE_RELEASE)
        self.assertEqual(names(lambda c: c["temp_cleanup_in_finally"]), UNGUARDED_TEMP_REMOVE_BEFORE_RELEASE)
        self.assertEqual(sorted(set(TEMP_MOVE) - set(names(lambda c: c["temp_cleanup_in_finally"]))),
                         ["run_bk56_60_deferred_selection.ps1"])


class Bk149ReleaseEvidence(unittest.TestCase):
    def test_evidence_classes(self):
        """29 runners write LOCKS_RELEASED=<created count> (a false aggregate: it counts locks CREATED, so a lock kept on
        token mismatch or delete failure is reported as released); 5 write no lock evidence; 0 write per-lock evidence."""
        evidence = {kind: names(lambda c, k=kind: c["evidence"] == k) for kind in ("created_count", "none", "per_lock")}
        self.assertEqual(len(evidence["created_count"]), 29)
        self.assertEqual(evidence["none"], NO_RELEASE_EVIDENCE)
        self.assertEqual(evidence["per_lock"], [])

    def test_warnings_cover_errors_but_not_token_mismatch(self):
        """All 34 warn when the ownership read/delete throws (catch), none warn on a plain token mismatch, and none
        compare case-sensitively (K1, X-2027)."""
        self.assertEqual(len(names(lambda c: c["catch_warns"])), 34)
        self.assertEqual(names(lambda c: c["mismatch_warns"]), [])
        self.assertEqual(names(lambda c: c["case_sensitive_compare"]), [])


if __name__ == "__main__":
    unittest.main()
