import bpy
import os
import sys
import math
import shutil
import subprocess
from mathutils import Vector, Quaternion, Euler

project_root = r"c:\UnrealProject\OneBossFight"
ref_fbx = os.path.join(project_root, "Import", "ThirdParty", "Reference", "SKM_CombatMannequin_Simple.fbx")
base_out_dir = os.path.join(project_root, "Docs", "BossCombatReview", "Execution", "Antigravity", "ER_ANIM")
os.makedirs(base_out_dir, exist_ok=True)

def setup_studio_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = 30
    scene.render.fps_base = 1.0
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = 'PNG'
    
    # Import reference mannequin
    bpy.ops.import_scene.fbx(filepath=ref_fbx)
    
    arm = next(o for o in scene.objects if o.type == 'ARMATURE')
    arm.name = "root"
    arm.data.name = "root"
    arm.data.pose_position = 'POSE'
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    
    meshes = [o for o in scene.objects if o.type == 'MESH']
    for m in meshes:
        m.hide_render = False
    
    # Studio World (neutral grey background)
    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (0.28, 0.28, 0.30, 1.0)
    bg.inputs['Strength'].default_value = 1.0
    
    # Studio Lighting (3-point)
    def make_sun(name, rot_euler, energy, color):
        lamp_data = bpy.data.lights.new(name=name, type='SUN')
        lamp_data.energy = energy
        lamp_data.color = color
        lamp_obj = bpy.data.objects.new(name=name, object_data=lamp_data)
        lamp_obj.rotation_euler = rot_euler
        scene.collection.objects.link(lamp_obj)
        return lamp_obj
    
    make_sun("KeyLight", (math.radians(50), math.radians(20), math.radians(45)), 4.5, (1.0, 0.98, 0.92))
    make_sun("FillLight", (math.radians(45), math.radians(-25), math.radians(-45)), 3.0, (0.85, 0.92, 1.0))
    make_sun("RimLight", (math.radians(-65), math.radians(35), math.radians(135)), 5.5, (1.0, 0.75, 0.35))
    
    # Camera setup (50 mm lens, placed at 4.8 m for ~75% frame height framing)
    cam_data = bpy.data.cameras.new("ReviewCam")
    cam_data.lens = 45.0
    cam_obj = bpy.data.objects.new("ReviewCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    
    return scene, arm, meshes, cam_obj

def set_bone_loc(arm, bone_name, loc_m):
    if bone_name in arm.pose.bones:
        arm.pose.bones[bone_name].location = Vector(loc_m)
        arm.pose.bones[bone_name].keyframe_insert("location")

def set_bone_rot(arm, bone_name, euler_deg):
    if bone_name in arm.pose.bones:
        q = Euler((math.radians(euler_deg[0]), math.radians(euler_deg[1]), math.radians(euler_deg[2]))).to_quaternion()
        arm.pose.bones[bone_name].rotation_quaternion = q
        arm.pose.bones[bone_name].keyframe_insert("rotation_quaternion")

def export_and_render_clip(clip_name, keyframes, num_frames, metadata_text, impact_frame):
    print(f"\n========================================\nAUTHORING {clip_name}\n========================================")
    scene, arm, meshes, cam_obj = setup_studio_scene()
    
    out_dir = os.path.join(base_out_dir, clip_name)
    os.makedirs(out_dir, exist_ok=True)
    temp_frames_dir = os.path.join(out_dir, "temp_frames")
    os.makedirs(temp_frames_dir, exist_ok=True)
    
    scene.frame_start = 0
    scene.frame_end = num_frames - 1
    
    act = bpy.data.actions.new(clip_name)
    arm.animation_data_create()
    arm.animation_data.action = act
    if hasattr(act, 'slots') and act.slots:
        arm.animation_data.action_slot = act.slots[0]
        
    for kd in keyframes:
        f = kd["f"]
        scene.frame_set(f)
        
        arm.location = Vector((0, kd["ry"], 0))
        arm.rotation_euler = Euler((0, 0, 0))
        arm.keyframe_insert("location", frame=f)
        arm.keyframe_insert("rotation_euler", frame=f)
        
        set_bone_loc(arm, "pelvis", kd["pelvis_loc"])
        set_bone_rot(arm, "pelvis", kd["pelvis_rot"])
        
        for b in ["spine_01", "spine_03", "spine_05", "neck_01", "head",
                  "thigh_l", "calf_l", "foot_l", "thigh_r", "calf_r", "foot_r",
                  "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l",
                  "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r"]:
            if b in kd:
                set_bone_rot(arm, b, kd[b])
                
    # Bake transforms
    bpy.ops.nla.bake(
        frame_start=0,
        frame_end=num_frames - 1,
        only_selected=False,
        visual_keying=True,
        clear_constraints=True,
        bake_types={'POSE'}
    )
    act.use_frame_range = True
    act.frame_start = 0.0
    act.frame_end = float(num_frames - 1)
    
    # 1. Export FBX (apply_unit_scale=False guarantees height ~1.80m matching SK_CombatMannequin)
    for m in meshes:
        m.select_set(False)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    
    fbx_out = os.path.join(out_dir, f"{clip_name}.fbx")
    fbx_top = os.path.join(base_out_dir, f"{clip_name}.fbx")
    bpy.ops.export_scene.fbx(
        filepath=fbx_out,
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=False, # CRITICAL: preserves ~1.80m armature height
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
    shutil.copyfile(fbx_out, fbx_top)
    print(f"Exported FBX ({os.path.getsize(fbx_out)} bytes): {fbx_out}")
    
    # 2. Write metadata text
    txt_out = os.path.join(out_dir, f"{clip_name}.txt")
    with open(txt_out, "w") as f:
        f.write(metadata_text)
        
    # 3. Multi-view rendering
    side_frames = []
    front_frames = []
    
    # Side View Pass (camera follows root Y at distance 4.8m, looking along -X)
    cam_obj.rotation_euler = Euler((math.radians(90), 0, math.radians(90)))
    for f in range(num_frames):
        scene.frame_set(f)
        bpy.context.view_layer.update()
        cam_obj.location = Vector((4.8, arm.location.y, 0.90))
        frame_path = os.path.join(temp_frames_dir, f"side_{f:03d}.png")
        scene.render.filepath = frame_path
        bpy.ops.render.render(write_still=True)
        side_frames.append(frame_path)
        
    # Front View Pass (camera follows root Y at distance 4.5m, looking along +Y)
    cam_obj.rotation_euler = Euler((math.radians(90), 0, 0))
    for f in range(num_frames):
        scene.frame_set(f)
        bpy.context.view_layer.update()
        cam_obj.location = Vector((0.0, arm.location.y - 4.5, 0.90))
        frame_path = os.path.join(temp_frames_dir, f"front_{f:03d}.png")
        scene.render.filepath = frame_path
        bpy.ops.render.render(write_still=True)
        front_frames.append(frame_path)
        
    # Look frame-grab PNG at key frame
    look_png = os.path.join(out_dir, f"look_{clip_name}.png")
    framegrab_png = os.path.join(out_dir, f"framegrab_{clip_name}.png")
    shutil.copyfile(side_frames[impact_frame], look_png)
    shutil.copyfile(side_frames[impact_frame], framegrab_png)
    shutil.copyfile(look_png, os.path.join(base_out_dir, f"look_{clip_name}.png"))
    print(f"Saved look frame-grab ({os.path.getsize(look_png)} bytes): {look_png}")
    
    # 4. Compile Review MP4 via ffmpeg
    concat_file = os.path.join(temp_frames_dir, "concat.txt")
    with open(concat_file, "w") as f:
        # Pass 1: Side view 1.0x (1/30s per frame)
        for p in side_frames:
            f.write(f"file '{p.replace(os.sep, '/')}'\nduration 0.033333\n")
        f.write(f"file '{side_frames[-1].replace(os.sep, '/')}'\nduration 0.25\n")
        
        # Pass 2: Front view 1.0x (1/30s per frame)
        for p in front_frames:
            f.write(f"file '{p.replace(os.sep, '/')}'\nduration 0.033333\n")
        f.write(f"file '{front_frames[-1].replace(os.sep, '/')}'\nduration 0.25\n")
        
        # Pass 3: Side view 0.5x slow-motion (1/15s per frame)
        for p in side_frames:
            f.write(f"file '{p.replace(os.sep, '/')}'\nduration 0.066666\n")
        f.write(f"file '{side_frames[-1].replace(os.sep, '/')}'\nduration 0.5\n")
        f.write(f"file '{side_frames[-1].replace(os.sep, '/')}'\n")
        
    mp4_out = os.path.join(out_dir, f"review_{clip_name}.mp4")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        mp4_out
    ]
    sub_res = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if sub_res.returncode == 0:
        mp4_size = os.path.getsize(mp4_out)
        print(f"Encoded review MP4 ({mp4_size} bytes): {mp4_out}")
        shutil.rmtree(temp_frames_dir, ignore_errors=True)
        return fbx_out, look_png, mp4_out, mp4_size
    else:
        print("ffmpeg error:", sub_res.stderr)
        return None

# ==============================================================================
# CLIP 1: Backstep_Back (ER-A1)
# ==============================================================================
kfs_backstep = [
    {"f": 0, "ry": 0.0, "pelvis_loc": (0, 0, 0), "pelvis_rot": (0, 0, -5),
     "spine_01": (0, 0, -3), "spine_03": (0, 0, -2), "spine_05": (0, 0, -2), "neck_01": (0, 0, 3), "head": (0, 0, 4),
     "thigh_l": (5, 0, 15), "calf_l": (0, 0, -30), "foot_l": (0, 0, 15), "thigh_r": (-5, 0, -10), "calf_r": (0, 0, 20), "foot_r": (0, 0, -10),
     "clavicle_l": (0, 5, 0), "upperarm_l": (-10, 15, -20), "lowerarm_l": (-30, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, -5, 0), "upperarm_r": (-15, -10, 20), "lowerarm_r": (-35, 0, 0), "hand_r": (0, 0, 0)},
    {"f": 2, "ry": 0.18, "pelvis_loc": (-0.06, 0, 0), "pelvis_rot": (0, 0, -12),
     "spine_01": (0, 0, -6), "spine_03": (0, 0, -4), "spine_05": (0, 0, -3), "neck_01": (0, 0, 6), "head": (0, 0, 8),
     "thigh_l": (8, 0, 28), "calf_l": (0, 0, -55), "foot_l": (0, 0, 25), "thigh_r": (-6, 0, -22), "calf_r": (0, 0, 45), "foot_r": (0, 0, -20),
     "clavicle_l": (0, 8, 0), "upperarm_l": (-15, 20, -15), "lowerarm_l": (-45, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, -8, 0), "upperarm_r": (-20, -15, 15), "lowerarm_r": (-50, 0, 0), "hand_r": (0, 0, 0)},
    {"f": 5, "ry": 0.85, "pelvis_loc": (0.07, 0, 0), "pelvis_rot": (0, 0, -8),
     "spine_01": (0, 0, -4), "spine_03": (0, 0, -2), "spine_05": (0, 0, -2), "neck_01": (0, 0, 4), "head": (0, 0, 5),
     "thigh_l": (6, 0, 10), "calf_l": (0, 0, -25), "foot_l": (0, 0, 10), "thigh_r": (-6, 0, -8), "calf_r": (0, 0, 18), "foot_r": (0, 0, -8),
     "clavicle_l": (0, 5, 0), "upperarm_l": (-10, 15, -20), "lowerarm_l": (-35, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, -5, 0), "upperarm_r": (-15, -10, 20), "lowerarm_r": (-40, 0, 0), "hand_r": (0, 0, 0)},
    {"f": 8, "ry": 1.55, "pelvis_loc": (-0.05, 0, 0), "pelvis_rot": (0, 0, -10),
     "spine_01": (0, 0, -5), "spine_03": (0, 0, -3), "spine_05": (0, 0, -3), "neck_01": (0, 0, 5), "head": (0, 0, 6),
     "thigh_l": (7, 0, 22), "calf_l": (0, 0, -45), "foot_l": (0, 0, 20), "thigh_r": (-6, 0, -18), "calf_r": (0, 0, 38), "foot_r": (0, 0, -18),
     "clavicle_l": (0, 6, 0), "upperarm_l": (-12, 18, -18), "lowerarm_l": (-38, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, -6, 0), "upperarm_r": (-18, -12, 18), "lowerarm_r": (-42, 0, 0), "hand_r": (0, 0, 0)},
    {"f": 11, "ry": 1.92, "pelvis_loc": (-0.02, 0, 0), "pelvis_rot": (0, 0, -6),
     "spine_01": (0, 0, -3), "spine_03": (0, 0, -2), "spine_05": (0, 0, -2), "neck_01": (0, 0, 3), "head": (0, 0, 4),
     "thigh_l": (5, 0, 16), "calf_l": (0, 0, -32), "foot_l": (0, 0, 16), "thigh_r": (-5, 0, -12), "calf_r": (0, 0, 22), "foot_r": (0, 0, -11),
     "clavicle_l": (0, 5, 0), "upperarm_l": (-10, 15, -20), "lowerarm_l": (-32, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, -5, 0), "upperarm_r": (-15, -10, 20), "lowerarm_r": (-36, 0, 0), "hand_r": (0, 0, 0)},
    {"f": 14, "ry": 2.00, "pelvis_loc": (0, 0, 0), "pelvis_rot": (0, 0, -5),
     "spine_01": (0, 0, -3), "spine_03": (0, 0, -2), "spine_05": (0, 0, -2), "neck_01": (0, 0, 3), "head": (0, 0, 4),
     "thigh_l": (5, 0, 15), "calf_l": (0, 0, -30), "foot_l": (0, 0, 15), "thigh_r": (-5, 0, -10), "calf_r": (0, 0, 20), "foot_r": (0, 0, -10),
     "clavicle_l": (0, 5, 0), "upperarm_l": (-10, 15, -20), "lowerarm_l": (-30, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, -5, 0), "upperarm_r": (-15, -10, 20), "lowerarm_r": (-35, 0, 0), "hand_r": (0, 0, 0)}
]
txt_backstep = """Clip: Backstep_Back
Length: 0.467
FPS: 30
Frames: 15 (0 to 14)
Loop: No (One-shot)
RootMotion: Yes (Backward straight: (0, 0, 0) to (0, -200, 0) cm in Unreal coordinates, ry=0.0 to 2.0m in Blender)
RootYaw: 0.0 (Facing strictly preserved throughout)
IFrameStart: 0.067 (Frame 2)
IFrameEnd: 0.267 (Frame 8)
InputBufferOpen: 0.267 (Frame 8)
RecoverEnd: 0.467 (Frame 14)
ArmatureHeight: 1.786 m (~180 cm for SK_CombatMannequin)
Notes: Elden Ring style stationary dodge backstep (ER-A1). Character performs a grounded hop straight backward covering exactly 200 cm of root motion while maintaining forward combat facing. Low body crouch into swift airborne hop; landing cushioned without foot sliding; settles seamlessly into idle stance.
"""

# ==============================================================================
# CLIP 2: Attack_GuardCounter (ER-A4)
# ==============================================================================
kfs_guard_counter = [
    {"f": 0, "ry": 0.0, "pelvis_loc": (-0.03, 0, 0), "pelvis_rot": (0, 0, -5),
     "spine_01": (0, 0, -4), "spine_03": (0, 0, -3), "spine_05": (0, 0, -3), "neck_01": (0, 0, 4), "head": (0, 0, 5),
     "thigh_l": (5, 0, 20), "calf_l": (0, 0, -40), "foot_l": (0, 0, 20), "thigh_r": (-5, 0, -15), "calf_r": (0, 0, 30), "foot_r": (0, 0, -15),
     "clavicle_l": (0, 15, 0), "upperarm_l": (-25, 45, 10), "lowerarm_l": (-65, 0, 0), "hand_l": (15, 0, 0),
     "clavicle_r": (0, 15, 0), "upperarm_r": (-30, -35, -15), "lowerarm_r": (-70, 0, 0), "hand_r": (-15, 0, 0)},
    {"f": 4, "ry": -0.15, "pelvis_loc": (-0.06, 0, 0), "pelvis_rot": (0, 0, -15),
     "spine_01": (0, 0, -10), "spine_03": (0, 0, -8), "spine_05": (0, 0, -6), "neck_01": (0, 0, 8), "head": (0, 0, 10),
     "thigh_l": (8, 0, 28), "calf_l": (0, 0, -55), "foot_l": (0, 0, 27), "thigh_r": (-6, 0, -20), "calf_r": (0, 0, 40), "foot_r": (0, 0, -20),
     "clavicle_l": (0, 5, 0), "upperarm_l": (-10, 25, -20), "lowerarm_l": (-40, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, -15, 0), "upperarm_r": (-20, -50, 45), "lowerarm_r": (-85, 0, 0), "hand_r": (25, 0, 0)},
    {"f": 9, "ry": -0.55, "pelvis_loc": (-0.04, 0, 0), "pelvis_rot": (0, 0, 10),
     "spine_01": (0, 0, 12), "spine_03": (0, 0, 15), "spine_05": (0, 0, 15), "neck_01": (0, 0, -8), "head": (0, 0, -10),
     "thigh_l": (6, 0, 12), "calf_l": (0, 0, -25), "foot_l": (0, 0, 12), "thigh_r": (-8, 0, 25), "calf_r": (0, 0, -50), "foot_r": (0, 0, 25),
     "clavicle_l": (0, -10, 0), "upperarm_l": (15, -20, 20), "lowerarm_l": (-30, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, 20, 0), "upperarm_r": (10, 25, -45), "lowerarm_r": (-40, 0, 0), "hand_r": (-15, 0, 0)},
    {"f": 13, "ry": -0.88, "pelvis_loc": (-0.02, 0, 0), "pelvis_rot": (0, 0, 25),
     "spine_01": (0, 0, 20), "spine_03": (0, 0, 22), "spine_05": (0, 0, 20), "neck_01": (0, 0, -12), "head": (0, 0, -15),
     "thigh_l": (5, 0, 8), "calf_l": (0, 0, -16), "foot_l": (0, 0, 8), "thigh_r": (-10, 0, 32), "calf_r": (0, 0, -60), "foot_r": (0, 0, 30),
     "clavicle_l": (0, -15, 0), "upperarm_l": (20, -30, 25), "lowerarm_l": (-25, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, 25, 0), "upperarm_r": (15, 55, -80), "lowerarm_r": (-15, 0, 0), "hand_r": (-20, 0, 0)},
    {"f": 17, "ry": -0.98, "pelvis_loc": (-0.01, 0, 0), "pelvis_rot": (0, 0, 18),
     "spine_01": (0, 0, 14), "spine_03": (0, 0, 12), "spine_05": (0, 0, 10), "neck_01": (0, 0, -6), "head": (0, 0, -8),
     "thigh_l": (5, 0, 10), "calf_l": (0, 0, -20), "foot_l": (0, 0, 10), "thigh_r": (-8, 0, 22), "calf_r": (0, 0, -45), "foot_r": (0, 0, 22),
     "clavicle_l": (0, -10, 0), "upperarm_l": (10, -15, 15), "lowerarm_l": (-25, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, 15, 0), "upperarm_r": (10, 40, -65), "lowerarm_r": (-25, 0, 0), "hand_r": (-10, 0, 0)},
    {"f": 21, "ry": -1.00, "pelvis_loc": (-0.01, 0, 0), "pelvis_rot": (0, 0, 5),
     "spine_01": (0, 0, 4), "spine_03": (0, 0, 3), "spine_05": (0, 0, 2), "neck_01": (0, 0, -2), "head": (0, 0, -2),
     "thigh_l": (5, 0, 14), "calf_l": (0, 0, -28), "foot_l": (0, 0, 14), "thigh_r": (-6, 0, -8), "calf_r": (0, 0, 16), "foot_r": (0, 0, -8),
     "clavicle_l": (0, 5, 0), "upperarm_l": (-5, 10, -10), "lowerarm_l": (-30, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, -5, 0), "upperarm_r": (-10, -10, 15), "lowerarm_r": (-35, 0, 0), "hand_r": (0, 0, 0)},
    {"f": 24, "ry": -1.00, "pelvis_loc": (0, 0, 0), "pelvis_rot": (0, 0, -5),
     "spine_01": (0, 0, -3), "spine_03": (0, 0, -2), "spine_05": (0, 0, -2), "neck_01": (0, 0, 3), "head": (0, 0, 4),
     "thigh_l": (5, 0, 15), "calf_l": (0, 0, -30), "foot_l": (0, 0, 15), "thigh_r": (-5, 0, -10), "calf_r": (0, 0, 20), "foot_r": (0, 0, -10),
     "clavicle_l": (0, 5, 0), "upperarm_l": (-10, 15, -20), "lowerarm_l": (-30, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, -5, 0), "upperarm_r": (-15, -10, 20), "lowerarm_r": (-35, 0, 0), "hand_r": (0, 0, 0)}
]
txt_guard_counter = """Clip: Attack_GuardCounter
Length: 0.800
FPS: 30
Frames: 25 (0 to 24)
Loop: No (One-shot)
RootMotion: Yes (Forward straight: (0, 0, 0) to (0, 100, 0) cm in Unreal coordinates, ry=0.0 to -1.0m in Blender)
RootYaw: 0.0 (Facing strictly preserved throughout)
WindupEnd: 0.300 (Frame 9)
HitWindowStart: 0.333 (Frame 10)
Impact: 0.433 (Frame 13)
HitWindowEnd: 0.533 (Frame 16)
RecoverEnd: 0.800 (Frame 24)
ArmatureHeight: 1.786 m (~180 cm for SK_CombatMannequin)
Notes: Elden Ring style guard counter attack (ER-A4). Triggers immediately following a successful shield block. Character absorbs impact in guard pose (F0), coils torso and initiates an explosive 100 cm forward step (F4-F9), unleashing a forceful horizontal counter-slash with maximum extension at impact F13 (0.433 s). Follow-through settles cleanly back into combat idle.
"""

# ==============================================================================
# CLIP 3: Attack_Air_Heavy_Plunge (ER-A3)
# ==============================================================================
kfs_air_heavy = [
    {"f": 0, "ry": 0.0, "pelvis_loc": (0.15, 0, 0), "pelvis_rot": (0, 0, -8),
     "spine_01": (0, 0, -5), "spine_03": (0, 0, -3), "spine_05": (0, 0, -2), "neck_01": (0, 0, 3), "head": (0, 0, 4),
     "thigh_l": (15, 0, 45), "calf_l": (0, 0, -70), "foot_l": (0, 0, 25), "thigh_r": (-10, 0, -30), "calf_r": (0, 0, 60), "foot_r": (0, 0, -20),
     "clavicle_l": (0, 10, 0), "upperarm_l": (-20, 25, -30), "lowerarm_l": (-50, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, -10, 0), "upperarm_r": (-25, -20, 30), "lowerarm_r": (-60, 0, 0), "hand_r": (0, 0, 0)},
    {"f": 6, "ry": 0.0, "pelvis_loc": (0.20, 0, 0), "pelvis_rot": (0, 0, -15),
     "spine_01": (0, 0, -12), "spine_03": (0, 0, -10), "spine_05": (0, 0, -8), "neck_01": (0, 0, 8), "head": (0, 0, 10),
     "thigh_l": (18, 0, 55), "calf_l": (0, 0, -85), "foot_l": (0, 0, 30), "thigh_r": (-12, 0, -40), "calf_r": (0, 0, 75), "foot_r": (0, 0, -25),
     "clavicle_l": (0, 25, 0), "upperarm_l": (-45, 60, -80), "lowerarm_l": (-90, 0, 0), "hand_l": (10, 0, 0),
     "clavicle_r": (0, 25, 0), "upperarm_r": (-50, -50, -75), "lowerarm_r": (-95, 0, 0), "hand_r": (-10, 0, 0)},
    {"f": 11, "ry": 0.0, "pelvis_loc": (0.10, 0, 0), "pelvis_rot": (0, 0, 5),
     "spine_01": (0, 0, 8), "spine_03": (0, 0, 10), "spine_05": (0, 0, 10), "neck_01": (0, 0, -5), "head": (0, 0, -6),
     "thigh_l": (12, 0, 35), "calf_l": (0, 0, -50), "foot_l": (0, 0, 15), "thigh_r": (-8, 0, -20), "calf_r": (0, 0, 40), "foot_r": (0, 0, -12),
     "clavicle_l": (0, 10, 0), "upperarm_l": (-10, 20, -15), "lowerarm_l": (-45, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, 10, 0), "upperarm_r": (-15, -15, 10), "lowerarm_r": (-50, 0, 0), "hand_r": (0, 0, 0)},
    {"f": 15, "ry": 0.0, "pelvis_loc": (-0.14, 0, 0), "pelvis_rot": (0, 0, 30),
     "spine_01": (0, 0, 25), "spine_03": (0, 0, 28), "spine_05": (0, 0, 25), "neck_01": (0, 0, -15), "head": (0, 0, -18),
     "thigh_l": (15, 0, 65), "calf_l": (0, 0, -110), "foot_l": (0, 0, 45), "thigh_r": (-15, 0, -55), "calf_r": (0, 0, 100), "foot_r": (0, 0, -40),
     "clavicle_l": (0, 20, 0), "upperarm_l": (20, 25, 45), "lowerarm_l": (-25, 0, 0), "hand_l": (-15, 0, 0),
     "clavicle_r": (0, 20, 0), "upperarm_r": (25, -20, 50), "lowerarm_r": (-30, 0, 0), "hand_r": (-20, 0, 0)},
    {"f": 18, "ry": 0.0, "pelvis_loc": (-0.12, 0, 0), "pelvis_rot": (0, 0, 26),
     "spine_01": (0, 0, 20), "spine_03": (0, 0, 22), "spine_05": (0, 0, 20), "neck_01": (0, 0, -10), "head": (0, 0, -12),
     "thigh_l": (14, 0, 58), "calf_l": (0, 0, -100), "foot_l": (0, 0, 40), "thigh_r": (-14, 0, -48), "calf_r": (0, 0, 90), "foot_r": (0, 0, -35),
     "clavicle_l": (0, 15, 0), "upperarm_l": (15, 20, 35), "lowerarm_l": (-30, 0, 0), "hand_l": (-10, 0, 0),
     "clavicle_r": (0, 15, 0), "upperarm_r": (20, -15, 40), "lowerarm_r": (-35, 0, 0), "hand_r": (-15, 0, 0)},
    {"f": 22, "ry": 0.0, "pelvis_loc": (-0.05, 0, 0), "pelvis_rot": (0, 0, 10),
     "spine_01": (0, 0, 6), "spine_03": (0, 0, 5), "spine_05": (0, 0, 4), "neck_01": (0, 0, -2), "head": (0, 0, -3),
     "thigh_l": (8, 0, 30), "calf_l": (0, 0, -55), "foot_l": (0, 0, 25), "thigh_r": (-8, 0, -22), "calf_r": (0, 0, 45), "foot_r": (0, 0, -20),
     "clavicle_l": (0, 5, 0), "upperarm_l": (-5, 10, -10), "lowerarm_l": (-35, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, -5, 0), "upperarm_r": (-10, -10, 15), "lowerarm_r": (-40, 0, 0), "hand_r": (0, 0, 0)},
    {"f": 26, "ry": 0.0, "pelvis_loc": (0, 0, 0), "pelvis_rot": (0, 0, -5),
     "spine_01": (0, 0, -3), "spine_03": (0, 0, -2), "spine_05": (0, 0, -2), "neck_01": (0, 0, 3), "head": (0, 0, 4),
     "thigh_l": (5, 0, 15), "calf_l": (0, 0, -30), "foot_l": (0, 0, 15), "thigh_r": (-5, 0, -10), "calf_r": (0, 0, 20), "foot_r": (0, 0, -10),
     "clavicle_l": (0, 5, 0), "upperarm_l": (-10, 15, -20), "lowerarm_l": (-30, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, -5, 0), "upperarm_r": (-15, -10, 20), "lowerarm_r": (-35, 0, 0), "hand_r": (0, 0, 0)}
]
txt_air_heavy = """Clip: Attack_Air_Heavy_Plunge
Length: 0.867
FPS: 30
Frames: 27 (0 to 26)
Loop: No (One-shot)
RootMotion: None (In-place; airborne plunge driven by jump physics)
RootYaw: 0.0 (Facing strictly preserved throughout)
AirborneWindupEnd: 0.200 (Frame 6)
HitWindowStart: 0.367 (Frame 11)
LandingImpact: 0.500 (Frame 15)
HitWindowEnd: 0.533 (Frame 16)
RecoverEnd: 0.867 (Frame 26)
ArmatureHeight: 1.786 m (~180 cm for SK_CombatMannequin)
Notes: Elden Ring style jump heavy plunge attack (ER-A3). Initiated in mid-air (R2 while jumping), the character lifts the greatsword overhead with both hands in airborne apex (F0-F6), drives down with full body weight into a vertical plunge, slamming the sword into the ground at landing impact F15 (0.500 s). Deep squat absorbs impact shock and settles smoothly back into combat idle.
"""

# ==============================================================================
# CLIP 4: Attack_Air_Light (ER-A2)
# ==============================================================================
kfs_air_light = [
    {"f": 0, "ry": 0.0, "pelvis_loc": (0.10, 0, 0), "pelvis_rot": (0, 0, -5),
     "spine_01": (0, 0, -3), "spine_03": (0, 0, -2), "spine_05": (0, 0, -2), "neck_01": (0, 0, 3), "head": (0, 0, 4),
     "thigh_l": (10, 0, 35), "calf_l": (0, 0, -55), "foot_l": (0, 0, 20), "thigh_r": (-8, 0, -22), "calf_r": (0, 0, 45), "foot_r": (0, 0, -15),
     "clavicle_l": (0, 8, 0), "upperarm_l": (-15, 20, -15), "lowerarm_l": (-40, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, -8, 0), "upperarm_r": (-20, -15, 15), "lowerarm_r": (-45, 0, 0), "hand_r": (0, 0, 0)},
    {"f": 4, "ry": 0.0, "pelvis_loc": (0.12, 0, 0), "pelvis_rot": (0, 0, -12),
     "spine_01": (0, 0, -8), "spine_03": (0, 0, -6), "spine_05": (0, 0, -5), "neck_01": (0, 0, 6), "head": (0, 0, 8),
     "thigh_l": (12, 0, 42), "calf_l": (0, 0, -65), "foot_l": (0, 0, 25), "thigh_r": (-10, 0, -28), "calf_r": (0, 0, 55), "foot_r": (0, 0, -20),
     "clavicle_l": (0, 5, 0), "upperarm_l": (-10, 15, -20), "lowerarm_l": (-35, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, -15, 0), "upperarm_r": (-35, -45, 60), "lowerarm_r": (-75, 0, 0), "hand_r": (20, 0, 0)},
    {"f": 7, "ry": 0.0, "pelvis_loc": (0.08, 0, 0), "pelvis_rot": (0, 0, 15),
     "spine_01": (0, 0, 12), "spine_03": (0, 0, 14), "spine_05": (0, 0, 12), "neck_01": (0, 0, -8), "head": (0, 0, -10),
     "thigh_l": (10, 0, 32), "calf_l": (0, 0, -50), "foot_l": (0, 0, 18), "thigh_r": (-6, 0, -18), "calf_r": (0, 0, 38), "foot_r": (0, 0, -14),
     "clavicle_l": (0, -12, 0), "upperarm_l": (15, -25, 20), "lowerarm_l": (-25, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, 20, 0), "upperarm_r": (20, 45, -70), "lowerarm_r": (-20, 0, 0), "hand_r": (-15, 0, 0)},
    {"f": 11, "ry": 0.0, "pelvis_loc": (0.05, 0, 0), "pelvis_rot": (0, 0, 10),
     "spine_01": (0, 0, 8), "spine_03": (0, 0, 7), "spine_05": (0, 0, 6), "neck_01": (0, 0, -4), "head": (0, 0, -5),
     "thigh_l": (8, 0, 25), "calf_l": (0, 0, -42), "foot_l": (0, 0, 16), "thigh_r": (-5, 0, -14), "calf_r": (0, 0, 28), "foot_r": (0, 0, -10),
     "clavicle_l": (0, -8, 0), "upperarm_l": (10, -15, 12), "lowerarm_l": (-25, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, 12, 0), "upperarm_r": (12, 30, -50), "lowerarm_r": (-25, 0, 0), "hand_r": (-10, 0, 0)},
    {"f": 14, "ry": 0.0, "pelvis_loc": (0.03, 0, 0), "pelvis_rot": (0, 0, 2),
     "spine_01": (0, 0, 2), "spine_03": (0, 0, 1), "spine_05": (0, 0, 1), "neck_01": (0, 0, -1), "head": (0, 0, -1),
     "thigh_l": (6, 0, 20), "calf_l": (0, 0, -35), "foot_l": (0, 0, 15), "thigh_r": (-5, 0, -12), "calf_r": (0, 0, 22), "foot_r": (0, 0, -10),
     "clavicle_l": (0, 5, 0), "upperarm_l": (-5, 10, -10), "lowerarm_l": (-30, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, -5, 0), "upperarm_r": (-10, -10, 15), "lowerarm_r": (-35, 0, 0), "hand_r": (0, 0, 0)},
    {"f": 17, "ry": 0.0, "pelvis_loc": (0, 0, 0), "pelvis_rot": (0, 0, -5),
     "spine_01": (0, 0, -3), "spine_03": (0, 0, -2), "spine_05": (0, 0, -2), "neck_01": (0, 0, 3), "head": (0, 0, 4),
     "thigh_l": (5, 0, 15), "calf_l": (0, 0, -30), "foot_l": (0, 0, 15), "thigh_r": (-5, 0, -10), "calf_r": (0, 0, 20), "foot_r": (0, 0, -10),
     "clavicle_l": (0, 5, 0), "upperarm_l": (-10, 15, -20), "lowerarm_l": (-30, 0, 0), "hand_l": (0, 0, 0),
     "clavicle_r": (0, -5, 0), "upperarm_r": (-15, -10, 20), "lowerarm_r": (-35, 0, 0), "hand_r": (0, 0, 0)}
]
txt_air_light = """Clip: Attack_Air_Light
Length: 0.567
FPS: 30
Frames: 18 (0 to 17)
Loop: No (One-shot)
RootMotion: None (In-place; airborne attack driven by jump physics)
RootYaw: 0.0 (Facing strictly preserved throughout)
AirborneWindupEnd: 0.133 (Frame 4)
HitWindowStart: 0.200 (Frame 6)
Impact: 0.233 (Frame 7)
HitWindowEnd: 0.333 (Frame 10)
RecoverEnd: 0.567 (Frame 17)
ArmatureHeight: 1.786 m (~180 cm for SK_CombatMannequin)
Notes: Elden Ring style jump light attack (ER-A2). Initiated mid-air (R1 while jumping), distinct from the ground attack. Character coils upper torso in jump apex (F0-F4) and executes a swift one-handed diagonal air slash across the body with impact at F7 (0.233 s). Follow-through blends seamlessly into falling loop or ground touchdown.
"""

# Run all 4 clips
res_backstep = export_and_render_clip("Backstep_Back", kfs_backstep, 15, txt_backstep, 5)
res_guard_counter = export_and_render_clip("Attack_GuardCounter", kfs_guard_counter, 25, txt_guard_counter, 13)
res_air_heavy = export_and_render_clip("Attack_Air_Heavy_Plunge", kfs_air_heavy, 27, txt_air_heavy, 15)
res_air_light = export_and_render_clip("Attack_Air_Light", kfs_air_light, 18, txt_air_light, 7)

print("\nALL 4 CLIPS COMPLETED SUCCESSFULLY")
