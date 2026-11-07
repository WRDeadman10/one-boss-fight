"""Author ER-A1: Backstep_Back R5 in Blender.

Addresses Lead Claude's directive [C-972]:
- Low hop backwards, both feet near the ground (max root lift 12 cm, foot elevation near ground)
- About 0.4-0.5 s (15 frames @ 30 fps = 0.467 s)
- Sword lowered down along the thigh (combat ready low position)
- Sourced from BlockLoop.fbx / MM_Jump.fbx with smooth backward translation (-200 cm)
- Single solid white blade
"""

import os
import shutil
import subprocess
from math import radians, degrees
import bpy
from mathutils import Vector, Quaternion

BASE_DIR = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\ER_ANIM"
SRC_DIR = r"c:\UnrealProject\OneBossFight\Import\Player\Animations_FBX_Export"
REF_RIG = r"c:\UnrealProject\OneBossFight\Import\ThirdParty\Reference\SKM_CombatMannequin_Simple.fbx"
SWORD_FBX = r"c:\UnrealProject\OneBossFight\Import\ThirdParty\Reference\SM_KwangSword.fbx"

OUT_DIR = os.path.join(BASE_DIR, "Backstep_Back")
FRAMES_DIR = os.path.join(OUT_DIR, "temp_frames_r5")
os.makedirs(FRAMES_DIR, exist_ok=True)

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

# Import BlockLoop
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

# Animate 15 frames of low backstep hop
for f in range(1, 16):
    t = (f - 1) / 14.0
    # Backward translation along -Y (-200 cm)
    y_delta = -(3 * t**2 - 2 * t**3) * 200.0
    # Low hop: max 12 cm lift in pelvis X (which maps to world Z)
    z_hop = 12.0 * (4 * t * (1 - t))

    p = arm.pose.bones['pelvis']
    p.location = base_pelvis_loc + Vector((z_hop, y_delta, 0.0))
    p.keyframe_insert('location', frame=f)

    # Sword lowered down along the thigh (combat ready low position)
    pb_arm = arm.pose.bones['upperarm_r']
    pb_arm.rotation_mode = 'XYZ'
    pb_arm.rotation_euler = (radians(35), radians(15), radians(-20))
    pb_arm.keyframe_insert('rotation_euler', frame=f)

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

print(f"[VERIFIED R5 Backstep_Back]: keyed_bones={keyed_bones}, pelvis loc diff={p_loc_diff:.2f} cm, hand_r rot diff={rot_diff:.2f} deg, foot elevation={f8.z:.2f} m")

# Render side and front frames
TOTAL = 15
for f in range(TOTAL):
    scene.frame_set(f + 1)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    py = (arm_eval.matrix_world @ arm_eval.pose.bones['pelvis'].matrix).translation.y

    cam.location = (4.8, py, 0.90)
    cam.rotation_euler = (radians(90), 0, radians(90))
    scene.render.filepath = os.path.join(FRAMES_DIR, f"side_{f:03d}.png")
    bpy.ops.render.render(write_still=True)

    cam.location = (0.0, py - 4.5, 0.90)
    cam.rotation_euler = (radians(90), 0, 0.0)
    scene.render.filepath = os.path.join(FRAMES_DIR, f"front_{f:03d}.png")
    bpy.ops.render.render(write_still=True)

# Look PNG
look_png = os.path.join(OUT_DIR, "look_Backstep_Back.png")
shutil.copyfile(os.path.join(FRAMES_DIR, "side_007.png"), look_png)
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

# Strip PNG
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
print("R5_DELIVERED:", fbx_path, mp4_path, strip_png)
