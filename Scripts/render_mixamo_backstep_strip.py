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
from math import radians
from mathutils import Vector, Euler, Matrix, Quaternion

repo_root = r"C:\UnrealProject\OneBossFight"
out_dir = os.path.join(repo_root, "Docs", "BossCombatReview", "Execution", "Antigravity")
os.makedirs(out_dir, exist_ok=True)
frames_dir = os.path.join(out_dir, "temp_backstep_frames_v2")
if os.path.exists(frames_dir):
    shutil.rmtree(frames_dir)
os.makedirs(frames_dir, exist_ok=True)

ref_path = os.path.join(repo_root, "Import", "ThirdParty", "Reference", "SKM_CombatMannequin_Simple.fbx")
anim_fbx = os.path.join(repo_root, "Import", "ThirdParty", "Mixamo", "AN_ER_Backstep_Mixamo_V2.fbx")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 30
scene.render.fps_base = 1.0
scene.render.resolution_x = 640
scene.render.resolution_y = 360
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

# World
world = bpy.data.worlds.new("StudioWorld")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value = (0.15, 0.15, 0.18, 1.0)
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

# Import Animated Rig
bpy.ops.import_scene.fbx(filepath=anim_fbx)
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
for mod in mesh.modifiers:
    if mod.type == 'ARMATURE':
        mod.object = arm

mat = bpy.data.materials.new("PlayerMat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.7, 0.72, 0.75, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.2
    bsdf.inputs['Roughness'].default_value = 0.4
mesh.data.materials.clear()
mesh.data.materials.append(mat)

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

# Track dummy target at center of mannequin height (~0.9m) and mid-travel (~-0.8m)
target = bpy.data.objects.new("CamTarget", None)
scene.collection.objects.link(target)
target.location = (0.0, -0.8, 0.9)

# Camera
cam_data = bpy.data.cameras.new("ReviewCam")
cam_data.lens = 45.0
cam = bpy.data.objects.new("ReviewCam", object_data=cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

# Position camera for full-body 3/4 view
cam.location = (4.8, -3.8, 2.2)
c_track = cam.constraints.new(type='TRACK_TO')
c_track.target = target
c_track.track_axis = 'TRACK_NEGATIVE_Z'
c_track.up_axis = 'UP_Y'

# 6 frames across 18 frames: [1, 4, 8, 12, 15, 18]
strip_indices = [1, 4, 8, 12, 15, 18]
for idx, f in enumerate(strip_indices):
    scene.frame_set(f)
    scene.render.filepath = os.path.join(frames_dir, f"frame_{idx:02d}.png")
    bpy.ops.render.render(write_still=True)
print("Rendered 6 frames for V2 successfully.")
"""

def main():
    print("Executing Blender render for V2 full-body strip...")
    res = execute_blender(BLENDER_CODE)
    print("Blender output:", res.get("result") or res.get("error"))

    repo_root = r"C:\UnrealProject\OneBossFight"
    out_dir = os.path.join(repo_root, "Docs", "BossCombatReview", "Execution", "Antigravity")
    frames_dir = os.path.join(out_dir, "temp_backstep_frames_v2")
    strip_v2_png = os.path.join(out_dir, "strip_backstep_mixamo_v2.png")
    strip_png = os.path.join(out_dir, "strip_backstep_mixamo.png")

    strip_indices = list(range(6))
    inputs = " ".join([f'-i "{os.path.join(frames_dir, f"frame_{i:02d}.png").replace(chr(92), "/")}"' for i in strip_indices])
    scales = "".join([f'[{i}:v]scale=320:180[v{i}];' for i in range(len(strip_indices))])
    stacks = "".join([f'[v{i}]' for i in range(len(strip_indices))])
    cmd = f'ffmpeg -y {inputs} -filter_complex "{scales}{stacks}hstack=inputs={len(strip_indices)}" "{strip_v2_png}"'
    print("Running ffmpeg...")
    subprocess.run(cmd, shell=True, check=True)
    shutil.copyfile(strip_v2_png, strip_png)
    print("V2 Strip generated at:", strip_v2_png, "Size:", os.path.getsize(strip_v2_png))

    # Clean up temp frames
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)

if __name__ == "__main__":
    main()
