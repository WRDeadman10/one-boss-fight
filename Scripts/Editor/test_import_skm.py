import unreal
import os

fbx_file = "C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/Characters/Builds/SKM_Roundtrip_Test.fbx"
dest_path = "/Game/OneBossFight/Characters/Builds"
dest_name = "SKM_Roundtrip_Test"

skel = unreal.load_asset("/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin")

task = unreal.AssetImportTask()
task.filename = fbx_file
task.destination_path = dest_path
task.destination_name = dest_name
task.replace_existing = True
task.automated = True
task.save = True

options = unreal.FbxImportUI()
options.import_mesh = True
options.import_as_skeletal = True
options.skeleton = skel
options.import_materials = False
options.import_textures = False
options.skeletal_mesh_import_data.set_editor_property("use_t0_as_ref_pose", True)

task.options = options

unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

imported_asset = unreal.load_asset(f"{dest_path}/{dest_name}")
print(f"[TEST_IMPORT] Result asset: {imported_asset}")
if imported_asset:
    mesh_skel = imported_asset.get_editor_property("skeleton")
    print(f"[TEST_IMPORT] Skeleton: {mesh_skel}")
    print(f"[TEST_IMPORT] Skeleton matches SK_CombatMannequin: {mesh_skel == skel}")
