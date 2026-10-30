# F6b/F5 read-only probe: measure pack player target capsule dimensions and hit sockets.
# Used by Claude to tighten the proof arrival band (KI-147 reach analysis).
# Writes nothing to Content. Tags: [TARGET_PROBE_*]
import json
import unreal

TARGET_BP = '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C'
BASE_BP = '/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/BP_BaseCombatCharacter.BP_BaseCombatCharacter_C'
SKM_MANNEQUIN = '/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin_Simple.SKM_CombatMannequin_Simple'

out = {}


def log(tag, payload):
    unreal.log('[TARGET_PROBE_%s] %s' % (tag, json.dumps(payload, default=str)))
    out[tag] = payload


# 1. Inspect Target Class & CDO
target_cls = unreal.load_class(None, TARGET_BP)
base_cls = unreal.load_class(None, BASE_BP)

log('CLASSES', {
    'target_bp': TARGET_BP,
    'target_loaded': target_cls is not None,
    'base_bp': BASE_BP,
    'base_loaded': base_cls is not None
})

if target_cls:
    cdo = unreal.get_default_object(target_cls)
    log('CDO', {'name': cdo.get_name() if cdo else None})
    if cdo:
        try:
            capsule = cdo.get_editor_property('capsule_component')
            if capsule:
                r = capsule.get_editor_property('capsule_radius')
                hh = capsule.get_editor_property('capsule_half_height')
                loc = capsule.get_editor_property('relative_location')
                col_prof = capsule.get_editor_property('collision_profile_name')
                log('CAPSULE', {
                    'radius_cm': r,
                    'half_height_cm': hh,
                    'relative_location': [loc.x, loc.y, loc.z] if loc else None,
                    'collision_profile': str(col_prof) if col_prof else None
                })
        except Exception as ex:
            log('CAPSULE_ERROR', {'error': str(ex)})

        try:
            mesh = cdo.get_editor_property('mesh')
            if mesh:
                rel_loc = mesh.get_editor_property('relative_location')
                rel_rot = mesh.get_editor_property('relative_rotation')
                skm = None
                for prop in ('skeletal_mesh_asset', 'skeletal_mesh'):
                    try:
                        skm = mesh.get_editor_property(prop)
                        if skm:
                            break
                    except Exception:
                        pass
                log('MESH_COMPONENT', {
                    'relative_location': [rel_loc.x, rel_loc.y, rel_loc.z] if rel_loc else None,
                    'relative_rotation': [rel_rot.pitch, rel_rot.yaw, rel_rot.roll] if rel_rot else None,
                    'skeletal_mesh': skm.get_path_name() if skm else None
                })
        except Exception as ex:
            log('MESH_COMPONENT_ERROR', {'error': str(ex)})

# 2. Inspect Skeletal Mesh Asset directly
skm_asset = unreal.load_asset(SKM_MANNEQUIN)
if skm_asset:
    box = skm_asset.get_bounds()
    o, e = box.origin, box.box_extent
    log('SKM_BOUNDS', {
        'origin': [o.x, o.y, o.z],
        'box_extent': [e.x, e.y, e.z],
        'sphere_radius': box.sphere_radius
    })

    # Query Sockets
    key_bones = ['root', 'pelvis', 'spine_01', 'spine_02', 'spine_03', 'head', 'hand_l', 'hand_r']
    bone_info = {}
    for b in key_bones:
        try:
            t = skm_asset.get_socket_transform(b, unreal.RelativeTransformSpace.RTS_ACTOR)
            bone_info[b] = {
                'translation': [t.translation.x, t.translation.y, t.translation.z]
            }
        except Exception as ex:
            bone_info[b] = {'error': str(ex)}
    log('KEY_SOCKETS', bone_info)

# 3. Spawn Test Instance in Editor Level (if world context available)
try:
    world = unreal.EditorLevelLibrary.get_editor_world()
    if world and target_cls:
        spawn_loc = unreal.Vector(0.0, 0.0, 100.0)
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(target_cls, spawn_loc)
        if actor:
            inst_capsule = actor.get_editor_property('capsule_component')
            ir = inst_capsule.get_editor_property('capsule_radius')
            ihh = inst_capsule.get_editor_property('capsule_half_height')
            inst_loc = actor.get_actor_location()
            log('SPAWNED_INSTANCE', {
                'radius_cm': ir,
                'half_height_cm': ihh,
                'world_location': [inst_loc.x, inst_loc.y, inst_loc.z]
            })
            unreal.EditorLevelLibrary.destroy_actor(actor)
except Exception as ex:
    log('SPAWN_NOTE', {'note': 'World spawn skipped or unsupported in current headless context', 'error': str(ex)})

log('END', {'status': 'ok'})
unreal.log('[TARGET_PROBE_COMPLETE] All player target capsule and socket measurements finished')
