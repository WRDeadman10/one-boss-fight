"""Exercise C2 compile-failure context using a small Unreal Python API stub."""
import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


class FakeAnimBlueprint:
    def get_path_name(self):
        return "/Game/Test/ABP_Boss.ABP_Boss"

    def get_name(self):
        return "ABP_Boss"

    def get_class(self):
        return types.SimpleNamespace(get_name=lambda: "AnimBlueprint")

    def get_editor_property(self, name):
        raise AssertionError(f"No editor properties should be read: {name}")


class AnimBlueprintCompileFailureContextTests(unittest.TestCase):
    def test_compile_exception_keeps_asset_and_compiler_log_context(self):
        logged = []
        shown = []
        asset = FakeAnimBlueprint()

        def compile_blueprint(_asset):
            with open(os.environ["C2_EDITOR_LOG_PATH"], "a", encoding="utf-8") as stream:
                stream.write("[Compiler] Error: ABP_Boss compile failed: missing node\n")
            raise RuntimeError("compile API raised")

        unreal_stub = types.SimpleNamespace(
            AnimBlueprint=FakeAnimBlueprint,
            EditorUtilityLibrary=types.SimpleNamespace(get_selected_assets=lambda: [asset]),
            BlueprintEditorLibrary=types.SimpleNamespace(compile_blueprint=compile_blueprint, generated_class=lambda _asset: None),
            EditorDialog=types.SimpleNamespace(show_message=lambda *args: shown.append(args)),
            AppMsgType=types.SimpleNamespace(OK="OK"),
            log=logged.append,
            log_warning=logged.append,
        )
        with tempfile.TemporaryDirectory() as temp:
            log_path = Path(temp) / "editor.log"
            log_path.write_text("existing log\n", encoding="utf-8")
            spec = importlib.util.spec_from_file_location("c2_anim_compile_failure", HERE / "validate_selected_anim_blueprint.py")
            module = importlib.util.module_from_spec(spec)
            with patch.dict(sys.modules, {"unreal": unreal_stub}), patch.dict(os.environ, {"C2_EDITOR_LOG_PATH": str(log_path)}):
                spec.loader.exec_module(module)

        self.assertEqual(len(logged), 1)
        self.assertTrue(logged[0].startswith("[C2_VALIDATE] "))
        receipt = json.loads(logged[0].split(" ", 1)[1])
        self.assertFalse(receipt["ok"])
        self.assertEqual(receipt["asset_path"], asset.get_path_name())
        codes = {item["code"] for item in receipt["diagnostics"]}
        self.assertIn("BlueprintCompile.Exception", codes)
        self.assertIn("BlueprintCompile.Failed", codes)
        self.assertNotIn("BlueprintCompile.StatusReadFailed", codes)
        compiler = next(item for item in receipt["diagnostics"] if item["code"] == "BlueprintCompile.CompilerLog")
        self.assertEqual(compiler["severity"], "error")
        self.assertTrue(compiler["asset_match"])
        self.assertEqual(len(shown), 1)

    def test_success_uses_generated_class_and_compiler_log_without_status(self):
        logged = []
        asset = FakeAnimBlueprint()
        generated = types.SimpleNamespace(get_path_name=lambda: "/Game/Test/ABP_Boss.ABP_Boss_C")
        unreal_stub = types.SimpleNamespace(
            AnimBlueprint=FakeAnimBlueprint,
            EditorUtilityLibrary=types.SimpleNamespace(get_selected_assets=lambda: [asset]),
            BlueprintEditorLibrary=types.SimpleNamespace(compile_blueprint=lambda _asset: None, generated_class=lambda _asset: generated),
            SystemLibrary=types.SimpleNamespace(get_command_line=lambda: '-abslog="%s"' % os.environ["C2_EXPECTED_EDITOR_LOG_PATH"]),
            EditorDialog=types.SimpleNamespace(show_message=lambda *_args: None),
            AppMsgType=types.SimpleNamespace(OK="OK"),
            log=logged.append,
            log_warning=logged.append,
        )
        def compile_blueprint(_asset):
            with open(os.environ["C2_EXPECTED_EDITOR_LOG_PATH"], "a", encoding="utf-8") as stream:
                stream.write("[Compiler] Display: ABP_Boss compile requested\n")

        unreal_stub.BlueprintEditorLibrary.compile_blueprint = compile_blueprint
        with tempfile.TemporaryDirectory() as temp:
            log_path = Path(temp) / "editor log with spaces.log"
            log_path.write_text("existing log\n", encoding="utf-8")
            spec = importlib.util.spec_from_file_location("c2_anim_compile_success", HERE / "validate_selected_anim_blueprint.py")
            module = importlib.util.module_from_spec(spec)
            with patch.dict(sys.modules, {"unreal": unreal_stub}), patch.dict(os.environ, {"C2_EXPECTED_EDITOR_LOG_PATH": str(log_path), "C2_EDITOR_LOG_PATH": ""}):
                spec.loader.exec_module(module)

        receipt = json.loads(logged[0].split(" ", 1)[1])
        self.assertTrue(receipt["ok"])
        self.assertTrue(receipt["compiled"])
        self.assertEqual(receipt["fields"]["generated_class"], generated.get_path_name())
        self.assertTrue(receipt["fields"]["compile_attempted"])
        self.assertEqual(receipt["compiler_log_path"], str(log_path))
        self.assertTrue(receipt["compiler_log_grew_during_compile"])

    def test_stale_editor_log_without_growth_refuses_verification(self):
        logged = []
        asset = FakeAnimBlueprint()
        generated = types.SimpleNamespace(get_path_name=lambda: "/Game/Test/ABP_Boss.ABP_Boss_C")
        unreal_stub = types.SimpleNamespace(
            AnimBlueprint=FakeAnimBlueprint,
            EditorUtilityLibrary=types.SimpleNamespace(get_selected_assets=lambda: [asset]),
            BlueprintEditorLibrary=types.SimpleNamespace(compile_blueprint=lambda _asset: None, generated_class=lambda _asset: generated),
            SystemLibrary=types.SimpleNamespace(get_command_line=lambda: ""),
            EditorDialog=types.SimpleNamespace(show_message=lambda *_args: None),
            AppMsgType=types.SimpleNamespace(OK="OK"),
            log=logged.append,
            log_warning=logged.append,
        )
        with tempfile.TemporaryDirectory() as temp:
            log_path = Path(temp) / "stale.log"
            log_path.write_text("old Editor session output\n", encoding="utf-8")
            spec = importlib.util.spec_from_file_location("c2_anim_compile_stale_log", HERE / "validate_selected_anim_blueprint.py")
            module = importlib.util.module_from_spec(spec)
            with patch.dict(sys.modules, {"unreal": unreal_stub}), patch.dict(os.environ, {"C2_EDITOR_LOG_PATH": str(log_path)}):
                spec.loader.exec_module(module)

        receipt = json.loads(logged[0].split(" ", 1)[1])
        self.assertFalse(receipt["ok"])
        self.assertFalse(receipt["compiler_log_grew_during_compile"])
        self.assertIn("BlueprintCompile.CompilerLogStale", {item["code"] for item in receipt["diagnostics"]})

    def test_log_older_than_editor_session_is_rejected_even_if_it_grows(self):
        logged = []
        asset = FakeAnimBlueprint()
        generated = types.SimpleNamespace(get_path_name=lambda: "/Game/Test/ABP_Boss.ABP_Boss_C")

        def compile_blueprint(_asset):
            with open(os.environ["C2_EDITOR_LOG_PATH"], "a", encoding="utf-8") as stream:
                stream.write("[Compiler] Display: compile completed\n")

        unreal_stub = types.SimpleNamespace(
            AnimBlueprint=FakeAnimBlueprint,
            EditorUtilityLibrary=types.SimpleNamespace(get_selected_assets=lambda: [asset]),
            BlueprintEditorLibrary=types.SimpleNamespace(compile_blueprint=compile_blueprint, generated_class=lambda _asset: generated),
            SystemLibrary=types.SimpleNamespace(get_command_line=lambda: ""),
            EditorDialog=types.SimpleNamespace(show_message=lambda *_args: None),
            AppMsgType=types.SimpleNamespace(OK="OK"),
            log=logged.append,
            log_warning=logged.append,
        )
        with tempfile.TemporaryDirectory() as temp:
            log_path = Path(temp) / "old-but-growing.log"
            log_path.write_text("previous session output\n", encoding="utf-8")
            spec = importlib.util.spec_from_file_location("c2_anim_compile_old_session_log", HERE / "validate_selected_anim_blueprint.py")
            module = importlib.util.module_from_spec(spec)
            future_session = str(log_path.stat().st_mtime + 10.0)
            with patch.dict(sys.modules, {"unreal": unreal_stub}), patch.dict(os.environ, {
                "C2_EDITOR_LOG_PATH": str(log_path),
                "C2_EDITOR_SESSION_START_EPOCH": future_session,
            }):
                spec.loader.exec_module(module)

        receipt = json.loads(logged[0].split(" ", 1)[1])
        self.assertFalse(receipt["ok"])
        self.assertTrue(receipt["compiler_log_grew_during_compile"])
        self.assertIn("BlueprintCompile.CompilerLogStale", {item["code"] for item in receipt["diagnostics"]})


if __name__ == "__main__":
    unittest.main()
