# AG-2: Second-Boss Canary Content Specification

**Document ID:** `AG2_CANARY_CONTENT_SPEC` (Rev 01)  
**Date:** 2026-10-25  
**Author:** Antigravity (Accountable Visual & Technical Animation Investigator)  
**Addressed to:** Claude (Technical Lead & Editor Owner), Codex GPT-6 Astra (Technical Reviewer & Data Architect)  
**Context & Authority:** Task AG-2 of Work Order 01 (`ANTIGRAVITY_WORK_ORDER_01.md`). Conforms to Codex `D02_DATA_MODEL.md` section "Second-boss, weapon and build canary". Strictly OFFLINE content brief.

> [!IMPORTANT]
> **CANARY TEST DATA NOTICE:** All numerical values (HP, damage, timings, reach, thresholds) in this specification are **CANARY TEST DATA** designed to prove data-driven registry extensibility, isolation, and lifecycle independence. None of these values alter or contaminate Boss01 (Ember Warden) or the existing three player builds.

---

## 1. Executive Summary & Extensibility Objectives

This specification delivers a complete content brief for a second boss (**"Cinder Knight Alistair"**), one new weapon (**"Silversteel Halberd"**), and a fourth player build (**"Vanguard"**).

### Architectural Extensibility Proofs (Codex D02 Pass Criteria)
1. **Zero New Combat Code:** Relies strictly on existing shared capability executors (weapon sweep, planar/projectile, radial wave, branching transitions). Zero C++ class additions, zero new Blueprints.
2. **Zero Boss01 Hardcoded Leakage:** Uses distinct registered IDs (`Boss_Canary_Alistair`, `Weapon_Player_Halberd`, `Build_Vanguard`). Validates that no global cvars, singletons, or string literals containing "Boss01" are required for combat resolution.
3. **No Retargeting Smuggling:** Reuses the existing compatible humanoid boss skeleton (`SK_Boss01_Skeleton` / pack compatible) to prevent unverified skeleton retargeting issues from obfuscating data-driven architecture tests.

---

## 2. Canary Boss Identity & Presentation: "Cinder Knight Alistair"

```
+----------------------------------------------------------------------------------------+
| CANARY BOSS IDENTITY CARD                                                              |
+----------------------+-----------------------------------------------------------------+
| Boss ID              | `Boss_Canary_Alistair` (Test Data)                              |
| Display Name         | "Cinder Knight Alistair"                                        |
| Archetype            | Heavy Polearm / Frost-Flame Vanguard                            |
| Primary Mesh         | `SKM_Canary_Alistair` (Compatible Humanoid Rig)                 |
| Skeleton Ref         | `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin` (Pack Mannequin Skeleton, `import_boss01.py:8`; to be confirmed in editor) |
| Weapon Mesh Ref      | `SM_Canary_Halberd` (Attached to `hand_r` / `RPGLookWeapon`)     |
| Component World Scale| `1.25` (Physical length: 220 cm; test data)                     |
| Visual Palette       | Weathered plate armor, tattered tabard, pale blue soulfire VFX  |
| Encounter ID         | `Encounter_Canary_Arena`                                        |
+----------------------+-----------------------------------------------------------------+
```

### 2.1 Lifecycle Animation Suite
To satisfy lifecycle data requirements without new gameplay classes, Alistair defines explicit data bindings for all lifecycle states:
1. **Dormant:** `AN_Canary_Dormant` (Kneeling with halberd grounded in stone).
2. **Wake:** `AN_Canary_Wake` ($1.800\text{ s}$ montage; grips weapon, pulls blade from floor with sparks, emits pale blue mist burst).
3. **Stagger / Posture Break:** `AN_Canary_Stagger` ($2.500\text{ s}$ kneeling posture collapse; visceral attack socket exposed at chest).
4. **Riposte Victim:** `AN_Canary_Riposte_Victim` ($1.800\text{ s}$ paired victim animation).
5. **Phase Transition:** `AN_Canary_PhaseTransition` ($2.500\text{ s}$ roar; halberd blade ignites with blazing blue frost-flame).
6. **Death:** `AN_Canary_Death` ($3.200\text{ s}$; drops halberd, dissolves into blue ash).

---

## 3. Canary Boss Move Inventory (Shared Capabilities Verification)

Alistair's move catalog exercises the full suite of required shared executor kinds:
- **Move 1:** Weapon sweep with **two active collision windows** in a single montage.
- **Move 2:** **Projectile release** launching a traveling crescent arc.
- **Move 3:** **Radial shockwave ground effect** expanding outward.
- **Move 4:** Explicit **branching move** with Success, Failure (Whiff), and Default Recovery paths.

---

### 3.1 Move 1: Double-Window Halberd Cleave (`Canary_M1_DoubleCleave`)

- **Executor Kind:** `ECombatExecutor::WeaponTraceSweep` (Dual Window).
- **Capability Tested:** Single montage driving two distinct, sequential damage windows with an intermediate poise pause and retargeting commit.
- **Move Timing Card (Canary Test Data):**
  * Windup 1: $0.000\text{ s}$ to $0.400\text{ s}$ ($400\text{ ms}$). Halberd drawn back horizontally.
  * Commit 1: $0.350\text{ s}$ (Heading tracking freezes).
  * **Active Window 1 (Forward Cleave):** $0.400\text{ s}$ to $0.580\text{ s}$ ($180\text{ ms}$). Horizontal forward slash.
  * Intermediate Seam: $0.580\text{ s}$ to $0.800\text{ s}$ ($220\text{ ms}$). Halberd twirls; tracking unfreezes briefly.
  * Commit 2: $0.750\text{ s}$ (Heading tracking locks again).
  * **Active Window 2 (Return Slash):** $0.800\text{ s}$ to $1.000\text{ s}$ ($200\text{ ms}$). Reverse upward diagonal slice.
  * Recovery: $1.000\text{ s}$ to $1.600\text{ s}$ ($600\text{ ms}$).
  * Blend In / Out: $0.150\text{ s}$ / $0.200\text{ s}$.
- **Notify Placements (D02 Spec):**
  * `ANS_CombatWindow` [Telegraph] ($0.000\text{--}0.400\text{ s}$)
  * `AN_CombatEvent` [Commit] ($0.350\text{ s}$, EventId: `Commit_1`)
  * `ANS_CombatWindow` [ActiveDamage] ($0.400\text{--}0.580\text{ s}$, WindowId: `Damage_Window_1`)
  * `AN_CombatEvent` [Commit] ($0.750\text{ s}$, EventId: `Commit_2`)
  * `ANS_CombatWindow` [ActiveDamage] ($0.800\text{--}1.000\text{ s}$, WindowId: `Damage_Window_2`)
  * `AN_CombatEvent` [RecoveryEnd] ($1.600\text{ s}$)
- **Sockets & Offsets:**
  * Halberd Tip: Local `(0.0, 0.0, 185.0)` cm.
  * Halberd Midpoint: Local `(0.0, 0.0, 95.0)` cm.
  * Halberd Hook/Axe: Local `(0.0, 22.0, 150.0)` cm.
- **Data Model Fields Filled:**
  * `MoveId`: `"Canary_M1_DoubleCleave"`
  * `ExecutorKind`: `WeaponSweep`
  * `ActiveWindows`: `[ {Start: 0.400, End: 0.580, DamageMultiplier: 1.0}, {Start: 0.800, End: 1.000, DamageMultiplier: 1.25} ]`
  * `MinDistance`: $150.0\text{ cm}$, `MaxDistance`: $450.0\text{ cm}$
  * `TrackingYawRate`: $240.0^\circ/\text{s}$

---

### 3.2 Move 2: Soulfire Crescent Projectile (`Canary_M2_SoulfireArc`)

- **Executor Kind:** `ECombatExecutor::ProjectileRelease`.
- **Capability Tested:** Vertical weapon slash that spawns a traveling linear/planar projectile actor (`ARPGBossJavelin` equivalent or generic projectile executor) on a precise release event.
- **Move Timing Card (Canary Test Data):**
  * Windup: $0.000\text{ s}$ to $0.500\text{ s}$ ($500\text{ ms}$). High vertical weapon raise.
  * Commit: $0.450\text{ s}$ (Heading locked).
  * **Vertical Chop & Release Event:** $0.500\text{ s}$ to $0.650\text{ s}$ ($150\text{ ms}$). Projectile released at $0.550\text{ s}$.
  * Recovery: $0.650\text{ s}$ to $1.200\text{ s}$ ($550\text{ ms}$).
  * Blend In / Out: $0.150\text{ s}$ / $0.200\text{ s}$.
- **Notify Placements (D02 Spec):**
  * `ANS_CombatWindow` [Telegraph] ($0.000\text{--}0.500\text{ s}$)
  * `AN_CombatEvent` [Commit] ($0.450\text{ s}$)
  * `AN_CombatEvent` [EffectRelease] ($0.550\text{ s}$, EventId: `Release_SoulfireArc`)
  * `AN_CombatEvent` [RecoveryEnd] ($1.200\text{ s}$)
- **Sockets & Offsets:**
  * Spawn Origin: Halberd tip at floor contact: Local offset `(0.0, 0.0, 185.0)` cm transformed to world space.
- **Projectile Data Parameters (Test Data):**
  * `ProjectileSpeed`: $1800.0\text{ cm/s}$
  * `MaxRange`: $2000.0\text{ cm}$
  * `CollisionRadius`: $50.0\text{ cm}$
  * `Damage`: $45.0$
  * `Homing`: Disabled (pure linear trajectory along commit forward yaw)

---

### 3.3 Move 3: Frost-Ember Radial Quake (`Canary_M3_RadialQuake`)

- **Executor Kind:** `ECombatExecutor::RadialShockwave` (Expanding Wave).
- **Capability Tested:** Radial ground effect expanding outward with jump counterplay, testing data-parameterized shockwave expansion.
- **Move Timing Card (Canary Test Data):**
  * Windup: $0.000\text{ s}$ to $0.600\text{ s}$ ($600\text{ ms}$). Boss vaults slightly, driving halberd butt into the stone floor.
  * Commit: $0.500\text{ s}$.
  * **Ground Impact Event:** $0.600\text{ s}$. Radial shockwave begins expanding from halberd impact point.
  * **Wave Expansion Band:** $0.600\text{ s}$ to $1.400\text{ s}$ ($800\text{ ms}$). Expands from $150.0\text{ cm}$ to $950.0\text{ cm}$ radius ($1000.0\text{ cm/s}$ expansion speed).
  * Recovery: $0.600\text{ s}$ to $1.350\text{ s}$ ($750\text{ ms}$).
  * Blend In / Out: $0.150\text{ s}$ / $0.250\text{ s}$.
- **Notify Placements (D02 Spec):**
  * `ANS_CombatWindow` [Telegraph] ($0.000\text{--}0.600\text{ s}$)
  * `AN_CombatEvent` [Commit] ($0.500\text{ s}$)
  * `AN_CombatEvent` [ImpactShockwave] ($0.600\text{ s}$, EventId: `Spawn_Quake`)
  * `AN_CombatEvent` [RecoveryEnd] ($1.350\text{ s}$)
- **Radial Query Parameters (Test Data):**
  * `OriginSocket`: `SOCKET_Halberd_Butt` at floor contact.
  * `StartRadius`: $150.0\text{ cm}$, `MaxRadius`: $950.0\text{ cm}$.
  * `ExpansionSpeed`: $1000.0\text{ cm/s}$.
  * `BandWidth`: $160.0\text{ cm}$.
  * `JumpClearanceHeight`: $45.0\text{ cm}$ above ground.

---

### 3.4 Move 4: Branching Thrust & Vault (`Canary_M4_ThrustVault`)

- **Executor Kind:** `ECombatExecutor::BranchingSequence`.
- **Capability Tested:** High-risk thrust attack that evaluates hit registration during an active window and branches to **Success** (vault kick follow-up), **Failure** (whiff overextension), or **Default Recovery**.
- **Move Timing Card (Canary Test Data):**
  * **Section 1: Initial Thrust (`Thrust_Intro`):** $0.000\text{ s}$ to $0.450\text{ s}$. Fast lunging thrust.
    - Commit: $0.350\text{ s}$.
    - Active Hit Window: $0.400\text{ s}$ to $0.500\text{ s}$ ($100\text{ ms}$).
    - Branch Decision Gate: $0.500\text{ s}$ (`BranchGate` marker).
  * **Branch A: Hit Confirmed (`Vault_Success`):** $0.500\text{ s}$ to $1.200\text{ s}$ ($700\text{ ms}$). Boss steps onto player shoulder, vaults airborne, and delivers heavy downward pommel strike.
  * **Branch B: Whiff / Missed (`Stumble_Failure`):** $0.500\text{ s}$ to $1.650\text{ s}$ ($1150\text{ ms}$). Halberd overextends into ground; boss stumbles forward. **$1.150\text{ s}$ highly punishable opening**.
  * **Default Fallback Recovery:** If interrupted or target destroyed during thrust, immediately blends out to neutral ($200\text{ ms}$ blend).
- **Notify Placements (D02 Spec):**
  * `ANS_CombatWindow` [Telegraph] ($0.000\text{--}0.400\text{ s}$)
  * `AN_CombatEvent` [Commit] ($0.350\text{ s}$)
  * `ANS_CombatWindow` [ActiveDamage] ($0.400\text{--}0.500\text{ s}$)
  * `AN_CombatEvent` [BranchGate] ($0.500\text{ s}$, EventId: `Evaluate_ThrustHit`)
  * `AN_CombatEvent` [RecoveryEnd] ($1.200\text{ s}$ on success / $1.650\text{ s}$ on failure)

---

## 4. Two-Phase Threshold System & Phase Transition

The Canary defines two distinct combat phases driven entirely by data-defined health fractions:

```
+----------------------------------------------------------------------------------------+
| CANARY PHASE CONFIGURATION (TEST DATA)                                                 |
+----------------+----------------+-------------------------------+----------------------+
| Phase ID       | Health Band    | Move Eligibility Pool         | Cooldown Scale / AI  |
+----------------+----------------+-------------------------------+----------------------+
| `Phase_1`      | 100% to 50% HP | `Canary_M1`, `Canary_M2`, `M4`| Cooldown Scale: 1.00 |
| `Transition`   | At 50% HP (2.5s)| Invulnerable Roar & Weapon VFX| Phase Lock Event     |
| `Phase_2`      | 50% to 0% HP   | Unlocks `Canary_M3_RadialQuake`| Cooldown Scale: 0.70 |
+----------------+----------------+-------------------------------+----------------------+
```

### 4.1 Phase Transition Execution
- **Trigger:** Health reaches $\le 50.0\%$ (Canary test threshold; Boss01 uses Phase 2 trigger at $60\%$).
- **Lifecycle Transition:** Boss enters uninterruptible phase transition montage (`AN_Canary_PhaseTransition`, $2.500\text{ s}$).
- **Presentation State:** Embers shift from pale blue to violent cerulean frost-fire; weapon attacks in Phase 2 gain auxiliary frost spark trails.
- **Verification Rule:** Reverting health in testing (or encounter reset) must cleanly reset the phase back to `Phase_1` without lingering tags.

---

## 5. New Weapon & Fourth Player Build Canary

To prove player build extensibility without hardcoding C++ enums, the Canary introduces one new weapon and a fourth player build.

### 5.1 New Weapon: "Silversteel Halberd"
- **Weapon ID:** `Weapon_Player_Halberd`
- **Weapon Type / Style:** Heavy Polearm (compatible with existing two-handed heavy weapon animations).
- **Art Needs:**
  * Static Mesh: `SM_Player_SilversteelHalberd` (Length $190.0\text{ cm}$; blade axe + piercing tip).
  * Materials: Polished damascus steel with blue inlaid runes.
  * Sockets: `SOCKET_Grip_Primary`, `SOCKET_Grip_Secondary`, `SOCKET_BladeStart`, `SOCKET_BladeEnd`.
  * UI Icon: `T_Icon_SilversteelHalberd` ($256 \times 256$ PNG/Texture2D).
- **Action Table Bindings (Input Table Rows):**
  * Light Attack 1: `AN_Player_Halberd_Light01` (Forward thrust, $450\text{ ms}$).
  * Light Attack 2: `AN_Player_Halberd_Light02` (Horizontal cleave, $500\text{ ms}$).
  * Heavy Attack: `AN_Player_Halberd_HeavyCharged` (Wide circular sweep, $850\text{ ms}$).
  * Dodge Attack: `AN_Player_Halberd_DodgeThrust` ($350\text{ ms}$).

### 5.2 Fourth Player Build: "Vanguard"
- **Build ID:** `Build_Vanguard`
- **Display Name:** "Vanguard"
- **Description:** "A heavily armored halberdier with immense reach and poised counter-attacks, trading evasion agility for stagger resistance."
- **Equipped Weapon:** `Weapon_Player_Halberd`
- **Build Definition Scope:** Strictly defined by **Weapon + Display Name + UI Icon**. Conforms to Codex D02: player builds choose equipment and keep current baseline player attributes (120 HP today).
- **Stat Profile Note:** Any custom attribute block (e.g. 650 HP, 140 Stamina, 45 Poise) is **illustrative non-binding design test data only**, strictly NOT for DD-1 or P8 canary acceptance.
- **UI Integration Proof:**
  * Appears in UI build picker (`RPGBuildSelect`) as option 4.
  * Selectable and equippable using the generic `BuildDefinition` data asset without altering the three existing build enums/records (Starter, Strength, Dex).
  * Cleanly unloads and restores original builds without state residue.

---

## 6. Canary Content Verification Checklist

| Verification Item | Pass Criteria | Validation Method |
| :--- | :--- | :--- |
| **Asset Self-Containment** | Zero references to `Boss01` or `SM_Boss01_Greatsword`. | Asset Dependency Graph audit. |
| **Skeleton Compatibility** | Retargets cleanly on shared boss rig with zero bone remapping errors. | Headless FBX / animation validator. |
| **Multi-Window Query** | Move 1 hits twice in a single animation pass without double-registering. | Test driver log verification. |
| **Branching Decision** | Move 4 branches to success on hit, failure on miss, neutral on abort. | Parameterized canary test harness. |
| **Phase Reset Isolation** | Encounter reset cleanly restores Phase 1 state without lingering phase tags. | Sequential run test (Boss01 $\to$ Canary $\to$ Boss01). |
| **Build Picker Extensibility** | Build 4 equips `Weapon_Player_Halberd` with correct UI icon and stats. | PIE build selection test. |

---

## 7. Evidence and Limits

| Claim / Field | Source File / Anchor | Kind | Status / Limit |
| :--- | :--- | :--- | :--- |
| Boss01 Body Skeleton | `Scripts/Editor/import_boss01.py:8` (`SK_CombatMannequin`) | Engine Script Export | Declared asset path; live skeleton uasset to be confirmed in editor |
| Baseline Player HP (120 HP) | `Source/OneBossFight/Player/RPGBossShockwave.h:29` | Engine Source Literal | Measured runtime fact; Vanguard 650 HP is illustrative test data only |
| Non-injective Style Mapping | `Docs/BossCombatReview/Execution/Codex/D02_DATA_MODEL.md:150` | Architectural Design | Design specification; live weapon actor bindings await editor readback |
| Multi-Window Sweep Capability | `Source/OneBossFight/Player/RPGCombatCatalog.h` | Design Contract | Tested via canary mock; live multi-trace execution awaits P2 runtime |
| Phase Threshold Modifiers | `AG2_CANARY_CONTENT_SPEC.md` Section 4 | Test Data Proposal | Illustrative test values; zero live asset or gameplay code created |

### What Could NOT Be Verified Offline:
1. Live skeleton hierarchy of `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin` cannot be inspected without an active Unreal Editor session.
2. In-engine rendering of halberd sockets and Niagara frost-fire particles cannot be verified without editor viewport tools.
