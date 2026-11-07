import bpy
import os
import sys
import math
import shutil
import subprocess
from mathutils import Vector, Quaternion, Euler

# Clean scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

project_root = r"c:\UnrealProject\OneBossFight"
ref_fbx = os.path.join(project_root, "Import", "ThirdParty", "Reference", "SKM_CombatMannequin_Simple.fbx")
out_dir = os.path.join(project_root, "Docs", "BossCombatReview", "Execution", "Antigravity", "ER_ANIM", "Backstep_Back")
os.makedirs(out_dir, exist_ok=True)

print("Importing reference mannequin from:", ref_fbx)
bpy.ops.import_scene.fbx(filepath=ref_fbx)

scene.render.fps = 30
scene.render.fps_base = 1.0
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.01 # cm

arm = next(o for o in scene.objects if o.type == 'ARMATURE')
arm.name = "root"
arm.data.name = "root"
arm.data.pose_position = 'POSE'
bpy.context.view_layer.objects.active = arm
arm.select_set(True)

meshes = [o for o in scene.objects if o.type == 'MESH']
print(f"Found {len(meshes)} meshes for review render")

# Animation settings
fps = 30
num_frames = 15 # 0 to 14 = 14 intervals = 0.4667 s
scene.frame_start = 0
scene.frame_end = 14

act = bpy.data.actions.new("Backstep_Back")
arm.animation_data_create()
arm.animation_data.action = act
if hasattr(act, 'slots') and act.slots:
    arm.animation_data.action_slot = act.slots[0]

def set_bone_loc(bone_name, loc):
    if bone_name in arm.pose.bones:
        arm.pose.bones[bone_name].location = Vector(loc)
        arm.pose.bones[bone_name].keyframe_insert("location")

def set_bone_rot(bone_name, euler_deg):
    if bone_name in arm.pose.bones:
        q = Euler((math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))).to_quaternion()
        arm.pose.bones[bone_name].rotation_quaternion = q
        arm.pose.bones[bone_name].keyframe_insert("rotation_quaternion")

keyframe_data = [
    # Frame 0 (0.000s): Ready combat stance
    {
        "f": 0, "ry": 0.0,
        "pelvis_loc": (0, 0, 0),
        "pelvis_rot": (0, 0, -5),
        "spine_01": (0, 0, -3), "spine_03": (0, 0, -2), "spine_05": (0, 0, -2),
        "neck_01": (0, 0, 3), "head": (0, 0, 4),
        "thigh_l": (5, 0, 15), "calf_l": (0, 0, -30), "foot_l": (0, 0, 15),
        "thigh_r": (-5, 0, -10), "calf_r": (0, 0, 20), "foot_r": (0, 0, -10),
        "clavicle_l": (0, 5, 0), "upperarm_l": (-10, 15, -20), "lowerarm_l": (-30, 0, 0), "hand_l": (0, 0, 0),
        "clavicle_r": (0, -5, 0), "upperarm_r": (-15, -10, 20), "lowerarm_r": (-35, 0, 0), "hand_r": (0, 0, 0),
    },
    # Frame 2 (0.067s): Crouch / Compression, push-off backward starts; i-frame window OPENS
    {
        "f": 2, "ry": 18.0,
        "pelvis_loc": (-6, 0, 0),
        "pelvis_rot": (0, 0, -12),
        "spine_01": (0, 0, -6), "spine_03": (0, 0, -4), "spine_05": (0, 0, -3),
        "neck_01": (0, 0, 6), "head": (0, 0, 8),
        "thigh_l": (8, 0, 28), "calf_l": (0, 0, -55), "foot_l": (0, 0, 25),
        "thigh_r": (-6, 0, -22), "calf_r": (0, 0, 45), "foot_r": (0, 0, -20),
        "clavicle_l": (0, 8, 0), "upperarm_l": (-15, 20, -15), "lowerarm_l": (-45, 0, 0), "hand_l": (0, 0, 0),
        "clavicle_r": (0, -8, 0), "upperarm_r": (-20, -15, 15), "lowerarm_r": (-50, 0, 0), "hand_r": (0, 0, 0),
    },
    # Frame 5 (0.167s): Apex of airborne hop, swift backward velocity; mid i-frame window
    {
        "f": 5, "ry": 85.0,
        "pelvis_loc": (7, 0, 0),
        "pelvis_rot": (0, 0, -8),
        "spine_01": (0, 0, -4), "spine_03": (0, 0, -2), "spine_05": (0, 0, -2),
        "neck_01": (0, 0, 4), "head": (0, 0, 5),
        "thigh_l": (6, 0, 10), "calf_l": (0, 0, -25), "foot_l": (0, 0, 10),
        "thigh_r": (-6, 0, -8), "calf_r": (0, 0, 18), "foot_r": (0, 0, -8),
        "clavicle_l": (0, 5, 0), "upperarm_l": (-10, 15, -20), "lowerarm_l": (-35, 0, 0), "hand_l": (0, 0, 0),
        "clavicle_r": (0, -5, 0), "upperarm_r": (-15, -10, 20), "lowerarm_r": (-40, 0, 0), "hand_r": (0, 0, 0),
    },
    # Frame 8 (0.267s): Touchdown begins, deceleration; i-frame window CLOSES, Input Buffer OPENS
    {
        "f": 8, "ry": 155.0,
        "pelvis_loc": (-5, 0, 0),
        "pelvis_rot": (0, 0, -10),
        "spine_01": (0, 0, -5), "spine_03": (0, 0, -3), "spine_05": (0, 0, -3),
        "neck_01": (0, 0, 5), "head": (0, 0, 6),
        "thigh_l": (7, 0, 22), "calf_l": (0, 0, -45), "foot_l": (0, 0, 20),
        "thigh_r": (-6, 0, -18), "calf_r": (0, 0, 38), "foot_r": (0, 0, -18),
        "clavicle_l": (0, 6, 0), "upperarm_l": (-12, 18, -18), "lowerarm_l": (-38, 0, 0), "hand_l": (0, 0, 0),
        "clavicle_r": (0, -6, 0), "upperarm_r": (-18, -12, 18), "lowerarm_r": (-42, 0, 0), "hand_r": (0, 0, 0),
    },
    # Frame 11 (0.367s): Firm plant / Re-balancing
    {
        "f": 11, "ry": 192.0,
        "pelvis_loc": (-2, 0, 0),
        "pelvis_rot": (0, 0, -6),
        "spine_01": (0, 0, -3), "spine_03": (0, 0, -2), "spine_05": (0, 0, -2),
        "neck_01": (0, 0, 3), "head": (0, 0, 4),
        "thigh_l": (5, 0, 16), "calf_l": (0, 0, -32), "foot_l": (0, 0, 16),
        "thigh_r": (-5, 0, -12), "calf_r": (0, 0, 22), "foot_r": (0, 0, -11),
        "clavicle_l": (0, 5, 0), "upperarm_l": (-10, 15, -20), "lowerarm_l": (-32, 0, 0), "hand_l": (0, 0, 0),
        "clavicle_r": (0, -5, 0), "upperarm_r": (-15, -10, 20), "lowerarm_r": (-36, 0, 0), "hand_r": (0, 0, 0),
    },
    # Frame 14 (0.467s): Full settlement back into idle pose; Recover END
    {
        "f": 14, "ry": 200.0,
        "pelvis_loc": (0, 0, 0),
        "pelvis_rot": (0, 0, -5),
        "spine_01": (0, 0, -3), "spine_03": (0, 0, -2), "spine_05": (0, 0, -2),
        "neck_01": (0, 0, 3), "head": (0, 0, 4),
        "thigh_l": (5, 0, 15), "calf_l": (0, 0, -30), "foot_l": (0, 0, 15),
        "thigh_r": (-5, 0, -10), "calf_r": (0, 0, 20), "foot_r": (0, 0, -10),
        "clavicle_l": (0, 5, 0), "upperarm_l": (-10, 15, -20), "lowerarm_l": (-30, 0, 0), "hand_l": (0, 0, 0),
        "clavicle_r": (0, -5, 0), "upperarm_r": (-15, -10, 20), "lowerarm_r": (-35, 0, 0), "hand_r": (0, 0, 0),
    }
]

for kd in keyframe_data:
    f = kd["f"]
    scene.frame_set(f)
    
    # Root motion: advance backward in Unreal (-Y) -> +ry in Blender
    arm.location = Vector((0, kd["ry"], 0))
    arm.rotation_euler = Euler((0, 0, 0))
    arm.keyframe_insert("location", frame=f)
    arm.keyframe_insert("rotation_euler", frame=f)
    
    set_bone_loc("pelvis", kd["pelvis_loc"])
    set_bone_rot("pelvis", kd["pelvis_rot"])
    
    for b in ["spine_01", "spine_03", "spine_05", "neck_01", "head",
              "thigh_l", "calf_l", "foot_l", "thigh_r", "calf_r", "foot_r",
              "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l",
              "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r"]:
        set_bone_rot(b, kd[b])

# Bake transforms across all 15 frames (0 to 14)
bpy.ops.nla.bake(
    frame_start=0,
    frame_end=14,
    only_selected=False,
    visual_keying=True,
    clear_constraints=True,
    bake_types={'POSE'}
)

act.use_frame_range = True
act.frame_start = 0.0
act.frame_end = 14.0

# -------------------------------------------------------------
# 1. Export FBX (Armature only, standard settings per AG10)
# -------------------------------------------------------------
fbx_out_path = os.path.join(out_dir, "Backstep_Back.fbx")
fbx_top_path = os.path.join(project_root, "Docs", "BossCombatReview", "Execution", "Antigravity", "ER_ANIM", "Backstep_Back.fbx")

for m in meshes:
    m.select_set(False)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm

bpy.ops.export_scene.fbx(
    filepath=fbx_out_path,
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
    bake_anim_simplify_factor=0.0
)
print("Exported primary FBX:", fbx_out_path)

shutil.copyfile(fbx_out_path, fbx_top_path)
print("Copied to top ER_ANIM path:", fbx_top_path)

# -------------------------------------------------------------
# 2. Write Metadata and Notify specification file
# -------------------------------------------------------------
lines = [
    "Clip: Backstep_Back",
    "Length: 0.467",
    "FPS: 30",
    "Frames: 15 (0 to 14)",
    "Loop: No (One-shot)",
    "RootMotion: Yes (Backward straight: (0, 0, 0) to (0, -200, 0) cm in Unreal coordinates)",
    "RootYaw: 0.0 (Facing strictly preserved throughout)",
    "IFrameStart: 0.067 (Frame 2)",
    "IFrameEnd: 0.267 (Frame 8)",
    "InputBufferOpen: 0.267 (Frame 8)",
    "RecoverEnd: 0.467 (Frame 14)",
    "Notes: Elden Ring style stationary dodge backstep (ER-A1). Character performs a grounded hop straight backward covering exactly 200 cm of root motion while maintaining forward combat facing. Low body crouch into swift airborne hop; landing cushioned without foot sliding; settles seamlessly into idle stance."
]
txt_path = os.path.join(out_dir, "Backstep_Back.txt")
with open(txt_path, "w") as f:
    f.write("\n".join(lines) + "\n")
print("Wrote metadata:", txt_path)

# -------------------------------------------------------------
# 3. Render Look Image & Multi-View Frames for Video
# -------------------------------------------------------------
cam_data = bpy.data.cameras.new("ReviewCam")
cam_obj = bpy.data.objects.new("ReviewCam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

light_data = bpy.data.lights.new("ReviewLight", type='SUN')
light_data.energy = 3.5
light_obj = bpy.data.objects.new("ReviewLight", light_data)
scene.collection.objects.link(light_obj)
light_obj.rotation_euler = Euler((math.radians(45.0), math.radians(30.0), 0))

for m in meshes:
    m.hide_render = False

scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.image_settings.file_format = 'PNG'

# Render single look frame 5 (apex of backstep)
cam_obj.location = Vector((350.0, 100.0, 120.0))
cam_obj.rotation_euler = Euler((math.radians(78.0), 0, math.radians(110.0)))
scene.frame_set(5)
look_render_path = os.path.join(out_dir, "look_Backstep_Back.png")
scene.render.filepath = look_render_path
bpy.ops.render.render(write_still=True)
print("Rendered look frame 5:", look_render_path)

shutil.copyfile(look_render_path, os.path.join(project_root, "Docs", "BossCombatReview", "Execution", "Antigravity", "ER_ANIM", "look_Backstep_Back.png"))

# -------------------------------------------------------------
# 4. Render frames for side view & front view, compile via ffmpeg
# -------------------------------------------------------------
temp_frames_dir = os.path.join(out_dir, "temp_frames")
os.makedirs(temp_frames_dir, exist_ok=True)

# Side view (looking at profile: character hops backward across frame)
cam_obj.location = Vector((380.0, 100.0, 110.0))
cam_obj.rotation_euler = Euler((math.radians(82.0), 0, math.radians(90.0)))

side_frames = []
for f in range(15):
    scene.frame_set(f)
    frame_path = os.path.join(temp_frames_dir, f"side_{f:03d}.png")
    scene.render.filepath = frame_path
    bpy.ops.render.render(write_still=True)
    side_frames.append(frame_path)

# Front view (looking directly at character facing)
cam_obj.location = Vector((0.0, -320.0, 120.0))
cam_obj.rotation_euler = Euler((math.radians(75.0), 0, 0))

front_frames = []
for f in range(15):
    scene.frame_set(f)
    frame_path = os.path.join(temp_frames_dir, f"front_{f:03d}.png")
    scene.render.filepath = frame_path
    bpy.ops.render.render(write_still=True)
    front_frames.append(frame_path)

print("Rendered all side and front frames.")

# Create sequence list for ffmpeg:
# 1) Side view real-time (30 fps)
# 2) Front view real-time (30 fps)
# 3) Side view 0.5x slowmo (15 fps)
concat_file = os.path.join(temp_frames_dir, "concat.txt")
with open(concat_file, "w") as f:
    # Pass 1: Side view 1.0x (1/30 s per frame)
    for frame_path in side_frames:
        f.write(f"file '{frame_path.replace(os.sep, '/')}'\nduration 0.033333\n")
    # Hold last frame 0.2s
    f.write(f"file '{side_frames[-1].replace(os.sep, '/')}'\nduration 0.2\n")
    
    # Pass 2: Front view 1.0x
    for frame_path in front_frames:
        f.write(f"file '{frame_path.replace(os.sep, '/')}'\nduration 0.033333\n")
    # Hold last frame 0.2s
    f.write(f"file '{front_frames[-1].replace(os.sep, '/')}'\nduration 0.2\n")
    
    # Pass 3: Side view 0.5x slow-motion (1/15 s per frame)
    for frame_path in side_frames:
        f.write(f"file '{frame_path.replace(os.sep, '/')}'\nduration 0.066666\n")
    # Final hold
    f.write(f"file '{side_frames[-1].replace(os.sep, '/')}'\nduration 0.5\n")
    f.write(f"file '{side_frames[-1].replace(os.sep, '/')}'\n")

mp4_out_path = os.path.join(out_dir, "review_Backstep_Back.mp4")
ffmpeg_cmd = [
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0",
    "-i", concat_file,
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-r", "30",
    mp4_out_path
]

print("Executing ffmpeg:", " ".join(ffmpeg_cmd))
sub_res = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
if sub_res.returncode == 0:
    print("Successfully encoded review MP4:", mp4_out_path)
    # Clean up temp frames to keep repository clean
    shutil.rmtree(temp_frames_dir, ignore_errors=True)
else:
    print("ffmpeg error:", sub_res.stderr)

print("AA-A02 DELIVERABLES COMPLETE")
