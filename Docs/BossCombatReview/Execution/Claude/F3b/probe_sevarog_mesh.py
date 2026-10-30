# F3b read-only probe (synchronous, no keep-alive needed): Sevarog mesh bounds, skeleton identity, weapon bones, AnimBP generated class.
# Writes nothing to Content. Tags: [F3B_*]
import json
import unreal

MESH = '/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog.Sevarog'
ANIMBP = '/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sevarog_AnimBlueprint.Sevarog_AnimBlueprint_C'
SEQ = '/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Slow.Swing1_Slow'
out = {}


def log(tag, payload):
    unreal.log('[F3B_%s] %s' % (tag, json.dumps(payload, default=str)))
    out[tag] = payload


mesh = unreal.load_asset(MESH)
log('MESH', {'path': MESH, 'class': mesh.get_class().get_name() if mesh else None})
if mesh:
    box = mesh.get_bounds()  # BoxSphereBounds in the mesh's own space, cm
    o, e = box.origin, box.box_extent
    log('BOUNDS', {'origin': [o.x, o.y, o.z], 'box_extent': [e.x, e.y, e.z], 'sphere_radius': box.sphere_radius})
    sk = mesh.get_editor_property('skeleton')
    log('SKELETON', {'path': sk.get_path_name() if sk else None})
    seq = unreal.load_asset(SEQ)
    log('SEQUENCE', {'path': SEQ, 'class': seq.get_class().get_name() if seq else None,
                     'length': seq.get_editor_property('sequence_length') if seq else None,
                     'skeleton_equal': bool(seq and seq.get_editor_property('skeleton') == sk)})
    names = list(unreal.AnimationLibrary.get_animation_track_names(seq)) if seq else []
    log('TRACKS', {'count': len(names), 'has_weapon_r': 'weapon_r' in [str(n) for n in names],
                   'has_root_weapon_end_r': 'root_weapon_end_r' in [str(n) for n in names]})
    try:
        pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, 0.0, unreal.AnimPoseEvaluationOptions())
        ws = unreal.AnimPoseSpaces.WORLD
        for bone in ('root', 'pelvis', 'weapon_r', 'root_weapon_end_r'):
            try:
                t = unreal.AnimPoseExtensions.get_bone_pose(pose, bone, ws)
                log('BONE_' + bone, {'t0_world': [t.translation.x, t.translation.y, t.translation.z]})
            except Exception as ex:  # a missing bone is a measurement, not a crash
                log('BONE_' + bone, {'error': str(ex)})
    except Exception as ex:
        log('POSE_ERROR', {'error': str(ex)})

abp = unreal.load_object(None, ANIMBP)
log('ANIMBP', {'path': ANIMBP, 'class': abp.get_name() if abp else None, 'loaded': abp is not None})
unreal.log('[F3B_END] ok')
