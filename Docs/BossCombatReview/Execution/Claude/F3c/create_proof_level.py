# F3c part 2 (lead, Claude): the level only, with a log tag BEFORE every step so a crash names its step. Refuses if the map exists.
# Card and profile were saved by create_framework_proof.py (run1_save); this script re-reads them and never rewrites them.
import json
import sys
import unreal

DIR = '/Game/OneBossFight/FrameworkProof'
PROFILE_PATH = DIR + '/DA_Sevarog_SwingProof'
LEVEL_PATH = DIR + '/L_SevarogFrameworkProof'
CAPSULE_HALF_HEIGHT = 165.0
BOSS_SPAWN = unreal.Vector(500.0, 0.0, CAPSULE_HALF_HEIGHT + 5.0)
SKIP = [s for s in sys.argv if s.startswith('--skip=')]
SKIP = SKIP[0].split('=', 1)[1].split(',') if SKIP else []


def tag(t, payload):
    unreal.log('[F3C_%s] %s' % (t, json.dumps(payload, default=str)))


def step(name):
    tag('STEP', name)


def fatal(msg):
    unreal.log_error('[F3C_FATAL] ' + msg)
    raise SystemExit(msg)


lib = unreal.EditorAssetLibrary
if lib.does_asset_exist(LEVEL_PATH):
    fatal('destination exists, refusing: ' + LEVEL_PATH)
prof = unreal.load_asset(PROFILE_PATH)
if prof is None:
    fatal('profile missing')
# 3. level
step('sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsyste')
sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.new_level(LEVEL_PATH):
    fatal('new_level failed')
step('world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsy')
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
step('world.get_world_settings().set_editor_propert')
world.get_world_settings().set_editor_property('default_game_mode', unreal.RPGFrameworkProofGameMode)
spawn = unreal.EditorLevelLibrary.spawn_actor_from_class
step('floor = spawn(unreal.StaticMeshActor, unreal.Vector(250.0, 0')
floor = spawn(unreal.StaticMeshActor, unreal.Vector(250.0, 0.0, -50.0))
floor.set_actor_label('ProofFloor')
step('floor.set_actor_scale3d')
floor.set_actor_scale3d(unreal.Vector(40.0, 40.0, 1.0))
step('floor.static_mesh_component.set_static_mesh(unreal.load_asse')
floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube.Cube'))
step('start = spawn(unreal.PlayerStart, unreal.Vector(0.0, 0.0, 10')
start = spawn(unreal.PlayerStart, unreal.Vector(0.0, 0.0, 100.0))
start.set_actor_label('ProofPlayerStart')
step('fix = spawn(unreal.RPGFrameworkProofFixture, unreal.Vector(0')
fix = spawn(unreal.RPGFrameworkProofFixture, unreal.Vector(0.0, 0.0, 0.0))
fix.set_actor_label('ProofFixture')
step("fix.set_editor_property('profile'")
fix.set_editor_property('profile', prof)
fix.set_editor_property('target_start', start)
step("fix.set_editor_property('boss_spawn_transform")
fix.set_editor_property('boss_spawn_transform', unreal.Transform(location=[BOSS_SPAWN.x, BOSS_SPAWN.y, BOSS_SPAWN.z], rotation=unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0), scale=[1.0, 1.0, 1.0]))
fix.set_editor_property('encounter_id', 1)
fix.set_editor_property('generation', 1)
step('nav = spawn(unreal.NavMeshBoundsVolume, unreal.Vector(250.0,')
nav = spawn(unreal.NavMeshBoundsVolume, unreal.Vector(250.0, 0.0, 100.0))
nav.set_actor_label('ProofNavBounds')
step('nav.set_actor_scale3d')
nav.set_actor_scale3d(unreal.Vector(20.0, 20.0, 5.0))  # brush 200 cm: 4000 x 4000 x 1000 cm
step('light = spawn(unreal.DirectionalLight, unreal.Vector(0.0, 0.')
light = spawn(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, 500.0), unreal.Rotator(roll=0.0, pitch=-50.0, yaw=30.0))
light.set_actor_label('ProofSun')
tag('LEVEL_READBACK', {
    'game_mode': str(world.get_world_settings().get_editor_property('default_game_mode').get_name()),
    'fixture_profile': fix.get_editor_property('profile').get_path_name(),
    'fixture_target_start_is_start': fix.get_editor_property('target_start') == start,
    'encounter': fix.get_editor_property('encounter_id'), 'generation': fix.get_editor_property('generation'),
    'actors': [a.get_actor_label() for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label().startswith('Proof')]})
step('if not unreal.EditorLoadingAndSavingUtils.save_map(world, LE')
if not unreal.EditorLoadingAndSavingUtils.save_map(world, LEVEL_PATH):
    fatal('save_map failed')
tag('END', {'mode': 'save', 'written': [CARD_PATH, PROFILE_PATH, LEVEL_PATH]})
