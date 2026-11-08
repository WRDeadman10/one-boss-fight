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


if __name__ == "__main__":
    unittest.main()
