"""Saves the Shiva shrine mesh and the level (log prefix [ShrineSave])."""
import unreal

log = lambda m: unreal.log("[ShrineSave] " + m)
log("mesh: %s" % unreal.EditorAssetLibrary.save_asset("/Game/OneBossFight/Environment/Shrine/SM_Boss01_ShivaShrine", only_if_is_dirty=False))
log("level: %s" % unreal.EditorLoadingAndSavingUtils.save_current_level())
