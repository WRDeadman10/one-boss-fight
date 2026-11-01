# MOV-004 proof (lead, Claude): NEW map only. A copy (load the source, add the wall, save as the new name) of the ANM-006 warp proof map (same profile DA_Sevarog_Warp_ANM006, same warp card: 150 cm / 45 deg budget) with one WALL added: a long cube 800 x 20 x 200 cm whose face is at y = 150, across the line the boss
# warps along when the target is shifted to the side (rpg.BossProofTargetShift 0.0:0,300,0). The boss capsule radius is 60, so a swept warp must stop at y = 90 and never put the boss through the wall. Refuses if the destination exists; reads back; saves only the new map.
import json
import unreal

SRC = '/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofANM006'
DST = '/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofMOV004'


def tag(t, payload):
    unreal.log('[MOV004_%s] %s' % (t, json.dumps(payload, default=str)))


def fatal(msg):
    unreal.log_error('[MOV004_FATAL] ' + msg)
    raise SystemExit(msg)


lib = unreal.EditorAssetLibrary
if lib.does_asset_exist(DST):
    fatal('destination exists, refusing: ' + DST)
if not lib.does_asset_exist(SRC):
    fatal('source map missing: ' + SRC)
tag('PREFLIGHT', {'src': SRC, 'dst_absent': DST})
# Load the SOURCE map, add the wall, and save the world under the NEW name (the source file on disk is never saved).
if not unreal.EditorLevelLibrary.load_level(SRC):
    fatal('load_level failed')
world = unreal.EditorLevelLibrary.get_editor_world()
cube = unreal.load_asset('/Engine/BasicShapes/Cube')
wall = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0.0, 160.0, 100.0))
if wall is None or cube is None:
    fatal('wall spawn failed')
wall.set_actor_label('ProofWall')
wall.static_mesh_component.set_static_mesh(cube)
wall.set_actor_scale3d(unreal.Vector(8.0, 0.2, 2.0))   # 800 x 20 x 200 cm: faces at y = 150 and y = 170
back = wall.get_actor_location()
scale = wall.get_actor_scale3d()
if abs(back.y - 160.0) > 1e-3 or abs(scale.y - 0.2) > 1e-3:
    fatal('wall readback mismatch')
tag('WALL', {'location': [back.x, back.y, back.z], 'scale': [scale.x, scale.y, scale.z], 'collision': str(wall.static_mesh_component.get_collision_profile_name())})
if not unreal.EditorLoadingAndSavingUtils.save_map(world, DST):
    fatal('save_map failed')
tag('END', {'written': DST})
