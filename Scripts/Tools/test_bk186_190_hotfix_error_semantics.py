"""X-2043 hotfix (C, implementer) for BK-186..190: PowerShell error semantics of bare `Remove-Item` lock releases.

BK-189 called all 22 bare (no -ErrorAction, no try/catch) lock `Remove-Item` releases "terminating". That holds only
where `$ErrorActionPreference = 'Stop'` is in effect: under PowerShell's default (Continue), a failed Remove-Item writes
a NON-terminating error record and the finally block continues. This module splits the 22 accordingly and recounts the
downstream stranded-lock claims. Source-only; no script is executed and no lock is touched. The BK-186..190 module and
report keep their original evidence; the report gets an append-only correction. X-1991 remains open.
"""
import importlib.util
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("lock_scope_bk186", HERE / "test_bk186_190_c1155_lock_scope.py")
S = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(S)

GLOBAL_STOP = re.compile(r"^\s*\$ErrorActionPreference\s*=\s*['\"]Stop['\"]", re.M)
ANY_PREFERENCE = re.compile(r"^\s*\$ErrorActionPreference\s*=\s*['\"](\w+)['\"]", re.M)


def effective_preference_at(text, line_no):
    """The last script-level `$ErrorActionPreference = '<x>'` assignment before line_no (1-based), else 'Continue'
    (the PowerShell default). Script-scope only; no runtime state is assumed."""
    value = "Continue"
    for match in ANY_PREFERENCE.finditer(text):
        if text.count("\n", 0, match.start()) + 1 < line_no:
            value = match.group(1)
    return value


def bare_release_semantics(path):
    """For a 'terminating'-class script (bare Remove-Item): 'terminating_stop' or 'non_terminating_default'."""
    text = S.read(path)
    preference = effective_preference_at(text, S.SCOPE[path]["release_line"])
    return "terminating_stop" if preference.lower() == "stop" else "non_terminating_default"


BARE = S.where(S.VIS, lambda c: c["visibility"] == "terminating")
SEMANTICS = {p: bare_release_semantics(p) for p in BARE}
E = "Scripts/Editor/"
NON_TERMINATING_DEFAULT = sorted(E + n for n in (
    "run_apply_notifies.ps1", "run_author_boss01_greatsword_sockets.ps1", "run_create_phase_two_aura_boost.ps1",
    "run_create_phase_two_aura_boost_lite.ps1", "run_export_sfx_candidates.ps1", "run_export_sfx_parry_addendum.ps1",
    "run_inspect_boss01_attach_transforms.ps1", "run_inspect_props.ps1", "run_reauthor_guard_counter_c1046.ps1",
    "run_rebuild_ppm.ps1", "run_verify_notifies.ps1"))
TERMINATING_STOP = sorted([E + n for n in (
    "run_aura_graph_authoring.ps1", "run_aura_graph_commandlet.ps1", "run_author_aura_boostlite_production.ps1",
    "run_author_boss01_heavyswordsocket.ps1", "run_c1210_build_suite.ps1", "run_c1210_ember_aura_definition.ps1",
    "run_export_sfx_batch3.ps1", "run_pie_ember_sword_probe_ag.ps1", "run_restore_pack_heavyswordsocket.ps1",
    "run_verify_aura_boostlite_roundtrip.ps1")] + ["Scripts/Tools/run_c1249_editor_validation.ps1"])


class ErrorSemantics(unittest.TestCase):
    def test_the_22_bare_releases_split_11_and_11(self):
        """Matches X-2043: the 11 listed files have no $ErrorActionPreference assignment (default Continue)."""
        self.assertEqual(len(BARE), 22)
        self.assertEqual(sorted(p for p, v in SEMANTICS.items() if v == "non_terminating_default"), NON_TERMINATING_DEFAULT)
        self.assertEqual(sorted(p for p, v in SEMANTICS.items() if v == "terminating_stop"), TERMINATING_STOP)

    def test_no_default_group_script_assigns_a_preference_anywhere(self):
        for path in NON_TERMINATING_DEFAULT:
            with self.subTest(path):
                self.assertIsNone(ANY_PREFERENCE.search(S.read(path)))

    def test_stop_group_sets_stop_before_the_release_and_never_changes_it(self):
        for path in TERMINATING_STOP:
            text = S.read(path)
            with self.subTest(path):
                self.assertEqual([m.group(1).lower() for m in ANY_PREFERENCE.finditer(text)], ["stop"])
                self.assertLess(text.count("\n", 0, GLOBAL_STOP.search(text).start()) + 1, S.SCOPE[path]["release_line"])

    def test_preference_resolution_on_synthetic_text(self):
        self.assertEqual(effective_preference_at("Remove-Item $lock\n", 1), "Continue")
        self.assertEqual(effective_preference_at("$ErrorActionPreference = 'Stop'\nRemove-Item $lock\n", 2), "Stop")
        self.assertEqual(effective_preference_at("Remove-Item $lock\n$ErrorActionPreference = 'Stop'\n", 1), "Continue")
        self.assertEqual(effective_preference_at("$ErrorActionPreference = \"Stop\"\n$ErrorActionPreference = 'Continue'\nRemove-Item $lock\n", 3),
                         "Continue")


class RecountedClaims(unittest.TestCase):
    def test_corrected_visibility_counts(self):
        """Corrected BK-189 table: warned 34, silenced 6, terminating (effective Stop) 11, non-terminating default 11."""
        counts = {"warned": len(S.where(S.VIS, lambda c: c["visibility"] == "warned")),
                  "silenced": len(S.where(S.VIS, lambda c: c["visibility"] == "silenced")),
                  "terminating_stop": len(TERMINATING_STOP), "non_terminating_default": len(NON_TERMINATING_DEFAULT)}
        self.assertEqual(counts, {"warned": 34, "silenced": 6, "terminating_stop": 11, "non_terminating_default": 11})

    def test_skip_later_release_claim_applies_only_to_multi_lock_stop_scripts(self):
        """'A failed release ends finally and skips later lock releases' needs BOTH effective Stop AND more than one
        lock to release in that finally. Of the 11 Stop scripts, 7 release both C-1155 locks (claim holds); 4 release
        a single lock (a failure strands only that lock). The 11 default-Continue scripts keep going after a failed
        delete (each lock may stay, but later releases still run)."""
        both = [p for p in TERMINATING_STOP if S.INV.CENSUS[p]["lock_paths"] == "both"]
        single = [p for p in TERMINATING_STOP if S.INV.CENSUS[p]["lock_paths"] != "both"]
        self.assertEqual(len(both), 7)
        self.assertEqual(sorted(single), sorted([E + "run_author_boss01_heavyswordsocket.ps1",
                                                 E + "run_pie_ember_sword_probe_ag.ps1",
                                                 E + "run_restore_pack_heavyswordsocket.ps1",
                                                 "Scripts/Tools/run_c1249_editor_validation.ps1"]))

    def test_unguarded_ownership_read_claim_still_holds(self):
        """All 4 unguarded-ownership-read scripts are in the effective-Stop group, so their abort-the-loop claim stands."""
        self.assertTrue(set(S.UNGUARDED_OWNERSHIP_READ) <= set(TERMINATING_STOP))


if __name__ == "__main__":
    unittest.main()
