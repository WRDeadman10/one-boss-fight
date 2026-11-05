"""Read-only SHA-256 manifest for existing C3 pack assets referenced by a weapon config."""
import argparse
import hashlib
import json
from pathlib import Path


REFERENCE_FIELDS = (
    'style_asset_path', 'item_path', 'item_base_class', 'actor_class', 'ability_class',
)


def package_to_file(asset_path, content_root):
    package = asset_path.split('.', 1)[0]
    leaf = package.rsplit('/', 1)[-1]
    if leaf.endswith('_C'):
        package = package[:-2]
    if not package.startswith('/Game/'):
        raise ValueError('Expected a /Game asset path: ' + asset_path)
    return content_root.joinpath(*package[len('/Game/'):].split('/')).with_suffix('.uasset')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('--content-root', type=Path, default=Path('Content'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding='utf-8-sig'))
    references = {key: config.get(key) for key in REFERENCE_FIELDS}
    icon = (config.get('catalog') or {}).get('icon_path')
    if icon:
        references['catalog.icon_path'] = icon
    records = []
    for field, asset_path in references.items():
        if not isinstance(asset_path, str) or not asset_path:
            raise ValueError('Missing prerequisite reference: ' + field)
        file_path = package_to_file(asset_path, args.content_root)
        if not file_path.is_file():
            raise FileNotFoundError('%s references missing package %s' % (field, file_path))
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        records.append({'field': field, 'asset_path': asset_path, 'file': file_path.as_posix(), 'sha256': digest})
    manifest = {
        'schema': 'c3.prerequisite-control.v1',
        'purpose': 'unchanged pack prerequisite control; excludes intended DA_WeaponAttacks and DA_CombatCatalog targets',
        'records': records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print('Wrote %d prerequisite hashes to %s' % (len(records), args.output))


if __name__ == '__main__':
    main()
