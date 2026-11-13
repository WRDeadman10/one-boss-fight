"""BQ-46..49 static contract for repoint_greystone_rolls_rm.py (no Unreal, no editor, no asset access)."""
import ast
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "repoint_greystone_rolls_rm.py"
RETARGET = HERE / "retarget_greystone_pack_rolls_rm.py"
AUTHOR = HERE / "author_greystone_player.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def literal_assign(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return node.value
    raise AssertionError(name + " not found")


class RepointContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.module = load(SCRIPT, "greystone_rm_repoint")  # must import without Unreal

    def test_unreal_import_only_inside_functions(self):
        top = [n for n in self.tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
        self.assertFalse(any(a.name == "unreal" for n in top for a in n.names))

    def test_rm_paths_follow_the_retarget_derivation(self):
        # retarget: OUT_ROOT + "/Montages/" + kind + "/" + <grey montage name> + SUFFIX
        rt = ast.parse(RETARGET.read_text(encoding="utf-8"))
        out_root = ast.literal_eval(literal_assign(rt, "OUT_ROOT"))
        suffix = ast.literal_eval(literal_assign(rt, "SUFFIX"))
        rolls = {r["kind"]: r for r in ast.literal_eval(literal_assign(rt, "ROLLS"))}
        self.assertEqual(self.module.RM_ROOT, out_root)
        for field, kind in (("QuickMontage", "quick"), ("FullMontage", "full")):
            grey, rm = self.module.REPOINTS[field]
            self.assertEqual(grey, rolls[kind]["source_grey_montage"])
            self.assertEqual(rm, out_root + "/Montages/" + kind + "/" + grey.rsplit("/", 1)[-1] + suffix)

    def test_grey_paths_match_the_authored_child_defaults(self):
        au = ast.parse(AUTHOR.read_text(encoding="utf-8"))
        fields = ast.literal_eval(literal_assign(au, "CHILD_FIELDS"))
        for field in ("QuickMontage", "FullMontage"):
            self.assertEqual(self.module.REPOINTS[field][0], fields[field])
        # author: CHILD_PATH = ALLOWLIST + "BP_GreystoneERPlayer"
        allowlist = ast.literal_eval(literal_assign(au, "ALLOWLIST"))
        self.assertEqual(self.module.CHILD_PATH, allowlist + "BP_GreystoneERPlayer")

    def test_plan_decisions(self):
        grey = {f: g for f, (g, _) in self.module.REPOINTS.items()}
        rm = {f: r for f, (_, r) in self.module.REPOINTS.items()}
        self.assertEqual(set(self.module.plan(grey).values()), {"repoint"})
        self.assertEqual(set(self.module.plan(rm).values()), {"already"})
        mixed = dict(grey, QuickMontage=rm["QuickMontage"])
        self.assertEqual(self.module.plan(mixed), {"QuickMontage": "already", "FullMontage": "repoint"})
        self.assertEqual(self.module.plan({"QuickMontage": "/Game/Other", "FullMontage": grey["FullMontage"]})["QuickMontage"], "refuse")
        self.assertEqual(set(self.module.plan({}).values()), {"refuse"})

    def test_write_is_opt_in_and_guarded(self):
        self.assertIn('WRITE_TOKEN = "-RMRepointWrite"', self.source)
        self.assertIn("RESULT=DRY_RUN", self.source)
        # the dry-run return happens before the first setter
        self.assertLess(self.source.index("if not write:"), self.source.index("timing.set_editor_property("))
        self.assertIn('require("refuse" not in decisions.values()', self.source)
        self.assertIn("require(all(rm_assets.values())", self.source)

    def test_no_destructive_or_out_of_scope_calls(self):
        called = {n.func.attr for n in ast.walk(self.tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        self.assertEqual(called & {"delete_asset", "duplicate_asset", "rename_asset", "create_asset", "delete_directory"}, set())
        self.assertEqual(self.source.count("save_loaded_asset("), 1)   # only the child Blueprint
        self.assertEqual(self.source.count("set_editor_property("), 1)  # only the two montage fields, in one loop

    def test_python_field_names(self):
        self.assertEqual(self.module.python_name("QuickMontage"), "quick_montage")
        self.assertEqual(self.module.python_name("FullMontage"), "full_montage")
        self.assertNotIn("get_editor_property(field)", self.source)

    def test_readback_and_rollback_receipt(self):
        self.assertIn("loading.reload_packages([bp.get_outermost()], reload_mode)", self.source)
        self.assertIn("saved child package reload failed", self.source)
        self.assertLess(self.source.index("loading.reload_packages("), self.source.index("reloaded = unreal.load_asset(CHILD_PATH)"))
        self.assertIn("READBACK field=%s asset=%s rollback_to=%s", self.source)
        self.assertIn("RESULT=PASS repointed=%d saves=1", self.source)


if __name__ == "__main__":
    unittest.main()
