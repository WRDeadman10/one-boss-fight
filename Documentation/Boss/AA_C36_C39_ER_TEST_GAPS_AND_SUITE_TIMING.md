# AA-C36–AA-C39 — ER test gaps, deprecation, and offline suite timing

Static audit, test additions, one API modernization, and measured offline-suite run, 2026-11-07. No Unreal Editor or UE build was run by Codex.

## AA-C36 — round-three test-gap audit

| Surface | Existing coverage before this batch | Gap and disposition |
|---|---|---|
| `bDoubleTapLongRoll` | `RPGAutomationTests.cpp` checks false by default; C-945 `pie4` observes no long roll on standing double tap. | Default has coverage. Accepted double-tap behavior with an imported backstep remains Lead PIE work; no long-roll enable case is added because the owner chose it off. |
| Backstep selection | `RPGDodgeInputRulesTests.cpp` covers directed roll, standing backstep when available, empty-clip fallback, and repeated choices. | The component's actual soft montage default was not asserted. Added an automation assertion that it is empty. ER-A1 remains rejected for R4, so no live clip test. |
| Guard-counter clip | `RPGGuardCounterRulesTests.cpp` covers pure timing/posture rules; C08 contract tests guard source wiring. | The optional component field's empty default had no native assertion. Added one. ER-A4 is accepted for import; Lead owns import/build/PIE. |
| R1/R2 actions | Native wiring test loaded `IMC_EldenRing`; C-945 `pie4` proved light/strong/charged control behavior. | The two project tap action assets were not individually loaded by native coverage. Added asset-load assertions for the R1 light and R2 tap actions. The R2 charged action is mapped directly by the context asset and remains covered by C-945 PIE. |
| Air attacks | Source wiring/readiness docs only; ER-A2/A3 clips rejected by C-968. | No montage-specific assertion is justified until R4 assets pass owner review and Lead imports them. |

## AA-C37 — top-gap native assertions

Extended the existing `OneBossFight.Content.PackWiring` automation with four checks: ER light action load, ER heavy-tap action load, empty optional BackstepMontage default, and empty optional GuardCounterMontage default. This is a source change; Claude must compile and run the native suite. Codex did not build Unreal.

## AA-C38 — UE 5.5 deprecation review

The retained historical `F6/build1_raw.log` reports direct `UProgressBar::WidgetStyle` access as deprecated, and that access remained at `RPGBossHud.cpp`'s `AddBar`. Replaced it with `GetWidgetStyle()` copy, mutation, and `SetWidgetStyle()`. Verified those APIs exist in the local UE 5.5 `ProgressBar.h` (getter line 72, setter line 75). The older `UUserWidget::bIsFocusable` warning no longer has a source occurrence. BUILD-241/242 logs contain no C4996 warning, but are incremental and do not compile `RPGBossHud.cpp`; Lead compile confirmation is pending. Latest logs still show only the UnrealClaude/Niagara plugin dependency and non-preferred Visual Studio toolchain warnings.

## AA-C39 — offline suite timing guard

Added `Scripts/Tools/run_offline_suite_timed.py` with a default 10.0 s budget and wired `Scripts/Gate.ps1` to use it for the offline step. Added an offline contract assertion for the wrapper. Measured with the wrapper on 2026-11-07: 401 tests, 1 skipped; unittest runtime 5.840 s; wrapper elapsed 6.187 s / 10.000 s; PASS. This measures local suite wall time only and does not assert Editor/build duration.

**C-978 correction:** Claude reported a later run at 9.2 s during a build, too close to the 10 s ceiling. `run_offline_suite_timed.py` now defaults to a 20.0 s budget and its source-contract fixture expects 20.0. This is a scheduling budget, not permission to trim tests; no suite timing is claimed from this source edit.
