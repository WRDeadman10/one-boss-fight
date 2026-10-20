"""
Copies the pack mannequin's sockets (weapon hand and sheath sockets, consumables, ...) to the Greystone skeleton under the same
names, so the pack's weapons attach to Greystone. Needs URPGSkeletonUtils (Python cannot set a socket name). Run in the editor.
"""
import unreal

log = lambda m: unreal.log("[GreySock] " + m)
src = unreal.load_asset("/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin")
dst = unreal.load_asset("/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone")
before = dst.num_sockets()
copied = unreal.RPGSkeletonUtils.copy_sockets(src, dst, False)
unreal.EditorAssetLibrary.save_loaded_asset(dst, False)
skeleton = dst.get_editor_property("skeleton")
if skeleton:
    unreal.EditorAssetLibrary.save_loaded_asset(skeleton, False)
log("copied %d sockets (%d before, %d after)" % (copied, before, dst.num_sockets()))
