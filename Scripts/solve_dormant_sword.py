import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy, os, math
from mathutils import Vector, Euler, Matrix, Quaternion

ref_path = os.path.abspath("Import/ThirdParty/Reference/SKM_CombatMannequin_Simple.fbx")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=ref_path)
arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
arm.data.pose_position = 'POSE'

v_grip_bone = Vector((-13.8996, 2.6063, 4.8925))
u_blade_bone = Vector((-0.49286, -0.12920, 0.86044))
v_tip_bone = v_grip_bone + 163.3 * u_blade_bone
S = Matrix.Diagonal(Vector((1.0, -1.0, 1.0, 1.0)))

def get_ue_sword(arm):
    pb_r = arm.pose.bones['hand_r']
    pb_l = arm.pose.bones['hand_l']
    M_ue_r = S @ pb_r.matrix @ S
    pos_r = M_ue_r.to_translation()
    rot_r = M_ue_r.to_quaternion()
    M_ue_l = S @ pb_l.matrix @ S
    pos_l = M_ue_l.to_translation()
    grip = pos_r + rot_r @ v_grip_bone
    tip = pos_r + rot_r @ v_tip_bone
    bdir = (tip - grip).normalized()
    return grip, tip, bdir, pos_r, pos_l

def set_rot(pb_name, euler_deg):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.rotation_quaternion = Euler((math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))).to_quaternion()

def set_loc(pb_name, loc_cm):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.location = Vector(loc_cm)

set_loc("pelvis", (-48.0, 4.0, 0.0))
set_rot("pelvis", (0.0, 0.0, -4.0))
set_rot("spine_01", (0.0, 0.0, -5.0))
set_rot("spine_03", (0.0, 0.0, -6.0))
set_rot("spine_05", (0.0, 0.0, -7.0))
set_rot("neck_01", (0.0, 0.0, -8.0))
set_rot("head", (0.0, 0.0, -10.0))

set_rot("thigh_l", (85.0, 0.0, 10.0))
set_rot("calf_l", (0.0, -120.0, -60.0))
set_rot("foot_l", (0.0, -30.0, -30.0))
set_rot("thigh_r", (95.0, 0.0, -20.0))
set_rot("calf_r", (0.0, 120.0, -40.0))
set_rot("foot_r", (0.0, 60.0, 30.0))

# Targeted search:
# We want hand_r at x in [-20, 20], y in [25, 60], z in [80, 115]
# Let's test combinations of upperarm_r (pitch, roll, yaw) and lowerarm_r pitch
matches = []
for u_p in [-20, -10, 0, 10]:
    for u_r in [20, 35, 50]:
        for u_y in [-60, -45, -30]:
            set_rot("upperarm_r", (u_p, u_r, u_y))
            for l_p in [-80, -65, -50]:
                set_rot("lowerarm_r", (l_p, 0.0, 0.0))
                # For hand_r, test orientation
                for hp in [-90, -45, 0, 45, 90, 135]:
                    for hr in [-90, -45, 0, 45, 90]:
                        for hy in [-90, -45, 0, 45, 90]:
                            set_rot("hand_r", (hp, hr, hy))
                            bpy.context.view_layer.update()
                            grip, tip, bdir, pos_r, pos_l = get_ue_sword(arm)
                            if -25.0 <= pos_r.x <= 25.0 and 20.0 <= pos_r.y <= 70.0 and 75.0 <= pos_r.z <= 125.0:
                                if -0.85 <= bdir.z <= -0.50 and bdir.y >= 0.40 and -0.30 <= bdir.x <= 0.30:
                                    if 0.0 <= tip.z <= 3.0:
                                        err = abs(tip.z - 1.0) + abs(pos_r.x) * 0.1
                                        matches.append((err, (u_p, u_r, u_y), l_p, (hp, hr, hy), pos_r, grip, tip, bdir))

matches.sort(key=lambda m: m[0])
print(f"Total valid matches found: {len(matches)}")
res = []
for m in matches[:10]:
    res.append({
        "upperarm_r": m[1],
        "lowerarm_r": m[2],
        "hand_r": m[3],
        "hand_pos": [round(x, 1) for x in m[4]],
        "grip": [round(x, 1) for x in m[5]],
        "tip": [round(x, 1) for x in m[6]],
        "bdir": [round(x, 2) for x in m[7]]
    })
result = res
"""

res = execute_blender(code)
import json
print(json.dumps(res, indent=2))
