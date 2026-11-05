# Report 12: tick audit, Shipping hardening, and balance review

## Scope and validation

- Completed Brief 10 first; `python -I Scripts/BalanceModel.py` read nine
  calibration records and printed 161.2 s Starter, 158.3 s Strength, and
  145.4 s Dex at skill 1.0 for the owner proposal.
- No editor, build, automation test, PIE, package, or game run occurred.
- This report is static review only; compilation remains Claude's validation.

## T1: tick and short-timer audit

Cost labels are estimates from the visible work, not measurements.

| Tick owner | Evidence / cadence | Per-tick work | Cost | Suggested action |
|---|---|---|---|---|
| `URPGHitIntake` | `Player/RPGHitIntake.cpp:159,175-194`, every frame | montage read; bind retry each 0.25 s; boss iterator/search each 0.5 s; health reflection every frame | worth fixing | Cache the watched boss attribute object or sample health only while a scaled hit is pending. |
| `URPGSwingTracker`, `URPGAttackTracker`, `URPGDodgeTiming`, `URPGCameraRig`, `URPGTraceGuard`, `URPGBossStagger`, `URPGBossDeath`, `URPGBossLowSweep`, `URPGBossShockwave`, `URPGBossHealPunish`, `URPGBossJavelin` | constructors listed by `rg`; no positive interval, therefore frame cadence | combat state, montage/component reads, movement or trace state | small to worth fixing | Keep correctness-critical trackers frame based; profile the boss-only combat set together before changing cadence. |
| `URPGTraceAudit` | `Player/RPGTraceAudit.cpp:23-31,155+`, post-update frame tick in non-Shipping | socket arrays, hit-set arrays, maps, `FString::Printf`, reflected health reads and Log calls on window edges | worth fixing | disabled in Shipping by this change; in Development keep for driver evidence. |
| `URPGCombatDebug` | `Player/RPGCombatDebug.cpp:62-70,535-559`, frame tick when debug cvar enabled | constructs `TArray<FString>`, reflection, on-screen messages; logging at most once/sec | worth fixing | disabled in Shipping already; Development behavior retained. |
| `URPGIFrameMonitor`, `URPGBossLegend`, `URPGFootsteps`, `URPGBossHud` / widget | `Player/RPGIFrameMonitor.cpp:20`, `Player/RPGLegend.cpp:257`, `Audio/RPGFootsteps.cpp:16`, `UI/RPGBossHud.cpp:180,281` | state/animation checks; HUD/widget presentation every frame | small | profile HUD string rebuilding under the packaged benchmark; avoid changing timing before capture. |
| `URPGBossPosture` | `Player/RPGBossPosture.cpp:32-33`, 0.05 s | attribute pin/read and posture regeneration | small | 20 Hz is appropriate; cache reflection target if profiling shows it. |
| `URPGBossEncounter`, `URPGBossPhases`, `URPGSevarogDirector`, `URPGBuildLoadout`, `URPGRiposteInput` | `Player/RPGBossEncounter.cpp:59-61`; `Player/RPGBossPhases.cpp:51-53`; `Boss/RPGSevarogDirector.cpp:27-29`; `Player/RPGBuildLoadout.cpp:255-256`; `Player/RPGRiposteInput.cpp:16-17` | AI/phase/build polling | negligible to small | Existing 0.1/0.2 s cadence is reasonable; no local change. |
| `URPGBossMusic` | `Audio/RPGBossMusic.cpp:16-17`, 0.25 s | music state/crossfade check | negligible | no change. |
| Arena actors (`RPGArenaDressing`, `RPGEmberField`, `RPGFireSource`, `RPGFogGate`) and benchmark actor | constructors found in `Arena/*.cpp`, `Benchmark/RPGBenchmarkRunner.cpp:36-38` | visual/environment or benchmark work | small | profile in packaged scene; benchmark actor starts disabled. |
| Next-tick timers | `RPGHitIntake.cpp:398`, `RPGBossLook.cpp:31`, `RPGBossStagger.cpp:570` | one deferred completion/attach/start | negligible | no change. |
| Director timer | `Boss/RPGSevarogDirector.cpp:82` | delayed lightning callback | negligible | no change. |

The audit found no per-frame `LoadObject` in the named T2 components. The
trace audit does do repeated `FindComponentByClass`, allocations, string work,
and Blueprint-attribute reflection while enabled; it is the material debug
cost and is now off in Shipping.

## T2: Shipping hardening change

| File | Before | After |
|---|---|---|
| `Source/OneBossFight/Player/RPGTraceAudit.cpp:25-30` | Shipping set only `bCanEverTick = false`. | Shipping also sets `bStartWithTickEnabled = false`. Non-Shipping code is unchanged. |

`RPGCombatDebug` already has unconditional reflected declarations in
`Player/RPGCombatDebug.h:83-88`, no-op Shipping bodies, and both tick flags
false in `Player/RPGCombatDebug.cpp:64-70`. `RPGInputTestUtils` declarations
are unconditional in `Combat/RPGInputTestUtils.h:24-41`; its Shipping bodies
return false/zero or no-op at `Combat/RPGInputTestUtils.cpp:23-113`, so a
reflected call cannot set fixed FPS or `r.VSync`.

Creation is still performed by `RPGPlayerMovesSubsystem`, which was outside
the claimed files. Removing those components conditionally needs a separate
review because existing code/BluePrint references may require them.

### Symbols used by the edit

| Symbol | Declaration / evidence |
|---|---|
| `URPGTraceAudit::URPGTraceAudit` | `Source/OneBossFight/Player/RPGTraceAudit.h:21-78` declares the class; constructor is defined at `.cpp:23`. |
| `PrimaryComponentTick` | inherited `UActorComponent` tick function, used throughout the class before this edit (`RPGTraceAudit.cpp:26,29`). |
| `bCanEverTick`, `bStartWithTickEnabled` | members of that tick function; the latter is already used in `RPGCombatDebug.cpp:66,69` and project component constructors. |
| `UE_BUILD_SHIPPING` | Unreal build configuration macro already enclosing the constructor branch at `RPGTraceAudit.cpp:25`. |

I reread `RPGTraceAudit.cpp:23-32` twice after the edit. No new include or
new identifier was introduced.

## T3: independent balance-code findings

### High — max-health application ignores `WriteMaxAttribute` failure

- **Evidence:** `Player/RPGBossEncounter.cpp:84-88` calls
  `WriteMaxAttribute(...)` and unconditionally writes
  `Current * BossMaxHealth / Max`. `Pack/RPGBlueprintCall.h:144-169` returns a
  bool from reflected `Set Max Attribute Value`, but the caller discards it.
- **Scenario:** if the pack function name or parameter layout is unavailable,
  a fresh boss at `500/500` takes the unconditional current-value write of
  `2000`; the max stays 500. Depending on pack clamping this either creates an
  invalid 2000/500 state or silently loses the intended configuration while
  `bMaxHealthApplied` remains true.
- **Fix:** require successful `WriteMaxAttribute`, reread max/current, verify
  the max is within tolerance of `BossMaxHealth`, then write the proportional
  current value and set `bMaxHealthApplied`. Retry on later 0.1 s ticks on
  failure.

### High — scaler may assign non-weapon health loss to a scaled hit

- **Evidence:** `Player/RPGDamageScale.h:39-59` stores every health loss when
  no pending scaled hit matches; `Player/RPGHitIntake.cpp:232-239` reports every
  observed boss-health decrease; `.cpp:474-481` claims a record with the row
  multiplier. The matcher has no damage source, target identity beyond the
  intake instance, or loss-size constraint.
- **Scenario:** Starter's `0.39` hit is finalized, then an unrelated 60-health
  bleed proc or boss environmental loss arrives within `Window = 0.35`. The
  scaler returns 36.6 health for that loss, incorrectly restoring it as though
  it were the Starter weapon hit. Conversely an unrelated loss stored just
  before a Starter record can be claimed at `.h:66-72`.
- **Fix:** correlate only a loss captured after the hit's actual pack event,
  carry target/hit identity into the pending record, and reject implausible
  loss magnitudes relative to the observed pack weapon damage. At minimum,
  expire pending scaled hits before processing a non-recorded loss and record a
  diagnostic instead of scaling it.

### Medium — matcher accepts a future timestamp as a valid match

- **Evidence:** `Player/RPGDamageScale.h:48` tests only
  `Time - Hits[Index].Time <= Window`; `:68` has the same one-sided predicate
  for losses.
- **Scenario:** if tick/order changes let `OnLoss(10.00, ...)` observe a loss
  after a record queued at 10.10 (or equivalent deferred callback ordering),
  `-0.10 <= 0.35` is true and the future hit claims the earlier loss.
- **Fix:** use `FMath::Abs(Time - Candidate.Time) <= Window` only if both
  directions are intended; preferably require `Time >= Candidate.Time` where
  the event ordering is known.

## Not verified

- No C++ compilation, UHT pass, editor launch, PIE driver, package, or
  benchmark was run.
- Pack reflection signatures, the first-PIE zero-health recovery, and the
  balance multiplier's real event order need Claude's build and PIE validation.
