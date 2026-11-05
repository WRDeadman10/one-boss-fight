# V-A069: Consolidated Content & Packaging Proposals

**Author:** Antigravity (Lane A)  
**Date:** 2026-11-06  
**Reference Tasks:** `V-A066`, `V-A067`, `V-A068`, `V-A069`
**Sources:** Documentation/Boss/V_A066_PACKAGE_SIZE_PROPOSALS_REVIEW.md, Documentation/Boss/V_A067_CONTENT_FOLDER_STRUCTURE_REVIEW.md

---

## 1. Executive Summary

Synthesizing the packaging size audit ([`V_A066`](./V_A066_PACKAGE_SIZE_PROPOSALS_REVIEW.md)), folder structure review ([`V_A067`](./V_A067_CONTENT_FOLDER_STRUCTURE_REVIEW.md)), and asset naming census ([`V_A068`](./V_A068_ASSET_NAMING_AUDIT.md)), we submit **five actionable, non-destructive content proposals**.

All five proposals adhere strictly to the project rules: zero source assets are deleted, zero look-changing modifications are executed without Owner authorization, and all size-reduction gains are achieved through packaging configuration, cook filters, and symbol hygiene.

---

## 2. The Five Content Proposals

### Proposal 1: Shipping Binary & Symbol Pruning (Immediate ~680 MB Savings)
- **Problem:** Development packaging bundles 405 MB PDBs, 142 MB debug DLSS variants (`nvngx_dlssd.dll`), and 33 MB of Vulkan debug SDK layers into the staged build.
- **Action:** Enforce strict Shipping packaging rules in `Scripts/Package.ps1`:
  - Exclude all `*.pdb` files from distribution stages (archive to symbol server).
  - Stage only release-mode DLSS binaries (`nvngx_dlss.dll`).
  - Strip Vulkan validation layers and DX12 debug layer runtimes.
- **Impact:** **~680 MB disk reduction (15.6% smaller package)** with zero code changes and zero asset risk.

### Proposal 2: Texture LOD Group Clamping for World Meshes (Projected ~1.2 GB Savings)
- **Problem:** Arena environment meshes use 4K source textures that bloat the `.ucas` container to 3.25 GB, exceeding requirements for our 1080p output target.
- **Action:** In `Config/DefaultEngine.ini`, configure `TEXTUREGROUP_World` with `MaxLODSize=2048`.
- **Impact:** Shrinks IoStore container from **3.25 GB to ~2.05 GB (saving ~1.2 GB)**.
- **Gate:** Requires Owner visual approval on 1080p capture comparison before committing.

### Proposal 3: Cook Exclusion for Historical Proof & Scratch Folders
- **Problem:** `/Game/OneBossFight/FrameworkProof` (193 legacy test assets) and `/Game/OneBossFight/Scratch` (2 experimental assets) sit inside the primary content tree.
- **Action:** Add `/Game/OneBossFight/FrameworkProof` and `/Game/OneBossFight/Scratch` to `DirectoriesToNeverCook` in `Config/DefaultEditor.ini`.
- **Impact:** Guarantees 195 non-production test assets never enter the Shipping package, preventing container bloat and asset spoofing.

### Proposal 4: Deprecate Legacy `/Boss/` Namespace
- **Problem:** Having both `/Game/OneBossFight/Boss/` (4 stand-in montages) and `/Game/OneBossFight/Boss01/` (75 authoritative combat animations) creates namespace ambiguity.
- **Action:** Verify zero production references exist to `/Game/OneBossFight/Boss/` (confirmed in `V_A037`), then formally deprecate `/Boss/` in favor of `/Boss01/`.
- **Impact:** Clean, unambiguous project structure for future agent and human developers.

### Proposal 5: Preserve Third-Party Pack Isolation
- **Policy:** Explicitly protect `/GreystonePack/` and `/SevarogPack/` from cosmetic renaming passes.
- **Rationale:** 384 vendor assets use custom naming (`ABP_*_Grey`, `MM_*`). Renaming them offers zero runtime performance gain while introducing extreme risk of broken animation blueprint references.
- **Impact:** Zero regression risk across core locomotion and character retargeting.
