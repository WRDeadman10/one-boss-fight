from __future__ import annotations

import ast
from pathlib import Path
import unittest


DRIVER = Path(__file__).resolve().parents[1] / "Editor" / "verify_greystone_wrapper_readback.py"
FORBIDDEN_CALLS = {
    "create_asset", "save_asset", "save_loaded_asset", "delete_asset",
    "rename_asset", "duplicate_asset", "set_editor_property",
}


class GreystoneWrapperReadbackSafetyTests(unittest.TestCase):
    def test_readback_driver_contains_no_asset_write_calls(self) -> None:
        tree = ast.parse(DRIVER.read_text(encoding="utf-8"), filename=str(DRIVER))
        calls = {
            node.func.attr if isinstance(node.func, ast.Attribute)
            else node.func.id if isinstance(node.func, ast.Name)
            else ""
            for node in ast.walk(tree) if isinstance(node, ast.Call)
        }
        self.assertEqual(sorted(calls & FORBIDDEN_CALLS), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
