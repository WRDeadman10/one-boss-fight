"""Keep first-dodge diagnostics observational; do not alter input semantics."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "Scripts" / "Editor" / "probe_first_dodge_after_draw.py"


class FirstDodgeObservationContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PROBE.read_text(encoding="utf-8")

    def test_known_read_only_buffer_and_montage_observations_are_logged(self):
        self.assertIn('"Get Buffered Input Tag"', self.source)
        self.assertIn("montage_position", self.source)
        self.assertIn("buffered_input_tag", self.source)

    def test_probe_does_not_bind_or_inject_actions_or_change_recovery(self):
        for forbidden in ("inject_action(", "BindAction(", "add_mapping_context(",
                          "TryActivateAbilityByClass", "set_editor_property("):
            self.assertNotIn(forbidden, self.source)
        self.assertIn('key(pc, DODGE, True)', self.source)
        self.assertIn('key(pc, DODGE, False)', self.source)

    def test_dodge_press_tick_cadence_is_unchanged(self):
        start = self.source.index('key(pc, DODGE, True)')
        tick = self.source.index('yield 0.0', start)
        release = self.source.index('key(pc, DODGE, False)', tick)
        sequence = self.source[start:release]
        self.assertEqual(sequence.count('yield 0.0'), 1)
        self.assertNotIn('yield from wait(', sequence)


if __name__ == "__main__":
    unittest.main(verbosity=2)
