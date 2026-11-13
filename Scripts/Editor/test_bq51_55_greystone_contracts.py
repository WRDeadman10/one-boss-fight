"""BQ-51..54 static contracts: saved-wrapper notify readback (B5) and the Greystone pawn gate (B6). No Unreal, no editor."""
import ast
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
READBACK = HERE / "verify_greystone_saved_wrapper_notifies.py"
GATE = HERE / "greystone_pawn_gate.py"
AUTHOR = HERE / "author_greystone_player.py"
ROOT_MOTION = HERE / "pie_greystone_root_motion.py"
HIT_DRIVER = HERE / "pie_er_default_wiring_hits.py"
PARRY_DRIVER = HERE / "pie_tier2_parry.py"
SUBSYSTEM = HERE.parents[1] / "Source" / "OneBossFight" / "Player" / "RPGPlayerMovesSubsystem.cpp"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SavedWrapperReadback(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = READBACK.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.module = load(READBACK, "saved_wrapper_readback")

    def test_read_only(self):
        called = {n.func.attr for n in ast.walk(self.tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        self.assertEqual(called & {"set_editor_property", "save_loaded_asset", "save_asset", "delete_asset",
                                   "duplicate_asset", "create_retarget_wrapper", "create_asset"}, set())

    def test_reload_before_compare_and_fail_closed(self):
        self.assertIn("reload_packages([asset.get_outermost()], mode)", self.source)
        self.assertIn("ASSUME_POSITIVE", self.source)
        self.assertIn("refusing to read a possibly resident object", self.source)
        main = self.source[self.source.index("def main"):]
        self.assertLess(main.index("reload_from_disk("), main.index("compare_wrapper_notify_rows("))

    def test_covers_every_authored_wrapper(self):
        au = ast.parse(AUTHOR.read_text(encoding="utf-8"))
        names = [m["name"] for m in next(ast.literal_eval(n.value) for n in au.body if isinstance(n, ast.Assign)
                                         and any(getattr(t, "id", "") == "MONTAGES" for t in n.targets))]
        self.assertEqual(len(names), 4)
        self.assertIn("for spec in author.MONTAGES", self.source)   # iterates the author's own list, no copy to drift
        self.assertEqual(self.module.saved_path("/Game/X/", "AM_A"), "/Game/X/AM_A")

    def test_unreal_only_inside_functions(self):
        top = [n for n in self.tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
        self.assertFalse(any(a.name == "unreal" for n in top for a in n.names))

    def test_markers(self):
        for marker in ("WRAPPER PASS name=", "WRAPPER FAIL name=", "RESULT=PASS wrappers=%d saves=0", "RESULT=FAIL"):
            self.assertIn(marker, self.source)


class GreystonePawnGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gate = load(GATE, "greystone_pawn_gate")

    def test_env_parsing(self):
        g = self.gate
        self.assertEqual(g.target_from_env(None), "mannequin")
        self.assertEqual(g.target_from_env(""), "mannequin")
        self.assertEqual(g.target_from_env(" Greystone "), "greystone")
        self.assertIsNone(g.target_from_env("sevarog"))

    def test_commands(self):
        g = self.gate
        self.assertEqual(g.cvar_command("greystone"), "rpg.GreystonePlayerTestPawn 1")
        self.assertEqual(g.cvar_command("mannequin"), "rpg.GreystonePlayerTestPawn 0")
        self.assertIsNone(g.cvar_command(None))
        self.assertEqual(g.restore_command(), "rpg.GreystonePlayerTestPawn 0")

    def test_possession(self):
        g = self.gate
        self.assertTrue(g.possession_ok("greystone", "BP_GreystoneERPlayer_C"))
        self.assertFalse(g.possession_ok("greystone", "BP_Player_C"))
        self.assertTrue(g.possession_ok("mannequin", "BP_CombatPlayerCharacter_C"))
        self.assertFalse(g.possession_ok("mannequin", "BP_GreystoneERPlayer_C"))
        self.assertFalse(g.possession_ok("mannequin", "BP_Unexpected_C"))
        self.assertFalse(g.possession_ok("mannequin", ""))
        self.assertFalse(g.possession_ok(None, "BP_Player_C"))

    def test_matches_existing_switch(self):
        rm = ROOT_MOTION.read_text(encoding="utf-8")
        self.assertIn('"C1257_PLAYER_TARGET"', rm)
        self.assertIn('EXPECTED_CHILD = "BP_GreystoneERPlayer_C"', rm)
        subsystem = SUBSYSTEM.read_text(encoding="utf-8")
        self.assertIn('TEXT("rpg.GreystonePlayerTestPawn")', subsystem)
        self.assertIn('Class->GetName() == TEXT("BP_CombatPlayerCharacter_C")', subsystem)
        self.assertEqual(self.gate.MANNEQUIN_CLASS, "BP_CombatPlayerCharacter_C")

    def test_lead_drivers_bind_exact_pawn_route_and_restore(self):
        for path in (HIT_DRIVER, PARRY_DRIVER):
            source = path.read_text(encoding="utf-8")
            self.assertIn("import greystone_pawn_gate as greystone_gate", source)
            self.assertIn("target_from_env(os.environ.get(greystone_gate.ENV_NAME))", source)
            self.assertIn("possession_ok(TARGET, pawn.get_class().get_name())", source)
            self.assertIn("greystone_gate.cvar_command(TARGET)", source)
            self.assertIn("greystone_gate.restore_command()", source)
            self.assertIn("RESULT target=%s", source)
        self.assertEqual(self.gate.ENV_NAME, "C1257_PLAYER_TARGET")


if __name__ == "__main__":
    unittest.main()
