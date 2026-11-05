# W-A018: Texture LOD Group Clamping Configuration Proposal

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** Proposal (Waiting on Owner Review)  
**Scope:** Specification of texture LOD group resolution clamping for `Config/DefaultEngine.ini` to mitigate VRAM over-allocation and shrink the packaged IoStore container.  
**Sources:** Documentation/Boss/V_A066_PACKAGE_SIZE_PROPOSALS_REVIEW.md:20-58, Documentation/Boss/V_A069_CONSOLIDATED_CONTENT_PROPOSALS.md:28-33, Documentation/Boss/V_A088_ART_CONTENT_RISK_REGISTER.md:17, Config/DefaultEngine.ini:9-29

---

## 1. Problem Statement & Motivation

As cataloged in `RSK-ART-003` ([`V_A088:17`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/V_A088_ART_CONTENT_RISK_REGISTER.md#L17)) and `V_A066:20-58`, the current staged IoStore container (`OneBossFight-Windows.ucas`) measures 3.25 GB, comprising 74.7% of the total 4.35 GB staged footprint.

The dominant storage consumer is uncompressed 4K environment texture maps (albedo, normal, roughness) for arena slabs, perimeter columns, and braziers in `/Game/OneBossFight/Environment/`.

At our target display resolution of **1080p / 60 FPS** on the reference RTX 2060 Super (8 GB VRAM baseline), full 4K background textures:
1. Provide virtually zero perceptible visual gain over 2K maps due to camera distance and screen pixel density.
2. Consume excessive texture streaming pool memory alongside Lumen global illumination and Virtual Shadow Maps.
3. Inflate package distribution size by an estimated [PROPOSAL] 1.2 GB.

---

## 2. Proposed Configuration Patch (`DefaultEngine.ini`)

Rather than destructively re-authoring or downsampling source textures in the Content directory, Unreal Engine provides engine-level texture LOD clamping via `TextureLODGroups`.

### 2.1 Proposed Ini Block

```ini
[/Script/Engine.TextureLODSettings]
@TextureLODGroups=ClearArray
+TextureLODGroups=(Group=TEXTUREGROUP_World,MinLODSize=1,MaxLODSize=2048,LODBias=0,MinMagFilter=aniso,MipFilter=point,MipGenSettings=TMGS_SimpleAverage)
+TextureLODGroups=(Group=TEXTUREGROUP_WorldNormalMap,MinLODSize=1,MaxLODSize=2048,LODBias=0,MinMagFilter=aniso,MipFilter=point,MipGenSettings=TMGS_SimpleAverage)
+TextureLODGroups=(Group=TEXTUREGROUP_WorldSpecular,MinLODSize=1,MaxLODSize=2048,LODBias=0,MinMagFilter=aniso,MipFilter=point,MipGenSettings=TMGS_SimpleAverage)
```

### 2.2 Preservation of Hero & Character Fidelity

Notice that character and visual effects groups remain completely untouched:
- `TEXTUREGROUP_Character`: Unclamped (retains full 4K source resolution for Greystone and Sevarog).
- `TEXTUREGROUP_CharacterNormalMap`: Unclamped.
- `TEXTUREGROUP_CharacterSpecular`: Unclamped.
- `TEXTUREGROUP_Effects`: Unclamped.

Only static world geometry textures (`TEXTUREGROUP_World*`) are clamped to a maximum mip size of 2048x2048.

---

## 3. Projected Impact Breakdown

| Metric | Baseline (Current) | Projected Clamped | Net Saving | Basis |
|---|---|---|---|---|
| IoStore Container (`.ucas`) | 3.25 GB | [PROPOSAL] ~2.05 GB | [PROPOSAL] ~1.20 GB (-36.9%) | [`V_A066:58`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/V_A066_PACKAGE_SIZE_PROPOSALS_REVIEW.md#L58) |
| Total Packaged Stage | 4.35 GB | [PROPOSAL] ~3.15 GB | [PROPOSAL] ~1.20 GB (-27.6%) | [`V_A066:23`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/V_A066_PACKAGE_SIZE_PROPOSALS_REVIEW.md#L23) |
| World Texture VRAM Allocation | > 1.8 GB | [PROPOSAL] ~1.2 GB | [PROPOSAL] ~600 MB (-33.3%) | [`V_A088:17`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/V_A088_ART_CONTENT_RISK_REGISTER.md#L17) |
| Character & Boss Detail | 100% Unaltered | 100% Unaltered | 0 loss | Full 4K hero textures retained |

---

## 4. Governance & Review Gate

Per project Look-Changing Rules and C-820 churn constraints:
- **No changes are made to `Config/DefaultEngine.ini` during this audit task.**
- This specification is logged as a non-destructive proposal for Owner evaluation.
- Application requires prior Owner review of 2K vs 4K side-by-side frame captures in `L_SevarogArena`.

- **Status:** PROPOSAL READY (WAITING ON OWNER REVIEW)
- **Next Task:** Audit unreferenced asset disposition against Asset Registry (`W-A019`).
