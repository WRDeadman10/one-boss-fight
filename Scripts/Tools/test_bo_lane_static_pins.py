"""BO-47 (C, implementer; per X-2270): static guards for the seven --redact integrations and the lane's import guards.

Source-level AST checks, so an accidental edit fails fast without running a tool:
  1. each KI-167 tool's `main` is decorated with `@redaction_scope` (BO-18/19);
  2. `add_redact_argument(parser)` is the last option added before `parse_args()` in `main` (the BO-26 pre-scan needs the
     complete option table);
  3. `install_stream_redaction` is only ever called as `install_stream_redaction(True)` inside `if args.redact:` (BO-23);
  4. in all 13 lane tools, the `sys.path` guard comes before any import of a sibling helper (atomic_io, json_input,
     redaction), so `python -m Scripts.Tools.*` works (BO-28/41).
"""
import ast
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REDACT_TOOLS = ("proof_report", "asset_provenance", "evidence_summary", "token_coverage", "suite_log_report",
                "summarize_framework_log", "plot_framework_timeline")
LANE_TOOLS = REDACT_TOOLS + ("evidence_pack", "make_source_manifest", "profile_dump", "card_table", "validate_baked_cards",
                             "plugin_dependencies")
HELPERS = {"atomic_io", "json_input", "redaction"}


def tree(tool):
    return ast.parse((HERE / f"{tool}.py").read_text(encoding="utf-8"))


def main_func(module):
    return next(node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == "main")


def call_name(node):
    if isinstance(node, ast.Call):
        func = node.func
        return func.attr if isinstance(func, ast.Attribute) else func.id if isinstance(func, ast.Name) else None
    return None


class RedactIntegrationPins(unittest.TestCase):
    def test_main_is_scoped(self):
        for tool in REDACT_TOOLS:
            with self.subTest(tool=tool):
                decorators = [d.id if isinstance(d, ast.Name) else getattr(d, "attr", None) for d in main_func(tree(tool)).decorator_list]
                self.assertIn("redaction_scope", decorators)

    def test_add_redact_argument_is_last_before_parse_args(self):
        for tool in REDACT_TOOLS:
            with self.subTest(tool=tool):
                calls = [(n.lineno, call_name(n)) for n in ast.walk(main_func(tree(tool))) if isinstance(n, ast.Call)]
                calls.sort()
                names = [name for _, name in calls]
                parse = names.index("parse_args")
                before = [name for name in names[:parse] if name in ("add_argument", "add_redact_argument")]
                self.assertTrue(before, "main adds options")
                self.assertEqual(before[-1], "add_redact_argument", "no option may be added after add_redact_argument")
                self.assertEqual(before.count("add_redact_argument"), 1)

    def test_install_only_enables_under_the_flag(self):
        for tool in REDACT_TOOLS:
            with self.subTest(tool=tool):
                module = tree(tool)
                installs = [n for n in ast.walk(module) if call_name(n) == "install_stream_redaction"]
                self.assertEqual(len(installs), 1, "exactly one install call")
                call = installs[0]
                self.assertEqual(len(call.args), 1)
                self.assertIsInstance(call.args[0], ast.Constant)
                self.assertIs(call.args[0].value, True, "never install_stream_redaction(args.redact) / (False)")
                guarded = [n for n in ast.walk(main_func(module)) if isinstance(n, ast.If)
                           and isinstance(n.test, ast.Attribute) and n.test.attr == "redact" and call in list(ast.walk(n))]
                self.assertTrue(guarded, "the install call sits inside `if args.redact:`")


class ImportGuardPins(unittest.TestCase):
    def test_sys_path_guard_precedes_helper_imports(self):
        for tool in LANE_TOOLS:
            with self.subTest(tool=tool):
                body = tree(tool).body
                helper_lines = [n.lineno for n in body if isinstance(n, ast.ImportFrom) and n.module in HELPERS]
                self.assertTrue(helper_lines, f"{tool} imports a sibling helper")
                guard_lines = [n.lineno for n in body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                               and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == "insert"
                               and "path" in ast.unparse(n.value.func.value)]
                self.assertTrue(guard_lines, f"{tool} has a sys.path guard")
                self.assertLess(min(guard_lines), min(helper_lines), f"{tool}: guard must precede the first helper import")


if __name__ == "__main__":
    unittest.main()
