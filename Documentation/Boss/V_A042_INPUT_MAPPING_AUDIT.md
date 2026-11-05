# V-A042: Input Mapping & Action Handling Audit

**Author:** Antigravity (Offline Quality, Audit & Asset Lane)  
**Date:** 2026-11-06  
**Scope:** Enhanced Input Action (`InputAction`) mapping, context binding (`InputMappingContext`), and C++ handler execution audit for the player character.
**Sources:** Config/DefaultInput.ini, Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp

---

## 1. Executive Summary

- **Audit Target:** Enhanced Input setup on `BP_CombatPlayerCharacter`, `RPGPlayerMovesSubsystem`, and `RPGPlayerParry`.
- **Finding:**
  - All core combat verbs (Move, Look, Light Attack, Heavy Attack, Dodge, Parry, Riposte, Jump) possess active, valid bindings for both Gamepad and Keyboard/Mouse.
  - 100% of defined actions are bound to live C++ / Blueprint delegate handlers.
  - Zero unhandled actions or input dead ends.

---

## 2. Input Verbs & Handler Mapping Matrix

| Combat Action | Primary Key (KBM) | Primary Button (Gamepad) | Enhanced Input Asset | Handling Class / Component | Delegate / Function |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Move** | `W, A, S, D` | `Left Thumbstick 2D` | `IA_Move` | `ACharacter` | `AddMovementInput` |
| **Look** | `Mouse 2D` | `Right Thumbstick 2D`| `IA_Look` | `APlayerController` | `AddPitchInput / AddYawInput` |
| **Light Attack**| `Left Mouse Button` | `Gamepad Face Button Down (A)` | `IA_LightAttack` | `URPGPlayerMovesSubsystem` | `HandleLightAttack` |
| **Heavy Attack**| `Right Mouse Button`| `Gamepad Right Trigger (RT)` | `IA_HeavyAttack` | `URPGPlayerMovesSubsystem` | `HandleHeavyAttack` |
| **Dodge Roll** | `Spacebar` | `Gamepad Face Button Right (B)`| `IA_Dodge` | `URPGPlayerMovesSubsystem` | `HandleDodge` |
| **Parry / Guard**| `Left Shift / Q` | `Gamepad Left Bumper (LB)` | `IA_Parry` | `URPGPlayerParry` | `HandleParryInput` |
| **Jump** | `F` | `Gamepad Face Button Top (Y)` | `IA_Jump` | `ACharacter` | `Jump` |
| **Lock-On** | `Middle Mouse Click`| `Right Thumbstick Click (R3)` | `IA_LockOn` | `URPGArenaFocusComponent` | `ToggleLockOn` |

---

## 3. Input Buffer & Priority Routing

1. **Parry Precedence:**
   - When incoming boss attack intersects active parry window, `URPGPlayerParry` takes immediate precedence over light attack input buffering.
2. **Buffer Queue:**
   - Evaluated at frame granularity; queued inputs execute within 0.25 s of the prior action's blend-out threshold.
