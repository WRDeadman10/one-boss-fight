# B10 — Live Authored Close Clips

## Delivered

- Added `URPGBossCloseClipSwap`, which reflects only the live `GA_GS_Boss_CloseAttack_C.AttackMontages` `F_AbilityMontage` array.
- The component replaces exactly pack `GS_Attack03_Montage`, `GS_Attack01_Montage`, and `GS_Attack02_Montage` with `AM_Boss01_A1`, `AM_Boss01_A3a`, and `AM_Boss01_A3b`; `GS_Attack04_Montage` remains untouched.
- Validation requires the expected four-entry pack array and all three unique replacement sources before mutating anything. Any mismatch is permanent fail-open and leaves the pack entries intact.
- The component restores originals on encounter reset, death, EndPlay, and its non-Shipping test disable hook.
- `RPGAttackTracker` now recognizes authored names and pack fallback names. Authored timings are A1 `0.33 / 0.35-0.50 / 1.20`, A3a `0.38 / 0.40-0.60 / 0.80`, and A3b `0.13 / 0.15-0.40 / 1.3333`; the authored rows bypass `rpg.CloseTelegraph` rate scaling. A1b retains its pack montage and old telegraph behavior.

## Files

- `Source/OneBossFight/Player/RPGBossCloseClipSwap.h`
- `Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp`
- `Source/OneBossFight/Player/RPGBossCloseClipSwapRules.h`
- `Source/OneBossFight/Player/RPGAttackTracker.h`
- `Source/OneBossFight/Player/RPGAttackTracker.cpp`
- `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp`
- `Source/OneBossFight/Tests/RPGBossCloseClipSwapTests.cpp`
- `Scripts/Editor/pie_authored_close_clips.py`
- `Scripts/RunDrivers.ps1`
- `Documentation/TEST_PLAN.md`

## Validation

- Pending: C++ compilation, automation test execution, and PIE execution are Claude-owned and were not run in this task.
- The driver contains 14 assertions; its `RunDrivers.ps1` minimum is 14.
- Dormant/Wake was not started; C-73 reserves it for B11.
