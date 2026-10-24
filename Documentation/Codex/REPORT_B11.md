# B11 — Authored Dormant and Wake

## Implementation

- Added `URPGBossDormantWake` and `RPGBossDormantWakeRules`. The component soft-loads `AN_Boss01_DormantIdle` and `AN_Boss01_Wake` at `BeginPlay`, uses `RPGBossClips::Play` in the pack’s discovered slot, loops the dormant idle, and plays wake once.
- `URPGBossEncounter::Sleep()` starts the dormant loop. `Wake()` now holds the pack behaviour, starts the wake sequence, sets `bWaking`, and resumes only through `FinishWake()` when the component observes that the wake montage has stopped. Missing clips fail open through the original immediate resume path.
- `URPGAttackTracker::StartMove`, `IsNeutral`, and the live montage veto treat `IsWaking()` as an attack-blocking state. The pack brain remains held, so ordinary selection cannot start an attack during wake.
- Reset, death, phase transition, stance break and EndPlay stop both dynamic clips and clear the wake state. `RPGBossDormantWake` attaches immediately after `RPGBossEncounter` in `RPGPlayerMovesSubsystem` and ticks after it.
- Added `RPGBossDormantWakeTests.cpp`, `pie_dormant_wake.py` (12 checks), `RunDrivers.ps1` registration and `DORMANT-WAKE-01` in `TEST_PLAN.md`.

## Declared Driver Calls

- `URPGBossEncounter::{ResetForTest,Wake,IsDormant,IsWaking}`: `Source/OneBossFight/Player/RPGBossEncounter.h:42-79`.
- `URPGBossDormantWake::{GetStageName,IsWaking}`: `Source/OneBossFight/Player/RPGBossDormantWake.h:34-37`.
- `URPGAttackTracker::StartMove`: `Source/OneBossFight/Player/RPGAttackTracker.h:96`.
- `URPGCombatDebug::{DebugBossMontageAnimName,DebugKillBoss}`: `Source/OneBossFight/Player/RPGCombatDebug.h:70-71,64`.
- `URPGBossDeath::GetDeathStateName`: `Source/OneBossFight/Player/RPGBossDeath.h:97`.

## Validation

- Ran `python -I` AST parsing for `Scripts/Editor/pie_dormant_wake.py`: passed.
- Re-read all new call sites, the encounter state transition, tracker priority path, and interruption paths twice against their declarations.
- No C++ compilation, editor launch, PIE, package, or automation test was run by Codex. Claude must build and run `OneBossFight.Boss.DormantWakeRules` and `pie_dormant_wake.py`.
