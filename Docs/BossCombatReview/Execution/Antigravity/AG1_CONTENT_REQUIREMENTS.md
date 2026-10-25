# AG-1: Content Requirements for the Eight Former-N/A Rows

**Document ID:** `AG1_CONTENT_REQUIREMENTS` (Rev 01)  
**Date:** 2026-10-25  
**Author:** Antigravity (Accountable Visual & Technical Animation Investigator)  
**Addressed to:** Claude (Technical Lead & Editor Owner), Codex GPT-6 Astra (Technical Reviewer & Data Architect)  
**Context & Authority:** Task AG-1 of Work Order 01 (`ANTIGRAVITY_WORK_ORDER_01.md`). Conforms to Owner directive (all 83 rows required, no N/A). Aligned with Codex `D05_CONDITIONAL_ROWS_COSTING.md` and `D02_DATA_MODEL.md`.

---

## 1. Executive Summary & Scope

This specification defines the exact animation content, montage structure, notify markers (`AN_CombatEvent` / `ANS_CombatWindow`), coordinate offsets, visual/audio telegraphs, accessibility rules, and authoring effort estimates for the eight former-N/A rows.

```
+-----------+-----------------------------------+--------------------+-----------------------------+
| Row ID    | Feature Summary                   | Content Scope      | Authoring Effort / Size     |
+-----------+-----------------------------------+--------------------+-----------------------------+
| QA-008    | Server Authority / Multiplayer    | ZERO Content       | ZERO (Pure Systems/NetCode) |
| HIT-012   | Boss Grab Fail-Safe               | Paired Two-Actor   | LARGE (High Complexity)     |
| ANM-003   | Bounded Variable Hold             | Hold & Release Cue | MEDIUM                      |
| AWR-008   | Adaptive Memory Tells             | Visual/Audio Cues  | SMALL–MEDIUM (Additive)     |
| SEL-004   | Normalized Utility Selection      | Neutral Pacing     | SMALL (Locomotion Tuning)   |
| SEL-008   | Purposeful Fallback Behavior      | Pacing Walk/Stare  | SMALL–MEDIUM (1-2 Clips)    |
| ANM-006   | Bounded Motion Warping            | Root-Motion Travel | MEDIUM–LARGE (Root Motion)  |
| DEF-005   | Fair Boss Defenses (All 3)        | Guard, Parry, Dodge| LARGE (8+ Clips)            |
+-----------+-----------------------------------+--------------------+-----------------------------+
```

---

## 2. BOSS-QA-008: Server Authority and Multiplayer Proof

- **Content Requirements:** **STRICTLY ZERO**.
- **Explanation:** Server-client authority, RPC allocation, state replication, and time-sync reconciliation are pure engine/systems code (`Source/OneBossFight/`) and networking infrastructure. No new meshes, skeleton modifications, or standalone animation clips are required for networking.
- **Animation Contract:** Animation evaluation on remote clients consumes authoritative server start times and section epochs using existing project montages and the normalized timeline cache (`TimelineSpec` in D02).

---

## 3. BOSS-HIT-012: Boss Grab Fail-Safe

A paired, two-actor interactive sequence requiring synchronized animation for both Attacker (Boss) and Victim (Player / Pack Mannequin).

### 3.1 Animation Assets Required
1. **Attacker Montage:** `AN_Boss01_Grab_Attack`
   - Sections: `Windup` $\to$ `CaptureWindow` $\to$ `HitHold` $\to$ `Slam` $\to$ `Recovery` (or branch to `MissRecovery`).
2. **Victim Montage:** `AN_Player_Grab_Victim`
   - Sections: `Caught` $\to$ `HeldStruggle` $\to$ `Slammed` $\to$ `GetUp`.

### 3.2 Move Timing Card (Attacker Frame)
- **Windup:** $0.000\text{ s}$ to $0.550\text{ s}$ ($550\text{ ms}$). Boss sinks into low stance, dorsal brazier surges crimson, left hand draws back.
- **Commit Marker:** $0.450\text{ s}$ ($100\text{ ms}$ before capture opens; rotational tracking freezes).
- **Active Capture Window:** $0.550\text{ s}$ to $0.750\text{ s}$ ($200\text{ ms}$). Forward lunge ($180\text{ cm}$ reach, $45^\circ$ forward cone).
- **Paired Hit Hold:** $0.750\text{ s}$ to $1.350\text{ s}$ ($600\text{ ms}$). Boss lifts victim by chest/throat.
- **Slam / Damage Strike:** $1.350\text{ s}$ to $1.650\text{ s}$ ($300\text{ ms}$). High-velocity downward smash to arena floor. Damage event fires at $1.500\text{ s}$.
- **Release Seam:** $1.650\text{ s}$ (Victim released to ragdoll or `GetUp` animation; collision safely separated).
- **Recovery (Success):** $1.650\text{ s}$ to $2.400\text{ s}$ ($750\text{ ms}$). Boss straightens and re-grips greatsword.
- **Recovery (Miss / Whiff):** $0.750\text{ s}$ to $1.850\text{ s}$ ($1100\text{ ms}$). Boss overextends forward onto one knee. **High-punish window for player**.
- **Blend In / Out:** $0.150\text{ s}$ / $0.250\text{ s}$.

### 3.3 Notify Markers (D02 Architecture)
- `ANS_CombatWindow` [Telegraph] ($0.000\text{--}0.550\text{ s}$)
- `AN_CombatEvent` [Commit] ($0.450\text{ s}$)
- `ANS_CombatWindow` [CaptureVolume] ($0.550\text{--}0.750\text{ s}$)
- `AN_CombatEvent` [PairedAlign] ($0.750\text{ s}$) $\implies$ Locks victim transform to grab socket.
- `AN_CombatEvent` [DamageImpact] ($1.500\text{ s}$) $\implies$ Single authoritative damage application.
- `AN_CombatEvent` [ReleaseVictim] ($1.650\text{ s}$) $\implies$ Restores player input/movement ownership.
- `AN_CombatEvent` [RecoveryEnd] ($2.400\text{ s}$ on hit / $1.850\text{ s}$ on whiff).

### 3.4 Sockets, Offsets & Coordinate Contracts
- **Grab Attachment Point:** Boss left palm / wrist socket: `SOCKET_Grab_Victim` (Local offset: `(X=15.0, Y=0.0, Z=0.0)` from `hand_l`).
- **Victim Alignment Offset:** Victim Pelvis attaches at $Z = 120\text{ cm}$ height, facing $+180^\circ$ toward boss chest.
- **Release Placement Safety:** Forward trace of $150\text{ cm}$ along arena floor ensures victim is not released inside pillars, walls, or kill planes.

### 3.5 Telegraph, VFX, Audio & Readability Cues
- **Telegraph Cue:** Bright crimson rune flare around boss left gauntlet; deep sub-bass vacuum sound cue during windup ($0.000\text{--}0.450\text{ s}$).
- **Accessibility:** Audio high-pass whine paired with visual silhouette flash ensures readability without relying purely on color. Unblockable grab icon appears above boss head.
- **Impact VFX:** Massive shockwave dust ring and floor fracture decal at slam impact ($1.500\text{ s}$).

### 3.6 Skeleton & Retarget Assumptions
- Attacker: `SK_Boss01_Skeleton` (pack boss skeleton).
- Victim: Standard UE Mannequin skeleton (`SK_Mannequin`).
- Retargeting: Paired root offsets must be authored relative to world center `(0, 0, 0)` in Blender/Maya and exported as synchronized paired FBXs.

### 3.7 Authoring Effort Estimate: **LARGE**
- **Reason:** Requires authoring two perfectly synchronized animations (attacker + victim) with precise contact constraints, authoring a severe miss/overextension recovery clip, setting up paired socket transforms, and establishing a safe floor-separation boundary.

---

## 4. BOSS-ANM-003: Bounded Variable Hold

Provides variable windup delays to defeat rote roll spam, without indefinite or unfair tracking.

### 4.1 Content Architecture: Discrete Variants vs Looping Seam
To comply with Codex D05 and D02, the variable hold is authored as a single master montage containing three distinct execution paths selected deterministically at windup start:
- **Variant A (Fast Release):** $0.350\text{ s}$ hold.
- **Variant B (Standard Release):** $0.650\text{ s}$ hold.
- **Variant C (Extended Hold):** $1.050\text{ s}$ hold.

*(Alternative conformant implementation: A looping `ApexHold` section with deterministic loop counter [1 to 3 cycles of $0.350\text{ s}$], bounded by a strict watchdog timer).*

### 4.2 Move Timing Card (Applied to Overhead Slam / Heavy Smash)
- **Raise / Windup:** $0.000\text{ s}$ to $0.450\text{ s}$ ($450\text{ ms}$). Boss raises sword to high overhead apex.
- **Commit Marker:** $0.400\text{ s}$ (Heading lock engaged).
- **Variable Apex Hold:** $0.450\text{ s}$ to $T_{\text{release}}$ ($350\text{ to }1050\text{ ms}$). Weapon held high with tense, vibrating poise.
- **Release Cue (CRITICAL FOR FAIRNESS):** Exactly **$150\text{ ms}$ prior to downward strike initiation**. An unmistakable visual burst and audio snap signals the drop.
- **Downward Strike (Active):** $T_{\text{release}}$ to $T_{\text{release}} + 0.220\text{ s}$ ($220\text{ ms}$).
- **Recovery:** $0.700\text{ s}$ after active window.
- **Blend In / Out:** $0.150\text{ s}$ / $0.200\text{ s}$.

### 4.3 Notify Markers (D02 Architecture)
- `ANS_CombatWindow` [Telegraph] ($0.000\text{ s}$ to $T_{\text{release}}$)
- `AN_CombatEvent` [Commit] ($0.400\text{ s}$)
- `ANS_CombatWindow` [HoldInterval] ($0.450\text{ s}$ to $T_{\text{release}}$)
- `AN_CombatEvent` [ReleaseCue] ($T_{\text{release}} - 0.150\text{ s}$) $\implies$ Authoritative telegraph for the strike release.
- `ANS_CombatWindow` [ActiveDamage] ($T_{\text{release}}$ for $0.220\text{ s}$)
- `AN_CombatEvent` [RecoveryEnd] (End of recovery)

### 4.4 Telegraph, VFX & Readability Cues
- **Hold Cue:** Heavy blade hums with gathering embers; blade tip micro-shakes.
- **Release Cue:** Sudden bright flash along the blade fuller and a crisp metallic "schwing" chime $150\text{ ms}$ before motion starts, giving the human player reactive dodge counterplay.

### 4.5 Skeleton & Effort Estimate: **MEDIUM**
- **Skeleton:** `SK_Boss01_Skeleton`.
- **Reason:** Requires authoring stable, non-popping apex loop seams and a distinct $150\text{ ms}$ release pre-cue transition, but involves only a single character mesh.

---

## 5. BOSS-ANM-006: Bounded Motion Warping

A directional travel attack that uses root motion translation with strictly clamped early-window warping, closing distance to the player without unreadable teleports.

### 5.1 Animation Assets Required
- Montage: `AN_Boss01_LungeTravel_Montage` (Single clip or 3-part: `Anticipation`, `RootTravel`, `ImpactSlash`, `Recovery`).
- Root Motion: Authored with nominal forward root displacement of **$450.0\text{ cm}$** along the +Y/+X forward axis over $0.400\text{ s}$.

### 5.2 Move Timing Card
- **Anticipation (Windup):** $0.000\text{ s}$ to $0.350\text{ s}$ ($350\text{ ms}$). Boss coils legs and leans forward.
- **Warp Window (Early Only):** $0.350\text{ s}$ to $0.600\text{ s}$ ($250\text{ ms}$). Motion warping adjusts translation/yaw toward player position.
- **Commit Marker:** $0.550\text{ s}$ ($50\text{ ms}$ before travel completes). **Warp translation and rotation strictly freeze**.
- **Strike Execution (Active Window):** $0.650\text{ s}$ to $0.850\text{ s}$ ($200\text{ ms}$). Greatsword sweep at destination.
- **Recovery:** $0.850\text{ s}$ to $1.500\text{ s}$ ($650\text{ ms}$).
- **Blend In / Out:** $0.200\text{ s}$ / $0.200\text{ s}$.

### 5.3 Warping Clamps & Constraints (Data Contract)
- **Maximum Distance Warp Scale:** $0.5\text{x}$ to $1.5\text{x}$ (Min travel $225\text{ cm}$, Max travel $675\text{ cm}$).
- **Maximum Rotation Warp:** $\pm 45.0^\circ$ total yaw adjustment across the window (Rate capped at $180^\circ/\text{s}$).
- **Vertical Clamping:** $Z$-warp strictly clamped to ground surface ($\pm 50\text{ cm}$ max step).
- **Prohibited:** No warping during or after the active damage window ($0.650\text{--}0.850\text{ s}$).

### 5.4 Notify Markers (D02 Architecture)
- `ANS_CombatWindow` [Telegraph] ($0.000\text{--}0.350\text{ s}$)
- `ANS_CombatWindow` [MotionWarp] ($0.350\text{--}0.550\text{ s}$, WindowId: `Warp_EarlyTravel`)
- `AN_CombatEvent` [Commit] ($0.550\text{ s}$)
- `ANS_CombatWindow` [ActiveDamage] ($0.650\text{--}0.850\text{ s}$)
- `AN_CombatEvent` [RecoveryEnd] ($1.500\text{ s}$)

### 5.5 Telegraph, VFX & Readability Cues
- **Trail VFX:** Dark ember wake trailing the boss root during the dash.
- **Audio Cue:** Heavy stone-scraping launch thud at $0.350\text{ s}$, rushing wind whoosh during dash.

### 5.6 Skeleton & Effort Estimate: **MEDIUM–LARGE**
- **Skeleton:** `SK_Boss01_Skeleton` with validated Root bone motion curves.
- **Reason:** Authoring clean root motion with proper foot contact curves to minimize visual sliding during non-warped playback, plus authoring boundary fallbacks for blocked paths.

---

## 6. BOSS-DEF-005: Fair Boss Defenses (Guard, Parry, Dodge)

Full compliance with DEF-005 requires all **three defense families** to be supported with readable animations and fair counterplay windows.

```
+--------------------+---------------------------------------+-----------------------------+
| Defense Family     | Animation Clips Needed                | Punishability / Counterplay |
+--------------------+---------------------------------------+-----------------------------+
| Family A: Guard    | Enter, Loop, HitReact, Break, Exit    | Guard Break Stagger (2.0s)  |
| Family B: Parry    | Stance Startup, Deflect, CounterSlash | Missed Parry Recovery (0.8s)|
| Family C: Dodge    | Backstep Hop, Lateral Hop (L/R)       | Post-IFrame Recovery (0.3s) |
+--------------------+---------------------------------------+-----------------------------+
```

### 6.1 Family A: Directional Guard (Block)
- **Clips:**
  1. `AN_Boss01_Guard_Enter` ($150\text{ ms}$): Brings broad blade horizontally across torso.
  2. `AN_Boss01_Guard_Loop`: Idle guarding stance (frontal $120^\circ$ protection cone).
  3. `AN_Boss01_Guard_HitReact` ($300\text{ ms}$): Recoil absorption upon blocking player attack.
  4. `AN_Boss01_Guard_Break` ($2.000\text{ s}$): Severe posture break. Greatsword forced aside, boss stumbles backward onto knee. **Massive player riposte window**.
  5. `AN_Boss01_Guard_Exit` ($200\text{ ms}$): Returns to combat neutral.
- **Notifies:** `ANS_CombatWindow` [GuardWindow], `AN_CombatEvent` [GuardBreakVulnerable].
- **Effort:** **MEDIUM–LARGE**.

### 6.2 Family B: Timed Parry (Deflect & Riposte)
- **Clips:**
  1. `AN_Boss01_Parry_Startup` ($180\text{ ms}$): Quick circular flourish raising blade into high parry guard.
  2. `AN_Boss01_Parry_Deflect` ($250\text{ ms}$): Violent deflection stroke sending player weapon flying.
  3. `AN_Boss01_Parry_CounterSlash` ($500\text{ ms}$): Immediate horizontal riposte strike.
  4. `AN_Boss01_Parry_Whiff` ($800\text{ ms}$): Stumble if no player attack hits the parry window. **Punishable window**.
- **Notifies:** `ANS_CombatWindow` [ParryWindow] ($100\text{--}280\text{ ms}$), `AN_CombatEvent` [DeflectImpact], `ANS_CombatWindow` [ActiveDamage] (CounterSlash).
- **Readability:** Sharp high-frequency blade ring and golden flash at deflection point.
- **Effort:** **MEDIUM**.

### 6.3 Family C: Directional Dodge (Evasive Hops)
- **Clips:**
  1. `AN_Boss01_Dodge_Back` ($500\text{ ms}$): Rapid backward hop ($300\text{ cm}$ displacement).
  2. `AN_Boss01_Dodge_Left` ($450\text{ ms}$): Lateral hop left ($220\text{ cm}$ displacement).
  3. `AN_Boss01_Dodge_Right` ($450\text{ ms}$): Lateral hop right ($220\text{ cm}$ displacement).
- **Timing & IFrames:**
  - Startup (vulnerable): $0.000\text{--}0.080\text{ s}$ ($80\text{ ms}$).
  - Protected I-Frame Window: $0.080\text{--}0.320\text{ s}$ ($240\text{ ms}$).
  - Recovery (vulnerable, no turn): $0.320\text{--}0.500\text{ s}$ ($180\text{ ms}$).
- **Notifies:** `ANS_CombatWindow` [IFrameWindow], `AN_CombatEvent` [RecoveryEnd].
- **Effort:** **MEDIUM**.

### 6.4 Total DEF-005 Authoring Effort: **LARGE**
- **Reason:** Authoring 8 distinct animation clips across 3 distinct mechanical families, each requiring strict timing cards, posture interaction states, and hit reaction physics.

---

## 7. BOSS-AWR-008: Adaptive Memory Tells & Feedback

When the boss adapts its utility weights based on accumulated player habits (e.g. anti-roll sweeps, anti-heal punishes), clear visual and auditory feedback must inform the player.

### 7.1 Content Requirements
- **Additive Animation Layer:** `AN_Boss01_Adapt_Tell` ($400\text{ ms}$ additive upper-body head tilt and shoulder flare).
- **VFX Parameter Curves:**
  * Dorsal brazier flame intensity and color shift (Orange $\to$ Fiery White) driven by an engine scalar parameter `EmberArousal` ($0.0\text{ to }1.0$).
  * Eye socket particle glow trail scales with adaptation tier.
- **Audio Feedback:** Resonant low-frequency spectral whisper / hum when adaptation threshold triggers.
- **Authoring Effort:** **SMALL–MEDIUM** (Additive blend pose + VFX parameter bindings).

---

## 8. BOSS-SEL-004 & BOSS-SEL-008: Selection & Purposeful Fallback

### 8.1 SEL-004 (Normalized Utility Presentation)
- **Content Scope:** Ensure locomotion transitions between utility-selected attacks are smooth and readable.
- **Clips:**
  * Clean $90^\circ$ and $180^\circ$ in-place turns (`AN_Boss01_Turn_L90`, `AN_Boss01_Turn_R90`) to prevent visual foot skating when pivoting between targets.
- **Effort:** **SMALL**.

### 8.2 SEL-008 (Purposeful Empty-Pool Fallback)
When all attacks are on cooldown or target is temporarily unreachable, the boss executes an intentional pacing action rather than stalling or twitching.
- **Clips:**
  1. `AN_Boss01_Fallback_PacingWalk` ($2.000\text{ s}$ loop): Slow, menacing lateral circle-strafe with greatsword held low, eyes locked on player.
  2. `AN_Boss01_Fallback_Flourish` ($1.500\text{ s}$): Greatsword tip drags across floor tiles with spark shower, resetting combat spacing.
- **Timing:** Bounded task duration: $1.500\text{ to }3.000\text{ s}$. Fully interruptible if player engages.
- **Effort:** **SMALL–MEDIUM**.

---

## 9. Alignment with Codex D05 Costing

| Requirement | Codex D05 Engineering Size | Antigravity Content Effort | Alignment & Agreement Status |
| :--- | :--- | :--- | :--- |
| **QA-008** | Large (Highest Uncertainty) | **ZERO** | **AGREED.** Pure systems/network code. No art assets. |
| **HIT-012** | Large | **LARGE** | **AGREED.** Paired two-actor capture, alignment, and release. |
| **ANM-003** | Medium | **MEDIUM** | **AGREED.** Variable apex hold variants and mandatory release cues. |
| **AWR-008** | Medium | **SMALL–MEDIUM** | **AGREED.** Additive tells and VFX parameter curves. |
| **SEL-004** | Medium–Large | **SMALL** | **AGREED.** Selection logic is code; content is clean turn transitions. |
| **SEL-008** | Small–Medium | **SMALL–MEDIUM** | **AGREED.** 1-2 pacing walk / flourish clips. |
| **ANM-006** | Medium–Large | **MEDIUM–LARGE** | **AGREED.** Root motion lunge with clamped early warp window. |
| **DEF-005** | Large | **LARGE** | **AGREED.** All 3 defense families require 8+ animation clips. |

**Antigravity fully supports and adopts the content assumptions of Codex D05 without exception.**
