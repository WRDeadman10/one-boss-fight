# BOSS-MOV-006 audit (lead, Claude): "Arena geometry (L_SevarogArena) provides a clear combat lane with zero player snag points." READ-ONLY: loads the level, traces, writes a JSON report, saves nothing.
# Lane: the disc INSIDE the pillar ring (the fight happens there): radius = ArenaRadius * PillarRingFraction - PillarRadius - 2 * the player capsule radius, read from the level's ARPGGreyboxArena actor.
# The floor trace starts just above the player's head (2 x half height + 58 cm = 250 cm), so the tops of tall props are not mistaken for floor.
# Per grid cell (GRID cm): the floor (line trace down) must exist and be walkable (the player's WalkableFloorAngle); no LIP: a neighbouring walkable floor cell more than the player's MaxStepHeight higher/lower;
# and a player-size capsule (radius/half height read from BP_CombatPlayerCharacter) swept in 8 directions for SWEEP_CM: a SNAG is a cell where the capsule starts INSIDE geometry, or is stopped by a LOW blocker
# (the blocker's bounds are lower than SNAG_HEIGHT_CM: the player can neither step over it nor easily see it). A tall blocker (pillar, wall, big prop) is a legitimate, visible obstacle and is counted, not flagged.
import json
import math
import os
import unreal

GRID = float(os.environ.get('MOV006_GRID', '60'))
SWEEP_CM = 150.0
SNAG_HEIGHT_CM = 100.0
MAP = '/Game/OneBossFight/Levels/L_SevarogArena'
PLAYER_BP = '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C'
OUT = os.environ.get('MOV006_OUT', 'C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/B_MOV006/report.json')


def tag(t, payload):
    unreal.log('[MOV006_%s] %s' % (t, json.dumps(payload, default=str)))


def fatal(msg):
    unreal.log_error('[MOV006_FATAL] ' + msg)
    raise SystemExit(msg)


if not unreal.EditorLevelLibrary.load_level(MAP):
    fatal('load_level failed: ' + MAP)
world = unreal.EditorLevelLibrary.get_editor_world()
if world is None:
    fatal('no editor world')

# NEGATIVE CONTROL (env MOV006_CONTROL=1, windowed editor only): a low 50 cm box is dropped into the lane, in memory, the level is never saved. The audit MUST flag it.
if os.environ.get('MOV006_CONTROL') == '1':
    cube = unreal.load_asset('/Engine/BasicShapes/Cube')
    box = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(300.0, 300.0, 25.0))
    box.set_actor_label('AuditControlLowBox')
    box.static_mesh_component.set_static_mesh(cube)
    box.set_actor_scale3d(unreal.Vector(1.0, 1.0, 0.5))   # 100 x 100 x 50 cm: below the 100 cm snag height
    tag('CONTROL', {'low_box_at': [300.0, 300.0], 'size_cm': [100, 100, 50]})

# the player numbers, read from the class default object (never hard-coded)
cls = unreal.load_class(None, PLAYER_BP)
if cls is None:
    fatal('player class not loaded')
cdo = unreal.get_default_object(cls)
cap = cdo.get_editor_property('capsule_component')
mv = cdo.get_editor_property('character_movement')
RADIUS = float(cap.get_editor_property('capsule_radius'))
HALF = float(cap.get_editor_property('capsule_half_height'))
MAX_STEP = float(mv.get_editor_property('max_step_height'))
WALK_ANGLE = float(mv.get_editor_property('walkable_floor_angle'))
MIN_NORMAL_Z = math.cos(math.radians(WALK_ANGLE))
LIP_CM = max(MAX_STEP, GRID * math.tan(math.radians(WALK_ANGLE)))   # a walkable slope may rise this much between two neighbouring cells
tag('PLAYER', {'radius': RADIUS, 'half_height': HALF, 'max_step_height': MAX_STEP, 'walkable_floor_angle': WALK_ANGLE})

# the lane, from the level's own arena actor
arena = None
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if a.get_class().get_name() == 'RPGGreyboxArena':
        arena = a
        break
if arena is None:
    fatal('no RPGGreyboxArena actor in the level')
ar = float(arena.get_editor_property('arena_radius'))
ring = float(arena.get_editor_property('pillar_ring_fraction'))
pr = float(arena.get_editor_property('pillar_radius'))
centre = arena.get_actor_location()
LANE_R = ar * ring - pr - 2.0 * RADIUS
tag('LANE', {'arena_radius': ar, 'pillar_ring_fraction': ring, 'pillar_radius': pr, 'centre': [centre.x, centre.y, centre.z], 'lane_radius': LANE_R, 'grid_cm': GRID})


def tup(hit):
    return hit.to_tuple() if hasattr(hit, 'to_tuple') else hit


def line_down(x, y):
    h = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, centre.z + 2.0 * HALF + 58.0), unreal.Vector(x, y, centre.z - 300.0), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
    if h is None:
        return None
    t = tup(h)
    if not t[0]:
        return None
    return t[5], t[7]   # impact point, impact normal


OBJECTS = [unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1, unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY2]


def sweep(sx, sy, sz, ex, ey):
    h = unreal.SystemLibrary.capsule_trace_single_for_objects(world, unreal.Vector(sx, sy, sz), unreal.Vector(ex, ey, sz), RADIUS, HALF, OBJECTS, False, [], unreal.DrawDebugTrace.NONE, True)
    if h is None:
        return None
    return tup(h)


def blocks_pawn(comp):
    try:
        return comp.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN) == unreal.CollisionResponse.ECR_BLOCK
    except Exception:
        return True   # unreadable response: assume it blocks (never silently pass)


def blocker_height(t):
    # The height of what blocked the capsule: its static mesh's bounding box height times the world scale (of the hit instance for an instanced component). Unreadable = None (counted, never silently passed).
    comp = t[10]
    if comp is None:
        return None, 'None', 'None'
    owner = comp.get_owner()
    oname = owner.get_name() if owner else 'None'
    try:
        mesh = comp.get_editor_property('static_mesh')
    except Exception:
        return None, oname, comp.get_name()
    if mesh is None:
        return None, oname, comp.get_name()
    bb = mesh.get_bounding_box()
    h = float(bb.max.z - bb.min.z)
    sz = None
    try:
        res = comp.get_instance_transform(int(t[12]), True)
        tr = res[1] if isinstance(res, tuple) else res
        sz = abs(float(tr.scale3d.z))
    except Exception:
        try:
            sz = abs(float(comp.get_world_transform().scale3d.z))
        except Exception:
            sz = None
    return (h * sz if sz is not None else None), oname, comp.get_name()


# the grid
cells = []
n = int(LANE_R // GRID)
floor = {}
for i in range(-n, n + 1):
    for j in range(-n, n + 1):
        x, y = centre.x + i * GRID, centre.y + j * GRID
        if math.hypot(x - centre.x, y - centre.y) <= LANE_R:
            floor[(i, j)] = line_down(x, y)
tag('GRID', {'cells': len(floor)})
holes, lips, unwalk, snags, unknown, tall = [], [], [], [], [], {}
seen, occupied = set(), set()
nonblocking = {}
pawn_hits = {}
near_tall = set()
sweeps = 0
dirs = [(math.cos(k * math.pi / 4.0), math.sin(k * math.pi / 4.0)) for k in range(8)]
for (i, j), f in floor.items():
    x, y = centre.x + i * GRID, centre.y + j * GRID
    if f is None:
        holes.append([x, y])
        continue
    z, nrm = f[0].z, f[1]
    if nrm.z < MIN_NORMAL_Z:
        unwalk.append([x, y, round(nrm.z, 3)])
        for dx, dy in dirs:   # the sweeps of an unwalkable cell only tell what it is beside
            sweeps += 1
            t = sweep(x, y, z + HALF + 2.0, x + dx * SWEEP_CM, y + dy * SWEEP_CM)
            if t is not None and t[0] and t[10] is not None and blocks_pawn(t[10]):
                h, _, _ = blocker_height(t)
                if h is not None and h >= SNAG_HEIGHT_CM:
                    near_tall.add((x, y))
        continue
    for di, dj in ((1, 0), (0, 1), (1, 1), (1, -1)):
        o = floor.get((i + di, j + dj))
        if o is not None and abs(o[0].z - z) > LIP_CM:
            lips.append([x, y, round(o[0].z - z, 1)])
            break
    sz = z + HALF + 2.0
    for dx, dy in dirs:
        sweeps += 1
        t = sweep(x, y, sz, x + dx * SWEEP_CM, y + dy * SWEEP_CM)
        if t is None or not t[0]:
            continue
        own = t[10].get_owner() if t[10] is not None else None
        if own is not None and isinstance(own, unreal.Pawn):
            pawn_hits[own.get_name()] = pawn_hits.get(own.get_name(), 0) + 1
            continue
        if t[10] is not None and not blocks_pawn(t[10]):
            nonblocking[(t[10].get_owner().get_name() if t[10].get_owner() else 'None', t[10].get_name())] = nonblocking.get((t[10].get_owner().get_name() if t[10].get_owner() else 'None', t[10].get_name()), 0) + 1
            continue
        height, owner, comp = blocker_height(t)
        hs = round(height, 1) if height is not None else None
        key = (x, y, owner, comp)
        if height is None:
            if key not in seen:
                seen.add(key); unknown.append({'x': x, 'y': y, 'actor': owner, 'component': comp})
        elif height < SNAG_HEIGHT_CM:
            # a LOW blocker: the capsule starts inside it or is stopped by it: nothing the player can see from afar or step over
            if key not in seen:
                seen.add(key); snags.append({'x': x, 'y': y, 'why': 'StartPenetrating' if t[1] else 'LowBlocker', 'actor': owner, 'component': comp, 'height_cm': hs})
        elif t[1]:
            occupied.add((x, y))   # the cell centre is inside a TALL obstacle (a brazier, a pillar): not a place a player can stand
            near_tall.add((x, y))
        else:
            tall[owner] = tall.get(owner, 0) + 1
            near_tall.add((x, y))
for (i, j), f in floor.items():
    if f is not None and f[0].z - centre.z >= SNAG_HEIGHT_CM:
        near_tall.add((centre.x + i * GRID, centre.y + j * GRID))   # the top of a prop taller than 100 cm
def beside_tall(x, y):
    return any(abs(x - tx) <= 2 * GRID + 1e-3 and abs(y - ty) <= 2 * GRID + 1e-3 for tx, ty in near_tall)
lips_free = [c for c in lips if not beside_tall(c[0], c[1])]
unwalk_free = [c for c in unwalk if not beside_tall(c[0], c[1])]
verdict = len(holes) == 0 and len(lips_free) == 0 and len(unwalk_free) == 0 and len(snags) == 0 and len(unknown) == 0
report = {'map': MAP, 'player': {'radius': RADIUS, 'half_height': HALF, 'max_step_height': MAX_STEP, 'walkable_floor_angle': WALK_ANGLE},
          'lane_radius_cm': LANE_R, 'grid_cm': GRID, 'cells': len(floor), 'capsule_sweeps': sweeps,
          'holes': len(holes), 'lips': len(lips), 'lips_beside_tall_obstacles': len(lips) - len(lips_free), 'lips_free': len(lips_free), 'unwalkable_cells': len(unwalk), 'unwalkable_beside_tall_obstacles': len(unwalk) - len(unwalk_free), 'unwalkable_free': len(unwalk_free), 'pawn_hits_excluded': pawn_hits, 'nonblocking_trigger_hits': {'%s/%s' % k: v for k, v in nonblocking.items()}, 'snag_points': len(snags), 'cells_inside_tall_obstacles': len(occupied), 'unreadable_blockers': len(unknown),
          'tall_obstacle_blocks_by_actor': tall, 'first_snags': snags[:50], 'first_unreadable': unknown[:20], 'first_lips': lips_free[:20], 'first_unwalkable_free': unwalk_free[:20], 'first_holes': holes[:20], 'first_unwalkable': unwalk[:20], 'pass': verdict}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as fh:
    json.dump(report, fh, indent=1, default=str)
tag('SUMMARY', {k: report[k] for k in ('lane_radius_cm', 'cells', 'capsule_sweeps', 'holes', 'lips', 'lips_beside_tall_obstacles', 'lips_free', 'unwalkable_cells', 'unwalkable_beside_tall_obstacles', 'unwalkable_free', 'snag_points', 'cells_inside_tall_obstacles', 'unreadable_blockers', 'pass')})
tag('TALL', tall)
for s in snags[:10]:
    tag('SNAG', s)
tag('VERDICT', {'pass': verdict})
