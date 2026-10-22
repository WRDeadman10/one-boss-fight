import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy, os, math
from mathutils import Vector, Euler, Matrix, Quaternion

anim_dir = os.path.abspath("Import/Boss01/Animations")

# Formula from summary:
# v_grip = (-13.8996, 2.6063, 4.8925)
# u_blade = (-0.49286, -0.12920, 0.86044)
# v_tip = v_grip + 163.3 * u_blade
v_grip = Vector((-13.8996, 2.6063, 4.8925))
v_tip = Vector((-94.39, -18.50, 145.39))

S = Matrix.Diagonal(Vector((1.0, -1.0, 1.0, 1.0)))

clips_to_test = [
    ("AN_Boss01_PhaseRoar.fbx", [
        (0.0, (-74, 12, 114), (-98, 173, 126), (-0.14, 0.99, 0.07), (-65, 2, 121), (34, 27, 104)),
        (0.7, (-80, -20, 125), (-163, 59, 241), (-0.51, 0.48, 0.71), (-65, -24, 123), (27, 32, 123))
    ]),
    ("AN_Boss01_StaggerDown.fbx", [
        (0.0, (-78, 9, 74), (-179, 50, 195), (-0.62, 0.25, 0.74), (-65, 0, 72), (44, 20, 57))
    ])
]

res_table = []
for fbx_name, checks in clips_to_test:
    fbx_p = os.path.join(anim_dir, fbx_name)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx_p)
    arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    
    for t_sec, exp_g, exp_t, exp_d, exp_hr, exp_hl in checks:
        f = int(round(t_sec * 30.0))
        bpy.context.scene.frame_set(f + 1)
        bpy.context.view_layer.update()
        
        pb_r = arm.pose.bones['hand_r']
        pb_l = arm.pose.bones['hand_l']
        
        # M_bone,UE = S @ M_bone,BL @ S
        # Note: In Blender, positions on imported FBX: let's check if translations are in meters (scale 0.01) or cm (scale 1.0)
        M_bl_r = arm.matrix_world @ pb_r.matrix
        M_bl_l = arm.matrix_world @ pb_l.matrix
        
        # Check scale
        scale_trans = 100.0 if abs(M_bl_r.translation.z) < 10.0 else 1.0
        
        M_ue_r = S @ M_bl_r @ S
        pos_ue_r = Vector((M_ue_r[0][3] * scale_trans, M_ue_r[1][3] * scale_trans, M_ue_r[2][3] * scale_trans))
        rot_ue_r = M_ue_r.to_quaternion()
        
        M_ue_l = S @ M_bl_l @ S
        pos_ue_l = Vector((M_ue_l[0][3] * scale_trans, M_ue_l[1][3] * scale_trans, M_ue_l[2][3] * scale_trans))
        
        g_ue = pos_ue_r + rot_ue_r @ v_grip
        t_ue = pos_ue_r + rot_ue_r @ v_tip
        d_ue = (t_ue - g_ue).normalized()
        
        res_table.append({
            "clip": f"{fbx_name} @ {t_sec:.2f}s",
            "calc_grip": [round(x, 1) for x in g_ue],
            "exp_grip": list(exp_g),
            "err_grip": round((g_ue - Vector(exp_g)).length, 2),
            "calc_tip": [round(x, 1) for x in t_ue],
            "exp_tip": list(exp_t),
            "err_tip": round((t_ue - Vector(exp_t)).length, 2),
            "calc_dir": [round(x, 2) for x in d_ue],
            "exp_dir": list(exp_d),
            "calc_hr": [round(x, 1) for x in pos_ue_r],
            "exp_hr": list(exp_hr),
            "calc_hl": [round(x, 1) for x in pos_ue_l],
            "exp_hl": list(exp_hl)
        })

result = res_table
"""

res = execute_blender(code)
import json
print(json.dumps(res, indent=2))
