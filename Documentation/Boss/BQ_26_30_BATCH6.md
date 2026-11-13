# BQ-26..30: Queue BQ batch 6, build HUD, flask counter, weapon slot

C (implementer), 2026-11-13. Queue: `QUEUE_BQ.md`.

**All C++ is written but NOT compiled or run.** Binary acceptance needs the Lead's C-1155 build and suite. No engine, editor, PIE, tool run, asset change or commit.

| Task | Result | Files |
|---|---|---|
| **BQ-26** G3-5 build-selector HUD indicator | **reconciled, already delivered.** `URPGBossHudWidget` draws the build line top centre (`BuildTextBlock`, `UI/RPGBossHud.cpp:107`). Its text comes from the pure truth rule `RPGBuildRules::BuildLine`: it names the weapon the player really holds, never the choice alone. Covered by `OneBossFight.Build.Rules` (7 BuildLine references in `RPGBuildTests.cpp`) and the historical `pie_build_hud.py` 8/8 run. The in-game selector `UI/RPGBuildSelect` exists too (`pie_build_select.py` 18/18). Still open: the shrine selector, which needs M-07 art (ART) | none |
| **BQ-27** G3-5 flask counter | **reconciled, already delivered.** `URPGFlaskHud` and `URPGFlaskHudWidget` (`UI/RPGFlaskHud.*`, pure rules `RPGFlaskHudRules.h`) are an overlay for the pack's HealthPotion stack. The pack widget is left untouched. It is attached to the pack player in `RPGPlayerMovesSubsystem.cpp:1055`. Test `OneBossFight.UI.FlaskFill`. The G3-5 row in TASKS.md still says "flask counter open"; that line predates this code. On-screen look and count stay ENG/owner | none |
| **BQ-28** KI-091 keep the slot out of MagicCombatStyle | **new, awaiting review.** Gap found: the default weapon slot holds the sword and the ExampleMagicStaff. If the player cycles to the staff before the boss wakes, `SyncLock` blocks `Ability.Quickslot` with the staff active, so the whole fight is locked in MagicCombatStyle. New opt-in `URPGBuildLoadout::bReturnToWeaponBeforeLock` (default **off**). When the lock is about to engage and the active item is not the weapon item, `SyncLock` asks the pack's own `Next Equip Slot Active Index` (the same call the equip path already uses) for one cycle per poll, then retries the lock. The pure seam is `RPGBuildRules::ShouldReturnToWeaponBeforeLock`. It is bounded: after `MaxAttempts` cycles (clamped to at least 1) the lock engages anyway, as before, instead of cycling for ever. The counter resets on lock and on unlock. With no explicit build nothing is locked, so that path is unchanged | `Player/RPGBuildRules.h`, `Player/RPGBuildLoadout.h/.cpp` |
| **BQ-29** source tests | **new:** `OneBossFight.Build.ReturnToWeaponBeforeLock`, 9 decision cases plus the CDO default. BQ-26 and BQ-27 are already covered by `Build.Rules` and `UI.FlaskFill`; no duplicates added | `Tests/RPGBuildReturnToWeaponTests.cpp` (new) |
| **BQ-30** | this report | |

## Gates still open

1. **The Lead's C-1155 build plus suite** for `Build.ReturnToWeaponBeforeLock`, with `Build.Rules` and `UI.FlaskFill` as regression checks.
2. **PIE (ENG):** cycle to the staff, wake the boss with the opt-in on, and check that the weapon item is active before `Ability.Quickslot` is blocked. Also check whether one cycle per poll is fast enough before the first boss swing.
3. **ART:** the shrine build selector (M-07). **Owner:** the build line and flask counter on screen.
4. **Design:** whether to turn `bReturnToWeaponBeforeLock` on. Removing the staff from the slot entirely would mean writing pack equipment state, which is out of scope.

**Earlier uncommitted edits** in `RPGBuildLoadout.h/.cpp` and `RPGBuildRules.h` were preserved; my edits were insertions only.
