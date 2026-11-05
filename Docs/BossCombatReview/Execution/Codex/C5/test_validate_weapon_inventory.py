"""Pure-Python fixtures for the read-only C5 inventory coverage validator."""
import copy
import hashlib
import json
import pathlib
import unittest

from validate_weapon_inventory import build_report, validate_inventory

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[4]
MANIFEST_PATH = HERE / 'weapon_parameter_coverage.json'


class WeaponInventoryValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = json.loads(MANIFEST_PATH.read_text(encoding='utf-8'))

    def test_repository_inventory_has_complete_coverage(self):
        self.assertEqual(validate_inventory(self.inventory, REPO_ROOT), [])
        report = build_report(self.inventory, REPO_ROOT)
        self.assertTrue(report['ok'])
        self.assertEqual(report['entry_count'], 25)
        self.assertEqual(report['mapped_entry_count'], 21)
        self.assertEqual(report['non_configurable_entry_count'], 4)

    def test_missing_schema_mapping_is_reported(self):
        data = copy.deepcopy(self.inventory)
        data['entries'] = [e for e in data['entries'] if e['field'] != 'style_name']
        errors = validate_inventory(data, REPO_ROOT)
        self.assertTrue(any('C3 schema coverage missing' in e for e in errors))

    def test_invalid_classification_is_reported(self):
        data = copy.deepcopy(self.inventory)
        data['entries'][0]['classification'] = 'tunable_everywhere'
        self.assertTrue(any('.classification is unsupported' in e for e in validate_inventory(data, REPO_ROOT)))

    def test_missing_evidence_is_reported(self):
        data = copy.deepcopy(self.inventory)
        data['entries'][0]['evidence'] = ['Source/does/not/exist.cpp:1']
        self.assertTrue(any('missing or unsafe evidence path' in e for e in validate_inventory(data, REPO_ROOT)))

    def test_validator_is_read_only(self):
        before = hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest()
        report = build_report(self.inventory, REPO_ROOT)
        after = hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest()
        self.assertFalse(report['no_mutation']['assets_written'])
        self.assertFalse(report['no_mutation']['source_written'])
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
