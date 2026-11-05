"""Read-only offline coverage validator for the C5 weapon parameter inventory."""
import json
from pathlib import Path

SCHEMA = 'c5.weapon-parameter-coverage.v1'
ALLOWED_CLASSIFICATIONS = {
    'data_driven', 'data_and_fallback', 'hardcoded_pack_asset',
    'hardcoded_structural', 'intentional_fixed_value', 'pack_authored_unresolved_offline',
}
REQUIRED_C3_FIELDS = {
    'weapon_id', 'style_name', 'style_asset_path', 'item_path', 'item_base_class',
    'actor_class', 'ability_class', 'hud_weapon_word', 'style_aliases',
    'attack_rows[].kind', 'attack_rows[].posture_damage', 'attack_rows[].stamina_cost',
    'attack_rows[].bleed_buildup', 'attack_rows[].health_damage_multiplier',
    'attack_rows[].hyperarmor_start', 'attack_rows[].hyperarmor_end',
    'build.build_id', 'build.console_name', 'build.aliases', 'build.display_name',
    'build.ui_order', 'catalog.legacy_slot', 'catalog.icon_path',
}


def _safe_evidence_path(repo_root, evidence):
    path_text = evidence.split(':', 1)[0]
    path = (repo_root / path_text).resolve()
    root = repo_root.resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return None
    return path if path.is_file() else None


def validate_inventory(inventory, repo_root):
    errors = []
    if not isinstance(inventory, dict):
        return ['Inventory root must be a JSON object.']
    if inventory.get('schema') != SCHEMA:
        errors.append('Inventory schema must equal %s.' % SCHEMA)
    if not isinstance(inventory.get('source_audit'), str) or not inventory.get('source_audit'):
        errors.append('source_audit must name the source audit document.')
    elif not _safe_evidence_path(repo_root, inventory['source_audit']):
        errors.append('source_audit path is missing or escapes the repository.')
    gaps = inventory.get('unresolved_gaps')
    if not isinstance(gaps, list) or not gaps or any(not isinstance(g, str) or not g.strip() for g in gaps):
        errors.append('unresolved_gaps must be a non-empty array of explanatory strings.')

    entries = inventory.get('entries')
    if not isinstance(entries, list) or not entries:
        return errors + ['entries must be a non-empty array.']
    names = set()
    mapped_fields = set()
    for index, entry in enumerate(entries):
        prefix = 'entries[%d]' % index
        if not isinstance(entry, dict):
            errors.append(prefix + ' must be an object.')
            continue
        name = entry.get('field')
        if not isinstance(name, str) or not name.strip():
            errors.append(prefix + '.field must be a non-empty string.')
        elif name in names:
            errors.append(prefix + '.field duplicates %s.' % name)
        else:
            names.add(name)
        if entry.get('classification') not in ALLOWED_CLASSIFICATIONS:
            errors.append(prefix + '.classification is unsupported.')
        for key in ('asset_surface', 'validator', 'consumer'):
            if not isinstance(entry.get(key), str) or not entry[key].strip():
                errors.append(prefix + '.' + key + ' must be a non-empty string.')
        mappings = entry.get('c3_config')
        if not isinstance(mappings, list) or any(not isinstance(x, str) or not x.strip() for x in mappings):
            errors.append(prefix + '.c3_config must be an array of non-empty strings.')
        else:
            mapped_fields.update(mappings)
        evidence = entry.get('evidence')
        if not isinstance(evidence, list) or not evidence:
            errors.append(prefix + '.evidence must be a non-empty array.')
        else:
            for ref in evidence:
                if not isinstance(ref, str) or not ref.strip() or not _safe_evidence_path(repo_root, ref):
                    errors.append(prefix + ' has missing or unsafe evidence path: %r.' % (ref,))

    missing_mappings = sorted(REQUIRED_C3_FIELDS - mapped_fields)
    if missing_mappings:
        errors.append('C3 schema coverage missing: ' + ', '.join(missing_mappings))
    unused_mappings = sorted(mapped_fields - REQUIRED_C3_FIELDS)
    if unused_mappings:
        errors.append('C3 mapping names not in required schema: ' + ', '.join(unused_mappings))
    return errors


def build_report(inventory, repo_root):
    errors = validate_inventory(inventory, repo_root)
    entries = inventory.get('entries', []) if isinstance(inventory, dict) else []
    mapping_count = sum(bool(e.get('c3_config')) for e in entries if isinstance(e, dict))
    return {
        'ok': not errors,
        'schema': SCHEMA,
        'entry_count': len(entries),
        'mapped_entry_count': mapping_count,
        'non_configurable_entry_count': len(entries) - mapping_count,
        'unresolved_gap_count': len(inventory.get('unresolved_gaps', [])) if isinstance(inventory, dict) and isinstance(inventory.get('unresolved_gaps'), list) else 0,
        'no_mutation': {'assets_written': False, 'source_written': False},
        'diagnostics': errors,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inventory', type=Path)
    parser.add_argument('--repo-root', type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        inventory = json.loads(args.inventory.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        report = {'ok': False, 'schema': SCHEMA, 'diagnostics': ['Cannot read inventory: %s' % exc],
                  'no_mutation': {'assets_written': False, 'source_written': False}}
    else:
        report = build_report(inventory, args.repo_root)
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
