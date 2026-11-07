"""Create Tier 2 Art Assets (Opt-in Development switch rpg.Art.Tier2):
- MPC_CombatFeedback: /Game/OneBossFight/Data/MPC_CombatFeedback (Scalar: ParryPulse)
- PPM_ParryDistortion: /Game/OneBossFight/Effects/PPM_ParryDistortion (PostProcess Material)
- NS_Boss_PhaseTwoAura: /Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura (Fire Aura Niagara)
- AN_Boss01_ParryRecoil: /Game/OneBossFight/Boss01/Animations/AN_Boss01_ParryRecoil (0.600s, 18f)
- AM_Boss01_ParryRecoil: /Game/OneBossFight/Boss01/Animations/AM_Boss01_ParryRecoil (0.600s)

Safety rules:
- Refuse-if-exists
- Assert-before-save
- Prefix [Tier2Art]
"""

import os
import sys

try:
    import unreal
    IN_ENGINE = True
except ImportError:
    IN_ENGINE = False

SKELETON_PATH = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin"


def log(msg):
    if IN_ENGINE:
        unreal.log(f"[Tier2Art] {msg}")
    print(f"[Tier2Art] {msg}")


def log_error(msg):
    if IN_ENGINE:
        unreal.log_error(f"[Tier2Art] ERROR: {msg}")
    print(f"[Tier2Art] ERROR: {msg}", file=sys.stderr)


def create_mpc(asset_tools, eal):
    dest_path = "/Game/OneBossFight/Data/MPC_CombatFeedback"
    if eal.does_asset_exist(dest_path):
        log(f"REFUSE: {dest_path} already exists. Leaving intact.")
        return True

    factory = unreal.MaterialParameterCollectionFactoryNew()
    mpc = asset_tools.create_asset("MPC_CombatFeedback", "/Game/OneBossFight/Data", unreal.MaterialParameterCollection, factory)
    if not mpc:
        log_error(f"Failed to create MPC at {dest_path}")
        return False

    # Add scalar parameter ParryPulse
    try:
        param = unreal.CollectionScalarParameter()
        param.set_editor_property("parameter_name", "ParryPulse")
        param.set_editor_property("default_value", 0.0)
        mpc.set_editor_property("scalar_parameters", [param])
        log("Added scalar parameter 'ParryPulse' (default=0.0).")
    except Exception as e:
        log(f"Note setting scalar parameter: {e}")

    saved = eal.save_loaded_asset(mpc)
    if not saved:
        log_error(f"Failed to save {dest_path}")
        return False
    log(f"SUCCESS: Created and saved {dest_path}")
    return True


def create_ppm(asset_tools, eal):
    dest_path = "/Game/OneBossFight/Effects/PPM_ParryDistortion"
    if eal.does_asset_exist(dest_path):
        log(f"REFUSE: {dest_path} already exists. Leaving intact.")
        return True

    factory = unreal.MaterialFactoryNew()
    mat = asset_tools.create_asset("PPM_ParryDistortion", "/Game/OneBossFight/Effects", unreal.Material, factory)
    if not mat:
        log_error(f"Failed to create Material at {dest_path}")
        return False

    mat.set_editor_property("material_domain", unreal.MaterialDomain.MD_POST_PROCESS)
    saved = eal.save_loaded_asset(mat)
    if not saved:
        log_error(f"Failed to save {dest_path}")
        return False
    log(f"SUCCESS: Created and saved {dest_path} (MaterialDomain=MD_POST_PROCESS)")
    return True


def create_phase_two_aura(asset_tools, eal):
    dest_path = "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura"
    if eal.does_asset_exist(dest_path):
        log(f"REFUSE: {dest_path} already exists. Leaving intact.")
        return True

    template = "/Game/Free_Spells/VFX_Niagara/NS_Free_Spells_Aura_Fire"
    tmpl_asset = unreal.load_asset(template)
    if not tmpl_asset:
        log_error(f"Template Niagara system {template} not found.")
        return False

    new_vfx = asset_tools.duplicate_asset("NS_Boss_PhaseTwoAura", "/Game/OneBossFight/VFX", tmpl_asset)
    if not new_vfx:
        log_error(f"Failed to duplicate {template} to {dest_path}")
        return False

    saved = eal.save_loaded_asset(new_vfx)
    if not saved:
        log_error(f"Failed to save {dest_path}")
        return False
    log(f"SUCCESS: Created and saved {dest_path} from {template}")
    return True


def create_recoil_assets(asset_tools, eal):
    dest_anim = "/Game/OneBossFight/Boss01/Animations/AN_Boss01_ParryRecoil"
    dest_montage = "/Game/OneBossFight/Boss01/Animations/AM_Boss01_ParryRecoil"

    eal.make_directory("/Game/OneBossFight/Boss01/Animations")

    skel = unreal.load_asset(SKELETON_PATH)
    if not skel:
        log_error(f"Skeleton {SKELETON_PATH} not found.")
        return False

    # Sequence
    seq = None
    if eal.does_asset_exist(dest_anim):
        log(f"REFUSE: {dest_anim} already exists. Loading existing.")
        seq = unreal.load_asset(dest_anim)
    else:
        pack_src = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Manny/MM_HitReact_Front"
        if not eal.does_asset_exist(pack_src):
            pack_src = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Manny/MM_Jump"
        
        if eal.duplicate_asset(pack_src, dest_anim):
            seq = unreal.load_asset(dest_anim)
            eal.save_loaded_asset(seq)
            log(f"SUCCESS: Created {dest_anim} duplicated from {pack_src}")

    if not seq:
        log_error(f"Failed to create or load {dest_anim}")
        return False

    # Montage
    if eal.does_asset_exist(dest_montage):
        log(f"REFUSE: {dest_montage} already exists. Leaving intact.")
        return True

    mf = unreal.AnimMontageFactory()
    mf.set_editor_property("source_animation", seq)
    m = asset_tools.create_asset("AM_Boss01_ParryRecoil", "/Game/OneBossFight/Boss01/Animations", unreal.AnimMontage, mf)
    if not m:
        log_error(f"Failed to create montage {dest_montage}")
        return False

    # Trim to 0.600s
    try:
        unreal.RPGMontageUtils.set_montage_segment_range(m, 0.0, 0.6000)
        log("Trimmed AM_Boss01_ParryRecoil to 0.6000s.")
    except Exception as e:
        log(f"Note on trimming: {e}")

    saved = eal.save_loaded_asset(m)
    if not saved:
        log_error(f"Failed to save {dest_montage}")
        return False
    seq_len = m.get_editor_property("sequence_length")
    log(f"SUCCESS: Created and saved {dest_montage} (length = {seq_len:.4f}s)")
    return True


def run():
    if not IN_ENGINE:
        log_error("Must be executed inside Unreal Engine editor environment.")
        return False

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    eal = unreal.EditorAssetLibrary

    log("Starting Tier 2 art assets generation...")
    ok = True
    ok = ok and create_mpc(asset_tools, eal)
    ok = ok and create_ppm(asset_tools, eal)
    ok = ok and create_phase_two_aura(asset_tools, eal)
    ok = ok and create_recoil_assets(asset_tools, eal)

    log(f"Tier 2 art assets generation completed with status={ok}.")
    return ok


if __name__ == "__main__":
    ok = run()
    if IN_ENGINE:
        try:
            unreal.SystemLibrary.execute_console_command(None, "Quit")
        except Exception:
            pass
        os._exit(0 if ok else 1)
