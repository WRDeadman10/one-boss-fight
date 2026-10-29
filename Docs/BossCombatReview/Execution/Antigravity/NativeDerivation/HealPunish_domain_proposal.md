# HealPunish Domain Proposal Sheet

> **DOCUMENT STATUS: SUPERSEDED BY CLAUDE LEAD CONTRACT [C-265]**  
> **Original Submission:** Antigravity under order AG-CONTENT07 / [C-263] in [A-186].  
> **Lead Review:** Returned with corrections in [C-265]; definitive DD22 Lead Contract established below.  
> **Audit Hygiene:** The original A-186 proposal text is preserved in Section 5 below for historical audit.

---

## 1. Corrections Applied Per Lead Review [C-265] (Items 1 - 7)

1. **Line Citations Corrected (read directly from RPGBossHealPunish.cpp/.h):**
   - Socket existence iteration: `RPGBossHealPunish.cpp:42` (previously cited `:63-68`).
   - `bCancelJavelinsOnInterrupt` evaluation in `CancelAll()`: `RPGBossHealPunish.cpp:81` (previously cited `:88`).
   - `bRespondToHeal` guard in `OnHealStarted()`: `RPGBossHealPunish.cpp:101` (previously cited `:106`).
   - `CooldownEnd` timestamp assignment in `Release()`: `RPGBossHealPunish.cpp:170` (previously cited `:189`).
   - `Javelin->Launch()` call with `Damage`: `RPGBossHealPunish.cpp:181` (previously cited `:182`).

2. **Re-labelling Header ClampMin as Editor Metadata (Authored Choice):**
   - Header `meta = (ClampMin = ...)` values are Unreal Editor property metadata only, not runtime guards or native engine checks.
   - Rows previously labelled NATIVE-DERIVED solely on the basis of `ClampMin` are correctly re-labelled **AUTHORED CHOICE**.

3. **Accurate Arithmetic & Clamp Semantics:**
   - Unreal Engine's `FMath::Clamp(X, Min, Max)` template returns `X < Min ? Min : (X < Max ? X : Max)` and does not trigger `check()` or undefined behavior in debug/release when `Min > Max`.
   - The requirement `MinSpeed <= MaxSpeed` is an **authored consistency contract** so the valid speed window is coherent.
   - For `FlightTime == 0.0f`: when `Dist > 0.0f`, `Dist / FlightTime` evaluates to `+Inf`, which `FMath::Clamp()` clamps to `MaxSpeed`. A `NaN` result occurs only if `Dist == 0.0f` (`0.0f / 0.0f`). The lower floor `FlightTime >= 0.05f` is an authored choice matching the editor floor.

4. **Damage Ceiling Correction:**
   - The previously proposed ceiling of `500.0f` was an authored invention.
   - Native code passes `Damage` directly to `Javelin->Launch()`, which subtracts it from player HP without an upper clamp.
   - In accordance with DD21 Shockwave `Damage` policy, `Damage` has **no ceiling** (must be finite and `>= 0.0f`).

5. **Socket Name Constraints:**
   - The previously proposed regex `^[A-Za-z0-9_]+$` was an authored invention and stricter than the engine allows (bone/socket names are not limited to this pattern).
   - The contract requires: array length `>= 1`, every entry not `NAME_None`/empty, and no whitespace or control characters (`ord(c) < 32`).

6. **Float Field Count:**
   - Corrected from "9 floats" to exactly **10 float fields**: `MinRange`, `MaxRange`, `Cooldown`, `Damage`, `FlightTime`, `MinSpeed`, `MaxSpeed`, `JavelinRadius`, `JavelinMaxRange`, `AimHeight`.

7. **MinRange vs MaxRange Window Semantics:**
   - `MinRange == MaxRange` represents a degenerate 1-distance window (a sphere shell of exact radius), not an empty set.
   - The requirement `MaxRange > MinRange` is an **authored choice** ensuring a non-trivial engagement window.

---

## 2. Definitive DD22 Lead Contract (from [C-265])

- **Component:** `URPGBossHealPunish` (`Source/OneBossFight/Player/RPGBossHealPunish.h`, `.cpp`)
- **Struct Name:** `FRPGHealPunishConfig` (14th native struct in AuthoringToolkit)
- **Status:** Authored record contract, NOT native guards; qualified as **pending DD22 live run**.
- **Constant:** `MaxAuthoredMagnitude = 1.0e6f` (DD21 constant, same reasoning: radius-like and speed values <= 1e6 stay finite for any frame DeltaTime below 1e30 s).
- **Native Fields (14 fields in exact header order):**
  1. `bEnabled` (`bool`, default `true`)
  2. `MinRange` (`float`, default `400.f`)
  3. `MaxRange` (`float`, default `1000.f`)
  4. `Cooldown` (`float`, default `4.f`)
  5. `Damage` (`float`, default `12.f`)
  6. `FlightTime` (`float`, default `1.2f`)
  7. `MinSpeed` (`float`, default `450.f`)
  8. `MaxSpeed` (`float`, default `2500.f`)
  9. `JavelinRadius` (`float`, default `25.f`)
  10. `JavelinMaxRange` (`float`, default `3000.f`)
  11. `SpawnSockets` (`TArray<FName>`, default `[TEXT("JavelinSpawn"), TEXT("hand_l")]`)
  12. `AimHeight` (`float`, default `100.f`)
  13. `bRespondToHeal` (`bool`, default `true`)
  14. `bCancelJavelinsOnInterrupt` (`bool`, default `true`)

- **Validation Order & Diagnostic Tokens:**
  1. **All 10 floats finite first in header order:**
     - Order: `MinRange`, `MaxRange`, `Cooldown`, `Damage`, `FlightTime`, `MinSpeed`, `MaxSpeed`, `JavelinRadius`, `JavelinMaxRange`, `AimHeight`.
     - Token: `InvalidPunish.NotFinite: HealPunish.<FieldName>`
  2. **Domains in header order:**
     - `MinRange >= 0.0f` (`InvalidPunish.Negative`) and `<= 1.0e6f` (`InvalidPunish.AboveCeiling`)
     - `MaxRange > 0.0f` (`InvalidPunish.NotPositive`), `<= 1.0e6f` (`InvalidPunish.AboveCeiling`), and `> MinRange` (`InvalidPunish.MaxNotAboveMin`)
     - `Cooldown >= 0.0f` (`InvalidPunish.Negative`) and `<= 1.0e6f` (`InvalidPunish.AboveCeiling`)
     - `Damage >= 0.0f` (`InvalidPunish.Negative`), no ceiling
     - `FlightTime >= 0.05f` (`InvalidPunish.BelowFlightTimeFloor`, authored floor equal to editor metadata) and `<= 1.0e6f` (`InvalidPunish.AboveCeiling`)
     - `MinSpeed > 0.0f` (`InvalidPunish.NotPositive`) and `<= 1.0e6f` (`InvalidPunish.AboveCeiling`)
     - `MaxSpeed > 0.0f` (`InvalidPunish.NotPositive`) and `<= 1.0e6f` (`InvalidPunish.AboveCeiling`)
     - `MinSpeed <= MaxSpeed` (`InvalidPunish.MinSpeedAboveMax`), equal is valid
     - `JavelinRadius > 0.0f` (`InvalidPunish.NotPositive`) and `<= 1.0e6f` (`InvalidPunish.AboveCeiling`)
     - `JavelinMaxRange > 0.0f` (`InvalidPunish.NotPositive`) and `<= 1.0e6f` (`InvalidPunish.AboveCeiling`)
  3. **SpawnSockets array:**
     - At least one entry (authored: an empty array would silently fall back to native owner location offset at `RPGBossHealPunish.cpp:50` and hide default loss): `InvalidDependency.Missing: HealPunish.SpawnSockets`
     - Every entry not None/empty (`InvalidDependency.Missing: HealPunish.SpawnSockets`) and without whitespace or control characters (`InvalidDependency.Malformed: HealPunish.SpawnSockets`)
  4. **AimHeight:**
     - Finite (checked at step 1) and within `[-1.0e6f, 1.0e6f]` (signed): `InvalidPunish.BelowFloor: HealPunish.AimHeight` / `InvalidPunish.AboveCeiling: HealPunish.AimHeight`
  5. **Booleans:**
     - `bEnabled`, `bRespondToHeal`, `bCancelJavelinsOnInterrupt` accept both `true` and `false`.

- **Unresolved Hardcoded Parameters:**
  1. Attack Move Identifier `ThrowMove` = `TEXT("A5")` hardcoded at `RPGBossHealPunish.cpp:22`.
  2. Player drinking montage soft path hardcoded at `RPGBossHealPunish.cpp:236`.
  Neither is an authored field of `URPGBossHealPunish` or part of `FRPGHealPunishConfig`.

---

## 3. Read-Only Native Overflow Audit for HealPunish

1. **`Dist / FlightTime` (`RPGBossHealPunish.cpp:176`):**
   - In native code: `const float Speed = FMath::Clamp(FVector::Dist(From, Target) / FlightTime, MinSpeed, MaxSpeed);`
   - With `FlightTime >= 0.05f` and `From, Target` within arena bounds (`<= 1e6 cm`), `Dist <= 2.0e6 cm`, so `Dist / FlightTime <= 4.0e7 cm/s`, which is well within float32 range (~3.4e38). Overflow is **not possible** under the authored contract.
   - If unvalidated (`FlightTime == 0.0f` and `Dist > 0.0f`), native float division produces `+Inf`, clamped to `MaxSpeed`. If `Dist == 0.0f` and `FlightTime == 0.0f`, native float division produces `NaN`, which propagates into projectile launch velocity.

2. **`World->GetTimeSeconds() + Cooldown` (`RPGBossHealPunish.cpp:170`):**
   - In native code: `CooldownEnd = GetWorld()->GetTimeSeconds() + Cooldown;`
   - `CooldownEnd` is stored as a `double` (64-bit IEEE 754 float), where `GetWorld()->GetTimeSeconds()` returns `double`.
   - With `Cooldown <= 1.0e6 s` (~11.5 days), `GetTimeSeconds() + Cooldown` remains exact and cannot overflow double (~1.8e308). Overflow is **not possible** under the authored contract.

3. **`FeetZ + AimHeight` (`RPGBossHealPunish.cpp:173`):**
   - In native code: `const FVector Target(Player->GetActorLocation().X, Player->GetActorLocation().Y, RPGBossDamage::FeetZ(Player) + AimHeight);`
   - `FeetZ` is a float (~0 to 1000 cm in arena). With `AimHeight` bounded to `[-1.0e6f, 1.0e6f]`, `Target.Z` remains strictly within `[-1.0e6f, 1.0e6f + 1000]`, well within float32 limits. Overflow is **not possible** under the authored contract.

---

## 4. Definitive Field Domain Table (DD22 Lead Contract)

| Field | Native Type | Default | Domain / Range | Label | Reasoning & Code Evidence |
|---|---|---|---|---|---|
| `bEnabled` | `bool` | `true` | `{true, false}` | **AUTHORED CHOICE** | Read in `OnHealStarted()` (`RPGBossHealPunish.cpp:101`). Both states accepted. |
| `MinRange` | `float` | `400.f` | `0.0f <= MinRange <= 1.0e6f` | **AUTHORED CHOICE** | Read in `OnHealStarted()` (`:120`). Editor ClampMin=0.0 is metadata. Upper ceiling prevents float overflow. |
| `MaxRange` | `float` | `1000.f` | `MinRange < MaxRange <= 1.0e6f` | **AUTHORED CHOICE** | Upper engagement window in `OnHealStarted()` (`:120`). Must be strictly `> MinRange` for non-degenerate window. |
| `Cooldown` | `float` | `4.f` | `0.0f <= Cooldown <= 1.0e6f` | **AUTHORED CHOICE** | Added to `GetTimeSeconds()` in `Release()` (`:170`). Non-negative, capped at 1.0e6 s. |
| `Damage` | `float` | `12.f` | `0.0f <= Damage` (finite, no ceiling) | **AUTHORED CHOICE** | Passed to `Javelin->Launch()` in `Release()` (`:181`). Same policy as DD21 Shockwave Damage. |
| `FlightTime` | `float` | `1.2f` | `0.05f <= FlightTime <= 1.0e6f` | **AUTHORED CHOICE** | Denominator in `Release()` (`:176`). Floor 0.05 matches editor metadata; prevents extreme speed/division risk. |
| `MinSpeed` | `float` | `450.f` | `0.0f < MinSpeed <= 1.0e6f` | **AUTHORED CHOICE** | Lower speed clamp in `Release()` (`:176`). Must be strictly positive and `<= MaxSpeed`. |
| `MaxSpeed` | `float` | `2500.f` | `MinSpeed <= MaxSpeed <= 1.0e6f` | **AUTHORED CHOICE** | Upper speed clamp in `Release()` (`:176`). Must be `>= MinSpeed` for coherent speed window. |
| `JavelinRadius` | `float` | `25.f` | `0.0f < JavelinRadius <= 1.0e6f` | **AUTHORED CHOICE** | Collision sphere radius passed to `Launch()` (`:181`). Must be strictly positive. |
| `JavelinMaxRange` | `float` | `3000.f` | `0.0f < JavelinMaxRange <= 1.0e6f` | **AUTHORED CHOICE** | Lifetime range passed to `Launch()` (`:181`). Must be strictly positive. |
| `SpawnSockets` | `TArray<FName>` | `["JavelinSpawn", "hand_l"]` | Length >= 1, non-empty, no whitespace/control | **AUTHORED CHOICE** | Iterated in `GetSpawnLocation()` (`:42`). Empty array rejected to prevent hidden fallback to native offset. |
| `AimHeight` | `float` | `100.f` | `-1.0e6f <= AimHeight <= 1.0e6f` | **AUTHORED CHOICE** | Added to `FeetZ` in `Release()` (`:173`). Finite, bounded within magnitude ceiling. |
| `bRespondToHeal` | `bool` | `true` | `{true, false}` | **AUTHORED CHOICE** | Guard in `OnHealStarted()` (`:101`). Both states accepted. |
| `bCancelJavelinsOnInterrupt` | `bool` | `true` | `{true, false}` | **AUTHORED CHOICE** | Guard in `CancelAll()` (`:81`). Both states accepted. |

---

## 5. Historical A-186 Proposal Text (Preserved for Audit Record)

*(The text below is the original proposal submitted in A-186, preserved verbatim for historical audit purposes. It is SUPERSEDED by Sections 1-4 above).*

### Historical Table from A-186:
| Field | Native Type | Default | Proposed Domain | Label | Derivation / Code Evidence |
|---|---|---|---|---|---|
| `bEnabled` | `bool` | `true` | `{true, false}` | **NATIVE-DERIVED** | Direct execution guard in `TickComponent()` (`RPGBossHealPunish.cpp:202`). Any boolean value accepted. |
| `MinRange` | `float` | `400.f` | `0.0f <= MinRange < MaxRange`, `<= 1.0e6f` | **NATIVE-DERIVED** | Checked in `OnHealStarted()` (`RPGBossHealPunish.cpp:120`). Must be non-negative (`ClampMin="0.0"` in header `:37`) and strictly `< MaxRange` so range window `[MinRange, MaxRange]` is non-empty. Ceiling `1.0e6f` prevents float overflow in distance checks. |
| `MaxRange` | `float` | `1000.f` | `MinRange < MaxRange <= 1.0e6f` | **NATIVE-DERIVED** | Upper window bound in `OnHealStarted()` (`RPGBossHealPunish.cpp:120`). Must be strictly `> MinRange` and `> 0.0f` (`ClampMin="0.0"` in header `:40`). Ceiling `1.0e6f` matches arena magnitude envelope. |
| `Cooldown` | `float` | `4.f` | `0.0f <= Cooldown <= 1.0e6f` | **NATIVE-DERIVED** | Added to world time in `Release()` (`RPGBossHealPunish.cpp:189`). Header enforces `ClampMin="0.0"` (`:44`). Must be `>= 0.0f`. Ceiling `1.0e6f` ensures `World->GetTimeSeconds() + Cooldown` does not overflow float32/double. |
| `Damage` | `float` | `12.f` | `0.0f <= Damage <= 500.0f` | **NATIVE-DERIVED / AUTHORED CHOICE** | Passed to `Javelin->Launch()` in `Release()` (`RPGBossHealPunish.cpp:182`). Header enforces `ClampMin="0.0"` (`:48`). Lower bound `>= 0.0f` is native-derived; upper bound `500.0f` is authored choice (player HP pool is 120, default is 12.0f; does not accumulate). |
| `FlightTime` | `float` | `1.2f` | `0.05f <= FlightTime <= 1.0e6f` | **NATIVE-DERIVED** | Denominator in speed calculation `Dist / FlightTime` in `Release()` (`RPGBossHealPunish.cpp:176`). Header explicitly specifies `meta = (ClampMin = "0.05")` (`:54`). Must be `>= 0.05f` to prevent division by zero or near-zero float overflow. |
| `MinSpeed` | `float` | `450.f` | `1.0f <= MinSpeed <= MaxSpeed`, `<= 1.0e6f` | **NATIVE-DERIVED** | Lower bound in `FMath::Clamp(Dist / FlightTime, MinSpeed, MaxSpeed)` (`RPGBossHealPunish.cpp:176`). Header enforces `ClampMin="1.0"` (`:57`). Must be strictly `> 0.0f` and `<= MaxSpeed` to prevent undefined `FMath::Clamp()` behavior. Ceiling `1.0e6f` caps flight speed. |
| `MaxSpeed` | `float` | `2500.f` | `MinSpeed <= MaxSpeed <= 1.0e6f` | **NATIVE-DERIVED** | Upper bound in `FMath::Clamp()` (`RPGBossHealPunish.cpp:176`). Header enforces `ClampMin="1.0"` (`:60`). Must be `>= MinSpeed`. Ceiling `1.0e6f` caps flight speed. |
| `JavelinRadius` | `float` | `25.f` | `1.0f <= JavelinRadius <= 1.0e6f` | **NATIVE-DERIVED** | Projectile collision sphere radius in `Release()` (`RPGBossHealPunish.cpp:181`). Header enforces `ClampMin="1.0"` (`:65`). Must be `> 0.0f` for collision to function. Ceiling `1.0e6f` prevents infinite/giant collision. |
| `JavelinMaxRange` | `float` | `3000.f` | `1.0f <= JavelinMaxRange <= 1.0e6f` | **NATIVE-DERIVED** | Projectile lifetime distance in `Release()` (`RPGBossHealPunish.cpp:181`). Header enforces `ClampMin="1.0"` (`:68`). Must be `> 0.0f`. Ceiling `1.0e6f` caps maximum travel. |
| `SpawnSockets` | `TArray<FName>` | `{TEXT("JavelinSpawn"), TEXT("hand_l")}` | Array of non-empty `FName`, matches `^[A-Za-z0-9_]+$`; empty array permitted | **NATIVE-DERIVED** | Iterated in `GetSpawnLocation()` (`RPGBossHealPunish.cpp:63-68`). Empty array is safe (falls back to owner location offset at `:71`). Non-empty entries must be valid identifiers without whitespace or control characters. |
| `AimHeight` | `float` | `100.f` | `-1.0e6f <= AimHeight <= 1.0e6f` | **NATIVE-DERIVED / AUTHORED CHOICE** | Added to player feet height `Target.Z = FeetZ + AimHeight` (`RPGBossHealPunish.cpp:173`). Signed float (default `100.f` is chest level). Bound `[-1.0e6, 1.0e6]` ensures `FeetZ + AimHeight` remains finite. Physically meaningful values are `[-500.0, 500.0]`. |
| `bRespondToHeal` | `bool` | `true` | `{true, false}` | **NATIVE-DERIVED** | Direct toggle in `OnHealStarted()` (`RPGBossHealPunish.cpp:106`). Any boolean value accepted. |
| `bCancelJavelinsOnInterrupt` | `bool` | `true` | `{true, false}` | **NATIVE-DERIVED** | Direct toggle in `CancelAll()` (`RPGBossHealPunish.cpp:88`). Any boolean value accepted. |
