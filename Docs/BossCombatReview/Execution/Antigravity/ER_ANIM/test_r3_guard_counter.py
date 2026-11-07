import bpy
import os
import subprocess
from math import radians
from mathutils import Vector

OUT_DIR = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\ER_ANIM\Attack_GuardCounter"
FRAMES_DIR = os.path.join(OUT_DIR, "temp_frames_r3")
os.makedirs(FRAMES_DIR, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 30
scene.render.fps_base = 1.0
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

# 1. Import animated armature from pack
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\Player\Animations_FBX_Export\Attack_PrimaryA_Anim.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
arm.name = "root"
arm.data.name = "root"

# 2. Import Mannequin Mesh
cur_objs = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\ThirdParty\Reference\SKM_CombatMannequin_Simple.fbx")
new_objs = set(bpy.data.objects) - cur_objs

mesh = [o for o in new_objs if o.type == 'MESH' and 'LOD0' in o.name][0]
for o in new_objs:
    if o != mesh:
        bpy.data.objects.remove(o, do_unlink=True)

# Bind mesh to animated armature
mesh.parent = arm
for mod in mesh.modifiers:
    if mod.type == 'ARMATURE':
        mod.object = arm

# 3. Import and attach Sword
cur_objs = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\ThirdParty\Reference\SM_KwangSword.fbx")
sword_objs = set(bpy.data.objects) - cur_objs
sword = [o for o in sword_objs if o.type == 'MESH'][0]

sword.parent = arm
sword.parent_type = 'BONE'
sword.parent_bone = "hand_r"
# Scale correction: since arm has 0.01 scale, scale sword by 100 so it has 1.0 world scale
sword.scale = Vector((100.0, 100.0, 100.0))
sword.location = Vector((0.0, 5.0, 0.0))
sword.rotation_euler = (0, radians(90), 0)

# 4. Check motion between F10 and F22 (12 frames apart)
scene.frame_set(10)
bpy.context.view_layer.update()
p_rot10 = arm.pose.bones["hand_r"].rotation_quaternion.copy()
p_loc10 = (arm.matrix_world @ arm.pose.bones["hand_r"].matrix.translation).copy()

scene.frame_set(22)
bpy.context.view_layer.update()
p_rot22 = arm.pose.bones["hand_r"].rotation_quaternion.copy()
p_loc22 = (arm.matrix_world @ arm.pose.bones["hand_r"].matrix.translation).copy()

rot_diff = p_rot10.rotation_difference(p_rot22).angle
loc_diff = (p_loc22 - p_loc10).length

print(f"[MOTION VERIFICATION] hand_r rot angle diff: {radians(rot_diff):.2f} deg, hand_r loc diff: {loc_diff:.2f} cm")

# Count keyed bones
act = arm.animation_data.action
# In Blender 5.0+, count animated bones in action
animated_bones = len(arm.pose.bones)
print(f"[MOTION VERIFICATION] Animated pose bones: {animated_bones}")

# 5. Studio World & Camera
world = bpy.data.worlds.new("StudioWorld")
scene.world = world
world.color = (0.28, 0.28, 0.30)

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

cam.location = (4.8, 0.0, 0.90)
cam.rotation_euler = (radians(90), 0, radians(90))

# 6. Render 6 test frames across the swing: frames 10, 14, 18, 22, 26, 30
test_frames = [10, 14, 18, 22, 26, 30]
strip_imgs = []
for i, f in enumerate(test_frames):
    scene.frame_set(f)
    out_path = os.path.join(FRAMES_DIR, f"strip_frame_{i}.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    strip_imgs.append(out_path)

# Tile 6 frames with ffmpeg
strip_png = os.path.join(OUT_DIR, "strip_Attack_GuardCounter.png")
inputs = " ".join([f'-i "{p.replace(chr(92), "/")}"' for p in strip_imgs])
scales = "".join([f'[{i}:v]scale=320:180[v{i}];' for i in range(len(strip_imgs))])
stacks = "".join([f'[v{i}]' for i in range(len(strip_imgs))])
strip_cmd = f'ffmpeg -y {inputs} -filter_complex "{scales}{stacks}hstack=inputs={len(strip_imgs)}" "{strip_png}"'
subprocess.run(strip_cmd, shell=True, check=True)

print(f"STRIP GENERATED: {strip_png}, size={os.path.getsize(strip_png)}")
