"""BK-181..185 corrections (X-2041 / A-847) and BK-186..190 (C, implementer; batch 4 of 20): lock acquisition scope
relative to the cleanup try, New-Item error handling, and release-failure visibility for every C-1155 lock writer.

Source-only: Scripts/**/*.ps1 are READ as text; nothing is executed and no lock, log, temp file or asset is touched.
The BK-181..185 module is imported read-only for its inventory; its file and report evidence are preserved (the report
gets an append-only correction). Classes describe code, not observed runtime. Audit only; X-1991 remains open.
"""
import importlib.util
import os
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPEC = importlib.util.spec_from_file_location("inventory_bk181", HERE / "test_bk181_185_c1155_full_inventory.py")
INV = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INV)

LOCKVAR = r"\$(lock\w*|path)\b"
WRITE = re.compile(r"FileMode\]::CreateNew|New-Item[^\n]*-ItemType File|(Set-Content|Out-File)[^\n]*\$lock|"
                   r"WriteAllText\(\$lock|\|\s*Set-Content -Path \$lock")
REMOVE = re.compile(r"Remove-Item[^\n]*" + LOCKVAR)


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8-sig", errors="replace")


def _indent(line):
    return len(line) - len(line.lstrip(" \t"))


def new_item_exclusivity(text):
    """BK-187: 'checked' if every lock New-Item fails hard (its own -ErrorAction Stop / -EA Stop, or a global
    $ErrorActionPreference = 'Stop' set before it); 'unchecked' if a New-Item can fail without stopping the script;
    'forced' if -Force replaces an existing file; None if the script has no lock New-Item."""
    lines = text.splitlines()
    sites = [i for i, l in enumerate(lines) if re.search(r"New-Item\b", l) and re.search(r"-ItemType\s+File", l)
             and re.search(LOCKVAR, l)]
    if not sites:
        return None
    global_stop = [i for i, l in enumerate(lines) if re.match(r"\s*\$ErrorActionPreference\s*=\s*['\"]Stop['\"]", l)]
    verdicts = []
    for i in sites:
        line = lines[i]
        if re.search(r"-Force\b", line):
            verdicts.append("forced")
        elif re.search(r"-(ErrorAction|EA)[:\s]+['\"]?Stop\b", line, re.I):
            verdicts.append("checked")
        elif re.search(r"-(ErrorAction|EA)[:\s]+['\"]?(SilentlyContinue|Continue|Ignore)\b", line, re.I):
            verdicts.append("unchecked")
        elif any(g < i for g in global_stop):
            verdicts.append("checked")
        else:
            verdicts.append("unchecked")
    for v in ("forced", "unchecked"):
        if v in verdicts:
            return v
    return "checked"


def cleanup_scope(text):
    """BK-188: locate the lock write, the release (Remove-Item of a lock), the finally holding it and the try that
    finally belongs to (same indentation), and say whether the write is inside that try."""
    lines = text.splitlines()
    write = next((i for i, l in enumerate(lines) if WRITE.search(l)), None)
    remove = next((i for i, l in enumerate(lines) if REMOVE.search(l)), None)
    if write is None or remove is None:
        return {"write_line": None if write is None else write + 1, "release_line": None, "try_line": None,
                "finally_line": None, "acquire": "no_release" if write is not None else "no_write"}
    fin = None
    for i in range(remove, -1, -1):
        if re.search(r"\bfinally\b", lines[i]):
            # a single-line `} finally { x }` that closes before the remove line is not the holder
            if i < remove and lines[i].count("{") <= lines[i].count("}") and not re.search(r"finally\s*\{\s*$", lines[i]):
                continue
            fin = i
            break
    if fin is None:
        return {"write_line": write + 1, "release_line": remove + 1, "try_line": None, "finally_line": None,
                "acquire": "release_not_in_finally"}
    level = _indent(lines[fin])
    tri = next((i for i in range(fin - 1, -1, -1)
                if re.search(r"(^|[\s}])try\s*\{", lines[i]) and _indent(lines[i]) == level), None)
    if tri is None:
        acquire = "try_not_found"
    elif tri < write < fin:
        acquire = "inside_cleanup_try"
    elif write < tri:
        acquire = "before_cleanup_try"
    else:
        acquire = "after_cleanup_try"
    return {"write_line": write + 1, "release_line": remove + 1, "try_line": None if tri is None else tri + 1,
            "finally_line": fin + 1, "acquire": acquire}


def failure_visibility(text):
    """BK-189: how a failed release is surfaced, and stranded-lock implications."""
    lines = text.splitlines()
    removes = [i for i, l in enumerate(lines) if REMOVE.search(l)]
    silenced = any(re.search(r"-ErrorAction SilentlyContinue|-EA SilentlyContinue", lines[i]) for i in removes)
    window = lambda i: "\n".join(lines[max(0, i - 4):i + 4])
    warned = any(re.search(r"catch\s*\{[^\n]*Write-Warning|catch\s*\{\s*$", window(i), re.M) and "Write-Warning" in window(i) for i in removes)
    unguarded_read = any(re.search(r"ConvertFrom-Json", lines[j]) and not re.search(r"\btry\b", "\n".join(lines[max(0, j - 2):j + 1]))
                         for i in removes for j in range(max(0, i - 4), i + 1))
    if not removes:
        visibility = "none"
    elif silenced:
        visibility = "silenced"
    elif warned:
        visibility = "warned"
    else:
        visibility = "terminating"
    return {
        "visibility": visibility,
        "ownership_read_unguarded": unguarded_read,
        "reports_created_as_released": re.search(r"LOCKS_RELEASED=(?:'\s*\+\s*|\$\()\$\w*[Cc]reated\w*\.Count", text) is not None,
    }


WRITERS = sorted(set(INV.SUBSET) | {p for p in INV.EXTRA if INV.CENSUS[p]["create"] != "none"})
SCOPE = {p: cleanup_scope(read(p)) for p in WRITERS}
VIS = {p: failure_visibility(read(p)) for p in WRITERS}
NEWITEM = {p: new_item_exclusivity(read(p)) for p in WRITERS}


def where(table, predicate):
    return sorted(n for n, c in table.items() if predicate(c))


E = "Scripts/Editor/"
# Frozen 2026-11-11; cross-checked by 62 independent read-only per-script agent reviews (310/310 field agreement).
BEFORE_CLEANUP_TRY = sorted([E + "run_author_aura_boostlite_production.ps1", E + "run_author_boss01_heavyswordsocket.ps1",
                             E + "run_export_sfx_batch3.ps1", E + "run_pie_ember_sword_probe_ag.ps1",
                             E + "run_restore_pack_heavyswordsocket.ps1", E + "run_verify_aura_boostlite_roundtrip.ps1",
                             "Scripts/RunLeadPie.ps1", "Scripts/Tools/run_c1249_editor_validation.ps1"])
SILENCED = sorted([E + "run_c1230b_ember_timing_audit.ps1", E + "run_c1231b_ember_notify_parity_build.ps1",
                   E + "run_c1232a_ember_notify_parity_build.ps1", E + "run_c1233a_ember_notify_parity_build.ps1",
                   E + "run_c1237a_montage_timing_opt_in_build.ps1", "Scripts/RunLeadPie.ps1"])
UNGUARDED_OWNERSHIP_READ = sorted([E + "run_aura_graph_authoring.ps1", E + "run_aura_graph_commandlet.ps1",
                                   E + "run_c1210_build_suite.ps1", E + "run_c1210_ember_aura_definition.ps1"])


class Bk181Corrections(unittest.TestCase):
    """X-2041 / A-847 corrections to BK-181..185 (that batch's files and evidence are preserved)."""

    def test_unique_tokens_are_nine_lock_writers(self):
        writers = [p for p in INV.EXTRA if INV.CENSUS[p]["create"] != "none"]
        tokens = sorted(p for p in writers if INV.CENSUS[p]["unique_token"])
        self.assertEqual(len(tokens), 9)
        self.assertTrue(INV.CENSUS["Scripts/Tests/TestRunLeadPieDryRun.ps1"]["unique_token"])  # 10th hit: temp-folder GUID
        self.assertIn("__dry_run_", read("Scripts/Tests/TestRunLeadPieDryRun.ps1"))

    def test_runleadpie_acquires_before_its_cleanup_try(self):
        """RunLeadPie.ps1 opens CreateNew at :59 and writes the payload inside an inner try whose finally only disposes
        the stream (:61-66); the try whose finally deletes the lock opens at :69. A payload/serialization exception
        between :59 and :69 leaves the lock stranded. DOCUMENTED ONLY - not edited or run, not separately assigned."""
        self.assertEqual(SCOPE["Scripts/RunLeadPie.ps1"],
                         {"write_line": 59, "release_line": 157, "try_line": 69, "finally_line": 156,
                          "acquire": "before_cleanup_try"})

    def test_new_item_exclusivity_now_requires_error_stop(self):
        """All 15 current lock New-Item writers are 'checked' (own -ErrorAction Stop or a prior global Stop)."""
        self.assertEqual(sum(1 for v in NEWITEM.values() if v == "checked"), 15)
        self.assertEqual(sum(1 for v in NEWITEM.values() if v in ("unchecked", "forced")), 0)


class Bk186InventoryReverification(unittest.TestCase):
    def test_independent_rederivation_matches(self):
        """Re-derive with os.walk + raw bytes (a different method from Path.rglob + text) and compare."""
        found = []
        for dirpath, _dirs, files in os.walk(ROOT / "Scripts"):
            for name in files:
                if name.lower().endswith(".ps1"):
                    data = (Path(dirpath) / name).read_bytes()
                    if b"ENGINE_LOCK" in data or b"C-1155" in data:
                        found.append((Path(dirpath) / name).relative_to(ROOT).as_posix())
        self.assertEqual(sorted(found), INV.ALL)
        owner = sorted(p for p in found if b"owner_token" in (ROOT / p).read_bytes())
        self.assertEqual(owner, INV.SUBSET)

    def test_split_is_34_28_1(self):
        extra_writers = len(WRITERS) - len(INV.SUBSET)
        self.assertEqual((len(INV.ALL), len(INV.SUBSET), extra_writers, len(INV.EXTRA) - extra_writers), (63, 34, 28, 1))
        self.assertEqual(len(WRITERS), 62)


class Bk187NewItemAdversarial(unittest.TestCase):
    CASES = {
        "New-Item -Path $lockFile -ItemType File -ErrorAction Stop | Out-Null": "checked",
        "New-Item -Path $lockFile -ItemType File -EA Stop": "checked",
        "New-Item -Path $lockFile -ItemType File -ErrorAction:Stop": "checked",
        "New-Item -Path $lockFile -ItemType File -ErrorAction 'Stop'": "checked",
        "New-Item -Path $lockFile -ItemType File | Out-Null": "unchecked",
        "New-Item -Path $lockFile -ItemType File -ErrorAction SilentlyContinue": "unchecked",
        "New-Item -Path $lockFile -ItemType File -ErrorAction Continue": "unchecked",
        "New-Item -Path $lockFile -ItemType File -ErrorAction Ignore": "unchecked",
        "New-Item -Path $lockFile -ItemType File -Force": "forced",
        "New-Item -Path $lockFile -ItemType File -Force -ErrorAction Stop": "forced",
        "New-Item -Path $path -ItemType File -Value $r -ErrorAction Stop": "checked",
    }

    def test_each_form(self):
        for line, expected in self.CASES.items():
            with self.subTest(line):
                self.assertEqual(new_item_exclusivity(line + "\n"), expected)

    def test_global_stop_only_counts_when_set_before(self):
        self.assertEqual(new_item_exclusivity("$ErrorActionPreference = 'Stop'\nNew-Item -Path $lockFile -ItemType File\n"), "checked")
        self.assertEqual(new_item_exclusivity("New-Item -Path $lockFile -ItemType File\n$ErrorActionPreference = 'Stop'\n"), "unchecked")
        self.assertEqual(new_item_exclusivity("$ErrorActionPreference = 'Stop'\n"
                                              "New-Item -Path $lockFile -ItemType File -ErrorAction SilentlyContinue\n"), "unchecked")

    def test_worst_site_wins_and_non_lock_new_item_is_ignored(self):
        two = "New-Item -Path $lockFile -ItemType File -ErrorAction Stop\nNew-Item -Path $lock2 -ItemType File\n"
        self.assertEqual(new_item_exclusivity(two), "unchecked")
        self.assertIsNone(new_item_exclusivity("New-Item -ItemType Directory -Path $outPath -Force\n"))
        self.assertIsNone(new_item_exclusivity("New-Item -Path $evidence -ItemType File\n"))


class Bk188AcquisitionScope(unittest.TestCase):
    def test_acquisition_relative_to_cleanup_try(self):
        """54 of 62 lock writers acquire inside the try whose finally releases; 8 acquire before it, so an exception
        between the write and the try leaves the lock behind (none of the 8 are in the owner_token subset)."""
        self.assertEqual(where(SCOPE, lambda c: c["acquire"] == "before_cleanup_try"), BEFORE_CLEANUP_TRY)
        self.assertEqual(len(where(SCOPE, lambda c: c["acquire"] == "inside_cleanup_try")), 54)
        self.assertEqual(set(BEFORE_CLEANUP_TRY) & set(INV.SUBSET), set())

    def test_scope_parser_on_synthetic_text(self):
        inside = "try {\n    Set-Content -Path $lockFile -Value x\n} finally {\n    Remove-Item $lockFile -Force\n}\n"
        before = "Set-Content -Path $lockFile -Value x\ntry {\n    work\n} finally {\n    Remove-Item $lockFile -Force\n}\n"
        self.assertEqual(cleanup_scope(inside)["acquire"], "inside_cleanup_try")
        self.assertEqual(cleanup_scope(before)["acquire"], "before_cleanup_try")
        self.assertEqual(cleanup_scope("Set-Content -Path $lockFile -Value x\n")["acquire"], "no_release")


class Bk189FailureVisibility(unittest.TestCase):
    def test_visibility_classes(self):
        """A failed release is warned in 34 runners (catch + Write-Warning), silenced in 6 (-ErrorAction
        SilentlyContinue: the lock can stay with no signal) and terminating in 22 (bare Remove-Item: the error ends
        the finally block, skipping any later lock release in the same block)."""
        counts = {k: len(where(VIS, lambda c, k=k: c["visibility"] == k)) for k in ("warned", "silenced", "terminating")}
        self.assertEqual(counts, {"warned": 34, "silenced": 6, "terminating": 22})
        self.assertEqual(where(VIS, lambda c: c["visibility"] == "silenced"), SILENCED)

    def test_stranded_lock_implications(self):
        self.assertEqual(where(VIS, lambda c: c["ownership_read_unguarded"]), UNGUARDED_OWNERSHIP_READ)
        self.assertEqual(len(where(VIS, lambda c: c["reports_created_as_released"])), 34)
        silent_and_counted = where(VIS, lambda c: c["visibility"] == "silenced" and c["reports_created_as_released"])
        self.assertEqual(len(silent_and_counted), 5)  # c123x: a failed delete is hidden AND reported as released


if __name__ == "__main__":
    unittest.main()
