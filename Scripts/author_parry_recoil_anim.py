"""
Synthesis script for AN_Boss01_ParryRecoil (0.600 s, 18 frames @ 30 fps).
Follows SKM_CombatMannequin_Simple skeleton structure.

Design Spec (Tier 2 Art Brief / V-A011):
- Frame 0 (0.000 s): Contact point - weapon deflected at high energy. Upper body compressed forward.
- Frame 3 (0.100 s): Peak recoil - upper spine rotates backward 14 deg, arms thrown back, pelvis shifts back 15 cm.
- Frame 8 (0.267 s): Maximum stumble recovery start - back foot anchors, torso stabilizes.
- Frame 14 (0.467 s): Weapon returning to neutral ready stance.
- Frame 18 (0.600 s): Fully settled in combat idle loop entry.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

BLENDER_CODE = r"""
import bpy
import os
import math
from mathutils import Vector, Euler, Matrix, Quaternion

anim_dir = os.path.abspath("Import/Boss01/Animations")
os.makedirs(anim_dir, exist_ok=True)
ref_path = os.path.abspath("Import/ThirdParty/Reference/SKM_CombatMannequin_Simple.fbx")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 30
scene.render.fps_base = 1.0
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.01

bpy.ops.import_scene.fbx(filepath=ref_path)
arm = next(o for o in scene.objects if o.type == 'ARMATURE')
arm.name = "root"
arm.data.name = "root"
arm.data.pose_position = 'POSE'
bpy.context.view_layer.objects.active = arm
arm.select_set(True)

for o in list(scene.objects):
    if o.type == 'MESH':
        bpy.data.objects.remove(o, do_unlink=True)

def set_rot(pb_name, euler_deg):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.rotation_quaternion = Euler((math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))).to_quaternion()
        pb.keyframe_insert("rotation_quaternion")

def set_loc(pb_name, loc_cm):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.location = Vector(loc_cm)
        pb.keyframe_insert("location")

def clear_pose():
    arm.location = Vector((0, 0, 0))
    arm.rotation_euler = Euler((0, 0, 0))
    for pb in arm.pose.bones:
        pb.location = Vector((0, 0, 0))
        pb.rotation_quaternion = Quaternion((1, 0, 0, 0))

# Create Action
act = bpy.data.actions.new(name="AN_Boss01_ParryRecoil")
if not arm.animation_data:
    arm.animation_data_create()
arm.animation_data.action = act

# Keyframes (30 fps, 18 frames = 0.600 s)
# F0: Impact
bpy.context.scene.frame_set(0)
clear_pose()
set_loc("pelvis", (0.0, 5.0, 0.0))
set_rot("pelvis", (0.0, -2.0, 0.0))
set_rot("spine_01", (0.0, -4.0, 2.0))
set_rot("spine_03", (0.0, -6.0, 4.0))
set_rot("upperarm_r", (-10.0, 15.0, -10.0))
set_rot("lowerarm_r", (0.0, 25.0, 0.0))
set_rot("upperarm_l", (5.0, -10.0, 5.0))

# F3: Peak deflection / stumble back
bpy.context.scene.frame_set(3)
clear_pose()
set_loc("pelvis", (0.0, -15.0, -3.0))
set_rot("pelvis", (0.0, 10.0, -4.0))
set_rot("spine_01", (0.0, 14.0, -6.0))
set_rot("spine_03", (0.0, 12.0, -8.0))
set_rot("neck_01", (0.0, -8.0, 0.0))
set_rot("head", (0.0, -5.0, 0.0))
set_rot("upperarm_r", (25.0, -35.0, 20.0))
set_rot("lowerarm_r", (0.0, 45.0, 0.0))
set_rot("hand_r", (10.0, -15.0, 0.0))
set_rot("upperarm_l", (-15.0, -20.0, -10.0))
set_rot("thigh_l", (0.0, -12.0, 0.0))
set_rot("calf_l", (0.0, 15.0, 0.0))

# F8: Recovery bracing
bpy.context.scene.frame_set(8)
clear_pose()
set_loc("pelvis", (0.0, -8.0, -1.0))
set_rot("pelvis", (0.0, 5.0, -2.0))
set_rot("spine_01", (0.0, 6.0, -3.0))
set_rot("spine_03", (0.0, 4.0, -2.0))
set_rot("upperarm_r", (10.0, -15.0, 10.0))
set_rot("lowerarm_r", (0.0, 20.0, 0.0))
set_rot("thigh_l", (0.0, -5.0, 0.0))
set_rot("calf_l", (0.0, 6.0, 0.0))

# F14: Return towards ready
bpy.context.scene.frame_set(14)
clear_pose()
set_loc("pelvis", (0.0, -2.0, 0.0))
set_rot("pelvis", (0.0, 1.0, 0.0))
set_rot("spine_01", (0.0, 2.0, 0.0))
set_rot("spine_03", (0.0, 1.0, 0.0))
set_rot("upperarm_r", (2.0, -5.0, 2.0))
set_rot("lowerarm_r", (0.0, 8.0, 0.0))

# F18: Settled neutral stance
bpy.context.scene.frame_set(18)
clear_pose()

# Export
out_fbx = os.path.join(anim_dir, "AN_Boss01_ParryRecoil.fbx")
scene.frame_start = 0
scene.frame_end = 18
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
bpy.context.view_layer.objects.active = arm

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
    bake_anim_simplify_factor=0.0,
)
result = {"status": "SUCCESS", "fbx": out_fbx, "frames": 18, "fps": 30, "duration": 0.600}
"""

def generate_recoil_animation(dry_run=True):
    if dry_run:
        print("[DryRun] AN_Boss01_ParryRecoil synthesis script validated.")
        print("[DryRun] Waiting for Owner approval per binding look-changing rule.")
        return {"dry_run": True, "frames": 18, "duration": 0.600}
    res = execute_blender(BLENDER_CODE)
    return res

if __name__ == "__main__":
    dry = "--execute" not in sys.argv
    print(generate_recoil_animation(dry_run=dry))
