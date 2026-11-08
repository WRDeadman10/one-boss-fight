import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class FirstDodgeAfterDrawContract(unittest.TestCase):
    def test_backstep_is_warmed_before_input_and_probe_exercises_first_press(self):
        source = (ROOT / "Source/OneBossFight/Player/RPGDodgeTiming.cpp").read_text(encoding="utf-8-sig")
        begin_play = source.split("void URPGDodgeTiming::BeginPlay()", 1)[1].split("void URPGDodgeTiming::TickComponent", 1)[0]
        self.assertIn("LoadedBackstepMontage = BackstepMontage.LoadSynchronous()", begin_play)
        self.assertLess(begin_play.index("LoadedBackstepMontage = BackstepMontage.LoadSynchronous()"), begin_play.index("TryBind()"))
        self.assertIn("LoadedBackstepMontage.Get()", source)
        self.assertNotIn("BackstepPrimedAbility", source, "no speculative ability-map priming")

        probe = (ROOT / "Scripts/Editor/probe_first_dodge_after_draw.py").read_text(encoding="utf-8")
        draw = probe.index('log("draw_ready=')
        first_press = probe.index("first_standing_dodge")
        self.assertLess(draw, first_press, "probe must perform the first dodge only after the R2 draw is ready")
        self.assertLess(probe.index('key(pc, R2, True)'), draw)
        self.assertIn("plc.player_montage(pawn)", probe)
        self.assertIn("first_standing_result", probe)
        self.assertIn("first_moving_result", probe)
        self.assertIn('"standing": "AM_ER_Backstep_Mixamo_V2"', probe)
        self.assertIn('"moving": "Dodge_Small_Forward_Roll_Montage"', probe)
        self.assertNotIn("set_editor_property", probe, "probe must not assign a runtime montage")
        self.assertIn("Gamepad_RightTrigger", probe)
        finish = probe.split("def finish(reason):", 1)[1].split("def tick(_dt):", 1)[0]
        self.assertIn("for name in list(STATE[\"held\"])", finish)
        self.assertIn("unregister_slate_post_tick_callback", finish)
        self.assertIn("plc.end_play()", finish)

    def test_existing_native_rules_cover_choice_but_not_runtime_activation(self):
        rules_tests = (ROOT / "Source/OneBossFight/Tests/RPGDodgeInputRulesTests.cpp").read_text(encoding="utf-8-sig")
        self.assertIn("standing tap with the optional clip selects a backstep", rules_tests)
        self.assertIn("empty optional clip preserves today's standing roll", rules_tests)
        self.assertIn("standing tap %d can choose a backstep again", rules_tests)
        self.assertNotIn("OnDodgePressed", rules_tests, "native rules test is not a runtime ability-activation test")


if __name__ == "__main__":
    unittest.main()
