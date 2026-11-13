"""BM-06..10 (C, implementer; lane BM batch 2): repo-wide Python parse census over Scripts/**/*.py.

Static only: every script is parsed with ast.parse (never imported or executed). Guards KI-170/171-style regressions: a script that
cannot even be parsed is silently unverifiable. Census on 2026-11-12: 990 files, 0 parse failures in the WORKING TREE. The two KI
files parse only because of uncommitted working-tree repairs (their HEAD versions still fail); see BM_06_10_PARSE_CENSUS.md.
"""
import ast
import unittest
import warnings
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "Scripts"
KI_FILES = ("Scripts/author_brief13_anims.py", "Scripts/Editor/sevarog_pack_02_montages_abilities.py")


def census():
    failures = []
    files = [p for p in SCRIPTS.rglob("*.py") if "__pycache__" not in p.parts]
    for path in files:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")  # invalid-escape SyntaxWarnings are not parse failures
                ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        except (SyntaxError, ValueError, UnicodeDecodeError) as error:
            failures.append(f"{path.relative_to(REPO).as_posix()}: {type(error).__name__}: {error}")
    return files, failures


class PythonParseCensus(unittest.TestCase):
    def test_every_script_parses(self):
        files, failures = census()
        self.assertGreater(len(files), 900, "the census must actually scan the Scripts tree")
        self.assertEqual(failures, [])

    def test_known_issue_files_parse_in_the_working_tree(self):
        for rel in KI_FILES:
            with self.subTest(file=rel):
                ast.parse((REPO / rel).read_text(encoding="utf-8-sig"))


if __name__ == "__main__":
    unittest.main()
