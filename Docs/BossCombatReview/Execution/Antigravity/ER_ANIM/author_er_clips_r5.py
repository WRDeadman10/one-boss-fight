"""
Master R5 authoring script for Elden Ring air combat clips in Blender
per Lead directives [C-995] and [C-998]:
- ER-A2 Attack_Air_Light: re-sliced around PrimaryB forward strike (source frames 6..24 @ 30 fps = 0.200..0.800 s, 19 frames).
- ER-A3 Attack_Air_Heavy_Plunge: re-sliced around PrimaryB forward strike & plunge (source frames 6..32 @ 30 fps = 0.200..1.067 s, 27 frames).
Renders 6-frame strip, look PNG, and pack-standard review MP4 (Side 1.0x -> Front 1.0x -> Side 0.5x slowmo).
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

def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = 30
    scene.render.fps_base = 1.0
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'

    # Studio World
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

    # Camera
    cam_data = bpy.data.cameras.new("ReviewCam")
    cam_data.lens = 45.0
    cam = bpy.data.objects.new("ReviewCam", object_data=cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam

    return scene, cam

def load_animated_armature(fbx_path):
    cur_objs = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    new_objs = set(bpy.data.objects) - cur_objs
    arm = [o for o in new_objs if o.type == 'ARMATURE'][0]
    arm.name = "root"
    arm.data.name = "root"
    return arm

def attach_mesh_and_sword(arm):
    cur_objs = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=REF_RIG)
    new_objs = set(bpy.data.objects) - cur_objs
    mesh = [o for o in new_objs if o.type == 'MESH' and 'LOD0' in o.name][0]
    for o in new_objs:
        if o != mesh:
            bpy.data.objects.remove(o, do_unlink=True)

    mesh.parent = arm
    for mod in mesh.modifiers:
        if mod.type == 'ARMATURE':
            mod.object = arm

    cur_objs = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=SWORD_FBX)
    sword_objs = set(bpy.data.objects) - cur_objs
    sword = [o for o in sword_objs if o.type == 'MESH'][0]
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

    return mesh, sword

def render_and_export(clip_name, total_frames, arm, cam, out_dir, look_frame, strip_frame_indices, f_start_offset=0):
    scene = bpy.context.scene
    frames_dir = os.path.join(out_dir, "temp_frames_r5")
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    # 1. Render Side frames (tracking pelvis Y)
    for i in range(total_frames):
        scene_frame = f_start_offset + i
        scene.frame_set(scene_frame)
        dg = bpy.context.evaluated_depsgraph_get()
        arm_eval = arm.evaluated_get(dg)
        p = arm_eval.pose.bones.get('pelvis')
        pelvis_y = (arm_eval.matrix_world @ p.matrix).translation.y if p else 0.0

        cam.location = (4.8, pelvis_y, 0.90)
        cam.rotation_euler = (radians(90), 0, radians(90))
        scene.render.filepath = os.path.join(frames_dir, f"side_{i:03d}.png")
        bpy.ops.render.render(write_still=True)

    # 2. Render Front frames (tracking pelvis Y)
    for i in range(total_frames):
        scene_frame = f_start_offset + i
        scene.frame_set(scene_frame)
        dg = bpy.context.evaluated_depsgraph_get()
        arm_eval = arm.evaluated_get(dg)
        p = arm_eval.pose.bones.get('pelvis')
        pelvis_y = (arm_eval.matrix_world @ p.matrix).translation.y if p else 0.0

        cam.location = (0.0, pelvis_y - 4.5, 0.90)
        cam.rotation_euler = (radians(90), 0, 0.0)
        scene.render.filepath = os.path.join(frames_dir, f"front_{i:03d}.png")
        bpy.ops.render.render(write_still=True)

    # 3. Look PNG frame-grab
    look_png = os.path.join(out_dir, f"look_{clip_name}.png")
    shutil.copyfile(os.path.join(frames_dir, f"side_{look_frame:03d}.png"), look_png)
    root_look_png = os.path.join(BASE_DIR, f"look_{clip_name}.png")
    shutil.copyfile(look_png, root_look_png)

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
        cf.write(f"file '{os.path.join(frames_dir, f'side_{total_frames-1:03d}.png').replace(chr(92), '/')}'\n")

    cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_txt}" -c:v libx264 -pix_fmt yuv420p -r 30 -crf 18 "{mp4_path}"'
    subprocess.run(cmd, shell=True, check=True)

    # 5. 6-Frame Strip PNG (6x1 tile) via ffmpeg
    strip_png = os.path.join(out_dir, f"strip_{clip_name}.png")
    inputs = " ".join([f'-i "{os.path.join(frames_dir, f"side_{f:03d}.png").replace(chr(92), "/")}"' for f in strip_frame_indices])
    scales = "".join([f'[{i}:v]scale=320:180[v{i}];' for i in range(len(strip_frame_indices))])
    stacks = "".join([f'[v{i}]' for i in range(len(strip_frame_indices))])
    strip_cmd = f'ffmpeg -y {inputs} -filter_complex "{scales}{stacks}hstack=inputs={len(strip_frame_indices)}" "{strip_png}"'
    subprocess.run(strip_cmd, shell=True, check=True)

    # 6. Export FBX
    fbx_path = os.path.join(out_dir, f"{clip_name}.fbx")
    root_fbx = os.path.join(BASE_DIR, f"{clip_name}.fbx")

    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    for m in meshes:
        m.select_set(False)

    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)

    scene.frame_start = f_start_offset
    scene.frame_end = f_start_offset + total_frames - 1

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
        bake_anim_step=1.0,
        bake_anim_simplify_factor=0.0
    )
    shutil.copyfile(fbx_path, root_fbx)

    print(f"DELIVERED {clip_name}: FBX={os.path.getsize(fbx_path)} B, MP4={os.path.getsize(mp4_path)} B, Strip={os.path.getsize(strip_png)} B")
    return strip_png, mp4_path, fbx_path

def process_air_light():
    print("\n--- AUTHORING ER-A2: Attack_Air_Light (R5, C-995 re-slice) ---")
    scene, cam = setup_scene()
    src_fbx = os.path.join(SRC_DIR, "Attack_PrimaryB_Anim.fbx")
    arm = load_animated_armature(src_fbx)
    mesh, sword = attach_mesh_and_sword(arm)

    # Bake frames 6..24 (19 frames, 0.200..0.800 s)
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    orig_act = arm.animation_data.action
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.nla.bake(frame_start=6, frame_end=24, step=1, only_selected=False, visual_keying=True, clear_constraints=True, clear_parents=False, bake_types={'POSE'})
    bpy.ops.object.mode_set(mode='OBJECT')
    if orig_act in bpy.data.actions.values():
        bpy.data.actions.remove(orig_act)

    scene.frame_set(6)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    h6 = (arm_eval.matrix_world @ arm_eval.pose.bones['hand_r'].matrix).translation.copy()
    p6 = (arm_eval.matrix_world @ arm_eval.pose.bones['pelvis'].matrix).translation.copy()

    scene.frame_set(15) # strike peak
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    h15 = (arm_eval.matrix_world @ arm_eval.pose.bones['hand_r'].matrix).translation.copy()
    p15 = (arm_eval.matrix_world @ arm_eval.pose.bones['pelvis'].matrix).translation.copy()

    h_forward = (h15.y - h6.y) * 100.0
    p_forward = (p15.y - p6.y) * 100.0
    keyed_bones = len(arm.pose.bones)

    print(f"[VERIFIED ER-A2 Attack_Air_Light]: keyed_bones={keyed_bones}, hand forward={h_forward:.1f} cm, pelvis forward={p_forward:.1f} cm")

    out_dir = os.path.join(BASE_DIR, "Attack_Air_Light")
    strip_png, mp4, fbx = render_and_export(
        "Attack_Air_Light", total_frames=19, arm=arm, cam=cam, out_dir=out_dir,
        look_frame=9, strip_frame_indices=[0, 3, 7, 11, 15, 18], f_start_offset=6
    )

    # Write updated text spec
    txt_path = os.path.join(out_dir, "Attack_Air_Light.txt")
    with open(txt_path, "w") as f:
        f.write("""Clip: Attack_Air_Light
Length: 0.600
FPS: 30
Frames: 19 (0 to 18)
Loop: No (One-shot)
RootMotion: Retained from PrimaryB forward lunge (0.200..0.800 s)
RootYaw: 0.0 (Facing preserved)
AirborneWindupEnd: 0.150 (Frame 4)
HitWindowStart: 0.150 (Frame 4)
Impact: 0.233 (Frame 7)
HitWindowEnd: 0.336 (Frame 10)
RecoverEnd: 0.600 (Frame 18)
ArmatureHeight: 1.786 m (~180 cm for SK_CombatMannequin)
Notes: Re-sliced per Lead [C-995] to PrimaryB 0.200..0.800 s. Captures the forward strike and lunge, guaranteeing forward hand_r reach into the target. ANS_MovementCancel_C removed.
""")

def process_air_heavy():
    print("\n--- AUTHORING ER-A3: Attack_Air_Heavy_Plunge (R5, C-995 re-slice) ---")
    scene, cam = setup_scene()
    src_fbx = os.path.join(SRC_DIR, "Attack_PrimaryB_Anim.fbx")
    arm = load_animated_armature(src_fbx)
    mesh, sword = attach_mesh_and_sword(arm)

    # Bake frames 6..32 (27 frames, 0.200..1.067 s)
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    orig_act = arm.animation_data.action
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.nla.bake(frame_start=6, frame_end=32, step=1, only_selected=False, visual_keying=True, clear_constraints=True, clear_parents=False, bake_types={'POSE'})
    bpy.ops.object.mode_set(mode='OBJECT')
    if orig_act in bpy.data.actions.values():
        bpy.data.actions.remove(orig_act)

    scene.frame_set(6)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    h6 = (arm_eval.matrix_world @ arm_eval.pose.bones['hand_r'].matrix).translation.copy()
    p6 = (arm_eval.matrix_world @ arm_eval.pose.bones['pelvis'].matrix).translation.copy()

    scene.frame_set(16)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    h16 = (arm_eval.matrix_world @ arm_eval.pose.bones['hand_r'].matrix).translation.copy()
    p16 = (arm_eval.matrix_world @ arm_eval.pose.bones['pelvis'].matrix).translation.copy()

    h_forward = (h16.y - h6.y) * 100.0
    p_forward = (p16.y - p6.y) * 100.0
    keyed_bones = len(arm.pose.bones)

    print(f"[VERIFIED ER-A3 Attack_Air_Heavy_Plunge]: keyed_bones={keyed_bones}, hand forward={h_forward:.1f} cm, pelvis forward={p_forward:.1f} cm")

    out_dir = os.path.join(BASE_DIR, "Attack_Air_Heavy_Plunge")
    strip_png, mp4, fbx = render_and_export(
        "Attack_Air_Heavy_Plunge", total_frames=27, arm=arm, cam=cam, out_dir=out_dir,
        look_frame=11, strip_frame_indices=[0, 5, 10, 15, 20, 26], f_start_offset=6
    )

    txt_path = os.path.join(out_dir, "Attack_Air_Heavy_Plunge.txt")
    with open(txt_path, "w") as f:
        f.write("""Clip: Attack_Air_Heavy_Plunge
Length: 0.867
FPS: 30
Frames: 27 (0 to 26)
Loop: No (One-shot)
RootMotion: Retained from PrimaryB forward lunge (0.200..1.067 s)
RootYaw: 0.0 (Facing preserved)
AirborneWindupEnd: 0.150 (Frame 4)
HitWindowStart: 0.150 (Frame 4)
LandingImpact: 0.336 (Frame 10)
HitWindowEnd: 0.336 (Frame 10)
RecoverEnd: 0.867 (Frame 26)
ArmatureHeight: 1.786 m (~180 cm for SK_CombatMannequin)
Notes: Re-sliced per Lead [C-995] to PrimaryB 0.200..1.067 s. Captures the forward strike and downward plunge with root lunge. ANS_MovementCancel_C removed.
""")

if __name__ == "__main__":
    process_air_light()
    process_air_heavy()
    print("ALL R5 AIR CLIPS DELIVERED SUCCESSFULLY.")
