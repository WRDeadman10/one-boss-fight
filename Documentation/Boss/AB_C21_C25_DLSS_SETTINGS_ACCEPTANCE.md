# AB-C21–C25 — DLSS settings and player acceptance

Date: 2026-11-07. Source/offline review only. The owner parked Round 6; no shipped mode/default is chosen here.

## C21 — persistence and migration

`URPGDLSSGameUserSettings` is registered by `GameUserSettingsClassName`. `DLSSPlayerMode` is a `Config` enum with an Off/TSR C++ default; setter applies and calls `SaveSettings()`, while `ApplySettings()` reapplies after base settings. Existing unrelated base `UGameUserSettings` values should continue through the class swap, but no archived user INI migration test is present. The implementation has no explicit config-version migration. Invalid/unrecognized serialized enum handling needs an engine-level readback test before any compatibility promise; static mapping helpers default unknown enum values to Off/TSR.

## C22 — unsupported hardware

The setting checks both DLSS overall support and requested-mode support. The pure native rules map Off or unsupported requests to TSR; supported DLAA/Quality/Balanced/Performance map through. Unsupported preferences are intentionally kept in `DLSSPlayerMode` so they can reapply on supported hardware. Added an offline source contract that rejects overwriting that preference in the fallback branch; native rules cases still require Lead automation/build. This does not simulate NVIDIA/non-NVIDIA hardware.

## C23 — apply semantics

`SetDLSSPlayerMode` applies immediately, then saves; there is no pending-selection, Apply, Cancel, or rollback state in this class. Superclass `ApplySettings` also reapplies the mode. UI must therefore present the control as immediate apply or add a separate draft/rollback layer before claiming Apply/Cancel behavior. Driver/plugin visual changes, resolution scale, and restart needs are not proven by source inspection.

## C24 — keyboard/controller parity

No graphics settings screen/widget was found in the current project assets/code. Combat Enhanced Input mappings do not prove navigation parity for a future menu. Acceptance for that future UI: the same single-choice value can be read, focused, changed, and announced using keyboard and gamepad; verify keyboard arrows/Enter and D-pad/confirm, focus retention, and descriptive TSR fallback text. There is no implemented UI or input binding to claim as passing today.

## C25 — plain-language hand sheet

1. Open Options → Graphics → Upscaling.
2. Choose Off (uses TSR), DLAA, Quality, Balanced, or Performance.
3. The game applies and saves the choice right away. Restart if the tested build or graphics driver requires it; this has not yet been measured.
4. On a PC without supported NVIDIA DLSS, the game uses TSR and keeps the saved choice so it can work later on supported hardware.
5. Record build ID, GPU/driver, selected value, displayed value, and whether TSR or DLSS actually ran. Do not treat a selected label alone as proof.

## Validation

`python -m unittest Scripts.Tools.test_dlss_player_settings_contract -q` checks source contracts; `RPGDLSSPlayerSettingsRulesTests.cpp` contains native mode mapping coverage. Neither proves a packaged settings menu exists or that a specific GPU/driver applies the requested mode. No benchmark or hardware run was performed; Round 6 remains parked.
