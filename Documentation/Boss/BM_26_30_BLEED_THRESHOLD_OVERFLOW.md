# BM-26..30: KI-128 bleed threshold-growth overflow (lane BM, batch 6 of 10)

C (implementer), 2026-11-12.

New file: `Source/OneBossFight/Tests/RPGBleedThresholdOverflowTests.cpp` (`OneBossFight.Framework.Bleed.ThresholdGrowthOverflow`). **Test only:** no production source change. **Not compiled or run:** the native run is engine-gated with the lead.

## BM-26: growth site

`RPGBleedRules.h`, in `Apply`: `State.Threshold = FMath::Min(State.Threshold + Config.ThresholdIncrease, Config.ThresholdMax)`. `URPGBossBleed` (`RPGBossBleed.cpp`) delegates to this rule and only logs `State.Threshold`, so this is the single growth site. The DD19 adapters (`RPGBossBleedAdapters.*`) only map configuration.

## BM-27: arithmetic (traced by hand)

- With `Threshold = Increase = FLT_MAX`, the intermediate `FLT_MAX + FLT_MAX` is `+Inf`.
- `FMath::Min(A, B) = A <= B ? A : B`, so `+Inf <= FLT_MAX` is false and the result is `B = FLT_MAX`, which is finite.
- **The overflow is transient. The stored threshold is always finite and at most `ThresholdMax`.** The input guards already require a finite `ThresholdMax`, and the existing property test asserts `Threshold <= ThresholdMax`.

## BM-28: test (new)

| Case | Assertions |
|---|---|
| control | a 100 hit procs; the threshold grows to 120 |
| **overflowing intermediate** | config `Increase = Max = FLT_MAX`, state threshold `FLT_MAX`, a `FLT_MAX` hit gives **Proc**; the threshold is **finite and equals `FLT_MAX`**; buildup resets to 0; the **next 1.0 hit is Added**, so the state stays valid (not refused) |
| clamp without overflow | from 150, an increase of 100 with cap 200 gives exactly 200 |

**Not duplicated:** `RPGBossDamageBleedFiniteInputTests.cpp:46-51` overflows the **buildup** with default thresholds (20 and 200); no existing test overflows the **threshold** intermediate.

## BM-29: clamp proposal

**No source change is needed for correctness:** the result is already bounded. An optional proposal, the lead's call, for clarity only: compute the growth as `Threshold + FMath::Min(Increase, ThresholdMax - Threshold)`, which avoids the transient `+Inf`. It would not change behavior for any valid input.

## BM-30: limits and KI-128 scope

KI-128 also lists **double-to-float health narrowing** and the **DD20 Distance+PlayerRadius / feet-ground** external-input risks. Those are not covered here, because they need external-input context; they stay Open. The threshold-growth part is now pinned by a test, pending the engine-gated run.

**Name uniqueness:** checked by `grep` (one file).
