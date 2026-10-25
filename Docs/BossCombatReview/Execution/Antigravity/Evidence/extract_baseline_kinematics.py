"""
extract_baseline_kinematics.py
Offline kinematic extraction script for CI-P0-A-01 (Revision 05).
Tool: Blender 5.1.2 (headless) / Python 3.11+
Outputs: raw_kinematic_extraction.log, SHA-256 input hashes, bone bounds, root excursion.

Provenance and Tooling Specifications:
- Blender Version: 5.1.2 (hash ec6e62d40fa9 built 2026-05-19)
- Import Settings: bpy.ops.import_scene.fbx(filepath=path) default importer
- Scene Units: Metric, Unit Scale = 1.0, Length Unit = METERS
- Coordinate Frame: Blender Right-Handed (Z-Up, Y-Forward, X-Right)
- Bound Box Computation: Object bound_box transformed by matrix_world gives world-space
  axis-aligned extents in meters, scaled by 100 to report in centimeters. For meshes
  at origin with identity object transform, world bounds match mesh local bounds.
- Root Sampling Guard: Samples pose bone 'root' if present; if absent, verifies whether the
  armature object itself represents the FBX 'root' node (arm.name == 'root') and samples
  arm.matrix_world. If no root node or bone exists, raises RuntimeError (fails loudly).
"""
import bpy
import os
import hashlib
import mathutils

ROOT_DIR = os.path.abspath(".")
ANIM_DIR = os.path.join(ROOT_DIR, "Import", "Boss01", "Animations")
WEAPON_DIR = os.path.join(ROOT_DIR, "Import", "Boss01", "Weapons")
REF_DIR = os.path.join(ROOT_DIR, "Import", "ThirdParty", "Reference")
OUT_LOG = os.path.join(ROOT_DIR, "Docs", "BossCombatReview", "Execution", "Antigravity", "Evidence", "raw_kinematic_extraction.log")

def get_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0

lines = []
def log(msg):
    lines.append(msg)
    print(msg)

log("================================================================================")
log("ANTIGRAVITY OFFLINE KINEMATIC & GEOMETRIC EXTRACTION LOG (REVISION 05)")
log("Initiative: P0-P8 Boss Combat Improvement Program (CI-P0-A-01)")
log("Tool: Blender 5.1.2 (headless) | Scene Units: Metric (1.0 scale, meters)")
log("Coordinate System: Blender Right-Handed (Z-Up, Y-Forward, X-Right)")
log("Provenance: Pose semantics cite authored .txt sidecars (author intent).")
log("Root Sampling: Strict guard against silent zero excursion on missing root.")
log("================================================================================\n")

# 1. Weapon Meshes
weapons = [
    ("Hidden Leader Reference Mesh", os.path.join(REF_DIR, "SM_KwangSword.fbx")),
    ("Visible Follower Project Mesh", os.path.join(WEAPON_DIR, "SM_Boss01_Greatsword.fbx")),
    ("Ember Javelin Project Mesh", os.path.join(WEAPON_DIR, "SM_Boss01_EmberJavelin.fbx"))
]

log("--- 1. WEAPON STATIC MESHES ---")
for role, path in weapons:
    if not os.path.exists(path):
        log(f"MISSING: {path}")
        continue
    sha = get_sha256(path)
    sz = os.path.getsize(path)
    clear_scene()
    bpy.ops.import_scene.fbx(filepath=path)
    
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    empties = [o for o in bpy.context.scene.objects if o.type == 'EMPTY']
    
    log(f"Asset: {os.path.basename(path)} ({role})")
    log(f"  Path: {path}")
    log(f"  SHA-256: {sha}")
    log(f"  Byte Size: {sz} bytes")
    
    for m in meshes:
        bpy.context.view_layer.objects.active = m
        bbox = [m.matrix_world @ mathutils.Vector(c) for c in m.bound_box]
        min_x, max_x = min(c.x for c in bbox), max(c.x for c in bbox)
        min_y, max_y = min(c.y for c in bbox), max(c.y for c in bbox)
        min_z, max_z = min(c.z for c in bbox), max(c.z for c in bbox)
        log(f"  Mesh: {m.name} | Verts: {len(m.data.vertices)} | Polys: {len(m.data.polygons)}")
        log(f"  World Bounds X (Width):  [{min_x*100:.2f}, {max_x*100:.2f}] cm (Delta: {(max_x - min_x)*100:.2f} cm)")
        log(f"  World Bounds Y (Thick):  [{min_y*100:.2f}, {max_y*100:.2f}] cm (Delta: {(max_y - min_y)*100:.2f} cm)")
        log(f"  World Bounds Z (Length): [{min_z*100:.2f}, {max_z*100:.2f}] cm (Delta: {(max_z - min_z)*100:.2f} cm)")
        log(f"  Blade Reach above Origin (Z>0): {max_z*100:.2f} cm")
        log(f"  Hilt Reach below Origin (Z<0):  {min_z*100:.2f} cm")
        
    for e in empties:
        t = e.matrix_world.translation * 100
        log(f"  Exported Empty/Socket: {e.name} at (X={t.x:.2f}, Y={t.y:.2f}, Z={t.z:.2f}) cm")
    log("")

# 2. Animation Clips
CLIPS = [
    "AN_Boss01_A1_QuickSlash",
    "AN_Boss01_A2_Raise",
    "AN_Boss01_A2_ApexHold",
    "AN_Boss01_A2_Slam",
    "AN_Boss01_A3a_Combo1",
    "AN_Boss01_A3b_Combo2",
    "AN_Boss01_A4_LowSweep",
    "AN_Boss01_A5_JavelinThrow",
    "AN_Boss01_DormantIdle",
    "AN_Boss01_Wake",
    "AN_Boss01_PhaseRoar",
    "AN_Boss01_StaggerFall",
    "AN_Boss01_StaggerDown",
    "AN_Boss01_StaggerGetUp",
    "AN_Boss01_DeathLegend",
    "AN_Riposte_Player_Front",
    "AN_Riposte_Boss_Reaction"
]

log("--- 2. ANIMATION CLIPS (30 FPS SKELETAL EXTRACTION) ---")
for clip in CLIPS:
    fbx_path = os.path.join(ANIM_DIR, clip + ".fbx")
    if not os.path.exists(fbx_path):
        log(f"MISSING CLIP: {clip}")
        continue
    sha = get_sha256(fbx_path)
    sz = os.path.getsize(fbx_path)
    clear_scene()
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    
    armatures = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
    if not armatures:
        raise RuntimeError(f"No armature found in {clip}")
    
    arm = armatures[0]
    action = arm.animation_data.action if arm.animation_data else None
    frame_start = int(action.frame_range[0]) if action else 1
    frame_end = int(action.frame_range[1]) if action else 1
    num_frames = frame_end - frame_start + 1
    fps = bpy.context.scene.render.fps
    elapsed_duration = (num_frames - 1) / fps if num_frames > 1 else 0.0
    
    bones = arm.pose.bones
    has_root_bone = "root" in bones
    is_armature_root = (arm.name.lower() == "root")
    
    if not (has_root_bone or is_armature_root):
        raise RuntimeError(f"FAIL-LOUD GUARD: No root bone or root armature found in {clip}!")
    
    root_sampling_mode = "pose_bone(root)" if has_root_bone else "armature_object(root)"
    
    has_pelvis = "pelvis" in bones
    has_hand_r = "hand_r" in bones
    
    root_start, root_end = None, None
    max_root_excursion = 0.0
    min_pelvis_z, max_pelvis_z = 9999.0, -9999.0
    min_foot_z, max_foot_z = 9999.0, -9999.0
    max_hand_r_dist2d = 0.0
    
    for f in range(frame_start, frame_end + 1):
        bpy.context.scene.frame_set(f)
        bpy.context.view_layer.update()
        
        if has_root_bone:
            r_mat = arm.matrix_world @ bones["root"].matrix
        else:
            r_mat = arm.matrix_world
            
        r_pos = r_mat.translation * 100 # cm
        if root_start is None:
            root_start = r_pos.copy()
        root_end = r_pos.copy()
        excursion = (r_pos - root_start).length
        if excursion > max_root_excursion:
            max_root_excursion = excursion
                
        if has_pelvis:
            p_mat = arm.matrix_world @ bones["pelvis"].matrix
            p_z = p_mat.translation.z * 100 # cm
            min_pelvis_z = min(min_pelvis_z, p_z)
            max_pelvis_z = max(max_pelvis_z, p_z)
            
        for ft_name in ["foot_r", "foot_l", "ball_r", "ball_l"]:
            if ft_name in bones:
                ft_mat = arm.matrix_world @ bones[ft_name].matrix
                ft_z = ft_mat.translation.z * 100
                min_foot_z = min(min_foot_z, ft_z)
                max_foot_z = max(max_foot_z, ft_z)
                
        if has_hand_r:
            hr_mat = arm.matrix_world @ bones["hand_r"].matrix
            hr_pos = hr_mat.translation * 100 # cm
            dist2d = mathutils.Vector((hr_pos.x, hr_pos.y)).length
            max_hand_r_dist2d = max(max_hand_r_dist2d, dist2d)

    end_start_disp = (root_end - root_start).length if (root_start and root_end) else 0.0

    log(f"Clip: {clip}.fbx")
    log(f"  SHA-256: {sha}")
    log(f"  Byte Size: {sz} bytes")
    log(f"  Frame Range: {frame_start} to {frame_end} ({num_frames} samples @ {fps} fps)")
    log(f"  Elapsed Duration: {elapsed_duration:.3f} s ((samples - 1) / fps)")
    log(f"  Root Sampling Mode: {root_sampling_mode}")
    log(f"  Max Root Excursion from Fr 1: {max_root_excursion:.4f} cm")
    log(f"  End-Minus-Start Root Displacement: {end_start_disp:.4f} cm")
    log(f"  Pelvis Bone-Origin Z Range: [{min_pelvis_z:.2f}, {max_pelvis_z:.2f}] cm")
    log(f"  Foot/Ball Bone-Origin Z Range: [{min_foot_z:.2f}, {max_foot_z:.2f}] cm")
    log(f"  Hand_R Max 2D Planar Distance from Origin: {max_hand_r_dist2d:.2f} cm")
    log("")

with open(OUT_LOG, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines) + "\n")

print(f"Extraction log written to: {OUT_LOG}")
