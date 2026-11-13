"""BK-141..145 (C, implementer; X-2024, extended for X-2027): static, source-only audit of the C-1155 lock code in the PowerShell runner.

Primary target: Scripts/Editor/run_bk56_60_deferred_selection.ps1 (the runner the executor contract cites). The runner is
only READ as text: it is never executed, and no lock file is created, read or deleted. Invariants that hold are
ordinary tests; confirmed gaps are pinned as expectedFailure tests with the rule in the docstring, for the lead.
A cross-runner survey checks the two invariants every C-1155 runner must share.
Proposal/audit only; no production edit; X-1991 remains open.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts" / "Editor" / "run_bk56_60_deferred_selection.ps1"
SRC = RUNNER.read_text(encoding="utf-8-sig")
LINES = SRC.splitlines()


def line_of(pattern, start=0):
    """1-based line number of the first line (from `start`) matching the regex; None if absent."""
    rx = re.compile(pattern)
    for index in range(start, len(LINES)):
        if rx.search(LINES[index]):
            return index + 1
    return None


def block(start_pattern, end_pattern):
    """Text from the first start match to the next end match (inclusive)."""
    start = line_of(start_pattern)
    end = line_of(end_pattern, start)
    return "\n".join(LINES[start - 1:end]), start, end


TOKEN_LINE = line_of(r"\$token\s*=\s*\[guid\]::NewGuid\(\)\.ToString\('N'\)")
LOCKS_LINE = line_of(r"^\$locks\s*=")
ACQUIRE, ACQ_START, ACQ_END = block(r"foreach \(\$lock in \$locks\) \{\s*$", r"^\s*\}\s*$")
FINALLY, FIN_START, FIN_END = block(r"^finally \{", r"^\}")
FIRST_CREATE_LINE = line_of(r"FileMode\]::CreateNew")
# K1 (X-2027): accepted exact (ordinal) ownership comparisons, and the rejected case-insensitive one.
K1_EXACT = re.compile(r"owner_token -ceq \$token|\[string\]::Equals\(\$current\.owner_token,\s*\$token,\s*\[StringComparison\]::Ordinal\)")
K1_INSENSITIVE = re.compile(r"owner_token -eq \$token")


class Bk141Token(unittest.TestCase):
    def test_token_is_a_guid_n_string_generated_before_any_lock_create(self):
        """[guid]::NewGuid().ToString('N') is 32 hex digits, lowercase on .NET; generated before the first create."""
        self.assertIsNotNone(TOKEN_LINE)
        self.assertLess(TOKEN_LINE, FIRST_CREATE_LINE)
        record_line = line_of(r"^\$record\s*=")
        self.assertLess(TOKEN_LINE, record_line)
        self.assertIn("owner_token=$token", LINES[record_line - 1])

    def test_token_is_never_reassigned(self):
        self.assertEqual(len(re.findall(r"^\s*\$token\s*=", SRC, re.M)), 1)

    @unittest.expectedFailure
    def test_gap_t1_token_format_is_asserted_before_any_lock_create(self):
        """T1 (BK-141): validity rests on the .NET GUID 'N' format; there is no explicit check such as
        `if ($token -cnotmatch '^[0-9a-f]{32}$') { throw ... }` between token generation and the first CreateNew.
        X-2023 (F1 = b) requires the executor to validate the token before any filesystem create; add the assertion."""
        between = "\n".join(LINES[TOKEN_LINE:FIRST_CREATE_LINE - 1])
        self.assertRegex(between, r"\$token\s+-c?(not)?match\s+'\^\[0-9a-f\]\{32\}\$'")


class Bk142PathsOrderCreate(unittest.TestCase):
    def test_both_canonical_paths_root_then_execution(self):
        locks = LINES[LOCKS_LINE - 1]
        root = locks.index("'ENGINE_LOCK.json'")
        execution = locks.index("'Docs\\BossCombatReview\\Execution\\ENGINE_LOCK.json'")
        self.assertLess(root, execution)
        self.assertEqual(locks.count("ENGINE_LOCK.json"), 2)

    def test_preexisting_lock_or_editor_aborts_before_create(self):
        self.assertLess(line_of(r"lock already exists"), FIRST_CREATE_LINE)
        self.assertLess(line_of(r"an UnrealEditor process is active"), FIRST_CREATE_LINE)
        self.assertGreater(line_of(r"UnrealEditor started during C-1155 lock acquisition"), ACQ_END - 1)

    def test_exclusive_temp_create_then_no_overwrite_move_then_record(self):
        """CreateNew + FileShare.None (fails if the temp exists), flush to disk, File.Move(src, dst) (2-argument form
        never overwrites an existing lock), then the path is recorded as created - in that order, inside try."""
        order = [ACQUIRE.index(s) for s in ("FileMode]::CreateNew", "FileShare]::None", "Flush($true)",
                                            "[System.IO.File]::Move($temp,$lock)", "$created.Add($lock)")]
        self.assertEqual(order, sorted(order))
        self.assertNotRegex(ACQUIRE, r"Move\(\$temp,\s*\$lock,\s*\$true\)|Copy|Overwrite|-Force")
        self.assertLess(line_of(r"^try \{"), ACQ_START)

    def test_first_failed_create_stops_acquisition(self):
        """$ErrorActionPreference='Stop' and .NET exceptions end the foreach, so the execution lock is never created
        after a failed root create (the v2 create_order root-first rule)."""
        self.assertLess(line_of(r"^\$ErrorActionPreference = 'Stop'"), ACQ_START)
        self.assertNotIn("catch", ACQUIRE)

    @unittest.expectedFailure
    def test_gap_l1_failed_move_leaves_no_orphan_temp_file(self):
        """L1 (BK-142): if File.Move throws (the lock appeared after the :24 pre-check, or the write failed), the
        `<lock>.<token>.tmp` file is left behind: $created never lists it and finally only visits $created. Rule: track
        the temp path and delete it (if still present) in the acquisition loop's catch/finally."""
        self.assertRegex(ACQUIRE + "\n" + FINALLY, r"Remove-Item[^\n]*\$temp")


class Bk143RecordFields(unittest.TestCase):
    RECORD = LINES[line_of(r"^\$record\s*=") - 1]

    def test_record_carries_the_identity_fields_the_v2_receipt_maps(self):
        for field in ("owner_token=$token", "party='X'", "policy='C-1155'", "agent='Codex'", "pid=$PID", "start_utc=",
                      "command_id=", "task=", "scope="):
            with self.subTest(field):
                self.assertIn(field, self.RECORD)

    def test_v2_mapping_sources(self):
        """v2 lock field <- runner source: path <- $locks; created and create_order <- membership/position in $created
        (root first by loop order); token <- $token; party/policy <- record literals."""
        self.assertIn("$created.Add($lock)", ACQUIRE)
        self.assertIn("ConvertTo-Json -Compress", self.RECORD)

    @unittest.expectedFailure
    def test_gap_r1_lock_is_read_back_after_create(self):
        """R1 (BK-143): nothing reads the lock file back after File.Move, so v2 `readback_token`/`party`/`policy` (and
        the contract's acquire_locks `observed` records, :127-136) have no runner source until finally. Rule: after each
        Move, read the lock (ConvertFrom-Json) and require owner_token == $token before continuing."""
        acquire_and_after = "\n".join(LINES[ACQ_START - 1:ACQ_END + 3])
        self.assertRegex(acquire_and_after, r"ConvertFrom-Json")

    @unittest.expectedFailure
    def test_gap_r2_per_lock_release_evidence_is_recorded(self):
        """R2 (BK-143): the runner records no per-lock release_attempted / release_token_match / released observation,
        which the v2 lock record needs. Rule: write one evidence line per created lock with those three values."""
        self.assertRegex(FINALLY, r"release_token_match|RELEASED_\w+=|TOKEN_MATCH")


class Bk144FinallyCleanup(unittest.TestCase):
    def test_cleanup_visits_only_recorded_created_paths(self):
        self.assertIn("foreach ($lock in $created)", FINALLY)
        self.assertNotIn("foreach ($lock in $locks)", FINALLY)

    def test_token_is_compared_before_delete(self):
        compare = re.search(r"\$current\.owner_token -c?eq \$token", FINALLY).start()
        delete = FINALLY.index("Remove-Item -LiteralPath $lock -Force")
        self.assertLess(compare, delete)
        self.assertRegex(FINALLY, r"if \(\$current\.owner_token -c?eq \$token\) \{ Remove-Item -LiteralPath \$lock -Force \}")

    def test_each_lock_release_is_isolated_by_its_own_try_catch(self):
        """A failure on one lock (garbled JSON, delete error) is caught and the loop continues to the next lock."""
        loop = FINALLY[FINALLY.index("foreach ($lock in $created)"):]
        self.assertLess(loop.index("try {"), loop.index("Remove-Item"))
        self.assertIn("catch { Write-Warning", loop)

    @unittest.expectedFailure
    def test_gap_c1_lock_release_cannot_be_skipped_by_earlier_finally_statements(self):
        """C1 (BK-144): finally first restores env vars and then runs `if (!$proc.HasExited) { $proc.Kill() ... }`
        unguarded. If Kill throws (the process exits between the check and the call, or access is denied), the
        exception leaves finally before the lock loop, retaining both locks. Rule: wrap the env/process cleanup in its
        own try/catch, or release the locks first."""
        kill = FINALLY.index("$proc.Kill()")
        lock_loop = FINALLY.index("foreach ($lock in $created)")
        guarded = re.search(r"try \{[^}]*\$proc\.Kill\(\)", FINALLY) is not None
        self.assertTrue(guarded or lock_loop < kill)

    @unittest.expectedFailure
    def test_gap_e1_lock_result_reports_released_not_created(self):
        """E1 (BK-144): lock_result.txt is written as 'LOCKS_RELEASED=' + $created.Count - the number CREATED. A lock
        kept on token mismatch (silently: no warning on mismatch) or after a delete error is still counted as released.
        Rule: count successful deletes (and report retained paths) instead of $created.Count."""
        self.assertNotIn("'LOCKS_RELEASED=' + $created.Count", FINALLY)

    @unittest.expectedFailure
    def test_gap_k1_release_token_comparison_is_case_sensitive(self):
        """K1 (BK-144, X-2027): `$current.owner_token -eq $token` (R:208) uses PowerShell's CASE-INSENSITIVE string
        equality, so a lock whose token differs from this run's lowercase token only by letter case (for example
        another run's 'ABC...' vs our 'abc...') passes the ownership check and is deleted. Rule: exact ordinal
        comparison - `-ceq`, or [string]::Equals($current.owner_token, $token, [StringComparison]::Ordinal)."""
        self.assertRegex(FINALLY, K1_EXACT)
        self.assertNotRegex(FINALLY, K1_INSENSITIVE)

    def test_k1_rule_accepts_exact_patterns_and_rejects_case_insensitive_on_synthetic_strings(self):
        """Synthetic-string check of the K1 rule (X-2028): the accepted fixes satisfy it, the current form does not."""
        accepted = ("if ($current.owner_token -ceq $token) { Remove-Item -LiteralPath $lock -Force }",
                    "if ([string]::Equals($current.owner_token, $token, [StringComparison]::Ordinal)) { Remove-Item -LiteralPath $lock -Force }")
        rejected = ("if ($current.owner_token -eq $token) { Remove-Item -LiteralPath $lock -Force }",
                    "if ($current.owner_token -ieq $token) { Remove-Item -LiteralPath $lock -Force }",
                    "if ([string]::Equals($current.owner_token, $token, [StringComparison]::OrdinalIgnoreCase)) { Remove-Item }")
        for text in accepted:
            with self.subTest(accepted=text):
                self.assertRegex(text, K1_EXACT)
                self.assertNotRegex(text, K1_INSENSITIVE)
        for text in rejected:
            with self.subTest(rejected=text):
                self.assertFalse(K1_EXACT.search(text) and not K1_INSENSITIVE.search(text))

    def test_token_mismatch_is_silent(self):
        """Documented with E1: on owner_token mismatch the lock is retained without any warning (only the catch warns)."""
        self.assertNotRegex(FINALLY, r"-ne \$token|else \{ Write-Warning")


C1155_RUNNERS = sorted(p for p in (ROOT / "Scripts").rglob("*.ps1") if "owner_token" in p.read_text(encoding="utf-8-sig", errors="replace"))


class Bk145CrossRunnerSurvey(unittest.TestCase):
    def test_survey_is_deterministic_and_nonempty(self):
        self.assertGreaterEqual(len(C1155_RUNNERS), 30)
        self.assertIn(RUNNER, C1155_RUNNERS)

    def test_every_c1155_runner_creates_exclusively_and_compares_the_token_before_delete(self):
        for path in C1155_RUNNERS:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            with self.subTest(runner=path.name):
                self.assertIn("FileMode]::CreateNew", text)
                self.assertIn("NewGuid().ToString('N')", text)
                self.assertRegex(text, r"owner_token -c?eq \$token\)\s*\{\s*Remove-Item")

    def test_case_insensitive_release_comparison_is_shared(self):
        """K1 is not specific to BK-56..60: every C-1155 runner compares the release token with case-insensitive -eq
        (one comparison each, none uses -ceq or an ordinal Equals). Update this count as runners are fixed."""
        insensitive = [p.name for p in C1155_RUNNERS
                       if re.search(r"owner_token -eq \$token", p.read_text(encoding="utf-8-sig", errors="replace"))]
        sensitive = [p.name for p in C1155_RUNNERS
                     if re.search(r"owner_token -ceq \$token|Equals\(\$current\.owner_token,\s*\$token,\s*\[StringComparison\]::Ordinal", p.read_text(encoding="utf-8-sig", errors="replace"))]
        self.assertEqual((len(insensitive), len(sensitive)), (34, 0), (insensitive, sensitive))

    def test_lock_result_counting_pattern_is_shared(self):
        """E1 is not specific to BK-56..60: count the runners that report $created.Count as released."""
        counted = [p.name for p in C1155_RUNNERS if "'LOCKS_RELEASED=' + $created.Count" in p.read_text(encoding="utf-8-sig", errors="replace")]
        self.assertEqual(len(counted), 28, counted)


if __name__ == "__main__":
    unittest.main()
