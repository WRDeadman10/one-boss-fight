# Music intensity rule audit — D106

**Scope:** pure input-to-output rule, phase behavior, reset/event ownership, and tests. Static source review only; no audio assets or runtime playback inspected.

`RPGBossMusicIntensity::Evaluate` accepts a health fraction, phase integer, and optional phase-two boost. It returns zero for nonfinite/out-of-range health, any phase other than 1 or 2, or a nonfinite/out-of-range boost. Otherwise it computes `clamp(1 - HealthFraction + (Phase == 2 ? PhaseTwoBoost : 0), 0, 1)` (`RPGBossMusicIntensityRules.h:7-13`). Phase two therefore adds intensity before the final cap; at low enough health both phases can produce the same maximum.

The function is explicitly documented “Unwired by design”; it has no mutable event state, transition, track selection, volume control, or reset operation. Reset/lifecycle claims belong to a future caller, not this helper (`RPGBossMusicIntensityRules.h:4-6`).

Tests check full/zero-health phase-one values, phase-two increase at health .8, maximum clamp, a 1001-sample monotonic phase-one sweep, invalid phase, and boost above one (`RPGBossMusicIntensityRulesTests.cpp:8-13`). They do not directly check health endpoints with phase two, boost endpoints 0/1, nonfinite health/boost, nor an event/reset sequence; the last is outside this stateless helper's contract.

**Acceptance result:** pure formula, test expectations, and stateless/unwired boundary agree. Endpoint and nonfinite cases listed above remain focused test gaps. No runtime music transition or reset behavior can be inferred from this helper.
