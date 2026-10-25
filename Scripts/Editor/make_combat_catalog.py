"""DD-1 step1 authoring helper. NOT run by Codex. Creates seven NEW assets only.
Existing assets are never edited/overwritten/deleted. Run only by Claude after review,
baseline acceptance and an explicit asset-authoring scope. Prefix [CombatCatalogAuthor]."""
import unreal

ROOT = "/Game/OneBossFight/Data/Catalog"
PACK = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/"
log = lambda msg: unreal.log("[CombatCatalogAuthor] " + msg)
ROWS = [
    ("Starter", "Sword", "SwordInstances", "ToughSword", "GA_Sword_Melee", "SwordCombatStyle", "Sword", "sword"),
    ("Strength", "Claymore", "ClaymoreInstances", "KwangSword", "GA_Claymore_Melee", "ClaymoreCombatStyle", "Claymore", "str"),
    ("Dex", "DualSwords", "DualSwordInstances", "DualSteelSwords", "GA_DuaSword_Melee", "DualSwordCombatStyle", "Dual Swords", "dexterity"),
]


def create(name, cls, values):
    path = ROOT + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        obj = unreal.EditorAssetLibrary.load_asset(path)
        if not isinstance(obj, cls):
            raise RuntimeError("existing asset has wrong type: " + path)
        log("UNCHANGED existing " + path)
        return obj
    obj = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, ROOT, cls, unreal.DataAssetFactory())
    if obj is None:
        raise RuntimeError("creation failed: " + path)
    for key, value in values.items():
        obj.set_editor_property(key, value)  # NEW editor asset, never a component in PIE
    if not unreal.EditorAssetLibrary.save_loaded_asset(obj):
        raise RuntimeError("save failed: " + path)
    log("CREATED " + path)
    return obj


def main():
    # Refuse all authoring if any required live dependency cannot be resolved first.
    pending = []
    for index, (build, folder, instances, item, ability, style, word, alias) in enumerate(ROWS):
        actor = PACK + "Weapons/" + folder + "/" + instances + "/BP_" + item
        ability_path = PACK + "Weapons/" + folder + "/" + ability
        style_path = PACK + "Weapons/" + folder + "/" + style
        item_path = PACK + "Items/Weapons/" + item
        if not all((unreal.load_asset(item_path), unreal.load_asset(style_path),
                    unreal.load_class(None, actor + ".BP_" + item + "_C"),
                    unreal.load_class(None, ability_path + "." + ability + "_C"))):
            raise RuntimeError("preflight missing dependency for " + build)
        w = unreal.RPGCatalogWeapon()
        for key, value in dict(weapon_id=build, style_name=style, style_asset=unreal.SoftObjectPath(style_path + "." + style),
                               item_path=unreal.SoftObjectPath(item_path + "." + item),
                               item_base_class=unreal.SoftObjectPath(unreal.load_asset(item_path).get_class().get_path_name()),
                               actor_class=unreal.SoftObjectPath(actor + ".BP_" + item + "_C"),
                               ability_class=unreal.SoftObjectPath(ability_path + "." + ability + "_C"), hud_weapon_word=word,
                               actions=[unreal.RPGAttackKind.LIGHT, unreal.RPGAttackKind.STRONG, unreal.RPGAttackKind.CHARGED,
                                        unreal.RPGAttackKind.JUMP_LIGHT, unreal.RPGAttackKind.JUMP_HEAVY, unreal.RPGAttackKind.KNOCKDOWN]).items():
            w.set_editor_property(key, value)
        if index in (0, 2):
            style_alias = "SwordAndShieldCombatStyle" if index == 0 else "TwinbladeCombatStyle"
            w.set_editor_property("style_aliases", [style_alias])
            w.set_editor_property("alias_hud_words", {style_alias: "Sword and Shield" if index == 0 else "Twinblades"})
        b = unreal.RPGCatalogBuild()
        icon = "/Game/OneBossFight/UI/Art/T_Boss01_Icon_" + build
        for key, value in dict(build_id=build, console_name=build, display_name=build, aliases=[alias], ui_order=index,
                               legacy_slot=index, weapon_id=build, icon=unreal.SoftObjectPath(icon + ".T_Boss01_Icon_" + build)).items():
            b.set_editor_property(key, value)
        w.set_editor_property("icon", b.get_editor_property("icon"))
        pending.append((build, w, b))
    unreal.EditorAssetLibrary.make_directory(ROOT)
    weapons, builds = [], []
    for name, weapon, build in pending:
        weapons.append(create("DA_Weapon_" + {"Starter": "Sword", "Strength": "Claymore", "Dex": "DualSwords"}[name], unreal.RPGWeaponDefinition, {"definition": weapon}))
        builds.append(create("DA_Build_" + name, unreal.RPGBuildDefinition, {"definition": build}))
    create("DA_CombatCatalog", unreal.RPGCombatCatalog, {"schema_version": 1, "weapons": weapons, "builds": builds})
    log("done; no existing asset changed. Fresh-session strict-data readback still required.")


main()
