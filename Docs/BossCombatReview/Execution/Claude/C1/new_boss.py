# C1 v1 "New Boss" utility (lead, Claude; v0 = cards must exist, v1 = cards with `spec_json` are authored and baked in the same run), run in the UNREAL EDITOR (windowed, needs the level editor for new_level):
#   UnrealEditor.exe <uproject> -ExecutePythonScript="<this file> <config.json> [--dry-run]" -unattended -nosound
# (through Claude/run_editor_script.ps1 -Script "<this file> <config.json>" -NullRhi 0 so the lock, snapshots and the raw log are kept)
#
# What it does, in this order, and stops at the first problem (fail closed, nothing is overwritten):
#   1. reads the config (schema: Antigravity/Reviews/C1_NEW_BOSS_CONFIG_SCHEMA.md), resolves every card from its EXISTING asset
#      <destination_package_dir>/Cards/<move_id> (cards are authored first with Antigravity/MoveCards/author_move_cards.py, baked with bake_blade_path.py),
#   2. runs the pure validator Antigravity/Reviews/validate_boss_config.py (mirrors RPGBossFrameworkProfile.cpp domains and tokens) on the resolved config,
#   3. refuses when the profile or the proof level already exist,
#   4. creates DA_<boss_name>_Profile (every field read back) and the proof level L_<boss_name>FrameworkProof (floor, player start, fixture, nav bounds, light, ProofGameMode),
#   5. saves ONLY those two packages.  --dry-run stops after step 3.
# The engine-side validation of the assets (ResolveProfile) happens when the proof PIE runs: `run_pie.ps1 -Map /Game/.../L_<boss>FrameworkProof ...`.
import copy
import importlib.util
import json
import os
import sys

import unreal

ROOT = 'C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/'
VALIDATOR = ROOT + 'Antigravity/Reviews/validate_boss_config.py'
CARD_TOOLS = ROOT + 'Antigravity/MoveCards/'

# config key -> profile property (snake_case of the C++ field), written with readback
NUMERIC_KEYS = [
    'band_min_cm', 'band_max_cm', 'walk_speed_cm_per_second', 'acceptance_cm', 'walk_timeout_seconds', 'blend_in_seconds', 'blend_out_seconds',
    'capsule_radius_cm', 'capsule_half_height_cm', 'target_health', 'hit_step_cm', 'hit_max_substeps', 'repeat_penalty', 'repeat_memory', 'attack_count',
    'boss_max_health', 'player_hit_damage', 'phase_two_fraction', 'posture_max', 'player_posture_hit_amount', 'stagger_seconds',
    'posture_regen_delay_seconds', 'posture_regen_per_second', 'bleed_buildup_per_hit', 'bleed_initial_threshold', 'bleed_threshold_increase',
    'bleed_threshold_max', 'bleed_hp_fraction',
]


def tag(t, payload):
    unreal.log('[NEWBOSS_%s] %s' % (t, json.dumps(payload, default=str)))


def fatal(msg):
    unreal.log_error('[NEWBOSS_FATAL] ' + msg)
    raise SystemExit(msg)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_validator():
    return load_module('validate_boss_config', VALIDATOR).validate_boss_config


argv = [a for a in sys.argv[1:] if a]
if not argv:
    fatal('usage: new_boss.py <config.json> [--dry-run]')
CONFIG_PATH = argv[0]
DRY = '--dry-run' in argv
with open(CONFIG_PATH, 'r', encoding='utf-8-sig') as f:   # utf-8-sig: PowerShell writes a BOM
    cfg = json.load(f)
BOSS = cfg['boss_name']
DIR = cfg['destination_package_dir']
PROFILE_NAME = 'DA_%s_Profile' % BOSS
LEVEL_NAME = 'L_%sFrameworkProof' % BOSS
PROFILE_PATH = DIR + '/' + PROFILE_NAME
LEVEL_PATH = DIR + '/' + LEVEL_NAME
lib = unreal.EditorAssetLibrary

# ---- 1. resolve the cards: a card with `spec_json` is NEW (its spec comes from the JSON file and is validated BEFORE anything is written), any other card is an EXISTING asset
resolved = copy.deepcopy(cfg)
card_assets = []
new_cards = []          # card dicts to bake + author (entries with spec_json)
for entry in resolved.get('cards', []):
    if entry.get('spec_json'):
        with open(entry['spec_json'], 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        pool = data.get('cards', [data]) if isinstance(data, dict) else data
        match = [c for c in pool if c.get('MoveId') == entry['move_id']]
        if len(match) != 1:
            fatal('spec_json does not contain exactly one card %s: %s' % (entry['move_id'], entry['spec_json']))
        c = match[0]
        entry['spec'] = {k: c.get(k) for k in ('MoveId', 'PhaseId', 'MinRangeCm', 'MaxRangeCm', 'ActiveStartSeconds', 'RecoveryEndSeconds', 'ClipLengthSeconds', 'HPDamage')}
        new_cards.append((entry, c))
        card_assets.append(None)
        continue
    path = DIR + '/Cards/' + entry['move_id']
    asset = unreal.load_asset(path)
    if asset is None:
        fatal('card asset missing (give a spec_json to author it, or author it first): ' + path)
    s_ = asset.get_editor_property('spec')
    seq = s_.get_editor_property('sequence')
    seq = seq.load_synchronous() if hasattr(seq, 'load_synchronous') else seq
    if seq is None:
        fatal('card sequence cannot be loaded: ' + path)
    clip_length = float(seq.get_play_length())   # the clip length is not a card field: it is read from the animation, as author_move_cards.py does
    entry['spec'] = {
        'MoveId': str(s_.get_editor_property('move_id')), 'PhaseId': str(s_.get_editor_property('phase_id')),
        'MinRangeCm': float(s_.get_editor_property('min_range_cm')), 'MaxRangeCm': float(s_.get_editor_property('max_range_cm')),
        'ActiveStartSeconds': float(s_.get_editor_property('active_start_seconds')), 'RecoveryEndSeconds': float(s_.get_editor_property('recovery_end_seconds')),
        'ClipLengthSeconds': clip_length, 'HPDamage': float(s_.get_editor_property('hp_damage')),
    }
    if entry['spec']['MoveId'] != entry['move_id']:
        fatal('card id mismatch for ' + path)
    card_assets.append(asset)
tag('CARDS_RESOLVED', [c['spec'] for c in resolved.get('cards', [])])

# ---- 2. pure validation
existing = {p for p in (PROFILE_PATH, LEVEL_PATH) if lib.does_asset_exist(p)}
for entry, _c in new_cards:
    if lib.does_asset_exist(DIR + '/Cards/' + entry['move_id']):
        fatal('new card already exists, refusing: ' + DIR + '/Cards/' + entry['move_id'])
errors = load_validator()(resolved, existing)
tag('VALIDATION', {'errors': errors})
if errors:
    fatal('config refused: ' + ', '.join(errors))

# ---- 3. destinations
for p in (PROFILE_PATH, LEVEL_PATH):
    if lib.does_asset_exist(p):
        fatal('destination exists, refusing: ' + p)
tag('PREFLIGHT', {'destinations_absent': [PROFILE_PATH, LEVEL_PATH], 'dry_run': DRY})
if DRY:
    tag('END', {'written': [], 'dry_run': True})
    raise SystemExit(0)

# ---- 3b. NEW cards (v1): bake the blade path in the engine, author the assets with the baked samples (read back by the tool), save, gate the bake
if new_cards:
    author = load_module('author_move_cards', CARD_TOOLS + 'author_move_cards.py')
    baker = load_module('bake_blade_path', CARD_TOOLS + 'bake_blade_path.py')
    verifier = load_module('verify_baked_cards', CARD_TOOLS + 'verify_baked_cards.py')
    to_author = []
    for entry, c in new_cards:
        if entry.get('bake', False):
            ok, baked, logs = baker.run_bake(card_data=c, unreal_mod=unreal)
            for line in logs:
                unreal.log(line)
            if not ok:
                fatal('bake failed for ' + entry['move_id'])
            to_author.append(baked)
        else:
            to_author.append(c)
    rc = author.execute_authoring(cards_data=to_author, apply_mode=True, save_mode=True)
    if rc != 0:
        fatal('card authoring failed (code %s)' % rc)
    baked_ids = [e['move_id'] for e, _c in new_cards if e.get('bake', False)]
    if baked_ids:
        ok, logs = verifier.run_verification(unreal_mod=unreal, require_baked_moves=baked_ids, only_move=None)
        for line in logs:
            unreal.log(line)
        if not ok:
            fatal('baked path verification failed (stale or drifting bake)')
    tag('NEW_CARDS', {'authored': [e['move_id'] for e, _c in new_cards], 'baked': baked_ids})
    card_assets = [unreal.load_asset(DIR + '/Cards/' + e['move_id']) if a is None else a for e, a in zip(cfg['cards'], card_assets)]
    if not all(card_assets):
        fatal('a card asset cannot be loaded after authoring')

# ---- 4. the profile
tools = unreal.AssetToolsHelpers.get_asset_tools()
prof = tools.create_asset(PROFILE_NAME, DIR, unreal.RPGBossFrameworkProfile, unreal.DataAssetFactory())
if prof is None:
    fatal('profile create_asset returned None')
mesh = unreal.load_asset(cfg['mesh_path'])
anim_cls = unreal.load_class(None, cfg['anim_class_path'])
target_cls = unreal.load_class(None, cfg['target_pawn_class_path'])
if not (mesh and anim_cls and target_cls):
    fatal('dependency load failed (mesh/anim class/target class)')
prof.set_editor_property('fixture_label', cfg['fixture_label'])
prof.set_editor_property('damage_enabled', bool(cfg['damage_enabled']))
prof.set_editor_property('alignment_authored', bool(cfg['alignment_authored']))
prof.set_editor_property('mesh', mesh)
prof.set_editor_property('anim_class', anim_cls)
prof.set_editor_property('target_pawn_class', target_cls)
if cfg.get('phase_two_id'):
    prof.set_editor_property('phase_two_id', cfg['phase_two_id'])
for k in NUMERIC_KEYS:
    if k in cfg:
        prof.set_editor_property(k, cfg[k])
mt = cfg['mesh_relative_transform']
prof.set_editor_property('mesh_relative_transform', unreal.Transform(location=mt['location'], rotation=unreal.Rotator(roll=mt['rotation'][0], pitch=mt['rotation'][1], yaw=mt['rotation'][2]), scale=mt['scale']))
entries = []
for entry, asset in zip(cfg['cards'], card_assets):
    e = unreal.RPGBossProfileCard()
    e.set_editor_property('card', asset)
    e.set_editor_property('cooldown_seconds', entry['cooldown_seconds'])
    e.set_editor_property('weight', entry['weight'])
    entries.append(e)
prof.set_editor_property('cards', entries)

# readback of everything that was written
back = {}
for k in NUMERIC_KEYS:
    if k in cfg:
        back[k] = prof.get_editor_property(k)
        if abs(float(back[k]) - float(cfg[k])) > 1e-4:
            fatal('readback mismatch %s: %r != %r' % (k, back[k], cfg[k]))
if str(prof.get_editor_property('fixture_label')) != cfg['fixture_label'] or bool(prof.get_editor_property('damage_enabled')) != bool(cfg['damage_enabled']):
    fatal('readback mismatch fixture label / damage flag')
got = list(prof.get_editor_property('cards'))
if len(got) != len(cfg['cards']):
    fatal('cards readback count')
for e, entry in zip(got, cfg['cards']):
    c = e.get_editor_property('card')
    if c is None or c.get_name() != entry['move_id'] or abs(e.get_editor_property('cooldown_seconds') - entry['cooldown_seconds']) > 1e-4:
        fatal('cards readback mismatch ' + entry['move_id'])
for k, want in (('mesh', mesh), ('anim_class', anim_cls), ('target_pawn_class', target_cls)):
    g = prof.get_editor_property(k)
    if g is None or g.get_path_name() != want.get_path_name():
        fatal('readback mismatch ' + k)
if cfg.get('phase_two_id') and str(prof.get_editor_property('phase_two_id')) != cfg['phase_two_id']:
    fatal('readback mismatch phase_two_id')
tag('PROFILE_READBACK', back)
if not lib.save_loaded_asset(prof):
    fatal('profile save failed')

# ---- 5. the proof level
pl = cfg['proof_level']
sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.new_level(LEVEL_PATH):
    fatal('new_level failed')
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
world.get_world_settings().set_editor_property('default_game_mode', unreal.RPGFrameworkProofGameMode)
spawn = unreal.EditorLevelLibrary.spawn_actor_from_class
floor = spawn(unreal.StaticMeshActor, unreal.Vector(250.0, 0.0, -50.0))
floor.set_actor_label('ProofFloor')
floor.set_actor_scale3d(unreal.Vector(40.0, 40.0, 1.0))
floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube.Cube'))
ps = pl['player_start_location']
start = spawn(unreal.PlayerStart, unreal.Vector(ps[0], ps[1], ps[2]))
start.set_actor_label('ProofPlayerStart')
fix = spawn(unreal.RPGFrameworkProofFixture, unreal.Vector(0.0, 0.0, 0.0))
fix.set_actor_label('ProofFixture')
fix.set_editor_property('profile', prof)
fix.set_editor_property('target_start', start)
bs = pl['boss_spawn_location']
fix.set_editor_property('boss_spawn_transform', unreal.Transform(location=list(bs), rotation=unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0), scale=[1.0, 1.0, 1.0]))
fix.set_editor_property('encounter_id', 1)
fix.set_editor_property('generation', 1)
nav = spawn(unreal.NavMeshBoundsVolume, unreal.Vector(250.0, 0.0, 100.0))
nav.set_actor_label('ProofNavBounds')
nav.set_actor_scale3d(unreal.Vector(20.0, 20.0, 5.0))
light = spawn(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, 500.0), unreal.Rotator(roll=0.0, pitch=-50.0, yaw=30.0))
light.set_actor_label('ProofSun')
tag('LEVEL_READBACK', {'game_mode': str(world.get_world_settings().get_editor_property('default_game_mode').get_name()),
                        'fixture_profile': fix.get_editor_property('profile').get_path_name()})
if not unreal.EditorLoadingAndSavingUtils.save_map(world, LEVEL_PATH):
    fatal('save_map failed')
tag('END', {'written': [PROFILE_PATH, LEVEL_PATH]})
