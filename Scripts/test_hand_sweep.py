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

v_grip = Vector((-13.8996, 2.6063, 4.8925))
v_tip = Vector((-94.39, -18.50, 145.39))
S = Matrix.Diagonal(Vector((1.0, -1.0, 1.0, 1.0)))

def set_rot(pb_name, euler_deg):
    pb = arm.pose.bones[pb_name]
    pb.rotation_quaternion = Euler((math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))).to_quaternion()

def set_loc(pb_name, loc_cm):
    pb = arm.pose.bones[pb_name]
    pb.location = Vector(loc_cm)

pb = arm.pose.bones['pelvis']
pb.location = Vector((-48.0, 4.0, 0.0))
pb.rotation_quaternion = Euler((0, 0, math.radians(-4.0))).to_quaternion()

# Set base kneel spine and legs
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

set_rot("upperarm_r", (0, 30, -45))
set_rot("lowerarm_r", (0, 0, -45))
set_rot("upperarm_l", (0, 30, -45))
set_rot("lowerarm_l", (0, 0, -45))

# Let's sweep hand_r rotation:
# In lowerarm_r space, let's test rx, ry, rz in steps of 5 or 10 degrees
matches = []

# We can precompute lowerarm_r matrix:
bpy.context.view_layer.update()
pb_r = arm.pose.bones['hand_r']
pb_l = arm.pose.bones['hand_l']

# Notice that setting hand_r.rotation_quaternion only affects hand_r and its children (none)!
# It does NOT affect parent bones, so we can compute hand_r matrix directly!
# pose_matrix(hand_r) = parent.matrix @ bone_rest_rel @ local_rot
# Or we can just call update and test:
for rx in range(-180, 181, 15):
    for ry in range(-90, 91, 15):
        for rz in range(-180, 181, 15):
            set_rot("hand_r", (rx, ry, rz))
            # Just update hand_r:
            bpy.context.view_layer.update()
            
            M_bl_r = arm.matrix_world @ pb_r.matrix
            scale_trans = 100.0 if abs(M_bl_r.translation.z) < 10.0 else 1.0
            M_ue_r = S @ M_bl_r @ S
            pos_ue_r = Vector((M_ue_r[0][3] * scale_trans, M_ue_r[1][3] * scale_trans, M_ue_r[2][3] * scale_trans))
            rot_ue_r = M_ue_r.to_quaternion()
            
            g_ue = pos_ue_r + rot_ue_r @ v_grip
            t_ue = pos_ue_r + rot_ue_r @ v_tip
            d_ue = (t_ue - g_ue).normalized()
            
            # Constraints:
            # - tip Z in [0.0, 3.0]
            # - blade dir: Z in [-0.85, -0.50], Y >= 0.40, X in [-0.30, 0.30]
            # - hand_r: X in [-25, 25], Y in [20, 70], Z in [75, 125]
            if 0.0 <= t_ue.z <= 3.0:
                if -0.85 <= d_ue.z <= -0.50 and d_ue.y >= 0.40 and -0.30 <= d_ue.x <= 0.30:
                    score = abs(t_ue.z - 1.5) + abs(d_ue.x) * 10.0
                    matches.append((score, (rx, ry, rz), list(pos_ue_r), list(g_ue), list(t_ue), list(d_ue)))

matches.sort(key=lambda m: m[0])
print(f"Total matching orientations: {len(matches)}")
res = []
for m in matches[:10]:
    res.append({
        "score": round(m[0], 2),
        "rot": m[1],
        "hand_r": [round(x, 1) for x in m[2]],
        "grip": [round(x, 1) for x in m[3]],
        "tip": [round(x, 1) for x in m[4]],
        "bdir": [round(x, 2) for x in m[5]]
    })

result = res
"""

res = execute_blender(code)
import json
print(json.dumps(res, indent=2))
