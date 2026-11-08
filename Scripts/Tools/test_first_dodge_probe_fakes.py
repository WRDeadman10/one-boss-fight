import importlib.util
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "Scripts/Editor/probe_first_dodge_after_draw.py"


class Vec:
    def __init__(self, x=0.0):
        self.x = x

    def length(self):
        return abs(self.x)

    def __sub__(self, other):
        return Vec(self.x - other.x)


class FakePawn:
    def __init__(self):
        self.location = 0.0
        self.moving = False

    def get_actor_location(self):
        return Vec(self.location)

    def get_actor_forward_vector(self):
        return Vec(1.0)

    def get_velocity(self):
        return Vec(100.0 if self.moving else 0.0)

    def get_last_movement_input_vector(self):
        return Vec(1.0 if self.moving else 0.0)

    def get_pending_movement_input_vector(self):
        return Vec(1.0 if self.moving else 0.0)

    def add_movement_input(self, _direction, _scale, _force):
        self.moving = True
        self.location += 1.0


class FakeDodge:
    def __init__(self):
        self.count = 0

    def get_press_count(self):
        return self.count

    def get_stage_name(self):
        return "None"

    def get_backstep_count(self):
        return 0

    def get_editor_property(self, _name):
        return "AM_ER_Backstep_Mixamo_V2"


class FirstDodgeProbeFakes(unittest.TestCase):
    def run_case(self, case):
        clock = [0.0]
        messages = []
        world, pc, pawn = object(), object(), FakePawn()
        dodge, loadout = FakeDodge(), types.SimpleNamespace(is_combat_enabled=lambda: True)
        input_utils = types.SimpleNamespace()

        def set_key_down(_pc, key, down):
            if down and key == "Gamepad_FaceButton_Right":
                dodge.count += 1
            return True

        input_utils.set_key_down = set_key_down
        unreal_stub = types.SimpleNamespace(
            Paths=types.SimpleNamespace(project_dir=lambda: str(ROOT)),
            RPGInputTestUtils=input_utils,
            register_slate_post_tick_callback=lambda _callback: "fake-handle",
            log=lambda _message: None,
        )
        plc_stub = types.ModuleType("pie_lead_common")
        plc_stub.component = lambda _pawn, name: loadout if name == "RPGBuildLoadout" else dodge
        plc_stub.player_montage = lambda _pawn: (None, None)
        plc_stub.enter_combat = lambda _pawn: None

        def game_time(_world):
            clock[0] += 0.05
            return clock[0]

        def wait(_seconds):
            yield 0.0

        plc_stub.game_time = game_time
        sys.modules["unreal"] = unreal_stub
        sys.modules["pie_lead_common"] = plc_stub
        name = "first_dodge_probe_fake_" + case
        spec = importlib.util.spec_from_file_location(name, PROBE)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            module.CASE = case
            module.actors = lambda: (world, pc, pawn)
            module.wait = wait
            module.log = lambda message: messages.append(str(message))
            list(module.run())
        finally:
            sys.modules.pop(name, None)
            sys.modules.pop("unreal", None)
            sys.modules.pop("pie_lead_common", None)
        return messages

    def test_standing_first_press_scenario_runs_with_no_direction_input(self):
        messages = self.run_case("standing")
        draw_ready = next(i for i, x in enumerate(messages) if "draw_ready=True" in x)
        first_press = next(i for i, x in enumerate(messages) if "first_standing_dodge" in x)
        self.assertLess(draw_ready, first_press)
        self.assertTrue(any("scenario=standing expected_first_montage=AM_ER_Backstep_Mixamo_V2" in x for x in messages))
        self.assertTrue(any("first_standing_dodge case=standing" in x for x in messages))
        self.assertTrue(any("first_standing_result" in x for x in messages))
        self.assertTrue(any("press_observables case=standing press=1 speed_cm_s=0.0 last_input_size=0.000" in x for x in messages))

    def test_moving_first_press_samples_movement_before_input(self):
        messages = self.run_case("moving")
        draw_ready = next(i for i, x in enumerate(messages) if "draw_ready=True" in x)
        first_press = next(i for i, x in enumerate(messages) if "first_moving_dodge" in x)
        self.assertLess(draw_ready, first_press)
        self.assertTrue(any("scenario=moving expected_first_montage=Dodge_Small_Forward_Roll_Montage" in x for x in messages))
        self.assertTrue(any("first_moving_dodge case=moving" in x for x in messages))
        self.assertTrue(any("first_moving_result" in x for x in messages))
        self.assertTrue(any("press_observables case=moving press=1 speed_cm_s=100.0 last_input_size=1.000" in x for x in messages))


if __name__ == "__main__":
    unittest.main()
