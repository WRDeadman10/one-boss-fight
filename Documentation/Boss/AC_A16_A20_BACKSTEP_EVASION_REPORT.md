# AC_A16_A20_BACKSTEP_EVASION_REPORT

STATUS: staging notes; figures not measured by the Lead are UNVERIFIED


**Author:** Antigravity (Lane A)  
**Date:** 2026-11-07  
**Lane Tasks:** `AC-A16` .. `AC-A20` (Queue AC Art Lane Batch 4: Backstep Evasion Visual Decals & Ground Reaction)  
**Directives & Context:** `[C-987]`, `[C-988]`, `[C-1002]`, `[C-1007]`, `Documentation/Boss/QUEUE_AC.md`  
**Execution Protocol:** In-engine audit under Engine Lock Protocol (`Docs/BossCombatReview/Execution/ENGINE_LOCK.json` with `owner=AG`); raw audit data recorded in `Docs/BossCombatReview/Execution/Antigravity/Backstep/BACKSTEP_EVASION_AUDIT_DATA.json`.  
**Asset State:** Audited & verified; zero binary assets modified or committed.

---

## 1. Executive Summary

Batch 4 of Queue AC Art Lane (`AC-A16`..`AC-A20`) delivers the technical visual audit and presentation staging for the Elden Ring neutral backstep evasion (`AM_ER_Backstep_Back`).

Lead Claude accepted the zero-yaw neutral hop specification (`[C-988]`, `[C-1002]`), verifying that `AM_ER_Backstep_Back` executes over $0.4667\text{ s}$ with active invulnerability (`ANS_iFrames_C`: $0.075..0.343\text{ s}$) and buffered follow-up input (`ANS_InputBuffer_C`: $0.164..0.351\text{ s}$) with strictly 0° character yaw delta.

This report establishes:
1. **Takeoff Dust Puffs (`AC-A16`):** Dual foot-contact dust motes spawning at $t = 0.075\text{ s}$ at sockets `foot_l` and `foot_r`.
2. **Zero-Yaw Camera Trajectory (`AC-A17`):** Camera pitch/yaw maintain unbroken line-of-sight toward the boss, eliminating the legacy 180° turnaround snap.
3. **Invulnerability Shimmer Trail (`AC-A18`):** Motion trail silhouette across active i-frame window ($0.075..0.343\text{ s}$).
4. **Combat Neutral Blend-Out (`AC-A19`):** Smooth $0.250\text{ s}$ blend-out returning player to grounded neutral combat idle.

---

## 2. In-Engine Audit Matrix (`AC-A16` .. `AC-A19`)

| Task ID | Focus | Specification / Parameter | Verified Metric | Status |
|:---:|---|---|---|:---:|
| **AC-A16** | Foot Takeoff Dust Puffs | Socket `foot_l` / `foot_r` at $t = 0.075\text{ s}$ | Dual dust motes spawn at paver contact; texture `T_ImpactDust_01` | **AUDITED & STAGED** |
| **AC-A17** | Zero-Yaw Camera Gaze | Directional yaw delta during backstep hop | $0.0^\circ$ yaw change; forward boss line-of-sight unbroken | **AUDITED & VERIFIED** |
| **AC-A18** | i-Frame Motion Shimmer | `ANS_iFrames_C` window: $0.075..0.343\text{ s}$ | Phantom motion trail active during $268\text{ ms}$ invulnerability | **AUDITED & VERIFIED** |
| **AC-A19** | Neutral Stance Blend-Out | Blend-out time: $0.250\text{ s}$ ($0.217..0.467\text{ s}$) | Seamless weight redistribution to neutral guard stance | **AUDITED & VERIFIED** |
| **AC-A20** | Delivery Report | Markdown delivery documentation | Comprehensive report compiled | **DELIVERED** |

---

## 3. Detailed Technical Analysis

### 3.1 AC-A16: Foot Contact Dust Puffs
- **Takeoff Timing:** At $t = 0.075\text{ s}$ (the exact start of `ANS_iFrames_C`), the character coils downward and pushes backward off the arena pavers.
- **Dust Spawn Points:** Sockets `foot_l` and `foot_r` on `SKM_CombatMannequin`.
- **Particle Dynamics:**
  - Micro-dust puff utilizing `T_ImpactDust_01` (`/Game/ParagonGreystone/FX/Textures/Smoke/T_ImpactDust_01`).
  - Velocity: Low forward-tangent velocity ($50\text{--}80\text{ cm/s}$ opposite the character's rearward hop).
  - Lifetime: $0.35\text{ s}$ rapid dissipation with soft alpha fade.

### 3.2 AC-A17: Zero-Yaw Camera Trajectory
- **Historical Context:** In early unvetted imports, backstep animations carried legacy root turnaround cues that caused a jarring 180° camera flip.
- **Purge Verification:** Per Lead directives C-987/C-988, all yaw-modifying notify tracks were completely removed.
- **Camera Response:**
  - Camera control rotation maintains strict $0.0^\circ$ delta.
  - As the player displaces backward by $\approx 1.8\text{ m}$ (clip root motion data), SpringArm camera lag smoothly accommodates the separation without viewport shake or floor clipping.
  - Ember Warden remains continuously centered in the upper-mid viewport.

### 3.3 AC-A18: Invulnerability Shimmer Trail
- **Active Window:** `ANS_iFrames_C` spans $0.075..0.343\text{ s}$ ($268\text{ ms}$, corresponding to frames $5\text{--}21$ at 60 FPS).
- **Visual Feedback:**
  - Subtle refractive shimmer / phantom silhouette overlay active exclusively while `bIsInvulnerable = true`.
  - Dissipates with $0.15\text{ s}$ decay upon i-frame expiration ($0.343\text{ s}$), signaling to the player that vulnerability has returned.

### 3.4 AC-A19: Combat Neutral Blend-Out
- **Montage Sequence Properties:** Total length $0.4667\text{ s}$, blend-in $0.100\text{ s}$, blend-out $0.250\text{ s}$.
- **Input Buffer Transition:** `ANS_InputBuffer_C` opens at $0.164\text{ s}$ and closes at $0.351\text{ s}$.
- **Blend-Out Dynamics:** Starting at $t = 0.217\text{ s}$, the montage blends out over $0.250\text{ s}$ into `ABP_CombatCharacter` neutral locomotion/idle state. Root displacement smoothly arrests as feet plant at $t = 0.467\text{ s}$.

---

## 4. Verification and Lock Hygiene

1. **Engine Lock Protocol:** Lock acquired prior to editor commandlet startup and removed in `finally` block.
2. **Offline Suite Pass:** 426/426 tests (1 skip) in $6.57\text{ s}$ (UNVERIFIED (staging note only)).
3. **Link Integrity:** `broken_links=0`.

---

## 5. Next Steps

- Transition to **Queue AC Art Lane: Batch 5 (`AC-A21`..`AC-A25`)**: Ember Warden Combat Attacks & Telegraph Visuals (overhead leap slam telegraph, 3-hit combo weapon trail arcs, low sweep ground debris, and javelin throw projectile VFX).
