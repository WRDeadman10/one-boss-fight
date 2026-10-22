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

# Keyframe points for Player Riposte (49 frames: 0..48)
# Root travels along +Y in Unreal from (0,0,0) to (0,90,0) reached by frame 21 (0.7s)
# In Blender, forward is -Y!
# Let's verify whether arm.location along -Y produces +Y in Unreal:
# In review_report11:
# When arm.location was (rx, 0, 0), Unreal reported root x = rx!
# For Y: when foot_l had -19.4 in Blender, Unreal reported foot_l.y = +19.4!
# Let's verify whether Blender -Y is Unreal +Y!
"""

res = execute_blender(code)
print(res)
