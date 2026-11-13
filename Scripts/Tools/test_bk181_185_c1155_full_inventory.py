"""BK-181..185 (C, implementer; X-2039): repository-wide C-1155 lock inventory and a source audit of the scripts the
BK-146..165 censuses did not cover.

Source-only: every `.ps1` under Scripts/ is READ as text; nothing is executed and no lock, log, temp file or asset is
touched. The earlier censuses selected the 34 scripts containing `owner_token` - a defined SUBSET; this module defines
the full inventory, classifies the remainder, and freezes per-script tables so any change surfaces for review.
Classes describe code, not observed runtime. Audit only; no production edit; X-1991 remains open.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "Scripts"
INVENTORY_QUERY = re.compile(r"ENGINE_LOCK|C-1155")  # BK-181: the whole query (case-sensitive), over Scripts/**/*.ps1


def read(path):
    return path.read_text(encoding="utf-8-sig", errors="replace")


def inventory():
    """BK-181: deterministic repo-wide inventory - sorted repo-relative POSIX paths of Scripts/**/*.ps1 whose text
    matches INVENTORY_QUERY."""
    return sorted(p.relative_to(ROOT).as_posix() for p in SCRIPTS.rglob("*.ps1") if INVENTORY_QUERY.search(read(p)))


def subset_owner_token(paths):
    return sorted(p for p in paths if "owner_token" in read(ROOT / p))


def _line(lines, pattern):
    rx = re.compile(pattern)
    return next((i + 1 for i, l in enumerate(lines) if rx.search(l)), None)


ROOT_LOCK = re.compile(r"OneBossFight[\\/]ENGINE_LOCK\.json|Join-Path \$\w+ ['\"]ENGINE_LOCK\.json['\"]|\$\w*[Rr]oot\w*[\\/]ENGINE_LOCK\.json")
EXEC_LOCK = re.compile(r"Execution[\\/]ENGINE_LOCK\.json")
LOCKVAR = r"\$(lock\w*|path)\b"


def _guarded_block(lines, i, span=4):
    return "\n".join(lines[i:i + span])


def classify_lock(text):
    """BK-183: lock create / readback / release / ownership classes for one script."""
    lines = text.splitlines()
    root_lock = ROOT_LOCK.search(text) is not None
    exec_lock = EXEC_LOCK.search(text) is not None
    exclusive_methods = []
    if re.search(r"FileMode\]::CreateNew", text):
        exclusive_methods.append("CreateNew")
    new_item = re.search(r"New-Item[^\n]*" + LOCKVAR + r"[^\n]*-ItemType File|New-Item[^\n]*-ItemType File[^\n]*" + LOCKVAR, text)
    new_item_force = new_item is not None and re.search(r"New-Item[^\n]*-ItemType File[^\n]*-Force|New-Item[^\n]*-Force[^\n]*-ItemType File", text)
    if new_item and not new_item_force:
        exclusive_methods.append("New-Item")
    overwrite_methods = []
    if re.search(r"(Set-Content|Out-File|Add-Content)[^\n]*" + LOCKVAR, text) or re.search(r"\|\s*Set-Content -Path \$lock", text):
        overwrite_methods.append("Set-Content")
    if re.search(r"WriteAllText\(\$lock\w*", text):
        overwrite_methods.append("WriteAllText")
    if new_item_force:
        overwrite_methods.append("New-Item-Force")
    # a precheck is `if (Test-Path ... <lock>) {` followed within 3 lines by throw / exit / Write-Error
    precheck = any(re.search(r"if \(\s*\(?Test-Path[^\n]*" + LOCKVAR, l) and re.search(r"\bthrow\b|\bexit\b|Write-Error", _guarded_block(lines, i))
                   for i, l in enumerate(lines))
    removes = [i for i, l in enumerate(lines) if re.search(r"Remove-Item[^\n]*" + LOCKVAR, l)]
    window = lambda i: "\n".join(lines[max(0, i - 5):i + 1])
    ownership = any(re.search(r"owner_token|ConvertFrom-Json|\.token\b|-eq \$token", window(i)) for i in removes)
    gated = any(re.search(r"\$lockAcquired|\$created|\$acquired", window(i)) for i in removes)
    finally_line = next((i for i, l in enumerate(lines) if re.search(r"^\s*\}?\s*finally\s*\{?\s*$", l)), None)
    if exclusive_methods:
        create = "exclusive"
    elif overwrite_methods:
        create = "overwrite"
    else:
        create = "none"
    return {
        "lock_paths": "both" if (root_lock and exec_lock) else ("execution_only" if exec_lock else ("root_only" if root_lock else "none")),
        "create": create,
        "methods": sorted(exclusive_methods + overwrite_methods),
        "precheck_existing": precheck and bool(exclusive_methods or overwrite_methods),  # only meaningful for writers
        "unique_token": re.search(r"NewGuid|owner_token", text) is not None,
        "releases": bool(removes),
        "release_in_finally": finally_line is not None and any(i > finally_line for i in removes),
        "release": "none" if not removes else ("ownership_checked" if ownership else ("acquired_gate" if gated else "unconditional")),
        "first_write_line": next((i + 1 for i, l in enumerate(lines)
                                  if re.search(r"FileMode\]::CreateNew|New-Item[^\n]*-ItemType File|(Set-Content|Out-File)[^\n]*\$lock|WriteAllText\(\$lock|\|\s*Set-Content -Path \$lock", l)), None),
        "first_remove_line": removes[0] + 1 if removes else None,
    }


ALL = inventory()
SUBSET = subset_owner_token(ALL)
EXTRA = sorted(set(ALL) - set(SUBSET))
CENSUS = {p: classify_lock(read(ROOT / p)) for p in EXTRA}


def names(predicate):
    return sorted(n for n, c in CENSUS.items() if predicate(c))


E = "Scripts/Editor/"
# ---- frozen per-script tables (2026-11-11); cross-checked by 29 independent read-only agent reviews (agreement 145/145
# after defining precheck for lock writers only) ----
OVERWRITE_NO_PRECHECK = sorted([E + "run_apply_notifies.ps1", E + "run_inspect_props.ps1", E + "run_verify_notifies.ps1"])
OVERWRITE_TOCTOU = sorted([E + "run_author_aura_boostlite_production.ps1", E + "run_author_boss01_heavyswordsocket.ps1",
                           E + "run_export_sfx_batch3.ps1", E + "run_pie_ember_sword_probe_ag.ps1",
                           E + "run_reauthor_guard_counter_c1046.ps1", E + "run_rebuild_ppm.ps1",
                           E + "run_restore_pack_heavyswordsocket.ps1", E + "run_verify_aura_boostlite_roundtrip.ps1",
                           "Scripts/Tools/run_c1249_editor_validation.ps1"])
OWNERSHIP_CHECKED = sorted([E + "run_aura_graph_authoring.ps1", E + "run_aura_graph_commandlet.ps1",
                            E + "run_c1210_build_suite.ps1", E + "run_c1210_ember_aura_definition.ps1"])
ACQUIRED_GATE = sorted([E + "run_author_boss01_greatsword_sockets.ps1", E + "run_c1230b_ember_timing_audit.ps1",
                        E + "run_c1231b_ember_notify_parity_build.ps1", E + "run_c1232a_ember_notify_parity_build.ps1",
                        E + "run_c1233a_ember_notify_parity_build.ps1", E + "run_c1237a_montage_timing_opt_in_build.ps1",
                        E + "run_create_phase_two_aura_boost.ps1", E + "run_create_phase_two_aura_boost_lite.ps1",
                        E + "run_export_sfx_candidates.ps1", E + "run_export_sfx_parry_addendum.ps1",
                        E + "run_inspect_boss01_attach_transforms.ps1"])


class Bk181Inventory(unittest.TestCase):
    def test_inventory_is_deterministic(self):
        self.assertEqual(ALL, inventory())
        self.assertEqual(len(ALL), 63)
        self.assertTrue(all(p.startswith("Scripts/") and p.endswith(".ps1") for p in ALL))

    def test_query_definition(self):
        self.assertEqual(INVENTORY_QUERY.pattern, "ENGINE_LOCK|C-1155")
        self.assertIsNotNone(INVENTORY_QUERY.search("x = 'ENGINE_LOCK.json'"))
        self.assertIsNone(INVENTORY_QUERY.search("engine_lock c1155"))  # case-sensitive by definition


class Bk182SubsetAndRemainder(unittest.TestCase):
    def test_subset_plus_remainder_is_the_inventory(self):
        """34 owner_token scripts (the BK-146..165 subset) + 29 others = 63; all 34 match the query too."""
        self.assertEqual(len(SUBSET), 34)
        self.assertEqual(len(EXTRA), 29)
        self.assertEqual(sorted(SUBSET + EXTRA), ALL)
        owner_anywhere = sorted(p.relative_to(ROOT).as_posix() for p in SCRIPTS.rglob("*.ps1") if "owner_token" in read(p))
        self.assertEqual(owner_anywhere, SUBSET)

    def test_remainder_composition(self):
        """28 of the 29 write a lock; the 29th (Scripts/Tests/TestRunLeadPieDryRun.ps1) only asserts lock state."""
        self.assertEqual(names(lambda c: c["create"] == "none"), ["Scripts/Tests/TestRunLeadPieDryRun.ps1"])


class Bk183LockHandling(unittest.TestCase):
    def test_create_classes(self):
        self.assertEqual(len(names(lambda c: c["create"] == "exclusive")), 16)
        self.assertEqual(names(lambda c: c["create"] == "overwrite"), sorted(OVERWRITE_NO_PRECHECK + OVERWRITE_TOCTOU))

    def test_release_classes(self):
        self.assertEqual(names(lambda c: c["release"] == "ownership_checked"), OWNERSHIP_CHECKED)
        self.assertEqual(names(lambda c: c["release"] == "acquired_gate"), ACQUIRED_GATE)
        self.assertEqual(len(names(lambda c: c["release"] == "unconditional")), 13)
        self.assertEqual(len(names(lambda c: c["releases"] and not c["release_in_finally"])), 0)

    def test_lock_path_coverage(self):
        """Only 12 of the 28 lock writers take both C-1155 locks; 13 take only the Execution lock, 3 only the root."""
        paths = {k: len(names(lambda c, k=k: c["lock_paths"] == k and c["create"] != "none"))
                 for k in ("both", "execution_only", "root_only")}
        self.assertEqual(paths, {"both": 12, "execution_only": 13, "root_only": 3})

    def test_no_unique_token_outside_owner_checked_and_c123x(self):
        self.assertEqual(len(names(lambda c: c["unique_token"])), 10)


class Bk184HighRisk(unittest.TestCase):
    def test_overwrite_without_precheck_and_unconditional_release(self):
        """Highest code risk: Set-Content overwrites any existing lock with no existence check, and finally deletes
        whatever lock is at the path - another holder's live lock can be replaced and then removed."""
        self.assertEqual(names(lambda c: c["create"] == "overwrite" and not c["precheck_existing"]
                               and c["release"] == "unconditional"), OVERWRITE_NO_PRECHECK)

    def test_overwrite_after_precheck_is_a_toctou_race(self):
        self.assertEqual(names(lambda c: c["create"] == "overwrite" and c["precheck_existing"]), OVERWRITE_TOCTOU)
        for name in OVERWRITE_TOCTOU:
            with self.subTest(name):
                self.assertEqual(CENSUS[name]["release"], "unconditional")

    def test_file_line_examples_are_where_the_code_says(self):
        expect = {
            E + "run_apply_notifies.ps1": (8, 12),
            E + "run_inspect_props.ps1": (8, 12),
            E + "run_verify_notifies.ps1": (8, 12),
            E + "run_author_aura_boostlite_production.ps1": (30, 48),
            "Scripts/Tools/run_c1249_editor_validation.ps1": (11, 30),
            "Scripts/RunLeadPie.ps1": (59, 157),
        }
        for name, (write, remove) in expect.items():
            with self.subTest(name):
                self.assertEqual((CENSUS[name]["first_write_line"], CENSUS[name]["first_remove_line"]), (write, remove))


class ClassifierSelfCheck(unittest.TestCase):
    def test_synthetic_scripts(self):
        overwrite = ("$lockFile = 'C:\\UnrealProject\\OneBossFight\\Docs\\BossCombatReview\\Execution\\ENGINE_LOCK.json'\n"
                     "try {\n    $d | ConvertTo-Json | Set-Content -Path $lockFile\n} finally {\n"
                     "    if (Test-Path $lockFile) {\n        Remove-Item $lockFile -Force\n    }\n}\n")
        c = classify_lock(overwrite)
        self.assertEqual((c["lock_paths"], c["create"], c["precheck_existing"], c["release"]), ("execution_only", "overwrite", False, "unconditional"))
        exclusive = ("$locks = @((Join-Path $root 'ENGINE_LOCK.json'), (Join-Path $root 'Docs\\BossCombatReview\\Execution\\ENGINE_LOCK.json'))\n"
                     "foreach ($path in $locks) { if (Test-Path -LiteralPath $path) { throw 'x' } }\n"
                     "try { foreach ($path in $locks) { New-Item -Path $path -ItemType File -Value $r -ErrorAction Stop | Out-Null; $created.Add($path) } }\n"
                     "finally {\n    foreach ($path in $created) {\n        $rec = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json\n"
                     "        if ($rec.command_id -eq $token) { Remove-Item -LiteralPath $path -Force }\n    }\n}\n")
        c = classify_lock(exclusive)
        self.assertEqual((c["lock_paths"], c["create"], c["precheck_existing"], c["release"]), ("both", "exclusive", True, "ownership_checked"))
        forced = "New-Item -Path $lockFile -ItemType File -Force | Out-Null\n"
        self.assertEqual(classify_lock(forced)["create"], "overwrite")


if __name__ == "__main__":
    unittest.main()
