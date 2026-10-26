"""Scratch route (a) authoring (owner approval G-3, 2026-10-26). Creates NEW assets only under /Game/OneBossFight/Scratch/RouteA:
BT_ScratchRouteA (C++ minimal tree) and DA_ScratchRouteAInfo (a duplicate of the pack boss info, BehaviorTree swapped).
Never edits, renames or deletes an existing asset; refuses to run if a target exists. Log prefix [ScratchAuthor]."""
import hashlib
import os
import unreal

ROOT = "/Game/OneBossFight/Scratch/RouteA"
PACK_INFO = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/ExampleGreatSwordBoss"
BB = "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BB_Base.BB_Base"
PROJECT = "C:/UnrealProject/OneBossFight/Content"
log = lambda msg: unreal.log("[ScratchAuthor] " + msg)


def sha(rel):
    path = PROJECT + rel
    return hashlib.sha256(open(path, "rb").read()).hexdigest() if os.path.exists(path) else "absent"


WATCH = ["/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/ExampleGreatSwordBoss.uasset",
         "/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/BT_ExampleBoss.uasset",
         "/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BB_Base.uasset"]
before = {p: sha(p) for p in WATCH}
if unreal.EditorAssetLibrary.does_asset_exist(ROOT + "/DA_ScratchRouteAInfo"):
    raise RuntimeError("refused: scratch info already exists")
unreal.EditorAssetLibrary.make_directory(ROOT)
if unreal.EditorAssetLibrary.does_asset_exist(ROOT + "/BT_ScratchRouteA"):
    log("reusing the scratch tree created by an earlier run of this script (never overwritten)")
else:
    res = unreal.RPGScratchRouteALibrary.create_scratch_behavior_tree(ROOT + "/BT_ScratchRouteA", BB)
    log("create tree raw result: %r" % (res,))
    ok, err = (res[0], res[1]) if isinstance(res, (tuple, list)) and len(res) >= 2 else (bool(res), "")
    if not ok:
        raise RuntimeError("tree creation failed: " + str(err))
dup = unreal.EditorAssetLibrary.duplicate_asset(PACK_INFO, ROOT + "/DA_ScratchRouteAInfo")
if dup is None:
    raise RuntimeError("info duplicate failed")
tree = unreal.EditorAssetLibrary.load_asset(ROOT + "/BT_ScratchRouteA")
log("duplicate class: %s" % dup.get_class().get_name())
prop = None
for candidate in ("BehaviorTree", "behavior_tree", "Behavior Tree", "behaviorTree"):
    try:
        current = dup.get_editor_property(candidate)
        prop = candidate
        log("property readable as %r, current value %s" % (candidate, current.get_name() if current else None))
        break
    except Exception as error:
        log("property name %r failed: %s" % (candidate, str(error)[:120]))
if prop is None:
    raise RuntimeError("no behavior tree property found on the info duplicate")
dup.set_editor_property(prop, tree)  # NEW scratch asset, never a pack asset or a component in PIE
log("set %s on the scratch info" % prop)
if not unreal.EditorAssetLibrary.save_loaded_asset(dup):
    raise RuntimeError("info save failed")
after = {p: sha(p) for p in WATCH}
log("pack assets unchanged: %s" % (before == after))
log("done; scratch assets created, no existing asset changed")
