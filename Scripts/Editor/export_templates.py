import unreal
import os

out_dir = "C:/UnrealProject/OneBossFight/Saved/Templates_t3d"
os.makedirs(out_dir, exist_ok=True)

templates = [
    ("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryA_Montage", "Attack_PrimaryA_Montage.t3d"),
    ("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Ability_E_Anim_Montage", "Ability_E_Anim_Montage.t3d"),
    ("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/HitReactions/HitReact_Back_Montage", "HitReact_Back_Montage.t3d"),
]

for path, fname in templates:
    obj = unreal.load_asset(path)
    if not obj:
        unreal.log_error(f"Failed to load {path}")
        continue
    out_file = os.path.join(out_dir, fname)
    task = unreal.AssetExportTask()
    task.object = obj
    task.filename = out_file
    task.automated = True
    task.prompt = False
    task.replace_identical = True
    res = unreal.Exporter.run_asset_export_task(task)
    unreal.log(f"Exported {path} to {out_file}: {res}")
