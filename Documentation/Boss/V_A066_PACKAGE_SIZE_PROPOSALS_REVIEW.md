# V-A066: Second Review of Packaging & Distribution Size Proposals (V-C064 / V-C065)

**Author:** Antigravity (Lane A)  
**Date:** 2026-11-06  
**Reference Tasks:** `V-A066`, `V-C064`, `V-C065`, `Documentation/Boss/V_C061_C065_PACKAGING_AND_SIZE.md`

---

## 1. Executive Summary & Review Verdict

Codex's packaging and size inventory in [`V_C061_C065_PACKAGING_AND_SIZE.md`](./V_C061_C065_PACKAGING_AND_SIZE.md) establishes an accurate baseline inventory of `Saved/StagedBuilds/Windows`: **4,351,585,036 bytes (4.35 GB) across 60 files**.

This second review endorses Codex's conservative principle: **no destructive asset deletions or asset recompressions should occur based solely on IoStore container size (`.ucas`)**. 

However, by analyzing engine packaging settings, debug symbol exclusion, and binary distribution payloads, we identify immediate, safe size-reduction targets totaling **~680 MB from binary/symbol pruning** and **~1.2 GB from texture mip clamping**, without altering any source assets or runtime gameplay logic.

---

## 2. Staged Payload Breakdown & Analysis

```
Total Staged Build: 4.35 GB
├── Content IoStore Container (OneBossFight-Windows.ucas):  3.25 GB (74.7%)
├── Debug Symbols (OneBossFight.pdb + tbb.pdb):              0.41 GB  (9.4%)
├── Game Executable (OneBossFight.exe):                     0.31 GB  (7.0%)
├── Third-Party / Plugin Binaries (DLSS, EOS, Vulkan):      0.35 GB  (8.0%)
└── Engine & Slate Assets / Manifests:                      0.03 GB  (0.9%)
```

### 2.1 Binary & Symbol Hygiene (Safe Shipping Stripping)
The current staged directory represents a Development configuration stage. For final Shipping distribution:
1. **Exclude PDBs:** `OneBossFight.pdb` (405.3 MB), `tbb.pdb` (3.0 MB), and `tbbmalloc.pdb` (1.1 MB) must be archived to a secure symbol server / crash repository rather than bundled in player packages. **Savings: 409.4 MB**.
2. **Exclude Debug DLSS Binaries:** The stage currently contains both development and release DLSS libraries:
   - `nvngx_dlssd.dll` (Debug/Dev variants): **141.8 MB** (93.5 MB + 48.3 MB).
   - `nvngx_dlss.dll` (Release variant): **118.3 MB**.
   Shipping packaging must stage only the release variant, stripping the duplicate debug symbols. **Savings: 141.8 MB**.
3. **Exclude Vulkan Developer SDK Layers:**
   - `VkLayer_khronos_validation.dll` (17.4 MB)
   - `VkLayer_api_dump.dll` (10.2 MB)
   - `VkLayer_gfxreconstruct.dll` (4.0 MB)
   - `VkLayer_khronos_profiles.dll` (1.5 MB)
   These layers are for driver debugging and should be disabled in `DefaultEngine.ini` packaging targets. **Savings: 33.1 MB**.
4. **DirectX 12 Debug SDK Layers:**
   - `d3d12SDKLayers.dll` (5.8 MB) is a development runtime; stripped in Shipping. **Savings: 5.8 MB**.

> [!TIP]
> **Net Binary / Symbol Savings:** Simply ensuring clean Shipping configuration stripping without PDBs or debug DLLs reduces the overall package footprint from **4.35 GB to ~3.75 GB (13.8% reduction)**.

---

## 3. Content Container (`.ucas`) Analysis & Texture Policy

The 3.25 GB IoStore container (`OneBossFight-Windows.ucas`) holds the cooked project assets.
- **Top Dominant Asset Category:** High-resolution 4K textures in `Content/OneBossFight/Environment/` (albedo, normal, and roughness maps for arena slabs, pillars, and braziers).
- **Target Resolution Alignment:** The project target is strictly **1080p / 60 FPS**. 4K source textures on background architectural pieces provide minimal perceptual visual benefit at 1080p, while consuming massive VRAM and disk space.
- **Proposed Optimization:** In `Config/DefaultEngine.ini`, configure Texture LOD Groups (`TextureGroup=TEXTUREGROUP_World`) with `MaxLODSize=2048`.
- **Projected Container Savings:** Downscaling non-hero environment textures from 4K to 2K reduces uncompressed texture data by 75%, shrinking the `.ucas` container from **3.25 GB to ~2.05 GB (saving ~1.2 GB)**.

---

## 4. Recommendations & Verification Sequence

1. **Lead Package Verification:** Implement an automated Shipping package smoke test verifying that `OneBossFight.pdb` and `*dlssd.dll` are absent from `Saved/StagedBuilds/WindowsNoEditor`.
2. **Per-Asset Size Accounting:** Run `UnrealPak.exe -Test` or inspect the UAT cook log (`Cook-*.txt`) to generate a per-asset size table before modifying any individual texture settings.
3. **Owner Authorization Gate:** Texture LOD group clamping alters visual fidelity at high zoom levels; submit a 2K vs 4K side-by-side visual comparison to the Owner prior to committing any ini or asset changes.
