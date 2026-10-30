# F4 authoring (lead, Claude): NEW assets only, refuses if any destination exists, reads values back, saves only the named packages. Windowed editor.
#   /Game/OneBossFight/FrameworkProof/Cards/Move_Sevarog_SwingSlow_F4  (author_move_cards.py, HPDamage 35 = design value, proposed)
#   /Game/OneBossFight/FrameworkProof/DA_Sevarog_SwingProof_F4          (label "F4 fixture", damage enabled)
#   /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF4         (floor, PlayerStart, fixture, nav bounds, light)
import importlib.util
import json
import unreal

ROOT = 'C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/'
TOOL = ROOT + 'Antigravity/MoveCards/author_move_cards.py'
CARDS_JSON = ROOT + 'Claude/F4/move_card_f4_swingslow.json'
MOVE_ID = 'Move_Sevarog_SwingSlow_F4'
DIR = '/Game/OneBossFight/FrameworkProof'
CARD_PATH = DIR + '/Cards/' + MOVE_ID
PROFILE_NAME = 'DA_Sevarog_SwingProof_F4'
PROFILE_PATH = DIR + '/' + PROFILE_NAME
LEVEL_PATH = DIR + '/L_SevarogFrameworkProofF4'
CAPSULE_RADIUS, CAPSULE_HALF_HEIGHT = 60.0, 165.0
# Band 150..180 cm: the measured blade reaches 150 cm forward at 0.475..0.49 s (F3d), so the player stands inside the swing. Design values.
BAND = (150.0, 180.0)
BOSS_SPAWN = (500.0, 0.0, CAPSULE_HALF_HEIGHT + 5.0)


def tag(t, payload):
    unreal.log('[F4C_%s] %s' % (t, json.dumps(payload, default=str)))


def fatal(msg):
    unreal.log_error('[F4C_FATAL] ' + msg)
    raise SystemExit(msg)


lib = unreal.EditorAssetLibrary
for p in (CARD_PATH, PROFILE_PATH, LEVEL_PATH):
    if lib.does_asset_exist(p):
        fatal('destination exists, refusing: ' + p)
tag('PREFLIGHT', {'destinations_absent': [CARD_PATH, PROFILE_PATH, LEVEL_PATH]})

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

tools = unreal.AssetToolsHelpers.get_asset_tools()
prof = tools.create_asset(PROFILE_NAME, DIR, unreal.RPGBossFrameworkProfile, unreal.DataAssetFactory())
if prof is None:
    fatal('profile create_asset returned None')
mesh = unreal.load_asset('/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog.Sevarog')
anim_cls = unreal.load_class(None, '/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sevarog_AnimBlueprint.Sevarog_AnimBlueprint_C')
target_cls = unreal.load_class(None, '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C')
if not (mesh and anim_cls and target_cls and card):
    fatal('dependency load failed')
numbers = {
    'band_min_cm': BAND[0], 'band_max_cm': BAND[1], 'walk_speed_cm_per_second': 180.0, 'acceptance_cm': 5.0,
    'walk_timeout_seconds': 10.0, 'blend_in_seconds': 0.1, 'blend_out_seconds': 0.04,
    'capsule_radius_cm': CAPSULE_RADIUS, 'capsule_half_height_cm': CAPSULE_HALF_HEIGHT, 'target_health': 800.0,
    'hit_step_cm': 15.0, 'hit_max_substeps': 8,
}
prof.set_editor_property('fixture_label', 'F4 fixture')
prof.set_editor_property('damage_enabled', True)
prof.set_editor_property('alignment_authored', True)
for k, v in numbers.items():
    prof.set_editor_property(k, v)
prof.set_editor_property('mesh', mesh)
prof.set_editor_property('anim_class', anim_cls)
prof.set_editor_property('target_pawn_class', target_cls)
prof.set_editor_property('card', card)
prof.set_editor_property('mesh_relative_transform', unreal.Transform(location=[0.0, 0.0, -CAPSULE_HALF_HEIGHT], rotation=unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0), scale=[1.0, 1.0, 1.0]))
back = {'fixture_label': prof.get_editor_property('fixture_label'), 'damage_enabled': prof.get_editor_property('damage_enabled')}
for k, v in numbers.items():
    back[k] = prof.get_editor_property(k)
    if abs(float(back[k]) - float(v)) > 1e-4:
        fatal('readback mismatch %s: %r != %r' % (k, back[k], v))
if back['fixture_label'] != 'F4 fixture' or back['damage_enabled'] is not True:
    fatal('readback mismatch label/flag')
for k, want in (('mesh', mesh), ('card', card), ('anim_class', anim_cls), ('target_pawn_class', target_cls)):
    got = prof.get_editor_property(k)
    if got is None or got.get_path_name() != want.get_path_name():
        fatal('readback mismatch ' + k)
tag('PROFILE_READBACK', back)
if not lib.save_loaded_asset(prof):
    fatal('profile save failed')

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
fix.set_editor_property('boss_spawn_transform', unreal.Transform(location=list(BOSS_SPAWN), rotation=unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0), scale=[1.0, 1.0, 1.0]))
fix.set_editor_property('encounter_id', 1)
fix.set_editor_property('generation', 1)
nav = spawn(unreal.NavMeshBoundsVolume, unreal.Vector(250.0, 0.0, 100.0))
nav.set_actor_label('ProofNavBounds')
nav.set_actor_scale3d(unreal.Vector(20.0, 20.0, 5.0))
light = spawn(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, 500.0), unreal.Rotator(roll=0.0, pitch=-50.0, yaw=30.0))
light.set_actor_label('ProofSun')
tag('LEVEL_READBACK', {
    'game_mode': str(world.get_world_settings().get_editor_property('default_game_mode').get_name()),
    'fixture_profile': fix.get_editor_property('profile').get_path_name(),
    'encounter': fix.get_editor_property('encounter_id'), 'generation': fix.get_editor_property('generation')})
if not unreal.EditorLoadingAndSavingUtils.save_map(world, LEVEL_PATH):
    fatal('save_map failed')
tag('END', {'written': [CARD_PATH, PROFILE_PATH, LEVEL_PATH]})
