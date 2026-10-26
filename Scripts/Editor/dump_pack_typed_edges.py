"""READ-ONLY typed property dump of the pack weapon classes (owner approval 2026-10-26, scratch only; asks Codex X-140). Writes text files PR5_*.txt
under Claude/Evidence/exports; changes no asset. Log prefix [TypedDump]."""
import os
import unreal

OUT = "C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/Evidence/exports"
B = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/"
C = "/Game/AdvancedARPGCombat/AdvancedCombatFramework/"
ASSETS = {  # name: (path, kind) kind: data = the asset object itself, cdo = the generated class default object
    "Item_ToughSword": (B + "Items/Weapons/ToughSword", "data"), "Item_KwangSword": (B + "Items/Weapons/KwangSword", "data"),
    "Item_DualSteelSwords": (B + "Items/Weapons/DualSteelSwords", "data"),
    "BP_ToughSword": (B + "Weapons/Sword/SwordInstances/BP_ToughSword", "cdo"), "BP_KwangSword": (B + "Weapons/Claymore/ClaymoreInstances/BP_KwangSword", "cdo"),
    "BP_DualSteelSwords": (B + "Weapons/DualSwords/DualSwordInstances/BP_DualSteelSwords", "cdo"),
    "SwordCombatStyle": (B + "Weapons/Sword/SwordCombatStyle", "data"), "ClaymoreCombatStyle": (B + "Weapons/Claymore/ClaymoreCombatStyle", "data"),
    "DualSwordCombatStyle": (B + "Weapons/DualSwords/DualSwordCombatStyle", "data"),
    "GA_Sword_Melee": (B + "Weapons/Sword/GA_Sword_Melee", "cdo"), "GA_Claymore_Melee": (B + "Weapons/Claymore/GA_Claymore_Melee", "cdo"),
    "GA_DuaSword_Melee": (B + "Weapons/DualSwords/GA_DuaSword_Melee", "cdo"),
    "WeaponItem": (C + "CoreCombatSystem/DataAssets/Items/WeaponItem", "cdo"), "DualWeaponItem": (C + "CoreCombatSystem/DataAssets/Items/DualWeaponItem", "cdo"),
    "BP_BaseWeapon": (C + "CoreCombatSystem/Actors/Weapons/BP_BaseWeapon", "cdo"),
    "BP_AdvancedGameplayAbility": (C + "AbilitySystem/Abilities/BP_AdvancedGameplayAbility", "cdo"),
    "BP_CombatStyle": (C + "CoreCombatSystem/DataAssets/BP_CombatStyle", "cdo"),
}
os.makedirs(OUT, exist_ok=True)
done = 0
for name, (path, kind) in ASSETS.items():
    leaf = path.rsplit("/", 1)[1]
    if kind == "cdo":
        cls = unreal.load_class(None, path + "." + leaf + "_C")
        obj = unreal.get_default_object(cls) if cls else None
    else:
        obj = unreal.load_asset(path)
    if obj is None:
        unreal.log("[TypedDump] %s: NOT FOUND" % name)
        continue
    lines = unreal.RPGScratchRouteALibrary.dump_typed_properties(obj)
    with open("%s/PR5_%s.txt" % (OUT, name), "w", encoding="utf-8") as handle:
        handle.write("\n".join(str(l) for l in lines) + "\n")
    done += 1
    unreal.log("[TypedDump] %s: %d lines" % (name, len(lines)))
unreal.log("[TypedDump] done %d of %d" % (done, len(ASSETS)))
