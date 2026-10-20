"""ABP_CombatCharacter_Grey (retargeted copy) still imports the pack's ORIGINAL ABP_UnarmedLayer as its default linked layer, so Greystone ran the mannequin layer
(runtime errors when no combat style layer is linked, for example after death). Consolidate replaces every reference to the original layer by the Greystone
retarget and removes the original (it is only referenced by the mannequin player ABP, which is not used any more)."""
import traceback
import unreal

try:
    base = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/LinkedLayers/"
    grey = "/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/LinkedLayers/"
    target = unreal.load_asset(grey + "ABP_UnarmedLayer_Grey")
    source = unreal.load_asset(base + "ABP_UnarmedLayer")
    ok = unreal.EditorAssetLibrary.consolidate_assets(target, [source])
    print("[Cons] consolidate ->", ok)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    print("[Cons] saved")
except Exception:
    print("[Cons] " + traceback.format_exc())
