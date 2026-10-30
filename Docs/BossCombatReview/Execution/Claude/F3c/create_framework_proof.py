# F3c authoring (lead, Claude): creates ONLY new assets, refuses if any destination exists, reads every value back, saves only the named packages.
#   1. /Game/OneBossFight/FrameworkProof/Cards/Move_Sevarog_SwingSlow  (via Antigravity author_move_cards.py, F3 telemetry JSON, HPDamage 0)
#   2. /Game/OneBossFight/FrameworkProof/DA_Sevarog_SwingProof          (URPGBossFrameworkProfile, label "F3 fixture")
#   3. /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProof        (new level: floor, PlayerStart, fixture, nav bounds, light)
# Mode: --dry (default, only checks and prints) | --save (writes). Synchronous script, run with -ExecutePythonScript. Tags: [F3C_*].
import importlib.util
import json
import sys
import unreal

ROOT = 'C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/'
TOOL = ROOT + 'Antigravity/MoveCards/author_move_cards.py'
CARDS_JSON = ROOT + 'Antigravity/MoveCards/move_cards_f3_telemetry.json'
MOVE_ID = 'Move_Sevarog_SwingSlow'
DIR = '/Game/OneBossFight/FrameworkProof'
CARD_PATH = DIR + '/Cards/' + MOVE_ID
PROFILE_NAME = 'DA_Sevarog_SwingProof'
PROFILE_PATH = DIR + '/' + PROFILE_NAME
LEVEL_PATH = DIR + '/L_SevarogFrameworkProof'
SAVE = '--save' in sys.argv

# Design values (OUR fixture values, not measured combat data; capsule from the F3b mesh bounds, mesh z 14.7..325.8 cm above the root).
CAPSULE_RADIUS, CAPSULE_HALF_HEIGHT = 60.0, 165.0
BAND = (250.0, 350.0)
BOSS_SPAWN = unreal.Vector(500.0, 0.0, CAPSULE_HALF_HEIGHT + 5.0)


def tag(t, payload):
    unreal.log('[F3C_%s] %s' % (t, json.dumps(payload, default=str)))


def fatal(msg):
    unreal.log_error('[F3C_FATAL] ' + msg)
    raise SystemExit(msg)


lib = unreal.EditorAssetLibrary
for p in (CARD_PATH, PROFILE_PATH, LEVEL_PATH):
    if lib.does_asset_exist(p):
        fatal('destination exists, refusing: ' + p)
tag('PREFLIGHT', {'destinations_absent': [CARD_PATH, PROFILE_PATH, LEVEL_PATH], 'save': SAVE})
if not SAVE:
    tag('END', {'mode': 'dry', 'written': 0})
    raise SystemExit(0)

# 1. card through the reviewed helper
spec = importlib.util.spec_from_file_location('author_move_cards', TOOL)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
with open(CARDS_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)
if data.get('synthetic') is True:
    fatal('card JSON is synthetic')
rc = tool.execute_authoring(cards_data=data['cards'], apply_mode=True, save_mode=True, only_move_id=MOVE_ID)
tag('CARD_RC', {'rc': rc})
if rc != 0 or not lib.does_asset_exist(CARD_PATH):
    fatal('card authoring failed')
card = unreal.load_asset(CARD_PATH)

# 2. profile
tools = unreal.AssetToolsHelpers.get_asset_tools()
prof = tools.create_asset(PROFILE_NAME, DIR, unreal.RPGBossFrameworkProfile, unreal.DataAssetFactory())
if prof is None:
    fatal('profile create_asset returned None')
mesh = unreal.load_asset('/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog.Sevarog')
anim_cls = unreal.load_class(None, '/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sevarog_AnimBlueprint.Sevarog_AnimBlueprint_C')
target_cls = unreal.load_class(None, '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C')
if not (mesh and anim_cls and target_cls and card):
    fatal('dependency load failed')
values = {
    'fixture_label': 'F3 fixture', 'mesh': mesh, 'anim_class': anim_cls, 'target_pawn_class': target_cls, 'card': card,
    'band_min_cm': BAND[0], 'band_max_cm': BAND[1], 'walk_speed_cm_per_second': 180.0, 'acceptance_cm': 5.0,
    'walk_timeout_seconds': 10.0, 'blend_in_seconds': 0.1, 'blend_out_seconds': 0.1,
    'capsule_radius_cm': CAPSULE_RADIUS, 'capsule_half_height_cm': CAPSULE_HALF_HEIGHT,
    'mesh_relative_transform': unreal.Transform(location=[0.0, 0.0, -CAPSULE_HALF_HEIGHT], rotation=unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0), scale=[1.0, 1.0, 1.0]),
    'alignment_authored': True,
}
for k, v in values.items():
    prof.set_editor_property(k, v)
back = {}
for k in ('fixture_label', 'band_min_cm', 'band_max_cm', 'walk_speed_cm_per_second', 'acceptance_cm', 'walk_timeout_seconds',
          'blend_in_seconds', 'blend_out_seconds', 'capsule_radius_cm', 'capsule_half_height_cm', 'alignment_authored'):
    back[k] = prof.get_editor_property(k)
    if back[k] != values[k] and not (isinstance(values[k], float) and abs(back[k] - values[k]) < 1e-4):
        fatal('readback mismatch %s: %r != %r' % (k, back[k], values[k]))
for k, want in (('mesh', mesh), ('card', card)):
    got = prof.get_editor_property(k)
    if got is None or got.get_path_name() != want.get_path_name():
        fatal('readback mismatch ' + k)
for k, want in (('anim_class', anim_cls), ('target_pawn_class', target_cls)):
    got = prof.get_editor_property(k)
    if got is None or got.get_path_name() != want.get_path_name():
        fatal('readback mismatch ' + k)
tag('PROFILE_READBACK', back)
if not lib.save_loaded_asset(prof):
    fatal('profile save failed')

# 3. level
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
start = spawn(unreal.PlayerStart, unreal.Vector(0.0, 0.0, 100.0))
start.set_actor_label('ProofPlayerStart')
fix = spawn(unreal.RPGFrameworkProofFixture, unreal.Vector(0.0, 0.0, 0.0))
fix.set_actor_label('ProofFixture')
fix.set_editor_property('profile', prof)
fix.set_editor_property('target_start', start)
fix.set_editor_property('boss_spawn_transform', unreal.Transform(location=[BOSS_SPAWN.x, BOSS_SPAWN.y, BOSS_SPAWN.z], rotation=unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0), scale=[1.0, 1.0, 1.0]))
fix.set_editor_property('encounter_id', 1)
fix.set_editor_property('generation', 1)
nav = spawn(unreal.NavMeshBoundsVolume, unreal.Vector(250.0, 0.0, 100.0))
nav.set_actor_label('ProofNavBounds')
nav.set_actor_scale3d(unreal.Vector(20.0, 20.0, 5.0))  # brush 200 cm: 4000 x 4000 x 1000 cm
light = spawn(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, 500.0), unreal.Rotator(roll=0.0, pitch=-50.0, yaw=30.0))
light.set_actor_label('ProofSun')
tag('LEVEL_READBACK', {
    'game_mode': str(world.get_world_settings().get_editor_property('default_game_mode').get_name()),
    'fixture_profile': fix.get_editor_property('profile').get_path_name(),
    'fixture_target_start_is_start': fix.get_editor_property('target_start') == start,
    'encounter': fix.get_editor_property('encounter_id'), 'generation': fix.get_editor_property('generation'),
    'actors': [a.get_actor_label() for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label().startswith('Proof')]})
if not unreal.EditorLoadingAndSavingUtils.save_map(world, LEVEL_PATH):
    fatal('save_map failed')
tag('END', {'mode': 'save', 'written': [CARD_PATH, PROFILE_PATH, LEVEL_PATH]})
