"""BK-201..205 (C, implementer; X-2049): references, invocation paths and lock-record schema compatibility for the two
legacy Python lock mutators (Scripts/Editor/retarget_mixamo_backstep.py, Scripts/Editor/run_c1003_under_lock.py).

Source-only: files are READ as text; neither mutator (nor the C-1003 child) is run or imported, and no lock, asset,
editor or subprocess is touched. Unknowns are stated in the report, not asserted here. X-1991 remains open.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RETARGET = "Scripts/Editor/retarget_mixamo_backstep.py"
C1003 = "Scripts/Editor/run_c1003_under_lock.py"
CHILD = "Scripts/Editor/set_strong_attack_data_c1003.py"
NAMES = ("retarget_mixamo_backstep", "run_c1003_under_lock")
SKIP_DIRS = {".git", "Saved", "Intermediate", "Binaries", "DerivedDataCache", "__pycache__", "Content", "Ref"}
SOURCE_SUFFIXES = {".py", ".ps1", ".bat", ".cmd"}  # executable/source call-site boundary (BK-202)
TEXT_SUFFIXES = {".py", ".ps1", ".bat", ".cmd", ".md", ".json", ".ini", ".txt", ".yml", ".yaml", ".cfg", ".uproject"}


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8-sig", errors="replace")


def walk_text_files():
    for path in ROOT.rglob("*"):
        if path.suffix.lower() not in TEXT_SUFFIXES or not path.is_file():
            continue
        if SKIP_DIRS & set(path.relative_to(ROOT).parts):
            continue
        yield path


def references():
    """BK-201: every text file (outside build/output dirs) naming either mutator, excluding the mutators themselves
    and audit files numbered BK-196 and later."""
    hits = {}
    for path in walk_text_files():
        rel = path.relative_to(ROOT).as_posix()
        if rel in (RETARGET, C1003):
            continue
        m = re.match(r"test_bk(\d+)_", path.name)
        if m and int(m.group(1)) >= 196:
            continue
        if path.name.startswith("BK_") and re.match(r"BK_(\d+)_", path.name) and int(re.match(r"BK_(\d+)_", path.name).group(1)) >= 196:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        found = [n for n in NAMES if n in text]
        if found:
            hits[rel] = found
    return dict(sorted(hits.items()))


def classify_reference(rel):
    """BK-202: invocation = a launcher that could run the file (ps1/bat/cmd, or py using subprocess/ExecutePythonScript
    with the name); test = a test module; doc = everything else."""
    text = read(rel)
    if Path(rel).suffix in (".ps1", ".bat", ".cmd"):
        return "invocation"
    if Path(rel).suffix == ".py" and re.search(r"subprocess|ExecutePythonScript|-script=", text) and any(n in text for n in NAMES):
        return "invocation"
    if Path(rel).name.startswith("test_"):
        return "test"
    return "doc"


REFS = references()


class Bk201References(unittest.TestCase):
    def test_reference_inventory(self):
        self.assertEqual(sorted(REFS), sorted([
            "Documentation/KNOWN_ISSUES.md", "Documentation/TASKS.md", "Documentation/TEAM_MAILBOX.md",
            "scratch/test_retarget_mixamo_backstep_offline.py"]))

    def test_both_mutators_are_tracked_source(self):
        self.assertTrue((ROOT / RETARGET).is_file() and (ROOT / C1003).is_file())


class Bk202InvocationPaths(unittest.TestCase):
    def test_no_launcher_invokes_either_mutator(self):
        """No .ps1/.bat/.cmd or subprocess-launching .py in the working tree names either mutator; every reference is
        documentation or a test, so neither is reachable from an existing runner (manual launch remains possible)."""
        classes = {rel: classify_reference(rel) for rel in REFS}
        self.assertEqual(sorted(r for r, c in classes.items() if c == "invocation"), [])
        self.assertEqual(classes["scratch/test_retarget_mixamo_backstep_offline.py"], "test")

    def test_scratch_test_cannot_load_the_real_mutator(self):
        """The untracked scratch test resolves `Path(__file__).with_name("retarget_mixamo_backstep.py")`, i.e.
        scratch/retarget_mixamo_backstep.py, which does not exist - it never loads Scripts/Editor/...."""
        text = read("scratch/test_retarget_mixamo_backstep_offline.py")
        self.assertIn('Path(__file__).with_name("retarget_mixamo_backstep.py")', text)
        self.assertFalse((ROOT / "scratch" / "retarget_mixamo_backstep.py").exists())

    def test_retarget_mutates_assets_only_after_its_lock_helper(self):
        """Asset work in retarget lives in execute_pipeline after acquire_engine_lock(); the no-FBX path returns before
        any lock or asset write, and outside the editor only dry_check() runs."""
        text = read(RETARGET)
        body = text[text.index("def execute_pipeline"):text.index("def main")]
        self.assertLess(body.index("return True"), body.index("acquire_engine_lock(proj)"))  # no-FBX early return
        self.assertLess(body.index("acquire_engine_lock(proj)"), body.index("get_asset_tools()"))

    def test_c1003_child_has_no_lock_of_its_own(self):
        """The asset-writing child set_strong_attack_data_c1003.py contains no lock handling and is referenced only by
        run_c1003_under_lock.py: launched directly (manual -ExecutePythonScript) it runs with NO lock."""
        child = read(CHILD)
        self.assertNotRegex(child, r"(?i)engine_lock|lock")
        self.assertIn("unreal.load_asset", child)
        # X-2052: caller boundary = executable/source files only (.py/.ps1/.bat/.cmd), excluding the child itself and
        # audit tests; documentation (mailbox, reports) may name the child and is inventoried separately in BK-201.
        users = [p.relative_to(ROOT).as_posix() for p in walk_text_files()
                 if p.suffix.lower() in SOURCE_SUFFIXES
                 and "set_strong_attack_data_c1003" in p.read_text(encoding="utf-8-sig", errors="replace")
                 and p.relative_to(ROOT).as_posix() != CHILD and not re.match(r"test_bk(\d+)_", p.name)]
        self.assertEqual(users, [C1003])

    def test_documentation_mentions_of_the_child_are_not_callers(self):
        docs = [p.relative_to(ROOT).as_posix() for p in walk_text_files()
                if p.suffix.lower() not in SOURCE_SUFFIXES
                and "set_strong_attack_data_c1003" in p.read_text(encoding="utf-8-sig", errors="replace")]
        self.assertTrue(all(d.endswith((".md", ".txt", ".json")) for d in docs), docs)


class Bk203RecordSchemas(unittest.TestCase):
    def test_legacy_record_keys(self):
        r, c = read(RETARGET), read(C1003)
        self.assertRegex(r, r'"purpose":[\s\S]{0,120}"owner": "AG",[\s\S]{0,80}"startTime": time\.strftime\("%Y-%m-%d %H:%M:%S"\)')
        self.assertRegex(c, r'"owner": "AG",\s*\n\s*"task": [^\n]*\n\s*"acquired_at": time\.strftime\("%Y-%m-%dT%H:%M:%S"\)')
        for text in (r, c):
            self.assertNotRegex(text, r"owner_token|command_id|policy|party|pid")

    def test_c1155_records_carry_no_owner_key(self):
        """C-1155 runner records use agent/party/owner_token/policy; none writes an `owner` key, so retarget's
        `data.get("owner") != "AG"` check refuses (does not take over) a C-1155 lock."""
        for rel in ("Scripts/Editor/run_bk56_60_deferred_selection.ps1", "Scripts/Editor/run_c1280_x26_locked_validation.ps1"):
            with self.subTest(rel):
                record = next(l for l in read(rel).splitlines() if re.match(r"\s*\$record\s*=", l))
                self.assertIn("owner_token=$token", record)
                self.assertNotRegex(record, r"\bowner=")

    def test_token_readers_never_match_a_legacy_record(self):
        """The 34 owner_token-comparing PowerShell releases delete only on a token match; a legacy AG record has no
        owner_token, so they never delete it (and their prechecks refuse to start while it exists)."""
        readers = [p for p in (ROOT / "Scripts").rglob("*.ps1") if re.search(r"\$\w+\.owner_token -c?eq \$token", p.read_text(encoding="utf-8-sig", errors="replace"))]
        self.assertEqual(len(readers), 34)


if __name__ == "__main__":
    unittest.main()
