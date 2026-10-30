# F6 DESIGN: FRAMEWORK BOSS AS TARGET, LIFE PROVIDER, AND MINIMAL PHASE AUTHORITY

Author: Antigravity  
Date: 2026-10-30  
Task: Order A-291 (Lead Order C-413)  
Status: Authoring Complete, Offline Verified Against Project Source and Pack Assets  

---

## 1. Executive Summary & Problem Statement

### 1.1 The Ghost Boss Problem in F3-F5
Throughout proof phases F3, F4, and F5b, the Sevarog framework boss (`ARPGFrameworkBossCharacter`) was developed strictly as an autonomous **attacker**:
- Evaluating candidate move cards (`FRPGBossMoveCard`) via `RPGBossMoveSelector::Decide`.
- Executing montage playbacks through `URPGFrameworkMoveExecutor`.
- Driving kinematic root motion and resolving damage against the player via `URPGDamageResolver::Resolve`.

However, as an in-world combatant, the framework boss is currently an untouchable **ghost**:
1. **Disabled Collision & Damage Gate:** In `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:19-21`:
   - Line 19: `GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);`
   - Line 21: `SetCanBeDamaged(false);`
   The character mesh has zero collision query representation, and `CanBeDamaged` explicitly rejects engine damage queries.
2. **Subsystem Filter Blindness:** In `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:95-105`, `URPGPlayerMovesSubsystem::IsPackBoss` checks strictly for `BP_ExampleGreatSwordBoss_C`. In `Source/OneBossFight/Player/RPGHitIntake.cpp:399-404`, any hit received from player weapon traces on an actor not matching `IsPackBoss` is classified as `OtherHitCount` and ignored.
3. **Missing Health & Lifecycle State:** The framework boss has no authoritative Health/MaxHealth attributes, no death state machine, no generation reset handling, and no phase authority.

### 1.2 Objective of Order A-291
This design document establishes the concrete architecture for F6 to turn the framework boss into a fully responsive, damageable combat target:
1. **Intake & Detection Seam (Section 2):** Define collision profiles, skeletal physics asset requirements, and interface hooks required for the pack player's weapon traces to register hits without modifying any pack Blueprints.
2. **Health, Resolver, Generation & Death (Section 3):** Compare HP storage options (Native C++ vs Runtime Pack Component), wire the `URPGDamageResolver` life provider seam (`InIsAlive = HP > 0`), handle encounter generation resets, and define death authority.
3. **Minimal Phase Authority (Section 4):** Author data-driven phase thresholds, strict monotonic latching, and neutral-only transition gating mapped directly to `BOSS-PHS-001..006`.
4. **Concrete Recommendation & Honest Unknowns (Section 5):** Recommend a single coherent implementation path and detail all remaining unverified assumptions.

---

## 2. Pack Player Hit Detection Prerequisites on Framework Boss

### 2.1 The Pack Player Weapon Trace Pipeline
The stock player character (`BP_CombatPlayerCharacter`) deals melee damage via sweeping socket traces:
1. **Trace Component Activation:** During attack montages, anim notify states (`RPGANS_HitWindow` or pack equivalent) activate collision sampling on `BP_CollisionComponent_C`.
2. **Socket Sweeps:** The active `BP_WeaponTraceTarget_C` sweeps collision spheres between weapon sockets (e.g. `Socket_Start`, `Socket_End`) against configured `CollisionObjectTypes` (`Source/OneBossFight/Pack/RPGPackTrace.cpp:40-42`).
3. **Object Query Types:** The sweep queries `ECC_Pawn` and `ECC_PhysicsBody` (`Config/DefaultEngine.ini:97-101`).
4. **Event Dispatch:** When the weapon sweep touches a blocking/overlapping primitive, `BP_CollisionComponent_C` fires its multicast delegate `OnHit(FHitResult HitResult)`.

### 2.2 Framework Boss Collision & Primitive Requirements
To receive hits from the player's weapon sweeps without editing pack Blueprints, `ARPGFrameworkBossCharacter` must satisfy four primitive requirements:

1. **Capsule Component Collision:**
   - Object Type: `ECC_Pawn` (`CollisionChannel = ECC_Pawn`).
   - Collision Enabled: `ECollisionEnabled::QueryOnly` (or `QueryAndPhysics`).
   - Responses: Block or Overlap `ECC_Pawn`, `ECC_WorldDynamic`, `ECC_Camera` (Ignore per `DefaultEngine.ini:100`).
2. **Skeletal Mesh Component Collision (`GetMesh()`):**
   - Currently hardcoded in `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:19` to `ECollisionEnabled::NoCollision`.
   - **Required Fix:** Set `GetMesh()->SetCollisionEnabled(ECollisionEnabled::QueryOnly);` (or `QueryAndPhysics`).
   - Collision Profile: Set profile to `CharacterMesh` (`Config/DefaultEngine.ini:101`), which ignores `Visibility` and `Camera` but blocks/overlaps `Pawn` queries.
3. **Physics Asset & Per-Bone Hit Registration:**
   - In `Source/OneBossFight/Player/RPGHitIntake.cpp:378-395`, `BuildRecord` records `Record.HitBone = HitResult.BoneName;`.
   - If a skeletal mesh has no valid Physics Asset (`PhysicsAsset`), complex/per-bone traces against the skeletal mesh fail or return `HitBone = NAME_None`.
   - **Prerequisite:** The Sevarog skeletal mesh (`Content/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog.uasset`) must have an assigned `UPhysicsAsset` with kinematic bodies on major bones (`pelvis`, `spine_01`, `head`, `upperarm_l`, `upperarm_r`, etc.).
4. **Damage Enablement Flag:**
   - Currently hardcoded in `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:21` to `SetCanBeDamaged(false);`.
   - **Required Fix:** Set `SetCanBeDamaged(true);`.

### 2.3 Blueprint Interfaces & Intake Routing
In the stock pack, `BP_CollisionComponent` routes hits through `BP_DamageExecution` calling `BP_DamageInterface.OnDamageApplied(DamagedActor, EventData, HitResult)` (`Content/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/Interfaces/BP_DamageInterface.uasset`).

However, the OneBossFight project has already established a decoupled C++ intake architecture that **bypasses pack damage execution Blueprints entirely**:
- **Existing C++ Intake Binding:** In `Source/OneBossFight/Player/RPGHitIntake.cpp:336-377`, `URPGHitIntake::TryBind()` binds `HandlePackHit` directly to `BP_CollisionComponent_C.OnHit(FHitResult)` via engine reflection.
- **The Boss Recognition Seam:**
  In `Source/OneBossFight/Player/RPGHitIntake.cpp:397-404`:
  ```cpp
  void URPGHitIntake::HandlePackHit(FHitResult HitResult)
  {
      AActor* Target = HitResult.GetActor();
      if (!Target || !URPGPlayerMovesSubsystem::IsPackBoss(Target))
      {
          ++OtherHitCount;
          return;
      }
      ...
  }
  ```
  And in `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:95-105`:
  ```cpp
  bool URPGPlayerMovesSubsystem::IsPackBoss(const AActor* Actor)
  {
      for (const UClass* Class = Actor ? Actor->GetClass() : nullptr; Class; Class = Class->GetSuperClass())
      {
          if (Class->GetName() == TEXT("BP_ExampleGreatSwordBoss_C"))
          {
              return true;
          }
      }
      return false;
  }
  ```
- **Prerequisite for F6 Hit Registration:**
  To register player hits on the framework boss without modifying pack Blueprints, `URPGPlayerMovesSubsystem::IsPackBoss` (or an adjacent `IsTargetableBoss` predicate) must be extended to recognize `ARPGFrameworkBossCharacter` (or check for a native C++ marker interface `IRPGBossTarget`):
  ```cpp
  if (Actor->IsA<ARPGFrameworkBossCharacter>() || Class->GetName() == TEXT("BP_ExampleGreatSwordBoss_C"))
  {
      return true;
  }
  ```
  Once recognized, `URPGHitIntake::HandlePackHit` captures the hit, generates `FRPGHitRecord` (`Source/OneBossFight/Player/RPGHitIntake.h:17-49`), scales damage, applies posture/bleed, and broadcasts `OnBossHit`.

---

## 3. Boss HP Architecture, Resolver Seams, Generation Reset, and Death

### 3.1 Comparison of Boss HP Storage Options

| Criterion | Option 1: Native C++ Framework HP (`FRPGBossAttributes`) | Option 2: Runtime Pack Component (`BP_AttributesComponent_C`) | Option 3 (RECOMMENDED): Native C++ Authoritative HP with Adapter Bridge |
| :--- | :--- | :--- | :--- |
| **Storage Location** | Native C++ fields on `ARPGFrameworkBossCharacter` | Dynamically spawned `BP_AttributesComponent_C` | Authoritative native C++ fields + C++ Interface (`IRPGBossLifeInterface`) |
| **Performance Overhead** | Zero (direct field access) | High (`ProcessEvent` reflection + memory allocations per hit) | Zero on hot path; minimal when bridging legacy systems |
| **ABI & Cook Stability** | 100% stable; pure C++ compilation | Fragile (relies on loading Blueprint class path at runtime) | 100% stable; compiled natively into `OneBossFight` module |
| **Headless / -nullrhi Safety**| Complete immunity from Blueprint crashes | Known crash hazard if asset dependencies uninitialized (`KI-144`)| Complete immunity from Blueprint crashes |
| **Intake Compatibility** | Requires modifying `URPGHitIntake` attribute read/write | Fully transparent to `RPGPack::ReadAttribute` / `WriteAttribute` | Native check first, falls back to `RPGPack::ReadAttribute` for pack boss |
| **Offline Testability** | Pure unit testable with synthetic structs | Requires full engine UObject world & Blueprint bytecode | 100% offline testable via mock interface |
| **Architectural Verdict** | Viable, but creates bifurcated API | **REJECTED** (Fragile, heavy runtime cost, headless risk) | **RECOMMENDED** (Clean, deterministic, backward-compatible) |

### 3.2 Authoritative Native Health Architecture (Option 3 Details)
1. **Native Character Fields:**
   `ARPGFrameworkBossCharacter` holds authoritative state:
   ```cpp
   float CurrentHealth = 800.0f;
   float MaxHealth = 800.0f;
   int32 EncounterGeneration = 1;
   bool bDead = false;
   ```
2. **Target Life Interface (`IRPGBossLifeInterface`):**
   ```cpp
   class IRPGBossLifeInterface
   {
   public:
       virtual float GetCurrentHealth() const = 0;
       virtual float GetMaxHealth() const = 0;
       virtual bool ApplyHealthDelta(float Delta, float& OutNewHealth) = 0;
       virtual bool IsBossAlive() const = 0;
       virtual int32 GetBossGeneration() const = 0;
   };
   ```
3. **Decoupled Intake Adjustment:**
   In `Source/OneBossFight/Player/RPGHitIntake.cpp:258-275` (`AdjustBossHealth`):
   ```cpp
   if (IRPGBossLifeInterface* Life = Cast<IRPGBossLifeInterface>(Boss))
   {
       float NewHealth = 0.0f;
       Life->ApplyHealthDelta(static_cast<float>(Adjust), NewHealth);
       return;
   }
   // Fallback to legacy pack reflection:
   RPGPack::WriteAttribute(Boss, TEXT("Attribute.Health"), NewHealth);
   ```

### 3.3 The Resolver Seam & Life Provider
`URPGDamageResolver` (`Source/OneBossFight/Player/RPGDamageResolver.h:133-135`) already provides the exact plug-in seam for life and generation authority:
```cpp
void SetLifeProvider(TFunction<bool()> InIsAlive, TFunction<int32()> InGeneration);
void ClearLifeProvider();
bool HasLifeProvider() const;
```
- In `ARPGFrameworkBossCharacter::InitializeProof` (or `BeginPlay`):
  ```cpp
  Resolver->SetLifeProvider(
      [this]() { return CurrentHealth > 0.0f && !bDead; },
      [this]() { return EncounterGeneration; }
  );
  ```
- **Resolution Behavior:**
  When `URPGDamageResolver::Resolve` executes (`Source/OneBossFight/Player/RPGDamageResolver.cpp:110-155`):
  1. Calls `SyncGeneration()`, querying `ProviderGeneration()`. If the payload generation does not match `EncounterGeneration`, returns `ERPGDamageOutcome::RejectedStale` (`RPGDamageResolver.cpp:123, 148`).
  2. Calls `ProviderIsAlive()`. If false, returns `ERPGDamageOutcome::RejectedDead` or `RejectedStale` (`RPGDamageResolver.cpp:121, 147`).
  3. Evaluates `RPGDamageRules::Decide` (`RPGDamageResolver.h:94-102`) deterministically.

### 3.4 Generation Reset & Death Flow
1. **Generation Reset (`BOSS-EXE-001`, `BOSS-DEF-001`):**
   Modelled directly on legacy `URPGBossEncounter::ResetEncounter` (`Source/OneBossFight/Player/RPGBossEncounter.cpp:310-325`):
   - Increments `++EncounterGeneration;` (instantly invalidates all in-flight payloads and active attack tracking).
   - Resets `CurrentHealth = MaxHealth;`.
   - Clears status tags (`bDead = false; bPhaseTwoLatched = false;`).
   - Aborts active playback on `URPGFrameworkMoveExecutor` via `Stop()` / clean exit.
   - Repositions character to initial arena spawn transform.
   - Emits structured log: `[FrameworkProof] encounter_reset gen=<n> hp=<max>`.
2. **Death Authority (`RPGBossDeath` Integration):**
   Modelled on `Source/OneBossFight/Player/RPGBossDeath.h:160-189`:
   - Trigger: In `ApplyHealthDelta`, when `CurrentHealth <= 0.0f`, set `CurrentHealth = 0.0f; bDead = true;`.
   - Halt: Cease all move selection and abort active executor playback.
   - Guarded Pose / Niagara Remains: Disable capsule collision (`ECC_Pawn`), freeze pose at terminal frame or trigger death animation clip, and spawn death remains/burst (`RPGBossDeath.h:195-200`).
   - Inform Resolver: Subsequent calls to `ProviderIsAlive()` return false, ensuring all pending attacks cleanly fail with `RejectedDead`.

---

## 4. Minimal Phase Authority Mapped to BOSS-PHS-001..006

### 4.1 Phase Authority Specification & Core Invariants
To prevent combat glitches, state desynchronization, and exploit loops, the framework phase authority enforces three strict mathematical invariants:
1. **Data-Driven Configuration:** Authored in `URPGBossFrameworkProfile` (e.g. `PhaseTwoThresholdFraction = 0.60f`).
2. **Strict Monotonicity (`bPhaseTwoLatched`):** The transition from Phase 1 to Phase 2 is an absorbing Markov state. Once latched, healing, attribute manipulation, or posture breaks cannot unlatch or re-trigger the transition sequence (`BOSS-PHS-003`).
3. **Safe Transition Policy (Neutral Gating):** A phase transition cannot interrupt an active attack swing, grab execution, or player riposte. If the threshold is crossed while the boss is busy, the transition is queued (`QueuedBehindStagger` / `QueuedBehindExecution`) and executes exclusively upon returning to neutral (`BOSS-PHS-002`).

### 4.2 Mapping to BOSS-PHS Requirements and Exact Witnesses

#### BOSS-PHS-001: Phase Rule Set
- **Requirement:** Reducing boss HP below threshold (e.g. 60%) triggers Phase 2 transition sequence and moveset expansion.
- **Framework Implementation:**
  - Evaluated in `RPGBossRules::ResolveTransition(Flags, Health, MaxHealth, Fraction)` (`Source/OneBossFight/Player/RPGBossRules.h:72-80`).
  - When `Health / MaxHealth <= 0.60f` and `!bPhaseTwoLatched`, returns `ETransitionResult::Start`.
  - Framework switches active candidate profile subset to Phase 2 move cards (`PhaseId = 2`), enabling expanded attacks (e.g. MC-04 heavy combo, MC-05 gap-closer).
- **Exact Witness Observable:**
  Structured log line:  
  `[FrameworkProof] phase_transition from=1 to=2 threshold=0.60 hp=480.00 max=800.00`

#### BOSS-PHS-002: Safe Transition Policy
- **Requirement:** Phase transition cannot interrupt active grab or player critical riposte; waits for neutral/safe window.
- **Framework Implementation:**
  - Evaluated via `RPGBossRules::ResolveTransition` (`RPGBossRules.h:77`): if `Flags.bStaggered` or `Executor->IsBusy()`, returns `ETransitionResult::QueuedBehindStagger` or defers transition.
  - The transition sequence is only started when `Executor->IsClean()` and no player riposte/stagger window is active.
- **Exact Witness Observable:**
  Structured log sequence:  
  1. `[FrameworkProof] phase_transition_deferred reason=ExecutorBusy move=MC-01`  
  2. `[FrameworkProof] move_cleanup move=MC-01 state=Neutral`  
  3. `[FrameworkProof] phase_transition_start state=Neutral`

#### BOSS-PHS-003: Phase Monotonicity
- **Requirement:** Healing boss above phase threshold does not re-trigger phase transition or reset phase state (monotonicity).
- **Framework Implementation:**
  - Latch variable: `bool bPhaseTwoLatched = false;`.
  - When Phase 2 starts, `bPhaseTwoLatched = true;`.
  - `RPGBossRules::ResolveTransition` checks `if (F.bPhaseTwo) { return ETransitionResult::AlreadyDone; }` (`Source/OneBossFight/Player/RPGBossRules.h:75`).
  - If boss health increases above 60% (e.g. 700 / 800), `ResolveTransition` returns `AlreadyDone`. Active phase remains Phase 2.
- **Exact Witness Observable:**
  Headless proof log demonstrating health increase without transition:  
  `[FrameworkProof] target_health_adjusted old=450.00 new=700.00`  
  `[FrameworkProof] phase_eval result=AlreadyDone phase=2`

#### BOSS-PHS-004: Fair Heal Punish
- **Requirement:** Heal punish move (MC-03/MC-05) triggers only when player initiates flask drink within reachable band.
- **Framework Implementation:**
  - Move card selector inspects player gameplay tags (`Status.Action.DrinkingFlask` or `Status.Consuming`).
  - Candidate cards flagged `bHealPunish = true` receive a score multiplier (+50.0) when the tag is present AND player is within reach band ($400\text{cm} \le \text{Distance} \le 950\text{cm}$).
  - Gated by cooldown to avoid unfair chaining.
- **Exact Witness Observable:**
  Structured selector log line:  
  `[FrameworkProof] selector_decision card=MC-05 trigger=HealPunish player_tag=Status.Action.DrinkingFlask dist=620.00`

#### BOSS-PHS-005: Anti-Cheese with Counterplay
- **Requirement:** Extreme player kiting or hugging triggers anti-greed/gap-closer moves, preventing exploit loops.
- **Framework Implementation:**
  - Extreme Range (> 1200 cm for > 3.0 s): Selector boosts weight of gap-closer card (MC-05) to break kiting stall.
  - Ultra-Close Range (< 150 cm for > 4.0 s): Selector triggers defensive disengage or quick sweep card to prevent hugging blind-spot exploits.
- **Exact Witness Observable:**
  Structured selector log line:  
  `[FrameworkProof] anti_cheese_trigger condition=Kiting distance=1350.00 chosen=MC-05`

#### BOSS-PHS-006: Phase State Deactivation & Generation Monotonicity
- **Requirement:** Phase authority cleanly resets upon player respawn / encounter reset, restoring Phase 1 while incrementing generation token.
- **Framework Implementation:**
  - Handled in `ResetEncounter()`:
    ```cpp
    ++EncounterGeneration;
    bPhaseTwoLatched = false;
    CurrentPhase = 1;
    ```
  - Guarantees encounters are isolated and reproducible across generations.
- **Exact Witness Observable:**
  Structured reset log line:  
  `[FrameworkProof] encounter_reset gen=2 phase=1 hp=800.00 latched=false`

---

## 5. Concrete Recommendation & Honest Unknowns

### 5.1 Single Concrete Recommendation
We recommend **Option 3: Authoritative Native C++ Boss Health & Phase Authority on `ARPGFrameworkBossCharacter` with Direct Intake Integration**.

**Key Steps for Implementation:**
1. **Collision & Damage Flag Setup:** In `ARPGFrameworkBossCharacter::ARPGFrameworkBossCharacter()`:
   - Change line 19 to `GetMesh()->SetCollisionEnabled(ECollisionEnabled::QueryOnly);`.
   - Set `GetMesh()->SetCollisionProfileName(TEXT("CharacterMesh"));`.
   - Change line 21 to `SetCanBeDamaged(true);`.
2. **Subsystem Boss Target Recognition:** In `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:95-105`:
   - Extend `IsPackBoss` to accept `ARPGFrameworkBossCharacter`:
     ```cpp
     bool URPGPlayerMovesSubsystem::IsPackBoss(const AActor* Actor)
     {
         if (!Actor) return false;
         if (Actor->IsA<ARPGFrameworkBossCharacter>()) return true;
         for (const UClass* Class = Actor->GetClass(); Class; Class = Class->GetSuperClass())
         {
             if (Class->GetName() == TEXT("BP_ExampleGreatSwordBoss_C")) return true;
         }
         return false;
     }
     ```
3. **Native Health & Life Provider Wiring:**
   - Add `float Health = 800.f; float MaxHealth = 800.f; int32 Generation = 1; bool bDead = false;` to `ARPGFrameworkBossCharacter`.
   - Implement `IRPGBossLifeInterface` on `ARPGFrameworkBossCharacter`.
   - Wire `URPGDamageResolver::SetLifeProvider` in `ARPGFrameworkBossCharacter::InitializeProof`.
4. **Intake Bridge:** In `URPGHitIntake::AdjustBossHealth`, check for `IRPGBossLifeInterface` first, bypassing Blueprint reflection for the framework boss while preserving full backwards compatibility for the legacy pack boss.
5. **Phase Authority Integration:** Add `bPhaseTwoLatched` and evaluate `RPGBossRules::ResolveTransition` within character tick, switching the active profile candidate phase from 1 to 2 when crossed in neutral.

### 5.2 Honest List of Unknowns & UNVERIFIED Assumptions
1. **[UNVERIFIED - Physics Asset Bone Coverage]:** Whether the stock Sevarog physics asset (`Content/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog_PhysicsAsset.uasset`) has full primitive capsule coverage across all lower extremities and cape bones. If cape bones lack collision bodies, traces passing through the lower cloak may register as misses.
2. **[UNVERIFIED - Double Hit Sweep Priority]:** When player weapon sweeps hit both the capsule component and the skeletal mesh in the same physics frame, whether `BP_CollisionComponent_C` raises one merged `OnHit` event or two separate events. `URPGHitIntake.cpp:430-440` handles same-frame duplicate montage hits, but priority ordering between capsule and bone hits under live sweep traces remains to be verified in PIE.
3. **[UNVERIFIED - Player HUD Health Bar Linkage]:** `RPGBossHud` (`Source/OneBossFight/UI/RPGBossHud.cpp`) currently looks for `BP_AttributesComponent_C` to update the boss health bar. If the framework boss uses native health without an attribute component, the player on-screen boss HUD will remain blank unless bridged via `IRPGBossLifeInterface` or a lightweight attribute component facade.

