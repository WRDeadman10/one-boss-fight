import unreal
import os

skins = [
    ("/Game/ParagonGreystone/Characters/Heroes/Greystone/Skins/WhiteTiger/Meshes/Greystone_WhiteTiger", "Greystone_WhiteTiger.fbx"),
    ("/Game/ParagonGreystone/Characters/Heroes/Greystone/Skins/Dragonlord/Meshes/Greystone_Dragonlord", "Greystone_Dragonlord.fbx"),
    ("/Game/ParagonGreystone/Characters/Heroes/Greystone/Skins/Novaborn/Meshes/Greystone_Novaborn", "Greystone_Novaborn.fbx"),
    ("/Game/ParagonGreystone/Characters/Heroes/Greystone/Skins/Tough/Meshes/Greystone_Tough", "Greystone_Tough.fbx"),
]

out_dir = "C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/Characters"
os.makedirs(out_dir, exist_ok=True)

fbx_opt = unreal.FbxExportOption()
fbx_opt.collision = False
fbx_opt.vertex_color = True

for path, fbx_name in skins:
    asset = unreal.load_asset(path)
    if not asset:
        print(f"[-] Could not load {path}")
        continue
    
    out_file = os.path.join(out_dir, fbx_name).replace("\\", "/")
    task = unreal.AssetExportTask()
    task.object = asset
    task.filename = out_file
    task.automated = True
    task.replace_identical = True
    task.prompt = False
    task.options = fbx_opt
    
    res = unreal.Exporter.run_asset_export_task(task)
    sz = os.path.getsize(out_file) if os.path.exists(out_file) else 0
    print(f"[+] Exported {fbx_name}: result={res}, size={sz} bytes")

print("[EXPORT] Done!")
