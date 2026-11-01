# REPOSITION proof (lead, Claude; opt-in RepositionMax, rows MOV-002/003/005 partly): the same two cards and numbers as the combo proof, NO combo graph, reposition_max 3: when the target leaves the band the boss walks back and decides again. NEW profile and map only.
# (kept from the combo proof) COMBO proof (lead, Claude; BOSS-COM-001/003/005/006/007): two cards of phase one, the combo graph SwingSlow -> HeavySlam (any outcome, range 0..400 cm, yaw 90 deg), no phase two, no posture, attack_count 3, weak HeavySlam weight so the selector starts the root first. Proof values, proposed. NEW profile and map only.
# (kept from F8) F8 posture proof (C-448): the Near phased profile (same four cards, band [110,140], attack_count 2) plus posture 100 / hit 60 / stagger 1.0 s / regen 6 s + 13 per s (design values, proposed). NEW profile and map only.
# Near-band variant (C-435): same cards as the baked variant, band [110,140] cm (Antigravity A-321 reach proposal for SwingMedium_P2). NEW profile and map only.
# Baked variant of create_f6c_content.py (C-433): phase one = F7 baked SwingSlow + HeavySlam, phase two = Antigravity P2 baked SwingMedium + AntiGreed. NEW profile and map only.
# F6c authoring (lead, Claude): phase authority proof. Copies of the F6 script; two NEW phase-two cards are DUPLICATES of existing F5 cards (SwingMedium, HeavySlam) with MoveId *_P2 and PhaseId Phase_2.
# F6 authoring (lead, Claude): NEW assets only (the four F5 cards are reused, not rewritten), refuses if any destination exists, reads values back, saves only the named packages. Windowed editor.
#   4 cards (author_move_cards.py, Antigravity move_cards_f5_set.json, damages = design values, proposed): Cards/Move_Sevarog_*_F5
#   /Game/OneBossFight/FrameworkProof/DA_Sevarog_SelectorProof_F5  (label "F5 fixture", selector config, 4 candidates, 2 attacks)
#   /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF5
import importlib.util
import json
import unreal

ROOT = 'C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/'
TOOL = ROOT + 'Antigravity/MoveCards/author_move_cards.py'
CARDS_JSON = ROOT + 'Antigravity/MoveCards/move_cards_f5_set.json'
DIR = '/Game/OneBossFight/FrameworkProof'
PROFILE_NAME = 'DA_Sevarog_Ring_HIT011'
PROFILE_PATH = DIR + '/' + PROFILE_NAME
LEVEL_PATH = DIR + '/L_SevarogFrameworkProofHIT011'
CAPSULE_RADIUS, CAPSULE_HALF_HEIGHT = 60.0, 165.0
BAND = (110.0, 140.0)   # inside every card range (100..200, 90..180, 90..185, 90..180) and the measured reach of the swings
BOSS_SPAWN = (500.0, 0.0, CAPSULE_HALF_HEIGHT + 5.0)
# Proof cooldowns (design values, proposed): SwingSlow 3.0 s, longer than Antigravity's 1.5 s, so the second decision shows the hard filter.
COOLDOWNS = {'Move_Sevarog_HeavyRing_HIT011': 0.1}
ORDER = ['Move_Sevarog_HeavyRing_HIT011']
DUPLICATES = {}  # F6c baked variant: all four cards already exist (F7 baked phase one, A-317 phase two), nothing is duplicated


def tag(t, payload):
    unreal.log('[F6C2_%s] %s' % (t, json.dumps(payload, default=str)))


def fatal(msg):
    unreal.log_error('[F6C2_FATAL] ' + msg)
    raise SystemExit(msg)


lib = unreal.EditorAssetLibrary
paths = [PROFILE_PATH, LEVEL_PATH] + [DIR + '/Cards/' + d for d in DUPLICATES]
for p in paths:
    if lib.does_asset_exist(p):
        fatal('destination exists, refusing: ' + p)
tag('PREFLIGHT', {'destinations_absent': paths})

# BOSS-HIT-011: ONE new card: a copy of HeavySlam_F7 with a SECONDARY RING window (ground shockwave around the boss, same hit group as the blade window, no sockets).
SRC = DIR + '/Cards/Move_Sevarog_HeavySlam_F7'
NEW_CARD = DIR + '/Cards/Move_Sevarog_HeavyRing_HIT011'
if lib.does_asset_exist(NEW_CARD):
    fatal('destination exists, refusing: ' + NEW_CARD)
if not lib.duplicate_asset(SRC, NEW_CARD):
    fatal('duplicate failed')
nc = unreal.load_asset(NEW_CARD)
spec = nc.get_editor_property('spec')
spec.set_editor_property('move_id', 'Move_Sevarog_HeavyRing_HIT011')
direct = list(spec.get_editor_property('windows'))
if len(direct) != 1:
    fatal('expected one window in HeavySlam_F7, got %d' % len(direct))
d0 = direct[0]
ring = unreal.RPGBossMoveWindow()
ring.set_editor_property('window_id', 'Window_HeavyRing_Ring')
ring.set_editor_property('hit_group', d0.get_editor_property('hit_group'))
ring_start = float(d0.get_editor_property('start_seconds'))
active_end = float(spec.get_editor_property('active_end_seconds'))
recovery_end = float(spec.get_editor_property('recovery_end_seconds'))
ring_end = min(ring_start + 0.3, recovery_end)   # the wave outlives the blade window; the card's active end moves to the wave's end (a NEW card, the original is untouched)
tag('CARD_TIMES', {'ring_start': ring_start, 'blade_end': float(d0.get_editor_property('end_seconds')), 'active_end': active_end, 'recovery_end': recovery_end, 'ring_end': ring_end})
if ring_end - ring_start < 0.2:
    fatal('no room for a 0.2 s wave in this card')
ring.set_editor_property('start_seconds', ring_start)
ring.set_editor_property('end_seconds', ring_end)
ring.set_editor_property('ring', True)
ring.set_editor_property('ring_start_radius_cm', 40.0)       # design values, proposed
ring.set_editor_property('ring_speed_cm_per_second', 600.0)
ring.set_editor_property('ring_thickness_cm', 50.0)
ring.set_editor_property('ring_height_cm', 80.0)
ring.set_editor_property('secondary', True)
spec.set_editor_property('active_end_seconds', max(active_end, ring_end))
spec.set_editor_property('windows', [ring, d0])
nc.set_editor_property('spec', spec)
back = nc.get_editor_property('spec').get_editor_property('windows')
if len(back) != 2 or not back[0].get_editor_property('ring') or back[1].get_editor_property('ring') or abs(float(back[0].get_editor_property('ring_speed_cm_per_second')) - 600.0) > 1e-3 or abs(float(back[0].get_editor_property('ring_thickness_cm')) - 50.0) > 1e-3:
    fatal('window readback mismatch')
if not lib.save_loaded_asset(nc):
    fatal('card save failed')
tag('RING_CARD', {'windows': [str(w.get_editor_property('window_id')) + ':ring=' + str(w.get_editor_property('ring')) + ':secondary=' + str(w.get_editor_property('secondary')) for w in back]})
for dst, srcname in DUPLICATES.items():
    if not lib.duplicate_asset(DIR + '/Cards/' + srcname, DIR + '/Cards/' + dst):
        fatal('duplicate failed ' + dst)
    d = unreal.load_asset(DIR + '/Cards/' + dst)
    spec = d.get_editor_property('spec')
    spec.set_editor_property('move_id', dst)
    spec.set_editor_property('phase_id', 'Phase_2')
    d.set_editor_property('spec', spec)
    back2 = d.get_editor_property('spec')
    if str(back2.get_editor_property('move_id')) != dst or str(back2.get_editor_property('phase_id')) != 'Phase_2':
        fatal('card readback ' + dst)
    if not lib.save_loaded_asset(d):
        fatal('card save ' + dst)
    tag('CARD', {'card': dst, 'phase': 'Phase_2', 'from': srcname})
cards = [unreal.load_asset(DIR + '/Cards/' + m) for m in ORDER]
p1 = [str(c.get_editor_property('spec').get_editor_property('phase_id')) for c in cards[:2]]
tag('PHASE_ONE_IDS', p1)
if len(set(p1)) != 1 or p1[0] == 'Phase_2':
    fatal('first two cards must share a phase one id')

tools = unreal.AssetToolsHelpers.get_asset_tools()
prof = tools.create_asset(PROFILE_NAME, DIR, unreal.RPGBossFrameworkProfile, unreal.DataAssetFactory())
if prof is None:
    fatal('profile create_asset returned None')
mesh = unreal.load_asset('/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog.Sevarog')
anim_cls = unreal.load_class(None, '/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sevarog_AnimBlueprint.Sevarog_AnimBlueprint_C')
target_cls = unreal.load_class(None, '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C')
if not (mesh and anim_cls and target_cls and all(cards)):
    fatal('dependency load failed')
numbers = {
    'band_min_cm': BAND[0], 'band_max_cm': BAND[1], 'walk_speed_cm_per_second': 180.0, 'acceptance_cm': 5.0,
    'walk_timeout_seconds': 10.0, 'blend_in_seconds': 0.1, 'blend_out_seconds': 0.03,
    'capsule_radius_cm': CAPSULE_RADIUS, 'capsule_half_height_cm': CAPSULE_HALF_HEIGHT, 'target_health': 800.0,
    'hit_step_cm': 15.0, 'hit_max_substeps': 8, 'repeat_penalty': 1.0, 'repeat_memory': 2, 'attack_count': 1, 'boss_max_health': 250.0, 'player_hit_damage': 100.0, 'phase_two_fraction': 0.0, 'posture_max': 0.0, 'player_posture_hit_amount': 0.0, 'stagger_seconds': 0.0, 'posture_regen_delay_seconds': 0.0, 'posture_regen_per_second': 0.0,
}
prof.set_editor_property('fixture_label', 'F5 fixture')  # same lane label: the F5 selector profile plus the boss health fields (design values, proposed)
prof.set_editor_property('damage_enabled', True)
prof.set_editor_property('alignment_authored', True)
for k, v in numbers.items():
    prof.set_editor_property(k, v)
prof.set_editor_property('phase_two_id', '')
def edge(to, lo, hi, yaw):
    e = unreal.RPGBossComboEdgeData()
    e.set_editor_property('to_node', to)
    e.set_editor_property('min_range_cm', lo)
    e.set_editor_property('max_range_cm', hi)
    e.set_editor_property('max_abs_yaw_degrees', yaw)
    e.set_editor_property('any_outcome', True)
    return e
def node(nid, move, edges):
    n = unreal.RPGBossComboNodeData()
    n.set_editor_property('node_id', nid)
    n.set_editor_property('move_id', move)
    n.set_editor_property('edges', edges)
    return n
prof.set_editor_property('mesh', mesh)
prof.set_editor_property('anim_class', anim_cls)
prof.set_editor_property('target_pawn_class', target_cls)
entries = []
for move, card in zip(ORDER, cards):
    e = unreal.RPGBossProfileCard()
    e.set_editor_property('card', card)
    e.set_editor_property('cooldown_seconds', COOLDOWNS[move])
    e.set_editor_property('weight', 1.0)   # equal weights: the choice is decided by range factor and the seeded tie stream
    entries.append(e)
prof.set_editor_property('cards', entries)
prof.set_editor_property('mesh_relative_transform', unreal.Transform(location=[0.0, 0.0, -CAPSULE_HALF_HEIGHT], rotation=unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0), scale=[1.0, 1.0, 1.0]))
back = {'fixture_label': prof.get_editor_property('fixture_label'), 'damage_enabled': prof.get_editor_property('damage_enabled')}
for k, v in numbers.items():
    back[k] = prof.get_editor_property(k)
    if abs(float(back[k]) - float(v)) > 1e-4:
        fatal('readback mismatch %s: %r != %r' % (k, back[k], v))
got = list(prof.get_editor_property('cards'))
if len(got) != len(ORDER):
    fatal('cards readback count')
for e, move in zip(got, ORDER):
    c = e.get_editor_property('card')
    if c is None or c.get_name() != move or abs(e.get_editor_property('cooldown_seconds') - COOLDOWNS[move]) > 1e-4:
        fatal('cards readback mismatch ' + move)
for k, want in (('mesh', mesh), ('anim_class', anim_cls), ('target_pawn_class', target_cls)):
    g = prof.get_editor_property(k)
    if g is None or g.get_path_name() != want.get_path_name():
        fatal('readback mismatch ' + k)
if prof.get_editor_property('card') is not None:
    fatal('single card must stay empty in an F5 profile')
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
tag('LEVEL_READBACK', {'game_mode': str(world.get_world_settings().get_editor_property('default_game_mode').get_name()),
                        'fixture_profile': fix.get_editor_property('profile').get_path_name()})
if not unreal.EditorLoadingAndSavingUtils.save_map(world, LEVEL_PATH):
    fatal('save_map failed')
tag('END', {'written': paths})
