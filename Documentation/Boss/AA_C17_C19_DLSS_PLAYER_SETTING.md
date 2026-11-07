# AA-C17–AA-C19 — DLSS player setting design and acceptance

## AA-C17 — Settings menu hook (design only)

Place the option in **Options → Graphics → Upscaling** as a single-choice control:

- **Off (TSR)** — current default and fallback.
- **DLAA**, **DLSS Quality**, **DLSS Balanced**, **DLSS Performance** — available only when the DLSS plugin reports the requested mode supported.

The widget reads `URPGDLSSGameUserSettings::GetDLSSPlayerMode()` and applies a selection through `SetDLSSPlayerMode()`. That setter applies the mode and saves `GameUserSettings.ini`. When hardware or driver support is absent, retain the user's saved selection but show that TSR is active. No UI assets were edited.

## AA-C18 — Non-NVIDIA / unsupported fallback test

**Automated coverage:** `RPGDLSSPlayerSettingsRulesTests.cpp` covers every selectable DLSS mode resolving to TSR when support is false. `Scripts/Tools/test_dlss_player_settings_contract.py` checks registration, the support guard, and the TSR fallback path; the focused Python contract test passed 3/3.

**Device acceptance still required:** on a non-NVIDIA or otherwise unsupported Win64 device, set a DLSS mode, restart, confirm the preference remains saved, confirm the active view reports TSR, and verify no DLSS error blocks play. This machine-level check was not run here.

## AA-C19 — Shipping behavior (test plan)

The project registers `URPGDLSSGameUserSettings` through `GameUserSettingsClassName`. The preference is a `Config` property stored by `SaveSettings()` in the user's game settings ini; application uses the DLSS Blueprint library and a game-setting CVar write for the TSR fallback. No console command is used. The default enum is Off (TSR), so a new profile preserves today's renderer behavior.

Lead Shipping acceptance: select each supported mode through the settings API/UI, restart and verify persistence; on unsupported hardware verify TSR fallback; inspect packaged logs to confirm the chosen active upscaler; confirm no console is needed. UI wiring and packaged verification remain open. This Codex change has only focused static contract coverage, not a UE build or Shipping run.
