import bpy
import os
import subprocess
from math import radians
from mathutils import Vector, Quaternion

OUT_DIR = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\ER_ANIM\Attack_GuardCounter"
os.makedirs(OUT_DIR, exist_ok=True)
FRAMES_DIR = os.path.join(OUT_DIR, "temp_frames_r2")
os.makedirs(FRAMES_DIR, exist_ok=True)

# 1. Clean scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 30
scene.render.fps_base = 1.0

# 2. Import BlockLoop
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\Player\Animations_FBX_Export\BlockLoop.fbx")
arm_block = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
act_block = arm_block.animation_data.action
act_block.name = "act_block"

# 3. Import Attack_PrimaryA
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\Player\Animations_FBX_Export\Attack_PrimaryA_Anim.fbx")
arm_attack = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != arm_block][0]
act_attack = arm_attack.animation_data.action
act_attack.name = "act_attack"

# Clean duplicate armature
bpy.data.objects.remove(arm_attack, do_unlink=True)
arm = arm_block
arm.name = "root"
arm.data.name = "root"

# 4. Import weapon SM_KwangSword
sword_path = r"c:\UnrealProject\OneBossFight\Import\ThirdParty\Reference\SM_KwangSword.fbx"
sword = None
if os.path.exists(sword_path):
    bpy.ops.import_scene.fbx(filepath=sword_path)
    swords = [o for o in bpy.data.objects if o.type == 'MESH' and o != arm]
    if swords:
        sword = swords[0]
        sword.parent = arm
        sword.parent_type = 'BONE'
        sword.parent_bone = "hand_r"
        # Adjust local sword rotation/position to fit naturally in hand
        sword.location = Vector((0.0, 0.05, 0.0))
        sword.rotation_euler = (radians(0), radians(90), radians(0))

# Helper to sample snapshot
def get_snapshot(action, frame):
    arm.animation_data.action = action
    scene.frame_set(int(frame))
    bpy.context.view_layer.update()
    snap = {}
    for pb in arm.pose.bones:
        snap[pb.name] = {
            'loc': pb.location.copy(),
            'quat': pb.rotation_quaternion.copy(),
            'scale': pb.scale.copy(),
        }
    return snap

# Pre-sample snapshots
# Block loop frame 1
snap_block = get_snapshot(act_block, 1)

# Attack key snapshots:
# F15 (anticipation apex), F21 (swing down), F25 (impact), F31 (follow-through), F41 (combat recovery)
snap_att_15 = get_snapshot(act_attack, 15)
snap_att_19 = get_snapshot(act_attack, 19)
snap_att_23 = get_snapshot(act_attack, 23)
snap_att_25 = get_snapshot(act_attack, 25)
snap_att_29 = get_snapshot(act_attack, 29)
snap_att_35 = get_snapshot(act_attack, 35)
snap_att_41 = get_snapshot(act_attack, 41)

# 5. Create new action for Guard Counter (25 frames, 0 to 24)
new_act = bpy.data.actions.new(name="AN_ER_Attack_GuardCounter")
arm.animation_data.action = new_act

TOTAL_FRAMES = 25

for f in range(TOTAL_FRAMES):
    scene.frame_set(f)
    
    # Motion mapping:
    # F0..F6: Block pose
    # F7..F9: Blend block -> attack anticipation F15
    # F10..F12: Acceleration forward (F15 -> F23)
    # F13: Impact (F25)
    # F14..F18: Follow-through (F25 -> F35)
    # F19..F24: Recovery into combat stance (F35 -> F41)
    
    if f <= 6:
        curr_snap = snap_block
    elif f == 7:
        # 33% blend to F15
        alpha = 0.33
        curr_snap = {b: {'loc': snap_block[b]['loc'].lerp(snap_att_15[b]['loc'], alpha),
                         'quat': snap_block[b]['quat'].slerp(snap_att_15[b]['quat'], alpha),
                         'scale': snap_block[b]['scale']} for b in snap_block}
    elif f == 8:
        # 66% blend to F15
        alpha = 0.66
        curr_snap = {b: {'loc': snap_block[b]['loc'].lerp(snap_att_15[b]['loc'], alpha),
                         'quat': snap_block[b]['quat'].slerp(snap_att_15[b]['quat'], alpha),
                         'scale': snap_block[b]['scale']} for b in snap_block}
    elif f == 9:
        curr_snap = snap_att_15
    elif f == 10:
        alpha = 0.5
        curr_snap = {b: {'loc': snap_att_15[b]['loc'].lerp(snap_att_19[b]['loc'], alpha),
                         'quat': snap_att_15[b]['quat'].slerp(snap_att_19[b]['quat'], alpha),
                         'scale': snap_att_15[b]['scale']} for b in snap_att_15}
    elif f == 11:
        curr_snap = snap_att_19
    elif f == 12:
        curr_snap = snap_att_23
    elif f == 13: # IMPACT
        curr_snap = snap_att_25
    elif f == 14:
        curr_snap = snap_att_29
    elif f <= 18:
        alpha = (f - 14) / 4.0
        curr_snap = {b: {'loc': snap_att_29[b]['loc'].lerp(snap_att_35[b]['loc'], alpha),
                         'quat': snap_att_29[b]['quat'].slerp(snap_att_35[b]['quat'], alpha),
                         'scale': snap_att_29[b]['scale']} for b in snap_att_29}
    else:
        alpha = (f - 18) / 6.0
        curr_snap = {b: {'loc': snap_att_35[b]['loc'].lerp(snap_att_41[b]['loc'], alpha),
                         'quat': snap_att_35[b]['quat'].slerp(snap_att_41[b]['quat'], alpha),
                         'scale': snap_att_35[b]['scale']} for b in snap_att_35}

    # Apply to pose bones
    for b_name, data in curr_snap.items():
        pb = arm.pose.bones.get(b_name)
        if pb:
            pb.rotation_mode = 'QUATERNION'
            pb.location = data['loc']
            pb.rotation_quaternion = data['quat']
            pb.scale = data['scale']
            pb.keyframe_insert("location", frame=f)
            pb.keyframe_insert("rotation_quaternion", frame=f)

    # Root motion: lunge step forward 100 cm (+Y) between F6 and F14
    if f <= 6:
        y_trans = 0.0
    elif f >= 14:
        y_trans = 1.0  # 1.0 m = 100 cm in Blender metric
    else:
        # Smooth hermite step
        t = (f - 6) / 8.0
        y_trans = (3 * t**2 - 2 * t**3) * 1.0
        
    arm.location = Vector((0.0, y_trans, 0.0))
    arm.rotation_euler = (0.0, 0.0, 0.0)
    arm.keyframe_insert("location", frame=f)
    arm.keyframe_insert("rotation_euler", frame=f)

print("Authoring complete: 25 frames keyframed!")

# 6. Set up Studio lighting & Camera
world = bpy.data.worlds.new("StudioWorld")
scene.world = world
world.color = (0.28, 0.28, 0.30)

def add_sun(name, loc, rot, energy, color):
    light_data = bpy.data.lights.new(name=name, type='SUN')
    light_data.energy = energy
    light_data.color = color
    light_obj = bpy.data.objects.new(name=name, object_data=light_data)
    scene.collection.objects.link(light_obj)
    light_obj.location = loc
    light_obj.rotation_euler = rot

add_sun("KeySun", (5.0, -5.0, 10.0), (radians(45), radians(15), radians(-45)), 3.0, (1.0, 0.98, 0.95))
add_sun("FillSun", (-6.0, -4.0, 6.0), (radians(60), radians(-20), radians(120)), 1.2, (0.75, 0.85, 1.0))
add_sun("RimSun", (0.0, 7.0, 6.0), (radians(-45), 0, radians(180)), 2.5, (1.0, 1.0, 1.0))

cam_data = bpy.data.cameras.new("ReviewCam")
cam_data.lens = 45.0
cam = bpy.data.objects.new("ReviewCam", object_data=cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

# Render side frames
for f in range(TOTAL_FRAMES):
    scene.frame_set(f)
    arm_y = arm.location.y
    cam.location = (4.8, arm_y, 0.90)
    cam.rotation_euler = (radians(90), 0, radians(90))
    scene.render.filepath = os.path.join(FRAMES_DIR, f"side_{f:03d}.png")
    bpy.ops.render.render(write_still=True)

# Render front frames
for f in range(TOTAL_FRAMES):
    scene.frame_set(f)
    arm_y = arm.location.y
    cam.location = (0.0, arm_y - 4.5, 0.90)
    cam.rotation_euler = (radians(90), 0, 0.0)
    scene.render.filepath = os.path.join(FRAMES_DIR, f"front_{f:03d}.png")
    bpy.ops.render.render(write_still=True)

# Save look grab
look_png = os.path.join(OUT_DIR, "look_Attack_GuardCounter.png")
import shutil
shutil.copyfile(os.path.join(FRAMES_DIR, "side_013.png"), look_png)

# Compile review MP4 with ffmpeg
mp4_path = os.path.join(OUT_DIR, "review_Attack_GuardCounter.mp4")
concat_txt = os.path.join(FRAMES_DIR, "concat.txt")
with open(concat_txt, "w") as cf:
    # Pass 1: Side 1.0x
    for f in range(TOTAL_FRAMES):
        p = os.path.join(FRAMES_DIR, f"side_{f:03d}.png").replace("\\", "/")
        cf.write(f"file '{p}'\nduration 0.033333\n")
    # Pass 2: Front 1.0x
    for f in range(TOTAL_FRAMES):
        p = os.path.join(FRAMES_DIR, f"front_{f:03d}.png").replace("\\", "/")
        cf.write(f"file '{p}'\nduration 0.033333\n")
    # Pass 3: Side 0.5x Slowmo
    for f in range(TOTAL_FRAMES):
        p = os.path.join(FRAMES_DIR, f"side_{f:03d}.png").replace("\\", "/")
        cf.write(f"file '{p}'\nduration 0.066666\n")
    cf.write(f"file '{os.path.join(FRAMES_DIR, 'side_024.png').replace('/', '/')}'\n")

cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_txt}" -c:v libx264 -pix_fmt yuv420p -r 30 -crf 18 "{mp4_path}"'
subprocess.run(cmd, shell=True, check=True)

# Export FBX
fbx_path = os.path.join(OUT_DIR, "Attack_GuardCounter.fbx")
# Temporarily unlink sword for clean FBX
if sword:
    bpy.data.objects.remove(sword, do_unlink=True)

bpy.ops.export_scene.fbx(
    filepath=fbx_path,
    check_existing=False,
    use_selection=True,
    global_scale=1.0,
    apply_unit_scale=False,
    apply_scale_options='FBX_SCALE_NONE',
    bake_space_transform=False,
    object_types={'ARMATURE'},
    use_mesh_modifiers=False,
    mesh_smooth_type='OFF',
    use_subsurf=False,
    use_armature_deform_only=True,
    add_leaf_bones=False,
    primary_bone_axis='Y',
    secondary_bone_axis='X',
    armature_nodetype='NULL',
    bake_anim=True,
    bake_anim_use_all_bones=True,
    bake_anim_use_nla_strips=False,
    bake_anim_use_all_actions=False,
    bake_anim_force_startend_keying=True,
    bake_anim_step=1.0,
    bake_anim_simplify_factor=0.0,
    axis_forward='-Z',
    axis_up='Y'
)

# Generate 6-frame strip PNG (ffmpeg tile)
strip_path = os.path.join(OUT_DIR, "strip_Attack_GuardCounter.png")
# Select 6 key frames from side pass: F0, F6, F9, F13, F18, F24
# In concat: frames 0..24 are side pass
strip_cmd = f'ffmpeg -y -i "{mp4_path}" -vf "select=\'eq(n\,0)+eq(n\,6)+eq(n\,9)+eq(n\,13)+eq(n\,18)+eq(n\,24)\',scale=320:180,tile=6x1" "{strip_path}"'
subprocess.run(strip_cmd, shell=True, check=True)

print(f"R2 TEST COMPLETE for Attack_GuardCounter! FBX={os.path.getsize(fbx_path)}, MP4={os.path.getsize(mp4_path)}, Strip={os.path.getsize(strip_path)}")
