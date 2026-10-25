# Technical Animation & Combat Visual Authoring Contract Proposal (CI-P0-A-02) - Revision 03

Date: 2026-10-25 (Revision 03)
Author: Antigravity (Accountable Visual Investigator)
Technical Review: Claude (Technical Lead) and Codex GPT-6 Astra
Initiative: P0-P8 Boss Combat Improvement Program - Data-Driven Architecture Gate
Target Implementation: Universal Data-Driven Boss & Weapon Combat Framework ("Elden Ring Architecture")
Status: **PROPOSAL ALIGNED WITH GATE DECISION G-1 & E-008 RUNTIME EVIDENCE (Non-Binding Guidance; Offline Investigation Only)**

---

## 1. Objectives & Executive Scope

Per the Owner Directive of 2026-10-25 (`OWNER_DIRECTIVE_2026-10-25.md`), the combat engine is transitioning to a **data-driven architecture**:
> *"Hundreds of bosses, one combat code. Bosses, weapons, and player builds are all data. Adding a new boss must need only data and animation (plus weapon and player-weapon data likewise), with no new combat code."*

To satisfy the **"Second Boss Canary"** acceptance criteria (creating a functional second boss without modifying C++, headers, or introducing bespoke components), this **Authoring Contract Proposal** defines the animation and technical visual specifications for data asset authoring.

*Status Note (Per Codex Review [X-100]):* This document is a technical design proposal prepared for integration into Claude's `DATA_DRIVEN_ARCHITECTURE_GATE.md`. It does not unilaterally authorize code changes, asset overwrites, or pack modifications.

---

## 2. File & Asset Naming Standards

All assets for any boss entity (e.g. `Boss01_Sevarog`, `Boss02_Canary`) must follow strict prefix and directory conventions:

### 2.1 File & Object Prefixes
| Asset Type | Prefix | Example | Unreal Content Path |
|---|---|---|---|
| Source FBX Animation | `AN_` | `AN_Boss01_A1_QuickSlash.fbx` | `Import/<BossID>/Animations/` |
| Authoring Sidecar Metadata | `AN_` (`.txt` & `.json`) | `AN_Boss01_A1_QuickSlash.json` | `Import/<BossID>/Animations/` |
| Live Unreal Anim Sequence | `A_` or `AN_` | `AN_Boss01_A1_QuickSlash` | `/Game/OneBossFight/<BossID>/Animations/` |
| Live Unreal Anim Montage | `AM_` | `AM_Boss01_A1` | `/Game/OneBossFight/<BossID>/Animations/` |
| Static Mesh Prop / Weapon | `SM_` | `SM_Boss01_Greatsword.fbx` | `/Game/OneBossFight/<BossID>/Weapons/` |
| Skeletal Mesh Armor / Body | `SK_` | `SK_Boss01_Body.fbx` | `/Game/OneBossFight/<BossID>/Meshes/` |
| Data-Driven Boss Move Data | `DA_Move_` | `DA_Move_Boss01_A1` | `/Game/OneBossFight/<BossID>/Data/` |
| Data-Driven Boss Archetype | `DA_Boss_` | `DA_Boss_Boss01` | `/Game/OneBossFight/<BossID>/Data/` |

---

## 3. Frame Rate, Coordinate System, & Unit Conventions

1. **Authoring Frame Rate:** Strictly **30.0 fps** (or **60.0 fps** integer multiple). All keyframes must be keyed to integer frames (no sub-frame drifting).
2. **Coordinate System:** Unreal Standard Z-Up, X-Forward, Y-Right (or Blender Right-Handed Z-Up, -Y Forward / +Y Forward with explicit FBX export axis mapping).
3. **World Units:** Metric centimeters ($1\text{ Unreal Unit} = 1.0\text{ cm}$).
4. **Frame Indexing Convention:**
   - **JSON / Code Metadata:** Zero-based ($0 \dots N-1$). Frame $0$ is time $t = 0.000\text{ s}$.
   - **Blender GUI / Headless Extraction:** 1-based ($1 \dots N$). Frame $1$ is time $t = 0.000\text{ s}$.
   - **Offset Mapping Rule:** $F_{\text{Blender}} = F_{\text{Metadata}} + 1$.
   - **Elapsed Duration:** Strictly $((N - 1) / 30.0)\text{ s}$ for $N$ sample frames.

---

## 4. Per-Move Timing Markers & Unified Notify Architecture

In the legacy architecture, attack timings were hard-coded in C++ constructors (`URPGAttackTracker::URPGAttackTracker`). In the data-driven architecture, **the animation montage itself is the primary source of truth for move lifecycle and collision timing**, reconciled with the `FBossMoveDefinition` data asset.

### 4.1 Minimal Unified Project Notify Model (Per Codex D02)
Rather than proliferating bespoke notify classes, the authoring contract proposes **two unified, reusable project notify types**:

```
MONTAGE NOTIFY TIMELINE SCHEMA:
[0.00 s] ---------------------------------------------------------------------------------------- [End s]
Track 1 (Windows):    |==== ANS_CombatWindow(Telegraph) ====|
Track 2 (Tracking):   |======== ANS_CombatWindow(YawTracking) ========|
Track 3 (Events):                                                    [AN_CombatEvent(Commit)]
Track 4 (Threat):                                                         |==== ANS_CombatWindow(ThreatTrace) ====|
Track 5 (Branching):                                                               [AN_CombatEvent(BranchCheck)]
Track 6 (Defense):    |================ ANS_CombatWindow(HyperArmor) ================|
Track 7 (Recovery):                                                                            [AN_CombatEvent(RecoveryEnd)]
```

1. **`ANS_CombatWindow` (AnimNotifyState):** Defines an active temporal interval with payload parameters:
   - `ThreatTrace`: Weapon collision sweep active window (matching or adapting `ANS_CollisionTrace`).
   - `TelegraphCue`: Dynamic telegraph windup window (driving `rpg.CloseTelegraph` scaling and shader cues).
   - `YawTracking`: Target-facing rotation window (specifying `YawTurnRate` in deg/s).
   - `HyperArmor`: Poise resistance / flinch mitigation window (specifying poise damage multiplier).
   - `Invulnerable`: Dodging / i-frame window.
2. **`AN_CombatEvent` (AnimNotify):** Defines a discrete lifecycle milestone:
   - `Commit`: Heading lock / commit point (locks rotation toward target).
   - `BranchCheck`: Multi-stage combo decision point (e.g. A3a -> A3b follow-up window).
   - `RecoveryEnd`: Earliest point boss can blend to combat idle or transition to another action.
   - `SpawnProjectile`: Detachment point for ranged weapons (e.g. A5 Javelin release).

---

## 5. Weapon Geometry & Trace Socket Contract

### 5.1 Runtime Socket Reality & Explicit Data Offset Contract
1. **Runtime Socket Reality (Claude E-008 Verification & KI-070):**
   - Live engine probing (`Docs/BossCombatReview/Execution/Claude/Evidence/exports/a4_geometry_probe_v2_2026-10-25.txt`) confirms that the runtime static mesh component `RPGLookSword` (`SM_Boss01_Greatsword`) has **zero engine sockets at run time** (`SOCKET_Weapon_Start`, `SOCKET_Weapon_End`, `SOCKET_BladeEnd`, `BladeEnd`, `BladeStart`, `SOCKET_TrailEndSocket` all return `False`; Known Issue KI-070 holds).
   - Cosmetic empties present in the Blender/FBX source do not become engine sockets on imported Unreal static mesh assets without manual editor socket creation.
2. **Explicit Data Offset Contract (Reconciling BladeEnd / Weapon End):**
   - Because no sockets exist on the visible static mesh at runtime, combat hit traces and threat geometry must **never assume socket names on weapon static meshes**.
   - Instead, all weapon trace points must be declared as **explicit numerical offsets in data** (`FBossMoveDefinition` / `FWeaponDefinition`), defined relative to either the attachment socket on the character body (`HeavySwordSocket_R` on `hand_r`) or the static mesh component origin:
     * **Grip / Hilt Origin (`BladeStart`):** `(0.0, 0.0, 0.0)` cm in mesh space (aligned with `HeavySwordSocket_R`).
     * **Blade Midpoint (`BladeMiddle`):** `(0.0, 0.0, +78.0)` cm in mesh space ($+117.0\text{ cm}$ at 1.50x world scale).
     * **Physical Tip (`BladeEnd` / `Weapon End`):** `(0.0, 0.0, +163.30)` cm in mesh space along the +Z blade axis ($+244.95\text{ cm}$ at 1.50x world scale).
   - In future approved editor updates, if project mesh sockets are created, they must snap exactly to these measured vertex bounds; until then, data-defined offsets are the sole source of geometric truth.
3. **Collision Radius:**
   - Production queries utilize the live pack trace radius (**$50.0\text{ cm}$** default), ensuring seamless threat coverage along the swept offset trajectory.

---

## 6. Root Motion Architecture & Conventions

### 6.1 Duel Movement Rule
1. **Boss Combat Duel Moves:** Strictly **In-Place (Zero Root Motion)**.
   - All standard attack moves (A1, A1b, A2, A3a, A3b, A4, A5), staggers, idle, wake, and death maintain `0.0000 cm` root excursion on the root bone.
   - Spatial translation across the arena floor during windups is driven by gameplay navigation and tracking components, not animated root translation, avoiding navigation mesh desynchronization.
2. **Player Execution / Riposte Moves:** **Authored Travel Permitted**.
   - Moves involving synchronized kinematic translation (e.g. `AN_Riposte_Player_Front` advancing $+90.0\text{ cm}$ forward along $+Y$) author translation directly into the root node.
   - In Unreal, runtime execution aligns the player capsule and slides to the boss contact point ($150\text{ cm}$ slide / $60\text{ cm}$ root offset).

---

## 7. Montage Assembly & Bounded Hold Structure

### 7.1 Standard Attack Montage Configuration
- **Slot Name:** `DefaultSlot` (full body) or `UpperBody` (for blended locomotion).
- **Blend In Time:** $0.10\text{ to }0.20\text{ s}$.
- **Blend Out Time:** $0.20\text{ to }0.30\text{ s}$.

### 7.2 The Authored Hold Architecture (A2 Overhead Slam Canary)
For variable or delayed windup telegraphs (such as the A2 Overhead Slam), animators assemble the montage as a **3-Section Composite with a Bounded Hold**:

```
AM_Boss01_A2 MONTAGE SECTIONS:
[Section: Raise]           --> [Section: ApexHold (Looping)] --> [Section: Slam]
(0.00 s - 0.60 s)              (0.00 s - 1.167 s Loop)           (0.00 s - 1.367 s)
Hoist to apex guard             Strained poise with 4 Hz flutter  Snap forward slam to floor
                                Bounded by timeout in Data Asset  Impact event at Z = 2 cm
```

- **Bounded Hold Safeguard:** The looping `ApexHold` section maintains a locked heading. To prevent deadlocks, the data asset specifies a maximum hold duration (e.g. $1.5\text{ to }2.0\text{ s}$) after which the encounter component automatically triggers `Montage_JumpToSection(TEXT("Slam"))`.

---

## 8. Compliance & Contract Audit of Existing Boss Assets

*Boundary Note:* Per project rules, **third-party pack assets (e.g. `GS_Attack04_Montage`, `GS_ChargedAttack_Montage`, `Mid01_Anim_Montage`) must NEVER be modified directly**. Instead, project data assets wrap these moves, and project notify adapters interface with their existing notify tracks.

| Asset / Move | Requirement | Current Asset State | Contract Status | Proposed Integration Path |
|---|---|---|---|---|
| `SM_Boss01_Greatsword` | Socket Tip Alignment | `BladeEnd` at 140 cm, physical tip at 163.3 cm | Geometric Discrepancy (VIS-05) | Reconcile socket offset in data asset; re-export empty when asset update authorized. |
| `AN_Boss01_A2 Trio` | Montage Sectioning | Delivered as 3 standalone clips, unwired in code | Unwired Asset (VIS-02) | Assemble `AM_Boss01_A2` with Raise -> Bounded ApexHold -> Slam sections. |
| `AN_Boss01_A5_Javelin` | Visual Release Alignment | Sidecar release at 0.40 s; C++ tracker at 0.45 s | Hypothesis (VIS-03) | Retain 0.45 s code spawn until Claude runtime capture verifies alignment. |
| `Mid01_Anim_Montage` | Pack Ability Coverage | Pack native; trace 0.637–0.884 s | Coverage Gap (VIS-08) | Wrap via `FBossMoveDefinition` using existing pack notify windows without pack edit. |
| `SprintFollowUp_Montage`| Pack Ability Coverage | Pack native; trace 0.037–0.230 s & 0.364–0.551 s | Coverage Gap (VIS-08) | Wrap via `FBossMoveDefinition` without modifying pack asset. |
| `RetaliationAttack_Montage`| Pack Ability Coverage | Pack native; trace 0.444–0.630 s; stun immunity 0–1.267 s | Coverage Gap (VIS-08) | Wrap via `FBossMoveDefinition` without modifying pack asset. |
| `AN_Riposte_Player_Front` | Root Motion Format | 90 cm forward travel on FBX root node | Compliant | Retain root motion; reconcile runtime slide with engine capture. |
| `Boss Clips (15 Total)` | In-Place Root Standard | Exactly 0.0000 cm excursion on all 15 clips | Compliant | Retain in-place duel standard. |

---

## 9. Machine-Readable Move Sheets & Validation Diagnostics Contract

To ensure complete, automated traceability across authored intent, offline kinematics, and live engine execution, all boss and player combat moves are represented as machine-readable JSON move sheets under `Docs/BossCombatReview/Execution/Antigravity/Evidence/movesheets/` conforming to Schema 2.0 (Codex D02 / Claude C-98).

### 9.1 The 4-Block Separation Schema
1. **`declared_intent`**: Author intent markers parsed from `.txt` sidecars (commit, windup, active windows, recovery, notes) with sidecar SHA-256. For third-party pack clips without sidecars, `has_declared_intent` is `false` with explicit `null` fields (never defaulting to 0).
2. **`measured_extraction`**: Headless Blender forward kinematics (FPS, samples, duration, root excursion, pelvis/foot Z ranges, reach) with FBX SHA-256. For unedited pack moves, `has_measured_extraction` is `false` with all kinematic bounds strictly `null` (never defaulting to 0, satisfying Codex D02).
3. **`engine_timeline`**: Live Unreal engine montage notifies parsed from `Claude/Evidence/exports/montage_notifies_2026-10-25.txt` with SHA-256 digest, recording exact damage windows (`ANS_CollisionTrace_C`), movement disable windows, and rotation windows.
4. **`approved_runtime`**: Retains status `"PENDING_ARCHITECTURE_GATE_APPROVAL"` with empty definition `{}` until approved by the technical lead and owner.

### 9.2 Meaning of Validation Diagnostics for Reviewers
- **Accountable Discrepancy Flag:** A validation diagnostic indicates a cross-block timing or parameter mismatch (e.g. between declared intent in sidecars and live engine montage notifies) exceeding the stated tolerance ($50\text{ ms}$).
- **Non-Fatal Structural Status:** Diagnostics do **not** fail structural file validation. A sheet with diagnostics passes validation structurally while reporting the divergence for architectural review.
- **Strict Prohibition on Silent Auto-Tuning:** Diagnostics **must NEVER be silently auto-corrected, normalized, or overwritten**. They serve as accountable evidence flags indicating either an intentional gameplay feel offset (e.g. A5 projectile release), an authored tuning difference, or a candidate defect for P1–P7 investigation.
- **Parity Baseline Preservation:** In accordance with the DD-1 parity rule, legacy behavior is preserved as measured; corrections are deferred to subsequent approved phases.

---

## 10. Conclusion

This proposal aligns technical animation authoring with Codex's data model (`D02_DATA_MODEL.md`), Claude's Architecture Gate (`DATA_DRIVEN_ARCHITECTURE_GATE.md`), and the Owner Directive, providing a clear contract for the "Second Boss Canary" while respecting all single-editor, parity, and no-pack-edits boundaries.
