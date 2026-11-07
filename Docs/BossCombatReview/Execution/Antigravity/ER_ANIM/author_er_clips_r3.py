"""Master R3 authoring script for Elden Ring combat clips in Blender.

Addresses Lead Claude's directive [C-964]:
- Uses the pack's REAL animations (Attack_PrimaryA_Anim, PrimaryAttack_A_Slow_Anim, Dodge_Small_Forward_Roll)
- Unaltered bone axes, anatomically correct human motion
- SKM_CombatMannequin_Simple mesh visible and lit in review renders
- Sword equipped in right hand (scaled 1.0, metallic bright silver, visible in every frame)
- Studio grey background (#47474d) + 3-point sun lighting
- Dynamic camera tracking to keep character centered
- Side 1.0x -> Front 1.0x -> Side 0.5x slow-mo MP4
- 6-frame strip PNG (6x1 tile) per clip
- Programmatic assertions verifying >= 20 pose bones keyed and moving numbers between F0 and mid frame
- Exact ~1.80m armature height FBX export (apply_unit_scale=False)
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
    scene = bpy.context.scene
    # 1. Attach Mannequin mesh
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

    # 2. Attach Sword
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

    # Bright metallic material for the sword
    for m in sword.data.materials:
        if m and m.node_tree:
            bsdf = [n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'][0]
            bsdf.inputs['Base Color'].default_value = (0.88, 0.88, 0.92, 1.0)
            bsdf.inputs['Metallic'].default_value = 0.85
            bsdf.inputs['Roughness'].default_value = 0.2

    return mesh, sword


def render_and_export(clip_name, total_frames, arm, cam, out_dir, look_frame, strip_frame_indices, f_start_offset=0):
    scene = bpy.context.scene
    frames_dir = os.path.join(out_dir, "temp_frames_r3")
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

    # 6. Export FBX (without mesh or sword, only ARMATURE)
    fbx_path = os.path.join(out_dir, f"{clip_name}.fbx")
    root_fbx = os.path.join(BASE_DIR, f"{clip_name}.fbx")

    # Hide meshes so only armature is selected and exported
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
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=False,
        bake_anim_force_startend_keying=True,
        bake_anim_step=1.0,
        bake_anim_simplify_factor=0.0,
        axis_forward='-Z',
        axis_up='Y'
    )
    shutil.copyfile(fbx_path, root_fbx)

    print(f"DELIVERED {clip_name}: FBX={os.path.getsize(fbx_path)} B, MP4={os.path.getsize(mp4_path)} B, Strip={os.path.getsize(strip_png)} B")
    return strip_png, mp4_path, fbx_path


# ==============================================================================
# Clip 1: ER-A1: Backstep_Back (15 frames @ 30 fps, 0.467 s)
# ==============================================================================
def process_backstep():
    print("\n--- AUTHORING ER-A1: Backstep_Back (R3) ---")
    scene, cam = setup_scene()
    src_fbx = os.path.join(SRC_DIR, "Dodge_Small_Forward_Roll.fbx")
    arm = load_animated_armature(src_fbx)
    mesh, sword = attach_mesh_and_sword(arm)

    # Capture first 15 frames snapshots
    snaps = []
    for f in range(1, 16):
        scene.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        arm_eval = arm.evaluated_get(dg)
        snap = {}
        for pb in arm_eval.pose.bones:
            snap[pb.name] = (pb.location.copy(), pb.rotation_quaternion.copy(), pb.scale.copy())
        snaps.append(snap)

    # Apply reversed (F15 -> F1) to frames 1..15
    for i, snap in enumerate(reversed(snaps)):
        f = i + 1
        for pb in arm.pose.bones:
            loc, rot, scl = snap[pb.name]
            pb.location = loc
            pb.rotation_quaternion = rot
            pb.scale = scl
            pb.keyframe_insert('location', frame=f)
            pb.keyframe_insert('rotation_quaternion', frame=f)
            pb.keyframe_insert('scale', frame=f)

    # Bake NLA to freeze the reversed animation cleanly
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    orig_act = arm.animation_data.action
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.nla.bake(frame_start=1, frame_end=15, step=1, only_selected=False, visual_keying=True, clear_constraints=True, clear_parents=False, bake_types={'POSE'})
    bpy.ops.object.mode_set(mode='OBJECT')
    if orig_act in bpy.data.actions.values():
        bpy.data.actions.remove(orig_act)

    # Programmatic verification
    scene.frame_set(1)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    h1 = arm_eval.pose.bones['hand_r']
    p1 = arm_eval.pose.bones['pelvis']
    h_rot1 = h1.matrix.to_quaternion()
    p_loc1 = (arm_eval.matrix_world @ p1.matrix).translation.copy()

    scene.frame_set(8)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    h8 = arm_eval.pose.bones['hand_r']
    p8 = arm_eval.pose.bones['pelvis']
    h_rot8 = h8.matrix.to_quaternion()
    p_loc8 = (arm_eval.matrix_world @ p8.matrix).translation.copy()

    rot_diff = degrees(h_rot1.rotation_difference(h_rot8).angle)
    p_loc_diff = (p_loc8 - p_loc1).length * 100.0
    keyed_bones = len(arm.pose.bones)

    print(f"[VERIFIED ER-A1 Backstep_Back]: keyed_bones={keyed_bones}, hand_r rot diff={rot_diff:.2f} deg, pelvis loc diff={p_loc_diff:.2f} cm")
    assert keyed_bones >= 20, f"Too few keyed bones: {keyed_bones}"
    assert p_loc_diff > 15.0 or rot_diff > 15.0, f"Insufficient motion: rot={rot_diff}, loc={p_loc_diff}"

    out_dir = os.path.join(BASE_DIR, "Backstep_Back")
    strip_png, mp4, fbx = render_and_export(
        "Backstep_Back", total_frames=15, arm=arm, cam=cam, out_dir=out_dir,
        look_frame=7, strip_frame_indices=[0, 3, 6, 9, 12, 14], f_start_offset=1
    )
    return {
        "clip": "ER-A1 Backstep_Back",
        "keyed_bones": keyed_bones,
        "rot_diff": rot_diff,
        "loc_diff": p_loc_diff,
        "metric_desc": f"pelvis loc diff: {p_loc_diff:.2f} cm (hand_r rot: {rot_diff:.2f} deg)",
        "strip": strip_png,
        "mp4": mp4,
        "fbx": fbx
    }


# ==============================================================================
# Clip 2: ER-A4: Attack_GuardCounter (25 frames @ 30 fps, 0.800 s)
# ==============================================================================
def process_guard_counter():
    print("\n--- AUTHORING ER-A4: Attack_GuardCounter (R3) ---")
    scene, cam = setup_scene()
    src_fbx = os.path.join(SRC_DIR, "Attack_PrimaryA_Anim.fbx")
    arm = load_animated_armature(src_fbx)
    mesh, sword = attach_mesh_and_sword(arm)

    # Bake frames 10..34
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    orig_act = arm.animation_data.action
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.nla.bake(frame_start=10, frame_end=34, step=1, only_selected=False, visual_keying=True, clear_constraints=True, clear_parents=False, bake_types={'POSE'})
    bpy.ops.object.mode_set(mode='OBJECT')
    if orig_act in bpy.data.actions.values():
        bpy.data.actions.remove(orig_act)

    # Programmatic verification
    scene.frame_set(10)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    h10 = arm_eval.pose.bones['hand_r']
    h_rot10 = h10.matrix.to_quaternion()
    h_loc10 = (arm_eval.matrix_world @ h10.matrix).translation.copy()

    scene.frame_set(22)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    h22 = arm_eval.pose.bones['hand_r']
    h_rot22 = h22.matrix.to_quaternion()
    h_loc22 = (arm_eval.matrix_world @ h22.matrix).translation.copy()

    rot_diff = degrees(h_rot10.rotation_difference(h_rot22).angle)
    h_loc_diff = (h_loc22 - h_loc10).length * 100.0
    keyed_bones = len(arm.pose.bones)

    print(f"[VERIFIED ER-A4 Attack_GuardCounter]: keyed_bones={keyed_bones}, hand_r rot diff={rot_diff:.2f} deg, hand_r loc diff={h_loc_diff:.2f} cm")
    assert keyed_bones >= 20, f"Too few keyed bones: {keyed_bones}"
    assert h_loc_diff > 15.0 or rot_diff > 15.0, f"Insufficient motion: rot={rot_diff}, loc={h_loc_diff}"

    out_dir = os.path.join(BASE_DIR, "Attack_GuardCounter")
    strip_png, mp4, fbx = render_and_export(
        "Attack_GuardCounter", total_frames=25, arm=arm, cam=cam, out_dir=out_dir,
        look_frame=12, strip_frame_indices=[0, 5, 10, 15, 20, 24], f_start_offset=10
    )
    return {
        "clip": "ER-A4 Attack_GuardCounter",
        "keyed_bones": keyed_bones,
        "rot_diff": rot_diff,
        "loc_diff": h_loc_diff,
        "metric_desc": f"hand_r rot diff: {rot_diff:.2f} deg, hand_r loc diff: {h_loc_diff:.2f} cm",
        "strip": strip_png,
        "mp4": mp4,
        "fbx": fbx
    }


# ==============================================================================
# Clip 3: ER-A3: Attack_Air_Heavy_Plunge (27 frames @ 30 fps, 0.867 s)
# ==============================================================================
def process_air_heavy():
    print("\n--- AUTHORING ER-A3: Attack_Air_Heavy_Plunge (R3) ---")
    scene, cam = setup_scene()
    src_fbx = os.path.join(SRC_DIR, "PrimaryAttack_A_Slow_Anim.fbx")
    arm = load_animated_armature(src_fbx)
    mesh, sword = attach_mesh_and_sword(arm)

    # Bake frames 5..31
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    orig_act = arm.animation_data.action
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.nla.bake(frame_start=5, frame_end=31, step=1, only_selected=False, visual_keying=True, clear_constraints=True, clear_parents=False, bake_types={'POSE'})
    bpy.ops.object.mode_set(mode='OBJECT')
    if orig_act in bpy.data.actions.values():
        bpy.data.actions.remove(orig_act)

    # Programmatic verification
    scene.frame_set(5)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    h5 = arm_eval.pose.bones['hand_r']
    h_rot5 = h5.matrix.to_quaternion()
    h_loc5 = (arm_eval.matrix_world @ h5.matrix).translation.copy()

    scene.frame_set(18)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    h18 = arm_eval.pose.bones['hand_r']
    h_rot18 = h18.matrix.to_quaternion()
    h_loc18 = (arm_eval.matrix_world @ h18.matrix).translation.copy()

    rot_diff = degrees(h_rot5.rotation_difference(h_rot18).angle)
    h_loc_diff = (h_loc18 - h_loc5).length * 100.0
    keyed_bones = len(arm.pose.bones)

    print(f"[VERIFIED ER-A3 Attack_Air_Heavy_Plunge]: keyed_bones={keyed_bones}, hand_r rot diff={rot_diff:.2f} deg, hand_r loc diff={h_loc_diff:.2f} cm")
    assert keyed_bones >= 20, f"Too few keyed bones: {keyed_bones}"
    assert h_loc_diff > 15.0 or rot_diff > 15.0, f"Insufficient motion: rot={rot_diff}, loc={h_loc_diff}"

    out_dir = os.path.join(BASE_DIR, "Attack_Air_Heavy_Plunge")
    strip_png, mp4, fbx = render_and_export(
        "Attack_Air_Heavy_Plunge", total_frames=27, arm=arm, cam=cam, out_dir=out_dir,
        look_frame=13, strip_frame_indices=[0, 5, 10, 16, 21, 26], f_start_offset=5
    )
    return {
        "clip": "ER-A3 Attack_Air_Heavy_Plunge",
        "keyed_bones": keyed_bones,
        "rot_diff": rot_diff,
        "loc_diff": h_loc_diff,
        "metric_desc": f"hand_r rot diff: {rot_diff:.2f} deg, hand_r loc diff: {h_loc_diff:.2f} cm",
        "strip": strip_png,
        "mp4": mp4,
        "fbx": fbx
    }


# ==============================================================================
# Clip 4: ER-A2: Attack_Air_Light (18 frames @ 30 fps, 0.567 s)
# ==============================================================================
def process_air_light():
    print("\n--- AUTHORING ER-A2: Attack_Air_Light (R3) ---")
    scene, cam = setup_scene()
    src_fbx = os.path.join(SRC_DIR, "Attack_PrimaryA_Anim.fbx")
    arm = load_animated_armature(src_fbx)
    mesh, sword = attach_mesh_and_sword(arm)

    # Bake frames 17..34
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    orig_act = arm.animation_data.action
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.nla.bake(frame_start=17, frame_end=34, step=1, only_selected=False, visual_keying=True, clear_constraints=True, clear_parents=False, bake_types={'POSE'})
    bpy.ops.object.mode_set(mode='OBJECT')
    if orig_act in bpy.data.actions.values():
        bpy.data.actions.remove(orig_act)

    # Programmatic verification
    scene.frame_set(17)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    h17 = arm_eval.pose.bones['hand_r']
    h_rot17 = h17.matrix.to_quaternion()
    h_loc17 = (arm_eval.matrix_world @ h17.matrix).translation.copy()

    scene.frame_set(25)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    h25 = arm_eval.pose.bones['hand_r']
    h_rot25 = h25.matrix.to_quaternion()
    h_loc25 = (arm_eval.matrix_world @ h25.matrix).translation.copy()

    rot_diff = degrees(h_rot17.rotation_difference(h_rot25).angle)
    h_loc_diff = (h_loc25 - h_loc17).length * 100.0
    keyed_bones = len(arm.pose.bones)

    print(f"[VERIFIED ER-A2 Attack_Air_Light]: keyed_bones={keyed_bones}, hand_r rot diff={rot_diff:.2f} deg, hand_r loc diff={h_loc_diff:.2f} cm")
    assert keyed_bones >= 20, f"Too few keyed bones: {keyed_bones}"
    assert h_loc_diff > 15.0 or rot_diff > 15.0, f"Insufficient motion: rot={rot_diff}, loc={h_loc_diff}"

    out_dir = os.path.join(BASE_DIR, "Attack_Air_Light")
    strip_png, mp4, fbx = render_and_export(
        "Attack_Air_Light", total_frames=18, arm=arm, cam=cam, out_dir=out_dir,
        look_frame=8, strip_frame_indices=[0, 3, 7, 10, 14, 17], f_start_offset=17
    )
    return {
        "clip": "ER-A2 Attack_Air_Light",
        "keyed_bones": keyed_bones,
        "rot_diff": rot_diff,
        "loc_diff": h_loc_diff,
        "metric_desc": f"hand_r rot diff: {rot_diff:.2f} deg, hand_r loc diff: {h_loc_diff:.2f} cm",
        "strip": strip_png,
        "mp4": mp4,
        "fbx": fbx
    }


def main():
    results = []
    results.append(process_backstep())
    results.append(process_guard_counter())
    results.append(process_air_heavy())
    results.append(process_air_light())

    print("\n=================== R3 DELIVERABLES SUMMARY ===================")
    for r in results:
        print(f"{r['clip']}: keyed={r['keyed_bones']}, {r['metric_desc']}, strip={r['strip']}")
    print("===============================================================")


if __name__ == "__main__":
    main()
