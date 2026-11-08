"""Offline camera-selection regression for the Tier 2 parry capture probe."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("pie_tier2_parry.py")


class P:
    def __init__(self, **properties):
        self.properties = properties

    def get_editor_property(self, name):
        return self.properties[name]


class ParryCameraTests(unittest.TestCase):
    def test_readback_prefers_follow_camera_over_other_player_cameras(self):
        ue = types.SimpleNamespace(
            Paths=types.SimpleNamespace(project_dir=lambda: str(SCRIPT.parents[2])),
            register_slate_post_tick_callback=lambda callback: object(),
            CameraComponent=type("CameraComponent", (), {}),
        )
        spec = importlib.util.spec_from_file_location("parry_probe_under_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"unreal": ue}):
            spec.loader.exec_module(module)

        def camera(name, entries):
            c = P(post_process_settings=P(weighted_blendables=P(array=entries)))
            c.get_name = lambda: name
            return c

        other = camera("CinematicCamera", [])
        material = types.SimpleNamespace(get_name=lambda: "PPM_ParryDistortion")
        follow = camera("FollowCamera", [P(object=material, weight=1.0)])
        pawn = types.SimpleNamespace(get_components_by_class=lambda klass: [other, follow])
        self.assertEqual(module.camera_blendables(pawn),
                         "camera=FollowCamera count=1 weights=[PPM_ParryDistortion=1.000]")


if __name__ == "__main__":
    unittest.main()
