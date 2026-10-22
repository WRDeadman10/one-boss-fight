import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy, os, math
from mathutils import Vector, Euler

bpy.ops.wm.read_factory_settings(use_empty=True)
ref_path = os.path.abspath('Import/ThirdParty/Reference/SKM_CombatMannequin_Simple.fbx')
bpy.ops.import_scene.fbx(filepath=ref_path)

arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
arm.name = 'root'
arm.data.name = 'root'

# Test 1: arm.location = (0, +90, 0) in cm (0.90 m)
# Test export
scene = bpy.context.scene
scene.render.fps = 30
scene.render.fps_base = 1.0
arm.animation_data_create()
act = bpy.data.actions.new('TestAct')
arm.animation_data.action = act

scene.frame_set(0)
arm.location = Vector((0, 0, 0))
arm.rotation_euler = Euler((0, 0, 0))
arm.keyframe_insert('location')
arm.keyframe_insert('rotation_euler')

scene.frame_set(30)
arm.location = Vector((0, 90.0, 0)) # or what unit?
arm.rotation_euler = Euler((0, 0, 0))
arm.keyframe_insert('location')
arm.keyframe_insert('rotation_euler')

out_fbx = os.path.abspath('Import/Boss01/Animations/test_root_travel.fbx')
bpy.ops.export_scene.fbx(
    filepath=out_fbx,
    use_selection=True,
    global_scale=1.0,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_NONE',
    axis_forward='-Z',
    axis_up='Y',
    object_types={'ARMATURE'},
    add_leaf_bones=False,
    primary_bone_axis='Y',
    secondary_bone_axis='X',
    bake_anim=True,
    bake_anim_use_all_bones=True,
    bake_anim_use_nla_strips=False,
    bake_anim_use_all_actions=False,
    bake_anim_step=1.0,
    bake_anim_simplify_factor=0.0
)
print('Exported test_root_travel.fbx')
"""

res = execute_blender(code)
print(res)
