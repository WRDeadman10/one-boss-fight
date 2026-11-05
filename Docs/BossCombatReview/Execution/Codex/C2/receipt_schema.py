"""Pure receipt serialization and action dispatch helpers for the C2 Editor utilities."""
import json

SCHEMA_VERSION = 'c2.validate-boss.receipt.v1'


def dispatch_action(selection_count, asset_class_name):
    if selection_count != 1:
        return None, 'Selection.Count'
    if asset_class_name == 'RPGBossFrameworkProfile':
        return 'validate_selected_boss_profile.py', ''
    if asset_class_name == 'AnimBlueprint':
        return 'validate_selected_anim_blueprint.py', ''
    return None, 'Selection.WrongAssetType'


def normalize_receipt(payload, action):
    result = dict(payload)
    result['schema_version'] = SCHEMA_VERSION
    result['action'] = action
    result.setdefault('ok', False)
    result.setdefault('summary', '')
    result.setdefault('asset_path', '')
    result.setdefault('fields', {})
    result.setdefault('diagnostics', [])
    result.setdefault('saved', False)
    result.setdefault('compiled', False)
    return result


def serialize_receipt(payload, action):
    return json.dumps(normalize_receipt(payload, action), sort_keys=True, separators=(',', ':'), default=str)
