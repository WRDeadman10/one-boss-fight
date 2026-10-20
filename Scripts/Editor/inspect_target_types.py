"""How the pack configures trace targets: PlayerInfo.Default Target Types, BP_UnarmedTraceTarget.CollisionSocketNames, enemy infos."""
import unreal

log = lambda m: unreal.log("[TargetTypes] " + m)
A = "/Game/AdvancedARPGCombat/"
pi = unreal.load_asset(A + "MeleeCombatSystem/Blueprints/DataAssets/PlayerInfo")
for k, v in pi.get_editor_property("Default Target Types").items():
    log("PlayerInfo %s => %s" % (k.export_text(), v.get_path_name() if hasattr(v, "get_path_name") else v))

cls = unreal.load_object(None, A + "AdvancedCombatFramework/CoreCombatSystem/Collision/BP_UnarmedTraceTarget.BP_UnarmedTraceTarget_C")
cdo = unreal.get_default_object(cls)
for n in ("CollisionSocketNames", "TargetTypeTag", "Collision Radius", "CollisionRadius"):
    try:
        v = cdo.get_editor_property(n)
        if isinstance(v, (dict, unreal.Map)):
            for kk, vv in v.items():
                log("Unarmed.%s %s => %s" % (n, kk.export_text() if hasattr(kk, "export_text") else kk, vv.export_text() if hasattr(vv, "export_text") else vv))
        else:
            log("Unarmed.%s = %s" % (n, v.export_text() if hasattr(v, "export_text") else v))
    except Exception as e:
        log("Unarmed.%s failed %s" % (n, str(e)[:70]))

# Which enemy infos use Default Target Types?
registry = unreal.AssetRegistryHelpers.get_asset_registry()
for a in registry.get_assets_by_class(unreal.TopLevelAssetPath("/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/DataAssets", "BP_EnemyInfo_C")) if False else []:
    pass
for a in registry.get_assets_by_path(A + "MeleeCombatSystem/Blueprints/AI/Enemies", recursive=True):
    if "BP_EnemyInfo" in str(a.asset_class_path.asset_name):
        o = a.get_asset()
        m = o.get_editor_property("Default Target Types")
        log("%s targets=%s" % (a.asset_name, {k.export_text(): (v.get_path_name() if hasattr(v, "get_path_name") else str(v)) for k, v in m.items()}))
