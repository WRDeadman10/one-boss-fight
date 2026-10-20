"""
import_all_builds.py - Imports all 6 character builds into Unreal Engine as SkeletalMeshes
bound to the project's SK_CombatMannequin skeleton.
"""

import os
import unreal

builds = [
    ("SKM_Samurai", "C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/Characters/Builds/SKM_Samurai.fbx"),
    ("SKM_IndianYoddha", "C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/Characters/Builds/SKM_IndianYoddha.fbx"),
    ("SKM_MedievalWarrior", "C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/Characters/Builds/SKM_MedievalWarrior.fbx"),
    ("SKM_Viking", "C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/Characters/Builds/SKM_Viking.fbx"),
    ("SKM_IndianGoddess", "C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/Characters/Builds/SKM_IndianGoddess.fbx"),
    ("SKM_GirlWarrior", "C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/Characters/Builds/SKM_GirlWarrior.fbx"),
]

dest_dir = "/Game/OneBossFight/Characters/Builds"
skel = unreal.load_asset("/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin")
print(f"[IMPORT_BUILDS] Target Skeleton: {skel}")

tasks = []
for name, fbx_path in builds:
    if not os.path.exists(fbx_path):
        print(f"[IMPORT_BUILDS] Warning: File not found {fbx_path}")
        continue
        
    task = unreal.AssetImportTask()
    task.filename = fbx_path
    task.destination_path = dest_dir
    task.destination_name = name
    task.replace_existing = True
    task.automated = True
    task.save = True
    
    options = unreal.FbxImportUI()
    options.import_mesh = True
    options.import_as_skeletal = True
    options.skeleton = skel
    options.import_materials = True
    options.import_textures = True
    options.skeletal_mesh_import_data.set_editor_property("use_t0_as_ref_pose", True)
    
    task.options = options
    tasks.append(task)

print(f"[IMPORT_BUILDS] Starting import of {len(tasks)} character builds...")
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)

print("[IMPORT_BUILDS] Verification of imported assets:")
for name, _ in builds:
    asset_path = f"{dest_dir}/{name}"
    loaded = unreal.load_asset(asset_path)
    if loaded:
        mesh_skel = loaded.get_editor_property("skeleton")
        print(f"  ✓ {name}: SUCCESS (Skeleton: {mesh_skel.get_name() if mesh_skel else 'None'})")
    else:
        print(f"  ✗ {name}: FAILED TO LOAD")

print("[IMPORT_BUILDS] Batch import complete!")
