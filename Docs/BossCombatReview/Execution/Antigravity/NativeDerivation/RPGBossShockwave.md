# Native Derivation Dossier: RPGBossShockwave

## 1. Component Overview & File Locations
- **Header:** `Source/OneBossFight/Player/RPGBossShockwave.h`
- **Source:** `Source/OneBossFight/Player/RPGBossShockwave.cpp`
- **Class:** `URPGBossShockwave` (`UActorComponent`)
- **Primary Function:** Implements the boss's expanding circular ground shockwave (Move A6 / Jump wave, Master Design Freeze 16 A6, 21, 32.3). Tracks the attack window, computes outward expanding collision band, checks player jump clearance, and dispatches damage through `URPGDamageResolver`.

---

## 2. Exact Public Authored Fields
Directly extracted from `Source/OneBossFight/Player/RPGBossShockwave.h`:

```cpp
// Source/OneBossFight/Player/RPGBossShockwave.h:30
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shockwave")
bool bEnabled = true;

// Source/OneBossFight/Player/RPGBossShockwave.h:34
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shockwave")
FName MoveId = TEXT("A6");

// Source/OneBossFight/Player/RPGBossShockwave.h:39
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shockwave", meta = (ClampMin = "0.0"))
float Damage = 48.f;

// Source/OneBossFight/Player/RPGBossShockwave.h:42
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shockwave", meta = (ClampMin = "0.0"))
float StartRadius = 200.f;

// Source/OneBossFight/Player/RPGBossShockwave.h:45
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shockwave", meta = (ClampMin = "1.0"))
float MaxRadius = 1100.f;

// Source/OneBossFight/Player/RPGBossShockwave.h:49
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shockwave", meta = (ClampMin = "1.0"))
float Speed = 1000.f;

// Source/OneBossFight/Player/RPGBossShockwave.h:53
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shockwave", meta = (ClampMin = "1.0"))
float Thickness = 180.f;

// Source/OneBossFight/Player/RPGBossShockwave.h:57
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shockwave", meta = (ClampMin = "0.0"))
float JumpClearance = 50.f;
```

Total authored fields: **8**.

---

## 3. Code Readings & Extreme Handling (Read From Code)

### `bEnabled` (`bool`, default `true`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossShockwave.cpp:133`: `if (!bEnabled || !Boss) { return; }` in `TickComponent()`.
- **Extremes (Read From Code):**
  - `false`: Component tick returns immediately on line 135. No launch trigger check, no radius advance, no collision resolution, and no reset. The shockwave is entirely dormant.
  - `true`: Component executes full tick logic.

### `MoveId` (`FName`, default `TEXT("A6")`)
- **Read Locations:**
  - `Source/OneBossFight/Player/RPGBossShockwave.cpp:98`: `Payload.MoveId = MoveId;` in `Resolve()`.
  - `Source/OneBossFight/Player/RPGBossShockwave.cpp:153`: `const bool bAttacking = Tracker->GetCurrentMove() == MoveId;` in `TickComponent()`.
- **Extremes (Read From Code):**
  - `NAME_None` or unassigned: `GetCurrentMove() == MoveId` will never evaluate to true against an active move in `URPGAttackTracker`. The shockwave will never be launched from tick.
  - Mismatched name (e.g. `TEXT("InvalidMove")`): Same as `NAME_None`; `bAttacking` remains false.

### `Damage` (`float`, default `48.f`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossShockwave.cpp:101`: `Payload.HPDamage = Damage;` in `Resolve()`.
- **Extremes (Read From Code):**
  - `0.0f`: Payload passes 0.0 HP damage to `URPGDamageResolver::ResolveDamage()`. Player receives zero damage upon hit.
  - Negative (`< 0.0f`): Negative damage float is written directly into `FRPGDamagePayload::HPDamage`. If resolver does not clamp, could result in negative damage application or health restoration.
  - `NaN` / `Inf`: Propagated into damage resolver math; can cause undefined attribute calculations, NaN health, or assertion in engine numerical helpers.
  - Huge (`> 1000.f`): In the project's standard 120 HP player economy, deals lethal one-shot damage immediately on hit.

### `StartRadius` (`float`, default `200.f`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossShockwave.cpp:40`: `Radius = StartRadius;` in `Launch()`.
- **Extremes (Read From Code):**
  - `0.0f`: Wave starts at point origin at the boss's location (`Origin = Boss->GetActorLocation()`).
  - Negative (`< 0.0f`): `Radius` begins negative. In `Resolve()`, `Inner = Radius - Thickness * 0.5f` and `Outer = Radius + Thickness * 0.5f`. If `Outer <= 0.0f`, `PlayerDistance >= Inner && PlayerDistance <= Outer` cannot match any positive horizontal distance (`PlayerDistance >= 0`). Wave cannot hit until `Radius` grows sufficiently positive.
  - `>= MaxRadius`: In `TickComponent()`, line 167 executes: `if (Radius > MaxRadius) { Stop(TEXT("max radius")); }`. If `StartRadius >= MaxRadius`, the shockwave is stopped immediately on the first tick without traversing the arena.
  - `NaN` / `Inf`: Sets `Radius` to non-finite; `Radius += Speed * DeltaTime` remains non-finite; comparisons with `MaxRadius` fail or stop immediately.

### `MaxRadius` (`float`, default `1100.f`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossShockwave.cpp:167`: `if (Radius > MaxRadius) { Stop(TEXT("max radius")); }` in `TickComponent()`.
- **Extremes (Read From Code):**
  - `<= StartRadius`: When launched, `Radius` starts at `StartRadius`. On the very first tick where `Radius > MaxRadius` (or immediately if `StartRadius > MaxRadius`), `Stop(TEXT("max radius"))` halts the wave.
  - `<= 0.0f`: Halts wave immediately.
  - Huge (`>= 50000.f`): The shockwave expands across the entire level without terminating via radius check; runs until boss death or encounter reset.
  - `NaN` / `Inf`: Comparison `Radius > MaxRadius` behaves unpredictably or never fires, preventing natural wave termination.

### `Speed` (`float`, default `1000.f`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossShockwave.cpp:162`: `Radius += Speed * DeltaTime;` in `TickComponent()`.
- **Extremes (Read From Code):**
  - `0.0f`: `Radius` remains constant at `StartRadius`. The wave ring is static; never reaches `MaxRadius` and never stops unless encounter resets.
  - Negative (`< 0.0f`): `Radius` shrinks towards negative infinity each tick. `Radius > MaxRadius` never fires; wave runs indefinitely.
  - Huge (`> 20000.f`): Large step per frame (`Speed * DeltaTime`). If `Speed * DeltaTime > Thickness`, the active band `[Radius - Thickness*0.5, Radius + Thickness*0.5]` can completely skip over the player's horizontal distance in a single frame, resulting in a missed hit (tunneling).
  - `NaN` / `Inf`: `Radius` becomes non-finite immediately.

### `Thickness` (`float`, default `180.f`)
- **Read Locations:**
  - `Source/OneBossFight/Player/RPGBossShockwave.cpp:73`: `const float Inner = Radius - Thickness * 0.5f;` in `Resolve()`.
  - `Source/OneBossFight/Player/RPGBossShockwave.cpp:74`: `const float Outer = Radius + Thickness * 0.5f;` in `Resolve()`.
- **Extremes (Read From Code):**
  - `0.0f`: `Inner == Outer == Radius`. Collision band has zero width; discrete frame sampling makes `PlayerDistance == Radius` practically impossible. Wave never hits.
  - Negative (`< 0.0f`): `Inner > Outer`. Condition `PlayerDistance >= Inner && PlayerDistance <= Outer` is mathematically impossible for any positive `PlayerDistance`. Wave can never hit player.
  - Huge (`>= 5000.f`): Band spans entire arena; player is inside the hit band from launch until stop.
  - `NaN` / `Inf`: `Inner` and `Outer` become non-finite; range check fails.

### `JumpClearance` (`float`, default `50.f`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossShockwave.cpp:91`: `if (FeetZ - GroundZ >= JumpClearance)` in `Resolve()`.
- **Extremes (Read From Code):**
  - `<= 0.0f`: For any player standing at or above floor level (`FeetZ >= GroundZ`), `FeetZ - GroundZ >= JumpClearance` evaluates to true. The player is permanently marked `bClearedBand = true` without jumping! Shockwave cannot hit even a grounded player.
  - Huge (`>= 2000.f`): Standard character jump height cannot achieve `FeetZ - GroundZ >= JumpClearance`. The wave becomes strictly un-jumpable.
  - `NaN` / `Inf`: Comparison fails or behaves unpredictably.

---

## 4. External Dependencies
Directly cited from `Source/OneBossFight/Player/RPGBossShockwave.cpp`:

1. **`URPGAttackTracker` (Component Lookup):**
   - Lookup: `Source/OneBossFight/Player/RPGBossShockwave.cpp:152`: `const URPGAttackTracker* Tracker = Boss->FindComponentByClass<URPGAttackTracker>();`
   - Calls: `Tracker->GetCurrentMove()`, `Tracker->IsActiveWindow()`, `Tracker->GetAttackInstance()`.
   - Structural Verifiability: **Partially provable offline**. Move identifier `MoveId` can be checked syntactically (non-empty `FName`), but whether `MoveId` matches an authored row in `URPGAttackTracker` requires cross-referencing move tables.

2. **`URPGBossEncounter` (Component Lookup):**
   - Lookup: `Source/OneBossFight/Player/RPGBossShockwave.cpp:45, 147`: `const URPGBossEncounter* Encounter = GetOwner()->FindComponentByClass<URPGBossEncounter>();`
   - Calls: `Encounter->GetGeneration()`. Resets shockwave state when generation increments.
   - Structural Verifiability: Standard component lookup on Owner; provable by actor blueprint hierarchy.

3. **`URPGDamageResolver` (Component Lookup / Addition):**
   - Lookup: `Source/OneBossFight/Player/RPGBossShockwave.cpp:102`: `URPGDamageResolver* Resolver = URPGDamageResolver::FindOrAdd(GetOwner());`
   - Calls: `Resolver->ResolveDamage(Payload)`.
   - Structural Verifiability: Fully self-contained; adds resolver dynamically if absent.

4. **Player Pawn (`ACharacter`):**
   - Lookup: `Source/OneBossFight/Player/RPGBossShockwave.cpp:48, 66`: `UGameplayStatics::GetPlayerPawn(this, 0)`
   - Calls: Reads player capsule component for feet elevation (`GetScaledCapsuleHalfHeight()`) and location.
   - Structural Verifiability: Standard world player 0 lookup.

5. **Gameplay Attribute (`Attribute.Health`):**
   - Lookup: `Source/OneBossFight/Player/RPGBossShockwave.cpp:50, 105, 142`: `ReadAttribute(..., TEXT("Attribute.Health"), false, Health)`
   - Reads boss and player health.
   - Structural Verifiability: String tag convention matching RPG gameplay framework.

6. **Soft Paths / Asset Loads:**
   - **NONE**. `URPGBossShockwave` declares zero `TSoftObjectPtr` properties and performs zero `LoadSynchronous` calls.

---

## 5. Proposed Typed Domain

| Field | Type | Domain / Constraints | Label | Derivation Reason |
|---|---|---|---|---|
| `bEnabled` | `bool` | `{true, false}` | **NATIVE-DERIVED** | Direct boolean guard on tick (`RPGBossShockwave.cpp:133`). |
| `MoveId` | `FName` | Non-empty `FName`, matches `^[A-Za-z0-9_]+$` | **NATIVE-DERIVED** | Checked against `URPGAttackTracker::GetCurrentMove()` (`RPGBossShockwave.cpp:153`). |
| `Damage` | `float` | `0.0f <= Damage <= 500.0f` (finite) | **NATIVE-DERIVED / AUTHORED CHOICE** | Lower bound `>= 0.0f` derived from header `ClampMin="0.0"` and resolver payload; upper bound `500.0f` is authored choice for 120 HP player economy (default is 48.0f). |
| `StartRadius` | `float` | `0.0f <= StartRadius < MaxRadius` (finite) | **NATIVE-DERIVED** | Must be `< MaxRadius` otherwise `Stop()` is called immediately on tick 1 (`RPGBossShockwave.cpp:167`). Header enforces `ClampMin="0.0"`. |
| `MaxRadius` | `float` | `StartRadius < MaxRadius <= 10000.0f` (finite) | **NATIVE-DERIVED** | Termination condition in tick (`RPGBossShockwave.cpp:167`). Header enforces `ClampMin="1.0"`. Upper bound `10000.0f` covers arena geometry. |
| `Speed` | `float` | `1.0f <= Speed <= 10000.0f` (finite) | **NATIVE-DERIVED** | Must be `> 0.0f` to advance radius (`RPGBossShockwave.cpp:162`). Header enforces `ClampMin="1.0"`. Upper bound prevents frame-tunneling across standard thickness. |
| `Thickness` | `float` | `1.0f <= Thickness <= 2000.0f` (finite) | **NATIVE-DERIVED** | Must be `> 0.0f` for `Inner < Outer` band check (`RPGBossShockwave.cpp:73-75`). Header enforces `ClampMin="1.0"`. |
| `JumpClearance` | `float` | `1.0f <= JumpClearance <= 500.0f` (finite) | **NATIVE-DERIVED** | Must be `> 0.0f` so standing player does not clear wave (`RPGBossShockwave.cpp:91`). Header enforces `ClampMin="0.0"`. Upper bound reflects player jump capability. |

*Unresolved Items:* **None**. All properties and relational invariants are strictly derived from native source code.

---

## 6. Lifecycle Facts & Configure Guard Rules
- **Component Tick:** `PrimaryComponentTick.bCanEverTick = true; PrimaryComponentTick.TickInterval = 0.f;` (`RPGBossShockwave.cpp:21-23`). Ticks every frame.
- **BeginPlay / EndPlay:** Does not override `BeginPlay()` or `EndPlay()`.
- **Preload / Asset Loads:** None.
- **Runtime State Fields (MUST NOT be overwritten or touched during runtime configure):**
  - `bool bActive` (`RPGBossShockwave.h:80`)
  - `bool bClearedBand` (`RPGBossShockwave.h:81`)
  - `bool bResolved` (`RPGBossShockwave.h:82`)
  - `float Radius` (`RPGBossShockwave.h:83`)
  - `FVector Origin` (`RPGBossShockwave.h:84`)
  - `float GroundZ` (`RPGBossShockwave.h:85`)
  - `int32 LaunchCount`, `HitCount`, `JumpClearCount`, `ResolveCount` (`RPGBossShockwave.h:86-89`)
  - `int32 LastAttackInstance` (`RPGBossShockwave.h:90`)
  - `int32 SeenGeneration` (`RPGBossShockwave.h:91`)
- **Configure Guard Constraint:** If re-configured while `bActive == true`, changing `MaxRadius` or `StartRadius` mid-flight could cause premature `Stop()` or sudden jump in band detection. Safe configuration occurs when `bActive == false`.
