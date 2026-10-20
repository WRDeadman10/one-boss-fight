import os
import unreal

mesh_path = "/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone"
mesh = unreal.load_asset(mesh_path)
print(f"Loaded Greystone: {mesh}")

out_path = "C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/Characters/Greystone.fbx"
os.makedirs(os.path.dirname(out_path), exist_ok=True)

export_task = unreal.AssetExportTask()
export_task.object = mesh
export_task.filename = out_path
export_task.selected = False
export_task.replace_identical = True
export_task.prompt = False
export_task.automated = True
export_task.options = unreal.FbxExportOption()
export_task.options.set_editor_property("collision", False)
export_task.options.set_editor_property("vertex_color", True)

res = unreal.Exporter.run_asset_export_task(export_task)
print(f"Greystone export: {res}, size={os.path.getsize(out_path) if os.path.exists(out_path) else 0}")
