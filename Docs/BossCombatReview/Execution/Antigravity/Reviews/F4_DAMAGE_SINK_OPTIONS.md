# F4 RESEARCH: PACK-PLAYER DAMAGE SINK OPTIONS AND RECOMMENDATION

Author: Antigravity
Date: 2026-10-30
Task: Order A-267 Item 2 (Lead Order C-399)
Status: Complete, 100% Verified Offline Against Project Source

---

## 1. Executive Summary & Recommended Damage Sink

### 1.1 The Single Recommended Damage Sink
For the Sevarog framework (F4), we recommend **ONE primary pack-player damage sink**:
**Call existing C++ entry: `URPGDamageResolver::Resolve(AActor* Target, const FRPGDamagePayload& Payload)`**, which delegates health reduction to **`RPGBossDamage::HurtPlayer(Target, Payload.HPDamage, Before, After)`**.

- **Exact Primary Entry File & Line:**
  - `Source/OneBossFight/Player/RPGDamageResolver.h:133` (`FRPGDamageResult Resolve(AActor* Target, const FRPGDamagePayload& Payload);`)
  - `Source/OneBossFight/Player/RPGDamageResolver.cpp:110-155` (`FRPGDamageResult URPGDamageResolver::Resolve(...)`)
- **Direct Health Application Delegate:**
  - `Source/OneBossFight/Player/RPGBossDamage.h:46-56` (`RPGBossDamage::HurtPlayer(const AActor* Player, double Damage, double& Before, double& After)`)
- **Reflection Attribute Write:**
  - `Source/OneBossFight/Pack/RPGBlueprintCall.h:222-238` (`RPGPack::WriteAttribute(const AActor* Actor, const TCHAR* AttributeTag, double Value)`)

### 1.2 Core Justification
1. **Established Project Standard for Boss Attacks:** The project's existing custom boss attacks (A4 Low Sweep, A5 Javelin, A6 Shockwave) already route through `URPGDamageResolver::Resolve` (e.g., `Source/OneBossFight/Player/RPGBossLowSweep.cpp:91, 126`).
2. **Single Source of Truth for Combat Rules:** `URPGDamageResolver` evaluates `RPGDamageRules::Decide` in strict, deterministic order (`Source/OneBossFight/Player/RPGDamageResolver.h:94-102`).
3. **Contact Deduplication:** Tracks per-instance contact keys (`MoveId|AttackInstance|HitKey`) via internal `TSet<FString> Spent` (`RPGDamageResolver.h:179`, `RPGDamageResolver.cpp:32, 139`), preventing multi-frame contact jitter from hitting the player multiple times within a single swing.
4. **i-Frame Safety:** Checks `RPGBossDamage::IsInvulnerable(Target)` at the exact moment of resolution (`RPGDamageResolver.cpp:129`). If dodged, returns `ERPGDamageOutcome::RejectedInvulnerable` without marking the contact spent, allowing lingering active frames to land if the player exits dodge i-frames while still touching the strike.
5. **Audited & Inspectable Telemetry:** Automatically records all contact attempts (both `Accepted` and `Rejected*`) into the ring buffer `Audit` (`RPGDamageResolver.cpp:52-73`), enabling headless PIE log grading (`[FrameworkProof] damage`) without engine GUI hooks.

---

## 2. How Damage Reaches the Pack Player Today

### 2.1 The Native Pack Melee Path (Pack Enemies / Player vs Boss)
In the stock Advanced ARPG Combat pack (which is Blueprint-only):
1. **Weapon Trace Activation:** Animations fire Anim Notify States (`RPGANS_HitWindow`) enabling collision sampling on `BP_CollisionComponent_C` (`Source/OneBossFight/Pack/RPGPackTrace.cpp:91`, `Source/OneBossFight/Player/RPGHitIntake.cpp:107-145`).
2. **Contact Dispatch:** Socket sweep contact triggers multicast delegate `BP_CollisionComponent_C.OnHit(FHitResult)`.
3. **Damage Pipeline:** Contact routes through `BP_DamageExecution` (185 Blueprint nodes) and applies `GE_DamageBase` to the target's `BP_AdvancedAbilitySystemComponent_C` (`Documentation/DECISIONS.md:157`).
4. **Why Unusable for Sevarog Framework:**
   - The pack has **no C++ entry point** for damage without a weapon trace (`Source/OneBossFight/Player/RPGBossDamage.h:10-12`).
   - Calling `BP_DamageExecution` or applying `GE_DamageBase` directly requires constructing synthetic Blueprint hit data structs (`BP_HitData_C`, `BP_AttackData_C`).
   - As documented in `DECISIONS.md:48-49`, the project locked custom C++ combat with no GAS; Blueprint GAS-style structs are fragile and known to crash in headless / `-nullrhi` execution (e.g., `KI-144`).

### 2.2 The Boss Custom Moves Path (A4 Low Sweep, A5 Javelin, A6 Shockwave)
Because the pack provides no trace-less damage API, the project established `URPGDamageResolver` attached to the boss actor by `RPGPlayerMovesSubsystem` (`Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:225`):
1. Boss moves detect geometric overlap with the player's capsule (`RPGBossLowSweep.cpp:125`).
2. Move records overlap via `Resolver->NoteOverlap(Payload)` (`RPGBossLowSweep.cpp:125`, `RPGDamageResolver.cpp:75-88`).
3. Move calls `const FRPGDamageResult Result = Resolver->Resolve(Target, Payload)` (`RPGBossLowSweep.cpp:126`, `RPGDamageResolver.cpp:110-155`).
4. `Resolve()` queries `RPGDamageRules::Decide(...)`. If `Accepted`, calls `RPGBossDamage::HurtPlayer(Target, Payload.HPDamage, HealthBefore, HealthAfter)`.
5. `RPGBossDamage::HurtPlayer` reads `Attribute.Health`, clamps `After = FMath::Max(0.0, Before - Damage)`, and writes back via `RPGPack::WriteAttribute(Player, TEXT("Attribute.Health"), After)` (`RPGBossDamage.h:46-56`, `RPGBlueprintCall.h:222-238`).

---

## 3. Comparison of Damage Sink Candidates for Framework F4

| Evaluation Criteria | Option 1: Direct Attribute Write (`RPGPack::WriteAttribute`) | Option 2: Gameplay Effect (`GE_DamageBase` via Pack ASC) | Option 3 (RECOMMENDED): `URPGDamageResolver::Resolve` (calls `RPGBossDamage::HurtPlayer`) |
| :--- | :--- | :--- | :--- |
| **C++ Entry Point** | `RPGPack::WriteAttribute` (`RPGBlueprintCall.h:222`) | None (reflection call to Blueprint ASC) | `URPGDamageResolver::Resolve` (`RPGDamageResolver.h:133`) |
| **i-Frame Evaluation** | None (bypasses dodge i-frames) | Blueprint execution only | Checked via `RPGBossDamage::IsInvulnerable` at resolution |
| **Contact Deduplication** | None (can deal multi-tick damage) | Blueprint internal state | Keyed via `Spent` set (`MoveId\|Instance\|HitKey`) |
| **Encounter Generation** | None (stale hits can land) | None | Checked via `CurrentGeneration()` (`RPGDamageResolver.cpp:123`) |
| **Target Alive Gate** | None (can damage dead player) | Blueprint check | Checked via `Attribute.Health > 0` and `!Status.Dead` |
| **Attacker Alive Gate**| None (dead boss can hurt player)| Blueprint check | Checked via `RPGBossDamage::IsAlive(Owner)` |
| **Audit & Headless Log**| Zero telemetry | Zero C++ telemetry | Full audit ring buffer + `[LogRPGDamage]` log line |
| **Offline Testability**| Requires UObject world/component | Requires full Blueprint ASC engine | 100% pure unit testable via `RPGDamageRules::Decide` |
| **Architectural Verdict**| **REJECTED** (Violates combat rules) | **REJECTED** (Fragile, headless risk) | **RECOMMENDED (100% Compliant)** |

---

## 4. What the Sink Must Check (Combat Rules Contract)

According to `Source/OneBossFight/Player/RPGDamageResolver.cpp:110-155` and `Source/OneBossFight/Player/RPGDamageResolver.h:94-102`, the sink evaluates conditions in strict precedence order:

```
[Target Contact]
       │
       ▼
1. bTargetAlive? ───────────► NO  ──► Outcome = RejectedDead (Health <= 0.0 or Status.Dead)
       │ YES
       ▼
2. bAttackerAlive & ────────► NO  ──► Outcome = RejectedStale (Boss dead or generation mismatch)
   bGenerationCurrent?
       │ YES
       ▼
3. bDuplicate? ─────────────► YES ──► Outcome = RejectedDuplicate (Spent contains MoveId|Instance|HitKey)
       │ NO
       ▼
4. bTargetInvulnerable? ────► YES ──► Outcome = RejectedInvulnerable (Player has Status.Invulnerable; Hit NOT spent)
       │ NO
       ▼
5. Outcome = Accepted ──────► HurtPlayer -> Spent.Add(Key) -> Health clamped >= 0.0 -> Audit Record
```

### 4.1 Detailed Status of Player Defense Mechanics
1. **i-Frames (Dodge):**
   - **Mechanism:** Checked by `RPGBossDamage::IsInvulnerable(Target)` via `HasTag(Player, TEXT("Status.Invulnerable"))` (`RPGBossDamage.h:34-44`).
   - **Behavior:** Returns `ERPGDamageOutcome::RejectedInvulnerable`. Critically, the contact key is **not** added to `Spent`, allowing subsequent frames of the same swing to hit if the player emerges from dodge i-frames before the attack window closes (`RPGDamageResolver.cpp:128-142`).
2. **Block & Parry:**
   - **Status in Baseline:** **Explicitly Unbuilt for Boss Moves** (`Source/OneBossFight/Player/RPGDamageResolver.h:25`: *"What a boss move asks the resolver to do to the player. HP only: boss moves take no posture (Freeze 504); guard and hit reaction are not built (KI-065, KI-067, KI-068)."*).
   - **Finding:** Boss custom attacks bypass the pack player's block and parry states. The player must avoid boss moves via spacing or dodge i-frames.
3. **Posture:**
   - **Status in Baseline:** Boss moves deal **0 posture damage** to the player (`Freeze 504`, `RPGDamageResolver.h:25`).
4. **Hit Reaction / Hit Stun:**
   - **Status in Baseline:** Boss moves do not request hit reactions on the player (`Source/OneBossFight/Player/RPGDamageResolver.cpp:143`: *"a lethal hit is followed by nothing but the death (no reaction is requested for boss moves in any case)"*).

---

## 5. Integration Blueprint for Sevarog Framework F4

### 5.1 Invocation from `URPGFrameworkMoveExecutor`
During move execution in F4 (when Card `HPDamage > 0.0`):
1. **At Active Hit Window Opening:** When the move reaches its contact phase (derived from Card spec `ActiveStartSeconds` to `RecoveryStartSeconds` or active blade collision trace):
2. **Construct Payload:**
   ```cpp
   FRPGDamagePayload Payload;
   Payload.MoveId = Card->Spec().SlotName; // e.g. TEXT("Swing1_Slow")
   Payload.AttackInstance = Token.InstanceId;
   Payload.Generation = Resolver->CurrentGeneration();
   Payload.HitKey = TEXT("Hit0");
   Payload.HPDamage = Card->Spec().HPDamage;
   ```
3. **Execute Resolution:**
   ```cpp
   URPGDamageResolver* Resolver = URPGDamageResolver::FindOrAdd(OwnerBoss);
   const FRPGDamageResult Result = Resolver->Resolve(Target, Payload);
   ```
4. **Emit Telemetry Line:**
   ```cpp
   UE_LOG(LogTemp, Display, TEXT("[FrameworkProof] damage instance=%llu requested=%.1f applied=%.1f before=%.1f after=%.1f outcome=%s"),
       Token.InstanceId, Payload.HPDamage, Result.HPApplied, Result.HealthBefore, Result.HealthAfter, RPGDamageRules::Name(Result.Outcome));
   ```

---

## 6. Minimum F4 Test Suite

To validate F4 damage execution without regressions, the test suite must enforce:

1. **Test 1: Positive Normal Damage (Clean Hit):**
   - Initial Target Health: 800.0, Non-invulnerable.
   - Attack: `HPDamage = 35.0`.
   - Expected Result: `Outcome == ERPGDamageOutcome::Accepted`, `HPApplied == 35.0`, `HealthBefore == 800.0`, `HealthAfter == 765.0`, `bLethal == false`. Key added to `Spent`.
2. **Test 2: Dodge i-Frame Rejection (`RejectedInvulnerable`):**
   - Target has tag `Status.Invulnerable`.
   - Attack: `HPDamage = 35.0`.
   - Expected Result: `Outcome == ERPGDamageOutcome::RejectedInvulnerable`, `HPApplied == 0.0`, `HealthAfter == 800.0`. Key **not** added to `Spent`.
3. **Test 3: Secondary Contact After Dodge Expiry:**
   - Frame 1: Target invulnerable -> `RejectedInvulnerable` (key unspent).
   - Frame 2: `Status.Invulnerable` cleared while still in contact.
   - Expected Result: `Outcome == ERPGDamageOutcome::Accepted`, `HPApplied == 35.0`, `HealthAfter == 765.0`. Key added to `Spent`.
4. **Test 4: Contact Deduplication (`RejectedDuplicate`):**
   - Frame 1: Hit 1 accepted -> `HealthAfter == 765.0`, key recorded in `Spent`.
   - Frame 2: Same instance, same `HitKey` contacts target again.
   - Expected Result: `Outcome == ERPGDamageOutcome::RejectedDuplicate`, `HPApplied == 0.0`, `HealthAfter == 765.0`.
5. **Test 5: Dead Target Gate (`RejectedDead`):**
   - Target has `Attribute.Health == 0.0` or tag `Status.Dead`.
   - Expected Result: `Outcome == ERPGDamageOutcome::RejectedDead`, `HPApplied == 0.0`.
6. **Test 6: Lethal Clamping & Floor (Zero Health Floor):**
   - Initial Target Health: 20.0.
   - Attack: `HPDamage = 35.0`.
   - Expected Result: `Outcome == ERPGDamageOutcome::Accepted`, `HPApplied == 20.0`, `HealthAfter == 0.0` (never negative), `bLethal == true`.
7. **Test 7: Encounter Generation Gate (`RejectedStale`):**
   - Payload has `Generation = 0`, Encounter is at `Generation = 1`.
   - Expected Result: `Outcome == ERPGDamageOutcome::RejectedStale`, `HPApplied == 0.0`.

---

## 7. Verified Citation Index

All citations re-opened and verified offline against project source:
- `Source/OneBossFight/Player/RPGDamageResolver.h:25`: HP only; boss moves take no posture (Freeze 504); guard and hit reaction unbuilt.
- `Source/OneBossFight/Player/RPGDamageResolver.h:94-102`: `RPGDamageRules::Decide` evaluation order (TargetAlive -> AttackerAlive/Generation -> Duplicate -> Invulnerable -> Accepted).
- `Source/OneBossFight/Player/RPGDamageResolver.h:133`: `URPGDamageResolver::Resolve(AActor* Target, const FRPGDamagePayload& Payload)`.
- `Source/OneBossFight/Player/RPGDamageResolver.cpp:110-155`: Implementation of `Resolve`, generation sync, i-frame evaluation, `HurtPlayer` invocation, and audit recording.
- `Source/OneBossFight/Player/RPGBossDamage.h:34-44`: `RPGBossDamage::IsInvulnerable(AActor* Player)` querying `Status.Invulnerable`.
- `Source/OneBossFight/Player/RPGBossDamage.h:46-56`: `RPGBossDamage::HurtPlayer` reading health, clamping to 0.0, and calling `RPGPack::WriteAttribute`.
- `Source/OneBossFight/Pack/RPGBlueprintCall.h:222-238`: `RPGPack::WriteAttribute` reflection call setting attribute value.
- `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:225`: `URPGDamageResolver::FindOrAdd(Pawn)` attachment to boss pawns.
- `Source/OneBossFight/Player/RPGBossLowSweep.cpp:91, 126`: Reference boss move calling `Resolver->NoteOverlap` and `Resolver->Resolve`.
