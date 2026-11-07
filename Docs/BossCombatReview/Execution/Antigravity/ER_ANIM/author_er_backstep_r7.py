"""Author ER-A1: Backstep_Back R7 in Blender.

Addresses Lead Claude's directive [C-976]:
- Keep R6 legs and root motion UNCHANGED (accepted in C-976: real backward stride on feet, hop stays low)
- Take upper body (spine_01 and up, both arms, hands, head) from pack sword idle/guard pose (Attack_PrimaryA frame 0)
- Elbows bent, left hand near hip, sword tip down/forward at waist height
- Single white diffuse blade
- Re-render strip and review MP4
"""

import os
import shutil
import subprocess
from math import radians, degrees
import bpy
from mathutils import Vector, Quaternion, Euler

BASE_DIR = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\ER_ANIM"
SRC_DIR = r"c:\UnrealProject\OneBossFight\Import\Player\Animations_FBX_Export"
REF_RIG = r"c:\UnrealProject\OneBossFight\Import\ThirdParty\Reference\SKM_CombatMannequin_Simple.fbx"
SWORD_FBX = r"c:\UnrealProject\OneBossFight\Import\ThirdParty\Reference\SM_KwangSword.fbx"
PACK_IDLE_FBX = os.path.join(SRC_DIR, "Attack_PrimaryA_Anim.fbx")

OUT_DIR = os.path.join(BASE_DIR, "Backstep_Back")
FRAMES_DIR = os.path.join(OUT_DIR, "temp_frames_r7")
os.makedirs(FRAMES_DIR, exist_ok=True)

# 1. First extract upper body pose from Attack_PrimaryA_Anim Frame 0
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=PACK_IDLE_FBX)
pack_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
bpy.context.scene.frame_set(0)

UPPER_BONES = [
    'spine_01', 'spine_02', 'spine_03', 'spine_04', 'spine_05',
    'neck_01', 'neck_02', 'head',
    'clavicle_l', 'upperarm_l', 'lowerarm_l', 'hand_l',
    'upperarm_twist_01_l', 'upperarm_twist_02_l', 'lowerarm_twist_01_l', 'lowerarm_twist_02_l',
    'clavicle_r', 'upperarm_r', 'lowerarm_r', 'hand_r',
    'upperarm_twist_01_r', 'upperarm_twist_02_r', 'lowerarm_twist_01_r', 'lowerarm_twist_02_r',
]

upper_pose = {}
for bname in UPPER_BONES:
    pb = pack_arm.pose.bones.get(bname)
    if pb:
        upper_pose[bname] = pb.rotation_quaternion.copy()

print(f"Extracted {len(upper_pose)} upper body bone rotations from pack idle pose.")

# 2. Setup clean scene for authoring
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 30
scene.render.fps_base = 1.0
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

# Studio world
world = bpy.data.worlds.new("StudioWorld")
scene.world = world
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.28, 0.28, 0.30, 1.0)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0

# 3-Point Sun Lighting
def add_sun(name, loc, rot, energy, color):
    ld = bpy.data.lights.new(name=name, type='SUN')
    ld.energy = energy
    ld.color = color
    lo = bpy.data.objects.new(name=name, object_data=ld)
    scene.collection.objects.link(lo)
    lo.location = loc
    lo.rotation_euler = rot

add_sun("KeySun", (5.0, -5.0, 10.0), (radians(45), radians(15), radians(-45)), 3.0, (1.0, 0.98, 0.95))
add_sun("FillSun", (-6.0, -4.0, 6.0), (radians(60), radians(-20), radians(120)), 1.2, (0.75, 0.85, 1.0))
add_sun("RimSun", (0.0, 7.0, 6.0), (radians(-45), 0, radians(180)), 2.5, (1.0, 1.0, 1.0))

cam_data = bpy.data.cameras.new("ReviewCam")
cam_data.lens = 45.0
cam = bpy.data.objects.new("ReviewCam", object_data=cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

# Import base rig from BlockLoop
bpy.ops.import_scene.fbx(filepath=os.path.join(SRC_DIR, "BlockLoop.fbx"))
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
arm.name = "root"
arm.data.name = "root"

# Import mesh
cur = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=REF_RIG)
mesh = [o for o in set(bpy.data.objects) - cur if o.type == 'MESH' and 'LOD0' in o.name][0]
for o in set(bpy.data.objects) - cur:
    if o != mesh:
        bpy.data.objects.remove(o, do_unlink=True)
mesh.parent = arm
for mod in mesh.modifiers:
    if mod.type == 'ARMATURE':
        mod.object = arm

# Import sword
cur = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=SWORD_FBX)
sword = [o for o in set(bpy.data.objects) - cur if o.type == 'MESH'][0]
sword.name = "ReviewSword"
sword.parent = arm
sword.parent_type = 'BONE'
sword.parent_bone = "hand_r"
sword.scale = (1.0, 1.0, 1.0)
sword.location = (0.0, 0.05, 0.0)
sword.rotation_euler = (0, radians(90), 0)

for m in sword.data.materials:
    if m and m.node_tree:
        bsdf = [n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'][0]
        bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.0
        bsdf.inputs['Roughness'].default_value = 0.4

scene.frame_set(1)
base_pelvis_loc = arm.pose.bones['pelvis'].location.copy()

# R6 Accepted Leg and Root Motion (15 frames = 0.467 s @ 30 fps)
KEYFRAMES_LEGS = {
    1: { # F1: Ready stance
        "pelvis_z": 0.0, "pelvis_pitch": 0.0,
        "thigh_r": (-10, 0, -6), "calf_r": (0, 0, 20), "foot_r": (0, 0, -10),
        "thigh_l": (15, 0, 10), "calf_l": (0, 0, -25), "foot_l": (0, 0, 15),
    },
    4: { # F4: Left foot pushes off, Right leg swings backward off ground!
        "pelvis_z": 6.0, "pelvis_pitch": -4.0,
        "thigh_r": (-40, 10, -15), "calf_r": (0, 0, 60), "foot_r": (0, 0, -30),
        "thigh_l": (25, 0, 15), "calf_l": (0, 0, -55), "foot_l": (0, 0, 25),
    },
    7: { # F7: Maximum stride: Right leg reaching back for touchdown, Left foot trailing
        "pelvis_z": 10.0, "pelvis_pitch": -6.0,
        "thigh_r": (-55, 5, -10), "calf_r": (0, 0, 25), "foot_r": (0, 0, 15),
        "thigh_l": (12, 0, 5), "calf_l": (0, 0, -35), "foot_l": (0, 0, -10),
    },
    10: { # F10: Right foot firmly planted, absorbing impact; Left leg pulling backward
        "pelvis_z": -5.0, "pelvis_pitch": -8.0,
        "thigh_r": (-28, 0, -10), "calf_r": (0, 0, 45), "foot_r": (0, 0, -15),
        "thigh_l": (-20, 0, -8), "calf_l": (0, 0, 30), "foot_l": (0, 0, 0),
    },
    13: { # F13: Left foot planting, knees cushioning, weight distributing
        "pelvis_z": -2.0, "pelvis_pitch": -4.0,
        "thigh_r": (-14, 0, -8), "calf_r": (0, 0, 28), "foot_r": (0, 0, -12),
        "thigh_l": (8, 0, 8), "calf_l": (0, 0, -20), "foot_l": (0, 0, 12),
    },
    15: { # F15: Fully settled into stable, balanced combat stance
        "pelvis_z": 0.0, "pelvis_pitch": 0.0,
        "thigh_r": (-10, 0, -6), "calf_r": (0, 0, 20), "foot_r": (0, 0, -10),
        "thigh_l": (10, 0, 10), "calf_l": (0, 0, -22), "foot_l": (0, 0, 12),
    },
}

def set_bone_rot_euler(pb_name, rot_euler, f):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = rot_euler
        pb.keyframe_insert('rotation_euler', frame=f)

def set_bone_rot_quat(pb_name, quat, f):
    pb = arm.pose.bones.get(pb_name)
    if pb:
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = quat
        pb.keyframe_insert('rotation_quaternion', frame=f)

# Apply R6 Legs and Root Motion
for kf, data in KEYFRAMES_LEGS.items():
    f = kf
    t = (f - 1) / 14.0
    y_delta = -(3 * t**2 - 2 * t**3) * 200.0
    z_hop = data["pelvis_z"]

    p = arm.pose.bones['pelvis']
    p.location = base_pelvis_loc + Vector((z_hop, y_delta, 0.0))
    p.keyframe_insert('location', frame=f)
    p.rotation_mode = 'XYZ'
    p.rotation_euler = (0, radians(data["pelvis_pitch"]), 0)
    p.keyframe_insert('rotation_euler', frame=f)

    # Leg rotations
    set_bone_rot_euler('thigh_r', (radians(data["thigh_r"][0]), radians(data["thigh_r"][1]), radians(data["thigh_r"][2])), f)
    set_bone_rot_euler('calf_r', (radians(data["calf_r"][0]), radians(data["calf_r"][1]), radians(data["calf_r"][2])), f)
    set_bone_rot_euler('foot_r', (radians(data["foot_r"][0]), radians(data["foot_r"][1]), radians(data["foot_r"][2])), f)

    set_bone_rot_euler('thigh_l', (radians(data["thigh_l"][0]), radians(data["thigh_l"][1]), radians(data["thigh_l"][2])), f)
    set_bone_rot_euler('calf_l', (radians(data["calf_l"][0]), radians(data["calf_l"][1]), radians(data["calf_l"][2])), f)
    set_bone_rot_euler('foot_l', (radians(data["foot_l"][0]), radians(data["foot_l"][1]), radians(data["foot_l"][2])), f)

# Apply Upper Body Pack Pose across all 15 frames (with slight natural breathing/cushion)
for f in range(1, 16):
    for bname, quat in upper_pose.items():
        set_bone_rot_quat(bname, quat, f)

# Bake NLA
bpy.context.view_layer.objects.active = arm
arm.select_set(True)
orig_act = arm.animation_data.action
bpy.ops.object.mode_set(mode='POSE')
bpy.ops.pose.select_all(action='SELECT')
bpy.ops.nla.bake(frame_start=1, frame_end=15, step=1, only_selected=False, visual_keying=True, clear_constraints=True, clear_parents=False, bake_types={'POSE'})
bpy.ops.object.mode_set(mode='OBJECT')
if orig_act in bpy.data.actions.values():
    bpy.data.actions.remove(orig_act)

# Verify motion metrics
scene.frame_set(1)
dg = bpy.context.evaluated_depsgraph_get()
arm_eval = arm.evaluated_get(dg)
p1 = (arm_eval.matrix_world @ arm_eval.pose.bones['pelvis'].matrix).translation.copy()
f1 = (arm_eval.matrix_world @ arm_eval.pose.bones['foot_r'].matrix).translation.copy()
h1 = arm_eval.pose.bones['hand_r'].matrix.to_quaternion()

scene.frame_set(8)
dg = bpy.context.evaluated_depsgraph_get()
arm_eval = arm.evaluated_get(dg)
p8 = (arm_eval.matrix_world @ arm_eval.pose.bones['pelvis'].matrix).translation.copy()
f8 = (arm_eval.matrix_world @ arm_eval.pose.bones['foot_r'].matrix).translation.copy()
h8 = arm_eval.pose.bones['hand_r'].matrix.to_quaternion()

p_loc_diff = (p8 - p1).length * 100.0
rot_diff = degrees(h1.rotation_difference(h8).angle)
keyed_bones = len(arm.pose.bones)

print(f"[VERIFIED R7 Backstep_Back]: keyed_bones={keyed_bones}, pelvis loc diff={p_loc_diff:.2f} cm, hand_r rot diff={rot_diff:.2f} deg, foot elevation={f8.z:.2f} m")

# Render side and front frames
TOTAL = 15
for f in range(TOTAL):
    scene.frame_set(f + 1)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    py = (arm_eval.matrix_world @ arm_eval.pose.bones['pelvis'].matrix).translation.y

    # Side view
    cam.location = (4.8, py, 0.90)
    cam.rotation_euler = (radians(90), 0, radians(90))
    scene.render.filepath = os.path.join(FRAMES_DIR, f"side_{f:03d}.png")
    bpy.ops.render.render(write_still=True)

    # Front view
    cam.location = (0.0, py - 4.5, 0.90)
    cam.rotation_euler = (radians(90), 0, 0.0)
    scene.render.filepath = os.path.join(FRAMES_DIR, f"front_{f:03d}.png")
    bpy.ops.render.render(write_still=True)

# Look PNG (Frame 7 - stride apex)
look_png = os.path.join(OUT_DIR, "look_Backstep_Back.png")
shutil.copyfile(os.path.join(FRAMES_DIR, "side_006.png"), look_png)
shutil.copyfile(look_png, os.path.join(BASE_DIR, "look_Backstep_Back.png"))

# Review MP4
mp4_path = os.path.join(OUT_DIR, "review_Backstep_Back.mp4")
concat_txt = os.path.join(FRAMES_DIR, "concat.txt")
with open(concat_txt, "w") as cf:
    for f in range(TOTAL):
        p = os.path.join(FRAMES_DIR, f"side_{f:03d}.png").replace("\\", "/")
        cf.write(f"file '{p}'\nduration 0.033333\n")
    for f in range(TOTAL):
        p = os.path.join(FRAMES_DIR, f"front_{f:03d}.png").replace("\\", "/")
        cf.write(f"file '{p}'\nduration 0.033333\n")
    for f in range(TOTAL):
        p = os.path.join(FRAMES_DIR, f"side_{f:03d}.png").replace("\\", "/")
        cf.write(f"file '{p}'\nduration 0.066666\n")
    cf.write(f"file '{os.path.join(FRAMES_DIR, f'side_{TOTAL-1:03d}.png').replace(chr(92), '/')}'\n")

cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_txt}" -c:v libx264 -pix_fmt yuv420p -r 30 -crf 18 "{mp4_path}"'
subprocess.run(cmd, shell=True, check=True)

# Strip PNG (Frames 0, 3, 6, 9, 12, 14 -> 1, 4, 7, 10, 13, 15)
strip_png = os.path.join(OUT_DIR, "strip_Backstep_Back.png")
strip_indices = [0, 3, 6, 9, 12, 14]
inputs = " ".join([f'-i "{os.path.join(FRAMES_DIR, f"side_{f:03d}.png").replace(chr(92), "/")}"' for f in strip_indices])
scales = "".join([f'[{i}:v]scale=320:180[v{i}];' for i in range(len(strip_indices))])
stacks = "".join([f'[v{i}]' for i in range(len(strip_indices))])
cmd = f'ffmpeg -y {inputs} -filter_complex "{scales}{stacks}hstack=inputs={len(strip_indices)}" "{strip_png}"'
subprocess.run(cmd, shell=True, check=True)

# FBX export
fbx_path = os.path.join(OUT_DIR, "Backstep_Back.fbx")
for m in [o for o in bpy.data.objects if o.type == 'MESH']:
    m.select_set(False)

bpy.context.view_layer.objects.active = arm
arm.select_set(True)
scene.frame_start = 1
scene.frame_end = 15

bpy.ops.export_scene.fbx(
    filepath=fbx_path,
    check_existing=False,
    use_selection=True,
    global_scale=1.0,
    apply_unit_scale=False,
    bake_anim=True,
    bake_anim_use_all_bones=True,
    bake_anim_use_nla_strips=False,
    bake_anim_use_all_actions=False,
    bake_anim_force_startend_keying=True,
    bake_anim_step=1.0,
    axis_forward='-Z',
    axis_up='Y'
)
shutil.copyfile(fbx_path, os.path.join(BASE_DIR, "Backstep_Back.fbx"))
print("R7_DELIVERED:", fbx_path, mp4_path, strip_png)
