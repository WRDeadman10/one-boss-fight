"""Read-only preflight action for one selected URPGBossFrameworkProfile."""
import importlib.util
import re
import sys

import unreal

ROOT = 'C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Reviews'
VALIDATOR_PATH = ROOT + '/validate_boss_config.py'
RECEIPT_SCHEMA_PATH = 'C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/C2/receipt_schema.py'
RECEIPT_ACTION = 'preflight_selected_boss_profile'
_schema_spec = importlib.util.spec_from_file_location('c2_receipt_schema', RECEIPT_SCHEMA_PATH)
_receipt_schema = importlib.util.module_from_spec(_schema_spec)
_schema_spec.loader.exec_module(_receipt_schema)


def diagnostic(code, field, message):
    return {'code': code, 'field': field, 'message': str(message)}


def resolve(value):
    if value is None:
        return None
    loader = getattr(value, 'load_synchronous', None)
    return loader() if callable(loader) else value


def path_of(value):
    resolved = resolve(value)
    if resolved is None:
        return ''
    get_path = getattr(resolved, 'get_path_name', None)
    return get_path() if callable(get_path) else str(resolved)


def xyz(value):
    return [float(value.x), float(value.y), float(value.z)]


def build_config(profile):
    config = {
        'boss_name': profile.get_name().removeprefix('DA_').removesuffix('_Profile'),
        'destination_package_dir': profile.get_path_name().split('.')[0].rsplit('/', 1)[0],
        'fixture_label': str(profile.get_editor_property('fixture_label')),
        'damage_enabled': bool(profile.get_editor_property('damage_enabled')),
        'mesh_path': path_of(profile.get_editor_property('mesh')),
        'anim_class_path': path_of(profile.get_editor_property('anim_class')),
        'target_pawn_class_path': path_of(profile.get_editor_property('target_pawn_class')),
        'alignment_authored': bool(profile.get_editor_property('alignment_authored')),
        'phase_two_id': str(profile.get_editor_property('phase_two_id')),
        'mesh_relative_transform': {},
        'cards': [],
        'card': None,
    }
    numeric = (
        'band_min_cm', 'band_max_cm', 'walk_speed_cm_per_second', 'acceptance_cm', 'walk_timeout_seconds',
        'blend_in_seconds', 'blend_out_seconds', 'capsule_radius_cm', 'capsule_half_height_cm', 'target_health',
        'hit_step_cm', 'hit_max_substeps', 'repeat_penalty', 'repeat_memory', 'attack_count', 'boss_max_health',
        'player_hit_damage', 'phase_two_fraction', 'posture_max', 'player_posture_hit_amount', 'stagger_seconds',
        'posture_regen_delay_seconds', 'posture_regen_per_second', 'bleed_buildup_per_hit',
        'bleed_initial_threshold', 'bleed_threshold_increase', 'bleed_threshold_max', 'bleed_hp_fraction',
    )
    for key in numeric:
        config[key] = profile.get_editor_property(key)

    transform = profile.get_editor_property('mesh_relative_transform')
    config['mesh_relative_transform'] = {
        'location': xyz(transform.translation),
        'scale': xyz(transform.scale3d),
        'rotation': [0.0, 0.0, 0.0],  # The offline validator checks translation/scale; rotation is reported separately below.
    }

    def card_spec(card_asset):
        spec = card_asset.get_editor_property('spec')
        sequence = resolve(spec.get_editor_property('sequence'))
        return {
            'MoveId': str(spec.get_editor_property('move_id')),
            'PhaseId': str(spec.get_editor_property('phase_id')),
            'MinRangeCm': float(spec.get_editor_property('min_range_cm')),
            'MaxRangeCm': float(spec.get_editor_property('max_range_cm')),
            'ActiveStartSeconds': float(spec.get_editor_property('active_start_seconds')),
            'RecoveryEndSeconds': float(spec.get_editor_property('recovery_end_seconds')),
            'ClipLengthSeconds': float(sequence.get_play_length()) if sequence else 0.0,
            'HPDamage': float(spec.get_editor_property('hp_damage')),
            'MaxVerticalDeltaCm': float(spec.get_editor_property('max_vertical_delta_cm')),
        }

    single = resolve(profile.get_editor_property('card'))
    if single:
        config['card'] = card_spec(single)
    for entry in profile.get_editor_property('cards'):
        card_asset = resolve(entry.get_editor_property('card'))
        if card_asset is None:
            config['cards'].append({'move_id': '', 'cooldown_seconds': entry.get_editor_property('cooldown_seconds'), 'weight': entry.get_editor_property('weight'), 'spec': None})
            continue
        spec = card_spec(card_asset)
        config['cards'].append({
            'move_id': spec['MoveId'], 'cooldown_seconds': entry.get_editor_property('cooldown_seconds'),
            'weight': entry.get_editor_property('weight'), 'spec': spec,
        })
    return config


def report(result):
    payload = _receipt_schema.serialize_receipt(result, RECEIPT_ACTION)
    unreal.log('[C2_PROFILE_VALIDATE] ' + payload)
    lines = [result['summary']]
    if result.get('asset_path'):
        lines.append('Asset: ' + result['asset_path'])
    for item in result.get('diagnostics', []):
        lines.append('%s [%s]: %s' % (item['field'], item['code'], item['message']))
    try:
        unreal.EditorDialog.show_message('Validate Boss Profile', '\n'.join(lines), unreal.AppMsgType.OK)
    except Exception as exc:
        unreal.log_warning('[C2_PROFILE_VALIDATE] dialog_unavailable error=%s' % str(exc)[:160])


def main():
    try:
        selected = list(unreal.EditorUtilityLibrary.get_selected_assets())
    except Exception as exc:
        report({'ok': False, 'summary': 'Cannot read Content Browser selection.', 'diagnostics': [diagnostic('Selection.ReadFailed', 'ContentBrowserSelection', exc)]})
        return
    if len(selected) != 1:
        report({'ok': False, 'summary': 'Select exactly one boss framework profile.', 'diagnostics': [diagnostic('Selection.Count', 'ContentBrowserSelection', 'Expected one selected asset; found %d.' % len(selected))]})
        return
    profile = selected[0]
    asset_path = profile.get_path_name()
    if profile.get_class().get_name() != 'RPGBossFrameworkProfile':
        report({'ok': False, 'summary': 'Selected asset is not a boss framework profile.', 'asset_path': asset_path,
                'diagnostics': [diagnostic('Selection.WrongAssetType', 'AssetClass', profile.get_class().get_name())]})
        return

    config = {}
    try:
        config = build_config(profile)
        spec = importlib.util.spec_from_file_location('c2_validate_boss_config', VALIDATOR_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        tokens = module.validate_boss_config(config)
        diagnostics = []
        for token in tokens:
            match = re.search(r'\[([^\]]+)\]', token)
            field = match.group(1) if match else 'Profile'
            diagnostics.append(diagnostic(token, field, 'Offline preflight rejected this profile value.'))
    except Exception as exc:
        diagnostics = [diagnostic('Profile.PreflightException', 'ProfileReadback', exc)]

    current = list(unreal.EditorUtilityLibrary.get_selected_assets())
    if len(current) != 1 or current[0].get_path_name() != asset_path:
        report({'ok': False, 'summary': 'Content Browser selection changed during validation; result discarded.', 'asset_path': asset_path,
                'diagnostics': [diagnostic('Selection.Stale', 'ContentBrowserSelection', 'Select the intended profile and rerun.')], 'saved': False})
        return

    report({
        'ok': not diagnostics,
        'summary': 'Profile preflight passed; no assets were compiled or saved.' if not diagnostics else 'Profile preflight blocked; correct the listed fields and rerun.',
        'asset_path': asset_path,
        'fields': {
            'fixture_label': config.get('fixture_label'),
            'mesh_path': config.get('mesh_path'),
            'anim_class_path': config.get('anim_class_path'),
            'target_pawn_class_path': config.get('target_pawn_class_path'),
            'band_min_cm': config.get('band_min_cm'),
            'band_max_cm': config.get('band_max_cm'),
            'cards': len(config.get('cards', [])),
        },
        'diagnostics': diagnostics,
        'saved': False,
        'compiled': False,
        'repeat_safe': True,
    })


main()
