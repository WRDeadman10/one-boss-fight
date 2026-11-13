import ast
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EDITOR_DIR = REPO_ROOT / "Scripts" / "Editor"


class BiA09EditorSafetyContractTest(unittest.TestCase):
    def test_zero_bare_except_clauses_in_editor_scripts(self) -> None:
        bare = []
        for path in sorted(EDITOR_DIR.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    bare.append(path.relative_to(REPO_ROOT).as_posix())
                    break
        self.assertEqual(bare, [], f"Bare except clauses prohibited: {bare}")

    def test_active_authoring_scripts_retain_fail_closed_write_and_import_guards(self) -> None:
        author_text = (EDITOR_DIR / "author_sevarog_draft_cards.py").read_text(encoding="utf-8")
        self.assertIn("except ImportError", author_text)
        self.assertIn("--dry-run", author_text)

        rm_fix_text = (EDITOR_DIR / "fix_greystone_fit_root_motion.py").read_text(encoding="utf-8")
        self.assertIn("--write", rm_fix_text)

        retarget_text = (EDITOR_DIR / "retarget_er_fit_candidate.py").read_text(encoding="utf-8")
        self.assertIn("except ImportError", retarget_text)

    def test_ki169_sevarog_pack_07_literal_remains_unguessed_pending_editor_check(self) -> None:
        pack07 = (EDITOR_DIR / "sevarog_pack_07_bolt_impact.py").read_text(encoding="utf-8")
        self.assertIn("Damage Gampelay Effect", pack07)


if __name__ == "__main__":
    unittest.main()
