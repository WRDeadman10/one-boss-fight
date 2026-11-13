"""BP-31..34 (C, implementer; Queue BP batch 7) under X-2295: in-process tests for previously untested tools.

No main(), CLI or subprocess is run. Each test imports a tool module (import-time safety proven by cli_static_contract)
and calls a pure helper on in-memory text or on files inside a TemporaryDirectory.
  BP-32: existing helpers - check_headers_selfcontained.inspect, compare_framework_tokens.count, diff_manifests.load.
  BP-33: cores extracted from main() by a behaviour-preserving refactor - log_failures.find_failures and
         mailbox_stats.party_day_counts; each is compared with the exact inline expression main() used before.
Paths touched: a TemporaryDirectory only.
"""
import collections
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_headers_selfcontained as headers  # noqa: E402
import compare_framework_tokens as tokens  # noqa: E402
import diff_manifests as manifests  # noqa: E402
import log_failures  # noqa: E402
import mailbox_stats  # noqa: E402

LOG = ("ok line\nERROR: something broke\nwarning only\nTest failed here   \nfatal error C1083\n"
       "assertion failed: x\nerrorless word\nfailureMode\n")
MAILBOX = ("### [C-1] Claude -> Codex, 2026-11-12 10:00\nbody\n### [X-2] Codex -> Claude, 2026-11-12 11:00\n"
           "### [C-3] Claude -> Codex (lead) and Antigravity, 2026-11-12 12:00\n### [A-4] Antigravity -> Codex, 2026-11-13 01:00\n"
           "not a header ### [C-5] x -> y, 2026-11-13\n")


class Temp(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def put(self, name, text):
        path = self.dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        return path


class Bp32ExistingHelpers(Temp):
    def test_inspect_flags_header_problems(self):
        src = self.dir / "Source"
        (src / "Player").mkdir(parents=True)
        (src / "Player" / "Real.h").write_text("", encoding="utf-8")
        bad = self.put("Bad.h", '#include "X.generated.h"\n#include "Player/Missing.h"\nstd::vector<int> v; FVector p;\n')
        found = headers.inspect(bad, src)
        self.assertIn("uses std:: without an apparent standard-library include", found)
        self.assertIn("uses common Unreal core types without CoreMinimal/CoreTypes include", found)
        self.assertIn("generated header is not the final include", found)
        self.assertIn("project include not found: Player/Missing.h", found)
        good = self.put("Good.h", '#include "CoreMinimal.h"\n#include <vector>\n#include "Player/Real.h"\n#include "G.generated.h"\nstd::vector<int> v; FVector p;\n')
        self.assertEqual(headers.inspect(good, src), [])

    def test_count_framework_tokens(self):
        log = self.put("f.log", "[FrameworkProof] hit a=1\n[FrameworkProof] hit b=2\n[FrameworkProof]   decision\nnoise\n")
        self.assertEqual(tokens.count(log), collections.Counter({"hit": 2, "decision": 1}))

    def test_load_manifest(self):
        digest = "A" * 64
        path = self.put("m.txt", f"# comment\n\n{digest}  dir/file.txt\n{'b' * 64} *bin.dat\n")
        self.assertEqual(manifests.load(path), {"dir/file.txt": "a" * 64, "bin.dat": "b" * 64})
        bad = self.put("bad.txt", "not-a-hash file\n")
        with self.assertRaises(ValueError) as caught:
            manifests.load(bad)
        self.assertIn(f"{bad}:1", str(caught.exception))


class Bp33ExtractedCores(unittest.TestCase):
    def test_find_failures_matches_former_inline_expression(self):
        former = [(n, line.rstrip()) for n, line in enumerate(LOG.splitlines(), 1) if log_failures.FAIL.search(line)]
        self.assertEqual(log_failures.find_failures(LOG), former)
        self.assertEqual([n for n, _ in former], [2, 4, 5, 6])
        self.assertEqual(log_failures.find_failures(""), [])

    def test_party_day_counts_matches_former_inline_expression(self):
        former = collections.Counter((p, d) for p, _, _, d in mailbox_stats.HEADER.findall(MAILBOX))
        self.assertEqual(mailbox_stats.party_day_counts(MAILBOX), former)
        self.assertEqual(former, collections.Counter({("C", "2026-11-12"): 2, ("X", "2026-11-12"): 1, ("A", "2026-11-13"): 1}))


class Bp34RemainingMainOnlyTools(unittest.TestCase):
    """X-2308: one in-process test per remaining main-only tool, on the core extracted verbatim from its main()."""

    def test_check_line_endings(self):
        import check_line_endings as m
        self.assertIsNone(m.line_ending_counts(b"bin\0ary\n"))
        self.assertEqual(m.line_ending_counts(b"a\r\nb\nc\rd\r\n"), (2, 1, 1))
        self.assertFalse(m.is_mixed(*m.line_ending_counts(b"a\r\nb\r\n")))
        self.assertFalse(m.is_mixed(*m.line_ending_counts(b"a\nb\n")))
        self.assertTrue(m.is_mixed(*m.line_ending_counts(b"a\r\nb\n")))
        self.assertTrue(m.is_mixed(*m.line_ending_counts(b"a\rb")))

    def test_check_test_plan_ids(self):
        import check_test_plan_ids as m
        ids, dups = m.build_ids("| BUILD-001 | x |\n| BUILD-003 | y |\n| BUILD-002 | z |\n| BUILD-003 | w |\n not | BUILD-9 |\n")
        self.assertEqual(ids, [1, 3, 2, 3])
        self.assertEqual(dups, [3])
        self.assertEqual(m.build_ids("| BUILD-010 | a |\n"), ([10], []))

    def test_list_cvars(self):
        import list_cvars as m
        text = ('static TAutoConsoleVariable<int32> CVarA(\n    TEXT("rpg.Alpha"),\n    0, TEXT("help"));\n'
                'TAutoConsoleVariable<float> CVarB(TEXT("rpg.Beta."), 1.f, TEXT("x"));\n'
                '  RPG_PERF_SWITCH(Gi, "GiOff")\n// TEXT("rpg.InComment") outside a registration\n')
        self.assertEqual(m.registrations(text, "Source/X.cpp"),
                         {("rpg.Alpha", "Source/X.cpp", 1), ("rpg.Perf.GiOff", "Source/X.cpp", 5)})

    def test_list_todo_markers(self):
        import list_todo_markers as m
        self.assertEqual(m.marker_lines("ok\n// TODO: x\nfixme later\nTODOS plural\nxxx\n"),
                         [(2, "// TODO: x"), (3, "fixme later"), (5, "xxx")])

    def test_source_metrics(self):
        import source_metrics as m
        source = Path("C:/repo/Source/OneBossFight")
        self.assertEqual(m.file_metrics(source / "Player" / "A.cpp", source, "a\nb\nIMPLEMENT_SIMPLE_AUTOMATION_TEST(X)\n"),
                         ("Player", 3, False, 0))
        self.assertEqual(m.file_metrics(source / "Tests" / "T.cpp", source,
                                        "IMPLEMENT_SIMPLE_AUTOMATION_TEST(A)\nIMPLEMENT_AUTOMATION_TEST(B)\n"), ("Tests", 2, True, 2))
        self.assertEqual(m.file_metrics(source / "Root.h", source, ""), ("(root)", 0, False, 0))

    def test_new_profile_field_scaffold(self):
        import new_profile_field_scaffold as m
        lines = m.checklist_lines("MyField", None, None, False)
        self.assertEqual(lines[0], "Eight edit/review sites for profile field MyField (disabled default required):")
        self.assertEqual(len(lines), 1 + 8 + 3)
        self.assertIn("Framework.Profile.<choose-token-for-MyField>", lines[2])
        self.assertTrue(lines[8].endswith("not applicable unless this change adds a CVar/test hook"))
        hooked = m.checklist_lines("MyField", "Framework.Profile.X", "Tok", True)
        self.assertIn("include only when adding a CVar/test hook", hooked[8])
        self.assertEqual(hooked[-3], "Chosen error token: Framework.Profile.X")
        self.assertEqual(hooked[-2], "Chosen emission token: Tok")


if __name__ == "__main__":
    unittest.main()
