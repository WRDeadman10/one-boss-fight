# V-A041: Configuration Dead Keys Audit (`Config/Default*.ini`)

**Author:** Antigravity (Offline Quality, Audit & Asset Lane)  
**Date:** 2026-11-06  
**Scope:** Systematic review of all `Config/Default*.ini` files for obsolete properties, dead legacy bindings, and stale template remnants.

---

## 1. Executive Summary

- **Audit Target:** `DefaultEngine.ini`, `DefaultGame.ini`, `DefaultInput.ini`, `DefaultEditor.ini`, `DefaultGameplayTags.ini`.
- **Finding:**
  - `DefaultGame.ini` and `DefaultEngine.ini` are well-maintained with authoritative cook coverage and rendering CVars.
  - **Dead Key Remnants Identified:**
    1. **`DefaultInput.ini`:** 38 legacy VR controller axis bindings (`Vive_*`, `MixedReality_*`, `OculusTouch_*`, `ValveIndex_*`) inherited from third-party templates. The project uses Enhanced Input (`DefaultPlayerInputClass=/Script/EnhancedInput.EnhancedPlayerInput`), rendering these axes completely inert.
    2. **`DefaultGame.ini`:** `[StartupActions]` section referencing `StarterContent.upack`. Starter content was purged from the repo during milestone M1; this key is a dead engine bootstrap artifact.

---

## 2. Dead Keys Inventory

| Config File | Section Header | Dead / Stale Key | Purpose / Reason for Redundancy | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| **`DefaultInput.ini`** | `[/Script/Engine.InputSettings]` | `+AxisConfig=(AxisKeyName="Vive_*")` (6 entries) | Dead VR motion controller axes; no VR support in Soulslike duel. | Propose removal in future config cleanup. |
| **`DefaultInput.ini`** | `[/Script/Engine.InputSettings]` | `+AxisConfig=(AxisKeyName="MixedReality_*")` (10 entries) | Dead Windows MR axes. | Propose removal in future config cleanup. |
| **`DefaultInput.ini`** | `[/Script/Engine.InputSettings]` | `+AxisConfig=(AxisKeyName="OculusTouch_*")` (8 entries) | Dead Oculus Touch axes. | Propose removal in future config cleanup. |
| **`DefaultInput.ini`** | `[/Script/Engine.InputSettings]` | `+AxisConfig=(AxisKeyName="ValveIndex_*")` (14 entries) | Dead Valve Index axes. | Propose removal in future config cleanup. |
| **`DefaultGame.ini`** | `[StartupActions]` | `InsertPack=(PackSource="StarterContent.upack",...)` | Remnant from UE project generation; StarterContent is not used or packaged. | Propose deprecation. |
| **`DefaultGame.ini`** | `[SectionsToSave]` | `+Section=StartupActions` | Saves the dead StartupActions section. | Propose deprecation. |

---

## 3. Active & Critical Config Protections

1. **`DirectoriesToAlwaysCook`:**
   - 28 explicit directory entries in `DefaultGame.ini` are strictly validated by `OneBossFight.Content.CookCoverage`.
   - Protects soft-referenced assets in `/Game/OneBossFight/` and `/Game/AdvancedARPGCombat/`.
2. **`bUseLegacyStartup=True`:**
   - Authoritative startup gate in `DefaultGame.ini` preserving strict D5 runtime parity.
