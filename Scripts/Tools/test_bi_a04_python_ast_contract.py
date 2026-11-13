import ast
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "Scripts"


class BiA04PythonAstContractTest(unittest.TestCase):
    def test_all_python_scripts_parse_cleanly_via_ast(self) -> None:
        py_files = sorted(SCRIPTS_DIR.rglob("*.py"))
        self.assertGreaterEqual(len(py_files), 880)
        failures = []
        for py_path in py_files:
            try:
                source = py_path.read_text(encoding="utf-8")
                ast.parse(source, filename=str(py_path))
            except Exception as exc:  # pragma: no cover - diagnostic surface
                failures.append((py_path.relative_to(REPO_ROOT).as_posix(), type(exc).__name__, str(exc)))
        self.assertEqual(failures, [], f"Python AST syntax failures in Scripts/: {failures}")

    def test_retarget_er_fit_candidate_retains_c1285_root_chain_and_import_guard(self) -> None:
        source = (SCRIPTS_DIR / "Editor" / "retarget_er_fit_candidate.py").read_text(encoding="utf-8")
        tree = ast.parse(source, filename="retarget_er_fit_candidate.py")
        top_funcs = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
        self.assertIn("ensure_root_chain_globally_scaled", top_funcs)
        self.assertIn("except ImportError:", source)
        self.assertIn("GLOBALLY_SCALED", source)
        self.assertIn("set_retarget_chain_settings", source)


if __name__ == "__main__":
    unittest.main()
