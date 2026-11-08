"""Lead read-only (C-992): export montages to .t3d (text) in this folder to compare notify-state instance properties. Saves no asset."""
import unreal
OUT = "C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/P_C992_AIRHITS/t3d"
ASSETS = ["/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryA_Montage",
          "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryB_Montage",
          "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Light",
          "/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter"]
for path in ASSETS:
    task = unreal.AssetExportTask()
    task.object = unreal.load_asset(path)
    task.filename = "%s/%s.t3d" % (OUT, path.split("/")[-1])
    task.automated = True
    task.prompt = False
    task.replace_identical = True
    unreal.log("[ExportText] %s -> %s" % (path.split("/")[-1], unreal.Exporter.run_asset_export_task(task)))
unreal.SystemLibrary.quit_editor()
