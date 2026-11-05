import unreal

DIR = '/Game/OneBossFight/FrameworkProof'
CARD_DIR = DIR + '/Cards'
PROFILE_BASE = DIR + '/DA_Sevarog_RangeBands_MOV001'
CARD_BASE = CARD_DIR + '/Move_Sevarog_HeavySlam_F7'
LEVEL_BASE = DIR + '/L_SevarogFrameworkProofMOV001_R150'
LEVELS = {
    'Melee100': (100.0, 380.0),
    'Close250': (250.0, 220.0),
    'Medium375': (375.0, 100.0),
    'Gap700': (700.0, -220.0),
}
BOSS_X = 580.0
MIN_APPROACH_CLEARANCE_CM = 80.0
# Existing source maps R150/R300/R700 are immutable; destinations are unique proof copies.
PROFILE_BASE_FAG5 = DIR + '/DA_Sevarog_RangePartition_FAG5'
CARDS = {
    'Melee': (CARD_DIR + '/Move_Sevarog_Melee_FAG5', 0.0, 220.0),
    'Close': (CARD_DIR + '/Move_Sevarog_Close_FAG5', 150.0, 350.0),
}

lib = unreal.EditorAssetLibrary

def checked(obj, name, value, predicate):
    obj.set_editor_property(name, value)
    actual = obj.get_editor_property(name)
    assert predicate(actual), 'readback failed: %s' % name
    return actual

def absent(path):
    assert not lib.does_asset_exist(path), 'destination exists; refusing overwrite: ' + path

for path in [PROFILE_BASE_FAG5 + '_' + n for n in LEVELS] + [v[0] for v in CARDS.values()] + [DIR + '/L_SevarogFrameworkProofFAG5_' + n for n in LEVELS]:
    absent(path)

source_card = unreal.load_asset(CARD_BASE)
assert source_card is not None
for family, (dst, lo, hi) in CARDS.items():
    assert lib.duplicate_asset(CARD_BASE, dst), 'card duplicate failed: ' + dst
    card = unreal.load_asset(dst)
    assert card is not None
    spec = card.get_editor_property('spec')
    checked(spec, 'move_id', 'Move_Sevarog_%s_FAG5' % family, lambda x: str(x) == 'Move_Sevarog_%s_FAG5' % family)
    checked(spec, 'min_range_cm', lo, lambda x: abs(float(x) - lo) <= 1e-4)
    checked(spec, 'max_range_cm', hi, lambda x: abs(float(x) - hi) <= 1e-4)
    checked(card, 'spec', spec, lambda x: str(x.get_editor_property('move_id')) == 'Move_Sevarog_%s_FAG5' % family)
    assert lib.save_loaded_asset(card), 'card save failed: ' + dst

base = unreal.load_asset(PROFILE_BASE)
assert base is not None
base_cards = list(base.get_editor_property('cards'))
assert len(base_cards) == 4, 'unexpected base card count'
base_move_ids = []
for entry in base_cards:
    card = entry.get_editor_property('card')
    assert card is not None, 'base profile contains a missing card'
    move_id = str(card.get_editor_property('spec').get_editor_property('move_id'))
    assert move_id, 'base card has empty MoveId'
    base_move_ids.append(move_id)
new_entries = base_cards[:]
for family, (path, _lo, _hi) in CARDS.items():
    asset = unreal.load_asset(path)
    assert asset is not None
    entry = unreal.RPGBossProfileCard()
    checked(entry, 'card', asset, lambda x: x is not None and x.get_path_name() == asset.get_path_name())
    checked(entry, 'cooldown_seconds', 0.1, lambda x: abs(float(x) - 0.1) <= 1e-4)
    checked(entry, 'weight', 1.0, lambda x: abs(float(x) - 1.0) <= 1e-4)
    new_entries.append(entry)
all_move_ids = base_move_ids + ['Move_Sevarog_%s_FAG5' % family for family in CARDS]
assert len(all_move_ids) == len(set(all_move_ids)), 'duplicate MoveId in four base plus two FAG5 cards: %s' % all_move_ids

def make_level(level_path, profile, player_x):
    band_max = float(profile.get_editor_property('band_max_cm'))
    start_distance = abs(BOSS_X - player_x)
    assert start_distance - band_max >= MIN_APPROACH_CLEARANCE_CM, 'boss must start at least 80 cm outside the band: %s distance=%s max=%s' % (level_path, start_distance, band_max)
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert subsystem.new_level(level_path), 'new_level failed: ' + level_path
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert world is not None, 'editor world missing after new_level'
    world.get_world_settings().set_editor_property('default_game_mode', unreal.RPGFrameworkProofGameMode)
    spawn = unreal.EditorLevelLibrary.spawn_actor_from_class
    floor = spawn(unreal.StaticMeshActor, unreal.Vector(250.0, 0.0, -50.0))
    assert floor is not None
    floor.set_actor_label('ProofFloor')
    floor.set_actor_scale3d(unreal.Vector(40.0, 40.0, 1.0))
    floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube.Cube'))
    start = spawn(unreal.PlayerStart, unreal.Vector(player_x, 0.0, 100.0))
    assert start is not None
    start.set_actor_label('ProofPlayerStart')
    assert abs(float(start.get_actor_location().x) - player_x) <= 1e-3, 'PlayerStart location readback failed'
    fix = spawn(unreal.RPGFrameworkProofFixture, unreal.Vector(0.0, 0.0, 0.0))
    assert fix is not None
    fix.set_actor_label('ProofFixture')
    checked(fix, 'profile', profile, lambda x: x is not None and x.get_path_name() == profile.get_path_name())
    checked(fix, 'target_start', start, lambda x: x is not None and x.get_path_name() == start.get_path_name())
    checked(fix, 'boss_spawn_transform', unreal.Transform(location=[BOSS_X, 0.0, 170.0], rotation=unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0), scale=[1.0, 1.0, 1.0]), lambda x: abs(float(x.translation.x) - BOSS_X) <= 1e-3)
    checked(fix, 'encounter_id', 1, lambda x: int(x) == 1)
    checked(fix, 'generation', 1, lambda x: int(x) == 1)
    nav = spawn(unreal.NavMeshBoundsVolume, unreal.Vector(250.0, 0.0, 100.0))
    assert nav is not None
    nav.set_actor_label('ProofNavBounds')
    nav.set_actor_scale3d(unreal.Vector(20.0, 20.0, 5.0))
    light = spawn(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, 500.0), unreal.Rotator(roll=0.0, pitch=-50.0, yaw=30.0))
    assert light is not None
    light.set_actor_label('ProofSun')
    assert unreal.EditorLoadingAndSavingUtils.save_map(world, level_path), 'save_map failed: ' + level_path
    back = unreal.load_asset(level_path)
    assert back is not None, 'saved map asset did not read back: ' + level_path
    unreal.log('[FAG5_MOV001] map_created=%s profile=%s player_x=%s' % (level_path, profile.get_path_name(), player_x))

for name, (range_cm, target_x) in LEVELS.items():
    expected_band_max = range_cm + 10.0
    initial_distance = abs(BOSS_X - target_x)
    assert initial_distance - expected_band_max >= MIN_APPROACH_CLEARANCE_CM, 'invalid approach clearance for %s: %s cm' % (name, initial_distance - expected_band_max)
    profile_path = PROFILE_BASE_FAG5 + '_' + name
    assert lib.duplicate_asset(PROFILE_BASE, profile_path), 'profile duplicate failed: ' + profile_path
    profile = unreal.load_asset(profile_path)
    assert profile is not None
    checked(profile, 'band_min_cm', range_cm - 10.0, lambda x: abs(float(x) - (range_cm - 10.0)) <= 1e-4)
    checked(profile, 'band_max_cm', range_cm + 10.0, lambda x: abs(float(x) - (range_cm + 10.0)) <= 1e-4)
    checked(profile, 'cards', new_entries, lambda x: len(x) == 6 and all(e.get_editor_property('card') is not None for e in x))
    checked(profile, 'range_band_partition', True, lambda x: bool(x))
    assert lib.save_loaded_asset(profile), 'profile save failed: ' + profile_path
    dst = DIR + '/L_SevarogFrameworkProofFAG5_' + name
    make_level(dst, profile, target_x)
