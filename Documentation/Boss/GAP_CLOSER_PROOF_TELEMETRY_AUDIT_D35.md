# Gap-closer proof telemetry audit (Queue D35)

Scope: trace maintained start/step/end/refusal telemetry candidates against the gap-closer gate and optional generic warp path. Source/schema/doc review only; no validator/tests/build/Editor run.

## Candidate emitters

| Proof event | Candidate token | What it shows | What it does not prove |
|---|---|---|---|
| Generic card playback begins | `playback_start` (`RPGFrameworkMoveExecutor.cpp:173`) | encounter/generation/instance, montage path, slot, rate, label | That the card was selected by `RPGBossGapCloser::ShouldClose` or is an assigned gap-closer. |
| Warp ease activates | `warp_ease` (`:455`) | Optional ease-distance branch became active | Actual movement or gap-closer intent by itself. |
| Warp sample step | `warp_step` (`:477`) | Card-time interval, distance need/step/actual, cumulative movement and budgets | That observed displacement is authored gap-close behavior unless actor/card assignment is independently established. |
| Warp blocked | `warp_blocked` (`:474`) | A requested step was smaller than actual movement and records blocker | A range-gate refusal or complete failure classification for the gap-closer feature. |
| Warp interval summary | `warp_summary` (`:432`) | Accumulated distance/turn versus budgets when the interval ends | Card selection reason, natural end, or distinct gap-closer completion. |
| Executor cleanup | `cleanup` (`RPGFrameworkMoveExecutor.cpp:208`; reason variants elsewhere) | Executor cleanup reason/state and owned montage stop | Gap-close action end unless the caller links the instance/card to that action. |
| Pure gate decision | none | `RPGBossGapCloser::ShouldClose` has no emitter/caller (`RPGBossGapCloserRules.h:8-14`) | Start/continue/stop/refusal of an actual gap-close action cannot be evidenced from a current gate token. |

`playback_start`, `warp_ease`, `warp_step`, `warp_blocked`, `warp_summary`, and `cleanup` are generic framework proof tokens with schemas/source links in `Documentation/Boss/LOG_TOKENS.md` and the validator. They are candidates only if a future run proves the relevant actor, card, and instance. There is no dedicated `gap_close_start`, `gap_close_step`, `gap_close_end`, or `gap_close_refused` token in maintained emitters/schema/glossary.

## Expected-sheet disposition

The D32 paired arena parry sheet is unrelated and remains unchanged. For a future gap-closer proof sheet, require the pure gate inputs/result from an external test harness or add a dedicated emitter only after feature wiring is approved; then link action identity to the generic executor's instance/card. Record movement observations separately from authored expectations. Until then classify gate start/end/refusal and action assignment as **UNKNOWN / no current emitter**, not as a pass or a failure. Generic warp logs alone cannot show the unconnected `ShouldClose` behavior.
