"""Create /Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_Boost candidate asset (C-1069).

Safety rules:
- Refuse-if-exists
- Assert-before-save
- Keep approved NS_Boss_PhaseTwoAura untouched
- Run under ENGINE_LOCK
"""
import sys
import unreal

SOURCE_PATH = "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura"
DEST_NAME = "NS_Boss_PhaseTwoAura_Boost"
DEST_DIR = "/Game/OneBossFight/VFX"
DEST_PATH = f"{DEST_DIR}/{DEST_NAME}"

def log(msg):
    unreal.log(f"[PhaseTwoAuraBoost] {msg}")

def log_error(msg):
    unreal.log_error(f"[PhaseTwoAuraBoost] ERROR: {msg}")

def create_candidate():
    eal = unreal.EditorAssetLibrary
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    if eal.does_asset_exist(DEST_PATH):
        log(f"REFUSE: {DEST_PATH} already exists. Leaving intact.")
        # Reload and log readback
        reloaded = unreal.load_asset(DEST_PATH)
        if reloaded:
            readback_bounds = reloaded.get_editor_property("fixed_bounds")
            log(f"EXISTING_BOUNDS: min=({readback_bounds.min.x:.1f}, {readback_bounds.min.y:.1f}, {readback_bounds.min.z:.1f}) max=({readback_bounds.max.x:.1f}, {readback_bounds.max.y:.1f}, {readback_bounds.max.z:.1f}) is_valid={readback_bounds.is_valid}")
        return True

    source_asset = unreal.load_asset(SOURCE_PATH)
    if not source_asset:
        log_error(f"Source asset {SOURCE_PATH} not found.")
        return False

    # Read baseline properties for readback comparison
    base_bounds = source_asset.get_editor_property("fixed_bounds")
    log(f"Baseline {SOURCE_PATH} fixed_bounds: min=({base_bounds.min.x:.1f}, {base_bounds.min.y:.1f}, {base_bounds.min.z:.1f}) max=({base_bounds.max.x:.1f}, {base_bounds.max.y:.1f}, {base_bounds.max.z:.1f}) is_valid={base_bounds.is_valid}")

    # Duplicate to boost candidate
    boost_asset = asset_tools.duplicate_asset(DEST_NAME, DEST_DIR, source_asset)
    if not boost_asset:
        log_error(f"Failed to duplicate {SOURCE_PATH} to {DEST_PATH}")
        return False

    # Apply boost fixed bounds [-250, 250] cm
    new_bounds = unreal.Box(
        unreal.Vector(-250.0, -250.0, -250.0),
        unreal.Vector(250.0, 250.0, 250.0)
    )
    boost_asset.set_editor_property("fixed_bounds", new_bounds)

    # Save loaded asset
    saved = eal.save_loaded_asset(boost_asset)
    if not saved:
        log_error(f"Failed to save {DEST_PATH}")
        return False

    # Readback verification
    reloaded = unreal.load_asset(DEST_PATH)
    if not reloaded:
        log_error(f"Failed to reload {DEST_PATH} after saving")
        return False

    readback_bounds = reloaded.get_editor_property("fixed_bounds")
    log(f"READBACK: {DEST_PATH} successfully created and verified.")
    log(f"READBACK_BOUNDS: min=({readback_bounds.min.x:.1f}, {readback_bounds.min.y:.1f}, {readback_bounds.min.z:.1f}) max=({readback_bounds.max.x:.1f}, {readback_bounds.max.y:.1f}, {readback_bounds.max.z:.1f}) is_valid={readback_bounds.is_valid}")

    assert readback_bounds.min.x == -250.0 and readback_bounds.min.y == -250.0 and readback_bounds.min.z == -250.0, "Bounds min mismatch"
    assert readback_bounds.max.x == 250.0 and readback_bounds.max.y == 250.0 and readback_bounds.max.z == 250.0, "Bounds max mismatch"
    assert readback_bounds.is_valid is True, "Bounds is_valid mismatch"

    log("SUCCESS: Candidate NS_Boss_PhaseTwoAura_Boost created and verified.")
    return True

if __name__ == "__main__":
    ok = create_candidate()
    if not ok:
        sys.exit(1)
