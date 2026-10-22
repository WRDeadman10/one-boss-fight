import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy, os

bpy.ops.wm.read_factory_settings(use_empty=True)
fbx_path = os.path.abspath('Import/Boss01/Animations/AN_Boss01_StaggerDown.fbx')
bpy.ops.import_scene.fbx(filepath=fbx_path)

arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
scene = bpy.context.scene
scene.frame_set(0)

# Set action slot
act = arm.animation_data.action
if act and act.slots:
    arm.animation_data.action_slot = act.slots[0]
bpy.context.view_layer.update()

for bname in ['pelvis', 'head', 'neck_01', 'thigh_l', 'calf_l', 'foot_l', 'ball_l', 'thigh_r', 'calf_r', 'foot_r', 'ball_r']:
    pb = arm.pose.bones[bname]
    loc = (arm.matrix_world @ pb.matrix).to_translation()
    print(f'{bname:10s} loc: ({loc.x*100:.1f}, {loc.y*100:.1f}, {loc.z*100:.1f}) cm')
"""

res = execute_blender(code)
print(res)
