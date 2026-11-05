# V-A068: Asset Naming Convention & Prefix Census

**Author:** Antigravity (Lane A)  
**Date:** 2026-11-06  
**Reference Tasks:** `V-A068`, `V_A037`, `V_A067`
**Sources:** Content/OneBossFight/, Documentation/Boss/V_A067_CONTENT_FOLDER_STRUCTURE_REVIEW.md

---

## 1. Executive Summary

This audit evaluated all **827 assets** located across `/Game/OneBossFight` against Epic Games standard Unreal Engine asset naming conventions (Prefix + BaseName + Suffix).

The census revealed a clean structural dichotomy:
- **Project-Authored Assets (100% Conformance):** All custom boss animations, audio cues, environment materials, static meshes, Niagara systems, and Enhanced Input assets strictly follow standardized prefixes (`AM_`, `AN_`, `SM_`, `M_`, `MI_`, `NS_`, `IA_`, `IMC_`, `DA_`).
- **Third-Party Pack Assets (Vendor Conventions):** 384 assets inside `/GreystonePack/` and `/SevarogPack/` use vendor-provided naming (`ABP_*_Grey`, `MM_*`, `Dodge_*`, `Manny_*`). Per project rules, third-party vendor assets are left unrenamed to preserve package integrity and avoid breaking internal pack references.

---

## 2. Prefix Census Across Custom Project Assets

| Prefix | Asset Type | Count | Directory Scope | Conformance Status |
|---|---|:---:|---|:---:|
| `DA_` | Data Asset | 100 | `/Data/`, `/FrameworkProof/` | **Standard** |
| `L_` | Level / Map | 84 | `/Levels/` (incl. streaming sub-levels) | **Standard** |
| `M_` | Material | 53 | `/Environment/Materials/`, `/Effects/` | **Standard** |
| `T_` | Texture (2D / Normal / Mask) | 45 | `/Environment/Textures/`, `/Effects/` | **Standard** |
| `AM_` | Animation Montage | 23 | `/Boss01/Animations/`, `/Boss/` | **Standard** |
| `AN_` | Animation Sequence / Notify | 18 | `/Boss01/Animations/` | **Standard** |
| `SM_` | Static Mesh | 14 | `/Environment/Meshes/` | **Standard** |
| `GA_` | Gameplay Ability | 14 | `/Data/TypedABIFixtures/` | **Standard** |
| `MI_` | Material Instance | 13 | `/Environment/`, `/Effects/` | **Standard** |
| `SK_` / `SKM_` | Skeletal Mesh | 10 | `/Characters/` | **Standard** |
| `IA_` | Enhanced Input Action | 10 | `/Input/Actions/` | **Standard** |
| `BP_` / `WBP_` | Blueprint / Widget Blueprint | 6 | `/Characters/`, `/UI/` | **Standard** |
| `BS_` | Blend Space | 6 | `/Characters/Animations/` | **Standard** |
| `MF_` | Material Function | 3 | `/Environment/Materials/` | **Standard** |
| `NS_` | Niagara System | 2 | `/VFX/` | **Standard** |
| `MX_` | Music Track | 2 | `/Audio/` | **Standard** |
| `Mix_` | Sound Mix Modifier | 1 | `/Audio/` | **Standard** |
| `IMC_` | Input Mapping Context | 1 | `/Input/Contexts/` | **Standard** |
| `BT_` | Behavior Tree | 1 | `/Scratch/` | **Standard** |

---

## 3. Discrepancy Analysis

### 3.1 Legacy FrameworkProof Move Cards (`Move_*`)
- **Found:** 34 assets named `Move_Sevarog_AntiGreed_*`, `Move_Sevarog_BackStep_*`, etc., in `/Game/OneBossFight/FrameworkProof/Cards/`.
- **Finding:** These are early development cards rather than current production `DA_Boss01_MoveCard_*` assets.
- **Recommendation:** Do not rename in-place (which risks generating object redirectors); archive or exclude from cook via `DirectoriesToNeverCook`.

### 3.2 Pack Vendor Assets (`GreystonePack`, `SevarogPack`)
- **Found:** 384 assets with custom pack prefixes (`MM_*`, `ABP_*_Grey`, `Dodge_*`).
- **Assessment:** Renaming third-party assets creates high regression risk across anim sequences and animation blueprints.
- **Rule:** Retain original vendor names within pack folders.
