"""Create a fresh framework proof profile/map with distinct outcome edges for COM-004."""
import unreal

DIR = '/Game/OneBossFight/FrameworkProof'
PROFILE_SRC = DIR + '/DA_Sevarog_Combo3Proof_COM3'
# Lead edit 2026-11-04: _FAG23b names; a failed first attempt left DA_Sevarog_ComboOutcome_FAG23 and an empty
# L_SevarogFrameworkProofComboOutcomeFAG23 behind (unreferenced, not deleted; cleanup needs the owner's approval).
# _FAG23c (4 attacks) proved the Guarded gate (Continue next=D) but ended before step D; _FAG23d raises the attack budget.
PROFILE_DST = DIR + '/DA_Sevarog_ComboOutcome_FAG23d'
LEVEL_DST = DIR + '/L_SevarogFrameworkProofComboOutcomeFAG23d'
ATTACK_COUNT = 8   # profile maximum; with cooldown 0.0 on every card the phase pool cannot starve (PhasePoolCannotStarve)
PLAYER_X = 0.0
BOSS_X = 500.0
MIN_APPROACH_CLEARANCE_CM = 80.0
CARDS = {
    'Hit': 'Move_Sevarog_SwingSlow_F7',
    'Whiff': 'Move_Sevarog_SwingSlow_F7',
    'Guarded': 'Move_Sevarog_HeavySlam_F7',
    'Parried': 'Move_Sevarog_HeavySlam_F7',
}
lib = unreal.EditorAssetLibrary
for path in (PROFILE_DST, LEVEL_DST):
    assert not lib.does_asset_exist(path), 'destination exists; refusing overwrite: ' + path
assert lib.does_asset_exist(PROFILE_SRC), 'source COM3 profile is missing'
assert lib.duplicate_asset(PROFILE_SRC, PROFILE_DST), 'profile duplicate failed'
profile = unreal.load_asset(PROFILE_DST)
assert profile is not None
profile_cards = list(profile.get_editor_property('cards'))
card_move_ids = []
for entry in profile_cards:
    card = entry.get_editor_property('card')
    assert card is not None, 'profile contains an unresolved card'
    move_id = str(card.get_editor_property('spec').get_editor_property('move_id'))
    assert move_id, 'profile contains an empty MoveId'
    card_move_ids.append(move_id)
assert len(card_move_ids) == len(set(card_move_ids)), 'profile card MoveIds must be distinct: %s' % card_move_ids
for entry in profile_cards:
    entry.set_editor_property('cooldown_seconds', 0.0)
profile.set_editor_property('cards', profile_cards)
assert all(abs(float(e.get_editor_property('cooldown_seconds'))) < 1e-6 for e in profile.get_editor_property('cards')), 'cooldown readback failed'
profile.set_editor_property('attack_count', ATTACK_COUNT)
assert int(profile.get_editor_property('attack_count')) == ATTACK_COUNT, 'attack_count readback failed'
band_max = float(profile.get_editor_property('band_max_cm'))
assert abs(BOSS_X - PLAYER_X) - band_max >= MIN_APPROACH_CLEARANCE_CM, 'boss spawn starts inside or too close to profile band'

def edge(to_node, outcome):
    value = unreal.RPGBossComboEdgeData()
    value.set_editor_property('to_node', to_node)
    assert str(value.get_editor_property('to_node')) == to_node
    value.set_editor_property('min_range_cm', 0.0)
    assert abs(float(value.get_editor_property('min_range_cm'))) < 1e-4
    value.set_editor_property('max_range_cm', 400.0)
    assert abs(float(value.get_editor_property('max_range_cm')) - 400.0) < 1e-4
    value.set_editor_property('max_abs_yaw_degrees', 180.0)
    assert abs(float(value.get_editor_property('max_abs_yaw_degrees')) - 180.0) < 1e-4
    value.set_editor_property('any_outcome', False)
    assert not bool(value.get_editor_property('any_outcome'))
    # Lead edit: set the UE Python enum by member name and compare .value (no int() conversion of an EnumBase).
    # UE Python drops the E prefix of UENUM names: ERPGBossComboOutcome -> unreal.RPGBossComboOutcome.
    member = getattr(unreal.RPGBossComboOutcome, ('HIT', 'WHIFF', 'GUARDED', 'PARRIED')[outcome])
    value.set_editor_property('outcome', member)
    assert value.get_editor_property('outcome').value == outcome
    return value

def node(node_id, move_id, edges):
    value = unreal.RPGBossComboNodeData()
    value.set_editor_property('node_id', node_id)
    assert str(value.get_editor_property('node_id')) == node_id
    value.set_editor_property('move_id', move_id)
    assert str(value.get_editor_property('move_id')) == move_id
    value.set_editor_property('edges', edges)
    assert len(value.get_editor_property('edges')) == len(edges)
    return value

nodes = [
    node('A', 'Move_Sevarog_SwingSlow_F7', [
        edge('B', 0),  # Hit control
        edge('C', 1),  # Whiff control
        edge('D', 2),  # Guarded distinct follow-up
        edge('E', 3),  # Parried distinct follow-up
    ]),
    node('B', CARDS['Hit'], []),
    node('C', CARDS['Whiff'], []),
    node('D', CARDS['Guarded'], []),
    node('E', CARDS['Parried'], []),
]
profile.set_editor_property('combo_nodes', nodes)
actual = list(profile.get_editor_property('combo_nodes'))
assert [str(n.get_editor_property('node_id')) for n in actual] == ['A', 'B', 'C', 'D', 'E']
assert all(str(n.get_editor_property('move_id')) in card_move_ids for n in actual), 'combo graph references a MoveId absent from its profile cards'
root = profile.get_editor_property('combo_nodes')[0]
assert [str(e.get_editor_property('to_node')) for e in root.get_editor_property('edges')] == ['B', 'C', 'D', 'E']
assert [e.get_editor_property('outcome').value for e in root.get_editor_property('edges')] == [0, 1, 2, 3]
assert str(profile.get_editor_property('combo_root')) == 'A'
assert lib.save_loaded_asset(profile), 'profile save failed'

subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert subsystem.new_level(LEVEL_DST), 'new_level failed'
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world is not None
world.get_world_settings().set_editor_property('default_game_mode', unreal.RPGFrameworkProofGameMode)
assert 'RPGFrameworkProofGameMode' in world.get_world_settings().get_editor_property('default_game_mode').get_name()
spawn = unreal.EditorLevelLibrary.spawn_actor_from_class
floor = spawn(unreal.StaticMeshActor, unreal.Vector(250.0, 0.0, -50.0))
assert floor is not None
floor.set_actor_label('ProofFloor')
floor.set_actor_scale3d(unreal.Vector(40.0, 40.0, 1.0))
floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube.Cube'))
start = spawn(unreal.PlayerStart, unreal.Vector(PLAYER_X, 0.0, 100.0))
assert start is not None
start.set_actor_label('ProofPlayerStart')
assert abs(float(start.get_actor_location().x) - PLAYER_X) <= 1e-3
fixture = spawn(unreal.RPGFrameworkProofFixture, unreal.Vector(0.0, 0.0, 0.0))
assert fixture is not None
fixture.set_actor_label('ProofFixture')
fixture.set_editor_property('profile', profile)
assert fixture.get_editor_property('profile').get_path_name().split('.')[0] == PROFILE_DST  # object path is <package>.<name>
fixture.set_editor_property('target_start', start)
assert fixture.get_editor_property('target_start').get_path_name() == start.get_path_name()
fixture.set_editor_property('boss_spawn_transform', unreal.Transform(location=[BOSS_X, 0.0, 170.0], rotation=unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0), scale=[1.0, 1.0, 1.0]))
assert abs(float(fixture.get_editor_property('boss_spawn_transform').translation.x) - BOSS_X) < 1e-3
fixture.set_editor_property('encounter_id', 1)
assert int(fixture.get_editor_property('encounter_id')) == 1
fixture.set_editor_property('generation', 1)
assert int(fixture.get_editor_property('generation')) == 1
nav = spawn(unreal.NavMeshBoundsVolume, unreal.Vector(250.0, 0.0, 100.0))
assert nav is not None
nav.set_actor_label('ProofNavBounds')
nav.set_actor_scale3d(unreal.Vector(20.0, 20.0, 5.0))
light = spawn(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, 500.0), unreal.Rotator(roll=0.0, pitch=-50.0, yaw=30.0))
assert light is not None
light.set_actor_label('ProofSun')
assert unreal.EditorLoadingAndSavingUtils.save_map(world, LEVEL_DST), 'save_map failed'
assert lib.does_asset_exist(LEVEL_DST), 'saved map not found'  # no map load inside a script
unreal.log('[FAG23_COM004] profile=%s map=%s outcomes=Hit:B,Whiff:C,Guarded:D,Parried:E' % (PROFILE_DST, LEVEL_DST))
