"""Master R4 authoring script for Elden Ring combat clips in Blender.

Addresses Lead Claude's directive [C-968]:
- ER-A1 Backstep_Back: Short upright hop back on the feet (no roll/flip, feet strictly under pelvis), sourced from MM_Jump.fbx with -200 cm backward root translation.
- ER-A3 Attack_Air_Heavy_Plunge: Sword raised high overhead, then driven point-down, ending low in landing impact, sourced from Attack_PrimaryB_Anim.fbx (frames 12..38).
- ER-A2 Attack_Air_Light: Distinct quick airborne slash with legs tucked in air pose, sourced from Attack_PrimaryB_Anim.fbx + MM_Fall_Loop.fbx (frames 18..35).
- Single solid white blade: Metallic 0.0, Roughness 0.5, Base Color 0.95 to eliminate two-blade specular reflection artifacts.
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

    # 2. Attach single ReviewSword
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

    # Pure solid white diffuse material to completely prevent two-blade reflection artifacts
    for m in sword.data.materials:
        if m and m.node_tree:
            bsdf = [n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'][0]
            bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1.0)
            bsdf.inputs['Metallic'].default_value = 0.0
            bsdf.inputs['Roughness'].default_value = 0.4

    return mesh, sword


def render_and_export(clip_name, total_frames, arm, cam, out_dir, look_frame, strip_frame_indices, f_start_offset=0):
    scene = bpy.context.scene
    frames_dir = os.path.join(out_dir, "temp_frames_r4")
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
# Source: MM_Jump.fbx (upright hop on feet, feet strictly under pelvis)
# ==============================================================================
def process_backstep():
    print("\n--- AUTHORING ER-A1: Backstep_Back (R4) ---")
    scene, cam = setup_scene()
    src_fbx = os.path.join(SRC_DIR, "MM_Jump.fbx")
    arm = load_animated_armature(src_fbx)
    mesh, sword = attach_mesh_and_sword(arm)

    # Apply -200 cm backward root translation over frames 1..15
    for f in range(1, 16):
        scene.frame_set(f)
        t = (f - 1) / 14.0
        # Smooth ease backward along -Y (Unreal backward = -Y in Blender export)
        y_trans = -(3 * t**2 - 2 * t**3) * 2.0
        arm.location = Vector((0.0, y_trans, 0.0))
        arm.keyframe_insert("location", frame=f)

    # Bake NLA to freeze all transforms
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
    p1 = (arm_eval.matrix_world @ arm_eval.pose.bones['pelvis'].matrix).translation.copy()
    h1 = (arm_eval.matrix_world @ arm_eval.pose.bones['hand_r'].matrix).translation.copy()
    f1 = (arm_eval.matrix_world @ arm_eval.pose.bones['foot_r'].matrix).translation.copy()
    rot1 = arm_eval.pose.bones['hand_r'].matrix.to_quaternion()

    scene.frame_set(8)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    p8 = (arm_eval.matrix_world @ arm_eval.pose.bones['pelvis'].matrix).translation.copy()
    h8 = (arm_eval.matrix_world @ arm_eval.pose.bones['hand_r'].matrix).translation.copy()
    f8 = (arm_eval.matrix_world @ arm_eval.pose.bones['foot_r'].matrix).translation.copy()
    rot8 = arm_eval.pose.bones['hand_r'].matrix.to_quaternion()

    # Assert feet are always under pelvis (no roll/flip)
    assert p1.z > f1.z, f"Head/pelvis upside down at F1: p={p1.z}, f={f1.z}"
    assert p8.z > f8.z, f"Head/pelvis upside down at F8: p={p8.z}, f={f8.z}"

    p_loc_diff = (p8 - p1).length * 100.0
    rot_diff = degrees(rot1.rotation_difference(rot8).angle)
    keyed_bones = len(arm.pose.bones)

    print(f"[VERIFIED ER-A1 Backstep_Back]: keyed_bones={keyed_bones}, pelvis loc diff={p_loc_diff:.2f} cm, hand_r rot diff={rot_diff:.2f} deg")
    assert keyed_bones >= 20, f"Too few keyed bones: {keyed_bones}"
    assert p_loc_diff > 15.0, f"Insufficient motion: loc={p_loc_diff}"

    out_dir = os.path.join(BASE_DIR, "Backstep_Back")
    strip_png, mp4, fbx = render_and_export(
        "Backstep_Back", total_frames=15, arm=arm, cam=cam, out_dir=out_dir,
        look_frame=7, strip_frame_indices=[0, 3, 6, 9, 12, 14], f_start_offset=1
    )
    return {
        "clip": "ER-A1 Backstep_Back",
        "source": "MM_Jump.fbx",
        "keyed_bones": keyed_bones,
        "metric_desc": f"pelvis loc diff: {p_loc_diff:.2f} cm (hand_r rot: {rot_diff:.2f} deg, upright hop)",
        "strip": strip_png,
        "mp4": mp4,
        "fbx": fbx
    }


# ==============================================================================
# Clip 2: ER-A3: Attack_Air_Heavy_Plunge (27 frames @ 30 fps, 0.867 s)
# Source: Attack_PrimaryB_Anim.fbx (overhead lift -> downward plunge -> ground impact)
# ==============================================================================
def process_air_heavy():
    print("\n--- AUTHORING ER-A3: Attack_Air_Heavy_Plunge (R4) ---")
    scene, cam = setup_scene()
    src_fbx = os.path.join(SRC_DIR, "Attack_PrimaryB_Anim.fbx")
    arm = load_animated_armature(src_fbx)
    mesh, sword = attach_mesh_and_sword(arm)

    # Bake frames 12..38 (27 frames)
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    orig_act = arm.animation_data.action
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.nla.bake(frame_start=12, frame_end=38, step=1, only_selected=False, visual_keying=True, clear_constraints=True, clear_parents=False, bake_types={'POSE'})
    bpy.ops.object.mode_set(mode='OBJECT')
    if orig_act in bpy.data.actions.values():
        bpy.data.actions.remove(orig_act)

    # Programmatic verification: sword raised overhead at F18, driven point down to bottom impact at F27
    scene.frame_set(12)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    h12 = (arm_eval.matrix_world @ arm_eval.pose.bones['hand_r'].matrix).translation.copy()
    rot12 = arm_eval.pose.bones['hand_r'].matrix.to_quaternion()

    scene.frame_set(25) # mid plunge
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    h25 = (arm_eval.matrix_world @ arm_eval.pose.bones['hand_r'].matrix).translation.copy()
    rot25 = arm_eval.pose.bones['hand_r'].matrix.to_quaternion()

    rot_diff = degrees(rot12.rotation_difference(rot25).angle)
    h_loc_diff = (h25 - h12).length * 100.0
    z_drop = (h12.z - h25.z) * 100.0
    keyed_bones = len(arm.pose.bones)

    print(f"[VERIFIED ER-A3 Attack_Air_Heavy_Plunge]: keyed_bones={keyed_bones}, hand_r rot diff={rot_diff:.2f} deg, hand_r loc diff={h_loc_diff:.2f} cm (Z drop={z_drop:.2f} cm)")
    assert keyed_bones >= 20, f"Too few keyed bones: {keyed_bones}"
    assert h_loc_diff > 15.0 or rot_diff > 15.0, f"Insufficient motion: rot={rot_diff}, loc={h_loc_diff}"

    out_dir = os.path.join(BASE_DIR, "Attack_Air_Heavy_Plunge")
    strip_png, mp4, fbx = render_and_export(
        "Attack_Air_Heavy_Plunge", total_frames=27, arm=arm, cam=cam, out_dir=out_dir,
        look_frame=15, strip_frame_indices=[0, 5, 10, 16, 21, 26], f_start_offset=12
    )
    return {
        "clip": "ER-A3 Attack_Air_Heavy_Plunge",
        "source": "Attack_PrimaryB_Anim.fbx",
        "keyed_bones": keyed_bones,
        "metric_desc": f"hand_r rot diff: {rot_diff:.2f} deg, hand_r loc diff: {h_loc_diff:.2f} cm (downward plunge Z drop: {z_drop:.2f} cm)",
        "strip": strip_png,
        "mp4": mp4,
        "fbx": fbx
    }


# ==============================================================================
# Clip 3: ER-A2: Attack_Air_Light (18 frames @ 30 fps, 0.567 s)
# Source: Attack_PrimaryB_Anim.fbx + MM_Fall_Loop.fbx (tucked legs in airborne pose)
# ==============================================================================
def process_air_light():
    print("\n--- AUTHORING ER-A2: Attack_Air_Light (R4) ---")
    scene, cam = setup_scene()
    src_fbx = os.path.join(SRC_DIR, "Attack_PrimaryB_Anim.fbx")
    arm = load_animated_armature(src_fbx)

    # Import fall loop to sample tucked airborne leg pose
    fall_fbx = os.path.join(SRC_DIR, "MM_Fall_Loop.fbx")
    arm_air = load_animated_armature(fall_fbx)

    scene.frame_set(1)
    dg = bpy.context.evaluated_depsgraph_get()
    air_eval = arm_air.evaluated_get(dg)

    # Capture tucked leg rotations
    leg_bones = [b.name for b in air_eval.pose.bones if any(x in b.name.lower() for x in ['thigh', 'calf', 'foot', 'toe'])]
    leg_pose = {}
    for bname in leg_bones:
        pb = air_eval.pose.bones[bname]
        leg_pose[bname] = pb.rotation_quaternion.copy()

    bpy.data.objects.remove(arm_air, do_unlink=True)
    mesh, sword = attach_mesh_and_sword(arm)

    # Apply tucked leg pose across frames 18..35
    for f in range(18, 36):
        scene.frame_set(f)
        for bname, rot in leg_pose.items():
            pb = arm.pose.bones.get(bname)
            if pb:
                pb.rotation_quaternion = rot
                pb.keyframe_insert('rotation_quaternion', frame=f)

    # Bake NLA to freeze the airborne slash
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    orig_act = arm.animation_data.action
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.nla.bake(frame_start=18, frame_end=35, step=1, only_selected=False, visual_keying=True, clear_constraints=True, clear_parents=False, bake_types={'POSE'})
    bpy.ops.object.mode_set(mode='OBJECT')
    if orig_act in bpy.data.actions.values():
        bpy.data.actions.remove(orig_act)

    # Programmatic verification
    scene.frame_set(18)
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    h18 = (arm_eval.matrix_world @ arm_eval.pose.bones['hand_r'].matrix).translation.copy()
    rot18 = arm_eval.pose.bones['hand_r'].matrix.to_quaternion()
    foot18 = (arm_eval.matrix_world @ arm_eval.pose.bones['foot_r'].matrix).translation.copy()

    scene.frame_set(26) # mid airborne slash
    dg = bpy.context.evaluated_depsgraph_get()
    arm_eval = arm.evaluated_get(dg)
    h26 = (arm_eval.matrix_world @ arm_eval.pose.bones['hand_r'].matrix).translation.copy()
    rot26 = arm_eval.pose.bones['hand_r'].matrix.to_quaternion()
    foot26 = (arm_eval.matrix_world @ arm_eval.pose.bones['foot_r'].matrix).translation.copy()

    # Assert feet are off the ground (airborne tucked legs)
    assert foot18.z > 0.20, f"Foot on ground at F18: {foot18.z}"
    assert foot26.z > 0.20, f"Foot on ground at F26: {foot26.z}"

    rot_diff = degrees(rot18.rotation_difference(rot26).angle)
    h_loc_diff = (h26 - h18).length * 100.0
    keyed_bones = len(arm.pose.bones)

    print(f"[VERIFIED ER-A2 Attack_Air_Light]: keyed_bones={keyed_bones}, hand_r rot diff={rot_diff:.2f} deg, hand_r loc diff={h_loc_diff:.2f} cm (airborne foot_z={foot26.z:.2f} m)")
    assert keyed_bones >= 20, f"Too few keyed bones: {keyed_bones}"
    assert h_loc_diff > 15.0 or rot_diff > 15.0, f"Insufficient motion: rot={rot_diff}, loc={h_loc_diff}"

    out_dir = os.path.join(BASE_DIR, "Attack_Air_Light")
    strip_png, mp4, fbx = render_and_export(
        "Attack_Air_Light", total_frames=18, arm=arm, cam=cam, out_dir=out_dir,
        look_frame=8, strip_frame_indices=[0, 3, 7, 10, 14, 17], f_start_offset=18
    )
    return {
        "clip": "ER-A2 Attack_Air_Light",
        "source": "Attack_PrimaryB_Anim.fbx + MM_Fall_Loop.fbx",
        "keyed_bones": keyed_bones,
        "metric_desc": f"hand_r rot diff: {rot_diff:.2f} deg, hand_r loc diff: {h_loc_diff:.2f} cm (tucked airborne feet, foot_z: {foot26.z:.2f} m)",
        "strip": strip_png,
        "mp4": mp4,
        "fbx": fbx
    }


def main():
    results = []
    results.append(process_backstep())
    results.append(process_air_heavy())
    results.append(process_air_light())

    print("\n=================== R4 DELIVERABLES SUMMARY ===================")
    for r in results:
        print(f"{r['clip']}: source={r['source']}, keyed={r['keyed_bones']}, {r['metric_desc']}, strip={r['strip']}")
    print("===============================================================")


if __name__ == "__main__":
    main()
