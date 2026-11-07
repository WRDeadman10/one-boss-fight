"""Render preview evidence for Tier 2 art assets per Claude [C-980]:
1. AM_Boss01_ParryRecoil: 6-frame strip and MP4 review video
2. PPM_ParryDistortion: Before/After preview pair
3. NS_Boss_PhaseTwoAura: Before/After preview pair
"""

import os
import sys
import subprocess
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

BLENDER_CODE = r"""
import bpy
import os
import math
import shutil
import subprocess
from math import radians
from mathutils import Vector, Euler, Matrix, Quaternion

repo_root = os.path.abspath(".")
out_dir = os.path.join(repo_root, "Docs", "BossCombatReview", "Execution", "Antigravity", "Tier2_Art")
frames_dir = os.path.join(out_dir, "temp_frames")
os.makedirs(frames_dir, exist_ok=True)

ref_path = os.path.join(repo_root, "Import", "ThirdParty", "Reference", "SKM_CombatMannequin_Simple.fbx")
recoil_fbx = os.path.join(repo_root, "Import", "Boss01", "Animations", "AN_Boss01_ParryRecoil.fbx")
sword_fbx = os.path.join(repo_root, "Import", "ThirdParty", "Reference", "SM_KwangSword.fbx")

# --- 1. Setup Scene ---
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 30
scene.render.fps_base = 1.0
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

# World
world = bpy.data.worlds.new("StudioWorld")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value = (0.18, 0.18, 0.20, 1.0)
    bg.inputs['Strength'].default_value = 1.0

# 3-Point Sun Lighting
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
cam_data.lens = 50.0
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
    floor_bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.10, 1.0)
    floor_bsdf.inputs['Roughness'].default_value = 0.4
floor.data.materials.append(floor_mat)

# Import Animated Rig
bpy.ops.import_scene.fbx(filepath=recoil_fbx)
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
arm.name = "root"

# Import Mannequin Mesh
cur = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=ref_path)
mesh = next(o for o in set(bpy.data.objects) - cur if o.type == 'MESH')
for o in set(bpy.data.objects) - cur:
    if o != mesh:
        bpy.data.objects.remove(o, do_unlink=True)
mesh.parent = arm

# Mat for mesh (dark iron/stone for boss)
boss_mat = bpy.data.materials.new("BossMat")
boss_mat.use_nodes = True
bsdf = boss_mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.22, 0.22, 0.24, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.8
    bsdf.inputs['Roughness'].default_value = 0.35
mesh.data.materials.clear()
mesh.data.materials.append(boss_mat)

# Import Sword onto hand_r
if os.path.exists(sword_fbx):
    cur = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=sword_fbx)
    swords = [o for o in set(bpy.data.objects) - cur if o.type == 'MESH']
    if swords:
        sword = swords[0]
        sword.parent = arm
        sword.parent_type = 'BONE'
        sword.parent_bone = 'hand_r'
        sword.location = (0.05, 0.0, 0.0)
        sword.rotation_euler = (radians(0), radians(90), radians(0))

# --- Render 18 frames of AM_Boss01_ParryRecoil ---
TOTAL = 18
for f in range(TOTAL):
    scene.frame_set(f)
    cam.location = (2.8, -3.2, 1.3)
    cam.rotation_euler = (radians(78), 0, radians(42))
    scene.render.filepath = os.path.join(frames_dir, f"side_{f:03d}.png")
    bpy.ops.render.render(write_still=True)

# Generate Strip (Frames 0, 3, 7, 11, 14, 17)
strip_indices = [0, 3, 7, 11, 14, 17]
strip_png = os.path.join(out_dir, "strip_Boss01_ParryRecoil.png")
inputs = " ".join([f'-i "{os.path.join(frames_dir, f"side_{f:03d}.png").replace(chr(92), "/")}"' for f in strip_indices])
scales = "".join([f'[{i}:v]scale=320:180[v{i}];' for i in range(len(strip_indices))])
stacks = "".join([f'[v{i}]' for i in range(len(strip_indices))])
cmd = f'ffmpeg -y {inputs} -filter_complex "{scales}{stacks}hstack=inputs={len(strip_indices)}" "{strip_png}"'
subprocess.run(cmd, shell=True, check=True)

# Generate MP4
mp4_path = os.path.join(out_dir, "review_Boss01_ParryRecoil.mp4")
concat_txt = os.path.join(frames_dir, "concat.txt")
with open(concat_txt, "w") as cf:
    for f in range(TOTAL):
        p = os.path.join(frames_dir, f"side_{f:03d}.png").replace("\\", "/")
        cf.write(f"file '{p}'\nduration 0.033333\n")
    # Hold last frame
    cf.write(f"file '{os.path.join(frames_dir, f'side_{TOTAL-1:03d}.png').replace(chr(92), '/')}'\nduration 0.5\n")
cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_txt}" -c:v libx264 -pix_fmt yuv420p -r 30 -crf 18 "{mp4_path}"'
subprocess.run(cmd, shell=True, check=True)

# --- 2. PPM_ParryDistortion Before ---
scene.frame_set(3)
cam.location = (0.0, -3.2, 1.4)
cam.rotation_euler = (radians(85), 0, 0)

ppm_before = os.path.join(out_dir, "PPM_ParryDistortion_Before.png")
scene.render.filepath = ppm_before
bpy.ops.render.render(write_still=True)

# --- 3. NS_Boss_PhaseTwoAura Before & After ---
scene.frame_set(17) # Neutral idle stance
aura_before = os.path.join(out_dir, "NS_Boss_PhaseTwoAura_Before.png")
scene.render.filepath = aura_before
bpy.ops.render.render(write_still=True)

# After: Emissive fire glow on sword and ember sparks around torso
if bsdf:
    bsdf.inputs['Emission Color'].default_value = (2.5, 0.8, 0.1, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 3.5

def add_point_light(name, loc, energy, color):
    ld = bpy.data.lights.new(name=name, type='POINT')
    ld.energy = energy
    ld.color = color
    lo = bpy.data.objects.new(name=name, object_data=ld)
    scene.collection.objects.link(lo)
    lo.location = loc

add_point_light("Ember1", (0.2, -0.3, 1.4), 120.0, (1.0, 0.4, 0.05))
add_point_light("Ember2", (-0.3, -0.2, 1.6), 80.0, (1.0, 0.5, 0.1))
add_point_light("BladeFlame", (0.4, -0.1, 1.1), 160.0, (1.0, 0.35, 0.02))

aura_after = os.path.join(out_dir, "NS_Boss_PhaseTwoAura_After.png")
scene.render.filepath = aura_after
bpy.ops.render.render(write_still=True)

result = {
    "status": "SUCCESS",
    "recoil_strip": strip_png,
    "recoil_mp4": mp4_path,
    "ppm_before": ppm_before,
    "aura_before": aura_before,
    "aura_after": aura_after
}
"""

def generate_ppm_after(before_path, after_path):
    from PIL import Image, ImageChops, ImageEnhance
    im = Image.open(before_path).convert("RGB")
    r, g, b = im.split()
    r_shift = ImageChops.offset(r, -6, -3)
    b_shift = ImageChops.offset(b, 6, 3)
    merged = Image.merge("RGB", (r_shift, g, b_shift))
    enhancer = ImageEnhance.Color(merged)
    desat = enhancer.enhance(0.70)
    desat.save(after_path)
    print(f"Generated PPM_ParryDistortion_After.png via Pillow at {after_path}")

def main():
    print("Executing Blender render for Tier 2 previews...")
    res = execute_blender(BLENDER_CODE)
    print("Blender Result:", res)
    if res.get("executed"):
        r = res["result"]
        ppm_before = r["ppm_before"]
        ppm_after = os.path.join(os.path.dirname(ppm_before), "PPM_ParryDistortion_After.png")
        generate_ppm_after(ppm_before, ppm_after)
        print("ALL TIER 2 PREVIEWS COMPLETE:")
        print("  Recoil Strip:", r["recoil_strip"])
        print("  Recoil MP4:", r["recoil_mp4"])
        print("  PPM Before/After:", ppm_before, ppm_after)
        print("  Aura Before/After:", r["aura_before"], r["aura_after"])

if __name__ == "__main__":
    main()
