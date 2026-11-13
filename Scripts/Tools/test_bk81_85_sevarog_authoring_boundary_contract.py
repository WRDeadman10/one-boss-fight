"""BK-82 (C, implementer; X-1998): static source contract for the Sevarog authoring boundary.

AST and exact-source assertions only: no Unreal import, no asset access. Covers the hardened Phase_1 prerequisite
helper (ensure_bk56_60_sevarog_initial_phase.py), the runner that calls it, and the other scripts that can create,
mutate or delete the Sevarog draft / framework encounter (BK-81 trace).
"""
import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "Scripts/Editor/ensure_bk56_60_sevarog_initial_phase.py"
RUNNER = ROOT / "Scripts/Editor/run_bk56_60_deferred_selection.ps1"
ENCOUNTER_AUTHOR = ROOT / "Scripts/Editor/author_framework_encounter_definition.py"
CARD_AUTHOR = ROOT / "Scripts/Editor/author_sevarog_draft_cards.py"
REPLACER = ROOT / "Scripts/Editor/replace_sevarog_draft_assets.py"
PHASE_FIELDS = ("entry_health_fraction", "speed_multiplier", "rate_multiplier", "attack_multiplier")


def tree(path):
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def function(module, name):
    return next(node for node in ast.walk(module) if isinstance(node, ast.FunctionDef) and node.name == name)


def calls(node, attr):
    """Call nodes whose callee name or attribute equals attr, in source order."""
    found = []
    for item in ast.walk(node):
        if isinstance(item, ast.Call):
            callee = item.func
            name = callee.attr if isinstance(callee, ast.Attribute) else getattr(callee, "id", None)
            if name == attr:
                found.append(item)
    return sorted(found, key=lambda call: (call.lineno, call.col_offset))


class Phase1HelperContract(unittest.TestCase):
    def setUp(self):
        self.module = tree(HELPER)
        self.source = HELPER.read_text(encoding="utf-8")

    def test_no_phase_field_is_ever_set_from_a_literal(self):
        for call in calls(self.module, "set_editor_property"):
            if call.args and isinstance(call.args[0], ast.Constant) and call.args[0].value in PHASE_FIELDS:
                self.fail("phase field %r set from a literal at line %d" % (call.args[0].value, call.lineno))
            if len(call.args) > 1 and isinstance(call.args[1], ast.Constant) and isinstance(call.args[1].value, (int, float)) \
                    and not isinstance(call.args[1].value, bool):
                self.fail("numeric literal written via set_editor_property at line %d" % call.lineno)

    def test_no_zero_threshold_or_identity_default_anywhere(self):
        self.assertNotRegex(self.source, r'entry_health_fraction"\s*,\s*0(\.0)?\s*\)')
        self.assertNotRegex(self.source, r'_multiplier"\s*,\s*1(\.0)?\s*\)')
        for call in calls(self.module, "get"):
            if isinstance(call.func, ast.Attribute) and getattr(call.func.value, "attr", None) == "environ":
                self.assertEqual(len(call.args), 1, "os.environ.get must not supply a default (line %d)" % call.lineno)

    def test_inputs_cover_exactly_the_four_phase_fields_from_explicit_env(self):
        assign = next(node for node in self.module.body if isinstance(node, ast.Assign)
                      and any(getattr(t, "id", None) == "INPUTS" for t in node.targets))
        inputs = ast.literal_eval(assign.value)
        self.assertEqual(set(inputs), set(PHASE_FIELDS))
        self.assertTrue(all(name.startswith("BK56_PHASE_") for name in inputs.values()))

    def test_approved_inputs_requires_presence_numeric_and_validation(self):
        body = ast.unparse(function(self.module, "approved_inputs"))
        self.assertIn("raw is not None", body)
        self.assertIn("float(raw)", body)
        self.assertIn("validate_values(values)", body)

    def test_validate_values_enforces_finite_open_threshold_and_positive_multipliers(self):
        body = ast.unparse(function(self.module, "validate_values"))
        self.assertIn("math.isfinite(fraction)", body)
        self.assertRegex(body, r"0\.0 < fraction <= 1\.0")
        self.assertIn("math.isfinite(value)", body)
        self.assertIn("value > 0.0", body)

    def test_existing_rows_are_validated_and_never_rewritten(self):
        main = function(self.module, "main")
        present_branch = next(node for node in ast.walk(main) if isinstance(node, ast.If)
                              and "PHASE_ID in ids" in ast.unparse(node.test))
        branch = ast.unparse(ast.Module(body=present_branch.body, type_ignores=[]))
        self.assertIn("validate_values(values)", branch)
        self.assertIn("return", branch)
        self.assertNotIn("save_loaded_asset", branch)
        self.assertNotIn('set_editor_property("phases"', branch)

    def test_new_row_write_happens_only_after_gate_inputs_and_validation(self):
        main = function(self.module, "main")
        save = calls(main, "save_loaded_asset")
        self.assertEqual(len(save), 1)
        save_line = save[0].lineno
        gate = [c for c in calls(main, "require") if "WRITE" in ast.unparse(c.args[0])]
        inputs = calls(main, "approved_inputs")
        set_phases = [c for c in calls(main, "set_editor_property") if c.args and getattr(c.args[0], "value", None) == "phases"]
        self.assertTrue(gate and inputs and set_phases)
        self.assertLess(gate[0].lineno, inputs[0].lineno)
        self.assertLess(inputs[0].lineno, set_phases[0].lineno)
        self.assertLess(set_phases[0].lineno, save_line)


class RunnerAndOtherWritersContract(unittest.TestCase):
    def test_runner_never_supplies_phase_values_itself(self):
        runner = RUNNER.read_text(encoding="utf-8")
        self.assertIn("$env:BK56_AUTHOR_PHASE_WRITE = '1'", runner)
        self.assertNotRegex(runner, r"\$env:BK56_PHASE_\w+\s*=", "the runner must not inject phase values")

    def test_card_author_creates_no_phases_or_stats_and_never_overwrites(self):
        source = CARD_AUTHOR.read_text(encoding="utf-8")
        module = tree(CARD_AUTHOR)
        assign = next(node for node in module.body if isinstance(node, ast.Assign)
                      and any(getattr(t, "id", None) == "DRAFT_DEFINITION_FIELDS" for t in node.targets))
        keys = {k.value for k in assign.value.keys}
        self.assertFalse(keys & {"phases", "stats"}, keys)
        self.assertIn("target already exists; never overwrite or recreate", source)

    def test_encounter_author_never_mutates_the_boss_definition(self):
        module = tree(ENCOUNTER_AUTHOR)
        for call in calls(module, "set_editor_property"):
            receiver = ast.unparse(call.func.value) if isinstance(call.func, ast.Attribute) else ""
            # `guid` is the fresh local unreal.Guid struct built in new_guid(); it is not an asset.
            self.assertIn(receiver, ("asset", "guid"), "only the new encounter asset may be written (line %d)" % call.lineno)
        self.assertIn('"target exists; never overwrite: "', ENCOUNTER_AUTHOR.read_text(encoding="utf-8"))

    def test_encounter_author_write_path_does_not_prevalidate_phase1_or_stats(self):
        # BK-81 finding (documented, not a guard bypass): the --write branch creates and saves the encounter before any
        # check that the boss definition has a valid Phase_1 row or valid Stats; Phase_1 presence is checked only in
        # --readback, after the save. This test pins the current shape so a change is noticed.
        main = ast.unparse(function(tree(ENCOUNTER_AUTHOR), "main"))
        write_branch = main[main.index("require(not unreal.EditorAssetLibrary.does_asset_exist(ASSET_PATH)"):]
        self.assertNotIn("phases", write_branch)
        self.assertNotIn("stats", write_branch.lower().replace("stable_manifest_hash", ""))

    def test_replacer_deletes_only_with_explicit_write_and_refuses_referenced_assets(self):
        source = REPLACER.read_text(encoding="utf-8")
        self.assertRegex(source, r'write = "--write" in ')
        self.assertIn("delete_asset", source)
        self.assertRegex(source, r"refus", "the replacer must refuse referenced assets")


if __name__ == "__main__":
    unittest.main()
