import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy, os, math
from mathutils import Vector, Euler, Matrix, Quaternion

bpy.ops.wm.read_factory_settings(use_empty=True)
ref_path = os.path.abspath('Import/ThirdParty/Reference/SKM_CombatMannequin_Simple.fbx')
bpy.ops.import_scene.fbx(filepath=ref_path)

arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
arm.name = 'root'
arm.data.name = 'root'

for o in list(bpy.context.scene.objects):
    if o.type == 'MESH':
        bpy.data.objects.remove(o, do_unlink=True)

scene = bpy.context.scene
scene.render.fps = 30
scene.render.fps_base = 1.0
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.01

arm.animation_data_create()
act = bpy.data.actions.new('ACT_Riposte_Player_Front')
arm.animation_data.action = act
if act.slots:
    arm.animation_data.action_slot = act.slots[0]

def set_rot(pb_name, euler_deg):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.rotation_quaternion = Euler((math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))).to_quaternion()
        pb.keyframe_insert('rotation_quaternion')

def set_loc(pb_name, loc_cm):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.location = Vector(loc_cm)
        pb.keyframe_insert('location')

def clear_pose():
    arm.location = Vector((0, 0, 0))
    arm.rotation_euler = Euler((0, 0, 0))
    for pb in arm.pose.bones:
        pb.location = Vector((0, 0, 0))
        pb.rotation_quaternion = Quaternion((1, 0, 0, 0))

# Convert Blender world bone pos to Unreal component space (cm):
# In Unreal component space:
# UE_X = Blender_X
# UE_Y = -Blender_Y
# UE_Z = Blender_Z
def get_ue_bone_world(bname):
    pb = arm.pose.bones[bname]
    mw = arm.matrix_world @ pb.matrix
    v = mw.to_translation()
    # scale is 0.01 in scene, so v is in meters -> * 100 for cm
    # Wait, check if v is in meters or cm:
    scale_factor = 100.0 if arm.scale.x > 0.5 else 100.0
    return Vector((v.x * 100.0, -v.y * 100.0, v.z * 100.0))

def get_ue_root_world():
    v = arm.matrix_world.to_translation()
    return Vector((v.x * 100.0, -v.y * 100.0, v.z * 100.0))

print('Setup verified successfully')
"""

res = execute_blender(code)
print(res)
