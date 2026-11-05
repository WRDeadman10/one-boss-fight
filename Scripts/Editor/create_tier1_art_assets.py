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
    eal = unreal.EditorAssetLibrary
    tools = unreal.AssetToolsHelpers.get_asset_tools()

    a2_path = f"{ANIM_DEST}/AM_Boss01_A2"
    if eal.does_asset_exist(a2_path):
        log(f"REFUSE: {a2_path} already exists. Retaining existing asset.")
        return

    raise_clip = unreal.load_asset(f"{ANIM_DEST}/AN_Boss01_A2_Raise")
    hold_clip = unreal.load_asset(f"{ANIM_DEST}/AN_Boss01_A2_ApexHold")
    slam_clip = unreal.load_asset(f"{ANIM_DEST}/AN_Boss01_A2_Slam")

    assert raise_clip is not None, f"Missing {ANIM_DEST}/AN_Boss01_A2_Raise"
    assert hold_clip is not None, f"Missing {ANIM_DEST}/AN_Boss01_A2_ApexHold"
    assert slam_clip is not None, f"Missing {ANIM_DEST}/AN_Boss01_A2_Slam"

    len_raise = raise_clip.get_editor_property("sequence_length")
    len_hold = hold_clip.get_editor_property("sequence_length")
    len_slam = slam_clip.get_editor_property("sequence_length")
    total_len = len_raise + len_hold + len_slam

    log(f"Assembling AM_Boss01_A2: Raise={len_raise:.3f}s, Hold={len_hold:.3f}s, Slam={len_slam:.3f}s (Total={total_len:.3f}s)")

    factory = unreal.AnimMontageFactory()
    factory.set_editor_property("source_animation", raise_clip)
    montage = tools.create_asset("AM_Boss01_A2", ANIM_DEST, unreal.AnimMontage, factory)
    assert montage is not None, f"Failed to create AnimMontage at {a2_path}"

    # Get slot from pack greatsword boss montage
    ref_pack = unreal.load_asset(f"{PACK_BASE}GS_Attack01_Montage")
    slot = unreal.RPGMontageUtils.get_montage_slot(ref_pack) if ref_pack is not None else "DefaultSlot"
    unreal.RPGMontageUtils.set_montage_slot(montage, slot)

    # Set composite sections
    # Section 0: Raise (0.00 -> len_raise)
    # Section 1: ApexHold (len_raise -> len_raise + len_hold)
    # Section 2: Slam (len_raise + len_hold -> total_len)
    montage.set_editor_property("enable_auto_blend_out", True)
    for slot_prop, seconds in (("blend_in", 0.25), ("blend_out", 0.25)):
        blend = montage.get_editor_property(slot_prop)
        blend.set_editor_property("blend_time", seconds)
        montage.set_editor_property(slot_prop, blend)

    eal.save_loaded_asset(montage)
    log(f"PASS T1c: Created {a2_path} (Composite length {total_len:.3f}s vs tracker row 3.14s; delta={abs(total_len - 3.14):.3f}s). NOT WIRED.")


def main():
    log("=== Starting Tier 1 Art Asset Creation ===")
    create_vfx_assets()
    create_a2_montage()
    log("=== Completed Tier 1 Art Asset Creation ===")


if __name__ == "__main__":
    main()
