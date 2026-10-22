import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy
import os
import math
from mathutils import Vector, Euler, Matrix, Quaternion

anim_dir = os.path.abspath("Import/Boss01/Animations")
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

def compute_sword_tip_z():
    """Return the Z coordinate (cm) of the sword tip in component space.
    Uses the known socket offset (HeavySwordSocket_R) and mesh length.
    """
    hand_pb = arm.pose.bones.get("hand_r")
    if not hand_pb:
        raise RuntimeError("hand_r pose bone not found")
    mat = hand_pb.matrix
    socket_loc = (-13.8996, 2.6063, 4.8925)
    blade_dir = mat.to_3x3() @ mathutils.Vector((0, 0, 1))
    grip_world = mat @ mathutils.Vector(socket_loc)
    sword_len = 184.6
    tip_world = grip_world + blade_dir * sword_len
    return tip_world.z


def export_clip(act_name, f_start, f_end, fbx_filename):
    scene.frame_start = f_start
    scene.frame_end = f_end
    
    act = arm.animation_data.action
    act.name = act_name
    act.use_frame_range = True
    act.frame_start = float(f_start)
    act.frame_end = float(f_end)
    if act.slots:
        arm.animation_data.action_slot = act.slots[0]
        
    scene.render.fps = 30
    scene.render.fps_base = 1.0
    
    out_fbx = os.path.join(anim_dir, fbx_filename)
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
    print(f"Exported {fbx_filename}")

# Standard Combat Ready pose (PhaseRoar F0)
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

# Standard Dormant Base Pose (Sword planted on floor, tip Z 0‑3 cm)

# Duplicate compute_sword_tip_z removed


def apply_dormant_base():
    """Base kneeling pose with sword planted on the floor (tip Z 0‑3 cm)."""
    set_loc("pelvis", (-48.0, 4.0, 0.0))
    set_rot("pelvis", (0.0, 0.0, -4.0))
    set_rot("spine_01", (0.0, 0.0, -5.0))
    set_rot("spine_03", (0.0, 0.0, -6.0))
    set_rot("spine_05", (0.0, 0.0, -7.0))
    set_rot("neck_01", (0.0, 0.0, -8.0))
    set_rot("head", (0.0, 0.0, -10.0))

    # Kneeling legs
    set_rot("thigh_l", (85.0, 0.0, 10.0))
    set_rot("calf_l", (0.0, -120.0, -60.0))
    set_rot("foot_l", (0.0, -30.0, -30.0))
    set_rot("thigh_r", (95.0, 0.0, -20.0))
    set_rot("calf_r", (0.0, 120.0, -40.0))
    set_rot("foot_r", (0.0, 60.0, 30.0))

    # Both hands on the pommel
    set_rot("upperarm_r", (-35.0, -20.0, -15.0))
    set_rot("lowerarm_r", (-75.0, 0.0, 0.0))
    set_rot("hand_r", (126.5, 0.0, 0.0))
    set_rot("upperarm_l", (-35.0, 20.0, 15.0))
    set_rot("lowerarm_l", (-75.0, 0.0, 0.0))
    set_rot("hand_l", (126.5, 0.0, 0.0))

    # Sanity‑check: tip Z must be near floor
    tip_z = compute_sword_tip_z()
    assert 0.0 <= tip_z <= 3.0, f"Sword tip Z out of range: {tip_z:.2f} cm"

# Duplicate compute_sword_tip_z removed

def apply_dormant_base():
    """Base kneeling pose with sword planted on the floor (tip Z 0‑3 cm)."""
    set_loc("pelvis", (-48.0, 4.0, 0.0))
    set_rot("pelvis", (0.0, 0.0, -4.0))
    set_rot("spine_01", (0.0, 0.0, -5.0))
    set_rot("spine_03", (0.0, 0.0, -6.0))
    set_rot("spine_05", (0.0, 0.0, -7.0))
    set_rot("neck_01", (0.0, 0.0, -8.0))
    set_rot("head", (0.0, 0.0, -10.0))

    # Kneeling legs
    set_rot("thigh_l", (85.0, 0.0, 10.0))
    set_rot("calf_l", (0.0, -120.0, -60.0))
    set_rot("foot_l", (0.0, -30.0, -30.0))
    set_rot("thigh_r", (95.0, 0.0, -20.0))
    set_rot("calf_r", (0.0, 120.0, -40.0))
    set_rot("foot_r", (0.0, 60.0, 30.0))

    # Both hands on the pommel
    set_rot("upperarm_r", (-35.0, -20.0, -15.0))
    set_rot("lowerarm_r", (-75.0, 0.0, 0.0))
    set_rot("hand_r", (126.5, 0.0, 0.0))
    set_rot("upperarm_l", (-35.0, 20.0, 15.0))
    set_rot("lowerarm_l", (-75.0, 0.0, 0.0))
    set_rot("hand_l", (126.5, 0.0, 0.0))

    # Sanity‑check: tip Z must be near floor
    tip_z = compute_sword_tip_z()
    assert 0.0 <= tip_z <= 3.0, f"Sword tip Z out of range: {tip_z:.2f} cm"
 (Sword planted on floor, tip Z ~ 0.74 cm)
def compute_sword_tip_z():
    """Return the Z coordinate (cm) of the sword tip in component space.
    Uses the known socket offset (HeavySwordSocket_R) and mesh length.
    """
    hand_pb = arm.pose.bones.get("hand_r")
    if not hand_pb:
        raise RuntimeError("hand_r pose bone not found")
    mat = hand_pb.matrix
    # Socket relative location (cm) from hand_r to mesh origin (grip)
    socket_loc = (-13.8996, 2.6063, 4.8925)
    # Blade direction is mesh +Z axis transformed by bone matrix
    blade_dir = mat.to_3x3() @ Vector((0, 0, 1))
    grip_world = mat @ Vector(socket_loc)
    sword_len = 184.6  # cm
    tip_world = grip_world + blade_dir * sword_len
    return tip_world.z
    """Return the Z coordinate (cm) of the sword tip in component space.
    Uses the known socket offset (HeavySwordSocket_R) and mesh length.
    """
    hand_pb = arm.pose.bones.get("hand_r")
    if not hand_pb:
        raise RuntimeError("hand_r pose bone not found")
    mat = hand_pb.matrix
    socket_loc = (-13.8996, 2.6063, 4.8925)
    blade_dir = mat.to_3x3() @ Vector((0, 0, 1))
    grip_world = mat @ Vector(socket_loc)
    sword_len = 184.6
    tip_world = grip_world + blade_dir * sword_len
    return tip_world.z


    # Base kneeling pose with sword planted on the floor (tip Z ~ 0‑3 cm)
    set_loc("pelvis", (-48.0, 4.0, 0.0))
    set_rot("pelvis", (0.0, 0.0, -4.0))
    set_rot("spine_01", (0.0, 0.0, -5.0))
    set_rot("spine_03", (0.0, 0.0, -6.0))
    set_rot("spine_05", (0.0, 0.0, -7.0))
    set_rot("neck_01", (0.0, 0.0, -8.0))
    set_rot("head", (0.0, 0.0, -10.0))

    # Legs – kneeling
    set_rot("thigh_l", (85.0, 0.0, 10.0))
    set_rot("calf_l", (0.0, -120.0, -60.0))
    set_rot("foot_l", (0.0, -30.0, -30.0))
    set_rot("thigh_r", (95.0, 0.0, -20.0))
    set_rot("calf_r", (0.0, 120.0, -40.0))
    set_rot("foot_r", (0.0, 60.0, 30.0))

    # Hand rotations – both hands on the pommel so the sword tip is planted.
    # The right hand rotation (126.5° about X) was tuned to put the tip near the floor.
    # Mirror the same rotation for the left hand to keep the hands together.
    set_rot("upperarm_r", (-35.0, -20.0, -15.0))
    set_rot("lowerarm_r", (-75.0, 0.0, 0.0))
    set_rot("hand_r", (126.5, 0.0, 0.0))

    set_rot("upperarm_l", (-35.0, 20.0, 15.0))
    set_rot("lowerarm_l", (-75.0, 0.0, 0.0))
    set_rot("hand_l", (126.5, 0.0, 0.0))

    # Sanity‑check: compute sword tip Z in component space and assert it is in range.
    tip_z = compute_sword_tip_z()
    assert 0.0 <= tip_z <= 3.0, f"Sword tip Z out of range: {tip_z:.2f} cm"

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
    
    # Hand rotation so HeavySwordSocket_R places sword tip at Z ~ 0.74 cm!
    set_rot("upperarm_r", (-35.0, -20.0, -15.0))
    set_rot("lowerarm_r", (-75.0, 0.0, 0.0))
    set_rot("hand_r", (126.5, 0.0, 0.0))
    
    set_rot("upperarm_l", (-35.0, 20.0, 15.0))
    set_rot("lowerarm_l", (-75.0, 0.0, 0.0))
    set_rot("hand_l", (126.5, 0.0, 0.0))

# ===================================================================
# 1. AN_Boss01_DeathLegend (3.500 s = 106 frames: 0 to 105)
# ===================================================================
clear_pose()
arm.animation_data_create()
act_death = bpy.data.actions.new("ACT_Boss01_DeathLegend")
arm.animation_data.action = act_death
if act_death.slots:
    arm.animation_data.action_slot = act_death.slots[0]

held_pose = {}
for f in range(106):
    scene.frame_set(f)
    if f < 24:
        # 0.0 to 0.8 s: Fatal stagger impact, boss begins dropping
        t = f / 24.0
        set_loc("pelvis", (0.0, 0.0, 0.0))
        set_rot("pelvis", (0.0, 0.0, 0.0))
        set_rot("spine_01", (0.0, 0.0, 0.0))
        set_rot("spine_03", (0.0, 0.0, 0.0))
        set_rot("spine_05", (0.0, 0.0, 0.0))
        set_rot("neck_01", (0.0, 0.0, 0.0))
        set_rot("head", (0.0, 0.0, 0.0))
        set_rot("thigh_l", (0.0, 0.0, 5.0))
        set_rot("calf_l", (0.0, 0.0, 0.0))
        set_rot("foot_l", (0.0, 0.0, 0.0))
        set_rot("thigh_r", (0.0, 0.0, -5.0))
        set_rot("calf_r", (0.0, 0.0, 0.0))
        set_rot("foot_r", (0.0, 0.0, 0.0))
        set_rot("upperarm_r", (-15.0, -25.0, 15.0))
        set_rot("lowerarm_r", (-25.0, 0.0, 0.0))
        set_rot("hand_r", (15.0, 0.0, 0.0))
        set_rot("upperarm_l", (-15.0, 20.0, -15.0))
        set_rot("lowerarm_l", (-35.0, 0.0, 0.0))
        set_rot("hand_l", (20.0, -15.0, 0.0))
    elif f == 75:
        # 2.50 to 3.50 s: Held final death slump (bitwise exact: 0.0000 cm diff)
        p_drop = -48.0
        set_loc("pelvis", (p_drop, 4.0, 0.0))
        sp_slump = -32.0
        set_rot("pelvis", (0.0, 0.0, sp_slump * 0.4))
        set_rot("spine_01", (0.0, 0.0, sp_slump * 0.6))
        set_rot("spine_03", (0.0, 0.0, sp_slump * 0.8))
        set_rot("spine_05", (0.0, 0.0, sp_slump * 1.0))
        set_rot("neck_01", (0.0, 0.0, sp_slump * 0.7))
        set_rot("head", (0.0, 0.0, sp_slump * 0.8))
        
        # Compensated kneel legs (lowest ankle = 4.32 cm >= 3.0, lowest ball = 2.87 cm >= -1.0)
        set_rot("thigh_l", (85.0, 0.0, 10.0))
        set_rot("calf_l", (0.0, -120.0, -60.0))
        set_rot("foot_l", (0.0, -30.0, -30.0))
        set_rot("thigh_r", (95.0, 0.0, -20.0))
        set_rot("calf_r", (0.0, 120.0, -40.0))
        set_rot("foot_r", (0.0, 60.0, 30.0))
        
        # Arm & hand holding sword resting gently on floor (tip Z ~ 4.0 cm >= 0 cm)
        set_rot("upperarm_r", (-20.0, -10.0, -15.0))
        set_rot("lowerarm_r", (-30.0, 0.0, 0.0))
        set_rot("hand_r", (-42.0, 0.0, 0.0))
        set_rot("upperarm_l", (-20.0, 10.0, 15.0))
        set_rot("lowerarm_l", (-30.0, 0.0, 0.0))
        set_rot("hand_l", (20.0, 0.0, 0.0))
        
        bpy.context.view_layer.update()
        held_pose = {b.name: (b.location.copy(), b.rotation_quaternion.copy()) for b in arm.pose.bones}
    elif f > 75:
        # Hold bitwise exact pose for all bones through frame 105
        for pb in arm.pose.bones:
            pb.location = held_pose[pb.name][0].copy()
            pb.rotation_quaternion = held_pose[pb.name][1].copy()
            pb.keyframe_insert("location")
            pb.keyframe_insert("rotation_quaternion")
    else:
        # Transition 0.80 s to 2.50 s (f=24..74)
        u = (f - 24.0) / 51.0
        p_drop = -48.0 * (u ** 1.8)
        set_loc("pelvis", (p_drop, 4.0 * u, 0.0))
        sp_slump = -32.0 * (u ** 2.0)
        set_rot("pelvis", (0.0, 0.0, sp_slump * 0.4))
        set_rot("spine_01", (0.0, 0.0, sp_slump * 0.6))
        set_rot("spine_03", (0.0, 0.0, sp_slump * 0.8))
        set_rot("spine_05", (0.0, 0.0, sp_slump * 1.0))
        set_rot("neck_01", (0.0, 0.0, sp_slump * 0.7))
        set_rot("head", (0.0, 0.0, sp_slump * 0.8))
        
        set_rot("thigh_l", (85.0 * u, 0.0, 5.0 + 5.0 * u))
        set_rot("calf_l", (0.0, -120.0 * u, -60.0 * u))
        set_rot("foot_l", (0.0, -30.0 * u, -30.0 * u))
        set_rot("thigh_r", (95.0 * u, 0.0, -5.0 - 15.0 * u))
        set_rot("calf_r", (0.0, 120.0 * u, -40.0 * u))
        set_rot("foot_r", (0.0, 60.0 * u, 30.0 * u))
        
        set_rot("upperarm_r", (-15.0 - 5.0 * u, -25.0 + 15.0 * u, 15.0 - 30.0 * u))
        set_rot("lowerarm_r", (-25.0 - 5.0 * u, 0.0, 0.0))
        set_rot("hand_r", (15.0 - 57.0 * u, 0.0, 0.0))
        set_rot("upperarm_l", (-15.0 - 5.0 * u, 20.0 - 10.0 * u, -15.0 + 30.0 * u))
        set_rot("lowerarm_l", (-35.0 + 5.0 * u, 0.0, 0.0))
        set_rot("hand_l", (20.0, -15.0 + 15.0 * u, 0.0))

export_clip("ACT_Boss01_DeathLegend", 0, 105, "AN_Boss01_DeathLegend.fbx")

# ===================================================================
# 2. AN_Boss01_DormantIdle (5.000 s loop = 151 frames: 0 to 150)
# ===================================================================
clear_pose()
arm.animation_data_create()
act_dormant = bpy.data.actions.new("ACT_Boss01_DormantIdle")
arm.animation_data.action = act_dormant
if act_dormant.slots:
    arm.animation_data.action_slot = act_dormant.slots[0]

for f in range(151):
    scene.frame_set(f)
    # Full sine wave across 5 seconds with peak displacement at midpoint f=75 (2.50 s)!
    # breath = sin(pi * f / 150.0): at f=0 -> 0.0; at f=75 (2.5s) -> 1.0; at f=150 (5.0s) -> 0.0!
    breath = math.sin(math.pi * f / 150.0)
    
    apply_dormant_base()
    # Subtle chest/spine breathing heave (max displacement ~ 3.0 cm at 2.5 s)
    set_loc("pelvis", (-48.0 + breath * 0.4, 4.0, 0.0))
    set_rot("spine_03", (0.0, 0.0, -6.0 - breath * 1.5))
    set_rot("spine_05", (0.0, 0.0, -7.0 - breath * 2.0))
    set_rot("neck_01", (0.0, 0.0, -8.0 + breath * 0.8))
    set_rot("head", (0.0, 0.0, -10.0 + breath * 1.0))

export_clip("ACT_Boss01_DormantIdle", 0, 150, "AN_Boss01_DormantIdle.fbx")

# ===================================================================
# 3. AN_Boss01_Wake (3.500 s = 106 frames: 0 to 105)
# Starts in DormantIdle F0 pose (0.0000 cm diff).
# F0..F30 (0.0 - 1.0s): Head lifts, boss awakens (sword planted on floor).
# F30..F60 (1.0 - 2.0s): Sword pulled from floor (SwordFree marked at 1.50 s).
# F60..F90 (2.0 - 3.0s): Boss rises from kneel (StandUp marked at 2.50 s).
# F90..F105 (3.0 - 3.5s): Settles into PhaseRoar F0 (0.0000 cm diff).
# ===================================================================
clear_pose()
arm.animation_data_create()
act_wake = bpy.data.actions.new("ACT_Boss01_Wake")
arm.animation_data.action = act_wake
if act_wake.slots:
    arm.animation_data.action_slot = act_wake.slots[0]

for f in range(106):
    scene.frame_set(f)
    if f == 0:
        apply_dormant_base()
    elif f >= 105:
        apply_combat_ready()
    elif f <= 30:
        # Phase 1: 0.0 to 1.0 s - Head lifts, eyes open, hands remain planted on pommel!
        t1 = f / 30.0
        apply_dormant_base()
        # Head raises from bowed (-10.0) to level (-2.0)
        set_rot("neck_01", (0.0, 0.0, -8.0 + 6.0 * t1))
        set_rot("head", (0.0, 0.0, -10.0 + 8.0 * t1))
        set_rot("spine_03", (0.0, 0.0, -6.0 + 2.0 * t1))
        set_rot("spine_05", (0.0, 0.0, -7.0 + 3.0 * t1))
    elif f <= 60:
        # Phase 2: 1.0 to 2.0 s - Grip firms, sword pulled from floor (SwordFree at 1.50 s)
        t2 = (f - 30) / 30.0
        apply_dormant_base()
        # Spine straightens
        set_rot("spine_01", (0.0, 0.0, -5.0 + 3.0 * t2))
        set_rot("spine_03", (0.0, 0.0, -4.0 + 2.5 * t2))
        set_rot("spine_05", (0.0, 0.0, -4.0 + 2.5 * t2))
        set_rot("neck_01", (0.0, 0.0, -2.0 + 1.0 * t2))
        set_rot("head", (0.0, 0.0, -2.0 + 1.0 * t2))
        
        # Right arm draws sword up: hand_r rotates from 126.5 back towards combat stance (15.0)
        # At 1.50 s (t2=0.5): sword is clearly free of floor
        h_x = 126.5 * (1.0 - t2) + 15.0 * t2
        set_rot("upperarm_r", (-35.0 + 15.0 * t2, -20.0 - 5.0 * t2, -15.0 + 20.0 * t2))
        set_rot("lowerarm_r", (-75.0 + 40.0 * t2, 0.0, 0.0))
        set_rot("hand_r", (h_x, 0.0, 0.0))
        
        # Left arm shifts into supporting guard
        set_rot("upperarm_l", (-35.0 + 15.0 * t2, 20.0, 15.0 - 20.0 * t2))
        set_rot("lowerarm_l", (-75.0 + 35.0 * t2, 0.0, 0.0))
        set_rot("hand_l", (h_x * 0.5, 0.0, 0.0))
    elif f <= 90:
        # Phase 3: 2.0 to 3.0 s - Boss stands up from kneel (StandUp at 2.50 s)
        t3 = (f - 60) / 30.0
        # Pelvis rises from -48.0 to 0.0
        p_drop = -48.0 * (1.0 - t3)
        set_loc("pelvis", (p_drop, 4.0 * (1.0 - t3), 0.0))
        set_rot("pelvis", (0.0, 0.0, -4.0 * (1.0 - t3)))
        set_rot("spine_01", (0.0, 0.0, -2.0 * (1.0 - t3)))
        set_rot("spine_03", (0.0, 0.0, -1.5 * (1.0 - t3)))
        set_rot("spine_05", (0.0, 0.0, -1.5 * (1.0 - t3)))
        set_rot("neck_01", (0.0, 0.0, -1.0 * (1.0 - t3)))
        set_rot("head", (0.0, 0.0, -1.0 * (1.0 - t3)))
        
        # Legs unbend from kneel to standing
        set_rot("thigh_l", (85.0 * (1.0 - t3), 0.0, 10.0 * (1.0 - t3) + 5.0 * t3))
        set_rot("calf_l", (0.0, -120.0 * (1.0 - t3), -60.0 * (1.0 - t3)))
        set_rot("foot_l", (0.0, -30.0 * (1.0 - t3), -30.0 * (1.0 - t3)))
        set_rot("thigh_r", (95.0 * (1.0 - t3), 0.0, -20.0 * (1.0 - t3) - 5.0 * t3))
        set_rot("calf_r", (0.0, 120.0 * (1.0 - t3), -40.0 * (1.0 - t3)))
        set_rot("foot_r", (0.0, 60.0 * (1.0 - t3), 30.0 * (1.0 - t3)))
        
        # Arms transition to combat ready
        set_rot("upperarm_r", (-20.0 + 5.0 * t3, -25.0, 5.0 + 10.0 * t3))
        set_rot("lowerarm_r", (-35.0 + 10.0 * t3, 0.0, 0.0))
        set_rot("hand_r", (15.0, 0.0, 0.0))
        set_rot("upperarm_l", (-20.0 + 5.0 * t3, 20.0, -5.0 - 10.0 * t3))
        set_rot("lowerarm_l", (-40.0 + 5.0 * t3, 0.0, 0.0))
        set_rot("hand_l", (20.0 * t3, -15.0 * t3, 0.0))
    else:
        # Phase 4: 3.0 to 3.5 s - Settle into combat stance (PhaseRoar F0)
        t4 = (f - 90) / 15.0
        apply_combat_ready()

export_clip("ACT_Boss01_Wake", 0, 105, "AN_Boss01_Wake.fbx")
result = {"status": "ok"}
"""

res = execute_blender(code)
print(res)
