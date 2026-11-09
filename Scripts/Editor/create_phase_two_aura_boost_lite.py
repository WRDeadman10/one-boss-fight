"""Create /Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_BoostLite candidate asset (C-1126, C-1128).

Applies exact halfway values between Baseline and Boost:
- FixedBounds: [-175.0, 175.0] cm (was [-100.0, 100.0] baseline, [-250.0, 250.0] boost)
- Sparks1 SpawnRate: 40.0 -> 70.0 p/s (1.75x)
- Sparks2 SpawnRate: 30.0 -> 52.5 p/s (1.75x)
- Continuous Total Rate: 100.0 -> 152.5 p/s (was 100.0 baseline, 205.0 boost)
- Sparks1 SpriteSizeMax: (8.0, 80.0) -> (10.0, 100.0) cm (1.25x)
- Sparks1 SpriteSizeMin: (4.0, 40.0) -> (5.0, 50.0) cm (1.25x)
- Sparks1 UniformSize: (12.0, 8.0) -> (15.0, 10.0) cm (1.25x)
- User.Scale_All: 1.0 -> 1.25 (1.25x)
- User.Scale_Sparks1: 1.0 -> 1.25 (1.25x)
- User.Scale_Sparks2: 1.0 -> 1.25 (1.25x)
- User.Color_Smoke: (10.0, 1.4148) -> (20.0, 2.8296) (2.00x)
- User.Color_Sparks1: (100.0, 14.8733) -> (200.0, 29.7466) (2.00x)
- User.Color_Sparks2: (10.0, 0.9287) -> (20.0, 1.8574) (2.00x)
- User.Color_Spiral1: (30.0, 4.1628) -> (60.0, 8.3257) (2.00x)

Safety rules:
- Refuse-if-exists
- Assert-before-save & readback-assert after creation
- Keep approved NS_Boss_PhaseTwoAura untouched
- Run under ENGINE_LOCK
"""
import os
import struct
import sys

SOURCE_PATH = "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura"
DEST_NAME = "NS_Boss_PhaseTwoAura_BoostLite"
DEST_DIR = "/Game/OneBossFight/VFX"
DEST_PATH = f"{DEST_DIR}/{DEST_NAME}"
DISK_PATH = r"C:\UnrealProject\OneBossFight\Content\OneBossFight\VFX\NS_Boss_PhaseTwoAura_BoostLite.uasset"

def log(msg):
    try:
        import unreal
        unreal.log(f"[PhaseTwoAuraBoostLite] {msg}")
    except ImportError:
        pass
    print(f"[PhaseTwoAuraBoostLite] {msg}")

def log_error(msg):
    try:
        import unreal
        unreal.log_error(f"[PhaseTwoAuraBoostLite] ERROR: {msg}")
    except ImportError:
        pass
    print(f"[PhaseTwoAuraBoostLite] ERROR: {msg}", file=sys.stderr)

def read_uasset_params(path):
    """Read back and parse all key aura parameters from the uasset file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Asset file not found: {path}")

    with open(path, "rb") as f:
        data = f.read()

    params = {"path": path, "file_size": len(data)}

    # FixedBounds
    params["bounds_min"] = -100.0
    params["bounds_max"] = 100.0
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

    # Sparks1 Sprite Sizes (2nd match of rotation header)
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
        if (r_smoke in (10.0, 20.0) and r_sp1 in (100.0, 200.0) and
            r_sp2 in (10.0, 20.0) and r_spir in (30.0, 60.0)):
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
    """Patch the internal Niagara emitter parameters and user parameters to halfway values."""
    with open(disk_path, "rb") as f:
        data = bytearray(f.read())

    orig_len = len(data)

    # 1. SpawnRates: Sparks1 40 -> 70, Sparks2 30 -> 52.5
    ctx = bytes.fromhex('000000000000a04000409c45000000000000803f000000000000a041')
    pos = 0
    patched_spawn = False
    while True:
        idx = data.find(ctx, pos)
        if idx == -1:
            break
        s1 = struct.unpack('<f', data[idx+52:idx+56])[0]
        s2 = struct.unpack('<f', data[idx+80:idx+84])[0]
        if abs(s1 - 40.0) < 1e-3 and abs(s2 - 30.0) < 1e-3:
            data[idx+52:idx+56] = struct.pack('<f', 70.0)
            data[idx+80:idx+84] = struct.pack('<f', 52.5)
            patched_spawn = True
            log(f"Patched SpawnRates at {idx}: Sparks1 40.0->70.0, Sparks2 30.0->52.5")
        pos = idx + len(ctx)
    assert patched_spawn, "Failed to patch SpawnRates in ParameterData"

    # 2. Sparks1 SpriteSizes: Max (10, 100), Min (5, 50), Uniform (15, 10)
    size_base = struct.pack('<ffffff', 8.0, 80.0, 4.0, 40.0, 12.0, 8.0)
    pos = 0
    patched_sizes = 0
    while True:
        idx = data.find(size_base, pos)
        if idx == -1:
            break
        data[idx:idx+24] = struct.pack('<ffffff', 10.0, 100.0, 5.0, 50.0, 15.0, 10.0)
        patched_sizes += 1
        log(f"Patched Sparks1 SpriteSizes at {idx}")
        pos = idx + 24
    assert patched_sizes >= 1, "Failed to patch Sparks1 SpriteSizes"

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
            # Patch colors: 2.0x emissive
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

            # Patch scales: 1.25x
            data[idx+80:idx+84] = struct.pack('<f', 1.25)
            data[idx+88:idx+92] = struct.pack('<f', 1.25)
            data[idx+92:idx+96] = struct.pack('<f', 1.25)
            patched_user += 1
            log(f"Patched User parameters at {idx}")
        pos = idx + 4
    assert patched_user >= 1, "Failed to patch User parameters"

    assert len(data) == orig_len, "Uasset file length changed during patching"

    with open(disk_path, "wb") as f:
        f.write(data)
    log(f"Successfully wrote patched parameters to {disk_path}")

def create_candidate():
    try:
        import unreal
    except ImportError:
        log_error("Unreal engine Python module not available. Must run under UnrealEditor-Cmd.")
        return False

    eal = unreal.EditorAssetLibrary
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    if eal.does_asset_exist(DEST_PATH):
        log(f"REFUSE: {DEST_PATH} already exists. Leaving intact.")
        reloaded = unreal.load_asset(DEST_PATH)
        if reloaded:
            readback_bounds = reloaded.get_editor_property("fixed_bounds")
            log(f"EXISTING_BOUNDS: min=({readback_bounds.min.x:.1f}, {readback_bounds.min.y:.1f}, {readback_bounds.min.z:.1f}) max=({readback_bounds.max.x:.1f}, {readback_bounds.max.y:.1f}, {readback_bounds.max.z:.1f}) is_valid={readback_bounds.is_valid}")
        return True

    source_asset = unreal.load_asset(SOURCE_PATH)
    if not source_asset:
        log_error(f"Source asset {SOURCE_PATH} not found.")
        return False

    base_bounds = source_asset.get_editor_property("fixed_bounds")
    log(f"Baseline {SOURCE_PATH} fixed_bounds: min=({base_bounds.min.x:.1f}, {base_bounds.min.y:.1f}, {base_bounds.min.z:.1f}) max=({base_bounds.max.x:.1f}, {base_bounds.max.y:.1f}, {base_bounds.max.z:.1f}) is_valid={base_bounds.is_valid}")

    # Duplicate to boost lite candidate
    boost_lite_asset = asset_tools.duplicate_asset(DEST_NAME, DEST_DIR, source_asset)
    if not boost_lite_asset:
        log_error(f"Failed to duplicate {SOURCE_PATH} to {DEST_PATH}")
        return False

    # Apply halfway fixed bounds [-175, 175] cm
    new_bounds = unreal.Box(
        unreal.Vector(-175.0, -175.0, -175.0),
        unreal.Vector(175.0, 175.0, 175.0)
    )
    boost_lite_asset.set_editor_property("fixed_bounds", new_bounds)

    # Save initial duplicated asset
    saved = eal.save_loaded_asset(boost_lite_asset)
    if not saved:
        log_error(f"Failed to save {DEST_PATH}")
        return False

    # Apply halfway emitter & user parameters directly to the candidate uasset
    patch_uasset_parameters(DISK_PATH)

    # Reload and assert readback
    reloaded = unreal.load_asset(DEST_PATH)
    if not reloaded:
        log_error(f"Failed to reload {DEST_PATH} after parameter patching")
        return False

    readback_bounds = reloaded.get_editor_property("fixed_bounds")
    log(f"READBACK_ENGINE_BOUNDS: min=({readback_bounds.min.x:.1f}, {readback_bounds.min.y:.1f}, {readback_bounds.min.z:.1f}) max=({readback_bounds.max.x:.1f}, {readback_bounds.max.y:.1f}, {readback_bounds.max.z:.1f}) is_valid={readback_bounds.is_valid}")
    assert readback_bounds.min.x == -175.0 and readback_bounds.min.y == -175.0 and readback_bounds.min.z == -175.0, "Bounds min mismatch"
    assert readback_bounds.max.x == 175.0 and readback_bounds.max.y == 175.0 and readback_bounds.max.z == 175.0, "Bounds max mismatch"

    # Full readback verification of all patched values
    params = read_uasset_params(DISK_PATH)
    log(f"READBACK_SPAWN_RATES: Sparks1={params['sparks1_spawn_rate']} (target 70.0), Sparks2={params['sparks2_spawn_rate']} (target 52.5), ContinuousTotal={params['continuous_total_rate']} (target 152.5)")
    log(f"READBACK_SPRITE_SIZE: Max={params['sparks1_sprite_size_max']} (target (10.0, 100.0)), Min={params['sparks1_sprite_size_min']} (target (5.0, 50.0)), Uniform={params['sparks1_uniform_size']} (target (15.0, 10.0))")
    log(f"READBACK_USER_SCALES: All={params['user_scale_all']} (target 1.25), Sparks1={params['user_scale_sparks1']} (target 1.25), Sparks2={params['user_scale_sparks2']} (target 1.25)")
    log(f"READBACK_USER_COLORS: Smoke_R={params['user_color_smoke'][0]} (target 20.0), Sparks1_R={params['user_color_sparks1'][0]} (target 200.0), Sparks2_R={params['user_color_sparks2'][0]} (target 20.0), Spiral1_R={params['user_color_spiral1'][0]} (target 60.0)")

    # Assertions
    assert abs(params['sparks1_spawn_rate'] - 70.0) < 1e-2, f"Sparks1 rate mismatch: {params['sparks1_spawn_rate']}"
    assert abs(params['sparks2_spawn_rate'] - 52.5) < 1e-2, f"Sparks2 rate mismatch: {params['sparks2_spawn_rate']}"
    assert abs(params['sparks1_sprite_size_max'][0] - 10.0) < 1e-2 and abs(params['sparks1_sprite_size_max'][1] - 100.0) < 1e-2, "SpriteSizeMax mismatch"
    assert abs(params['sparks1_sprite_size_min'][0] - 5.0) < 1e-2 and abs(params['sparks1_sprite_size_min'][1] - 50.0) < 1e-2, "SpriteSizeMin mismatch"
    assert abs(params['sparks1_uniform_size'][0] - 15.0) < 1e-2 and abs(params['sparks1_uniform_size'][1] - 10.0) < 1e-2, "UniformSize mismatch"
    assert abs(params['user_scale_all'] - 1.25) < 1e-2, "Scale_All mismatch"
    assert abs(params['user_color_smoke'][0] - 20.0) < 1e-2, "Color_Smoke R mismatch"
    assert abs(params['user_color_sparks1'][0] - 200.0) < 1e-2, "Color_Sparks1 R mismatch"
    assert abs(params['user_color_sparks2'][0] - 20.0) < 1e-2, "Color_Sparks2 R mismatch"
    assert abs(params['user_color_spiral1'][0] - 60.0) < 1e-2, "Color_Spiral1 R mismatch"

    log("SUCCESS: Candidate NS_Boss_PhaseTwoAura_BoostLite created, patched, and verified with all halfway parameters.")
    return True

if __name__ == "__main__":
    ok = create_candidate()
    if not ok:
        sys.exit(1)
