"""BK-161..165 (C, implementer; X-2032): static census of how C-1155 runners WRITE, ENCODE, READ BACK and PARSE their
status/receipt and evidence files.

Source-only: every `.ps1` under Scripts/ containing `owner_token` is READ; no runner or process is executed and no
file, lock, log or asset is touched. `classify_writes()` is checked on synthetic runner text, then compared with tables
frozen on 2026-11-11. Counts describe source text only - no runtime claims. Audit only; no production edit;
X-1991 remains open.
"""
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNERS = sorted(p for p in (ROOT / "Scripts").rglob("*.ps1")
                 if "owner_token" in p.read_text(encoding="utf-8-sig", errors="replace"))
STATUS_WRITE = re.compile(r"(Set-Content|Add-Content|Out-File|WriteAllText)\b[^\n]*(status|receipt)", re.I)


def _status_write_lines(lines):
    """Status/receipt write statements; a multi-line `"..." |` pipe into Add-Content counts once (its Add-Content line)."""
    hits = []
    for i, line in enumerate(lines):
        if STATUS_WRITE.search(line) and "failure" not in line.lower():
            hits.append(i)
        elif re.search(r"WriteAllText\(\$receiptPath", line):
            hits.append(i)
    return hits


GUARD = re.compile(r"(-eq 0\b|!\$\w|-not \$|-not \()")


def _positive_evidence_throw(lines):
    """True if an `if` whose condition fires on ABSENT evidence (count -eq 0, !$flag, -not ...) throws on the same line
    or within its next 5 lines (multi-line blocks)."""
    for i, line in enumerate(lines):
        if re.match(r"\s*if \(", line) and GUARD.search(line.split("{")[0] if "{" in line else line):
            if any(re.search(r"\bthrow\b", l) for l in lines[i:i + 6]):
                return True
    return False


def classify_writes(text):
    lines = text.splitlines()
    writes = _status_write_lines(lines)
    methods = sorted({m for i in writes for m in re.findall(r"Set-Content|Add-Content|Out-File|WriteAllText", lines[i])})
    region = "\n".join(lines[max(0, min(writes) - 25):max(writes) + 1]) if writes else ""
    status_values = "\n".join(l for l in lines if re.search(r"\$status|\$result|\$message|\$checks|_TRACE_START", l))
    return {
        # BK-161 write atomicity
        "write_methods": methods,
        "status_writes": len(writes),
        "atomic_status_write": re.search(r"Move\([^)]*(status|receipt)", text, re.I) is not None,
        # BK-162 encoding and key ambiguity
        "explicit_encoding": any(re.search(r"-Encoding|UTF8Encoding", lines[i]) for i in writes),
        "multi_pair_lines": re.search(r"=\{\d\}; [A-Z_]+=\{\d\}", text) is not None,
        "loop_repeated_keys": re.search(r"foreach[^\n]*\{[^\n]*$", text, re.M) is not None
        and re.search(r"\$status\.Add\(\(\"\{0\}_[A-Z_]+=\{1\}; ([A-Z_]+)=", text) is not None,
        "keys_derived_from_markers": re.search(r"-replace '\[\^A-Za-z0-9\]\+','_'\)=", text) is not None,
        "free_text_value": re.search(r"ERROR=\$\(\$\w+\.Exception\.Message\)", text) is not None,
        "mixed_boolean_encoding": bool(re.search(r"\[bool\]|\.Contains\(|HasExited|\.Success", status_values))
        and bool(re.search(r"(?<![A-Z0-9_])[A-Z][A-Z0-9_]*=[01](`|\"|'|$)", status_values, re.M)),
        # BK-163 readback
        "status_readback": re.search(r"(Get-Content|Select-String|Import-Csv|ConvertFrom-Json)[^\n]*(status\.txt|_status\.txt|\$statusPath|receipt\.json|\$receiptPath)", text) is not None,
        # BK-164 evidence parseability / missing-file behavior
        "missing_log_silent": re.search(r"Select-String[^\n]*-ErrorAction SilentlyContinue", text) is not None,
        "test_path_guarded_read": re.search(r"Test-Path -LiteralPath \$\w+\)[^\n]*(Get-Content|Select-String)", text) is not None,
        "zero_start_guard": re.search(r"\$started\.Count -eq 0", text) is not None,
        # a throw condition that fires when expected evidence is ABSENT (count == 0, !$flag, -not ...)
        "throw_requires_positive_evidence": _positive_evidence_throw(lines),
    }


CENSUS = {p.name: classify_writes(p.read_text(encoding="utf-8-sig", errors="replace")) for p in RUNNERS}


def names(predicate):
    return sorted(n for n, c in CENSUS.items() if predicate(c))


MIXED_BOOLEAN = sorted([
    "run_be_x01_x05_locked_build.ps1", "run_be_x06_x10_locked_build.ps1", "run_be_x11_x15_locked_build.ps1",
    "run_be_x16_x20_locked_build.ps1", "run_be_x21_x25_locked_build.ps1", "run_be_x26_x30_locked_validation.ps1",
    "run_be_x31_x35_locked_build.ps1", "run_be_x36_x40_locked_build.ps1", "run_bf_x01_x05_locked_build.ps1",
    "run_bf_x11_x15_locked_build.ps1", "run_bf_x16_x20_locked_build.ps1", "run_c1257a_dry_run.ps1", "run_c1257b_locked_build.ps1",
    "run_c1258a_locked_build.ps1", "run_c1262a_locked_build.ps1", "run_c1265b_clip_trace.ps1", "run_c1269a_locked_validation.ps1",
    "run_c1274_area_effect_validation.ps1", "run_c1274_channel_drain_validation.ps1", "run_c1275a_locked_validation.ps1",
    "run_c1280_x26_locked_validation.ps1"])
GUARDED_READ = sorted(["run_bk2_x26_locked_validation.ps1", "run_bk56_60_deferred_selection.ps1", "run_c1256a_live_self_test.ps1",
                       "run_c1257a_author.ps1", "run_c1257a_dry_run.ps1", "run_c1258a_live_self_test.ps1",
                       "run_c1262a_live_diagnostic.ps1", "run_c1265b_clip_trace.ps1", "run_c1275a_locked_validation.ps1"])
SUCCESS_KEY_IS_TEST_COUNT = ["run_c1252a_locked_validation.ps1", "run_c1253a_locked_validation.ps1"]


class ClassifierSelfCheck(unittest.TestCase):
    def test_synthetic_runner(self):
        text = ("$started = @(Select-String -Path $suiteLog -Pattern 'Test Started' -ErrorAction SilentlyContinue)\n"
                "if ($started.Count -eq 0) { throw 'no tests' }\n"
                "$status = \"COMPLETE=$([bool]$complete)`nNO_ASSETS=1\"\n"
                "Set-Content -LiteralPath (Join-Path $evidence 'status.txt') -Value $status\n")
        c = classify_writes(text)
        self.assertEqual(c["write_methods"], ["Set-Content"])
        self.assertFalse(c["atomic_status_write"] or c["explicit_encoding"] or c["status_readback"])
        self.assertTrue(c["missing_log_silent"] and c["zero_start_guard"] and c["throw_requires_positive_evidence"])
        self.assertTrue(c["mixed_boolean_encoding"])
        multiline = "if ($exit -ne 0 -or $pass -eq 0) {\n    Get-Content $log -Tail 5\n    throw 'x'\n}\n"
        self.assertTrue(classify_writes(multiline)["throw_requires_positive_evidence"])
        self.assertFalse(classify_writes("if ($exit -ne 0) { throw 'x' }\n")["throw_requires_positive_evidence"])
        atomic = ("Set-Content -LiteralPath $tmp -Value $status -Encoding utf8\n[System.IO.File]::Move($tmp, $statusPath)\n"
                  "Set-Content -LiteralPath $statusPath -Encoding utf8\n$check = Get-Content -Raw -LiteralPath $statusPath\n")
        a = classify_writes(atomic)
        self.assertTrue(a["atomic_status_write"] and a["explicit_encoding"] and a["status_readback"])
        loop = 'foreach ($move in $moves) {\n    $status.Add(("{0}_TRACE_START={1}; FRAMES={2}" -f $move,$a,$b))\n}\n'
        self.assertTrue(classify_writes(loop)["loop_repeated_keys"] and classify_writes(loop)["multi_pair_lines"])
        self.assertTrue(classify_writes("$m = \"ERROR=$($failure.Exception.Message)\"\n")["free_text_value"])


class Census(unittest.TestCase):
    def test_deterministic_and_complete(self):
        self.assertEqual(len(RUNNERS), 34)
        self.assertEqual(CENSUS, {p.name: classify_writes(p.read_text(encoding="utf-8-sig", errors="replace")) for p in RUNNERS})


class Bk161WriteAtomicity(unittest.TestCase):
    def test_all_status_writes_are_direct_and_non_atomic(self):
        """32 runners write status with Set-Content, 1 with Set-Content then per-stage Add-Content (bk2_x26), 1 with
        [IO.File]::WriteAllText (bk7 receipt). None writes to a temp file and moves it into place, so an interrupted
        write can leave a truncated or partially appended status file."""
        methods = Counter(tuple(c["write_methods"]) for c in CENSUS.values())
        self.assertEqual(methods, Counter({("Set-Content",): 32, ("Add-Content", "Set-Content"): 1, ("WriteAllText",): 1}))
        self.assertEqual(names(lambda c: c["atomic_status_write"]), [])
        self.assertEqual({n: c["status_writes"] for n, c in CENSUS.items() if c["status_writes"] != 1},
                         {"run_bk2_x26_locked_validation.ps1": 2})


class Bk162EncodingAndKeys(unittest.TestCase):
    def test_encoding_is_left_to_the_host(self):
        """33 runners write status without -Encoding (the encoding then depends on the PowerShell host); only bk7
        writes UTF-8 explicitly."""
        self.assertEqual(names(lambda c: c["explicit_encoding"]), ["run_bk7_shipping_pipeline.ps1"])

    def test_key_value_ambiguities(self):
        """c1265b writes several KEY=value pairs per line and repeats FRAMES/MAX_LOCAL_SECONDS/FULL_CLIP once per move
        (duplicate keys); the two c1257a runners derive keys from marker text by replacing non-alphanumerics with '_';
        bk56 puts a free-text exception message (may contain newlines or '=') in ERROR=; 21 runners mix True/False and
        1/0 booleans in one status."""
        self.assertEqual(names(lambda c: c["multi_pair_lines"]), ["run_c1265b_clip_trace.ps1"])
        self.assertEqual(names(lambda c: c["loop_repeated_keys"]), ["run_c1265b_clip_trace.ps1"])
        self.assertEqual(names(lambda c: c["keys_derived_from_markers"]), ["run_c1257a_author.ps1", "run_c1257a_dry_run.ps1"])
        self.assertEqual(names(lambda c: c["free_text_value"]), ["run_bk56_60_deferred_selection.ps1"])
        self.assertEqual(names(lambda c: c["mixed_boolean_encoding"]), MIXED_BOOLEAN)

    def test_success_key_is_a_test_count_not_a_verdict(self):
        """Correction to BK-158: in c1252a/c1253a `SUCCESS=$success` is the number of passed tests
        ((Select-String ... 'Result={Success}').Count), not an overall verdict; only bk7 has a verdict field."""
        for name in SUCCESS_KEY_IS_TEST_COUNT:
            text = next(p for p in RUNNERS if p.name == name).read_text(encoding="utf-8-sig", errors="replace")
            with self.subTest(name):
                self.assertRegex(text, r"\$success = \(Select-String[^\n]*Result=\\\{Success\\\}[^\n]*\)\.Count")
                self.assertIn("SUCCESS=$success", text)
                import importlib.util
                spec = importlib.util.spec_from_file_location("status_census_bk158", Path(__file__).resolve().parent / "test_bk156_160_c1155_runner_status_census.py")
                prior = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(prior)
                self.assertFalse(prior.classify_status(text)["verdict_field"])


class Bk163Readback(unittest.TestCase):
    def test_no_runner_reads_back_its_status(self):
        """0 of 34 runners re-read or parse the status/receipt file they wrote."""
        self.assertEqual(names(lambda c: c["status_readback"]), [])


class Bk164EvidenceParsing(unittest.TestCase):
    def test_missing_logs_become_zero_matches_but_fail_closed(self):
        """27 runners call Select-String with -ErrorAction SilentlyContinue, so a missing or unreadable log yields zero
        matches instead of an error; every runner (34/34) has a throw that fires when expected evidence is absent
        (count -eq 0, !$flag, -not ...), so a missing log fails the run rather than passing it."""
        self.assertEqual(len(names(lambda c: c["missing_log_silent"])), 27)
        self.assertEqual(len(names(lambda c: c["throw_requires_positive_evidence"])), 34)
        self.assertEqual(names(lambda c: c["missing_log_silent"] and not c["throw_requires_positive_evidence"]), [])

    def test_guarded_reads(self):
        """9 runners guard log reads with Test-Path; the only runner with neither is bk7 (exit codes only)."""
        self.assertEqual(names(lambda c: c["test_path_guarded_read"]), GUARDED_READ)
        self.assertEqual(names(lambda c: not c["missing_log_silent"] and not c["test_path_guarded_read"]), ["run_bk7_shipping_pipeline.ps1"])


if __name__ == "__main__":
    unittest.main()
