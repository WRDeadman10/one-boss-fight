"""Unit tests for the pure-Python decision sandbox. Run from package root:
python -m unittest discover -s tests -p 'test_*.py'
"""
import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from combat_decision_reference import decide, eligible, load_attacks

class BossDecisionSandboxTests(unittest.TestCase):
    def setUp(self):
        self.attacks={a['AttackID']:a for a in load_attacks()}

    def test_rear_hook_is_eligible_on_both_sides(self):
        a=self.attacks['A05']
        self.assertEqual([],eligible(a,140,165,1))
        self.assertEqual([],eligible(a,140,-165,1))
        self.assertIn('Angle',eligible(a,140,30,1))

    def test_phase_gate(self):
        self.assertIn('Phase',eligible(self.attacks['A10'],500,20,1))
        self.assertNotIn('Phase',eligible(self.attacks['A10'],500,20,2))

    def test_reposition_when_none_fit(self):
        pick,trace=decide(2000,0,1,0,123)
        self.assertIsNone(pick)
        self.assertEqual(12,len(trace))

    def test_fixed_seed_is_repeatable(self):
        x,_=decide(225,20,2,0,42)
        y,_=decide(225,20,2,0,42)
        self.assertEqual(x['id'],y['id'])

    def test_attack_ids_are_unique(self):
        self.assertEqual(12,len(self.attacks))

if __name__=='__main__': unittest.main()
