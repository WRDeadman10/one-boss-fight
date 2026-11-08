"""Scoped readback tests for the Lead-only aura lifecycle probe."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("pie_tier2_aura.py")


class AuraReadbackTests(unittest.TestCase):
    def test_only_target_aura_counts_and_inactive_or_duplicate_fails(self):
        ue = types.SimpleNamespace(
            Paths=types.SimpleNamespace(project_dir=lambda: str(SCRIPT.parents[2])),
            NiagaraComponent=type("NiagaraComponent", (), {}),
            register_slate_post_tick_callback=lambda callback: object(),
        )
        spec = importlib.util.spec_from_file_location("aura_probe_under_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"unreal": ue}):
            spec.loader.exec_module(module)

        def component(name, active=True):
            return types.SimpleNamespace(
                get_asset=lambda: types.SimpleNamespace(get_name=lambda: name),
                get_name=lambda: "NiagaraComponent",
                is_active=lambda: active,
            )

        boss = types.SimpleNamespace(get_components_by_class=lambda cls: [component("OtherEffect")])
        module.log = lambda message: None
        self.assertTrue(module.check("no_aura", boss, 0))
        boss.get_components_by_class = lambda cls: [component("OtherEffect"), component("NS_Boss_PhaseTwoAura")]
        self.assertTrue(module.check("one_active", boss, 1))
        boss.get_components_by_class = lambda cls: [component("NS_Boss_PhaseTwoAura", False)]
        self.assertFalse(module.check("inactive", boss, 1))
        boss.get_components_by_class = lambda cls: [component("NS_Boss_PhaseTwoAura"), component("NS_Boss_PhaseTwoAura")]
        self.assertFalse(module.check("duplicate", boss, 1))

    def test_lifecycle_probe_covers_above_and_at_half_health_then_resets(self):
        source = SCRIPT.read_text(encoding="utf-8")
        above = source.index('attribute(boss, "Set Current Attribute Value", maximum * 0.501)')
        above_check = source.index('check("above_threshold", boss, 0)', above)
        at = source.index('attribute(boss, "Set Current Attribute Value", maximum * 0.5)', above_check)
        at_check = source.index('check("half_health", boss, 1)', at)
        reset = source.index('check("encounter_reset", boss, 0)', at_check)
        next_phase = source.index('check("next_phase", boss, 1)', reset)
        self.assertLess(above, above_check)
        self.assertLess(above_check, at)
        self.assertLess(at_check, reset)
        self.assertLess(reset, next_phase)
        self.assertIn('"rpg.Art.Tier2 0"', source)
        self.assertIn('"rpg.Art.Tier2 1"', source)
        self.assertIn('len(S["checks"]) == 7', source)
        self.assertIn('"rpg.Art.Tier2 0"', source)
        self.assertIn('"rpg.Art.Tier2 1"', source)


if __name__ == "__main__":
    unittest.main()
