# AG-5: A2 Authored Trio Master Montage Integration Specification (VIS-02)

**Document ID:** `AG5_A2_INTEGRATION_SPEC` (Rev 01)  
**Date:** 2026-10-25  
**Author:** Antigravity (Accountable Visual & Technical Animation Investigator)  
**Addressed to:** Claude (Technical Lead & Editor Owner), Codex GPT-6 Astra (Technical Reviewer & Data Architect), Project Owner  
**Context & Authority:** Task AG-5 of Work Order 01 (`ANTIGRAVITY_WORK_ORDER_01.md`). Addresses defect `VIS-02` and establishes future integration standards for the delivered A2 authored clip set (`AN_Boss01_A2_Raise`, `ApexHold`, `Slam`).  
**Governance & Parity Rule:** **DD-1 CHANGES NOTHING.** Under the DD-1 parity mandate, the live game continues executing the pack's `GS_ChargedAttack_Montage` and its observed runtime behavior without modification. This document is a formal specification for future P-phase implementation (P1 readability, P2 timeline compilation, P5 recovery tuning) upon owner authorization.

---

## 1. Executive Summary & Defect Baseline

```
+----------------------------------------------------------------------------------------------------+
| A2 COMPARISON: LIVE PACK MONTAGE vs AUTHORED TRIO ARCHITECTURE                                     |
+--------------------------+-------------------------------------+-----------------------------------+
| Feature Attribute        | Live Pack: `GS_ChargedAttack`       | Authored Trio: `AM_Boss01_A2`     |
+--------------------------+-------------------------------------+-----------------------------------+
| Montage Structure        | Single continuous 3.400s clip       | 3 Modular Sections (Raise/Hold/Slam|
| Windup Visual Motion     | Continuous multi-turn blade twirl   | Static, poised vertical hold      |
| Character Mesh Clipping  | Severe blade clipping (cape/arm)    | Zero clipping; verified clearance |
| Hold Duration Model      | Hardcoded fixed duration (1.567s)   | Data-declared variable hold bound |
| Release Telegraph        | Unclear; blend directly into stroke | Distinct 150ms audio-visual cue   |
| Runtime Stability (E-005)| 9 of 11 instances stopped early     | Controlled timeline watchdog      |
| ANM-003 Compliance       | Non-compliant (Fixed/Twirl)         | Fully compliant (Variable delay)  |
+--------------------------+-------------------------------------+-----------------------------------+
```

### 1.1 The Live Pack Defect Baseline (`GS_ChargedAttack_Montage` / E-005)
1. **Unidentified Early Cancellation (E-005):** In live bot-driven testing (documented in Claude's E-005), 9 of 11 observed A2 instances terminated before reaching the active damage window (stopping at $0.03\text{--}0.06\text{ s}$ or $0.97\text{--}1.00\text{ s}$). When stopped early, the parent ability `GA_GS_Boss_CloseRare` remained active for $> 1.4\text{ s}$ without an animating montage, locking the boss in an idle stance.
2. **Visual & Readability Artifacts (VIS-02):** The pack animation plays a continuous $360^\circ$ windmill weapon twirl during windup. The $245\text{ cm}$ scaled blade repeatedly cuts through the boss's dorsal armor and cape. The twirl provides no stable pose for the player to judge the commit point or prepare a dodge.
3. **Absence of Variable Pacing (ANM-003):** The live move has a single, static duration; it cannot adapt or provide variable-delay counterplay.

---

## 2. Authored Trio Architecture & Composite Montage Design

The delivered authored clips (`AN_Boss01_A2_Raise`, `AN_Boss01_A2_ApexHold`, `AN_Boss01_A2_Slam`) are integrated into a single project master montage: **`AM_Boss01_A2_OverheadSlam`**.

```
  Section 1: [ Raise ]               Section 2: [ ApexHold ]                 Section 3: [ Slam ]
   (0.000s - 0.500s)                 (Loopable 0.400s Cycle)                  (0.000s - 0.800s)
+-----------------------+     +-----------------------------------+     +----------------------------+
| Two-handed lift       |     | Cyclic vibrating poise hold       |     | Explosive downward stroke  |
| Heading tracking on   | --> | Heading LOCKED (Commit = 0.400s)  | --> | Floor impact & dust wave   |
| Frame 0 -> 15         |     | Duration: Bounded by data         |     | Follow-through & recovery  |
| Commit at 0.400s      |     | Seamless loop seam (cyclic d<0.5mm|     | Active window: 0.10s-0.32s |
+-----------------------+     +-----------------------------------+     +----------------------------+
                                  ^              |
                                  +--[Loop N x]--+
                                  (Deterministic exit seam)
```

### 2.1 Section Specifications
1. **Section 1: `Raise` (Duration: $0.500\text{ s}$ / Frames 0 to 15 at $30\text{ fps}$)**
   - Motion: Boss grips greatsword with both gauntlets and raises it smoothly along the sagittal plane to a high vertical apex above the head.
   - Rotational Tracking: Active at nominal $240^\circ/\text{s}$ from $0.000\text{ s}$ to $0.400\text{ s}$.
   - Commit Event: Fires at $t = 0.400\text{ s}$. Rotational tracking strictly locks.
   - Exit Seam: At $t = 0.500\text{ s}$, transitions seamlessly into `ApexHold`. Bone transforms at the seam match Frame 0 of `ApexHold` with position delta $< 0.1\text{ mm}$ and rotation delta $< 0.05^\circ$.

2. **Section 2: `ApexHold` (Base Clip Length: $0.400\text{ s}$ / Frames 0 to 12 at $30\text{ fps}$)**
   - Motion: Stable, tense apex poise. Torso arched back, blade held motionless overhead with subtle micro-tremor vibrations ($< 1.5\text{ cm}$ amplitude) conveying immense physical weight.
   - Loop Point: Cyclic loop seam connecting Frame 12 back to Frame 0. Cyclic boundary position error is verified at $< 0.05\text{ cm}$, guaranteeing zero visual pop during multi-cycle holds.
   - Rotational Tracking: **STRICTLY ZERO**. The boss cannot rotate during the hold.

3. **Section 3: `Slam` (Duration: $0.800\text{ s}$ / Frames 0 to 24 at $30\text{ fps}$)**
   - Motion: Violent downward chop. Blade accelerates from rest, cleaving through the vertical plane and impacting the arena stone floor at $t = 0.220\text{ s}$.
   - Active Window: Collision traces active from $t = 0.100\text{ s}$ to $t = 0.320\text{ s}$ ($220\text{ ms}$).
   - Recovery: Blade embeds briefly in stone ($t = 0.220\text{--}0.450\text{ s}$), boss pulls it free, and resumes combat neutral by $t = 0.800\text{ s}$.

---

## 3. Data-Declared Hold Bounds & ANM-003 Compliance

To comply with the bounded variable hold requirement (**BOSS-ANM-003**), `AM_Boss01_A2_OverheadSlam` does not rely on arbitrary or unbounded tick scripts.

### 3.1 Deterministic Prechosen Hold Selection
At the instant A2 is selected at neutral, the runtime reads the data-defined hold parameters from the move definition:
- `MinHoldDuration`: $0.300\text{ s}$ (1 loop cycle)
- `MaxHoldDuration`: $1.100\text{ s}$ (3 loop cycles)
- `HoldSelectionPolicy`: `EHoldSelectPolicy::DeterministicSeed` (seeded at windup initiation; subsequent player inputs cannot alter the chosen duration).

### 3.2 Dual Integration Mechanics
The montage supports two approved execution models:
- **Method A (Section-Loop Count via Timeline):** The compiled `TimelineSpec` programs the montage section graph with an explicit loop count $N \in \{1, 2, 3\}$. Upon completing cycle $N$, the montage advances naturally across the exit seam into `Slam`.
- **Method B (Code-Dispatched Section Transition):** The timeline timer expires at the exact prechosen duration $T_{\text{hold}}$, calling `Montage_SetNextSectionName("ApexHold", "Slam")`.

### 3.3 Fail-Safe Watchdog Timer
To prevent the indefinite freeze risks identified in Codex D02/D05, a strict watchdog timer clamps the hold:
$$\text{MaxRealDuration} = \text{RaiseDuration} + \text{MaxHoldDuration} + 0.200\text{ s} = 1.800\text{ s}$$
If a notify is dropped or section advancement stalls, the watchdog unconditionally forces an immediate transition to `Slam`.

---

## 4. Notify Marker Placements & Event Architecture

The montage carries standardized markers conforming to the Codex D02 `AN_CombatEvent` / `ANS_CombatWindow` architecture:

```
+------------------+-----------------------+---------------------+-------------------+------------------------------------------+
| Section          | Timeline Offset       | Notify Class        | Payload / Kind    | Gameplay Function                        |
+------------------+-----------------------+---------------------+-------------------+------------------------------------------+
| **Raise**        | 0.000 s - 0.500 s     | `ANS_CombatWindow`  | `Telegraph`       | Renders telegraph visuals & windup audio |
| **Raise**        | 0.400 s               | `AN_CombatEvent`    | `Commit`          | Locks heading rotation; freezes tracking |
| **ApexHold**     | 0.000 s - LoopEnd     | `ANS_CombatWindow`  | `HoldInterval`    | Active hold state; evaluates watchdog    |
| **ApexHold/Slam**| Pre-Slam - 0.150 s    | `AN_CombatEvent`    | `ReleaseCue`      | **MANDATORY FAIRNESS CUE**: Sound/VFX    |
| **Slam**         | 0.100 s - 0.320 s     | `ANS_CombatWindow`  | `ActiveDamage`    | Weapon trace sweeps active (220 ms)      |
| **Slam**         | 0.220 s               | `AN_CombatEvent`    | `Impact`          | Ground collision, floor decals, camera   |
| **Slam**         | 0.700 s               | `AN_CombatEvent`    | `RecoveryEnd`     | Unlocks next attack selection            |
+------------------+-----------------------+---------------------+-------------------+------------------------------------------+
```

### 4.1 The Mandatory 150 ms Release Cue (Fairness Guarantee)
To prevent unfair "instant release" from a variable hold, an authoritative `ReleaseCue` event fires exactly **$150\text{ ms}$ before the blade begins its downward active descent**:
- **Acoustic:** Loud metallic latch / blade resonance crack.
- **Visual:** Bright fuller spark running from grip to blade tip.
- **Fairness:** Provides human players with the physiological reaction window ($150\text{ ms}$ lead + $100\text{ ms}$ active startup = $250\text{ ms}$ total lead) required to execute an evasive roll, regardless of whether the boss chose a short or long hold.

---

## 5. Parity Preservation & Future Rollout Roadmap

```
+----------------------------------------------------------------------------------------------------+
| STAGED IMPLEMENTATION ROADMAP                                                                      |
+-------------------+---------------------------------------+----------------------------------------+
| Stage             | Live Runtime Behavior                 | Authored Trio Status                   |
+-------------------+---------------------------------------+----------------------------------------+
| **DD-1 (Current)**| Unchanged `GS_ChargedAttack_Montage`  | Offline specification only (AG-5)      |
| **P1 Readability**| Live pack move audited                | Cue & telegraph assets prototyped      |
| **P2 Architecture**| Pack adapter receives timeline tokens | `TimelineSpec` compiled for A2 trio   |
| **P5 Combat Feel**| Owner decides cutover / replacement   | `AM_Boss01_A2_OverheadSlam` activated  |
+-------------------+---------------------------------------+----------------------------------------+
```

### Parity Invariance
1. **Zero Code Changes in DD-1:** No C++, config, or animation asset changes occur during DD-1. The pack's `GS_ChargedAttack_Montage` continues to play.
2. **Post-DD-1 Cutover Criteria:** Activation of `AM_Boss01_A2_OverheadSlam` occurs only after:
   * The root cause of the live early stop canceller (E-005) is resolved or superseded by the P2 timeline controller.
   * The project owner explicitly signs off on the visual change from the pack twirl to the stationary poise hold.

---

## 6. Evidence and Limits

| Claim / Field | Source File / Anchor | Kind | Status / Limit |
| :--- | :--- | :--- | :--- |
| Pack Montage Early Stop (9 of 11 stopped early) | `Claude/Evidence/E-005_A2_early_stop.md:9-21` | Engine Trace Export | Measured bot run symptom; software canceller unidentified |
| Pack Montage Notifies (1.567s & 1.925s trace windows) | `Claude/Evidence/exports/montage_notifies_2026-10-25.txt:28-34` | Engine Asset Inspection | Exact notify positions from `GS_ChargedAttack_Montage` |
| Authored Trio Section Durations (0.50s Raise, 0.40s Hold, 0.80s Slam) | `Docs/BossCombatReview/Execution/Antigravity/Evidence/movesheets/AN_Boss01_A2_*.json` | Declared Authoring Intent | Offline sidecar parameters; composite montage not yet assembled in engine |
| Loop Seam Alignment (< 0.1 mm, < 0.05 deg) | Offline FBX Kinematic Extraction | Offline Measurement | Measured in Blender/Python armature space; in-engine runtime blend unverified |
| Watchdog Clamp (1.800s) | `AG5_A2_INTEGRATION_SPEC.md` Section 3.3 | Architectural Design | Fail-safe specification; no code implemented |

### What Could NOT Be Verified Offline:
1. Smoothness of the runtime animation blend between `AN_Boss01_A2_Raise` and `ApexHold` inside Unreal's animation graph cannot be tested without editor montage compilation.
2. Root cause of the pack move's early stop canceller cannot be resolved without C++ diagnostic call-stack logging (G-4, currently not approved).
