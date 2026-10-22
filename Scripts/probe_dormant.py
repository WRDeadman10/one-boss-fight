import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy, os

for fname in ['AN_Boss01_DormantIdle.fbx', 'AN_Boss01_Wake.fbx']:
    p = os.path.abspath(os.path.join('Import/Boss01/Animations', fname))
    if not os.path.exists(p):
        print(f'{fname}: not found')
        continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=p)
    arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    act = arm.animation_data.action
    print(f'{fname}: frames {act.frame_range[0]}..{act.frame_range[1]} ({(act.frame_range[1]-act.frame_range[0]+1)} frames)')
    
    # Check bone positions
    s = bpy.context.scene
    s.frame_set(int(act.frame_range[0]))
    bpy.context.view_layer.update()
    pel = arm.matrix_world @ arm.pose.bones['pelvis'].matrix
    hr = arm.matrix_world @ arm.pose.bones['hand_r'].matrix
    hl = arm.matrix_world @ arm.pose.bones['hand_l'].matrix
    print(f'  frame 0: pelvis Z={pel.translation.z*100:.1f}, hand_r=({hr.translation.x*100:.1f}, {hr.translation.y*100:.1f}, {hr.translation.z*100:.1f}), hand_l=({hl.translation.x*100:.1f}, {hl.translation.y*100:.1f}, {hl.translation.z*100:.1f})')
"""

res = execute_blender(code)
print(res)
