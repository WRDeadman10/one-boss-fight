"""Exercise the C2 dispatcher refusal with a mocked Editor selection API."""
import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


class MissingSelectionDispatchTests(unittest.TestCase):
    def test_empty_selection_emits_stable_receipt_and_does_not_dispatch_action(self):
        logged = []
        shown = []
        unreal_stub = types.SimpleNamespace(
            EditorUtilityLibrary=types.SimpleNamespace(get_selected_assets=lambda: []),
            EditorDialog=types.SimpleNamespace(show_message=lambda *args: shown.append(args)),
            AppMsgType=types.SimpleNamespace(OK="OK"),
            log=logged.append,
            log_warning=logged.append,
        )
        script = HERE / "run_validate_boss.py"
        spec = importlib.util.spec_from_file_location("c2_dispatch_missing_selection", script)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"unreal": unreal_stub}):
            spec.loader.exec_module(module)

        self.assertEqual(len(logged), 1)
        self.assertTrue(logged[0].startswith("[C2_VALIDATE_BOSS] "))
        receipt = json.loads(logged[0].split(" ", 1)[1])
        self.assertFalse(receipt["ok"])
        self.assertEqual(receipt["action"], "dispatch")
        self.assertEqual(receipt["diagnostics"][0]["code"], "Selection.Count")
        self.assertEqual(receipt["diagnostics"][0]["field"], "ContentBrowserSelection")
        self.assertEqual(len(shown), 1)


if __name__ == "__main__":
    unittest.main()
