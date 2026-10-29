import copy
from pathlib import Path
import unittest
from native_profile_contract import extract_contract, validate_record

ROOT = Path(__file__).resolve().parents[5]


class NativeProfileContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = extract_contract(ROOT)

    def test_actual_stats_names(self):
        self.assertEqual(set(self.contract["records"]["FRPGBossStatsConfig"]),
                         {"MaxHealth", "MaxPosture", "PostureRegenDelay", "PostureRegenRate"})

    def test_explicit_good_values(self):
        self.assertEqual(validate_record(self.contract, "FRPGBossStatsConfig",
            {"MaxHealth": 1500.0, "MaxPosture": 120.0, "PostureRegenRate": 15.0, "PostureRegenDelay": 3.0}, require_all=True), [])

    def test_invented_nested_fields_reject(self):
        errors = validate_record(self.contract, "URPGBossDefinition", {"Stats": {"BasePoise": 120}, "EncounterPolicy": {"AutoTargetPlayer": True}})
        self.assertEqual(sum("unknown native property" in e for e in errors), 2)

    def test_missing_is_not_defaulted(self):
        self.assertEqual(len(validate_record(self.contract, "FRPGBossStatsConfig", {"MaxHealth": 1500}, require_all=True)), 3)

    def test_bool_and_nonfinite_reject(self):
        for value in [True, float("nan"), float("inf"), 10**1000]:
            with self.subTest(value_type=type(value).__name__):
                self.assertTrue(validate_record(self.contract, "FRPGBossStatsConfig", {"MaxHealth": value}))

    def test_recursive_phase_fields(self):
        errors = validate_record(self.contract, "URPGBossDefinition", {"Phases": [{"PhaseId": "PhaseTwo", "HealthThresholdPercent": .5}]})
        self.assertTrue(any("HealthThresholdPercent" in e for e in errors))
        self.assertEqual(validate_record(self.contract, "URPGBossDefinition", {"Phases": [{"PhaseId": "PhaseTwo", "EntryHealthFraction": .5}]}), [])

    def test_array_shape_and_softref_types(self):
        self.assertTrue(validate_record(self.contract, "URPGBossDefinition", {"Animations": "not an array"}))
        self.assertTrue(validate_record(self.contract, "URPGBossDefinition", {"Skeleton": 5}))

    def test_no_input_mutation_or_manifest_fabrication(self):
        payload = {"DefinitionId": "Draft", "Fields": []}
        before = copy.deepcopy(payload)
        self.assertEqual(validate_record(self.contract, "URPGBossDefinition", payload), [])
        self.assertEqual(payload, before)


if __name__ == "__main__":
    unittest.main()
