"""X-2290 hotfix (C, implementer): adversarial tests for cli_static_contract. Static only: fixtures are written to a temp
folder and only PARSED by the contract; no fixture or tool is ever imported or executed."""
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cli_static_contract as contract  # noqa: E402

SAFE = '''
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description="x")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    Path(args.root, "out.txt").write_text("x")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


class ContractFixtures(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def verdict(self, source, name="tool", extra=None):
        for other, text in (extra or {}).items():
            (self.dir / f"{other}.py").write_text(textwrap.dedent(text), encoding="utf-8")
        path = self.dir / f"{name}.py"
        path.write_text(textwrap.dedent(source), encoding="utf-8")
        return contract.analyse(path)

    def test_safe_baseline_is_proven(self):
        ok, reason = self.verdict(SAFE)
        self.assertTrue(ok, reason)

    def test_x2291_nested_uncalled_parse_cannot_hide_a_side_effect(self):
        """Codex's counter-example: a nested helper containing parse_args lexically precedes a real side effect."""
        ok, reason = self.verdict('''
            import argparse, subprocess
            def main():
                def helper():
                    argparse.ArgumentParser().parse_args()
                subprocess.run(["ffmpeg", "-y", "out.mp4"])
                parser = argparse.ArgumentParser()
                return parser.parse_args()
            if __name__ == "__main__":
                main()
        ''')
        self.assertFalse(ok)
        self.assertIn("FunctionDef before parse_args", reason)

    def test_branch_before_parse_is_rejected(self):
        ok, reason = self.verdict('''
            import argparse, sys
            def main():
                if len(sys.argv) > 5:
                    open("x", "w").write("boom")
                parser = argparse.ArgumentParser()
                return parser.parse_args()
            if __name__ == "__main__":
                main()
        ''')
        self.assertFalse(ok)
        self.assertIn("If before parse_args", reason)

    def test_parse_inside_branch_is_not_a_direct_parse(self):
        ok, _ = self.verdict('''
            import argparse
            def main():
                parser = argparse.ArgumentParser()
                if True:
                    args = parser.parse_args()
                return 0
            if __name__ == "__main__":
                main()
        ''')
        self.assertFalse(ok)

    def test_side_effect_call_before_parse_is_rejected(self):
        ok, reason = self.verdict('''
            import argparse
            from pathlib import Path
            def main():
                Path("x.txt").write_text("boom")
                return argparse.ArgumentParser().parse_args()
            if __name__ == "__main__":
                main()
        ''')
        self.assertFalse(ok)
        self.assertIn("write_text", reason)

    def test_lambda_or_comprehension_before_parse_is_rejected(self):
        ok, _ = self.verdict('''
            import argparse
            def main():
                parser = argparse.ArgumentParser(type=lambda v: open(v, "w"))
                return parser.parse_args()
            if __name__ == "__main__":
                main()
        ''')
        self.assertFalse(ok)

    def test_unsafe_local_import_is_rejected(self):
        ok, reason = self.verdict(SAFE.replace("import argparse", "import argparse\nimport sidecar"),
                                  extra={"sidecar": 'from pathlib import Path\nPath("x").write_text("boom")\n'})
        self.assertFalse(ok)
        self.assertIn("sidecar", reason)

    def test_safe_local_import_is_accepted(self):
        ok, reason = self.verdict(SAFE.replace("import argparse", "import argparse\nimport sidecar"),
                                  extra={"sidecar": 'from pathlib import Path\nCONST = Path("a")\ndef f():\n    return 1\n'})
        self.assertTrue(ok, reason)

    def test_third_party_import_fails_closed(self):
        ok, reason = self.verdict(SAFE.replace("import argparse", "import argparse\nimport numpy"))
        self.assertFalse(ok)
        self.assertIn("neither standard library", reason)

    def test_top_level_call_or_block_is_rejected(self):
        for snippet in ('print("hi")', 'open("x", "w")', 'try:\n    import json\nexcept ImportError:\n    json = None',
                        'for i in range(3):\n    pass'):
            with self.subTest(snippet=snippet):
                ok, _ = self.verdict(SAFE.replace("ROOT = ", snippet + "\nROOT = "))
                self.assertFalse(ok)

    def test_impure_decorator_default_or_class_body_is_rejected(self):
        cases = {
            "decorator": SAFE.replace("def main():", "@register\ndef main():"),
            "default": SAFE.replace("def main():", 'def helper(x=open("x", "w")):\n    return x\n\n\ndef main():'),
            "class body": SAFE.replace("def main():", 'class C:\n    VALUE = open("x").read()\n\n\ndef main():'),
        }
        for label, source in cases.items():
            with self.subTest(case=label):
                ok, _ = self.verdict(source)
                self.assertFalse(ok)

    def test_main_block_must_only_dispatch(self):
        ok, _ = self.verdict(SAFE.replace("    raise SystemExit(main())", '    print("side effect")\n    raise SystemExit(main())'))
        self.assertFalse(ok)

    def test_x2292_main_guard_must_be_exact(self):
        """A chained or altered __main__ condition can run code before argparse; only the exact guard is accepted."""
        cases = {
            "chained call": 'if __name__ == "__main__" == side_effect():',
            "wrong operator": 'if __name__ != "__main__":',
            "wrong comparator": 'if __name__ == "__other__":',
            "call comparator": 'if __name__ == open("x", "w").name:',
            "extra boolean term": 'if __name__ == "__main__" and side_effect():',
            "reversed": 'if "__main__" == __name__:',
        }
        for label, guard in cases.items():
            with self.subTest(case=label):
                ok, _ = self.verdict(SAFE.replace('if __name__ == "__main__":', guard))
                self.assertFalse(ok, f"{label} must not satisfy the guard predicate")
        ok, reason = self.verdict(SAFE.replace('if __name__ == "__main__":', "if __name__ == '__main__':"))
        self.assertTrue(ok, f"single-quoted exact guard stays accepted: {reason}")

    def test_x2292_path_guard_must_be_exact(self):
        """Only sys.path.insert(0, str(Path(__file__).resolve().parent)) is accepted; other inserts could redirect imports."""
        exact = "import sys\nsys.path.insert(0, str(Path(__file__).resolve().parent))\n"
        ok, reason = self.verdict(SAFE.replace("ROOT = ", exact + "ROOT = "))
        self.assertTrue(ok, reason)
        bad = {
            "other folder": 'import sys\nsys.path.insert(0, "C:/evil")\n',
            "parent of parent": "import sys\nsys.path.insert(0, str(Path(__file__).resolve().parents[2]))\n",
            "append": "import sys\nsys.path.append(str(Path(__file__).resolve().parent))\n",
            "other index": "import sys\nsys.path.insert(1, str(Path(__file__).resolve().parent))\n",
            "call in path": 'import sys\nsys.path.insert(0, str(Path(open("x", "w").name).resolve().parent))\n',
        }
        for label, snippet in bad.items():
            with self.subTest(case=label):
                ok, _ = self.verdict(SAFE.replace("ROOT = ", snippet + "ROOT = "))
                self.assertFalse(ok, f"{label} must be rejected")

    def test_stdlib_constant_getattr_only(self):
        ok, reason = self.verdict(SAFE.replace("ROOT = ", 'import os\nFLAGS = getattr(os, "O_BINARY", 0)\nROOT = '))
        self.assertTrue(ok, reason)
        ok, _ = self.verdict(SAFE.replace("ROOT = ", 'import os\nFLAGS = getattr(os, name, 0)\nROOT = '))
        self.assertFalse(ok)


class RealToolVerdicts(unittest.TestCase):
    def test_incident_tools_fail(self):
        for tool in ("build_parry_addendum_reel", "build_sfx_audition_reel", "build_sfx_batch3_reel",
                     "audit_source_test_coverage", "diff_phase_two_auras"):
            with self.subTest(tool=tool):
                self.assertFalse(contract.analyse(HERE / f"{tool}.py")[0])

    def test_helpers_are_import_safe(self):
        for helper in ("atomic_io", "json_input", "redaction"):
            with self.subTest(helper=helper):
                ok, reason = contract.import_time_safe(HERE / f"{helper}.py")
                self.assertTrue(ok, reason)


if __name__ == "__main__":
    unittest.main()
