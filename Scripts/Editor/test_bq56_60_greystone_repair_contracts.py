"""BQ-56..59 static contracts for repair_grey_layer_parents.py and inventory_grey_broken_refs_and_sockets.py.
No Unreal, no editor, no asset access; the on-disk existence checks read Content/ file names only."""
import ast
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPAIR = HERE / "repair_grey_layer_parents.py"
INVENTORY = HERE / "inventory_grey_broken_refs_and_sockets.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def content_file(game_path):
    return ROOT / "Content" / (game_path[len("/Game/"):] + ".uasset")


def calls(source):
    return [n.func.attr for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]


class RepairContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = REPAIR.read_text(encoding="utf-8")
        cls.m = load(REPAIR, "grey_layer_repair")

    def test_paths_exist_on_disk(self):
        self.assertTrue(content_file(self.m.REAL).is_file())
        self.assertEqual(len(self.m.LAYERS), 8)
        for layer in self.m.LAYERS:
            self.assertTrue(content_file(layer).is_file(), layer)
        self.assertNotIn(self.m.REAL, self.m.LAYERS)
        self.assertFalse(any("ABP_CombatCharacter_Grey" in p for p in self.m.LAYERS))

    def test_classify(self):
        c = self.m.classify
        stale = "/Script/Engine.AnimBlueprintGeneratedClass'/Game/ABP_CombatAnimLayersBase_Grey.ABP_CombatAnimLayersBase_Grey_C'"
        real = "/Script/Engine.AnimBlueprintGeneratedClass'%s.ABP_CombatAnimLayersBase_Grey_C'" % self.m.REAL
        self.assertEqual(c(stale), "stale")
        self.assertEqual(c(real), "ok")
        self.assertEqual(c("/Script/Engine.AnimInstance"), "unknown")
        self.assertEqual(c(None), "unknown")
        self.assertNotIn(self.m.STALE + ".", self.m.REAL + ".")   # the two checks cannot both match

    def test_write_guards_and_order(self):
        s = self.source
        self.assertIn('WRITE_TOKEN = "-GreyLayerRepairWrite"', s)
        self.assertLess(s.index("if not write:"), s.index("duplicate_asset("))
        self.assertLess(s.index("if not write:"), s.index("reparent_blueprint("))
        self.assertIn("for path in stale:", s)                          # only stale layers are re-parented
        self.assertLess(s.index("compile_blueprint(bp)"), s.index('require("ERROR" not in status.upper()'))
        self.assertLess(s.index('require("ERROR" not in status.upper()'), s.index("save_loaded_asset(bp)"))
        self.assertIn("reload_packages(", s)
        self.assertIn('require(reload_ok, "saved layer package reload failed:', s)
        reload_guard = s.index("require(reload_ok, \"saved layer package reload failed:")
        self.assertLess(reload_guard, s.index('data = registry.get_asset_by_object_path(path + "."', reload_guard))
        self.assertIn("if created_temp:", s)                            # only a copy made by this run may be removed
        self.assertLess(s.index("find_package_referencers_for_asset(STALE"), s.index("delete_asset(STALE)"))
        self.assertIn('require(removed, "temporary parent is unreferenced but could not be removed:', s)

    def test_only_expected_mutations(self):
        c = calls(self.source)
        self.assertEqual(c.count("delete_asset"), 1)
        self.assertEqual(c.count("duplicate_asset"), 1)
        self.assertNotIn("rename_asset", c)
        self.assertNotIn("set_editor_property", c)

    def test_unreal_import_inside_main(self):
        top = [n for n in ast.parse(self.source).body if isinstance(n, (ast.Import, ast.ImportFrom))]
        self.assertFalse(any(a.name == "unreal" for n in top for a in n.names))


class InventoryContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = INVENTORY.read_text(encoding="utf-8")
        cls.m = load(INVENTORY, "grey_inventory")

    def test_read_only(self):
        forbidden = {"set_editor_property", "save_loaded_asset", "save_asset", "delete_asset", "duplicate_asset",
                     "rename_asset", "create_asset", "reparent_blueprint"}
        self.assertEqual(set(calls(self.source)) & forbidden, set())

    def test_root_level(self):
        f = self.m.is_root_level
        self.assertTrue(f("/Game/RMB_Cast_Grey1"))
        self.assertFalse(f("/Game/OneBossFight/X"))
        self.assertFalse(f("/Script/Engine"))

    def test_same_transform(self):
        a = ((1.0, 2.0, 3.0), (0.0, 90.0, 0.0), (1.0, 1.0, 1.0))
        self.assertTrue(self.m.same_transform(a, a))
        self.assertFalse(self.m.same_transform(a, ((1.0, 2.0, 3.5), (0.0, 90.0, 0.0), (1.0, 1.0, 1.0))))

    def test_assets_exist_on_disk(self):
        for path in (self.m.KEEPALIVE, self.m.MANNEQUIN_SKELETON, self.m.GREYSTONE_SKELETON):
            self.assertTrue(content_file(path).is_file(), path)


if __name__ == "__main__":
    unittest.main()
