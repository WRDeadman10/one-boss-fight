# F2 selector/executor pure model — C373/C374

SOURCE STAGING ONLY, three absent destinations: Player/RPGBossMoveModel.h/.cpp; Tests/RPGBossMoveModelTests.cpp. All live222 Source hashes match accepted F1. No promotion, build, engine, Content, Config, map or git operation. Own production header FIRST in both cpp. pins.json, three from-absent diffs, full222 baseline and STATIC_CHECKS.json supplied.

FDecisionSnapshot holds explicit encounter/target IDs, target-valid/neutral flags, phase, generation, frame, wall clock, range and signed yaw. One compiled metadata card is the sole candidate. Filters reject missing/invalid card, wrong identity/generation, invalid target, nonneutral/busy state, nonfinite/negative inputs, wrong phase, out-of-range and full-cone-width/2 signed-yaw exclusion. Range/cone boundaries inclusive. No weights, RNG, default candidate, actor discovery or forced selection.

A noncopyable value-model owns one attack. Explicit Initialize once; no silent reset. Start allocates a monotonic uint64 instance bound to encounter+generation, refuses counter overflow and clears stale caller output. Last accepted frame survives abort/reset, so same-frame or older-frame restart is refused even after instant abort/finish. Monotonic wall clock and authored play rate advance montage-local seconds; a paused tick consumes elapsed wall time without local advancement, avoiding catch-up when resumed. HeadingCommitted is a pure predicate at the authored commit time. It does not rotate or capture an actor transform.

State: Idle -> Committed -> Active -> Recovery -> Idle. Begin opens a zero-local-time window exactly once where authored. Advance emits window Open/Close at authored local timestamps even if a long frame crosses both boundaries. Touching windows close the earlier before opening the next. Recovery and Finished edges follow window closes; a large step can traverse several states and finish Idle. This is an ordered proposal stream, NOT a real sweep/hit or pose proof. Future executor must handle the geometry over crossed intervals, not merely damage immediately on receipt of an Open event.

Abort closes currently open windows, signals Aborted once, releases card and becomes Idle. Repeat abort on same current/finished token emits nothing. Generation change must strictly increase, aborts first, preserves instance counter and frame history; old tokens cannot mutate newer work. Invalid/reversed/overflowing clock on CURRENT token aborts fail-closed. Stale callbacks produce named refusal and zero events without disturbing current work. Events and errors clear before each operation.

Five automation sources UNRUN:
- Eligibility: target/encounter/generation/state/phase/range/cone/domain filters and inclusive boundaries.
- Crossing: whole-window skip, exact timestamps/order/tokens; multiple step sizes at0.5/1/2/3 playrates; zero-start window.
- PauseAndBoundaries: commit, active/recovery/end boundaries, pause/resume, same-clock no duplicate.
- Abort: Committed/Active/Recovery/Idle idempotence, active closes before abort, clock reversal fails closed.
- GenerationAndDoubleStart: same-frame and busy refusal, monotonic IDs across resets, delayed callback/abort isolation.

Assumptions/limits requiring review: caller supplies truthful stable identity/phase/target flags, monotonic frame IDs and one model per encounter authority (tokens are unique within that instance, NOT globally allocated). Model IDs do not prove UObject/world/actor lifetime. Target changes/death/lifecycle events must call Abort through a future reviewed runtime adapter. No hit resolution/dedupe, movement, health authority, montage, callbacks/timers, animation load or asset mutation here. Metadata-only compiled cards deliberately usable for this pure model; future playback must still demand HasResolvedAssets and actual slot/pose proof. Full clock has no authored1e6 ceiling (uptime), but finite/nonnegative and monotonic; authored card domains remain F1's1e6. F3 proof-map approval C372 read; no map work before F1/F2 gates.

C374 warning baseline recorded separately in Framework/Regression/run_C373/C374_ACCEPTED_BASELINE.json: normalize every LogCore Warning UTS line to UTS-launcher with exact count; preserve historical raw difference and all other warning checks. Fullsuite187 accepted by lead, not rerun here.
