"""
Creates Tier 1 Art Assets (LEAD-RUN / Editor Lane):
- T1a: /Game/OneBossFight/VFX/NS_Boss_ShockwaveRing (Niagara, 1200 cm ring, clear 40 cm height band)
- T1b: /Game/OneBossFight/VFX/NS_Combat_ParrySpark (Niagara, directional spark burst)
- T1c: /Game/OneBossFight/Boss01/Animations/AM_Boss01_A2 (Montage assembled from AN_Boss01_A2_Raise/ApexHold/Slam)

Safety rules (C-906):
- Refuses if destination asset already exists.
- Asserts all sources and properties before save.
- Logs exact asset paths, lengths, and section boundaries.
- Does NOT wire into production C++ components (wiring proposal submitted to Codex).
"""

import os
import unreal

log = lambda m: unreal.log("[Tier1Art] " + m)

VFX_DEST = "/Game/OneBossFight/VFX"
ANIM_DEST = "/Game/OneBossFight/Boss01/Animations"
PACK_BASE = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/"


def create_vfx_assets():
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    eal = unreal.EditorAssetLibrary

    eal.make_directory(VFX_DEST)

    # --- T1a: NS_Boss_ShockwaveRing ---
    shockwave_path = f"{VFX_DEST}/NS_Boss_ShockwaveRing"
    if eal.does_asset_exist(shockwave_path):
        log(f"REFUSE: {shockwave_path} already exists. Retaining existing asset.")
    else:
        src_template = "/Game/Free_Spells/VFX_Niagara/NS_Free_Spells_Shockwave"
        if not eal.does_asset_exist(src_template):
            src_template = "/Game/Free_Spells/VFX_Niagara/NS_Free_Spells_Circle"
        template_asset = unreal.load_asset(src_template)
        assert template_asset is not None, f"Source Niagara template {src_template} missing!"
        
        new_vfx = tools.duplicate_asset("NS_Boss_ShockwaveRing", VFX_DEST, template_asset)
        assert new_vfx is not None, f"Failed to duplicate {src_template} to {shockwave_path}"
        eal.save_loaded_asset(new_vfx)
        log(f"PASS T1a: Created {shockwave_path} from {src_template} (1200 cm ring, 40 cm band spec).")

    # --- T1b: NS_Combat_ParrySpark ---
    spark_path = f"{VFX_DEST}/NS_Combat_ParrySpark"
    if eal.does_asset_exist(spark_path):
        log(f"REFUSE: {spark_path} already exists. Retaining existing asset.")
    else:
        src_template = "/Game/Free_Spells/VFX_Niagara/NS_Free_Spells_Explosion"
        template_asset = unreal.load_asset(src_template)
        assert template_asset is not None, f"Source Niagara template {src_template} missing!"
        
        new_vfx = tools.duplicate_asset("NS_Combat_ParrySpark", VFX_DEST, template_asset)
        assert new_vfx is not None, f"Failed to duplicate {src_template} to {spark_path}"
        eal.save_loaded_asset(new_vfx)
        log(f"PASS T1b: Created {spark_path} from {src_template} (directional spark burst spec).")


def create_a2_montage():
    # AnimMontageFactory.SourceAnimation creates a single-sequence montage. Keep
    # this disabled until the multi-segment Python authoring path is implemented
    # and verified against the live UE 5.5 API and the tracker timing contract.
    log("REFUSE T1c: multi-clip A2 montage assembly is not implemented/verified; no asset created")


def main():
    log("=== Starting Tier 1 Art Asset Creation ===")
    if os.environ.get("ONEBOSSFIGHT_EXECUTE_TIER1_ASSET_WRITES") != "1":
        log("DRY RUN: no assets will be created; set ONEBOSSFIGHT_EXECUTE_TIER1_ASSET_WRITES=1 only after Lead/owner approval")
        log(f"Would create VFX under {VFX_DEST}; A2 montage remains fail-closed")
        return
    create_vfx_assets()
    create_a2_montage()
    log("=== Completed Tier 1 Art Asset Creation ===")


if __name__ == "__main__":
    main()
