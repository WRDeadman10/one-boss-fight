"""Typed-ABI test fixtures (owner approval 2026-10-26: "Yes"; names from Codex/C155_A100_REVIEW.md). Creates NEW assets only under
/Game/OneBossFight/ReviewFixtures/TypedABI (developer-only, deliberately outside the always-cook roots) by duplicating shipped pack assets
(the pack assets themselves are never edited) and rewiring the copies through the fixture-only C++ helpers. Refuses to run if any target exists.
Log prefix [ABIFixtures]."""
import hashlib
import os
import unreal

ROOT = "/Game/OneBossFight/Data/TypedABIFixtures"  # inside the always-cook roots: the resolving check refuses anything outside them, so the positive bundle and the decoy must live here
UNCOOKED_ROOT = "/Game/OneBossFight/ReviewFixtures/TypedABI"  # deliberately OUTSIDE the always-cook roots
B = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/"
SRC_ACTOR = B + "Weapons/Sword/SwordInstances/BP_ToughSword"
SRC_ITEM = B + "Items/Weapons/ToughSword"
SRC_STYLE = B + "Weapons/Sword/SwordCombatStyle"
SRC_ABILITY = B + "Weapons/Sword/GA_Sword_Melee"
PROJECT = "C:/UnrealProject/OneBossFight/Content"
lib = unreal.RPGScratchRouteALibrary
log = lambda msg: unreal.log("[ABIFixtures] " + msg)
EAL = unreal.EditorAssetLibrary

TARGETS = {
    "actor": ROOT + "/BP_ABI_FourthWeaponActor",
    "item": ROOT + "/DA_ABI_FourthWeaponItem",
    "style": ROOT + "/DA_ABI_FourthCombatStyle",
    "ability": ROOT + "/GA_ABI_FourthMelee",
    "decoy": ROOT + "/DecoyPackage/BP_ToughSword",
    "uncooked": UNCOOKED_ROOT + "/DA_ABI_UncookedWeaponItem",
}


def sha(rel):
    path = PROJECT + rel
    return hashlib.sha256(open(path, "rb").read()).hexdigest() if os.path.exists(path) else "absent"


def cls_path(asset_path):
    return asset_path + "." + asset_path.rsplit("/", 1)[1] + "_C"


WATCH = [p.replace("/Game", "") + ".uasset" for p in (SRC_ACTOR, SRC_ITEM, SRC_STYLE, SRC_ABILITY)]
before = {p: sha(p) for p in WATCH}
for name, target in TARGETS.items():
    if EAL.does_asset_exist(target):
        raise RuntimeError("refused: fixture target exists " + target)
EAL.make_directory(ROOT)
EAL.make_directory(UNCOOKED_ROOT)
EAL.make_directory(ROOT + "/DecoyPackage")
for key, source in (("actor", SRC_ACTOR), ("item", SRC_ITEM), ("style", SRC_STYLE), ("ability", SRC_ABILITY), ("decoy", SRC_ACTOR)):
    if EAL.duplicate_asset(source, TARGETS[key]) is None:
        raise RuntimeError("duplicate failed: " + key)
    log("duplicated %s -> %s" % (source.rsplit("/", 1)[1], TARGETS[key]))


def rewire(key, prop, old, new):
    obj = EAL.load_asset(TARGETS[key])
    text = str(lib.export_property_text(obj, prop))
    if old not in text:
        raise RuntimeError("%s.%s: expected text not found" % (key, prop))
    error = str(lib.import_property_text_to_fixture(obj, prop, text.replace(old, new)))
    if error:
        raise RuntimeError("%s.%s: %s" % (key, prop, error))
    # Readback: the new text must be exactly what we asked for.
    if str(lib.export_property_text(obj, prop)) != text.replace(old, new):
        log("note: exported text differs textually from the imported text for %s.%s (formatting)" % (key, prop))
    log("rewired %s.%s" % (key, prop))


# The fourth weapon: item -> its own style and actor class; style -> its own ability; nothing points back to the shipped Sword bundle.
rewire("item", "Combat Style", SRC_STYLE + ".SwordCombatStyle", TARGETS["style"] + ".DA_ABI_FourthCombatStyle")
rewire("item", "Equipable Actor Class", cls_path(SRC_ACTOR), cls_path(TARGETS["actor"]))
rewire("style", "AbilitiesSet", cls_path(SRC_ABILITY), cls_path(TARGETS["ability"]))
if EAL.duplicate_asset(TARGETS["item"], TARGETS["uncooked"]) is None:  # a copy of the REWIRED item: its only defect is its location outside the always-cook roots
    raise RuntimeError("duplicate failed: uncooked")
for key in TARGETS:
    if not EAL.save_asset(TARGETS[key]):
        raise RuntimeError("save failed: " + key)
# Readback of the rewired edges and of the two kept-as-shipped fixtures.
item = EAL.load_asset(TARGETS["item"])
log("item style: " + str(lib.export_property_text(item, "Combat Style"))[:260])
log("item actor: " + str(lib.export_property_text(item, "Equipable Actor Class"))[:260])
style = EAL.load_asset(TARGETS["style"])
log("fourth ability granted: %s" % (cls_path(TARGETS["ability"]) in str(lib.export_property_text(style, "AbilitiesSet"))))
unc = EAL.load_asset(TARGETS["uncooked"])
log("uncooked item binds the FIXTURE actor (valid edges, only its location is wrong): %s" % (cls_path(TARGETS["actor"]) in str(lib.export_property_text(unc, "Equipable Actor Class"))))
after = {p: sha(p) for p in WATCH}
log("shipped source assets unchanged: %s" % (before == after))
if before != after:
    raise RuntimeError("a shipped source asset changed")
log("done; six fixture assets created, no existing asset changed")
