"""Master R2 authoring script for Elden Ring combat clips in Blender.

Addresses Lead Claude's directive [C-960]:
- Uses the pack's REAL animations (BlockLoop, Attack_PrimaryA, PrimaryAttack_A_Slow, Dodge_Roll, MM_Jump, MM_Fall_Loop)
- Unaltered bone axes, anatomically correct human motion
- SKM_CombatMannequin_Simple mesh visible and lit in review renders
- Sword equipped in right hand
- Studio grey background (#47474d) + 3-point sun lighting
- Side 1.0x -> Front 1.0x -> Side 0.5x slow-mo MP4
- 6-frame strip PNG (6x1 tile) per clip
- Exact ~1.80m armature height FBX export (apply_unit_scale=False)
"""

import os
import shutil
import subprocess
from math import radians
import bpy
from mathutils import Vector, Quaternion

BASE_DIR = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\ER_ANIM"
SRC_DIR = r"c:\UnrealProject\OneBossFight\Import\Player\Animations_FBX_Export"
REF_RIG = r"c:\UnrealProject\OneBossFight\Import\ThirdParty\Reference\SKM_CombatMannequin_Simple.fbx"
SWORD_FBX = r"c:\UnrealProject\OneBossFight\Import\ThirdParty\Reference\SM_KwangSword.fbx"

def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = 30
    scene.render.fps_base = 1.0
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'

    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
    world.color = (0.28, 0.28, 0.30)

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

    return scene, cam

def load_base_rig():
    bpy.ops.import_scene.fbx(filepath=REF_RIG)
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    arm.name = "root"
    arm.data.name = "root"
    
    # Keep only LOD0 mesh
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o.name != 'SKM_CombatMannequin_Simple_LOD0':
            bpy.data.objects.remove(o, do_unlink=True)
            
    # Attach sword
    if os.path.exists(SWORD_FBX):
        bpy.ops.import_scene.fbx(filepath=SWORD_FBX)
        swords = [o for o in bpy.data.objects if o.type == 'MESH' and o.name != 'SKM_CombatMannequin_Simple_LOD0']
        if swords:
            sword = swords[0]
            sword.name = "ReviewSword"
            sword.parent = arm
            sword.parent_type = 'BONE'
            sword.parent_bone = "hand_r"
            sword.location = (0.0, 0.05, 0.0)
            sword.rotation_euler = (0, radians(90), 0)
            
    return arm

def import_action(fbx_path, act_name):
    # Imports an FBX action and unlinks its temporary armature
    cur_objs = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    new_objs = set(bpy.data.objects) - cur_objs
    temp_arm = [o for o in new_objs if o.type == 'ARMATURE'][0]
    act = temp_arm.animation_data.action
    act.name = act_name
    for o in new_objs:
        bpy.data.objects.remove(o, do_unlink=True)
    return act

def sample_snapshot(arm, action, frame):
    if not arm.animation_data:
        arm.animation_data_create()
    arm.animation_data.action = action
    bpy.context.scene.frame_set(int(frame))
    bpy.context.view_layer.update()
    snap = {}
    for pb in arm.pose.bones:
        snap[pb.name] = {
            'loc': pb.location.copy(),
            'quat': pb.rotation_quaternion.copy(),
            'scale': pb.scale.copy(),
        }
    return snap

def blend_snapshots(snap_a, snap_b, alpha):
    out = {}
    for b in snap_a:
        if b in snap_b:
            out[b] = {
                'loc': snap_a[b]['loc'].lerp(snap_b[b]['loc'], alpha),
                'quat': snap_a[b]['quat'].slerp(snap_b[b]['quat'], alpha),
                'scale': snap_a[b]['scale'].lerp(snap_b[b]['scale'], alpha),
            }
        else:
            out[b] = snap_a[b]
    return out

def apply_and_key(arm, snap, frame):
    for b_name, data in snap.items():
        pb = arm.pose.bones.get(b_name)
        if pb:
            pb.rotation_mode = 'QUATERNION'
            pb.location = data['loc']
            pb.rotation_quaternion = data['quat']
            pb.scale = data['scale']
            pb.keyframe_insert("location", frame=frame)
            pb.keyframe_insert("rotation_quaternion", frame=frame)

def render_and_export(clip_name, total_frames, arm, cam, out_dir, look_frame, strip_frames):
    scene = bpy.context.scene
    frames_dir = os.path.join(out_dir, "temp_frames_r2")
    os.makedirs(frames_dir, exist_ok=True)
    
    # 1. Render Side frames
    for f in range(total_frames):
        scene.frame_set(f)
        arm_y = arm.location.y
        cam.location = (4.8, arm_y, 0.90)
        cam.rotation_euler = (radians(90), 0, radians(90))
        scene.render.filepath = os.path.join(frames_dir, f"side_{f:03d}.png")
        bpy.ops.render.render(write_still=True)

    # 2. Render Front frames
    for f in range(total_frames):
        scene.frame_set(f)
        arm_y = arm.location.y
        cam.location = (0.0, arm_y - 4.5, 0.90)
        cam.rotation_euler = (radians(90), 0, 0.0)
        scene.render.filepath = os.path.join(frames_dir, f"front_{f:03d}.png")
        bpy.ops.render.render(write_still=True)

    # 3. Look PNG frame-grab
    look_png = os.path.join(out_dir, f"look_{clip_name}.png")
    shutil.copyfile(os.path.join(frames_dir, f"side_{look_frame:03d}.png"), look_png)

    # 4. Review MP4 (Side 1.0x -> Front 1.0x -> Side 0.5x Slowmo)
    mp4_path = os.path.join(out_dir, f"review_{clip_name}.mp4")
    concat_txt = os.path.join(frames_dir, "concat.txt")
    with open(concat_txt, "w") as cf:
        for f in range(total_frames):
            p = os.path.join(frames_dir, f"side_{f:03d}.png").replace("\\", "/")
            cf.write(f"file '{p}'\nduration 0.033333\n")
        for f in range(total_frames):
            p = os.path.join(frames_dir, f"front_{f:03d}.png").replace("\\", "/")
            cf.write(f"file '{p}'\nduration 0.033333\n")
        for f in range(total_frames):
            p = os.path.join(frames_dir, f"side_{f:03d}.png").replace("\\", "/")
            cf.write(f"file '{p}'\nduration 0.066666\n")
        cf.write(f"file '{os.path.join(frames_dir, f'side_{total_frames-1:03d}.png').replace('/', '/')}'\n")

    cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_txt}" -c:v libx264 -pix_fmt yuv420p -r 30 -crf 18 "{mp4_path}"'
    subprocess.run(cmd, shell=True, check=True)

    # 5. 6-Frame Strip PNG (6x1 tile) via ffmpeg
    strip_png = os.path.join(out_dir, f"strip_{clip_name}.png")
    inputs = " ".join([f'-i "{os.path.join(frames_dir, f"side_{f:03d}.png").replace(chr(92), "/")}"' for f in strip_frames])
    scales = "".join([f'[{i}:v]scale=320:180[v{i}];' for i in range(len(strip_frames))])
    stacks = "".join([f'[v{i}]' for i in range(len(strip_frames))])
    strip_cmd = f'ffmpeg -y {inputs} -filter_complex "{scales}{stacks}hstack=inputs={len(strip_frames)}" "{strip_png}"'
    subprocess.run(strip_cmd, shell=True, check=True)

    # 6. Export FBX (without mesh or sword, only ARMATURE)
    fbx_path = os.path.join(out_dir, f"{clip_name}.fbx")
    
    # Hide/unlink meshes for FBX export
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    for m in meshes:
        m.select_set(False)

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
    
    print(f"DELIVERED {clip_name}: FBX={os.path.getsize(fbx_path)}, MP4={os.path.getsize(mp4_path)}, Strip={os.path.getsize(strip_png)}")


# ==============================================================================
# 1. ER-A1: Backstep_Back (15 frames @ 30 fps, 0.467 s)
# ==============================================================================
def author_backstep():
    print("\n--- AUTHORING ER-A1: Backstep_Back ---")
    scene, cam = clean_scene()
    arm = load_base_rig()
    
    act_roll = import_action(os.path.join(SRC_DIR, "Dodge_Small_Forward_Roll.fbx"), "act_roll")
    
    # Sample spring launch from roll F1..F4, upright apex, and cushion landing F19..F22
    s_f1 = sample_snapshot(arm, act_roll, 1)
    s_f2 = sample_snapshot(arm, act_roll, 2)
    s_f3 = sample_snapshot(arm, act_roll, 3)
    s_f4 = sample_snapshot(arm, act_roll, 4)
    s_f19 = sample_snapshot(arm, act_roll, 19)
    s_f21 = sample_snapshot(arm, act_roll, 21)
    s_f22 = sample_snapshot(arm, act_roll, 22)
    
    new_act = bpy.data.actions.new(name="AN_ER_Backstep_Back")
    if not arm.animation_data:
        arm.animation_data_create()
    arm.animation_data.action = new_act
    
    TOTAL = 15
    for f in range(TOTAL):
        scene.frame_set(f)
        if f == 0:
            snap = s_f1
        elif f == 1:
            snap = s_f2
        elif f == 2:
            snap = s_f3
        elif f <= 5: # Airborne apex hop
            snap = s_f4
        elif f <= 9: # Glide down
            alpha = (f - 5) / 4.0
            snap = blend_snapshots(s_f4, s_f19, alpha)
        elif f <= 12: # Touchdown cushion
            alpha = (f - 9) / 3.0
            snap = blend_snapshots(s_f19, s_f21, alpha)
        else: # Return to combat stance
            snap = s_f22
            
        apply_and_key(arm, snap, f)
        
        # Root motion: -200 cm (-2.0 m) straight back along -Y
        if f <= 2:
            y_trans = 0.0
        elif f >= 12:
            y_trans = -2.0
        else:
            t = (f - 2) / 10.0
            y_trans = -(3 * t**2 - 2 * t**3) * 2.0
            
        arm.location = Vector((0.0, y_trans, 0.0))
        arm.rotation_euler = (0.0, 0.0, 0.0)
        arm.keyframe_insert("location", frame=f)
        arm.keyframe_insert("rotation_euler", frame=f)
        
    out_dir = os.path.join(BASE_DIR, "Backstep_Back")
    render_and_export("Backstep_Back", TOTAL, arm, cam, out_dir, look_frame=5, strip_frames=[0, 3, 6, 9, 12, 14])


# ==============================================================================
# 2. ER-A4: Attack_GuardCounter (25 frames @ 30 fps, 0.800 s)
# ==============================================================================
def author_guard_counter():
    print("\n--- AUTHORING ER-A4: Attack_GuardCounter ---")
    scene, cam = clean_scene()
    arm = load_base_rig()
    
    act_block = import_action(os.path.join(SRC_DIR, "BlockLoop.fbx"), "act_block")
    act_att = import_action(os.path.join(SRC_DIR, "Attack_PrimaryA_Anim.fbx"), "act_att")
    
    snap_block = sample_snapshot(arm, act_block, 1)
    snap_att_15 = sample_snapshot(arm, act_att, 15)
    snap_att_19 = sample_snapshot(arm, act_att, 19)
    snap_att_23 = sample_snapshot(arm, act_att, 23)
    snap_att_25 = sample_snapshot(arm, act_att, 25)
    snap_att_29 = sample_snapshot(arm, act_att, 29)
    snap_att_35 = sample_snapshot(arm, act_att, 35)
    snap_att_41 = sample_snapshot(arm, act_att, 41)
    
    new_act = bpy.data.actions.new(name="AN_ER_Attack_GuardCounter")
    if not arm.animation_data:
        arm.animation_data_create()
    arm.animation_data.action = new_act
    
    TOTAL = 25
    for f in range(TOTAL):
        scene.frame_set(f)
        if f <= 6:
            snap = snap_block
        elif f == 7:
            snap = blend_snapshots(snap_block, snap_att_15, 0.33)
        elif f == 8:
            snap = blend_snapshots(snap_block, snap_att_15, 0.66)
        elif f == 9:
            snap = snap_att_15
        elif f == 10:
            snap = blend_snapshots(snap_att_15, snap_att_19, 0.5)
        elif f == 11:
            snap = snap_att_19
        elif f == 12:
            snap = snap_att_23
        elif f == 13: # Impact
            snap = snap_att_25
        elif f == 14:
            snap = snap_att_29
        elif f <= 18:
            alpha = (f - 14) / 4.0
            snap = blend_snapshots(snap_att_29, snap_att_35, alpha)
        else:
            alpha = (f - 18) / 6.0
            snap = blend_snapshots(snap_att_35, snap_att_41, alpha)
            
        apply_and_key(arm, snap, f)
        
        # Root motion: +100 cm (+1.0 m) forward step along +Y
        if f <= 6:
            y_trans = 0.0
        elif f >= 14:
            y_trans = 1.0
        else:
            t = (f - 6) / 8.0
            y_trans = (3 * t**2 - 2 * t**3) * 1.0
            
        arm.location = Vector((0.0, y_trans, 0.0))
        arm.rotation_euler = (0.0, 0.0, 0.0)
        arm.keyframe_insert("location", frame=f)
        arm.keyframe_insert("rotation_euler", frame=f)
        
    out_dir = os.path.join(BASE_DIR, "Attack_GuardCounter")
    render_and_export("Attack_GuardCounter", TOTAL, arm, cam, out_dir, look_frame=13, strip_frames=[0, 6, 9, 13, 18, 24])


# ==============================================================================
# 3. ER-A3: Attack_Air_Heavy_Plunge (27 frames @ 30 fps, 0.867 s)
# ==============================================================================
def author_air_heavy_plunge():
    print("\n--- AUTHORING ER-A3: Attack_Air_Heavy_Plunge ---")
    scene, cam = clean_scene()
    arm = load_base_rig()
    
    act_jump = import_action(os.path.join(SRC_DIR, "MM_Jump.fbx"), "act_jump")
    act_slow = import_action(os.path.join(SRC_DIR, "PrimaryAttack_A_Slow_Anim.fbx"), "act_slow")
    
    snap_jump_apex = sample_snapshot(arm, act_jump, 5)
    snap_slow_raise = sample_snapshot(arm, act_slow, 11)
    snap_slow_chop = sample_snapshot(arm, act_slow, 27)
    snap_slow_slam = sample_snapshot(arm, act_slow, 33)
    snap_slow_recov = sample_snapshot(arm, act_slow, 39)
    
    new_act = bpy.data.actions.new(name="AN_ER_Attack_Air_Heavy_Plunge")
    if not arm.animation_data:
        arm.animation_data_create()
    arm.animation_data.action = new_act
    
    TOTAL = 27
    for f in range(TOTAL):
        scene.frame_set(f)
        if f <= 3:
            alpha = f / 3.0
            snap = blend_snapshots(snap_jump_apex, snap_slow_raise, alpha)
        elif f <= 6:
            snap = snap_slow_raise # Overhead lift apex
        elif f <= 11:
            alpha = (f - 6) / 5.0
            snap = blend_snapshots(snap_slow_raise, snap_slow_chop, alpha)
        elif f <= 14:
            alpha = (f - 11) / 3.0
            snap = blend_snapshots(snap_slow_chop, snap_slow_slam, alpha)
        elif f == 15: # Ground impact slam
            snap = snap_slow_slam
        elif f <= 21:
            alpha = (f - 15) / 6.0
            snap = blend_snapshots(snap_slow_slam, snap_slow_recov, alpha)
        else:
            snap = snap_slow_recov
            
        apply_and_key(arm, snap, f)
        
        # In-place root
        arm.location = Vector((0.0, 0.0, 0.0))
        arm.rotation_euler = (0.0, 0.0, 0.0)
        arm.keyframe_insert("location", frame=f)
        arm.keyframe_insert("rotation_euler", frame=f)
        
    out_dir = os.path.join(BASE_DIR, "Attack_Air_Heavy_Plunge")
    render_and_export("Attack_Air_Heavy_Plunge", TOTAL, arm, cam, out_dir, look_frame=15, strip_frames=[0, 6, 11, 15, 20, 26])


# ==============================================================================
# 4. ER-A2: Attack_Air_Light (18 frames @ 30 fps, 0.567 s)
# ==============================================================================
def author_air_light():
    print("\n--- AUTHORING ER-A2: Attack_Air_Light ---")
    scene, cam = clean_scene()
    arm = load_base_rig()
    
    act_fall = import_action(os.path.join(SRC_DIR, "MM_Fall_Loop.fbx"), "act_fall")
    act_att = import_action(os.path.join(SRC_DIR, "Attack_PrimaryA_Anim.fbx"), "act_att")
    
    snap_fall = sample_snapshot(arm, act_fall, 1)
    snap_att_windup = sample_snapshot(arm, act_att, 17)
    snap_att_slash = sample_snapshot(arm, act_att, 25)
    snap_att_recov = sample_snapshot(arm, act_att, 31)
    
    new_act = bpy.data.actions.new(name="AN_ER_Attack_Air_Light")
    if not arm.animation_data:
        arm.animation_data_create()
    arm.animation_data.action = new_act
    
    TOTAL = 18
    for f in range(TOTAL):
        scene.frame_set(f)
        if f <= 3:
            alpha = f / 3.0
            snap = blend_snapshots(snap_fall, snap_att_windup, alpha)
        elif f == 4:
            snap = snap_att_windup
        elif f <= 7: # Slash forward to impact
            alpha = (f - 4) / 3.0
            snap = blend_snapshots(snap_att_windup, snap_att_slash, alpha)
        elif f <= 11:
            alpha = (f - 7) / 4.0
            snap = blend_snapshots(snap_att_slash, snap_att_recov, alpha)
        else:
            alpha = (f - 11) / 6.0
            snap = blend_snapshots(snap_att_recov, snap_fall, alpha)
            
        apply_and_key(arm, snap, f)
        
        # In-place root
        arm.location = Vector((0.0, 0.0, 0.0))
        arm.rotation_euler = (0.0, 0.0, 0.0)
        arm.keyframe_insert("location", frame=f)
        arm.keyframe_insert("rotation_euler", frame=f)
        
    out_dir = os.path.join(BASE_DIR, "Attack_Air_Light")
    render_and_export("Attack_Air_Light", TOTAL, arm, cam, out_dir, look_frame=7, strip_frames=[0, 4, 7, 10, 13, 17])


if __name__ == "__main__":
    author_backstep()
    author_guard_counter()
    author_air_heavy_plunge()
    author_air_light()
    print("\n>>> ALL 4 ER CLIPS SUCCESSFULLY AUTHORED UNDER R2! <<<")
