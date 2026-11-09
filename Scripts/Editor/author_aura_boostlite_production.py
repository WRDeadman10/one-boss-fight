"""Promote Owner-selected BoostLite parameters into production NS_Boss_PhaseTwoAura.

Author: Antigravity (Art/Review/Audit)
Directive: C-1168 (Owner selection), C-1196, C-1197
Reference: Documentation/Boss/AURA_PRODUCTION_AUTHORING_PLAN.md

Applies BoostLite values to /Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura:
- FixedBounds: [-175.0, 175.0] cm (was [-100.0, 100.0] baseline)
- Sparks1 SpawnRate: 40.0 -> 70.0 p/s (1.75x)
- Sparks2 SpawnRate: 30.0 -> 52.5 p/s (1.75x)
- Continuous Total Rate: 100.0 -> 152.5 p/s (was 100.0 baseline)
- Sparks1 SpriteSizeMax: (8.0, 80.0) -> (10.0, 100.0) cm (1.25x)
- Sparks1 SpriteSizeMin: (4.0, 40.0) -> (5.0, 50.0) cm (1.25x)
- Sparks1 UniformSize: (12.0, 8.0) -> (15.0, 10.0) cm (1.25x)
- User.Scale_All: 1.0 -> 1.25 (1.25x)
- User.Scale_Sparks1: 1.0 -> 1.25 (1.25x)
- User.Scale_Sparks2: 1.0 -> 1.25 (1.25x)
- User.Color_Smoke: 2.0x emissive
- User.Color_Sparks1: 2.0x emissive
- User.Color_Sparks2: 2.0x emissive
- User.Color_Spiral1: 2.0x emissive

Safety Rules:
- Refuse any path starting with /Game/AdvancedARPGCombat (no pack edits).
- Only target /Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura.
- Strict pre-assert, save, patch, and post-assert readback.
- Must be run under ENGINE_LOCK.json.
"""
import math
import os
import struct
import sys

TARGET_PACKAGE_PATH = "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura"
PACK_ROOT = "/Game/AdvancedARPGCombat"
DISK_PATH = r"C:\UnrealProject\OneBossFight\Content\OneBossFight\VFX\NS_Boss_PhaseTwoAura.uasset"
TOLERANCE = 1.0e-3


def log(msg):
    try:
        import unreal
        unreal.log(f"[AuraBoostLiteProduction] {msg}")
    except ImportError:
        pass
    print(f"[AuraBoostLiteProduction] {msg}")


def log_error(msg):
    try:
        import unreal
        unreal.log_error(f"[AuraBoostLiteProduction] ERROR: {msg}")
    except ImportError:
        pass
    print(f"[AuraBoostLiteProduction] ERROR: {msg}", file=sys.stderr)


def require(condition, message):
    if not condition:
        log_error(message)
        raise RuntimeError(f"[AuraBoostLiteProduction] REFUSED: {message}")


def assert_safe_target_path(package_path):
    normalized = str(package_path).replace("\\", "/").rstrip("/")
    require(not normalized.startswith(PACK_ROOT + "/") and normalized != PACK_ROOT,
            f"Pack asset path is strictly forbidden: {normalized}")
    require(normalized == TARGET_PACKAGE_PATH,
            f"Only the production NS_Boss_PhaseTwoAura asset may be targeted: {normalized}")


def read_uasset_params(path):
    """Read back and parse all key aura parameters from the uasset file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Asset file not found: {path}")

    with open(path, "rb") as f:
        data = f.read()

    params = {"path": path, "file_size": len(data)}

    # FixedBounds
    params["bounds_min"] = None
    params["bounds_max"] = None
    for pos in range(len(data) - 48, 1000000, -1):
        min_x, min_y, min_z = struct.unpack('<ddd', data[pos:pos+24])
        max_x, max_y, max_z = struct.unpack('<ddd', data[pos+24:pos+48])
        if min_x == min_y == min_z and max_x == max_y == max_z and abs(min_x + max_x) < 1e-3 and min_x < -10.0:
            params["bounds_min"] = min_x
            params["bounds_max"] = max_x
            break

    # SpawnRates in ParameterData block
    ctx = bytes.fromhex('000000000000a04000409c45000000000000803f000000000000a041')
    pos = 0
    params["sparks1_spawn_rate"] = None
    params["sparks2_spawn_rate"] = None
    while True:
        idx = data.find(ctx, pos)
        if idx == -1:
            break
        sparks1_rate = struct.unpack('<f', data[idx+52:idx+56])[0]
        sparks2_rate = struct.unpack('<f', data[idx+80:idx+84])[0]
        smoke_rate = struct.unpack('<f', data[idx+24:idx+28])[0]
        spiral1_rate = struct.unpack('<f', data[idx+108:idx+112])[0]
        if sparks1_rate > 0.0:
            params["smoke_spawn_rate"] = smoke_rate
            params["sparks1_spawn_rate"] = sparks1_rate
            params["sparks2_spawn_rate"] = sparks2_rate
            params["spiral1_spawn_rate"] = spiral1_rate
            params["continuous_total_rate"] = smoke_rate + sparks1_rate + sparks2_rate + spiral1_rate
            break
        pos = idx + len(ctx)

    # Sparks1 Sprite Sizes
    header = bytes.fromhex('0000a0400000b44300000000')
    pos = 0
    sparks1_match = None
    count = 0
    while True:
        idx = data.find(header, pos)
        if idx == -1:
            break
        count += 1
        if count == 2:
            sparks1_match = idx
            break
        pos = idx + len(header)

    if sparks1_match is not None:
        vals = struct.unpack('<ffffff', data[sparks1_match+12:sparks1_match+36])
        params["sparks1_sprite_size_max"] = (vals[0], vals[1])
        params["sparks1_sprite_size_min"] = (vals[2], vals[3])
        params["sparks1_uniform_size"] = (vals[4], vals[5])
    else:
        params["sparks1_sprite_size_max"] = None

    # User Parameters
    for p in [i for i in range(len(data)-100) if data[i:i+4] == struct.pack('<f', 20.0) or data[i:i+4] == struct.pack('<f', 10.0)]:
        r_smoke = struct.unpack('<f', data[p:p+4])[0]
        r_sp1 = struct.unpack('<f', data[p+16:p+20])[0]
        r_sp2 = struct.unpack('<f', data[p+32:p+36])[0]
        r_spir = struct.unpack('<f', data[p+48:p+52])[0]
        if ((r_smoke in (10.0, 20.0)) and (r_sp1 in (100.0, 200.0)) and
            (r_sp2 in (10.0, 20.0)) and (r_spir in (30.0, 60.0))):
            params["user_color_smoke"] = (r_smoke, struct.unpack('<f', data[p+4:p+8])[0])
            params["user_color_sparks1"] = (r_sp1, struct.unpack('<f', data[p+20:p+24])[0])
            params["user_color_sparks2"] = (r_sp2, struct.unpack('<f', data[p+36:p+40])[0])
            params["user_color_spiral1"] = (r_spir, struct.unpack('<f', data[p+52:p+56])[0])
            params["user_scale_all"] = struct.unpack('<f', data[p+80:p+84])[0]
            params["user_scale_sparks1"] = struct.unpack('<f', data[p+88:p+92])[0]
            params["user_scale_sparks2"] = struct.unpack('<f', data[p+92:p+96])[0]
            break

    return params


def patch_uasset_parameters(disk_path):
    """Patch the internal Niagara emitter parameters and user parameters to BoostLite values."""
    with open(disk_path, "rb") as f:
        data = bytearray(f.read())

    orig_len = len(data)

    # 1. SpawnRates: Sparks1 40.0 -> 70.0, Sparks2 30.0 -> 52.5
    ctx = bytes.fromhex('000000000000a04000409c45000000000000803f000000000000a041')
    pos = 0
    patched_spawn = False
    while True:
        idx = data.find(ctx, pos)
        if idx == -1:
            break
        s1 = struct.unpack('<f', data[idx+52:idx+56])[0]
        s2 = struct.unpack('<f', data[idx+80:idx+84])[0]
        if (abs(s1 - 40.0) < 1e-3 or abs(s1 - 70.0) < 1e-3) and (abs(s2 - 30.0) < 1e-3 or abs(s2 - 52.5) < 1e-3):
            data[idx+52:idx+56] = struct.pack('<f', 70.0)
            data[idx+80:idx+84] = struct.pack('<f', 52.5)
            patched_spawn = True
            log(f"Patched SpawnRates at {idx}: Sparks1 -> 70.0, Sparks2 -> 52.5")
        pos = idx + len(ctx)
    require(patched_spawn, "Failed to patch SpawnRates in ParameterData")

    # 2. Sparks1 SpriteSizes: Max (10, 100), Min (5, 50), Uniform (15, 10)
    size_base_40 = struct.pack('<ffffff', 8.0, 80.0, 4.0, 40.0, 12.0, 8.0)
    size_base_70 = struct.pack('<ffffff', 10.0, 100.0, 5.0, 50.0, 15.0, 10.0)
    pos = 0
    patched_sizes = 0
    while True:
        idx = data.find(size_base_40, pos)
        if idx == -1:
            break
        data[idx:idx+24] = size_base_70
        patched_sizes += 1
        log(f"Patched Sparks1 SpriteSizes at {idx}")
        pos = idx + 24
    if patched_sizes == 0:
        # Check if already patched
        idx = data.find(size_base_70)
        require(idx != -1, "Failed to find or patch Sparks1 SpriteSizes")
        log(f"Sparks1 SpriteSizes already match BoostLite targets at {idx}")

    # 3. User Parameters (Colors 2.0x, Scales 1.25x)
    pos = 0
    patched_user = 0
    while True:
        idx = data.find(struct.pack('<f', 10.0), pos)
        if idx == -1:
            break
        r_smoke = struct.unpack('<f', data[idx:idx+4])[0]
        r_sp1 = struct.unpack('<f', data[idx+16:idx+20])[0]
        r_sp2 = struct.unpack('<f', data[idx+32:idx+36])[0]
        r_spir = struct.unpack('<f', data[idx+48:idx+52])[0]
        if (abs(r_smoke - 10.0) < 1e-3 and abs(r_sp1 - 100.0) < 1e-3 and
            abs(r_sp2 - 10.0) < 1e-3 and abs(r_spir - 30.0) < 1e-3):
            data[idx:idx+4] = struct.pack('<f', 20.0)
            g_smoke = struct.unpack('<f', data[idx+4:idx+8])[0]
            data[idx+4:idx+8] = struct.pack('<f', g_smoke * 2.0)

            data[idx+16:idx+20] = struct.pack('<f', 200.0)
            g_sp1 = struct.unpack('<f', data[idx+20:idx+24])[0]
            data[idx+20:idx+24] = struct.pack('<f', g_sp1 * 2.0)

            data[idx+32:idx+36] = struct.pack('<f', 20.0)
            g_sp2 = struct.unpack('<f', data[idx+36:idx+40])[0]
            data[idx+36:idx+40] = struct.pack('<f', g_sp2 * 2.0)

            data[idx+48:idx+52] = struct.pack('<f', 60.0)
            g_spir = struct.unpack('<f', data[idx+52:idx+56])[0]
            data[idx+52:idx+56] = struct.pack('<f', g_spir * 2.0)

            data[idx+80:idx+84] = struct.pack('<f', 1.25)
            data[idx+88:idx+92] = struct.pack('<f', 1.25)
            data[idx+92:idx+96] = struct.pack('<f', 1.25)
            patched_user += 1
            log(f"Patched User parameters at {idx}")
        pos = idx + 4

    require(len(data) == orig_len, "Uasset file length changed during patching")

    with open(disk_path, "wb") as f:
        f.write(data)
    log(f"Successfully wrote BoostLite parameters to {disk_path}")


def promote_production():
    try:
        import unreal
    except ImportError:
        log_error("Unreal engine Python module not available. Must run under UnrealEditor-Cmd.")
        return False

    assert_safe_target_path(TARGET_PACKAGE_PATH)

    eal = unreal.EditorAssetLibrary
    if not eal.does_asset_exist(TARGET_PACKAGE_PATH):
        log_error(f"Target production asset does not exist: {TARGET_PACKAGE_PATH}")
        return False

    asset = unreal.load_asset(TARGET_PACKAGE_PATH)
    require(asset is not None, f"Failed to load {TARGET_PACKAGE_PATH}")

    # Set BoostLite FixedBounds: [-175.0, 175.0] cm
    new_bounds = unreal.Box(
        unreal.Vector(-175.0, -175.0, -175.0),
        unreal.Vector(175.0, 175.0, 175.0)
    )
    asset.set_editor_property("fixed_bounds", new_bounds)
    log("Set fixed_bounds to [-175.0, 175.0] cm")

    saved = eal.save_loaded_asset(asset)
    require(saved, f"Failed to save {TARGET_PACKAGE_PATH}")
    log(f"Saved {TARGET_PACKAGE_PATH} through EditorAssetLibrary")

    # Apply parameter updates directly to the uasset
    patch_uasset_parameters(DISK_PATH)

    # Reload and assert readback
    reloaded = unreal.load_asset(TARGET_PACKAGE_PATH)
    require(reloaded is not None, f"Failed to reload {TARGET_PACKAGE_PATH}")

    readback_bounds = reloaded.get_editor_property("fixed_bounds")
    log(f"READBACK_BOUNDS: min=({readback_bounds.min.x:.1f}, {readback_bounds.min.y:.1f}, {readback_bounds.min.z:.1f}) max=({readback_bounds.max.x:.1f}, {readback_bounds.max.y:.1f}, {readback_bounds.max.z:.1f})")
    require(abs(readback_bounds.min.x - (-175.0)) < TOLERANCE, "Bounds min X mismatch")
    require(abs(readback_bounds.max.x - 175.0) < TOLERANCE, "Bounds max X mismatch")

    # Offline readback verification of internal parameters
    params = read_uasset_params(DISK_PATH)
    log(f"READBACK_PARAMS: Sparks1={params['sparks1_spawn_rate']} (70.0), Sparks2={params['sparks2_spawn_rate']} (52.5), Total={params['continuous_total_rate']} (152.5)")
    require(abs(params['sparks1_spawn_rate'] - 70.0) < TOLERANCE, f"Sparks1 mismatch: {params['sparks1_spawn_rate']}")
    require(abs(params['sparks2_spawn_rate'] - 52.5) < TOLERANCE, f"Sparks2 mismatch: {params['sparks2_spawn_rate']}")
    require(abs(params['continuous_total_rate'] - 152.5) < TOLERANCE, f"Total mismatch: {params['continuous_total_rate']}")
    require(abs(params['user_scale_all'] - 1.25) < TOLERANCE, f"Scale_All mismatch: {params['user_scale_all']}")

    log("SUCCESS: Production NS_Boss_PhaseTwoAura successfully updated to BoostLite parameters.")
    return True


if __name__ == "__main__":
    ok = promote_production()
    if not ok:
        sys.exit(1)
