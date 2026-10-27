"""Isolated TEST catalog for the live fourth-weapon equip (Codex lead decision C170, X-156 2026-10-26). Creates three NEW assets only under
/Game/OneBossFight/Data/TypedABIFixtures: DA_ABITest_Weapon_Fourth, DA_ABITest_Build_Fourth and DA_ABITest_Catalog. The catalog lists the three SHIPPED weapon and build
definitions (referenced, never edited; the pinned three-build contract requires them) plus the fourth weapon of the typed-ABI fixtures (own item, style, actor and ability).
It is only read when rpg.CatalogPath names it (non-Shipping). The shipped DA_CombatCatalog and every pack asset stay untouched; the script refuses to overwrite an existing asset.
Log prefix [ABITestCatalog]."""
import hashlib
import os
import unreal

SHIPPED = "/Game/OneBossFight/Data/Catalog"
ROOT = "/Game/OneBossFight/Data/TypedABIFixtures"
PROJECT = "C:/UnrealProject/OneBossFight/Content"
EAL = unreal.EditorAssetLibrary
log = lambda msg: unreal.log("[ABITestCatalog] " + msg)

TARGETS = {
    "weapon": ROOT + "/DA_ABITest_Weapon_Fourth",
    "build": ROOT + "/DA_ABITest_Build_Fourth",
    "catalog": ROOT + "/DA_ABITest_Catalog",
}
WATCH = ["/OneBossFight/Data/Catalog/%s.uasset" % n for n in ("DA_CombatCatalog", "DA_Weapon_Sword", "DA_Weapon_Claymore", "DA_Weapon_DualSwords", "DA_Build_Starter", "DA_Build_Strength", "DA_Build_Dex")]


def sha(rel):
    path = PROJECT + rel
    return hashlib.sha256(open(path, "rb").read()).hexdigest() if os.path.exists(path) else "absent"


def create(key, cls, values):
    path = TARGETS[key]
    if EAL.does_asset_exist(path):
        raise RuntimeError("refused: fixture target exists " + path)
    obj = unreal.AssetToolsHelpers.get_asset_tools().create_asset(path.rsplit("/", 1)[1], ROOT, cls, unreal.DataAssetFactory())
    if obj is None:
        raise RuntimeError("creation failed: " + path)
    for name, value in values.items():
        obj.set_editor_property(name, value)  # NEW editor asset, never a component in PIE
    if not EAL.save_loaded_asset(obj):
        raise RuntimeError("save failed: " + path)
    log("CREATED " + path)
    return obj


before = {p: sha(p) for p in WATCH}
shipped_weapons = [EAL.load_asset(SHIPPED + "/" + n) for n in ("DA_Weapon_Sword", "DA_Weapon_Claymore", "DA_Weapon_DualSwords")]
shipped_builds = [EAL.load_asset(SHIPPED + "/" + n) for n in ("DA_Build_Starter", "DA_Build_Strength", "DA_Build_Dex")]
if not all(shipped_weapons + shipped_builds):
    raise RuntimeError("a shipped definition is missing")
item = EAL.load_asset(ROOT + "/DA_ABI_FourthWeaponItem")
if item is None:
    raise RuntimeError("run Scripts/Editor/make_typed_abi_fixtures.py first")

# The fourth weapon: FRESH structs (never the struct returned by get_editor_property of a shipped definition: that is a reference into the shipped asset, and writing to it dirties the
# shipped DA_Weapon_Sword / DA_Build_Starter, which the editor then saves on close; this happened once on 2026-10-26 and was restored from git). Values equal the ones the
# TypedABIFixtures automation test compiles.
cls = lambda name: ROOT + "/" + name + "." + name + "_C"
obj = lambda name: ROOT + "/" + name + "." + name
w = unreal.RPGCatalogWeapon()
for key, value in dict(weapon_id="ABIFourthWeapon", style_name="DA_ABI_FourthCombatStyle", style_asset=unreal.SoftObjectPath(obj("DA_ABI_FourthCombatStyle")),
                       item_path=unreal.SoftObjectPath(obj("DA_ABI_FourthWeaponItem")), item_base_class=unreal.SoftObjectPath(item.get_class().get_path_name()),
                       actor_class=unreal.SoftObjectPath(cls("BP_ABI_FourthWeaponActor")), ability_class=unreal.SoftObjectPath(cls("GA_ABI_FourthMelee")),
                       hud_weapon_word="ABI Fourth", style_aliases=[], alias_hud_words={},
                       actions=[unreal.RPGAttackKind.LIGHT, unreal.RPGAttackKind.STRONG, unreal.RPGAttackKind.CHARGED,
                                unreal.RPGAttackKind.JUMP_LIGHT, unreal.RPGAttackKind.JUMP_HEAVY, unreal.RPGAttackKind.KNOCKDOWN]).items():
    w.set_editor_property(key, value)
b = unreal.RPGCatalogBuild()
for key, value in dict(build_id="ABIFourth", console_name="ABIFourth", display_name="ABI Fourth", aliases=[], ui_order=3, legacy_slot=-1,
                       weapon_id="ABIFourthWeapon").items():
    b.set_editor_property(key, value)

weapon_asset = create("weapon", unreal.RPGWeaponDefinition, {"definition": w})
build_asset = create("build", unreal.RPGBuildDefinition, {"definition": b})
create("catalog", unreal.RPGCombatCatalog, {"schema_version": 1, "weapons": shipped_weapons + [weapon_asset], "builds": shipped_builds + [build_asset]})
dirty = [p.get_path_name() for p in shipped_weapons + shipped_builds if p.get_outermost().is_dirty()]
log("shipped definitions dirty in memory: %s" % dirty)
if dirty:
    raise RuntimeError("a shipped definition is dirty in memory: the editor would save it on close")
after = {p: sha(p) for p in WATCH}
log("shipped catalog and definitions unchanged: %s" % (before == after))
if before != after:
    raise RuntimeError("a shipped catalog asset changed")
log("done; three new assets, no existing asset changed")
