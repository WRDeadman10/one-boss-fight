# F6a Implementation Second-Review: Native Boss Health, Hit Intake & Death Authority

**Author:** Antigravity  
**Date:** 2026-10-30  
**Context:** Lead Order `[C-420]` second-review of F6a runtime source additions while awaiting F6b build.  
**Reviewed Files:**  
- `Source/OneBossFight/Player/RPGNativeBossHealth.h`
- `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.h` and `.cpp`
- `Source/OneBossFight/Pack/RPGBlueprintCall.h`
- `Source/OneBossFight/Player/RPGHitIntake.h` and `.cpp`

---

## 1. Executive Summary

The F6a native boss health implementation introduces a clean native bridge (`IRPGNativeBossHealth`) that decouples the framework boss from the legacy pack attribute component reflection while preserving read compatibility across consumers (`ReadAttribute`). 

This second-review identifies **six concrete findings**:
1. **[CRITICAL / CONTRACT] Double-Death Reentrancy:** Absence of `bDead` guard at entry of `Die()` and missing `Health <= 0.` check in `ApplyPlayerHit` can trigger duplicate `boss_dead` and duplicate `RESULT outcome=BossDefeated` lines.
2. **[HIGH / CRASH] Null Pointer Dereference in `ReadAttribute`:** `FCString::Stricmp(AttributeTag, ...)` dereferences `AttributeTag` without checking for `nullptr`.
3. **[MEDIUM / HYGIENE] Null Actor Cast Ordering in `HandlePackHit`:** Interface cast is attempted on `Target` before `!Target` is verified.
4. **[MEDIUM / BUILD] Shipping Build Stripping of Test Hook:** `#if UE_BUILD_SHIPPING` completely strips `InjectBossHitForTest`, causing silent failure if automated packaging or shipping benchmarks drive test hits.
5. **[LOW / THREAD] Lack of GameThread Guard in `ReadNativeHealth`:** Read access to non-atomic double `Health` lacks `check(IsInGameThread())`.
6. **[PERFORMANCE] Interface Cast Overhead on Unhit Non-Native Actors:** `Cast<const IRPGNativeBossHealth>(Actor)` walks interface table for every non-boss actor querying `"Attribute.Health"`.

---

## 2. Detailed Findings & Triggering Sequences

### Finding 1: Double-Death Reentrancy & Duplicate Contract Lines
- **Files & Lines:** `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:134, 138, 160-169`
- **Triggering Sequence:**
  1. Boss health is low (e.g., 50.0). A lethal hit arrives via `ApplyPlayerHit(1.0)`.
  2. Line 136 executes `Health -= Loss;` (Health reaches 0.0).
  3. Line 138 evaluates `if (Health <= 0.) Die();` and invokes `Die()`.
  4. In `Die()`, line 144 sets `bDead=true;`, then line 147 executes `Executor->Abort(TEXT("BossDead"))`.
  5. While `Executor->Abort()` is cleaning up, stopping montages, or notifying delegates, a secondary hit callback or queued frame hit arrives and calls `ApplyPlayerHit()`.
  6. Line 134 checks:
     ```cpp
     if (!bHittable||bDead||bFailed||!bInitialized||!FMath::IsFinite(Multiplier)||Multiplier<0.) return 0.;
     ```
     Notice: If `Die()` was called directly from another failure path or if `bDead` was not yet set, or if `Die()` itself is entered twice, `Die()` has **no guard**:
     ```cpp
     void ARPGFrameworkBossCharacter::Die()
     {
         bDead=true;
         // ...
         UE_LOG(LogTemp, Display, TEXT("[FrameworkProof] boss_dead generation=%llu executorAborted=1"), GenerationId);
         UE_LOG(LogTemp, Display, TEXT("[FrameworkProof] RESULT outcome=BossDefeated ..."));
     }
     ```
  7. **Failure Result:** Two `boss_dead` lines or two `RESULT outcome=BossDefeated` lines are emitted in the log. This violates the strict F6a log contract: *"after boss_dead no decision/playback_start/hit-on-player lines ... and exactly one boss_dead; RESULT BossDefeated exactly once"*.
- **Recommended Fix:**
  - Add `if (bDead) return;` at the very top of `Die()` (`RPGFrameworkBossCharacter.cpp:161`).
  - Add `Health <= 0.` to the guard in `ApplyPlayerHit()` (`RPGFrameworkBossCharacter.cpp:134`).

---

### Finding 2: Fatal Access Violation on Null `AttributeTag` in `ReadAttribute`
- **Files & Lines:** `Source/OneBossFight/Pack/RPGBlueprintCall.h:210-213`
- **Code:**
  ```cpp
  inline bool ReadAttribute(const AActor* Actor, const TCHAR* AttributeTag, bool bMax, double& Value)
  {
      if (FCString::Stricmp(AttributeTag, TEXT("Attribute.Health")) == 0)
      {
          // ...
      }
  ```
- **Triggering Sequence:**
  1. A caller passes a `nullptr` `AttributeTag` (e.g. from an uninitialized `FName`, an empty gameplay tag string conversion, or an invalid tag table lookup).
  2. `FCString::Stricmp(nullptr, TEXT("Attribute.Health"))` immediately attempts to read memory address `0x00000000`.
  3. **Failure Result:** Access Violation crash in GameThread.
  4. Note that line 223 downstream has `if (!Attributes || !Tag.IsValid())`, but line 213 crashes before reaching line 223.
- **Recommended Fix:**
  Add null check at function entry:
  ```cpp
  if (!Actor || !AttributeTag)
  {
      return false;
  }
  ```

---

### Finding 3: Target Null Check Ordering in `HandlePackHit`
- **Files & Lines:** `Source/OneBossFight/Player/RPGHitIntake.cpp:413-422`
- **Code:**
  ```cpp
  void URPGHitIntake::HandlePackHit(FHitResult HitResult)
  {
      AActor* Target = HitResult.GetActor();
      if (IRPGNativeBossHealth* Native = Cast<IRPGNativeBossHealth>(Target))
      {
          Native->ApplyPlayerHit(1.0);
          return;
      }
      if (!Target || !URPGPlayerMovesSubsystem::IsPackBoss(Target))
  ```
- **Triggering Sequence:**
  1. A player swing strikes world geometry, static level props, or terrain where `HitResult.GetActor()` returns `nullptr`.
  2. Line 417 performs `Cast<IRPGNativeBossHealth>(nullptr)`. While Unreal's `Cast` template safely returns `nullptr` on a null object, defensive engine programming requires verifying `if (!Target)` before dispatching interface polymorphism.
  3. Line 422 checks `if (!Target || !URPGPlayerMovesSubsystem::IsPackBoss(Target))` and increments `++OtherHitCount`.
  4. By placing the null check before line 417, null actor hits cleanly increment `OtherHitCount` and exit without unnecessary interface evaluation.
- **Recommended Fix:**
  Move the `!Target` guard above line 417:
  ```cpp
  if (!Target)
  {
      ++OtherHitCount;
      return;
  }
  ```

---

### Finding 4: Shipping Build Stripping in `InjectBossHitForTest`
- **Files & Lines:** `Source/OneBossFight/Player/RPGHitIntake.cpp:398-410`
- **Code:**
  ```cpp
  void URPGHitIntake::InjectBossHitForTest(AActor* Boss)
  {
  #if UE_BUILD_SHIPPING
      return;
  #else
      if (Boss)
      {
          // ...
      }
  #endif
  }
  ```
- **Triggering Sequence:**
  1. The project targets packaged 1080p / 60 FPS verification (`PROJECT_STATE.md`).
  2. If an automated headless test, packaged PIE run, or performance benchmark is compiled with `UE_BUILD_SHIPPING=1`, `InjectBossHitForTest` turns into an empty no-op.
  3. The test harness will wait indefinitely for boss health reduction or timeout, because no hits are injected and no `[FrameworkProof] boss_health_read` lines are emitted.
- **Recommended Fix:**
  If test injection is intended strictly for editor automation, document this constraint explicitly in `TEST_PLAN.md`. If packaged validation runs require test hit injection, guard with `#if !UE_BUILD_SHIPPING || WITH_AUTOMATION_TESTS`.

---

### Finding 5: GameThread Concurrency Guard for `ReadNativeHealth`
- **Files & Lines:** `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.h:27`, `RPGFrameworkBossCharacter.cpp:136`
- **Triggering Sequence:**
  1. `ReadNativeHealth` is an inline const method returning `double Health`:
     ```cpp
     virtual bool ReadNativeHealth(bool bMax, double& Out) const override 
     { 
         if (!bHittable) return false; 
         Out = bMax ? MaxHealth : Health; 
         return true; 
     }
     ```
  2. `Health` is a raw 64-bit IEEE-754 float (`double Health=0.0;`) modified by `ApplyPlayerHit()` on line 136.
  3. If a background worker (e.g. async UI widget, HUD slate tick off-thread, or audio thread parameter update) calls `RPGPack::ReadAttribute` on the boss, torn double reads or data races can occur.
- **Recommended Fix:**
  Add `check(IsInGameThread());` or ensure reads are synchronized.

---

### Finding 6: Interface Cast Overhead in Hot `ReadAttribute` Path
- **Files & Lines:** `Source/OneBossFight/Pack/RPGBlueprintCall.h:213-220`
- **Triggering Sequence:**
  1. In a multi-actor combat scene, `ReadAttribute(Actor, TEXT("Attribute.Health"), ...)` is called every frame across player, pack enemies, and target dummies.
  2. On every call where `AttributeTag == "Attribute.Health"`, `Cast<const IRPGNativeBossHealth>(Actor)` is evaluated.
  3. For actors that do *not* implement `IRPGNativeBossHealth` (the player, pack minions), `Cast` searches the `UClass` interface table and returns `nullptr`, before falling back to the cached attribute component reflection path.
  4. While the cost is negligible for 1-2 actors, if enemy count scales, a class flag or fast interface check (`Actor->GetClass()->ImplementsInterface(URPGNativeBossHealth::StaticClass())`) or checking whether `Actor->IsA<ARPGFrameworkBossCharacter>()` avoids generic interface map traversal.
- **Evaluation:**
  In the current 1-boss duel (`OneBossFight`), there is only 1 boss and 1 player actor. Therefore, the interface cast overhead is negligible (< 100 ns) and acceptable for the current architecture.

---

## 3. Summary of Recommendations for F6b Integration

| Finding | Severity | File & Line | Recommended Action |
|:---|:---:|:---|:---|
| **1. Double-Death Reentrancy** | CRITICAL | `RPGFrameworkBossCharacter.cpp:134, 142` | Add `if (bDead) return;` at entry of `Die()` and `Health <= 0.` to `ApplyPlayerHit` guard. |
| **2. Null Tag Dereference** | HIGH | `RPGBlueprintCall.h:211` | Add `if (!Actor \|\| !AttributeTag) return false;` at entry of `ReadAttribute`. |
| **3. Target Null Ordering** | MEDIUM | `RPGHitIntake.cpp:415` | Move `if (!Target)` check before `Cast<IRPGNativeBossHealth>`. |
| **4. Shipping Build Guard** | MEDIUM | `RPGHitIntake.cpp:400` | Document shipping exclusion or use `!UE_BUILD_SHIPPING \|\| WITH_AUTOMATION_TESTS`. |
| **5. GameThread Guard** | LOW | `RPGFrameworkBossCharacter.h:27` | Add `checkSlow(IsInGameThread());` inside `ReadNativeHealth`. |
| **6. Interface Cast Cost** | LOW | `RPGBlueprintCall.h:215` | Acceptable for 1v1 duel; consider caching if multi-actor scaling occurs. |
