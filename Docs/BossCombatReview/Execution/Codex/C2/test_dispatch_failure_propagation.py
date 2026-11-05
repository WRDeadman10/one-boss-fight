"""Verify exceptions raised by the selected C2 action reach the Editor caller."""
import builtins
import importlib.util
import io
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


class DispatchFailurePropagationTests(unittest.TestCase):
    def test_action_exception_is_not_swallowed_by_dispatcher(self):
        asset = types.SimpleNamespace(get_class=lambda: types.SimpleNamespace(get_name=lambda: "RPGBossFrameworkProfile"))
        logged = []
        unreal_stub = types.SimpleNamespace(
            EditorUtilityLibrary=types.SimpleNamespace(get_selected_assets=lambda: [asset]),
            log=logged.append, log_warning=logged.append,
        )
        real_open = builtins.open

        def fake_open(path, *args, **kwargs):
            if str(path).endswith("validate_selected_boss_profile.py"):
                return io.StringIO("raise RuntimeError('injected action failure')\n")
            return real_open(path, *args, **kwargs)

        spec = importlib.util.spec_from_file_location("c2_dispatch_failure", HERE / "run_validate_boss.py")
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"unreal": unreal_stub}), patch("builtins.open", side_effect=fake_open):
            with self.assertRaisesRegex(RuntimeError, "injected action failure"):
                spec.loader.exec_module(module)
        self.assertEqual(logged, [], "dispatcher must not turn an action exception into a success receipt")


if __name__ == "__main__":
    unittest.main()
