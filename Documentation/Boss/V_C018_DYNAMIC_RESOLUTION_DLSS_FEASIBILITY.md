# V-C018 — UE 5.5.4 Dynamic Resolution with DLSS feasibility

## Feasibility

The installed UE 5.5.4 and DLSS 8.9.0 source expose the necessary resolution-fraction concepts: `IDynamicResolutionState` reports approximation and upper-bound fraction maps (`Engine/Source/Runtime/Engine/Public/DynamicResolutionState.h`), the view family supplies a screen-percentage interface, and the DLSS plugin exposes optimal/min/max resolution fractions per quality mode (`Engine/Plugins/Marketplace/DLSS/Source/DLSS/Public/DLSSUpscaler.h`). This is evidence of API-level compatibility, not proof the current project config enables a working dynamic-resolution path with DLSS.

UE's `r.DynamicRes.OperationMode` is declared with default 0 (disabled) in `Engine/Source/Runtime/Engine/Private/UnrealEngine.cpp:487-490`; the engine branches distinguish enabled/disabled state at lines 13621-13632. Round 6 must keep it 0 because P2a records a primary fraction upper bound and the experiment requires a stable requested fraction.

## Safe feasibility test (proposal)

1. First finish the fixed-fraction Round 6 mode and owner image-quality review. Keep all shipped settings unchanged.
2. On an isolated Development build, validate the exact UE 5.5.4 CVars and the DLSS mode's supported min/max fraction through runtime help/API readback. Choose one explicit min/max range only after inspecting project/platform constraints; do not guess.
3. Add no project default or player setting for this test. In one opt-in Development run, enable dynamic resolution at a conservative fixed GPU budget, log the active upscaler, operation mode, per-frame primary fraction and frame times, then verify the fraction moves within the configured bounds under controlled GPU load.
4. Check for DLSS mode switching, abrupt quality transitions, oscillation, frame-pacing regressions, unsupported GPU/plugin fallback, and stable TSR fallback. Compare with a matched fixed-resolution run on the same GPU/driver/session.
5. Disable the feature after the test. Integration is a separate decision requiring stable measurements and owner image-quality acceptance.

Unknowns: whether the current project has a DynamicResolutionState implementation active, how its target GPU timing budget interacts with DLSS, actual RTX 2060 Super behavior, and packaged/Shipping fallback. No test, runtime control, or project setting is changed here.
