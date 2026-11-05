"""Pure-Python contract checks for C2 selection dispatch and receipt serialization."""
import importlib.util
import json
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('c2_receipt_schema', HERE / 'receipt_schema.py')
schema = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(schema)
FIXTURE = json.loads((HERE / 'fixtures' / 'dispatch_cases.json').read_text(encoding='utf-8'))


class ReceiptSchemaTests(unittest.TestCase):
    def test_dispatch_fixture_cases(self):
        self.assertEqual(len(FIXTURE['cases']), 5)
        for case in FIXTURE['cases']:
            with self.subTest(case=case['name']):
                self.assertEqual(
                    schema.dispatch_action(case['selection_count'], case['asset_class']),
                    (case['action'], case['diagnostic'] or ''),
                )

    def test_normalize_adds_stable_defaults_and_preserves_payload(self):
        result = schema.normalize_receipt({'ok': True, 'custom': 7}, 'dispatch')
        self.assertEqual(result['schema_version'], 'c2.validate-boss.receipt.v1')
        self.assertEqual(result['action'], 'dispatch')
        self.assertEqual(result['custom'], 7)
        self.assertEqual(result['fields'], {})
        self.assertEqual(result['diagnostics'], [])
        self.assertFalse(result['saved'])
        self.assertFalse(result['compiled'])

    def test_serialization_is_compact_sorted_and_round_trips(self):
        payload = {'ok': True, 'summary': 'ok', 'asset_path': '/Game/Boss/BP'}
        first = schema.serialize_receipt(payload, 'preflight_selected_boss_profile')
        second = schema.serialize_receipt(payload, 'preflight_selected_boss_profile')
        self.assertEqual(first, second)
        self.assertNotIn(': ', first)
        decoded = json.loads(first)
        self.assertEqual(decoded['schema_version'], schema.SCHEMA_VERSION)
        self.assertEqual(decoded['action'], 'preflight_selected_boss_profile')
        self.assertEqual(decoded['asset_path'], payload['asset_path'])
        self.assertFalse(decoded['compiled'])

    def test_structured_diagnostic_context_survives_serialization(self):
        diagnostic = {
            'code': 'BlueprintCompile.CompilerLog', 'severity': 'error',
            'asset_match': True, 'asset_path': '/Game/Boss/ABP_Boss.ABP_Boss',
            'field': 'CompilerLog', 'message': '[Compiler] Error: missing node',
        }
        payload = {
            'ok': False, 'asset_path': diagnostic['asset_path'],
            'fields': {'status_before': 'UpToDate', 'status_after': 'Error', 'generated_class': ''},
            'diagnostics': [diagnostic], 'saved': False, 'compiled': True,
        }
        encoded = schema.serialize_receipt(payload, 'compile_selected_anim_blueprint')
        decoded = json.loads(encoded)
        self.assertEqual(decoded['diagnostics'], [diagnostic])
        self.assertEqual(decoded['fields'], payload['fields'])
        self.assertEqual(decoded['asset_path'], diagnostic['asset_path'])
        self.assertFalse(decoded['ok'])


if __name__ == '__main__':
    unittest.main()
