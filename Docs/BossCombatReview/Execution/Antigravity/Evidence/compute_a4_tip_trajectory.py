"""
compute_a4_tip_trajectory.py
Offline forward kinematic trajectory calculation for A4 Low Sweep (CI-P0-A-01 / CAP-02).
Tool: Blender 5.1.2 (headless) / Python 3.11+
Coordinate System: Blender Right-Handed (Z-Up, Y-Forward, X-Right).
Unit Convention: Centimeters (cm) throughout.

Provenance & Geometry Parameters:
- Animation Clip: Import/Boss01/Animations/AN_Boss01_A4_LowSweep.fbx (54 frames @ 30 fps)
- Weapon Static Mesh: Import/Boss01/Weapons/SM_Boss01_Greatsword.fbx
  * Authored unscaled mesh bounds length: 163.30 cm (tip at local Z = +163.30 cm)
  * Runtime scaling factor: 1.50x
  * Scaled blade reach along sword axis: 163.30 cm * 1.50 = 244.95 cm
- Attachment Socket: HeavySwordSocket_R on hand_r (from Source/OneBossFight/Player/RPGBossLook.h:42)
  * Translation relative to hand_r: (-13.9, 2.6, 4.9) cm
  * Rotation: Pitch -28.0 deg (Y), Yaw 168.8 deg (Z), Roll 12.8 deg (X)
  * Local distance from socket origin to sword tip: exactly 244.95 cm
  * Local distance from hand_r origin to sword tip: 243.11 cm

Unit Self-Test:
- Every frame asserts that the transformed 3D Euclidean distance from the socket origin to
  the visible sword tip equals 244.95 cm (+/- 0.05 cm floating-point tolerance).
- Every frame asserts that the transformed 3D Euclidean distance from the hand_r bone to
  the visible sword tip equals 243.11 cm (+/- 0.05 cm floating-point tolerance).
"""
import bpy
import os
import math
import mathutils
import json

def find_repo_root():
    curr = os.path.dirname(os.path.abspath(__file__))
    while curr and os.path.dirname(curr) != curr:
        if os.path.exists(os.path.join(curr, "OneBossFight.uproject")):
            return curr
        curr = os.path.dirname(curr)
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", ".."))

ROOT_DIR = find_repo_root()
ANIM_FBX = os.path.join(ROOT_DIR, "Import", "Boss01", "Animations", "AN_Boss01_A4_LowSweep.fbx")
OUT_JSON = os.path.join(ROOT_DIR, "Docs", "BossCombatReview", "Execution", "Antigravity", "Evidence", "a4_offline_tip_trajectory.json")

# Clean scene setup
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1.0

# Import animation FBX
bpy.ops.import_scene.fbx(filepath=ANIM_FBX)
arm = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE'][0]
hand_r = arm.pose.bones['hand_r']

# Socket & Weapon parameters (all in cm)
SWORD_UNSCALED_LENGTH_CM = 163.30
SWORD_SCALE = 1.50
SWORD_SCALED_LENGTH_CM = SWORD_UNSCALED_LENGTH_CM * SWORD_SCALE # 244.95 cm

# Relative socket transform from RPGBossLook.h:42:
# Translation: (-13.9, 2.6, 4.9) cm
# Rotation: Pitch -28, Yaw 168.8, Roll 12.8 deg
socket_loc_cm = mathutils.Vector((-13.9, 2.6, 4.9))

rot_x = mathutils.Matrix.Rotation(math.radians(12.8), 4, 'X')
rot_y = mathutils.Matrix.Rotation(math.radians(-28.0), 4, 'Y')
rot_z = mathutils.Matrix.Rotation(math.radians(168.8), 4, 'Z')
socket_rot = rot_z @ rot_y @ rot_x

tip_in_socket_cm = mathutils.Vector((0.0, 0.0, SWORD_SCALED_LENGTH_CM))
tip_in_hand_cm = socket_loc_cm + (socket_rot.to_3x3() @ tip_in_socket_cm)

# Verify local un-transformed vectors
expected_sock_dist = SWORD_SCALED_LENGTH_CM
expected_hand_dist = tip_in_hand_cm.length # 243.11 cm
assert abs((tip_in_hand_cm - socket_loc_cm).length - expected_sock_dist) < 1e-4, "Local socket-to-tip dist failed"
assert abs(expected_hand_dist - 243.11) < 0.05, f"Local hand-to-tip dist expected ~243.11 cm, got {expected_hand_dist}"

trajectory = []

for f in range(1, 55):
    bpy.context.scene.frame_set(f)
    bpy.context.view_layer.update()
    t_sec = (f - 1) / 30.0
    
    # Pose bone matrix hand_r.matrix is relative to the armature root in centimeters
    b_mat = hand_r.matrix
    
    hand_pos = b_mat.translation
    sock_pos = b_mat @ socket_loc_cm
    tip_pos = b_mat @ tip_in_hand_cm
    
    d_sock = (tip_pos - sock_pos).length
    d_hand = (tip_pos - hand_pos).length
    
    # REQUIRED UNIT SELF-TEST: strict assertion of 244.95 cm blade length on every frame
    assert abs(d_sock - expected_sock_dist) < 0.05, f"Frame {f} self-test failed: d_sock={d_sock:.4f} cm"
    assert abs(d_hand - expected_hand_dist) < 0.05, f"Frame {f} self-test failed: d_hand={d_hand:.4f} cm"
    
    d_h = math.hypot(tip_pos.x, tip_pos.y)
    
    trajectory.append({
        "frame_1based": f,
        "frame_0based": f - 1,
        "time_s": round(t_sec, 3),
        "hand_cm": [round(hand_pos.x, 2), round(hand_pos.y, 2), round(hand_pos.z, 2)],
        "socket_cm": [round(sock_pos.x, 2), round(sock_pos.y, 2), round(sock_pos.z, 2)],
        "tip_cm": [round(tip_pos.x, 2), round(tip_pos.y, 2), round(tip_pos.z, 2)],
        "tip_to_socket_dist_cm": round(d_sock, 2),
        "tip_to_hand_dist_cm": round(d_hand, 2),
        "tip_horizontal_reach_cm": round(d_h, 2),
        "tip_height_above_armature_origin_cm": round(tip_pos.z, 2)
    })

with open(OUT_JSON, "w", encoding="utf-8") as fp:
    json.dump(trajectory, fp, indent=2)

print(f"Computed trajectory for {len(trajectory)} frames and saved to {OUT_JSON}")
print("ALL 54 FRAMES PASSED UNIT SELF-TEST ASSERTIONS (tip_to_socket == 244.95 cm, tip_to_hand == 243.11 cm)")
print("\nFrames with negative tip height (below armature origin Z=0):")
for p in trajectory:
    if p["tip_height_above_armature_origin_cm"] < 0:
        print(f"Fr {p['frame_1based']:2d} (t={p['time_s']:.3f}s): tip_z={p['tip_height_above_armature_origin_cm']:6.1f} cm, d_h={p['tip_horizontal_reach_cm']:5.1f} cm, socket_z={p['socket_cm'][2]:5.1f} cm")
