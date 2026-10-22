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
    pb = arm.pose.bones.get(pb_name)
    pb.rotation_quaternion = Euler((math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))).to_quaternion()

def set_loc(pb_name, loc_cm):
    pb = arm.pose.bones.get(pb_name)
    pb.location = Vector(loc_cm)

pb = arm.pose.bones['pelvis']
pb.location = Vector((-48.0, 4.0, 0.0))
pb.rotation_quaternion = Euler((0, 0, math.radians(-4.0))).to_quaternion()

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
set_rot("hand_r", (0, 0, 0))

bpy.context.view_layer.update()

pb_r = arm.pose.bones['hand_r']
pb_p = pb_r.parent
b = arm.data.bones['hand_r']
b_p = b.parent

M_rest_rel = b_p.matrix_local.inverted() @ b.matrix_local
M_parent = pb_p.matrix.copy()

scale_trans = 100.0 if abs(M_parent.translation.z) < 10.0 else 1.0

near_zeros = []
for rx in range(-180, 181, 5):
    for ry in range(-90, 91, 5):
        for rz in range(-180, 181, 5):
            q_loc = Euler((math.radians(rx), math.radians(ry), math.radians(rz))).to_quaternion()
            M_bone = M_parent @ M_rest_rel @ q_loc.to_matrix().to_4x4()
            
            M_ue = S @ M_bone @ S
            pos_ue = Vector((M_ue[0][3] * scale_trans, M_ue[1][3] * scale_trans, M_ue[2][3] * scale_trans))
            rot_ue = M_ue.to_quaternion()
            
            g_ue = pos_ue + rot_ue @ v_grip
            t_ue = pos_ue + rot_ue @ v_tip
            d_ue = (t_ue - g_ue).normalized()
            
            if -0.85 <= d_ue.z <= -0.50 and d_ue.y >= 0.40 and -0.30 <= d_ue.x <= 0.30:
                if abs(t_ue.z - 1.5) < 10.0:
                    near_zeros.append(((rx, ry, rz), t_ue.z, list(d_ue)))

print(f"Near zeros found: {len(near_zeros)}")

# Now for each near zero, do a fine 0.2 deg sweep on rx, ry, rz:
fine_matches = []
for (bx, by, bz), tz, d_ue in near_zeros[:50]:
    for dx in [-2.0, -1.0, 0.0, 1.0, 2.0]:
        for dy in [-2.0, -1.0, 0.0, 1.0, 2.0]:
            for dz in [-2.0, -1.0, 0.0, 1.0, 2.0]:
                rx = bx + dx
                ry = by + dy
                rz = bz + dz
                q_loc = Euler((math.radians(rx), math.radians(ry), math.radians(rz))).to_quaternion()
                M_bone = M_parent @ M_rest_rel @ q_loc.to_matrix().to_4x4()
                
                M_ue = S @ M_bone @ S
                pos_ue = Vector((M_ue[0][3] * scale_trans, M_ue[1][3] * scale_trans, M_ue[2][3] * scale_trans))
                rot_ue = M_ue.to_quaternion()
                
                g_ue = pos_ue + rot_ue @ v_grip
                t_ue = pos_ue + rot_ue @ v_tip
                d_ue = (t_ue - g_ue).normalized()
                
                if 0.5 <= t_ue.z <= 2.5:
                    if -0.85 <= d_ue.z <= -0.50 and d_ue.y >= 0.40 and -0.30 <= d_ue.x <= 0.30:
                        score = abs(t_ue.z - 1.0) + abs(d_ue.x) * 10.0
                        fine_matches.append((score, (rx, ry, rz), list(pos_ue), list(g_ue), list(t_ue), list(d_ue)))

fine_matches.sort(key=lambda m: m[0])
print(f"Fine matches found: {len(fine_matches)}")

res = []
for m in fine_matches[:10]:
    res.append({
        "score": round(m[0], 2),
        "rot": [round(x, 1) for x in m[1]],
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
