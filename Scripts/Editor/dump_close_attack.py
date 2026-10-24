"""Read-only dump for the authored-clips design (log prefix [CloseDump]): the properties of the pack's GA_GS_Boss_CloseAttack_C (class defaults) and the notifies of the four pack montages GS_Attack01..04 (class, trigger time, duration), plus the montage slot and section names, and the authored clips' lengths."""
import unreal

log = lambda m: unreal.log("[CloseDump] " + m)
BASE = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/"
for path in ("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/GreatswordBoss/GA_GS_Boss_CloseAttack", ):
    pass
# find the ability asset by name
reg = unreal.AssetRegistryHelpers.get_asset_registry()
found = [a for a in reg.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", "Blueprint")) if "GA_GS_Boss_CloseAttack" in str(a.asset_name)]
for a in found:
    log("ability asset %s" % a.package_name)
    bp = unreal.load_asset(str(a.package_name))
    gen = bp.generated_class() if hasattr(bp, "generated_class") else None
    log("  generated class %s" % gen)
    cdo = unreal.get_default_object(gen) if gen else None
    if cdo:
        for name in sorted(dir(cdo)):
            if name.startswith("_") or callable(getattr(cdo, name, None)):
                continue
            try:
                v = cdo.get_editor_property(name)
            except Exception:
                continue
            log("  prop %s = %s" % (name, str(v)[:240]))
for i in (1, 2, 3, 4):
    hits = [a for a in reg.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", "AnimMontage")) if str(a.asset_name) == "GS_Attack0%d_Montage" % i]
    for a in hits:
        m = unreal.load_asset(str(a.package_name))
        log("montage %s length %.3f" % (a.package_name, m.get_editor_property("sequence_length")))
        try:
            for n in m.get_editor_property("notifies"):
                log("   notify '%s' trigger %.3f duration %.3f notify %s state %s" % (n.get_editor_property("notify_name"), n.get_editor_property("link_value") if False else n.get_editor_property("trigger_time_offset") if False else n.get_editor_property("display_time") if hasattr(n, "get_editor_property") else -1, n.get_editor_property("duration"), n.get_editor_property("notify"), n.get_editor_property("notify_state_class")))
        except Exception as e:
            log("   notifies: %s" % e)
        try:
            log("   sections %s" % [(str(x.get_editor_property("section_name")), round(x.get_editor_property("start_time"), 3)) for x in m.get_editor_property("composite_sections")])
        except Exception as e:
            log("   sections: %s" % e)
log("DONE")
