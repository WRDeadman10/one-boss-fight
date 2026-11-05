# C3 v0 "New Weapon" utility, rows part (lead, Claude), run in the UNREAL EDITOR:
#   run_editor_script.ps1 -Script "<this file> <weapon_config.json> [--apply]" -OutDir <absolute dir> -Task <name> -NullRhi 1
# DRY-RUN BY DEFAULT: without --apply nothing is written. What it does:
#   1. reads the config (schema: Antigravity/Reviews/C3_NEW_WEAPON_UTILITY_DESIGN.md), loads the saved /Game/OneBossFight/Data/DA_WeaponAttacks rows,
#   2. runs the pure validator Antigravity/Reviews/validate_weapon_config.py with the REAL existing rows and the engine's does_asset_exist,
#   3. prints the plan (rows to append, or old -> new numbers in update_existing_style mode),
#   4. with --apply: appends the rows (mode new_weapon) or edits them in place (update_existing_style), reads EVERY row back, saves ONLY DA_WeaponAttacks.
# The pack parts of a weapon (combat style asset, item, actor Blueprint, ability, montages) are NOT created here: they must exist (the validator checks the paths).
# v1: with `catalog.register: true` it also creates DA_Weapon_<id> and DA_Build_<id> (NEW assets, refused if they exist) and appends them to the catalog root (DA_CombatCatalog, an EDIT of a shipped asset, read back).
import importlib.util
import json
import sys

import unreal

ROOT = 'C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/'
VALIDATOR = ROOT + 'Antigravity/Reviews/validate_weapon_config.py'
TABLE = '/Game/OneBossFight/Data/DA_WeaponAttacks.DA_WeaponAttacks'
FIELDS = [('posture_damage', 'posture_damage'), ('stamina_cost', 'stamina_cost'), ('bleed_buildup', 'bleed_buildup'),
          ('health_damage_multiplier', 'health_damage_multiplier'), ('hyperarmor_start', 'hyper_armor_start'), ('hyperarmor_end', 'hyper_armor_end')]


def tag(t, payload):
    unreal.log('[NEWWEAPON_%s] %s' % (t, json.dumps(payload, default=str)))


def fatal(msg):
    unreal.log_error('[NEWWEAPON_FATAL] ' + msg)
    raise SystemExit(msg)


def load_reference(value):
    loader = getattr(value, 'load_synchronous', None)
    resolved = loader() if callable(loader) else value
    return resolved


def normalized_token(value):
    return str(value).strip().strip('"').strip().lower()


def preflight_catalog(catalog_cfg, weapon_cfg):
    """Load the live root and refuse identity/token collisions before any mutation."""
    if not catalog_cfg.get('register'):
        return None
    weapon_package = catalog_cfg['weapon_asset_path'].split('.')[0]
    build_package = catalog_cfg['build_asset_path'].split('.')[0]
    if weapon_package == build_package:
        fatal('weapon and build definitions must use distinct destination packages')
    for package in (weapon_package, build_package):
        if lib.does_asset_exist(package):
            fatal('catalog destination exists, refusing before table write: ' + package)
    root_path = catalog_cfg['catalog_root_path']
    root = unreal.load_asset(root_path)
    if root is None:
        fatal('catalog root not found before table write: ' + root_path)
    if root_path.split('.')[0] in (weapon_package, build_package):
        fatal('catalog root cannot be a new definition destination')

    existing_weapon_ids = set()
    existing_styles = {}
    for soft_ref in root.get_editor_property('weapons'):
        asset = load_reference(soft_ref)
        if asset is None:
            fatal('catalog preflight found an unresolved weapon definition; refusing')
        definition = asset.get_editor_property('definition')
        weapon_id = str(definition.get_editor_property('weapon_id'))
        existing_weapon_ids.add(normalized_token(weapon_id))
        for field in ('style_name', 'style_aliases'):
            values = definition.get_editor_property(field)
            if field == 'style_name':
                values = [values]
            for value in values:
                token = normalized_token(value)
                if token:
                    existing_styles[token] = weapon_id

    existing_build_ids = set()
    existing_build_tokens = {}
    for soft_ref in root.get_editor_property('builds'):
        asset = load_reference(soft_ref)
        if asset is None:
            fatal('catalog preflight found an unresolved build definition; refusing')
        definition = asset.get_editor_property('definition')
        build_id = str(definition.get_editor_property('build_id'))
        existing_build_ids.add(normalized_token(build_id))
        tokens = [definition.get_editor_property('console_name'), build_id]
        tokens.extend(list(definition.get_editor_property('aliases')))
        for value in tokens:
            token = normalized_token(value)
            if token:
                existing_build_tokens[token] = build_id

    candidate_weapon_id = normalized_token(weapon_cfg['weapon_id'])
    if candidate_weapon_id in existing_weapon_ids:
        fatal('duplicate catalog WeaponId: ' + weapon_cfg['weapon_id'])
    candidate_styles = [weapon_cfg['style_name']] + list(weapon_cfg.get('style_aliases', []))
    for value in candidate_styles:
        token = normalized_token(value)
        if token in existing_styles:
            fatal('duplicate catalog style/alias %s already belongs to %s' % (value, existing_styles[token]))

    build_cfg = weapon_cfg['build']
    candidate_build_id = normalized_token(build_cfg['build_id'])
    if candidate_build_id in existing_build_ids:
        fatal('duplicate catalog BuildId: ' + build_cfg['build_id'])
    candidate_tokens = [build_cfg['console_name'], build_cfg['build_id']] + list(build_cfg.get('aliases', []))
    for value in candidate_tokens:
        token = normalized_token(value)
        if token in existing_build_tokens:
            fatal('duplicate catalog build token %s already belongs to %s' % (value, existing_build_tokens[token]))
    return root


def kind_enum(name):
    out = ''.join('_' + c if c.isupper() and i else c for i, c in enumerate(name)).upper()
    return getattr(unreal.RPGAttackKind, out)


def reference_path(value):
    # Lead fix 2026-11-04 (live probe): UE 5.5 Python SoftObjectPath has no get_asset_path_string and its repr is "{}";
    # export_text() returns the full path (C3/runs_v2_lead/probe_softpath).
    if type(value).__name__ == 'SoftObjectPath' and callable(getattr(value, 'export_text', None)):
        return value.export_text()   # duck-typed so offline mocks (where SoftObjectPath may be a factory) still work
    path_string = getattr(value, 'get_asset_path_string', None)
    if callable(path_string):
        return path_string()
    loader = getattr(value, 'load_synchronous', None)
    resolved = loader() if callable(loader) else value
    if resolved is None:
        return ''
    get_path = getattr(resolved, 'get_path_name', None)
    if callable(get_path):
        return get_path()
    path_string = getattr(resolved, 'get_asset_path_string', None)
    return path_string() if callable(path_string) else str(resolved)


argv = [a for a in sys.argv[1:] if a]
if not argv:
    fatal('usage: new_weapon.py <weapon_config.json> [--apply]')
APPLY = '--apply' in argv
try:
    with open(argv[0], 'r', encoding='utf-8-sig') as f:
        cfg = json.load(f)
except (OSError, UnicodeError, json.JSONDecodeError) as exc:
    fatal('invalid weapon config input: ' + str(exc))
if not isinstance(cfg, dict):
    fatal('invalid weapon config input: root must be a JSON object')
STYLE = cfg.get('style_name', '')
MODE = cfg.get('mode', 'new_weapon')

table = unreal.load_asset(TABLE)
if table is None:
    fatal('DA_WeaponAttacks not found')
rows = list(table.get_editor_property('rows'))
existing_rows = {(str(r.get_editor_property('weapon')), str(r.get_editor_property('kind')).split('.')[-1].split(':')[0].title().replace('_', '')) for r in rows}
# the enum prints as <RPGAttackKind.JUMP_LIGHT: 4>: normalise to the config spelling (Light, JumpLight ...)
def norm(k):
    k = str(k)
    if '.' in k:
        k = k.split('.')[-1].split(':')[0]
    return ''.join(p.title() for p in k.split('_'))
existing_rows = {(str(r.get_editor_property('weapon')), norm(r.get_editor_property('kind'))) for r in rows}

lib = unreal.EditorAssetLibrary


def exists(path):
    base = path[:-2] if path.endswith('_C') else path   # a generated Blueprint class path ends with _C: the asset is the Blueprint
    return lib.does_asset_exist(base)


spec = importlib.util.spec_from_file_location('validate_weapon_config', VALIDATOR)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
errors = mod.validate_weapon_config(cfg, None, exists, existing_rows)
tag('VALIDATION', {'errors': errors, 'existing_rows': len(existing_rows)})
if errors:
    fatal('config refused: ' + '; '.join(errors))

# Catalog destination checks happen before any attack-table mutation or save.
CAT = cfg.get('catalog') or {}
catalog_root = None
if CAT.get('register'):
    wpath, bpath, rpath = CAT['weapon_asset_path'], CAT['build_asset_path'], CAT['catalog_root_path']
    wpkg = wpath.split('.')[0]
    bpkg = bpath.split('.')[0]
    catalog_root = preflight_catalog(CAT, cfg)

plan = []
for r in cfg['attack_rows']:
    plan.append({'style': STYLE, 'kind': r['kind'], 'mode': MODE, **{k: r.get(k) for k, _p in FIELDS}})
tag('PLAN', plan)
if (cfg.get('catalog') or {}).get('register'):
    tag('CATALOG_PLAN', {'weapon_asset': cfg['catalog']['weapon_asset_path'], 'build_asset': cfg['catalog']['build_asset_path'], 'root': cfg['catalog']['catalog_root_path'], 'console_name': cfg['build']['console_name'], 'legacy_slot': cfg['catalog'].get('legacy_slot', -1)})
if not APPLY:
    tag('END', {'written': [], 'dry_run': True})
    raise SystemExit(0)

# ---- apply
by_key = {(str(x.get_editor_property('weapon')), norm(x.get_editor_property('kind'))): x for x in rows}
for r in cfg['attack_rows']:
    kind = r['kind']
    if MODE == 'update_existing_style':
        row = by_key[(STYLE, kind)]
        tag('UPDATE', {'style': STYLE, 'kind': kind, 'old': {k: row.get_editor_property(p) for k, p in FIELDS}, 'new': {k: r.get(k) for k, _p in FIELDS}})
    else:
        row = unreal.RPGWeaponAttackRow()
        row.set_editor_property('weapon', STYLE)
        row.set_editor_property('kind', kind_enum(kind))
        rows.append(row)
    for k, p in FIELDS:
        if k in r:
            row.set_editor_property(p, float(r[k]))
    row.set_editor_property('note', r.get('note', ''))
table.set_editor_property('rows', rows)

# readback of every written row
back = list(table.get_editor_property('rows'))
got = {(str(x.get_editor_property('weapon')), norm(x.get_editor_property('kind'))): x for x in back}
for r in cfg['attack_rows']:
    x = got.get((STYLE, r['kind']))
    if x is None:
        fatal('readback: row missing %s/%s' % (STYLE, r['kind']))
    for k, p in FIELDS:
        if k in r and abs(float(x.get_editor_property(p)) - float(r[k])) > 1e-4:
            fatal('readback mismatch %s/%s %s: %r != %r' % (STYLE, r['kind'], k, x.get_editor_property(p), r[k]))
tag('READBACK_OK', {'rows_total': len(back), 'written': len(cfg['attack_rows'])})
if not lib.save_loaded_asset(table):
    fatal('DA_WeaponAttacks save failed')

# ---- v1: catalog registration (weapon definition + build definition + root catalog), only when asked
CAT = cfg.get('catalog') or {}
written = [TABLE]
if CAT.get('register'):
    def spath(p):
        return unreal.SoftObjectPath(p)

    def split(path):
        pkg, name = path.rsplit('/', 1)
        return pkg, name.split('.')[0]

    wpath, bpath, rpath = CAT['weapon_asset_path'], CAT['build_asset_path'], CAT['catalog_root_path']
    for p in (wpath, bpath):
        if lib.does_asset_exist(p.split('.')[0]):
            fatal('catalog asset exists, refusing: ' + p)
    root = catalog_root
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    wpkg, wname = split(wpath)
    weapon_asset = tools.create_asset(wname, wpkg, unreal.RPGWeaponDefinition, unreal.DataAssetFactory())
    bpkg, bname = split(bpath)
    build_asset = tools.create_asset(bname, bpkg, unreal.RPGBuildDefinition, unreal.DataAssetFactory())
    if weapon_asset is None or build_asset is None:
        fatal('catalog asset creation failed')
    wd = weapon_asset.get_editor_property('definition')
    wd.set_editor_property('weapon_id', cfg['weapon_id'])
    wd.set_editor_property('style_name', STYLE)
    wd.set_editor_property('style_asset', spath(cfg['style_asset_path']))
    wd.set_editor_property('item_path', spath(cfg['item_path']))
    wd.set_editor_property('item_base_class', spath(cfg['item_base_class']))
    wd.set_editor_property('actor_class', spath(cfg['actor_class']))
    wd.set_editor_property('ability_class', spath(cfg['ability_class']))
    wd.set_editor_property('hud_weapon_word', cfg['hud_weapon_word'])
    wd.set_editor_property('style_aliases', [unreal.Name(a) for a in cfg.get('style_aliases', [])])
    if CAT.get('icon_path'):
        wd.set_editor_property('icon', spath(CAT['icon_path']))
    wd.set_editor_property('actions', [kind_enum(r['kind']) for r in cfg['attack_rows']])
    wd.set_editor_property('require_exact_rows', bool(CAT.get('require_exact_rows', False)))
    weapon_asset.set_editor_property('definition', wd)
    b = cfg['build']
    bd = build_asset.get_editor_property('definition')
    bd.set_editor_property('build_id', b['build_id'])
    bd.set_editor_property('console_name', b['console_name'])
    bd.set_editor_property('aliases', list(b.get('aliases', [])))
    bd.set_editor_property('display_name', b['display_name'])
    bd.set_editor_property('ui_order', int(b['ui_order']))
    bd.set_editor_property('legacy_slot', int(CAT.get('legacy_slot', -1)))
    bd.set_editor_property('weapon_id', cfg['weapon_id'])
    if CAT.get('icon_path'):
        bd.set_editor_property('icon', spath(CAT['icon_path']))
    build_asset.set_editor_property('definition', bd)
    # readback of the two new definitions
    wb = weapon_asset.get_editor_property('definition')
    bb = build_asset.get_editor_property('definition')
    expected_weapon_fields = {
        'weapon_id': cfg['weapon_id'], 'style_name': STYLE,
        'style_asset': cfg['style_asset_path'], 'item_path': cfg['item_path'],
        'item_base_class': cfg['item_base_class'], 'actor_class': cfg['actor_class'],
        'ability_class': cfg['ability_class'], 'hud_weapon_word': cfg['hud_weapon_word'],
    }
    for field, expected in expected_weapon_fields.items():
        actual = wb.get_editor_property(field)
        actual = reference_path(actual) if field in ('style_asset', 'item_path', 'item_base_class', 'actor_class', 'ability_class') else str(actual)
        if actual != expected:
            fatal('weapon definition readback mismatch %s: %r != %r' % (field, actual, expected))
    got_aliases = [str(x) for x in wb.get_editor_property('style_aliases')]
    if got_aliases != list(cfg.get('style_aliases', [])):
        fatal('weapon definition readback mismatch style_aliases')
    got_actions = [norm(x) for x in wb.get_editor_property('actions')]
    if got_actions != [r['kind'] for r in cfg['attack_rows']]:
        fatal('weapon definition readback mismatch')
    if bool(wb.get_editor_property('require_exact_rows')) != bool(CAT.get('require_exact_rows', False)):
        fatal('weapon definition readback mismatch require_exact_rows')
    if CAT.get('icon_path') and reference_path(wb.get_editor_property('icon')) != CAT['icon_path']:
        fatal('weapon definition readback mismatch icon')
    expected_build_fields = {
        'build_id': b['build_id'], 'console_name': b['console_name'],
        'display_name': b['display_name'], 'weapon_id': cfg['weapon_id'],
    }
    for field, expected in expected_build_fields.items():
        if str(bb.get_editor_property(field)) != expected:
            fatal('build definition readback mismatch %s' % field)
    if [str(x) for x in bb.get_editor_property('aliases')] != list(b.get('aliases', [])):
        fatal('build definition readback mismatch aliases')
    if int(bb.get_editor_property('ui_order')) != int(b['ui_order']) or int(bb.get_editor_property('legacy_slot')) != -1:
        fatal('build definition readback mismatch ui_order/legacy_slot')
    if CAT.get('icon_path') and reference_path(bb.get_editor_property('icon')) != CAT['icon_path']:
        fatal('build definition readback mismatch icon')
    # the root catalog: append the two soft references
    weapons = list(root.get_editor_property('weapons'))
    builds = list(root.get_editor_property('builds'))
    n_w, n_b = len(weapons), len(builds)
    weapons.append(weapon_asset)
    builds.append(build_asset)
    root.set_editor_property('weapons', weapons)
    root.set_editor_property('builds', builds)
    rw_, rb_ = list(root.get_editor_property('weapons')), list(root.get_editor_property('builds'))
    if len(rw_) != n_w + 1 or len(rb_) != n_b + 1:
        fatal('catalog root readback count mismatch')
    if reference_path(rw_[-1]) != weapon_asset.get_path_name() or reference_path(rb_[-1]) != build_asset.get_path_name():
        fatal('catalog root readback reference mismatch')
    for a_ in (weapon_asset, build_asset, root):
        if not lib.save_loaded_asset(a_):
            fatal('catalog save failed: ' + a_.get_name())
    written += [wpath, bpath, rpath]
    tag('CATALOG_READBACK_OK', {'weapons': [n_w, len(rw_)], 'builds': [n_b, len(rb_)]})
    tag('CATALOG_COMPILE_PENDING', {'surface': 'URPGCombatCatalogSubsystem startup initialization', 'restart_required': True, 'native_compile_run': False})
tag('END', {'written': written, 'dry_run': False})
