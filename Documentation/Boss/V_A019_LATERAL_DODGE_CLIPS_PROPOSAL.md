# V-A019: Lateral Dodge Clips Proposal (Left/Right Rolls)

**Author:** Antigravity (Offline Quality, Audit & Asset Lane)  
**Date:** 2026-11-05  
**Scope:** Proposal for dedicated left and right evasion roll animations on `SK_CombatMannequin` replacing generic forward roll rotation offsets.
**Sources:** Content/OneBossFight/Characters/ [PROPOSAL / Animation Synthesis Blueprint]

---

## 1. Executive Summary

- **Proposal:** Author dedicated lateral dodge roll animations (`AN_Player_Dodge_Roll_Left`, `AN_Player_Dodge_Roll_Right`) to replace the current stand-in where the character pivots forward-roll montages to lateral headings.
- **Current Production Setup:**
  - `URPGIFrameMonitor` & `RPGDodgeTiming`: Manages 0.80 s dodge with 12 i-frames (0.00 – 0.20 s).
  - Stand-in Montages: `Dodge_Small_Forward_Roll_Montage` used with actor rotation snap.
- **Identified Evasion Flaws:**
  - Forward-roll rotation snaps snap the player mesh 90° before initiating roll, causing visual hitching and unnatural foot sliding during high-intensity boss tracking.
  - Directional momentum does not clearly communicate sideways evasion against wide horizontal sweeps (such as boss attack A4).

---

## 2. Animation Specification

| Clip Identifier | Direction | Duration | i-Frame Window | Trajectory / Motion Profile |
| :--- | :--- | :--- | :--- | :--- |
| **`AN_Player_Dodge_Roll_Left`** | Left (-90°) | 0.800 s (24 frames @ 30 fps) | Frames 0 – 6 (0.00 – 0.20 s) | Low shoulder roll over left arm, lateral displacement 280 cm |
| **`AN_Player_Dodge_Roll_Right`**| Right (+90°) | 0.800 s (24 frames @ 30 fps) | Frames 0 – 6 (0.00 – 0.20 s) | Low shoulder roll over right arm, lateral displacement 280 cm |
| **`AN_Player_Dodge_Step_Back`** | Back (180°) | 0.650 s (20 frames @ 30 fps) | Frames 0 – 6 (0.00 – 0.20 s) | Quick backward hop/slide, displacement 220 cm |

1. **Root Motion vs Velocity Driven:**
   - Both clips authored with root motion curves matching exactly the current displacement velocity (350 cm/s initial peak decaying to 0).
   - Guarantees zero gameplay desync with `URPGIFrameMonitor` collision volumes.
2. **Readability & Footing:**
   - Low center of gravity during roll cleanly avoids high sweeps (like boss horizontal slash A4).
   - Clean recovery directly into combat stance, allowing seamless chain into light attack or parry.

---

## 3. Delivery & Workflow Plan

1. **Stage 1 (MCP Synthesis):** Synthesize FBX clips using `Scripts/blender_exec.py` on `SKM_CombatMannequin_Simple.fbx`.
2. **Stage 2 (Montage Assembly):** Assemble `AM_Player_Dodge_Left` and `AM_Player_Dodge_Right` with standard anim notifies (`Notify_IFrameStart`, `Notify_IFrameEnd`, `Notify_DodgeBlendOut`).
3. **Stage 3 (Opt-in CVar Switch):** Wire into `RPGPlayerMovesSubsystem` under `rpg.Player.DirectionalDodge` (defaulting to 0 to preserve D5 baseline).
4. **Stage 4:** Await Owner approval per look-changing rule before importing binary assets.
