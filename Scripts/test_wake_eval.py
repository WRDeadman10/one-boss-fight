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

def get_sword():
    pb_r = arm.pose.bones['hand_r']
    pb_l = arm.pose.bones['hand_l']
    M_bl_r = arm.matrix_world @ pb_r.matrix
    M_bl_l = arm.matrix_world @ pb_l.matrix
    scale_trans = 100.0 if abs(M_bl_r.translation.z) < 10.0 else 1.0
    M_ue_r = S @ M_bl_r @ S
    pos_r = Vector((M_ue_r[0][3] * scale_trans, M_ue_r[1][3] * scale_trans, M_ue_r[2][3] * scale_trans))
    rot_r = M_ue_r.to_quaternion()
    M_ue_l = S @ M_bl_l @ S
    pos_l = Vector((M_ue_l[0][3] * scale_trans, M_ue_l[1][3] * scale_trans, M_ue_l[2][3] * scale_trans))
    grip = pos_r + rot_r @ v_grip
    tip = pos_r + rot_r @ v_tip
    bdir = (tip - grip).normalized()
    return pos_r, pos_l, grip, tip, bdir

def get_bone_ue(bname):
    pb = arm.pose.bones[bname]
    M_bl = arm.matrix_world @ pb.matrix
    scale_trans = 100.0 if abs(M_bl.translation.z) < 10.0 else 1.0
    M_ue = S @ M_bl @ S
    return Vector((M_ue[0][3] * scale_trans, M_ue[1][3] * scale_trans, M_ue[2][3] * scale_trans))

def apply_dormant_base():
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
    
    set_rot("upperarm_r", (0.0, 30.0, -50.0))
    set_rot("lowerarm_r", (0.0, 0.0, -50.0))
    set_rot("hand_r", (190.0, 5.0, 5.0))
    
    set_rot("upperarm_l", (0.0, 30.0, -50.0))
    set_rot("lowerarm_l", (0.0, 0.0, -50.0))
    set_rot("hand_l", (190.0, -5.0, -5.0))

def apply_combat_ready():
    set_loc("pelvis", (0.0, 0.0, 0.0))
    set_rot("pelvis", (0.0, 0.0, 0.0))
    set_rot("spine_01", (0.0, 0.0, 0.0))
    set_rot("spine_03", (0.0, 0.0, 0.0))
    set_rot("spine_05", (0.0, 0.0, 0.0))
    set_rot("neck_01", (0.0, 0.0, 0.0))
    set_rot("head", (0.0, 0.0, 0.0))
    set_rot("clavicle_r", (0.0, 0.0, 0.0))
    set_rot("upperarm_r", (-15.0, -25.0, 15.0))
    set_rot("lowerarm_r", (-25.0, 0.0, 0.0))
    set_rot("hand_r", (15.0, 0.0, 0.0))
    set_rot("clavicle_l", (0.0, 0.0, 0.0))
    set_rot("upperarm_l", (-15.0, 20.0, -15.0))
    set_rot("lowerarm_l", (-35.0, 0.0, 0.0))
    set_rot("hand_l", (20.0, -15.0, 0.0))
    set_rot("thigh_l", (0.0, 0.0, 5.0))
    set_rot("calf_l", (0.0, 0.0, 0.0))
    set_rot("foot_l", (0.0, 0.0, 0.0))
    set_rot("thigh_r", (0.0, 0.0, -5.0))
    set_rot("calf_r", (0.0, 0.0, 0.0))
    set_rot("foot_r", (0.0, 0.0, 0.0))

# Test Wake frame evaluations:
# Frames: 0, 30 (1.0s), 45 (1.5s), 60 (2.0s), 69 (2.3s), 75 (2.5s), 105 (3.5s)
wake_eval = []

# Arm pull keyframes:
# At f=0..45: hands remain in dormant planted pose!
# At f=45 (1.5s): SwordFree - blade begins sliding up!
# At f=60 (2.0s): hands have lifted sword by ~35 cm, tip Z >= 25 cm, hands dist <= 25 cm.
# At f=69 (2.3s): tip Z >= 45 cm (rose >= 40 cm from 1.5s).
# At f=75 (2.5s): StandUp - pelvis Z >= 73 cm.
# At f=105 (3.5s): exact PhaseRoar F0.

for f in [0, 30, 45, 60, 69, 75, 105]:
    if f <= 45:
        # F0 to F45: Planted pose holds exactly
        t = f / 45.0
        apply_dormant_base()
        # Head raises slightly
        set_rot("neck_01", (0.0, 0.0, -8.0 + 4.0 * t))
        set_rot("head", (0.0, 0.0, -10.0 + 6.0 * t))
    elif f <= 60:
        # F45 to F60 (1.5 to 2.0s): Two-handed vertical pull!
        t = (f - 45.0) / 15.0
        apply_dormant_base()
        set_rot("neck_01", (0.0, 0.0, -4.0 + 2.0 * t))
        set_rot("head", (0.0, 0.0, -4.0 + 2.0 * t))
        
        # Lift arms up while keeping hands together:
        # upperarm_r Z goes from -50 towards -30, lowerarm_r goes towards -30
        set_rot("upperarm_r", (0.0, 30.0 - 5.0 * t, -50.0 + 20.0 * t))
        set_rot("lowerarm_r", (0.0, 0.0, -50.0 + 20.0 * t))
        set_rot("hand_r", (190.0 - 40.0 * t, 5.0, 5.0))
        
        set_rot("upperarm_l", (0.0, 30.0 - 5.0 * t, -50.0 + 20.0 * t))
        set_rot("lowerarm_l", (0.0, 0.0, -50.0 + 20.0 * t))
        set_rot("hand_l", (190.0 - 40.0 * t, -5.0, -5.0))
    elif f <= 75:
        # F60 to F75 (2.0 to 2.5s): Rise up from kneel (StandUp at 2.5s, f=75)
        t = (f - 60.0) / 15.0
        # Pelvis rises from -48.0 to 0.0 (at f=75, pelvis is high: pelvis Z >= 73)
        p_drop = -48.0 * (1.0 - t)
        set_loc("pelvis", (p_drop, 4.0 * (1.0 - t), 0.0))
        set_rot("pelvis", (0.0, 0.0, -4.0 * (1.0 - t)))
        
        # Spine straightens
        set_rot("spine_01", (0.0, 0.0, -5.0 * (1.0 - t)))
        set_rot("spine_03", (0.0, 0.0, -6.0 * (1.0 - t)))
        set_rot("spine_05", (0.0, 0.0, -7.0 * (1.0 - t)))
        set_rot("neck_01", (0.0, 0.0, -2.0 * (1.0 - t)))
        set_rot("head", (0.0, 0.0, -2.0 * (1.0 - t)))
        
        # Legs straighten
        set_rot("thigh_l", (85.0 * (1.0 - t), 0.0, 10.0 * (1.0 - t) + 5.0 * t))
        set_rot("calf_l", (0.0, -120.0 * (1.0 - t), -60.0 * (1.0 - t)))
        set_rot("foot_l", (0.0, -30.0 * (1.0 - t), -30.0 * (1.0 - t)))
        set_rot("thigh_r", (95.0 * (1.0 - t), 0.0, -20.0 * (1.0 - t) - 5.0 * t))
        set_rot("calf_r", (0.0, 120.0 * (1.0 - t), -40.0 * (1.0 - t)))
        set_rot("foot_r", (0.0, 60.0 * (1.0 - t), 30.0 * (1.0 - t)))
        
        # Right arm transitions from pull to combat stance
        # At f=60: uarm (-30), larm (-30), hand (150)
        # At f=75: uarm (-15, -25, 15), larm (-25, 0, 0), hand (15, 0, 0)
        set_rot("upperarm_r", (-15.0 * t, 25.0 * (1.0 - t) - 25.0 * t, -30.0 * (1.0 - t) + 15.0 * t))
        set_rot("lowerarm_r", (-25.0 * t, 0.0, -30.0 * (1.0 - t)))
        set_rot("hand_r", (150.0 * (1.0 - t) + 15.0 * t, 5.0 * (1.0 - t), 5.0 * (1.0 - t)))
        
        # Left arm lets go and moves to combat guard
        set_rot("upperarm_l", (-15.0 * t, 25.0 * (1.0 - t) + 20.0 * t, -30.0 * (1.0 - t) - 15.0 * t))
        set_rot("lowerarm_l", (-35.0 * t, 0.0, -30.0 * (1.0 - t)))
        set_rot("hand_l", (150.0 * (1.0 - t) + 20.0 * t, -5.0 * (1.0 - t) - 15.0 * t, -5.0 * (1.0 - t)))
    else:
        # F75 to F105 (2.5 to 3.5s): Settle cleanly into PhaseRoar F0
        apply_combat_ready()
    
    bpy.context.view_layer.update()
    pos_r, pos_l, grip, tip, bdir = get_sword()
    pel_z = get_bone_ue("pelvis").z
    wake_eval.append({
        "f": f,
        "t": round(f / 30.0, 2),
        "tip_z": round(tip.z, 2),
        "grip": [round(x, 1) for x in grip],
        "tip": [round(x, 1) for x in tip],
        "bdir": [round(x, 2) for x in bdir],
        "hand_r": [round(x, 1) for x in pos_r],
        "hand_l": [round(x, 1) for x in pos_l],
        "hands_dist": round((pos_r - pos_l).length, 1),
        "pelvis_z": round(pel_z, 1)
    })

result = wake_eval
"""

res = execute_blender(code)
import json
print(json.dumps(res, indent=2))
