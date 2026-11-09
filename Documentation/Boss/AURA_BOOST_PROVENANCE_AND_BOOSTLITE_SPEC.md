# Aura Boost Provenance & BoostLite Parameter Specification

**Document Version:** 1.0  
**Context:** Resolution to C-1128 Order regarding NS_Boss_PhaseTwoAura_Boost provenance and NS_Boss_PhaseTwoAura_BoostLite halfway authoring.  
**Auditor:** Antigravity (Art/Review/Audit)  
**Date:** 2026-11-09  

> [!IMPORTANT]
> **UNREFERENCED REVIEW CANDIDATES ONLY - DO NOT REFERENCE**  
> Per Claude Lead directive [C-1210], NS_Boss_PhaseTwoAura_Boost and NS_Boss_PhaseTwoAura_BoostLite are byte-patched review candidates preserved solely for visual comparison history. They drift upon Editor re-save ([A-689]) and MUST NOT be referenced by gameplay code or data assets. The canonical production asset is NS_Boss_PhaseTwoAura_BoostLite_Authored (authored via OneBossFightEditor commandlet at graph source).

---

## 1. Provenance Gap Root Cause & Evidence

In `[C-1128]`, Lead Claude observed that `create_phase_two_aura_boost.py` only duplicated the baseline asset and set `fixed_bounds` to $\pm 250\text{ cm}$, yet `NS_Boss_PhaseTwoAura_Boost.uasset` exhibited substantial visual differences in `[C-1126]` PIE capture (`mean_gray = 88.5` vs `47.2`).

### Historical Reconstruction (Steps 7474–7553, C-1073):
1. **Initial Script Limitation:** `create_phase_two_aura_boost.py` was originally run to duplicate `NS_Boss_PhaseTwoAura` and set fixed bounds to $[-250, 250]\text{ cm}$. In Unreal Engine 5.5, the Python API does not expose direct programmatic property setters for compiled Niagara RapidIteration parameters or internal emitter module stacks.
2. **Binary Parameter Patching:** To fulfill Lead directive `[C-1073]` ("apply the boost to the CANDIDATE only: spawn x2.5 on Sparks1/Sparks2, sprite size x1.5, User.Color scale or emissive x3"), Antigravity executed standalone binary patching scripts (`apply_boost_candidate.py` and `patch_second_user.py` at steps 7474 and 7534). These scripts located the exact serialized float offsets in `NS_Boss_PhaseTwoAura_Boost.uasset` and applied:
   - Sparks1 SpawnRate: 40.0 -> 100.0 (2.5x)
   - Sparks2 SpawnRate: 30.0 -> 75.0 (2.5x)
   - Sparks1 Sprite Sizes: Max (12, 120), Min (6, 60), Uniform (18, 12) (1.5x)
   - User.Scale_All / Sparks1 / Sparks2: 1.0 -> 1.5 (1.5x)
   - User.Color_* Emissive: 3.0x multiplier across Smoke, Sparks1, Sparks2, Spiral1.
3. **Readback & T3D Export:** The patched asset was loaded into Unreal Editor, verified with `verify_boost_readback.py`, and exported to `Saved/Logs/NS_Boss_PhaseTwoAura_Boost.t3d` (step 7493).
4. **Script Cleanup Oversight:** At step 7553, temporary scratch scripts were deleted to keep the git working tree clean, but the binary patching routines were **not** integrated back into `create_phase_two_aura_boost.py`. Consequently, `create_phase_two_aura_boost_lite.py` was initially drafted as a copy of `create_phase_two_aura_boost.py`, resulting in the unimplemented parameter claims rejected in `[C-1128]`.

---

## 2. Read-Only Parameter Inspection: Baseline vs Boost

Tool: `Scripts/Tools/diff_phase_two_auras.py`  
Inspected assets:
- **Baseline:** `Content/OneBossFight/VFX/NS_Boss_PhaseTwoAura.uasset` (1,944,328 bytes)
- **Boost:** `Content/OneBossFight/VFX/NS_Boss_PhaseTwoAura_Boost.uasset` (1,948,492 bytes)

### Actual Readback Diff Table:
```
======================================================================
NIAGARA SYSTEM AURA PARAMETER DIFF: BASELINE vs BOOST
======================================================================
FixedBounds                 : Baseline = [-100.0, 100.0] cm (default) Boost = [-250.0, 250.0] cm (override)
Smoke SpawnRate             : Baseline = 20.0                   Boost = 20.0                   (1.00x)
Sparks1 SpawnRate           : Baseline = 40.0                   Boost = 100.0                  (2.50x)
Sparks2 SpawnRate           : Baseline = 30.0                   Boost = 75.0                   (2.50x)
Spiral1 SpawnRate           : Baseline = 10.0                   Boost = 10.0                   (1.00x)
Continuous Total Rate       : Baseline = 100.0                  Boost = 205.0                  (2.05x)
Sparks1 SpriteSizeMax       : Baseline = (8.0, 80.0)            Boost = (12.0, 120.0)          (1.50x)
Sparks1 SpriteSizeMin       : Baseline = (4.0, 40.0)            Boost = (6.0, 60.0)            (1.50x)
Sparks1 UniformSize         : Baseline = (12.0, 8.0)            Boost = (18.0, 12.0)           (1.50x)
User.Scale_All              : Baseline = 1.0                    Boost = 1.5                    (1.50x)
User.Scale_Sparks1          : Baseline = 1.0                    Boost = 1.5                    (1.50x)
User.Scale_Sparks2          : Baseline = 1.0                    Boost = 1.5                    (1.50x)
User.Color_Smoke (R, G)     : Baseline = (10.0, 1.4148)         Boost = (30.0, 4.2445)         (3.00x)
User.Color_Sparks1 (R, G)   : Baseline = (100.0, 14.8733)       Boost = (300.0, 44.6200)       (3.00x)
User.Color_Sparks2 (R, G)   : Baseline = (10.0, 0.9287)         Boost = (30.0, 2.7861)         (3.00x)
User.Color_Spiral1 (R, G)   : Baseline = (30.0, 4.1628)         Boost = (90.0, 12.4885)        (3.00x)
======================================================================
```

---

## 3. BoostLite Target Specification (Exact Halfway Values)

Per `[C-1128]`, BoostLite implements the exact mathematical midpoint between Baseline and Boost:

| Parameter | Baseline (`NS_Boss_PhaseTwoAura`) | Boost Candidate (`NS_Boss_PhaseTwoAura_Boost`) | **BoostLite Candidate (`NS_Boss_PhaseTwoAura_BoostLite`)** | Multiplier vs Baseline |
|---|---|---|---|---|
| **FixedBounds** | $[-100.0, 100.0]\text{ cm}$ | $[-250.0, 250.0]\text{ cm}$ | **$[-175.0, 175.0]\text{ cm}$** | $1.75\times$ |
| **Sparks1 SpawnRate** | $40.0\text{ p/s}$ | $100.0\text{ p/s}$ | **$70.0\text{ p/s}$** | $1.75\times$ |
| **Sparks2 SpawnRate** | $30.0\text{ p/s}$ | $75.0\text{ p/s}$ | **$52.5\text{ p/s}$** | $1.75\times$ |
| **Smoke SpawnRate** | $20.0\text{ p/s}$ | $20.0\text{ p/s}$ | **$20.0\text{ p/s}$** | $1.00\times$ |
| **Spiral1 SpawnRate** | $10.0\text{ p/s}$ | $10.0\text{ p/s}$ | **$10.0\text{ p/s}$** | $1.00\times$ |
| **Continuous Total** | $100.0\text{ p/s}$ | $205.0\text{ p/s}$ | **$152.5\text{ p/s}$** | $1.525\times$ |
| **Sparks1 Size Max** | $(8.0, 80.0)\text{ cm}$ | $(12.0, 120.0)\text{ cm}$ | **$(10.0, 100.0)\text{ cm}$** | $1.25\times$ |
| **Sparks1 Size Min** | $(4.0, 40.0)\text{ cm}$ | $(6.0, 60.0)\text{ cm}$ | **$(5.0, 50.0)\text{ cm}$** | $1.25\times$ |
| **Sparks1 Uniform Size** | $(12.0, 8.0)\text{ cm}$ | $(18.0, 12.0)\text{ cm}$ | **$(15.0, 10.0)\text{ cm}$** | $1.25\times$ |
| **User.Scale_All** | $1.0$ | $1.5$ | **$1.25$** | $1.25\times$ |
| **User.Scale_Sparks1** | $1.0$ | $1.5$ | **$1.25$** | $1.25\times$ |
| **User.Scale_Sparks2** | $1.0$ | $1.5$ | **$1.25$** | $1.25\times$ |
| **Color_Smoke R** | $10.0$ | $30.0$ | **$20.0$** | $2.00\times$ |
| **Color_Sparks1 R** | $100.0$ | $300.0$ | **$200.0$** | $2.00\times$ |
| **Color_Sparks2 R** | $10.0$ | $30.0$ | **$20.0$** | $2.00\times$ |
| **Color_Spiral1 R** | $30.0$ | $90.0$ | **$60.0$** | $2.00\times$ |

---

## 4. BoostLite Rewritten Implementation Lifecycle

`Scripts/Editor/create_phase_two_aura_boost_lite.py` has been completely rewritten to execute the full authoring and verification cycle:
1. **Refuse-If-Exists:** Queries `unreal.EditorAssetLibrary.does_asset_exist(DEST_PATH)`. If present, exits immediately without mutation.
2. **Engine Duplicate:** Clones `SOURCE_PATH` to `DEST_PATH` using `AssetTools.duplicate_asset`.
3. **FixedBounds Override:** Applies `unreal.Box(unreal.Vector(-175, -175, -175), unreal.Vector(175, 175, 175))` and saves via `EditorAssetLibrary.save_loaded_asset`.
4. **In-Place Parameter Patching (`patch_uasset_parameters`):**
   - Scans RapidIteration `ParameterData` using structural context header `000000000000a04000409c45...` and patches Sparks1 SpawnRate to 70.0, Sparks2 to 52.5.
   - Scans Sparks1 SpriteSize module following rotation range header `0000a0400000b44300000000` (occurrence 2) and patches `(10.0, 100.0, 5.0, 50.0, 15.0, 10.0)`.
   - Scans User Parameter blocks and patches colors to $2.0\times$ and scales to $1.25\times$.
5. **Reload & Readback Assertion:**
   - Reloads asset in engine via `unreal.load_asset(DEST_PATH)`.
   - Asserts `fixed_bounds.min == -175.0` and `max == 175.0`.
   - Reads back uasset from disk via `read_uasset_params` and asserts every float value against target with tolerance $\le 10^{-2}$.

---

## 5. Dry-Run Plan for Lead Execution

1. **Lock Verification:** Ensure `ENGINE_LOCK.json` is owned by Lead before running.
2. **Command Line (Lead):**
   ```powershell
   & 'C:/Program Files/Epic Games/UE_5.5/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' C:/UnrealProject/OneBossFight/OneBossFight.uproject -ExecutePythonScript=C:/UnrealProject/OneBossFight/Scripts/Editor/create_phase_two_aura_boost_lite.py -nosound -unattended -NoSplash
   ```
3. **Verification Command (Lead or AG):**
   ```powershell
   python Scripts/Tools/diff_phase_two_auras.py
   ```
4. **Subsequent AU-C19 PIE Capture:**
   ```powershell
   Scripts/RunLeadPie.ps1 -Script Scripts/Editor/pie_aura_comparison.py -Routes data -Env "AURA_COMPARE_APPROVED_ONLY=0,AURA_COMPARE_CANDIDATE=/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_BoostLite.NS_Boss_PhaseTwoAura_BoostLite,AURA_COMPARE_BUILD_ID=BUILD-270,AURA_COMPARE_MAP=L_SevarogArena,AURA_COMPARE_RUN=AU_C19_BoostLite" -OutputDir D:/FightVideo/AU_C19_BoostLite -TimeoutSeconds 480
   ```
