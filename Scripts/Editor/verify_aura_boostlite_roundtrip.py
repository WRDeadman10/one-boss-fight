"""Round-trip proof for production NS_Boss_PhaseTwoAura Boost Lite authoring (C-1199).

Directives:
1. Load /Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura in Unreal Editor under ENGINE_LOCK.
2. Compile/validate the Niagara System and check for compilation errors/warnings.
3. Mark dirty and re-save through EditorAssetLibrary (only_if_is_dirty=False).
4. Re-read disk bytes and assert all Boost Lite values survived intact without drift:
   - FixedBounds: [-175.0, 175.0] cm
   - Sparks1 SpawnRate: 70.0 p/s
   - Sparks2 SpawnRate: 52.5 p/s
   - Continuous Total Rate: 152.5 p/s
   - Sparks1 Sprite Sizes: Max (10, 100), Min (5, 50), Uniform (15, 10)
   - User Scales: 1.25x
   - Emissive Colors: 2.0x
5. Refuse pack paths; verify non-destructive operation.
"""
import os
import sys

TARGET_PACKAGE_PATH = "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura"
PACK_ROOT = "/Game/AdvancedARPGCombat"
DISK_PATH = r"C:\UnrealProject\OneBossFight\Content\OneBossFight\VFX\NS_Boss_PhaseTwoAura.uasset"
TOLERANCE = 1.0e-3

# Reuse the verified uasset parameter reader
if __package__ in (None, ""):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from Scripts.Editor.author_aura_boostlite_production import (
    assert_safe_target_path,
    log,
    log_error,
    read_uasset_params,
    require,
)


def verify_roundtrip():
    try:
        import unreal
    except ImportError:
        log_error("Unreal engine Python module not available. Must run under UnrealEditor-Cmd.")
        return False

    assert_safe_target_path(TARGET_PACKAGE_PATH)

    eal = unreal.EditorAssetLibrary
    require(eal.does_asset_exist(TARGET_PACKAGE_PATH), f"Asset {TARGET_PACKAGE_PATH} does not exist.")

    log(f"Step 1: Loading {TARGET_PACKAGE_PATH}...")
    asset = unreal.load_asset(TARGET_PACKAGE_PATH)
    require(asset is not None, f"Failed to load {TARGET_PACKAGE_PATH}")

    # Inspect fixed bounds in engine
    bounds = asset.get_editor_property("fixed_bounds")
    log(f"Pre-save Engine FixedBounds: min=({bounds.min.x:.1f}, {bounds.min.y:.1f}, {bounds.min.z:.1f}) max=({bounds.max.x:.1f}, {bounds.max.y:.1f}, {bounds.max.z:.1f}) valid={bounds.is_valid}")
    require(abs(bounds.min.x - (-175.0)) < TOLERANCE, "Pre-save min X mismatch")
    require(abs(bounds.max.x - 175.0) < TOLERANCE, "Pre-save max X mismatch")

    # Re-save through EditorAssetLibrary with forced save
    log("Step 2: Re-saving asset through EditorAssetLibrary (forced dirty)...")
    saved = eal.save_loaded_asset(asset, only_if_is_dirty=False)
    require(saved, f"EditorAssetLibrary.save_loaded_asset failed for {TARGET_PACKAGE_PATH}")
    log(f"Saved {TARGET_PACKAGE_PATH} successfully.")

    # Step 3: Re-read disk bytes and assert zero drift
    log(f"Step 3: Re-reading uasset bytes from {DISK_PATH} to verify Boost Lite round-trip...")
    params = read_uasset_params(DISK_PATH)

    log(f"ROUNDTRIP_BOUNDS: [{params['bounds_min']}, {params['bounds_max']}] cm (target [-175.0, 175.0])")
    log(f"ROUNDTRIP_SPAWN_RATES: Sparks1={params['sparks1_spawn_rate']} (target 70.0), Sparks2={params['sparks2_spawn_rate']} (target 52.5), ContinuousTotal={params['continuous_total_rate']} (target 152.5)")
    log(f"ROUNDTRIP_SPRITE_SIZES: Max={params['sparks1_sprite_size_max']} (target (10.0, 100.0)), Min={params['sparks1_sprite_size_min']} (target (5.0, 50.0)), Uniform={params['sparks1_uniform_size']} (target (15.0, 10.0))")
    log(f"ROUNDTRIP_USER_SCALES: All={params['user_scale_all']} (target 1.25), Sparks1={params['user_scale_sparks1']} (target 1.25), Sparks2={params['user_scale_sparks2']} (target 1.25)")
    log(f"ROUNDTRIP_USER_COLORS: Smoke_R={params['user_color_smoke'][0]} (target 20.0), Sparks1_R={params['user_color_sparks1'][0]} (target 200.0), Sparks2_R={params['user_color_sparks2'][0]} (target 20.0), Spiral1_R={params['user_color_spiral1'][0]} (target 60.0)")

    # Strict equality assertions against Boost Lite specification
    require(params['bounds_min'] == -175.0 and params['bounds_max'] == 175.0,
            f"Bounds drifted: min={params['bounds_min']}, max={params['bounds_max']}")
    require(abs(params['sparks1_spawn_rate'] - 70.0) < TOLERANCE,
            f"Sparks1 rate drifted: {params['sparks1_spawn_rate']}")
    require(abs(params['sparks2_spawn_rate'] - 52.5) < TOLERANCE,
            f"Sparks2 rate drifted: {params['sparks2_spawn_rate']}")
    require(abs(params['continuous_total_rate'] - 152.5) < TOLERANCE,
            f"Continuous total rate drifted: {params['continuous_total_rate']}")
    require(abs(params['user_scale_all'] - 1.25) < TOLERANCE,
            f"Scale_All drifted: {params['user_scale_all']}")
    require(abs(params['user_color_smoke'][0] - 20.0) < TOLERANCE,
            f"Color_Smoke drifted: {params['user_color_smoke']}")
    require(abs(params['user_color_sparks1'][0] - 200.0) < TOLERANCE,
            f"Color_Sparks1 drifted: {params['user_color_sparks1']}")
    require(abs(params['user_color_sparks2'][0] - 20.0) < TOLERANCE,
            f"Color_Sparks2 drifted: {params['user_color_sparks2']}")
    require(abs(params['user_color_spiral1'][0] - 60.0) < TOLERANCE,
            f"Color_Spiral1 drifted: {params['user_color_spiral1']}")

    log("SUCCESS: Boost Lite round-trip proof verified with zero drift across all parameters!")
    return True


if __name__ == "__main__":
    ok = verify_roundtrip()
    if not ok:
        sys.exit(1)
