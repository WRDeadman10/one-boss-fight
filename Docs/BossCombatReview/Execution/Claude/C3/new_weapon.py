# C3 v0 "New Weapon" utility, rows part (lead, Claude), run in the UNREAL EDITOR:
#   run_editor_script.ps1 -Script "<this file> <weapon_config.json> [--apply]" -OutDir <absolute dir> -Task <name> -NullRhi 1
# DRY-RUN BY DEFAULT: without --apply nothing is written. What it does:
#   1. reads the config (schema: Antigravity/Reviews/C3_NEW_WEAPON_UTILITY_DESIGN.md), loads the saved /Game/OneBossFight/Data/DA_WeaponAttacks rows,
#   2. runs the pure validator Antigravity/Reviews/validate_weapon_config.py with the REAL existing rows and the engine's does_asset_exist,
#   3. prints the plan (rows to append, or old -> new numbers in update_existing_style mode),
#   4. with --apply: appends the rows (mode new_weapon) or edits them in place (update_existing_style), reads EVERY row back, saves ONLY DA_WeaponAttacks.
# The pack parts of a weapon (combat style asset, item, actor Blueprint, ability, montages) are NOT created here: they must exist (the validator checks the paths).
# The catalog entry (RPGCombatCatalog) is not written by this version.
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


def kind_enum(name):
    out = ''.join('_' + c if c.isupper() and i else c for i, c in enumerate(name)).upper()
    return getattr(unreal.RPGAttackKind, out)


argv = [a for a in sys.argv[1:] if a]
if not argv:
    fatal('usage: new_weapon.py <weapon_config.json> [--apply]')
APPLY = '--apply' in argv
with open(argv[0], 'r', encoding='utf-8-sig') as f:
    cfg = json.load(f)
STYLE = cfg['style_name']
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

plan = []
for r in cfg['attack_rows']:
    plan.append({'style': STYLE, 'kind': r['kind'], 'mode': MODE, **{k: r.get(k) for k, _p in FIELDS}})
tag('PLAN', plan)
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
tag('END', {'written': [TABLE], 'dry_run': False})
