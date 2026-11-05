#!/usr/bin/env python3
"""Collision refusal must preserve existing offline scaffold output."""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

MODULE_PATH = Path(__file__).with_name("new_rule_scaffold.py")
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("new_rule_scaffold_collision_test", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class NewRuleScaffoldCollisionTests(unittest.TestCase):
    def test_existing_target_is_preserved_and_refusal_is_clear(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "Source/OneBossFight/Player/RPGBossCueRules.h"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"owner content\r\n")
            before_files = {path.relative_to(root) for path in root.rglob("*") if path.is_file()}
            stdout, stderr = io.StringIO(), io.StringIO()
            args = ["new_rule_scaffold.py", "--name", "Cue", "--requirement-id", "BOSS-CUE-001",
                    "--slug", "cue-rule", "--output-root", temp]
            with mock.patch.object(sys, "argv", args), redirect_stdout(stdout), redirect_stderr(stderr):
                code = MODULE.main()
            self.assertEqual(code, 2)
            self.assertIn("Refusing to overwrite existing scaffold target(s)", stderr.getvalue())
            self.assertIn("RPGBossCueRules.h", stderr.getvalue())
            self.assertEqual(target.read_bytes(), b"owner content\r\n")
            after_files = {path.relative_to(root) for path in root.rglob("*") if path.is_file()}
            self.assertEqual(after_files, before_files)


if __name__ == "__main__":
    unittest.main(verbosity=2)
