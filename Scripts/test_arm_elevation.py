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

pb_r = arm.pose.bones['hand_r']
pb_p = pb_r.parent
b = arm.data.bones['hand_r']
b_p = b.parent
M_rest_rel = b_p.matrix_local.inverted() @ b.matrix_local

# Test arm elevation adjustments:
# Test upperarm_r Z from -50 to -35, and lowerarm_r Z from -50 to -30
matches = []

for u_z in [-50, -45, -40, -35]:
    for u_y in [25, 30, 35]:
        set_rot("upperarm_r", (0, u_y, u_z))
        for l_z in [-50, -45, -40, -35, -30]:
            set_rot("lowerarm_r", (0, 0, l_z))
            set_rot("hand_r", (0, 0, 0))
            bpy.context.view_layer.update()
            
            M_parent = pb_p.matrix.copy()
            scale_trans = 100.0 if abs(M_parent.translation.z) < 10.0 else 1.0
            
            # Now fine sweep around (180, 10, -20)
            for drx in range(-30, 31, 5):
                for dry in range(-20, 21, 5):
                    for drz in range(-30, 31, 5):
                        rx = 180 + drx
                        ry = 10 + dry
                        rz = -20 + drz
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
                                if -25.0 <= pos_ue.x <= 25.0 and 20.0 <= pos_ue.y <= 70.0 and 75.0 <= pos_ue.z <= 125.0:
                                    score = abs(t_ue.z - 1.2) + abs(d_ue.x) * 10.0
                                    matches.append((score, (0, u_y, u_z), (0, 0, l_z), (rx, ry, rz), list(pos_ue), list(g_ue), list(t_ue), list(d_ue)))

matches.sort(key=lambda m: m[0])
print(f"Total matching poses: {len(matches)}")
res = []
for m in matches[:10]:
    res.append({
        "score": round(m[0], 2),
        "uarm_r": m[1],
        "larm_r": m[2],
        "hand_r_rot": m[3],
        "hand_r_pos": [round(x, 1) for x in m[4]],
        "grip": [round(x, 1) for x in m[5]],
        "tip": [round(x, 1) for x in m[6]],
        "bdir": [round(x, 2) for x in m[7]]
    })

result = res
"""

res = execute_blender(code)
import json
print(json.dumps(res, indent=2))
