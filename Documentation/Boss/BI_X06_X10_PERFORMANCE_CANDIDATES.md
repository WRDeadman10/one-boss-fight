# Queue BI — X06–X10: Source Performance Candidates and Measurement Boundary

Status: **offline source/documentation audit complete**. No optimization, benchmark, profiler, Unreal/Editor, build, package, or test run was performed. Findings below identify measurement candidates; source inspection does not establish runtime cost or Shipping inclusion.

## X06 — Call-path and allocation candidates

| Site | Static observation | Classification |
|---|---|---|
| `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp`, `ARPGFrameworkBossCharacter::Tick` (around lines 445–733) | Once the fixture reaches the arrived/neutral decision path, it builds a decision snapshot, calls the selector, iterates `Decision.Traces`, and emits formatted `LogTemp` messages for eligible/refused cards and active behavior patterns. Neutral strafe explicitly re-decides on tick. | Highest-priority profiling candidate if this framework proof actor is exercised in the measured route. Cadence and Shipping/runtime presence are unverified. |
| Same file, `TickLos`, `TickActivity`, `TickDodge`, and `TickFlask` (around lines 327–443) | Tracking helpers perform state reads each tick; their visible logs are tied to transitions or discrete events. | Audit CPU samples for helper cost; no repeated per-frame logging claim. |
| `Source/OneBossFight/Player/RPGAttackTracker.cpp`, `URPGAttackTracker::TickComponent` (around lines 375–556) | Tick path observes montage/phase/timing and emits logs on move start/end, active-window changes, vetoes, and branch decisions. | Event-gated formatting candidate; do not infer one log per frame from the tick function alone. |
| `Source/OneBossFight/Boss/RPGBossNavigationDiagnostics.h`, `ToString` | Builds a formatted diagnostic string containing route/generation/request/result/actor/goal/range fields. | Call-site frequency and allocation cost must be measured; helper definition alone does not show it is hot. |

The working tree contains active edits in several of these source files. This batch made no source changes. No candidate is recommended for optimization before representative packaged measurements.

## X07 — Diagnostics and Shipping boundary

The inspected framework decision path uses `UE_LOG(LogTemp, Display, ...)` at the decision/refusal/candidate sites and formats names/reasons/ranges for trace rows. Several `RPGFrameworkBossCharacter.cpp` logs are ordinary source statements rather than locally guarded by `#if !UE_BUILD_SHIPPING`; the class's inclusion/use in the shipped target and any compile-time/log-category filtering were not established here. `RPGAttackTracker.cpp` uses a static `LogRPGAttack` category, but category declaration does not prove what the Shipping binary retains or how frequently enabled logs execute. The existing Shipping reflection/CVar checks do not establish log stripping. A Shipping binary or authoritative target configuration check is required before making that claim.

## X08 — Minimal measurement counters for a Lead-owned run

Record per representative full-fight run, with the same build/map/route/device identity as the benchmark receipt:

1. Boss decision ticks and selector calls, split by phase and neutral-strafe state.
2. Candidate traces evaluated per selector call and eligible/refused counts.
3. `LogTemp`/`LogRPGAttack` events by site/category and bytes emitted; preserve normal benchmark logging configuration.
4. Game-thread inclusive/exclusive time for decision selection, tracker tick, navigation diagnostics formatting, and logging.
5. Allocation counts/bytes attributable to those scopes, if the chosen Unreal profiler can attribute them reliably.

Pair these with total frame, game-thread, render-thread, and GPU frame-time distributions. Compare repeated baseline and candidate runs on the same selected route and machine. Do not disable diagnostics in only one arm or use Development data as a packaged Shipping result.

## X09 — Target wording reconciliation

The current performance target is a packaged 1920×1080 full encounter, average at least 60 FPS and p99 frame time at most 16.67 ms; RTX 2060 Super is the target device. 120 FPS / 8.33 ms is stretch telemetry only. `Documentation/PERFORMANCE_LOG.md` states this at its opening target block and repeats that RTX 3060 figures are proxy data. `Documentation/TEST_PLAN.md` records the same target and labels RTX 3060 as proxy. `Documentation/DECISIONS.md` has the owner decision; no contradictory active target was identified in the targeted current-state docs reviewed. Historical round data and older snapshots must retain their date/context and must not be promoted to target-hardware acceptance.

## X10 — Batch disposition and limits

The source points to instrumentation candidates, not proven bottlenecks. The framework fixture's selector/log path is the clearest conditional candidate; attack-tracker output is transition-oriented from static inspection. No call counts, allocation counts, frame costs, Shipping retention, or 2060 Super result were measured. Next evidence step belongs to the authorized Lead benchmark/profiler workflow using a stable packaged build and immutable run identity; no default, logging level, runtime behavior, or owner decision changes follow from this audit.
