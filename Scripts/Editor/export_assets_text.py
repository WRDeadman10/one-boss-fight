"""Exports assets to text under Saved/asset_text/ so their default values can be read with grep. Edit ASSETS below."""
import os
import unreal

OUT = "C:/Users/winss/Documents/Unreal Projects/OneBossFight/Saved/asset_text"
P = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/"
ASSETS = [P + "GA_GS_Boss_" + n for n in ("CloseAttack", "CloseRare", "EnterCombat", "ExitCombat", "HitStun", "LeapAttack", "MidRangeAttack", "RetaliationAttack", "SprintAttack", "TurnInPlace")]
ASSETS += ["/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/AI/" + n for n in ("GA_EnemyMeleeAttack", "GA_EnemyEnterCombat", "GA_EnemyHitStun", "GA_LeapAttack", "GA_EnemyTurnInPlace", "GA_EnemySprintAttack")]
ASSETS += [P + "ExampleGreatSwordBoss"]
os.makedirs(OUT, exist_ok=True)
for path in ASSETS:
    asset = unreal.load_asset(path)
    task = unreal.AssetExportTask()
    task.object = asset
    task.filename = "%s/%s.t3d" % (OUT, path.split("/")[-1])
    task.automated = True
    task.prompt = False
    task.replace_identical = True
    unreal.log("[ExportText] %s -> %s" % (path.split("/")[-1], unreal.Exporter.run_asset_export_task(task)))
