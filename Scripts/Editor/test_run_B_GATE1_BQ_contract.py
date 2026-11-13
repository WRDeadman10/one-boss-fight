"""X-2406 static contract for run_B_GATE1_BQ_locked_build.ps1. Text checks only: the runner is never executed here."""
import re
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parent / "run_B_GATE1_BQ_locked_build.ps1"
DD27J = "cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec"


class Gate1RunnerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = SCRIPT.read_text(encoding="utf-8")
        cls.code = "\n".join(l for l in cls.s.splitlines() if not l.lstrip().startswith("#"))

    def idx(self, needle):
        i = self.code.find(needle)
        self.assertGreaterEqual(i, 0, needle)
        return i

    def test_both_lock_paths_and_pin(self):
        self.assertIn("(Join-Path $root 'ENGINE_LOCK.json')", self.code)
        self.assertIn("(Join-Path $root 'Docs\\BossCombatReview\\Execution\\ENGINE_LOCK.json')", self.code)
        self.assertIn("$manifest = '%s'" % DD27J, self.code)
        self.assertIn('"-DD27jManifestHash=$manifest"', self.code)

    def test_atomic_acquire_and_token_readback(self):
        self.assertIn("[System.IO.FileMode]::CreateNew", self.code)
        self.assertIn("[System.IO.FileShare]::None", self.code)
        self.assertIn("[System.IO.File]::Move($temp, $lock)", self.code)
        # read-back verification happens inside the acquire loop, after Move, before any engine work
        self.assertLess(self.idx("[System.IO.File]::Move($temp, $lock)"), self.idx("$readBack.owner_token -ne $token"))
        self.assertLess(self.idx("$readBack.owner_token -ne $token"), self.idx("Build.bat"))

    def test_unreal_process_checked_before_and_after_locks(self):
        self.assertIn("Get-Process UnrealEditor*", self.code)
        pre = self.idx("ABORT: UnrealEditor process is running (preflight)")
        post = self.idx("ABORT: UnrealEditor process appeared after lock acquisition")
        self.assertLess(pre, self.idx("[System.IO.FileMode]::CreateNew"))
        self.assertLess(self.idx("[System.IO.File]::Move($temp, $lock)"), post)
        self.assertLess(post, self.idx("Build.bat"))
        self.assertIn("ABORT: UnrealEditor process appeared before suite launch", self.code)
        self.assertIn("ABORT: UnrealEditor process appeared before build launch", self.code)

    def test_existing_lock_or_evidence_aborts(self):
        self.assertIn('throw "ABORT: engine lock exists: $lock"', self.code)
        self.assertIn('throw "ABORT: evidence directory already exists: $evidence"', self.code)
        self.assertIn("$token.Substring(0, 8)", self.code)   # unique evidence per invocation

    def test_scope_is_build_and_suite_only(self):
        self.assertIn("Build.bat') OneBossFightEditor Win64 Development", self.code)
        self.assertIn("'-ExecCmds=Automation RunTests OneBossFight; Quit'", self.code)
        self.assertIn("-nosound", self.code)
        self.assertIn("-NullRHI", self.code)
        for forbidden in ("Package.ps1", "BuildCookRun", "-run=cook", "-game", "py ", ".py", "save_", "RunUAT", "-ExecutePythonScript"):
            self.assertNotIn(forbidden, self.code, forbidden)
        # PIE launch patterns (the scope text and the NO_PIE=1 receipt marker legitimately contain the word "PIE")
        for pattern in (r"PlayInEditor", r"-PIE\b", r"pie_\w+", r"RunLeadPie", r"RunDrivers"):
            self.assertIsNone(re.search(pattern, self.code), pattern)
        self.assertEqual(len(re.findall(r"UnrealEditor-Cmd\.exe", self.code)), 1)
        self.assertEqual(len(re.findall(r"Build\.bat", self.code)), 1)

    def test_suite_pass_requires_all_started_tests_to_pass(self):
        self.assertIn("$started.Count -eq 0", self.code)
        self.assertIn("$started.Count -ne $passed.Count", self.code)
        self.assertIn("$failed.Count -gt 0", self.code)
        self.assertIn("TEST COMPLETE\\. EXIT CODE: 0", self.code)

    def test_status_written_on_every_exit_path(self):
        fin = self.idx("} finally {")
        self.assertGreater(self.code.index("Set-Content -LiteralPath (Join-Path $evidence 'status.txt')"), fin)
        self.assertIn("$reason = $_.Exception.Message", self.code)
        self.assertIn('"RESULT=$result"', self.code)
        self.assertIn("$result = if ($stage -eq 'done' -and $kept.Count -eq 0 -and $tempFailures.Count -eq 0) { 'PASS' } else { 'FAIL' }", self.code)

    def test_release_only_verified_own_locks(self):
        fin = self.code[self.idx("} finally {"):]
        self.assertIn("foreach ($lock in $created)", fin)
        self.assertIn("if ($current.owner_token -eq $token) { Remove-Item -LiteralPath $lock -Force; $released++ }", fin)
        self.assertIn("LOCKS_RELEASED=$released", fin)
        self.assertNotIn("foreach ($lock in $locks)", fin)   # never iterates locks it did not create
        self.assertIn("$temp = $lock + '.' + $token + '.tmp'", self.code)   # temp names carry this token

    def test_temp_cleanup_owns_only_successfully_created_temp_files(self):
        opened = self.idx("$stream = [System.IO.File]::Open($temp, [System.IO.FileMode]::CreateNew")
        tracked = self.idx("$temps.Add($temp)   # track only after CreateNew proves this run created it")
        self.assertLess(opened, tracked)
        cleanup_block = self.code[self.idx("} finally {"): ]
        self.assertIn("$tempFailures.Add($temp", cleanup_block)
        self.assertIn("TEMPS_KEPT=$($tempFailures -join '; ')", cleanup_block)
        self.assertLess(cleanup_block.index("$tempFailures.Add($temp"), cleanup_block.index("foreach ($lock in $created)"))

    def test_cleanup_faults_do_not_skip_lock_release_or_location_restore(self):
        cleanup_block = self.code[self.idx("} finally {"): ]
        self.assertIn("catch { $tempFailures.Add($temp", cleanup_block)
        self.assertIn("catch { $kept.Add($lock", cleanup_block)
        self.assertIn("Set-Location -LiteralPath $originalLocation.Path", cleanup_block)
        self.assertLess(cleanup_block.index("foreach ($lock in $created)"), cleanup_block.index("Set-Content -LiteralPath (Join-Path $evidence 'status.txt')"))

    def test_preflight_receipt_scope_is_not_overclaimed(self):
        self.assertIn("post-evidence exit path", self.s)
        self.assertIn("preflight refusals precede evidence creation", self.s)


if __name__ == "__main__":
    unittest.main()
