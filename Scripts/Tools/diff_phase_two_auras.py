"""Read-only parameter diff between approved baseline NS_Boss_PhaseTwoAura and candidate NS_Boss_PhaseTwoAura_Boost.

Extracts and displays:
1. FixedBounds (culling box)
2. Emitter SpawnRates (Sparks1, Sparks2, continuous totals)
3. Sparks1 Sprite Size modules (Min, Max, Uniform)
4. User Parameter Scales (User.Scale_All, User.Scale_Sparks1, User.Scale_Sparks2)
5. User Parameter Emissive Colors (Color_Smoke, Color_Sparks1, Color_Sparks2, Color_Spiral1)
"""
import os
import struct
import sys

BASE_UASSET = r"C:\UnrealProject\OneBossFight\Content\OneBossFight\VFX\NS_Boss_PhaseTwoAura.uasset"
BOOST_UASSET = r"C:\UnrealProject\OneBossFight\Content\OneBossFight\VFX\NS_Boss_PhaseTwoAura_Boost.uasset"

def read_uasset_params(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Asset not found: {path}")

    with open(path, "rb") as f:
        data = f.read()

    params = {
        "path": path,
        "file_size": len(data),
    }

    # 1. FixedBounds
    # Check System-level FixedBounds override near end of asset (> 1,000,000)
    params["bounds_min"] = -100.0
    params["bounds_max"] = 100.0
    params["fixed_bounds"] = "[-100.0, 100.0] cm (default)"
    for pos in range(len(data) - 48, 1000000, -1):
        min_x, min_y, min_z = struct.unpack('<ddd', data[pos:pos+24])
        max_x, max_y, max_z = struct.unpack('<ddd', data[pos+24:pos+48])
        if min_x == min_y == min_z and max_x == max_y == max_z and abs(min_x + max_x) < 1e-3 and min_x < -10.0:
            params["bounds_min"] = min_x
            params["bounds_max"] = max_x
            params["fixed_bounds"] = f"[{min_x:.1f}, {max_x:.1f}] cm (override)"
            break

    # 2. SpawnRates in RapidIterationParameters ParameterData block
    # Pattern: Loop Delay 0.0, Loop Duration 5.0, MaxDist 20000.0, MinDist 0.0, Prob 1.0, Group 0, Smoke 20.0
    # In bytes: 00000000 0000a040 00409c45 00000000 0000803f 00000000 0000a041
    ctx = bytes.fromhex('000000000000a04000409c45000000000000803f000000000000a041')
    pos = 0
    params["sparks1_spawn_rate"] = None
    params["sparks2_spawn_rate"] = None
    while True:
        idx = data.find(ctx, pos)
        if idx == -1:
            break
        # Offset +52 is Sparks1 SpawnRate, +80 is Sparks2 SpawnRate, +108 is Spiral1 SpawnRate
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

    # 3. Sprite Sizes
    # In each emitter, the sprite size block follows the rotation range header: (5.0, 360.0, 0.0)
    # The 2nd match is Sparks1:
    header = bytes.fromhex('0000a0400000b44300000000')
    pos = 0
    sparks1_match = None
    count = 0
    while True:
        idx = data.find(header, pos)
        if idx == -1:
            break
        count += 1
        if count == 2: # 2nd occurrence is Sparks1
            sparks1_match = idx
            break
        pos = idx + len(header)

    if sparks1_match is not None:
        vals = struct.unpack('<ffffff', data[sparks1_match+12:sparks1_match+36])
        params["sparks1_sprite_size_max"] = (vals[0], vals[1])
        params["sparks1_sprite_size_min"] = (vals[2], vals[3])
        params["sparks1_uniform_size"] = (vals[4], vals[5])
    else:
        params["sparks1_sprite_size_max"] = "UNKNOWN"

    # 4. User Parameters (User.Color_* and User.Scale_*)
    # Smoke: (R, G, B, A), Sparks1: (R, G, B, A), Sparks2: (R, G, B, A), Spiral1: (R, G, B, A)
    # followed at +80 by Scale_All, +88 Scale_Sparks1, +92 Scale_Sparks2
    # Search by User.Color_Smoke R float: 10.0 (base) or 30.0 (boost) followed by known green
    for pos in [i for i in range(len(data)-100) if (data[i:i+4] in [struct.pack('<f', 10.0), struct.pack('<f', 30.0)])]:
        # Check if R at pos+16 is 100.0 or 300.0, and pos+32 is 10.0 or 30.0
        r_smoke = struct.unpack('<f', data[pos:pos+4])[0]
        r_sparks1 = struct.unpack('<f', data[pos+16:pos+20])[0]
        r_sparks2 = struct.unpack('<f', data[pos+32:pos+36])[0]
        r_spiral1 = struct.unpack('<f', data[pos+48:pos+52])[0]
        if (r_smoke in (10.0, 30.0) and r_sparks1 in (100.0, 300.0) and
            r_sparks2 in (10.0, 30.0) and r_spiral1 in (30.0, 90.0)):
            # Found User parameter block!
            g_smoke = struct.unpack('<f', data[pos+4:pos+8])[0]
            g_sparks1 = struct.unpack('<f', data[pos+20:pos+24])[0]
            g_sparks2 = struct.unpack('<f', data[pos+36:pos+40])[0]
            g_spiral1 = struct.unpack('<f', data[pos+52:pos+56])[0]
            scale_all = struct.unpack('<f', data[pos+80:pos+84])[0]
            scale_sparks1 = struct.unpack('<f', data[pos+88:pos+92])[0]
            scale_sparks2 = struct.unpack('<f', data[pos+92:pos+96])[0]
            params["user_color_smoke"] = (r_smoke, g_smoke)
            params["user_color_sparks1"] = (r_sparks1, g_sparks1)
            params["user_color_sparks2"] = (r_sparks2, g_sparks2)
            params["user_color_spiral1"] = (r_spiral1, g_spiral1)
            params["user_scale_all"] = scale_all
            params["user_scale_sparks1"] = scale_sparks1
            params["user_scale_sparks2"] = scale_sparks2
            break

    return params

def diff_assets(base_path=BASE_UASSET, boost_path=BOOST_UASSET):
    base_p = read_uasset_params(base_path)
    boost_p = read_uasset_params(boost_path)

    print("=" * 70)
    print("NIAGARA SYSTEM AURA PARAMETER DIFF: BASELINE vs BOOST")
    print("=" * 70)
    print(f"Baseline: {base_p['path']} ({base_p['file_size']:,} bytes)")
    print(f"Boost:    {boost_p['path']} ({boost_p['file_size']:,} bytes)")
    print("-" * 70)

    fields = [
        ("FixedBounds", "fixed_bounds"),
        ("Smoke SpawnRate", "smoke_spawn_rate"),
        ("Sparks1 SpawnRate", "sparks1_spawn_rate"),
        ("Sparks2 SpawnRate", "sparks2_spawn_rate"),
        ("Spiral1 SpawnRate", "spiral1_spawn_rate"),
        ("Continuous Total Rate", "continuous_total_rate"),
        ("Sparks1 SpriteSizeMax", "sparks1_sprite_size_max"),
        ("Sparks1 SpriteSizeMin", "sparks1_sprite_size_min"),
        ("Sparks1 UniformSize", "sparks1_uniform_size"),
        ("User.Scale_All", "user_scale_all"),
        ("User.Scale_Sparks1", "user_scale_sparks1"),
        ("User.Scale_Sparks2", "user_scale_sparks2"),
        ("User.Color_Smoke (R, G)", "user_color_smoke"),
        ("User.Color_Sparks1 (R, G)", "user_color_sparks1"),
        ("User.Color_Sparks2 (R, G)", "user_color_sparks2"),
        ("User.Color_Spiral1 (R, G)", "user_color_spiral1"),
    ]

    for label, key in fields:
        b_val = base_p.get(key)
        bo_val = boost_p.get(key)
        ratio = ""
        if isinstance(b_val, (int, float)) and isinstance(bo_val, (int, float)) and b_val > 0:
            ratio = f" ({bo_val / b_val:.2f}x)"
        elif isinstance(b_val, tuple) and isinstance(bo_val, tuple) and len(b_val) == 2 and isinstance(b_val[0], (int, float)):
            r0 = bo_val[0] / b_val[0] if b_val[0] > 0 else 1.0
            ratio = f" ({r0:.2f}x)"
        print(f"{label:<28}: Baseline = {str(b_val):<22} Boost = {str(bo_val):<22}{ratio}")

    print("=" * 70)
    return base_p, boost_p

if __name__ == "__main__":
    diff_assets()
