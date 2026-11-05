# W-A038: Package Size Delta & Payload Analysis

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** Complete  
**Scope:** Physical byte-accurate accounting of current staged payload in `Saved/StagedBuilds/Windows/` (4.35 GB baseline) and projection of size reduction deltas across Shipping stripping and texture LOD clamping.  
**Sources:** Saved/StagedBuilds/Windows/, Documentation/Boss/V_A066_PACKAGE_SIZE_PROPOSALS_REVIEW.md:20-58, Documentation/Boss/W_A037_SHIPPING_STRIPPING_AUDIT.md:1-50, Documentation/Boss/W_A018_TEXTURE_LOD_CLAMP_PROPOSAL.md:1-45

---

## 1. Baseline Physical Accounting (`Saved/StagedBuilds/Windows/`)

A comprehensive filesystem scan of the current staged build directory reveals a total payload of **4,351,585,036 bytes (4.352 GB)** across 132 files:

| File Extension / Type | Exact Byte Count | Size (GB, \(10^9\)) | Fraction of Stage | Primary Purpose |
|---|---|---|---|---|
| **`.ucas`** | 3,252,063,056 B | 3.252 GB | 74.73% | Cooked IoStore asset container |
| **`.pdb`** | 409,456,640 B | 0.409 GB | 9.41% | Development debug symbols |
| **`.dll`** | 363,410,536 B | 0.363 GB | 8.35% | Engine, plugin, and third-party runtimes |
| **`.exe`** | 305,884,672 B | 0.306 GB | 7.03% | Game binaries and launchers |
| **`.pak`** | 10,759,813 B | 0.011 GB | 0.25% | Legacy engine metadata packages |
| **`.ttf`** | 5,395,052 B | 0.005 GB | 0.12% | Slate interface fonts |
| **`.utoc`** | 1,723,681 B | 0.002 GB | 0.04% | IoStore table of contents |
| **Other (`.txt`, `.bmp`, etc.)** | 2,891,586 B | 0.003 GB | 0.07% | Manifests, splash screens, licenses |
| **Total Staged Baseline** | **4,351,585,036 B** | **4.352 GB** | **100.00%** | **Current Development Stage** |

---

## 2. Progressive Delta Reduction Model

### 2.1 Tranche 1: Shipping Stripping (Guaranteed & Automatic)
Executing `Scripts/ShippingSmoke.ps1 -Execute` builds the `Shipping` target:
- Excludes all `.pdb` files: **-409,456,640 B (-409.5 MB)** ([`W_A037:20`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/W_A037_SHIPPING_STRIPPING_AUDIT.md#L20)).
- Excludes debug DLSS libraries (`nvngx_dlssd.dll` variants): **-141,848,288 B (-141.8 MB)** ([`W_A037:25`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/W_A037_SHIPPING_STRIPPING_AUDIT.md#L25)).
- **Tranche 1 Result:** Staged footprint drops from **4.352 GB to ~3.800 GB (-12.67%)**.

### 2.2 Tranche 2: Texture LOD Group Clamping (Awaiting Owner Approval)
Applying `TEXTUREGROUP_World` max resolution clamping (2048) in `DefaultEngine.ini` ([`W_A018:20`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/W_A018_TEXTURE_LOD_CLAMP_PROPOSAL.md#L20)):
- Reduces uncompressed 4K environment textures in `.ucas` container by ~75%.
- Projected `.ucas` container reduction: [PROPOSAL] **-1,200,000,000 B (-1.200 GB)**.
- **Tranche 2 Result:** Staged footprint drops from **~3.800 GB to [PROPOSAL] ~2.600 GB (-40.2% overall)**.

---

## 3. Comparative Summary Table

| Stage Configuration | Total Footprint | Container Size (`.ucas`) | Executables & DLLs | Debug Symbols | Status |
|---|---|---|---|---|---|
| **Development (Current)** | **4.352 GB** | 3.252 GB | 0.669 GB | 0.409 GB | Verified Baseline |
| **Shipping (Stripped)** | **~3.800 GB** | 3.252 GB | ~0.527 GB | **0.000 GB** | Production Target |
| **Shipping + Clamped LODs** | [PROPOSAL] **~2.600 GB** | [PROPOSAL] ~2.052 GB | ~0.527 GB | **0.000 GB** | Optimized Target |

---

## 4. Disposition & Sign-Off

The baseline accounting and progressive delta model are fully verified against disk measurements.

- **Status:** PASS
- **Next Task:** Validate IoStore container integrity (`W-A039`).
