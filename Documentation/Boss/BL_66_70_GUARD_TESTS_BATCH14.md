# BL-66..70: guard tests, batch 14 (BossStuck, TelegraphScale, Track)

Lane BL, batch 14 of 20. I continued per X-2190 ("continue after batch without waiting"); the headers follow the BL-01..05 queue. C (implementer), 2026-11-12.

**Three new test files only.** No production source edits, and no Unreal, build, PIE, commit or push.
- **Not compiled or run:** the engine-lock acceptance build is pending with the lead.
- **Checked by hand:** every assertion was traced against the header source.

## BL-69: re-verification and observability (by hand)

| Header | Audit gap (line) | Existing coverage, not repeated | Discriminates? |
|---|---|---|---|
| `RPGBossStuckRules.h` | `IsStuck` with a negative `MinRatio` (`:42`) | `…BossStuck.Rules`: NaN or Inf threshold, zero window, ratio boundary, overflow; QueueD window edges | **No, equivalent:** moved ≥ 0 gives a ratio ≥ 0, which is never below a negative MinRatio |
| `RPGBossTelegraphScaleRules.h` | `MinRateScale` ≤ 0 or > 1; `ActiveStartSeconds` ≤ 0 (`:12-13`) | `…TelegraphScale.Rules`: fair card, beyond the cap, zero rate, Inf requirement, NaN floor | **`MinRateScale ≤ 0`: yes**, because the floor becomes ≤ 0 and 0.8 would be returned. **`> 1` and `ActiveStart ≤ 0`: no, equivalent**: `Needed ≤ Current < Floor`, or `Needed ≤ 0 < Floor` |
| `RPGBossTrackRules.h` | `PlayerActivityName` mapping (`:146`); `WatchdogTimeoutSeconds` with a negative clip or blend-out (`:150`) | Runtime watchdog `:517-525` (bad recovery end or play rate, clip and blend budgets); the Track sweep | **Yes, both**: without the guard, a negative clip or blend-out still yields a positive timeout |

## BL-66..68: tests

| Task | File | Automation test | Cases |
|---|---|---|---|
| BL-66 | `Source/OneBossFight/Tests/RPGBossStuckGuardTests.cpp` | `OneBossFight.Framework.BossStuck.Guards` | **Control:** ratio 0.1 over 0.4 s is stuck. A MinRatio of -0.1 is refused (equivalent, documented) and does not consume the one-shot flip. |
| BL-67 | `.../RPGBossTelegraphScaleGuardTests.cpp` | `OneBossFight.Framework.TelegraphScale.Guards` | **Control:** slowed to 0.8. **Discriminating:** scale 0 and -0.1 give -1. **Equivalent:** scale 1.1, ActiveStart 0 and -0.4 give -1. |
| BL-68 | `.../RPGBossTrackGuardTests.cpp` | `OneBossFight.Framework.Track.Guards` | The exact `PlayerActivityName` for None, Flask and HeavyCommit, and the `"None"` fallback for an invalid value. **Watchdog:** control 2.15 s; a clip of -1 or a blend-out of -0.1 is invalid (< 0). |

## BL-70: status

- **Names:** the new names are unique; the existing tests are `…BossStuck.Rules`, `…TelegraphScale.Rules`, `…Track.Sweep` and `…Runtime.TrackYawCap`.
- **Defects:** none indicated.
- **Pending:** the engine-lock build.
