# Sevarog First Five Move Cards Design (A-244)

**Document Version:** 1.0.0  
**Author:** Antigravity  
**Task Reference:** `[C-379]`, Order A-244  
**Status:** DELIVERED (Design Specification, Offline, Zero Content/Source Writes)  
**Target Architecture:** `URPGBossMoveCard` / C++ Boss Combat Framework  

---

## 1. Executive Summary & Design Scope

Per Tech Lead Claude's directive in `[C-379]`, this document specifies the **first five foundational Move Cards** for Paragon Sevarog. These five cards form the initial playable moveset for the soulslike boss encounter in `L_SevarogArena` / `L_SevarogFrameworkProof`.

Design constraints strictly applied:
1. **Timing Decoupling:** Per `[C-379]`, this document specifies behavioral roles, spatial parameters (range, cone), combo links, and counterplay rules **WITHOUT hardcoded timing numbers**. Exact duration, commit timestamp, and active hit-window intervals will be populated directly from measured weapon-speed data produced by the Hit-Window Extraction Probe (`probe_weapon_motion.py`, Orders `A-242`/`A-243`).
2. **Grammar Alignment:** Each card maps to an attack family defined in the 15-family moveset inventory and directly satisfies specific requirement IDs from the *Morgott 82-Point Combat Engineering Reference* (`Documentation/Boss/Morgott_82_Point_Combat_Reference/Morgott_82_Point_Combat_Reference.md`).
3. **Finite Pressure:** Combo graphs are strictly bounded (maximum 3 consecutive attacks) with mandatory recovery resets, guaranteeing readable punish windows.

---

## 2. Master Move Cards Matrix

| Card ID | Family | Animation Sequence | Purpose & Encounter Role | Range Band (cm) [Proposed] | Front Cone (deg) [Proposed] | Combo Link | Player Counterplay | Block / Defense | Morgott Requirement IDs |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MC-01** | **Family 1** (Delayed Overhead) | `Swing1_Slow` | Primary telegraphed melee opener; delayed weapon swing punishes panic rolls. | 200 – 400 | 100° (±50°) | Branches to MC-02 on proximity; resets to neutral on whiff. | Roll laterally on weapon release (not during raise); exploit flank opening. | Blockable (medium stamina drain, poise damage = design value TBD). | `BOSS-AWR-003`, `BOSS-ANM-002`, `BOSS-PAC-001`, `BOSS-HIT-001` |
| **MC-02** | **Family 8** (Helicopter Continuation) | `Swing2_Medium` | Mid-speed horizontal combo continuation; catches roll-in attempts. | 150 – 350 | 140° (symmetric ±70°) | Follow-up from MC-01; branches to MC-04 or recovers. | Back-dodge out of sweep radius or roll through blade toward left hip. | Blockable (moderate stamina drain); parryable. | `BOSS-COM-001`, `BOSS-COM-003`, `BOSS-COM-006`, `BOSS-PAC-002` |
| **MC-03** | **Family 2** (Close Anti-Greed) | `Swing1_FAST_v2` | Reactive close-range check; punishes hugging/flank camping in neutral. | 0 – 220 | 80° (±40°) | Standalone check; transitions immediately to neutral recovery. | Maintain spacing discipline; avoid lingering in point-blank pocket. | Blockable (light stamina drain); deflectable. | `BOSS-AWR-006`, `BOSS-SEL-002`, `BOSS-PAC-006`, `BOSS-DEF-005` |
| **MC-04** | **Family 6** (Heavy Overhead Slam) | `Swing3_Slow` | Heavy terminal finisher; decisive ground plunge with high punishability. | 180 – 420 | 60° (±30°) | Terminal node; zero forward links; forces neutral reset. | Side-dodge commit; punish window = measured after the probe while scythe is lodged. | Heavy guard-crush; breaks light/medium shields. | `BOSS-PAC-003`, `BOSS-COM-007`, `BOSS-DEF-004`, `BOSS-HIT-007` |
| **MC-05** | **Family 5** (Gap Closer / Spear Charge) | `Speedburst` | Long-range gap closer; rushes retreating player to re-establish combat band. | 400 – 950 | 50° (±25°) | Transitions directly into MC-01 upon reaching melee distance. | Diagonal roll through the rushing wraith; avoid linear back-pedaling. | Guard break if blocked frontally without greatshield. | `BOSS-MOV-001`, `BOSS-MOV-003`, `BOSS-ANM-004`, `BOSS-PHS-005` |

> [!NOTE]
> **Timing Attributes (`CommitTime`, `ActiveWindows`, `RecoveryEnd`):** Marked `[TIMINGS PENDING PROBE RUN - A-243]`. Values will be authored from the measured component-space speed peaks extracted by `probe_weapon_motion.py`.

---

## 3. Detailed Card Specifications

### 3.1. Card MC-01: `DA_Card_Sevarog_SwingSlow` (Telegraphed Melee Opener)
- **Attack Family:** Family 1 (Curved sword slash / delayed overhead; `Morgott_...md:40`).
- **Animation Sequence Asset:**  
  `Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Slow.uasset`
- **Encounter Purpose:**  
  The core bread-and-butter melee attack. Sevarog raises his scythe high, introducing a perceptible hold phase that tests player dodge discipline. Panic rolling on the initial telegraph leads to roll-catching; evasion must occur at the release inflection point.
- **Range Band:** `[200.0, 400.0]` cm. Optimal engagement distance: 300 cm.
- **Orientation Cone:** `[-50.0, +50.0]` deg (100° total arc).
- **Combo Branching:**
  - On proximity (<350 cm after active phase): Can link into **MC-02** (`Swing2_Medium`).
  - On player retreat or whiff: Terminates and returns to Neutral Recovery.
- **Player Counterplay:**  
  Wait for downward arm motion before dodging. Flank dodge grants an immediate light-attack opening.
- **Block & Defense Rules:**  
  Fully blockable with standard shield; poise damage = design value TBD.
- **Morgott Requirements Satisfied:**
  - `BOSS-AWR-003` (Distance convention: explicit melee range band).
  - `BOSS-ANM-002` (Telegraph phases: distinguishable windup hold).
  - `BOSS-PAC-001` (Explicit attack segments: windup, active, recovery).
  - `BOSS-HIT-001` (Geometry fidelity: swept weapon blade trajectory).

---

### 3.2. Card MC-02: `DA_Card_Sevarog_SwingMedium` (Combo Continuation Sweep)
- **Attack Family:** Family 8 (Helicopter / Melee combo continuation; `Morgott_...md:47`).
- **Animation Sequence Asset:**  
  `Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing2_Medium.uasset`
- **Encounter Purpose:**  
  Maintains pressure following MC-01. If the player dodges in or attempts an immediate aggressive counterattack, this broad horizontal sweep catches them inside the swing radius.
- **Range Band:** `[150.0, 350.0]` cm.
- **Orientation Cone:** `[-40.0, +100.0]` deg (140° total arc, rightward bias).
- **Combo Branching:**
  - Follow-up from **MC-01**.
  - If player remains aggressive (<300 cm): Links into terminal finisher **MC-04** (`Swing3_Slow`).
  - Otherwise terminates combo cleanly into Recovery.
- **Player Counterplay:**  
  Recognize the two-beat cadence; roll through the sweep toward the boss's rear-left hip or disengage backward outside 350 cm.
- **Block & Defense Rules:**  
  Blockable; parryable during initial swing arc.
- **Morgott Requirements Satisfied:**
  - `BOSS-COM-001` (Authored combo graph: explicit directed branch from MC-01).
  - `BOSS-COM-003` (Fresh branch context: checks player position before committing).
  - `BOSS-COM-006` (Finite pressure: intermediate combo link).
  - `BOSS-PAC-002` (Pressure variation: shifts tempo from slow MC-01 to medium MC-02).

---

### 3.3. Card MC-03: `DA_Card_Sevarog_AntiGreedPoke` (Close Anti-Greed Check)
- **Attack Family:** Family 2 (Holy dagger double slash / Close anti-greed; `Morgott_...md:41`).
- **Animation Sequence Asset:**  
  `Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_FAST_v2.uasset`
- **Encounter Purpose:**  
  Prevents player from camping in point-blank range or exploiting recovery states with infinite light attacks. Rapid, short-arc scythe jab enforcing spacing discipline.
- **Range Band:** `[0.0, 220.0]` cm. Point-blank pocket check.
- **Orientation Cone:** `[-40.0, +40.0]` deg (80° focused corridor).
- **Combo Branching:**  
  Standalone poke. Does NOT combo into heavy attacks; resets rapidly to neutral to allow the encounter loop to breathe.
- **Player Counterplay:**  
  Do not linger in hugging distance. Backstep or single backward roll creates distance; move deals modest damage and is primarily a positional deterrent.
- **Block & Defense Rules:**  
  Blockable with minimal stamina drain.
- **Morgott Requirements Satisfied:**
  - `BOSS-AWR-006` (Observable player activity: reactive response to point-blank proximity).
  - `BOSS-SEL-002` (Hard-filter precedence: anti-greed prioritized when range < 220 cm).
  - `BOSS-PAC-006` (Neutral is purposeful: forces player out of hugging range).
  - `BOSS-DEF-005` (Fair boss defense: brief telegraph prevents unreactable damage).

---

### 3.4. Card MC-04: `DA_Card_Sevarog_HeavySlam` (Heavy Terminal Finisher)
- **Attack Family:** Family 6 / Family 8 (Heavy overhead slam / Finisher; `Morgott_...md:45, 47`).
- **Animation Sequence Asset:**  
  `Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing3_Slow.uasset`
- **Encounter Purpose:**  
  The decisive exclamation point at the end of a combo string (MC-01 -> MC-02 -> MC-04). High risk, high reward. A massive vertical downward slam that lodges the scythe momentarily into the arena surface, granting the player a guaranteed heavy punish window.
- **Range Band:** `[180.0, 420.0]` cm.
- **Orientation Cone:** `[-30.0, +30.0]` deg (60° narrow impact line).
- **Combo Branching:**  
  Strictly TERMINAL. No further combo links permitted (`BOSS-COM-007`). Always transitions to extended recovery state.
- **Player Counterplay:**  
  Sidestep or roll laterally around the blade. Once the slam impacts, the boss recovery duration will be measured by probe to establish the punish window.
- **Block & Defense Rules:**  
  Guard-crush tier: draining entire stamina bar on small shields; safe only with greatshield or complete evasion.
- **Morgott Requirements Satisfied:**
  - `BOSS-PAC-003` (Guaranteed openings: substantial recovery following heavy finisher).
  - `BOSS-COM-007` (Default recovery: terminal combo state forces neutral reset).
  - `BOSS-DEF-004` (Windowed hyperarmor during the active downward strike).
  - `BOSS-HIT-007` (Explicit hit policy: single hit registration per entity).

---

### 3.5. Card MC-05: DA_Card_Sevarog_Speedburst (Gap Closer / Engagement Rush)
- **Attack Family:** Family 5 (Holy spear charge / Gap closer; Morgott_...md:44).
- **Animation Sequence Asset:**  
  Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Speedburst.uasset
- **Root Motion Status:**  
  **IN-PLACE ONLY (UsesRootMotion = false).** Inventory check confirms Speedburst contains zero root motion displacement. Rush displacement requires an external movement envelope / facade in boss movement code, which is NOT yet implemented in F3/F4. MC-05 is explicitly marked **BLOCKED / DEFERRED** on that movement capability.
- **Encounter Purpose:**  
  Eliminates cheese strategies where the player stays at extreme distance to safely heal or kite. Sevarog phases forward at high velocity once movement facade is wired.
- **Range Band (Proposed):** [400.0, 950.0] cm. Active only outside melee range.
- **Orientation Cone (Proposed):** 50.0 deg (symmetric ±25.0°).
- **Combo Branching:**  
  On reaching proximity (<350 cm from player): Transitions directly into **MC-01** (Swing1_Slow) or returns to neutral melee stance.
- **Player Counterplay:**  
  Do not run backward linearly. Sprint perpendicular to dash direction or roll diagonally forward-left through Sevarog's rush trajectory as he approaches.
- **Block & Defense Rules:**  
  Guard break if blocked frontally without greatshield (UNVERIFIED pending player defense integration).
- **Morgott Requirements Satisfied:**
  - BOSS-MOV-001 (Range-band policy: strictly gated to long-range engagement).
  - BOSS-MOV-003 (Movement commitment: movement envelope cannot perform 90° turns).
  - BOSS-ANM-004 (Staged rotation cap: tracking drops to 0 once dash starts).
  - BOSS-PHS-005 (Anti-cheese: punishes passive long-range healing and kiting).

---

## 4. Encounter Combo Graph Topology

The directed acyclic graph (DAG) governing move card transitions:

```
                  [ Long Range (>400 cm) ]
                             │
                             ▼
                    ┌─────────────────┐
                    │  MC-05: Rush    │
                    │  (Speedburst)   │
                    └────────┬────────┘
                             │
                             ▼
                  [ Melee Range (200-400 cm) ]
                             │
            ┌────────────────┴────────────────┐
            │                                 │
            ▼                                 ▼
   ┌─────────────────┐               ┌─────────────────┐
   │  MC-01: Opener  │               │ MC-03: AntiGreed│ (Point Blank <220 cm)
   │  (Swing1_Slow)  │               │ (Swing1_FAST_v2)│
   └────────┬────────┘               └────────┬────────┘
            │                                 │
            ├──────────────┐                  ▼
            │ (whiff)      │ (hit / prox)   [ Return to Neutral ]
            ▼              ▼
       [ Recovery ]  ┌─────────────────┐
                     │  MC-02: Sweep   │
                     │ (Swing2_Medium) │
                     └────────┬────────┘
                              │
            ┌─────────────────┴─────────────────┐
            │ (whiff / space)                   │ (continued melee)
            ▼                                   ▼
       [ Recovery ]                    ┌─────────────────┐
                                       │  MC-04: Finisher│
                                       │  (Swing3_Slow)  │
                                       └────────┬────────┘
                                                │
                                                ▼
                                      [ Guaranteed Opening ]
                                      [ Punish Window = Measured After Probe ]
```

---

## 5. Citations & Verification Checklist

All animation sequence assets cited exist on disk under `Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/`:
- `Swing1_Slow.uasset` (857,645 bytes)
- `Swing2_Medium.uasset` (576,523 bytes)
- `Swing1_FAST_v2.uasset` (496,523 bytes)
- `Swing3_Slow.uasset` (648,644 bytes)
- `Speedburst.uasset` (340,654 bytes)

All Morgott references cited match exact text lines in `Documentation/Boss/Morgott_82_Point_Combat_Reference/Morgott_82_Point_Combat_Reference.md`:
- Family 1 (Line 40), Family 2 (Line 41), Family 5 (Line 44), Family 6 (Line 45), Family 8 (Line 47).
- 82-Point requirement categories: Awareness (`BOSS-AWR`), Selection (`BOSS-SEL`), Execution (`BOSS-EXE`), Combos (`BOSS-COM`), Animation (`BOSS-ANM`), Hit Detection (`BOSS-HIT`), Movement (`BOSS-MOV`), Pacing (`BOSS-PAC`), Defense (`BOSS-DEF`), and Phases (`BOSS-PHS`).
