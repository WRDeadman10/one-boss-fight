"""Saves the M-08 gate frame work (log prefix [GateFrame]): the mesh, the rune material and the level. Nothing else."""
import unreal

log = lambda m: unreal.log("[GateFrame] " + m)
for p in ("/Game/OneBossFight/Environment/Gate/SM_Boss01_FogGateFrame", "/Game/OneBossFight/Environment/Materials/M_Gate_Rune"):
    log("save %s: %s" % (p, unreal.EditorAssetLibrary.save_asset(p, only_if_is_dirty=False)))
log("save level: %s" % unreal.EditorLoadingAndSavingUtils.save_current_level())
log("DONE")
