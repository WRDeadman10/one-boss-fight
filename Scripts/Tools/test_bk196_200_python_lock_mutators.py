"""BK-196..200 (C, implementer; X-2045): source-only inventory of the non-.ps1 (Python) files under Scripts/ that mention
ENGINE_LOCK, and an analysis of the two Python lock mutators against the C-1155 PowerShell protocol.

Source-only: files are READ as text. Neither mutator is run, imported or edited; no lock, asset, editor or subprocess
is touched. Classes are code facts, risks are labelled as risks; no live event is claimed. X-1991 remains open.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "Scripts"
LATER_AUDIT = re.compile(r"^test_bk(\d+)_")  # audit files numbered BK-186+ were written after A-847/A-849


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8-sig", errors="replace")


def is_later_audit(path):
    match = LATER_AUDIT.match(path.name)
    return match is not None and int(match.group(1)) >= 186


def inventory():
    """BK-196 query: every Scripts/**/*.py (not .ps1, not __pycache__ / .pyc) whose text contains ENGINE_LOCK
    (case-sensitive), excluding audit files numbered BK-186 and later; sorted repo-relative POSIX paths."""
    found = []
    for path in SCRIPTS.rglob("*.py"):
        if "__pycache__" in path.parts or is_later_audit(path):
            continue
        if "ENGINE_LOCK" in path.read_text(encoding="utf-8-sig", errors="replace"):
            found.append(path.relative_to(ROOT).as_posix())
    return sorted(found)


WRITE = re.compile(r"open\([^)]*(LOCK|lock)[^)]*['\"]w['\"]|\.write_text\(|os\.open\([^)]*O_EXCL")
REMOVE = re.compile(r"os\.remove\(|os\.unlink\(|\.unlink\(")


def classify(rel):
    text = read(rel)
    if WRITE.search(text) or REMOVE.search(text):
        return "lock_mutator"
    if Path(rel).name.startswith("test_"):
        return "test_reference"
    if rel.startswith("Scripts/Editor/"):
        return "editor_precondition_doc"
    return "tool_constant_or_validator"


ALL = inventory()
CLASSES = {p: classify(p) for p in ALL}
RETARGET = "Scripts/Editor/retarget_mixamo_backstep.py"
C1003 = "Scripts/Editor/run_c1003_under_lock.py"


def line_of(rel, pattern):
    rx = re.compile(pattern)
    return next(i + 1 for i, line in enumerate(read(rel).splitlines()) if rx.search(line))


class Bk196Inventory(unittest.TestCase):
    def test_query_reproduces_the_original_32(self):
        self.assertEqual(len(ALL), 32)
        self.assertEqual(ALL, inventory())
        self.assertTrue(all(p.endswith(".py") for p in ALL))

    def test_boundary_excludes_caches_and_later_audit_files(self):
        later = sorted(p.relative_to(ROOT).as_posix() for p in SCRIPTS.rglob("*.py")
                       if is_later_audit(p) and "ENGINE_LOCK" in p.read_text(encoding="utf-8-sig", errors="replace"))
        self.assertIn("Scripts/Tools/test_bk186_190_c1155_lock_scope.py", later)
        self.assertIn("Scripts/Tools/test_bk196_200_python_lock_mutators.py", later)
        self.assertEqual(set(later) & set(ALL), set())
        self.assertFalse(any("__pycache__" in p for p in ALL))

    def test_classes(self):
        counts = {}
        for value in CLASSES.values():
            counts[value] = counts.get(value, 0) + 1
        self.assertEqual(sorted(p for p, c in CLASSES.items() if c == "lock_mutator"), sorted([RETARGET, C1003]))
        self.assertEqual(counts, {"lock_mutator": 2, "editor_precondition_doc": 12, "test_reference": 12,
                                  "tool_constant_or_validator": 6})


class Bk197RetargetMixamoBackstep(unittest.TestCase):
    def test_source_facts(self):
        text = read(RETARGET)
        self.assertEqual(line_of(RETARGET, r'^LOCK_PATH = "Docs/BossCombatReview/Execution/ENGINE_LOCK.json"'), 48)
        self.assertNotRegex(text, r"(?<!Execution/)ENGINE_LOCK\.json\"\s*$|Join[^\n]*'ENGINE_LOCK\.json'")  # no root lock
        self.assertEqual(line_of(RETARGET, r'if data\.get\("owner"\) != "AG":'), 98)       # any AG-owned lock is taken over
        self.assertEqual(line_of(RETARGET, r'with open\(full_lock, "w"'), 108)              # non-exclusive overwrite
        self.assertEqual(line_of(RETARGET, r"os\.remove\(full_lock\)"), 117)                # release: no owner/token check
        self.assertEqual(line_of(RETARGET, r'log_error\(f"Failed to release engine lock'), 120)  # failure only logged
        self.assertEqual((line_of(RETARGET, r"^    acquire_engine_lock\(proj\)"), line_of(RETARGET, r"^    finally:")), (350, 408))
        lines = text.splitlines()
        self.assertEqual(lines[350].strip(), "try:")  # :351 - the cleanup try opens only after the acquire call returns
        self.assertNotRegex(text, r"NewGuid|uuid|owner_token|token")                        # no run token at all

    def test_runs_inside_the_editor(self):
        """The lock is taken from INSIDE an already-running Unreal process (execute_pipeline only runs IN_ENGINE),
        the reverse of the C-1155 order: no Unreal process before both locks exist."""
        text = read(RETARGET)
        self.assertIn("import unreal", text)
        self.assertRegex(text, r"if not IN_ENGINE:\s*\n\s*ok, status = dry_check\(\)")


class Bk198RunC1003UnderLock(unittest.TestCase):
    def test_source_facts(self):
        text = read(C1003)
        self.assertEqual(line_of(C1003, r'^LOCK_PATH = os\.path\.join\(PROJECT_DIR, r"Docs\\BossCombatReview\\Execution\\ENGINE_LOCK\.json"\)'), 8)
        self.assertEqual(line_of(C1003, r"^if os\.path\.exists\(LOCK_PATH\):"), 13)        # check, then ...
        self.assertEqual(line_of(C1003, r'^with open\(LOCK_PATH, "w"'), 18)                 # ... non-exclusive write (TOCTOU)
        self.assertEqual(line_of(C1003, r"^try:"), 25)                                     # write happens BEFORE the try
        self.assertEqual(line_of(C1003, r"^        os\.remove\(LOCK_PATH\)"), 49)           # unconditional release in finally
        self.assertNotRegex(text, r"Get-Process|tasklist|psutil|UnrealEditor\.exe")         # no running-editor check
        self.assertNotRegex(text, r"token|uuid")

    def test_subprocess_boundary(self):
        """List-form argv (no shell), -nosound, 120 s timeout; the editor's return code is printed but never becomes
        this script's exit status, so a failed child still ends the script with exit 0."""
        text = read(C1003)
        self.assertRegex(text, r"subprocess\.run\(cmd, capture_output=True, text=True, timeout=120\)")
        self.assertNotIn("shell=True", text)
        self.assertIn('"-nosound"', text)
        self.assertNotRegex(text, r"sys\.exit\(res\.returncode\)|raise SystemExit\(res|check=True")


class Bk199ProtocolComparison(unittest.TestCase):
    """Facts compared with the C-1155 PowerShell protocol (BK-141..190 censuses)."""

    PROTOCOL = {  # C-1155 property -> (retarget_mixamo_backstep, run_c1003_under_lock)
        "both locks (root + execution)": (False, False),
        "no Unreal process before the lock": (False, False),
        "exclusive create (fails if present)": (False, False),
        "unique run token in the record": (False, False),
        "ownership-checked release": (False, False),
        "lock written inside the cleanup try": (False, False),
        "release in finally": (True, True),
    }

    def test_table_matches_source(self):
        r, c = read(RETARGET), read(C1003)
        observed = {
            "both locks (root + execution)": (bool(re.search(r"Join[^\n]*'ENGINE_LOCK\.json'", r)), bool(re.search(r'PROJECT_DIR, "ENGINE_LOCK\.json"', c))),
            "no Unreal process before the lock": ("import unreal" not in r, bool(re.search(r"tasklist|psutil|Get-Process", c))),
            "exclusive create (fails if present)": (bool(re.search(r"O_EXCL|'x'|\"x\"", r)), bool(re.search(r"O_EXCL|'x'|\"x\"", c))),
            "unique run token in the record": (bool(re.search(r"uuid|token", r)), bool(re.search(r"uuid|token", c))),
            "ownership-checked release": (bool(re.search(r"remove[\s\S]{0,200}owner", r[r.index("def release_engine_lock"):r.index("def dry_check")])),
                                          bool(re.search(r"finally:[\s\S]*owner", c))),
            # retarget writes inside acquire_engine_lock() (:108), called at :350 just BEFORE the try opens at :351
            "lock written inside the cleanup try": (line_of(RETARGET, r"^    acquire_engine_lock\(proj\)") > 351,
                                                    line_of(C1003, r'^with open\(LOCK_PATH, "w"') > line_of(C1003, r"^try:")),
            "release in finally": (line_of(RETARGET, r"release_engine_lock\(proj\)") > line_of(RETARGET, r"^    finally:"),
                                   line_of(C1003, r"os\.remove\(LOCK_PATH\)") > line_of(C1003, r"^finally:")),
        }
        self.assertEqual(observed, self.PROTOCOL)


if __name__ == "__main__":
    unittest.main()
