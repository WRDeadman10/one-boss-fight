"""Exports the pack mannequin (the skeleton every boss and player asset must use) as FBX for Blender work. Log prefix [Export].
Output: Import/ThirdParty/Reference/ (git ignored). Run with Scripts/run_in_editor.py."""
import os
import unreal

log = lambda m: unreal.log("[Export] " + m)
out_dir = os.path.abspath(os.path.join(unreal.SystemLibrary.get_project_directory(), "Import", "ThirdParty", "Reference"))
os.makedirs(out_dir, exist_ok=True)
items = [
    ("/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin_Simple", "SKM_CombatMannequin_Simple.fbx"),
    ("/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/Meshes/Weapons/Paragon/SM_KwangSword", "SM_KwangSword.fbx"),
]
for asset_path, fname in items:
    obj = unreal.load_asset(asset_path)
    if not obj:
        log("missing %s" % asset_path)
        continue
    task = unreal.AssetExportTask()
    task.object = obj
    task.filename = os.path.join(out_dir, fname)
    task.automated = True
    task.prompt = False
    task.replace_identical = True
    opt = unreal.FbxExportOption()
    opt.ascii = False
    opt.vertex_color = False
    opt.collision = False
    task.options = opt
    ok = unreal.Exporter.run_asset_export_task(task)
    log("%s -> %s ok=%s exists=%s" % (asset_path.split("/")[-1], task.filename, ok, os.path.exists(task.filename)))
log("done")
