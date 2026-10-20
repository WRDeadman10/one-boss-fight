import unreal
log = lambda m: unreal.log("[PawnInfo] " + m)
for path in ("/Game/OneBossFight/SevarogPack/BP_SevarogBossPack", "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss",
             "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BP_MasterEnemy"):
    bp = unreal.load_asset(path)
    cdo = unreal.get_default_object(bp.generated_class())
    for n in ("EnemyInfo", "EnemyInfoRef"):
        log("%s.%s = %s" % (path.split("/")[-1], n, cdo.get_editor_property(n)))
