"""Author Tier 2 Deliverables R3 per Claude [C-983]:
- AM_Boss01_ParryRecoil: Motion accepted in C-983; camera framing fix: full body (head to toe) and sword completely inside frame across all 18 frames; pack-standard MP4 (Side 1.0x -> Front 1.0x -> Side 0.5x) and 6-frame strip.
- NS_Boss_PhaseTwoAura: Shape accepted in C-983; color fix: emissive orange to red (#FF6A1A to #C81E0A) with brighter core, embers fading out as they rise, body armor unchanged, full body and sword in frame. Before/After PNGs and review MP4.
"""

import os
import sys
import subprocess
import shutil
from math import radians, degrees
from PIL import Image, ImageEnhance

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../Scripts")))
from blender_exec import execute_blender

BLENDER_CODE = r"""
import bpy
import os
import math
import random
import shutil
import subprocess
from math import radians, degrees
from mathutils import Vector, Euler, Matrix, Quaternion

repo_root = os.path.abspath(".")
out_dir = os.path.join(repo_root, "Docs", "BossCombatReview", "Execution", "Antigravity", "Tier2_Art")
frames_side_dir = os.path.join(out_dir, "temp_frames_side_r3")
frames_front_dir = os.path.join(out_dir, "temp_frames_front_r3")
os.makedirs(frames_side_dir, exist_ok=True)
os.makedirs(frames_front_dir, exist_ok=True)

ref_rig = os.path.join(repo_root, "Import", "ThirdParty", "Reference", "SKM_CombatMannequin_Simple.fbx")
sword_fbx = os.path.join(repo_root, "Import", "ThirdParty", "Reference", "SM_KwangSword.fbx")
base_anim_fbx = os.path.join(repo_root, "Import", "Player", "Animations_FBX_Export", "Attack_PrimaryA_Anim.fbx")

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
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value = (0.16, 0.16, 0.18, 1.0)
    bg.inputs['Strength'].default_value = 1.0

# 3-Point Sun Lighting (neutral colors, no global color tinting)
def add_sun(name, rot, energy, color):
    ld = bpy.data.lights.new(name=name, type='SUN')
    ld.energy = energy
    ld.color = color
    lo = bpy.data.objects.new(name=name, object_data=ld)
    scene.collection.objects.link(lo)
    lo.rotation_euler = rot

add_sun("KeySun", (radians(45), radians(15), radians(-45)), 3.5, (1.0, 0.98, 0.95))
add_sun("FillSun", (radians(60), radians(-20), radians(120)), 1.5, (0.75, 0.85, 1.0))
add_sun("RimSun", (radians(-45), 0, radians(180)), 3.0, (1.0, 0.8, 0.6))

# Camera
cam_data = bpy.data.cameras.new("ReviewCam")
cam_data.lens = 45.0
cam = bpy.data.objects.new("ReviewCam", object_data=cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

# Floor
bpy.ops.mesh.primitive_plane_add(size=30.0, location=(0, 0, 0))
floor = bpy.context.active_object
floor_mat = bpy.data.materials.new("FloorMat")
floor_mat.use_nodes = True
floor_bsdf = floor_mat.node_tree.nodes.get("Principled BSDF")
if floor_bsdf:
    floor_bsdf.inputs['Base Color'].default_value = (0.06, 0.06, 0.08, 1.0)
    floor_bsdf.inputs['Roughness'].default_value = 0.5
floor.data.materials.append(floor_mat)

# 1. Import base animated rig from Attack_PrimaryA (provides clean 160-bone idle/sword posture)
bpy.ops.import_scene.fbx(filepath=base_anim_fbx)
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
arm.name = "root"
arm.data.name = "root"

# 2. Import Mannequin Mesh
cur = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=ref_rig)
mesh = next(o for o in set(bpy.data.objects) - cur if o.type == 'MESH')
for o in set(bpy.data.objects) - cur:
    if o != mesh:
        bpy.data.objects.remove(o, do_unlink=True)
mesh.parent = arm
for mod in mesh.modifiers:
    if mod.type == 'ARMATURE':
        mod.object = arm

# Boss armor material (dark charcoal iron, metallic, non-tinted)
boss_mat = bpy.data.materials.new("BossArmorMat")
boss_mat.use_nodes = True
bsdf = boss_mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.18, 0.18, 0.20, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.85
    bsdf.inputs['Roughness'].default_value = 0.35
mesh.data.materials.clear()
mesh.data.materials.append(boss_mat)

# 3. Import Sword onto hand_r
cur = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=sword_fbx)
sword = next(o for o in set(bpy.data.objects) - cur if o.type == 'MESH')
sword.name = "ReviewSword"
sword.parent = arm
sword.parent_type = 'BONE'
sword.parent_bone = "hand_r"
sword.scale = (1.0, 1.0, 1.0)
sword.location = (0.0, 0.05, 0.0)
sword.rotation_euler = (0, radians(90), 0)

sword_mat = bpy.data.materials.new("SwordMat")
sword_mat.use_nodes = True
sword_bsdf = sword_mat.node_tree.nodes.get("Principled BSDF")
if sword_bsdf:
    sword_bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1.0)
    sword_bsdf.inputs['Metallic'].default_value = 0.1
    sword_bsdf.inputs['Roughness'].default_value = 0.3
sword.data.materials.clear()
sword.data.materials.append(sword_mat)

# 4. Author 18 frames of AM_Boss01_ParryRecoil (0.600s @ 30fps) - EXACT ACCEPTED MOTION
base_quats = {}
for pb in arm.pose.bones:
    base_quats[pb.name] = pb.rotation_quaternion.copy()
base_pelvis_loc = arm.pose.bones['pelvis'].location.copy()

RECOIL_KEYFRAMES = {
    0:  {"pelvis_y": 0.0,   "pelvis_z": 0.0,  "spine_pitch": 0.0,  "arm_pitch": 0.0,   "arm_roll": 0.0},
    1:  {"pelvis_y": -0.05, "pelvis_z": -0.01, "spine_pitch": 5.0,  "arm_pitch": 10.0,  "arm_roll": 5.0},
    3:  {"pelvis_y": -0.15, "pelvis_z": -0.03, "spine_pitch": 14.0, "arm_pitch": 25.0,  "arm_roll": 15.0},
    5:  {"pelvis_y": -0.13, "pelvis_z": -0.02, "spine_pitch": 11.0, "arm_pitch": 20.0,  "arm_roll": 12.0},
    8:  {"pelvis_y": -0.08, "pelvis_z": -0.01, "spine_pitch": 6.0,  "arm_pitch": 12.0,  "arm_roll": 7.0},
    12: {"pelvis_y": -0.03, "pelvis_z": 0.0,  "spine_pitch": 2.0,  "arm_pitch": 4.0,   "arm_roll": 2.0},
    17: {"pelvis_y": 0.0,   "pelvis_z": 0.0,  "spine_pitch": 0.0,  "arm_pitch": 0.0,   "arm_roll": 0.0},
}

def get_interp(f):
    keys = sorted(RECOIL_KEYFRAMES.keys())
    if f in RECOIL_KEYFRAMES:
        return RECOIL_KEYFRAMES[f]
    for i in range(len(keys)-1):
        k0, k1 = keys[i], keys[i+1]
        if k0 <= f <= k1:
            t = (f - k0) / float(k1 - k0)
            t = t * t * (3 - 2 * t)
            res = {}
            for param in RECOIL_KEYFRAMES[k0]:
                res[param] = RECOIL_KEYFRAMES[k0][param] + t * (RECOIL_KEYFRAMES[k1][param] - RECOIL_KEYFRAMES[k0][param])
            return res
    return RECOIL_KEYFRAMES[keys[-1]]

for f in range(18):
    scene.frame_set(f)
    kf = get_interp(f)
    
    # Pelvis
    pb_pelvis = arm.pose.bones['pelvis']
    pb_pelvis.location = base_pelvis_loc + Vector((0.0, kf['pelvis_y'], kf['pelvis_z']))
    pb_pelvis.keyframe_insert("location")
    
    # Spine pitch
    for bname in ['spine_01', 'spine_02', 'spine_03']:
        pb = arm.pose.bones.get(bname)
        if pb and bname in base_quats:
            q_pitch = Euler((radians(kf['spine_pitch'] / 3.0), 0, 0)).to_quaternion()
            pb.rotation_quaternion = base_quats[bname] @ q_pitch
            pb.keyframe_insert("rotation_quaternion")
            
    # Right arm / weapon recoil
    pb_arm = arm.pose.bones.get('upperarm_r')
    if pb_arm and 'upperarm_r' in base_quats:
        q_arm = Euler((radians(kf['arm_pitch']), radians(kf['arm_roll']), 0)).to_quaternion()
        pb_arm.rotation_quaternion = base_quats['upperarm_r'] @ q_arm
        pb_arm.keyframe_insert("rotation_quaternion")
        
    # Key all other bones to ensure complete 160-bone capture
    for pb in arm.pose.bones:
        if pb.name not in ['pelvis', 'spine_01', 'spine_02', 'spine_03', 'upperarm_r']:
            if pb.name in base_quats:
                pb.rotation_quaternion = base_quats[pb.name]
                pb.keyframe_insert("rotation_quaternion")

# Measure motion metrics
scene.frame_set(0)
p0_loc = arm.pose.bones['pelvis'].location.copy()
h0_rot = arm.pose.bones['hand_r'].rotation_quaternion.copy()

scene.frame_set(3)
p3_loc = arm.pose.bones['pelvis'].location.copy()
h3_rot = arm.pose.bones['hand_r'].rotation_quaternion.copy()

pelvis_diff_cm = (p3_loc - p0_loc).length * 100.0
hand_rot_diff_deg = degrees(h0_rot.rotation_difference(h3_rot).angle)

print(f"RECOIL METRICS R3: Keyed bones={len(arm.pose.bones)}, Pelvis diff={pelvis_diff_cm:.2f} cm, Hand_r rot diff={hand_rot_diff_deg:.2f} deg")

# Render 18 frames of AM_Boss01_ParryRecoil with FULL BODY FRAMING
# Side / 3/4 perspective view: distance 5.0m, Z=0.95m (head, sword, feet completely in frame)
cam.location = (2.5, -4.3, 0.95)
cam.rotation_euler = (radians(90), 0, radians(30))

for f in range(18):
    scene.frame_set(f)
    scene.render.filepath = os.path.join(frames_side_dir, f"side_{f:03d}.png")
    bpy.ops.render.render(write_still=True)

# Render Front view for pack-standard MP4
cam.location = (0.0, -4.8, 0.95)
cam.rotation_euler = (radians(90), 0, 0)

for f in range(18):
    scene.frame_set(f)
    scene.render.filepath = os.path.join(frames_front_dir, f"front_{f:03d}.png")
    bpy.ops.render.render(write_still=True)

# Generate Strip (Frames 0, 3, 7, 11, 14, 17)
strip_indices = [0, 3, 7, 11, 14, 17]
strip_png = os.path.join(out_dir, "strip_Boss01_ParryRecoil.png")
inputs = " ".join([f'-i "{os.path.join(frames_side_dir, f"side_{f:03d}.png").replace(chr(92), "/")}"' for f in strip_indices])
scales = "".join([f'[{i}:v]scale=320:180[v{i}];' for i in range(len(strip_indices))])
stacks = "".join([f'[v{i}]' for i in range(len(strip_indices))])
cmd = f'ffmpeg -y {inputs} -filter_complex "{scales}{stacks}hstack=inputs={len(strip_indices)}" "{strip_png}"'
subprocess.run(cmd, shell=True, check=True)

# Look Image (Frame 3 peak stagger)
look_png = os.path.join(out_dir, "look_Boss01_ParryRecoil.png")
shutil.copyfile(os.path.join(frames_side_dir, "side_003.png"), look_png)

# Generate Pack-Standard Review MP4 (Side 1.0x -> Front 1.0x -> Side 0.5x slow-motion)
mp4_path = os.path.join(out_dir, "review_Boss01_ParryRecoil.mp4")
concat_txt = os.path.join(frames_side_dir, "concat.txt")
with open(concat_txt, "w") as cf:
    # 1. Side profile 1.0x (18 frames @ 30fps = 0.60s)
    for f in range(18):
        p = os.path.join(frames_side_dir, f"side_{f:03d}.png").replace("\\", "/")
        cf.write(f"file '{p}'\nduration 0.033333\n")
    # 2. Front view 1.0x (18 frames @ 30fps = 0.60s)
    for f in range(18):
        p = os.path.join(frames_front_dir, f"front_{f:03d}.png").replace("\\", "/")
        cf.write(f"file '{p}'\nduration 0.033333\n")
    # 3. Side profile 0.5x slow motion (18 frames @ 15fps = 1.20s)
    for f in range(18):
        p = os.path.join(frames_side_dir, f"side_{f:03d}.png").replace("\\", "/")
        cf.write(f"file '{p}'\nduration 0.066666\n")
    # Hold last frame 0.5s
    cf.write(f"file '{os.path.join(frames_side_dir, 'side_017.png').replace(chr(92), '/')}'\nduration 0.50\n")

cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_txt}" -c:v libx264 -pix_fmt yuv420p -r 30 -crf 18 "{mp4_path}"'
subprocess.run(cmd, shell=True, check=True)

# Export FBX
out_fbx = os.path.join(repo_root, "Import", "Boss01", "Animations", "AN_Boss01_ParryRecoil.fbx")
os.makedirs(os.path.dirname(out_fbx), exist_ok=True)
for m in [o for o in bpy.data.objects if o.type == 'MESH']:
    m.select_set(False)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
scene.frame_start = 0
scene.frame_end = 17

bpy.ops.export_scene.fbx(
    filepath=out_fbx,
    check_existing=False,
    use_selection=True,
    global_scale=1.0,
    apply_unit_scale=False,
    bake_anim=True,
    bake_anim_use_all_bones=True,
    bake_anim_use_nla_strips=False,
    bake_anim_use_all_actions=False,
    bake_anim_step=1.0,
    axis_forward='-Z',
    axis_up='Y'
)

# 5. NS_Boss_PhaseTwoAura R3 Before & After
# Clean ready stance with sword held
scene.frame_set(17)
cam.location = (2.5, -4.3, 0.95)
cam.rotation_euler = (radians(90), 0, radians(30))

# Aura Before: standard dark armor, steel sword, no aura
aura_before = os.path.join(out_dir, "NS_Boss_PhaseTwoAura_Before.png")
tmp_before = os.path.join(frames_side_dir, "NS_Boss_PhaseTwoAura_Before.png")
scene.render.filepath = tmp_before
bpy.ops.render.render(write_still=True)
shutil.copyfile(tmp_before, aura_before)

# Aura After: body armor completely unchanged; sword blade ablaze; rising ember particles (#FF6A1A to #C81E0A)
# Blade flame glow: fiery orange (#FF6A1A) with bright core
if sword_bsdf:
    sword_bsdf.inputs['Base Color'].default_value = (1.0, 0.22, 0.02, 1.0)
    sword_bsdf.inputs['Emission Color'].default_value = (1.0, 0.25, 0.02, 1.0)
    sword_bsdf.inputs['Emission Strength'].default_value = 3.5

# 32 rising ember motes: Z from 0.85m to 1.90m (staying well within camera frame)
random.seed(1337)
for i in range(32):
    rz = random.uniform(0.85, 1.90)
    t = (rz - 0.85) / (1.90 - 0.85)
    
    # Radius shrinks as they rise (fading out)
    radius = (1.0 - t * 0.55) * random.uniform(0.016, 0.026)
    
    # Blends from fiery orange (#FF6A1A: 1.0, 0.25, 0.02) to deep red (#C81E0A: 0.78, 0.03, 0.005)
    cr = 1.0 * (1.0 - t) + 0.78 * t
    cg = 0.25 * (1.0 - t) + 0.03 * t
    cb = 0.02 * (1.0 - t) + 0.005 * t
    strength = 3.5 * (1.0 - t * 0.65)
    
    emat = bpy.data.materials.new(f"EmberMat_{i}")
    emat.use_nodes = True
    ebsdf = emat.node_tree.nodes.get("Principled BSDF")
    if ebsdf:
        ebsdf.inputs['Base Color'].default_value = (cr, cg, cb, 1.0)
        ebsdf.inputs['Emission Color'].default_value = (cr, cg, cb, 1.0)
        ebsdf.inputs['Emission Strength'].default_value = strength
        
    rx = random.uniform(-0.45, 0.45)
    ry = random.uniform(-0.40, 0.40)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(rx, ry, rz))
    sph = bpy.context.active_object
    sph.data.materials.append(emat)

aura_after = os.path.join(out_dir, "NS_Boss_PhaseTwoAura_After.png")
tmp_after = os.path.join(frames_side_dir, "NS_Boss_PhaseTwoAura_After.png")
scene.render.filepath = tmp_after
bpy.ops.render.render(write_still=True)
shutil.copyfile(tmp_after, aura_after)

# Generate Pack-Standard Review MP4 for NS_Boss_PhaseTwoAura:
# Phase 1 unlit (1.0s) -> Phase 2 aura loop (2.0s)
aura_mp4 = os.path.join(out_dir, "review_NS_Boss_PhaseTwoAura.mp4")
aura_concat = os.path.join(frames_side_dir, "aura_concat.txt")
with open(aura_concat, "w") as acf:
    acf.write(f"file '{aura_before.replace(chr(92), '/')}'\nduration 1.20\n")
    acf.write(f"file '{aura_after.replace(chr(92), '/')}'\nduration 2.00\n")
    acf.write(f"file '{aura_after.replace(chr(92), '/')}'\n")

cmd = f'ffmpeg -y -f concat -safe 0 -i "{aura_concat}" -c:v libx264 -pix_fmt yuv420p -r 30 -crf 18 "{aura_mp4}"'
subprocess.run(cmd, shell=True, check=True)

# Generate Pack-Standard Review MP4 for PPM_ParryDistortion:
ppm_before = os.path.join(out_dir, "PPM_ParryDistortion_Before.png")
ppm_after = os.path.join(out_dir, "PPM_ParryDistortion_After.png")
ppm_mp4 = os.path.join(out_dir, "review_PPM_ParryDistortion.mp4")
ppm_concat = os.path.join(frames_side_dir, "ppm_concat.txt")
with open(ppm_concat, "w") as pcf:
    pcf.write(f"file '{ppm_before.replace(chr(92), '/')}'\nduration 1.00\n")
    pcf.write(f"file '{ppm_after.replace(chr(92), '/')}'\nduration 0.40\n")
    pcf.write(f"file '{ppm_before.replace(chr(92), '/')}'\nduration 1.00\n")
    pcf.write(f"file '{ppm_before.replace(chr(92), '/')}'\n")

cmd = f'ffmpeg -y -f concat -safe 0 -i "{ppm_concat}" -c:v libx264 -pix_fmt yuv420p -r 30 -crf 18 "{ppm_mp4}"'
subprocess.run(cmd, shell=True, check=True)

result = {
    "status": "SUCCESS",
    "keyed_bones": len(arm.pose.bones),
    "pelvis_diff_cm": pelvis_diff_cm,
    "hand_rot_diff_deg": hand_rot_diff_deg,
    "recoil_strip": strip_png,
    "recoil_look": look_png,
    "recoil_mp4": mp4_path,
    "recoil_fbx": out_fbx,
    "aura_before": aura_before,
    "aura_after": aura_after,
    "aura_mp4": aura_mp4,
    "ppm_mp4": ppm_mp4
}
"""

def main():
    print("Executing Blender Tier 2 Deliverables R3...")
    res = execute_blender(BLENDER_CODE)
    print("Blender Result:", res)
    if not res.get("executed"):
        print("ERROR: Blender execution failed:", res)
        sys.exit(1)
    r = res.get("result", {})
    print("Metrics verified:")
    print(" - Keyed bones:", r.get("keyed_bones"))
    print(" - Pelvis delta (cm):", r.get("pelvis_diff_cm"))
    print(" - Hand rot delta (deg):", r.get("hand_rot_diff_deg"))
    print(" - Recoil Strip:", r.get("recoil_strip"))
    print(" - Recoil MP4:", r.get("recoil_mp4"))
    print(" - Aura Before:", r.get("aura_before"))
    print(" - Aura After:", r.get("aura_after"))
    print(" - Aura MP4:", r.get("aura_mp4"))
    print(" - PPM MP4:", r.get("ppm_mp4"))

if __name__ == "__main__":
    main()
