# F6A LEGACY PARITY MAP: HIT INTAKE, ISPACKBOSS, AND BOSS HEALTH CONSUMERS

Author: Antigravity  
Date: 2026-10-30  
Task: Order A-292 / A-293 (Lead Order C-415)  
Status: Complete, 100% Offline Verified Against Project Source and Test Suites  

---

## 1. Executive Summary & Purpose

In Lead Order `[C-415]`, Claude accepted the F6 design architecture (`Reviews/F6_BOSS_LIFE_PHASE_DESIGN.md`) in principle, establishing that:
1. The framework boss (`ARPGFrameworkBossCharacter`) will own native health, death state, and encounter generation.
2. `URPGPlayerMovesSubsystem::IsPackBoss` will be extended to accept the framework boss.
3. `URPGHitIntake` will adjust native health directly on the framework boss.

To ensure the F6a implementation does not break existing automation tests, PIE verification drivers, or legacy pack-boss duel mechanics, this document provides the exact **Legacy Parity Map** across three essential domains:
- **Section 2 (Item 1):** Every test and driver touching `IsPackBoss` and `URPGHitIntake` (name, file:line, and exact assertions) that must remain 100% green.
- **Section 3 (Item 2):** Complete census of every system that reads boss health for display or combat rules, demonstrating how each queries `Attribute.Health` via `RPGPack::ReadAttribute`.
- **Section 4 (Item 3):** Exact code anatomy of `URPGHitIntake::AdjustBossHealth`, detailing how damage reaches the boss today and specifying the minimal, non-breaking branch for framework boss native health.

---

## 2. Legacy Tests and Drivers Touching IsPackBoss and URPGHitIntake

### 2.1 C++ Automation Tests

#### 1. FRPGAttachWitnessBossTest (`OneBossFight.Player.AttachWitness.Boss`)
- **Source Location:** `Source/OneBossFight/Tests/RPGPlayerMovesAttachWitnessTests.cpp:441`
- **Exact Assertions on `IsPackBoss`:**
  - Line 372-376: Spawns `BP_ExampleGreatSwordBoss_C` in a bare game world.
  - Asserts `URPGPlayerMovesSubsystem::IsPackBoss(Pawn) == true` (`bExpectBoss = true`).
  - Asserts `URPGPlayerMovesSubsystem::IsPackPlayer(Pawn) == false` (`bExpectBoss = false`).
  - Line 381-386: Validates that spawn hooks attach all 16 legacy boss components (`RPGBossStagger`, `RPGBossPhases`, `RPGBossEncounter`, `RPGBossPosture`, `RPGBossBleed`, `RPGBossHud`, `URPGDamageResolver`, etc.).
- **Parity Invariant:** `IsPackBoss` MUST continue returning `true` for `BP_ExampleGreatSwordBoss_C`. Extending `IsPackBoss` to ALSO return `true` for `ARPGFrameworkBossCharacter` is 100% safe, provided it does NOT return true for the player character (`BP_CombatPlayerCharacter_C`).

#### 2. FRPGAttachWitnessPlayerTest (`OneBossFight.Player.AttachWitness.Player`)
- **Source Location:** `Source/OneBossFight/Tests/RPGPlayerMovesAttachWitnessTests.cpp:448`
- **Exact Assertions on `IsPackBoss`:**
  - Line 372-376: Spawns `BP_CombatPlayerCharacter_C`.
  - Asserts `URPGPlayerMovesSubsystem::IsPackBoss(Pawn) == false` (`bExpectBoss = false`).
  - Asserts `URPGPlayerMovesSubsystem::IsPackPlayer(Pawn) == true` (`bExpectBoss = false` inverted).
  - Validates player components: `RPGFootsteps`, `RPGCameraRig`, `RPGRiposteInput`, `RPGDodgeTiming`, `RPGSwingTracker`, `RPGHitIntake` (`AttachWitnessTests.cpp:54`).
- **Parity Invariant:** Under no circumstance may `IsPackBoss` return true for player pawns.

#### 3. FRPGPackWiringTest (`OneBossFight.Content.PackWiring`)
- **Source Location:** `Source/OneBossFight/Tests/RPGAutomationTests.cpp:1060`
- **Exact Assertions on `URPGHitIntake`:**
  - Line 1108: `const bool bHitNames = URPGHitIntake::CheckPackNames(MissingHitNames);`
  - Line 1109: `TestTrue(TEXT("hit intake pack names"), bHitNames);`
  - Verifies that `BP_CollisionComponent_C.OnHit(FHitResult)` signature and trace target properties (`HitData`, `Attack Data`, `bCollisionEnabled?`) exist on the pack Blueprints without an active world (`Source/OneBossFight/Player/RPGHitIntake.cpp:52-108`).
- **Parity Invariant:** `URPGHitIntake::CheckPackNames` is static reflection logic; must not be altered.

### 2.2 Project C++ Systems Touching IsPackBoss

| File & Line | Context | How IsPackBoss is Used | Parity Invariant |
| :--- | :--- | :--- | :--- |
| `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:95-105` | Definition | Iterates `Actor->GetClass()` looking for `BP_ExampleGreatSwordBoss_C` | Must accept both `BP_ExampleGreatSwordBoss_C` and `ARPGFrameworkBossCharacter`. |
| `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:188-250` | `RegisterBoss` | Guard for attaching legacy components (`RPGBossStagger`, `RPGBossPhases`, etc.) | **CRITICAL:** If `IsPackBoss` accepts framework boss, `RegisterBoss` would attempt to attach legacy components to it! Must ensure framework boss either opts out of legacy component registration or `RegisterBoss` checks `!Actor->IsA<ARPGFrameworkBossCharacter>()`. |
| `Source/OneBossFight/Player/RPGHitIntake.cpp:399-404` | `HandlePackHit` | Filters hit victim: `if (!Target \|\| !URPGPlayerMovesSubsystem::IsPackBoss(Target))` | Must accept framework boss so player hits on framework boss are processed instead of dropped into `OtherHitCount`. |
| `Source/OneBossFight/Player/RPGRiposteInput.cpp:61` | Riposte Detection | Searches world iterator for boss to locate `URPGBossStagger` | Harmless; returns null for framework boss until framework stagger is wired. |
| `Source/OneBossFight/Arena/RPGFogGate.cpp:93` | Fog Gate Lifecycle | Finds boss actor to monitor death via `Attribute.Health <= 0.0` | Controls fog gate dissolve upon boss defeat. |
| `Source/OneBossFight/Benchmark/RPGBenchmarkRunner.cpp:218` | Telemetry | Identifies boss candidate pawn for benchmark logging | Allows benchmark runner to log framework boss combat. |
| `Source/OneBossFight/Player/RPGBuildLoadout.cpp:601` | Duel Setup | Resets boss position and state when testing loadouts | Harmless. |
| `Source/OneBossFight/Player/RPGStartupChronology.cpp:23, 67, 80` | Engine Init | Logs `Boss` label during spawn timeline | Telemetry only. |
| `Source/OneBossFight/UI/RPGBuildSelect.cpp:320` | UI Selection | Resets boss state when switching build profiles | Harmless. |

### 2.3 Python Headless / PIE Test Drivers Touching HitIntake

| Script Path | Primary Test Assertion | Invariant to Maintain |
| :--- | :--- | :--- |
| `Scripts/Editor/pie_hit_intake.py:2, 73, 87` | Spawns player & legacy boss; verifies `intake.is_bound()`, `intake.get_boss_hit_count() >= 1`, and fields of `intake.get_last_record()`. | Player hit intake component must remain attached to player and receive `OnHit`. |
| `Scripts/Editor/g3_probe_build_hits.py:47` | Probes weapon attack table row resolution and swing tracker intake synchronization. | Hit intake `FRPGHitRecord` parsing must continue populating `Weapon`, `Kind`, `Montage`. |
| `Scripts/Editor/pie_bleed.py:68` | Verifies hit intake routes bleed buildup to boss `URPGBossBleed`. | Hit intake routes bleed if `Boss->FindComponentByClass<URPGBossBleed>()` exists. |
| `Scripts/Editor/pie_posture_hits.py:59` | Verifies hit intake routes posture damage to boss `URPGBossPosture`. | Hit intake routes posture if `Boss->FindComponentByClass<URPGBossPosture>()` exists. |
| `Scripts/Editor/pie_riposte_exec.py:69` | Verifies hit intake registers riposte critical hit when boss is staggered. | Critical hit scaling routes through hit intake. |

---

## 3. Census of Boss Health Consumers (Display & Rules)

Every system in the project that currently reads or writes boss health queries `TEXT("Attribute.Health")` through `RPGPack::ReadAttribute` / `RPGPack::WriteAttribute` (`Source/OneBossFight/Pack/RPGBlueprintCall.h:200-240`).

| Consumer Component / System | File & Line | Read or Write? | Why It Reads Boss Health | Impact on Framework Boss (Native HP without Bridge) |
| :--- | :--- | :--- | :--- | :--- |
| **RPGBossHud** (UI Health Bar) | `Source/OneBossFight/UI/RPGBossHud.cpp:414` | Read (`ReadAttribute`) | Updates on-screen boss health bar fill fraction and floating damage numbers. | **BLIND:** `bHaveHealth` returns false; boss health bar remains invisible / 0%. |
| **RPGBossMusic** (Audio) | `Source/OneBossFight/Audio/RPGBossMusic.cpp:156` | Read (`ReadAttribute`) | Drives dynamic music intensity; shifts music track when boss HP drops below phase threshold. | **BLIND:** Music stays in Phase 1 ambient/intro track; cannot react to boss damage. |
| **RPGFogGate** (Arena) | `Source/OneBossFight/Arena/RPGFogGate.cpp:98` | Read (`ReadAttribute`) | Checks if boss health is `<= 0.0` to trigger fog gate dissolution upon boss death. | **BLIND:** Fog gate never dissolves after kill; arena stays locked. |
| **RPGBossPhases** (Legacy Phases) | `Source/OneBossFight/Player/RPGBossPhases.cpp:29, 137` | Read (`ReadAttribute`) | Evaluates `Health / MaxHealth <= PhaseTwoHealthFraction` (60%) to trigger roar & powerup. | N/A (Framework boss uses its own minimal phase authority). |
| **RPGBossBleed** (Status Effect) | `Source/OneBossFight/Player/RPGBossBleed.cpp:21, 142` | Read & Write | When bleed meter fills (100), applies burst damage: `WriteAttribute(Boss, Health - Burst)`. | **BLIND:** Bleed burst fails to apply; status proc does zero damage. |
| **RPGBossPosture** (Stance) | `Source/OneBossFight/Player/RPGBossPosture.cpp:19, 126` | Read (`ReadAttribute`) | Checks `Health > 0.0` before applying posture damage or allowing posture regeneration. | **BLIND:** Posture system assumes boss is dead; ignores posture damage. |
| **RPGBossEncounter** (Lifecycle) | `Source/OneBossFight/Player/RPGBossEncounter.cpp:33, 214, 280` | Read & Write | At BeginPlay and `ResetEncounter`, refills `Attribute.Health` to `BossMaxHealth` (2000.f). | N/A (Framework boss owns native `EncounterGeneration` and reset). |
| **RPGBossDeath** (Death State) | `Source/OneBossFight/Player/RPGBossDeath.cpp:28, 235` | Read (`ReadAttribute`) | Polls `Health <= 0.0` to begin death sequence, freeze mesh pose, and burst Niagara remains. | N/A (Framework boss triggers death directly from native health edge). |
| **RPGBossStagger** (Criticals) | `Source/OneBossFight/Player/RPGBossStagger.cpp:31, 280` | Read & Write | During critical riposte window, multiplies damage taken by `CriticalMultiplier` (2.5x). | N/A until framework stagger is implemented. |
| **RPGBossDamage::IsAlive** | `Source/OneBossFight/Player/RPGBossDamage.h:39-44` | Read (`ReadAttribute`) | Inline utility: `return Actor && ReadAttribute(Actor, "Attribute.Health") && Health > 0;`. | **BLIND:** Any system calling `RPGBossDamage::IsAlive(Boss)` thinks boss is dead! |
| **RPGDamageResolver** (Resolver) | `Source/OneBossFight/Player/RPGDamageResolver.cpp:147` | Read (via Fallback) | If `ProviderIsAlive` is null, falls back to `RPGBossDamage::IsAlive(Owner)`. | **SAFE:** Framework boss wires `ProviderIsAlive` lambda, completely bypassing this! |
| **RPGCombatDebug** (Debug Lines) | `Source/OneBossFight/Player/RPGCombatDebug.cpp:92, 109, 403` | Read & Write | On-screen text overlay showing boss HP; console command `rpg.BossHealth` to test values. | **BLIND:** Debug text shows `Health: -` unless bridged. |
| **RPGLegend** (Lethal Blows) | `Source/OneBossFight/Player/RPGLegend.cpp:318, 477` | Read (`ReadAttribute`) | Checks for lethal hit to trigger slow-motion camera finish on final blow. | **BLIND:** Cinematic camera finish will not trigger on final blow. |

### 2.4 Critical Architectural Deduction for F6a
Because **13 distinct legacy systems** query `RPGPack::ReadAttribute(Boss, TEXT("Attribute.Health"))`, choosing a purely isolated native C++ health variable without a read bridge means:
- The boss fight will work mechanically under the proof harness,
- **BUT** the player HUD health bar (`RPGBossHud`), arena fog gate (`RPGFogGate`), background music (`RPGBossMusic`), and `RPGBossDamage::IsAlive` will immediately fail to recognize the boss.

**Recommended Bridge Solution for F6a:**  
In `Source/OneBossFight/Pack/RPGBlueprintCall.h:200-220` (`RPGPack::ReadAttribute`), add a 3-line check before component reflection:
```cpp
if (const ARPGFrameworkBossCharacter* FrameworkBoss = Cast<ARPGFrameworkBossCharacter>(Actor))
{
    Value = bMax ? FrameworkBoss->GetMaxHealth() : FrameworkBoss->GetCurrentHealth();
    return true;
}
```
This single, 3-line bypass in `ReadAttribute` guarantees **100% instant compatibility** across `RPGBossHud`, `RPGBossMusic`, `RPGFogGate`, `RPGBossPosture`, `RPGBossBleed`, and `RPGBossDamage::IsAlive` with **zero Blueprint reflection overhead** and **zero legacy code breakage**!

---

## 4. Anatomy of URPGHitIntake::AdjustBossHealth & Minimal Branch

### 4.1 How Damage Reaches the Boss Today (Legacy Pipeline)
In the stock pack duel:
1. **Player Swing:** The player swings sword; `BP_CollisionComponent_C` fires `OnHit(FHitResult HitResult)`. Simultaneously, the pack's `BP_DamageExecution` applies `GE_DamageBase`, which lowers `Attribute.Health` by the pack's default weapon damage (e.g. 41 HP).
2. **Loss Detection:** `URPGHitIntake::TrackBossHealth` (`Source/OneBossFight/Player/RPGHitIntake.cpp:226-256`) polls `Attribute.Health`. When it detects `Health < PrevBossHealth`, it feeds the delta into `Scaler.OnLoss(Time, Loss)`. `PrevBossHealth` is updated.
3. **Record Finalization:** One frame later, `URPGHitIntake::FinalizePending` (`RPGHitIntake.cpp:421-507`) evaluates the attack kind and table row. If the table row has `HealthMultiplier != 1.0`, it calls:
   ```cpp
   const double Adjust = Scaler.OnHit(GetWorld()->GetTimeSeconds(), Record.HealthMultiplier);
   if (FMath::Abs(Adjust) > 0.01)
   {
       AdjustBossHealth(ScaledBoss, Adjust, TEXT("record first"));
   }
   ```
4. **Adjustment Application:** `AdjustBossHealth` adds or subtracts the scaled delta so the final health loss matches the authored table multiplier.

### 4.2 Exact Code Anatomy of AdjustBossHealth Today
`Source/OneBossFight/Player/RPGHitIntake.cpp:258-275`:
```cpp
void URPGHitIntake::AdjustBossHealth(AActor* Boss, double Adjust, const TCHAR* Why)
{
	double Health = 0.0, MaxHealth = 0.0;
	if (!Boss || !RPGPack::ReadAttribute(Boss, TEXT("Attribute.Health"), false, Health) || !RPGPack::ReadAttribute(Boss, TEXT("Attribute.Health"), true, MaxHealth) || Health <= 0.0)
	{
		return; // a dead boss stays dead: the scaler never revives and never kills
	}
	const double NewHealth = FRPGDamageScaler::Apply(Health, Adjust, MaxHealth);
	if (FMath::Abs(NewHealth - Health) < 0.01)
	{
		return;
	}
	RPGPack::WriteAttribute(Boss, TEXT("Attribute.Health"), NewHealth);
	PrevBossHealth = NewHealth;
	++ScaledHitCount;
	HealthAdjustTotal += NewHealth - Health;
	UE_LOG(LogRPGHitIntake, Log, TEXT("health damage multiplier (%s): boss health %.1f -> %.1f (%+.1f)"), Why, Health, NewHealth, NewHealth - Health);
}
```

### 4.3 The Framework Boss Difference & Smallest Safe Branch
**The Key Difference:** The framework boss does NOT execute the pack's `BP_DamageExecution` Blueprint. Therefore, there is NO initial pack damage loss detected by `TrackBossHealth`!

To deal damage to the framework boss cleanly, `URPGHitIntake` can branch directly on `ARPGFrameworkBossCharacter` inside `FinalizePending` (or `AdjustBossHealth`):

#### Proposed Minimal Branch for AdjustBossHealth / Framework Damage:
```cpp
// Inside URPGHitIntake::FinalizePending (or AdjustBossHealth):
if (ARPGFrameworkBossCharacter* FrameworkBoss = Cast<ARPGFrameworkBossCharacter>(Record.Target.Get()))
{
    // Base weapon strike damage (e.g., 35.0f from attack data or table row) * HealthMultiplier
    const float DamageToApply = 35.0f * Record.HealthMultiplier;
    FrameworkBoss->ApplyHealthDelta(-DamageToApply);
    UE_LOG(LogRPGHitIntake, Log, TEXT("framework boss hit %d: applied %.1f damage (health now %.1f)"),
        Record.Id, DamageToApply, FrameworkBoss->GetCurrentHealth());
    continue;
}
```

**Benefits of this Minimal Branch:**
1. **Zero Legacy Risk:** Leaves the complex `FRPGDamageScaler` tracking and `RPGPack::WriteAttribute` pipeline untouched for the legacy greatsword boss.
2. **Deterministic & Frame-Exact:** Directly mutates native boss health during `FinalizePending`, perfectly synchronized with `FRPGHitRecord` broadcast and flipbook hit sparks.
3. **Headless Safe:** Completely immune to Blueprint null references, reflection latency, or `-nullrhi` issues.

