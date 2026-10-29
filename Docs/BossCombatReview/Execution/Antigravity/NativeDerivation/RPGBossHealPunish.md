# Native Derivation Dossier: RPGBossHealPunish

## 1. Component Overview & File Locations
- **Header:** `Source/OneBossFight/Player/RPGBossHealPunish.h`
- **Source:** `Source/OneBossFight/Player/RPGBossHealPunish.cpp`
- **Class:** `URPGBossHealPunish` (`UActorComponent`)
- **Primary Function:** Implements the boss's reaction to player healing (Move A5 / Javelin Throw, Master Design Freeze 16 A5, 21, 32.3). Detects player's `DrinkingPotion_Montage`, checks range, line of sight, cooldown, and boss state. On acceptance, starts move A5 on `URPGAttackTracker` and spawns/launches an `ARPGBossJavelin` towards the player's position at release.

---

## 2. Exact Public Authored Fields
Directly extracted from `Source/OneBossFight/Player/RPGBossHealPunish.h`:

```cpp
// Source/OneBossFight/Player/RPGBossHealPunish.h:33
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish")
bool bEnabled = true;

// Source/OneBossFight/Player/RPGBossHealPunish.h:37
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish", meta = (ClampMin = "0.0"))
float MinRange = 400.f;

// Source/OneBossFight/Player/RPGBossHealPunish.h:40
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish", meta = (ClampMin = "0.0"))
float MaxRange = 1000.f;

// Source/OneBossFight/Player/RPGBossHealPunish.h:44
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish", meta = (ClampMin = "0.0"))
float Cooldown = 4.f;

// Source/OneBossFight/Player/RPGBossHealPunish.h:48
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish", meta = (ClampMin = "0.0"))
float Damage = 12.f;

// Source/OneBossFight/Player/RPGBossHealPunish.h:54
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish", meta = (ClampMin = "0.05"))
float FlightTime = 1.2f;

// Source/OneBossFight/Player/RPGBossHealPunish.h:57
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish", meta = (ClampMin = "1.0"))
float MinSpeed = 450.f;

// Source/OneBossFight/Player/RPGBossHealPunish.h:60
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish", meta = (ClampMin = "1.0"))
float MaxSpeed = 2500.f;

// Source/OneBossFight/Player/RPGBossHealPunish.h:65
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish", meta = (ClampMin = "1.0"))
float JavelinRadius = 25.f;

// Source/OneBossFight/Player/RPGBossHealPunish.h:68
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish", meta = (ClampMin = "1.0"))
float JavelinMaxRange = 3000.f;

// Source/OneBossFight/Player/RPGBossHealPunish.h:72
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish")
TArray<FName> SpawnSockets = {TEXT("JavelinSpawn"), TEXT("hand_l")};

// Source/OneBossFight/Player/RPGBossHealPunish.h:76
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish")
float AimHeight = 100.f;

// Source/OneBossFight/Player/RPGBossHealPunish.h:80
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish")
bool bRespondToHeal = true;

// Source/OneBossFight/Player/RPGBossHealPunish.h:141
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish")
bool bCancelJavelinsOnInterrupt = true;
```

Total authored fields: **14**.

---

## 3. Code Readings & Extreme Handling (Read From Code)

### `bEnabled` (`bool`, default `true`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossHealPunish.cpp:202`: `if (!bEnabled || !Boss) { return; }` in `TickComponent()`.
- **Extremes (Read From Code):**
  - `false`: Component returns immediately in `TickComponent()`. Does not evaluate player drink montage, does not trigger `OnHealStarted()`, does not update cooldowns or release pending javelins.
  - `true`: Normal execution.

### `MinRange` (`float`, default `400.f`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossHealPunish.cpp:120`: `if (Distance < MinRange || Distance > MaxRange) { ++DiscardedRange; ... return; }` in `OnHealStarted()`.
- **Extremes (Read From Code):**
  - Negative (`< 0.0f`): `Distance < MinRange` never fires for non-negative horizontal distances. Range check relies solely on `Distance > MaxRange`.
  - `MinRange > MaxRange`: The conditional `Distance < MinRange || Distance > MaxRange` is a tautology (always true for any real number). Every single heal request is rejected with `DiscardedRange`! Boss will never throw a javelin.
  - `0.0f`: Boss can punish player at point-blank range (0 distance).

### `MaxRange` (`float`, default `1000.f`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossHealPunish.cpp:120`: `if (Distance < MinRange || Distance > MaxRange)` in `OnHealStarted()`.
- **Extremes (Read From Code):**
  - `<= 0.0f`: Rejects all heal requests (unless `Distance == 0.0f` and `MaxRange == 0.0f`).
  - `< MinRange`: Completely closes distance window; 100% of heal attempts discarded.
  - Huge (`>= 50000.f`): Allows boss to trigger punish from anywhere in arena as long as line of sight is clear.

### `Cooldown` (`float`, default `4.f`)
- **Read Locations:**
  - `Source/OneBossFight/Player/RPGBossHealPunish.cpp:189`: `CooldownEnd = World->GetTimeSeconds() + Cooldown;` in `Release()`.
  - `Source/OneBossFight/Player/RPGBossHealPunish.cpp:33`: `return CooldownEnd < 0.0 ? 0.f : FMath::Max(0.f, static_cast<float>(CooldownEnd - World->GetTimeSeconds()));` in `GetCooldownRemaining()`.
- **Extremes (Read From Code):**
  - `0.0f`: `CooldownEnd` equals current time. On subsequent frame, `World->GetTimeSeconds() < CooldownEnd` is false (`RPGBossHealPunish.cpp:128`), meaning cooldown is immediately ready.
  - Negative (`< 0.0f`): `CooldownEnd` is set in the past; cooldown check never triggers; boss can react immediately to consecutive heals.
  - Huge (`>= 3600.f`): Boss can only execute heal punish once per encounter.

### `Damage` (`float`, default `12.f`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossHealPunish.cpp:182`: `Javelin->Launch(..., Damage, ...)` in `Release()`.
- **Extremes (Read From Code):**
  - `0.0f`: Javelin deals 0 HP damage on collision.
  - Negative (`< 0.0f`): Passed to `ARPGBossJavelin::Launch()`, which dispatches negative damage to player resolver.
  - Huge (`>= 120.f`): Instant lethal kill in 120 HP economy.

### `FlightTime` (`float`, default `1.2f`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossHealPunish.cpp:176`: `const float Speed = FMath::Clamp(Dist / FlightTime, MinSpeed, MaxSpeed);` in `Release()`.
- **Extremes (Read From Code):**
  - `0.0f`: Float division by zero (`Dist / 0.0f` -> `+Inf`). `FMath::Clamp(+Inf, MinSpeed, MaxSpeed)` evaluates to `MaxSpeed` in standard IEEE float, but risks undefined behavior or float exceptions on strict platforms.
  - Negative (`< 0.0f`): `Dist / FlightTime` is negative; clamped to `MinSpeed`.
  - Huge (`>= 100.f`): `Dist / FlightTime` approaches 0; clamped to `MinSpeed`.

### `MinSpeed` (`float`, default `450.f`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossHealPunish.cpp:176`: `const float Speed = FMath::Clamp(Dist / FlightTime, MinSpeed, MaxSpeed);` in `Release()`.
- **Extremes (Read From Code):**
  - `MinSpeed > MaxSpeed`: `FMath::Clamp(X, Min, Max)` where `Min > Max` has undefined behavior in Unreal Engine (asserts or returns invalid bound).
  - `<= 0.0f`: Allows zero or negative javelin flight speed if `Dist / FlightTime` is low.

### `MaxSpeed` (`float`, default `2500.f`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossHealPunish.cpp:176`: `const float Speed = FMath::Clamp(Dist / FlightTime, MinSpeed, MaxSpeed);` in `Release()`.
- **Extremes (Read From Code):**
  - `< MinSpeed`: Inverted clamp bounds.
  - Huge (`>= 100000.f`): Instantaneous hitscan-like javelin travel.

### `JavelinRadius` (`float`, default `25.f`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossHealPunish.cpp:181`: `Javelin->Launch(..., JavelinRadius, JavelinMaxRange, ...)` in `Release()`.
- **Extremes (Read From Code):**
  - `<= 0.0f`: Projectile collision sphere has non-positive radius; cannot register overlap hits against character capsule.
  - Huge (`>= 1000.f`): Massive collision sphere hits player or arena geometry almost immediately upon spawn.

### `JavelinMaxRange` (`float`, default `3000.f`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossHealPunish.cpp:181`: `Javelin->Launch(..., JavelinRadius, JavelinMaxRange, ...)` in `Release()`.
- **Extremes (Read From Code):**
  - `<= 0.0f`: Javelin destroys itself on first tick after launch.
  - Huge (`>= 50000.f`): Javelin flies until hitting geometry or boundary.

### `SpawnSockets` (`TArray<FName>`, default `{TEXT("JavelinSpawn"), TEXT("hand_l")}`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossHealPunish.cpp:63-68`:
    ```cpp
    for (const FName& Socket : SpawnSockets)
    {
        if (Mesh->DoesSocketExist(Socket))
        {
            return Mesh->GetSocketLocation(Socket);
        }
    }
    ```
- **Extremes (Read From Code):**
  - Empty array: Loop finishes without match; executes fallback at line 71: `Boss->GetActorLocation() + FVector(0.f, 0.f, 150.f) + Boss->GetActorForwardVector() * 50.f`.
  - Non-existent socket names: Same fallback executed without crashing.

### `AimHeight` (`float`, default `100.f`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossHealPunish.cpp:173`: `Target.Z = FeetZ + AimHeight;` in `Release()`.
- **Extremes (Read From Code):**
  - `0.0f`: Aims directly at floor level / player feet.
  - Negative (`< 0.0f`): Aims into the floor; projectile collides with ground before reaching player.
  - Huge (`>= 1000.f`): Aims high overhead into the sky.

### `bRespondToHeal` (`bool`, default `true`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossHealPunish.cpp:106`: `if (!bRespondToHeal) { return; }` in `OnHealStarted()`.
- **Extremes (Read From Code):**
  - `false`: Silently ignores all player heal events; boss will not trigger heal punish.
  - `true`: Normal response enabled.

### `bCancelJavelinsOnInterrupt` (`bool`, default `true`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossHealPunish.cpp:88`: `if (bCancelJavelinsOnInterrupt) { for (auto& FlyingJavelin : Flying) { if (ARPGBossJavelin* J = FlyingJavelin.Get()) { J->DestroyActor(); } } }` in `CancelAll()`.
- **Extremes (Read From Code):**
  - `true`: When boss stance breaks or transitions phase, all currently flying javelins are destroyed immediately.
  - `false`: Flying javelins continue along their ballistic trajectory.

---

## 4. External Dependencies
Directly cited from `Source/OneBossFight/Player/RPGBossHealPunish.cpp`:

1. **`URPGAttackTracker` (Component Lookup & Move Trigger):**
   - Lookup: `Source/OneBossFight/Player/RPGBossHealPunish.cpp:100, 138, 249`: `const URPGAttackTracker* Tracker = Boss->FindComponentByClass<URPGAttackTracker>();`
   - Hardcoded Move Identifier: `Source/OneBossFight/Player/RPGBossHealPunish.cpp:22`: `const FName ThrowMove(TEXT("A5"));`
   - Calls: `Tracker->StartMove(ThrowMove, false)` (`:138`), `Tracker->GetCurrentMove() == ThrowMove` (`:254`), `Tracker->IsActiveWindow()`, `Tracker->GetAttackInstance()`.
   - Structural Verifiability: The move name `TEXT("A5")` is hardcoded in `.cpp` (not an authored property).

2. **Hardcoded Player Drink Montage Soft Path:**
   - Lookup: `Source/OneBossFight/Player/RPGBossHealPunish.cpp:236`:
     ```cpp
     DrinkMontage = LoadObject<UAnimMontage>(nullptr, TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/DrinkingPotion_Montage.DrinkingPotion_Montage"));
     ```
   - Evaluated in `TickComponent()` via `PlayerAnim->Montage_IsPlaying(DrinkMontage.Get())`.
   - Structural Verifiability: **Hardcoded string literal inside .cpp**. Provable structurally offline by checking package `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/DrinkingPotion_Montage`.

3. **`ARPGBossJavelin` (Spawned Projectile Class):**
   - Spawn: `Source/OneBossFight/Player/RPGBossHealPunish.cpp:179`: `ARPGBossJavelin* Javelin = World->SpawnActor<ARPGBossJavelin>(SpawnLocation, Rotation);`
   - Header include: `RPGBossHealPunish.h:7` (`#include "Player/RPGBossJavelin.h"`).
   - Structural Verifiability: Direct C++ class dependency.

4. **`URPGBossEncounter` (Component Lookup):**
   - Lookup: `Source/OneBossFight/Player/RPGBossHealPunish.cpp:175, 217`: `const URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();`
   - Reads: `Encounter->GetGeneration()`. Clears pending attacks and destroys javelins on generation mismatch.

5. **Player Pawn & Anim Instance:**
   - Lookup: `Source/OneBossFight/Player/RPGBossHealPunish.cpp:111, 232`: `Cast<ACharacter>(UGameplayStatics::GetPlayerPawn(this, 0))`
   - Reads: `Player->GetMesh()->GetAnimInstance()`.

6. **World Line Trace (Line of Sight):**
   - Trace: `Source/OneBossFight/Player/RPGBossHealPunish.cpp:45`: `World->LineTraceSingleByChannel(Hit, From, To, ECC_WorldStatic, QueryParams)`

7. **Authored Soft Paths:**
   - **NONE**. There are no `TSoftObjectPtr` properties declared in `URPGBossHealPunish.h`.

---

## 5. Proposed Typed Domain

| Field | Type | Domain / Constraints | Label | Derivation Reason |
|---|---|---|---|---|
| `bEnabled` | `bool` | `{true, false}` | **NATIVE-DERIVED** | Direct boolean check in `TickComponent()` (`RPGBossHealPunish.cpp:202`). |
| `MinRange` | `float` | `0.0f <= MinRange < MaxRange` (finite) | **NATIVE-DERIVED** | Header `ClampMin="0.0"`. Must be `< MaxRange` otherwise window is empty (`RPGBossHealPunish.cpp:120`). |
| `MaxRange` | `float` | `MinRange < MaxRange <= 10000.0f` (finite) | **NATIVE-DERIVED** | Must exceed `MinRange`. Upper bound encompasses combat arena dimensions. |
| `Cooldown` | `float` | `0.0f <= Cooldown <= 60.0f` (finite) | **NATIVE-DERIVED** | Header `ClampMin="0.0"`. Cooldown timer addition (`RPGBossHealPunish.cpp:189`). |
| `Damage` | `float` | `0.0f <= Damage <= 500.0f` (finite) | **NATIVE-DERIVED / AUTHORED CHOICE** | Header `ClampMin="0.0"`. Upper bound `500.0f` matches project damage envelope. |
| `FlightTime` | `float` | `0.05f <= FlightTime <= 10.0f` (finite) | **NATIVE-DERIVED** | Header enforces `ClampMin="0.05"`. Prevents division by zero in speed clamp (`RPGBossHealPunish.cpp:176`). |
| `MinSpeed` | `float` | `1.0f <= MinSpeed <= MaxSpeed` (finite) | **NATIVE-DERIVED** | Header enforces `ClampMin="1.0"`. Must be `<= MaxSpeed` for `FMath::Clamp()` validity (`RPGBossHealPunish.cpp:176`). |
| `MaxSpeed` | `float` | `MinSpeed <= MaxSpeed <= 20000.0f` (finite) | **NATIVE-DERIVED** | Header enforces `ClampMin="1.0"`. Must be `>= MinSpeed`. Upper bound limits ballistic velocity. |
| `JavelinRadius` | `float` | `1.0f <= JavelinRadius <= 500.0f` (finite) | **NATIVE-DERIVED** | Header enforces `ClampMin="1.0"`. Positive radius required for collision detection. |
| `JavelinMaxRange` | `float` | `100.0f <= JavelinMaxRange <= 20000.0f` (finite) | **NATIVE-DERIVED** | Header enforces `ClampMin="1.0"`. Range after which javelin despawns. |
| `SpawnSockets` | `TArray<FName>` | Array of non-empty `FName`, matches `^[A-Za-z0-9_]+$` | **NATIVE-DERIVED** | Iterated to find existing mesh sockets (`RPGBossHealPunish.cpp:63-68`). |
| `AimHeight` | `float` | `-500.0f <= AimHeight <= 500.0f` (finite) | **AUTHORED CHOICE** | Height offset from feet (`RPGBossHealPunish.cpp:173`). Default is `100.0f` (chest height). |
| `bRespondToHeal` | `bool` | `{true, false}` | **NATIVE-DERIVED** | Direct boolean check in `OnHealStarted()` (`RPGBossHealPunish.cpp:106`). |
| `bCancelJavelinsOnInterrupt` | `bool` | `{true, false}` | **NATIVE-DERIVED** | Guard for destroying in-flight projectiles in `CancelAll()` (`RPGBossHealPunish.cpp:88`). |

*Unresolved Items:*
- Move name `ThrowMove` is hardcoded as `TEXT("A5")` at `Source/OneBossFight/Player/RPGBossHealPunish.cpp:22`. It is not an authored property.
- Player potion montage path is hardcoded at `Source/OneBossFight/Player/RPGBossHealPunish.cpp:236`. It is not an authored property.

---

## 6. Lifecycle Facts & Configure Guard Rules
- **Component Tick:** `PrimaryComponentTick.bCanEverTick = true; PrimaryComponentTick.TickInterval = 0.f;` (`RPGBossHealPunish.cpp:18-20`). Ticks every frame.
- **BeginPlay / EndPlay:** Does not override `BeginPlay()` or `EndPlay()`.
- **Preload:** Lazy-loads `DrinkingPotion_Montage` inside `TickComponent()` on first check (`RPGBossHealPunish.cpp:236`).
- **Runtime State Fields (MUST NOT be overwritten or touched during runtime configure):**
  - `bool bPending` (`RPGBossHealPunish.h:156`)
  - `bool bStarted` (`RPGBossHealPunish.h:157`)
  - `bool bWasHealing` (`RPGBossHealPunish.h:158`)
  - `bool bDead` (`RPGBossHealPunish.h:159`)
  - `float DeathCheck` (`RPGBossHealPunish.h:160`)
  - `double PendingSince` (`RPGBossHealPunish.h:161`)
  - `double CooldownEnd` (`RPGBossHealPunish.h:162`)
  - `int32 LastInstance` (`RPGBossHealPunish.h:163`)
  - `int32 SeenGeneration` (`RPGBossHealPunish.h:164`)
  - `int32 HealEvents`, `Accepted`, `Released`, `DiscardedBusy`, `DiscardedRange`, `DiscardedSight`, `DiscardedCooldown`, `DiscardedPending`, `Cancelled`, `JavelinHits`, `JavelinDodged`, `JavelinWorld` (`RPGBossHealPunish.h:165-176`)
  - `TWeakObjectPtr<const UAnimMontage> DrinkMontage` (`RPGBossHealPunish.h:177`)
  - `TArray<TWeakObjectPtr<ARPGBossJavelin>> Flying` (`RPGBossHealPunish.h:178`)
- **Configure Guard Constraint:** Re-configuring while `bPending == true` or while javelins are in `Flying` array could create inconsistent tracking instances. Best configured while neutral / dormant.
