import unreal
log = lambda m: unreal.log("[ItemSockets] " + m)
reg = unreal.AssetRegistryHelpers.get_asset_registry()
seen = set()
for d in reg.get_assets_by_path("/Game/AdvancedARPGCombat", recursive=True):
    cls = str(d.asset_class_path.asset_name)
    if cls in ("WeaponItem_C", "DualWeaponItem_C", "ShieldItem_C", "ToolItem_C", "ArmorItem_C", "AccesoryItem_C", "PotionItem_C"):
        a = d.get_asset()
        vals = []
        for n in ("DefaultAttachSocket", "ActiveAttachSocket", "SecondWeaponAttachSocket", "SecondWeaponActiveSocket"):
            try:
                vals.append("%s=%s" % (n, a.get_editor_property(n)))
            except Exception:
                pass
        log("%-28s %-14s %s" % (d.asset_name, cls, " ".join(vals)))
