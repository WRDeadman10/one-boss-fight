"""BP-11..14 (C, implementer; Queue BP batch 3) under X-2295: static tests only (no tool, main() or subprocess is run).

  1. The four fixed tools check `args.<input>.is_file()` and call `parser.error(...)` immediately after parse_args, before
     any read of that input: a missing file is a named usage error (exit 2), not a traceback.
  2. Regression guard across the whole smoke ALLOWLIST: no main() reads `args.<name>` (read_text/read_bytes/open/load_json)
     unless it checks that argument (is_file/exists/is_dir) or handles OSError-family errors. This is the BP-11 inventory
     heuristic made permanent; it sees direct reads in main() only (reads inside helper functions are out of scope).
Only the tools' source files are read (parsed with ast).
"""
import ast
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import test_bp_cli_smoke as smoke  # noqa: E402  (reads the pinned ALLOWLIST only)

FIXED = {"fight_capture_receipt": "log", "log_failures": "log", "mailbox_stats": "mailbox", "make_fight_video": "log"}
READS = {"read_text", "read_bytes", "open", "load_json"}
CHECKS = {"is_file", "exists", "is_dir"}
HANDLED = {"OSError", "FileNotFoundError", "IOError", "Exception", "JsonInputError"}


def main_of(tool):
    tree = ast.parse((HERE / f"{tool}.py").read_text(encoding="utf-8"))
    return next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main"), None)


def arg_calls(main, names):
    out = []
    for node in ast.walk(main):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in names:
            target = node.func.value
            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "args":
                out.append((target.attr, node.lineno))
    return out


class FixedTools(unittest.TestCase):
    def test_guard_follows_parse_and_precedes_reads(self):
        for tool, arg in FIXED.items():
            with self.subTest(tool=tool):
                main = main_of(tool)
                body = main.body
                parse_index = next(i for i, s in enumerate(body) if "parse_args()" in ast.unparse(s))
                guard = body[parse_index + 1]
                self.assertIsInstance(guard, ast.If)
                self.assertEqual(ast.unparse(guard.test), f"not args.{arg}.is_file()")
                self.assertTrue(any(isinstance(c, ast.Call) and getattr(c.func, "attr", "") == "error"
                                    and getattr(getattr(c.func, "value", None), "id", "") == "parser" for c in ast.walk(guard)))
                reads = [line for name, line in arg_calls(main, READS) if name == arg]
                self.assertTrue(reads, "the tool reads the input")
                self.assertLess(guard.lineno, min(reads))


class AllowlistRegression(unittest.TestCase):
    def test_no_unchecked_direct_input_reads(self):
        offenders = []
        for tool in smoke.ALLOWLIST:
            main = main_of(tool)
            if main is None:
                continue
            handled = any(h.type is not None and any(getattr(e, "id", "") in HANDLED for e in
                                                     ([h.type] if isinstance(h.type, ast.Name) else getattr(h.type, "elts", [])))
                          for n in ast.walk(main) if isinstance(n, ast.Try) for h in n.handlers)
            unchecked = {name for name, _ in arg_calls(main, READS)} - {name for name, _ in arg_calls(main, CHECKS)}
            if unchecked and not handled:
                offenders.append(f"{tool}: {sorted(unchecked)}")
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
