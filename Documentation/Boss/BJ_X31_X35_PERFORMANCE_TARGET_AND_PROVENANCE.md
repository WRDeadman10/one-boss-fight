# Queue BJ Batch 7 — Performance target and provenance

Date: 2026-11-11. Documentation/source audit only; no profiler, benchmark, hardware capture, test, build, package, or Unreal operation was performed.

## BJ-X31 — Current release target

The current measured release gate is a packaged 1920×1080 full encounter including phase two, average at least 60 FPS and whole-frame p99 at most 16.67 ms on the RTX 2060 Super. 120 FPS / 8.33 ms is stretch telemetry. These terms are consistent across `PERFORMANCE_LOG.md`'s opening target and target-hardware warning, `TEST_PLAN.md` PERF-01/current status, and the owner decision recorded in `DECISIONS.md` (2026-11-05 A7 at line 1408; the older 2026-10-24 RTX 3060 proxy acceptance is explicitly superseded at line 630).

## BJ-X32 — Proxy versus target-device evidence

`PERFORMANCE_LOG.md` identifies an RTX 3060 host and labels its measurements proxy data for the RTX 2060 Super target. It records Round 4 (BUILD-222, 2026-11-05) at 27.29 FPS / 42.88 ms legacy and 27.10 FPS / 42.85 ms data, both missing the absolute gate; Round 5 (BUILD-224) records its DLSS-mode observations and also says none reached 60 FPS. `TEST_PLAN.md` contains corresponding dated entries at its Round 4/5 sections. These records do not establish target-device acceptance. The 2026-10-23 RDP run is separately marked invalid for GPU attribution in `PERFORMANCE_LOG.md`; it must not be blended with valid console captures.

## BJ-X33 — Per-run provenance limits

The retained-summary audit `PERFORMANCE_LOG_PROVENANCE_AUDIT_D145.md` inventories 59 JSON summaries: 20 legacy, 5 from r1, and 34 from r2. It reports map, build configuration, engine, and hardware fields in all 59; machine name, interactive session, and unique build ID/binary hash in 0/59. Collection-level `system_info.txt` and session context cannot be treated as per-run joins. Thus the recorded GPU model in these summaries is not enough by itself to bind a row to a particular package/source revision or interactive run. D145 also notes `RPGBenchmarkRunner.cpp:364-379` does not write those identity fields and `SummarizeBenchmark.py:44-79` neither displays nor fails on their absence.

## BJ-X34 — Candidate counters mapped to source

The existing static candidate inventory `BI_X06_X10_PERFORMANCE_CANDIDATES.md` maps counters to `ARPGFrameworkBossCharacter::Tick` (decision/selector cadence and trace counts, around `RPGFrameworkBossCharacter.cpp:445-733`), transition/event log sites in its tracking helpers, `URPGAttackTracker::TickComponent` and event-gated logs (`RPGAttackTracker.cpp:375-556`), and `FRPGBossNavigationDiagnostics::ToString` (`RPGBossNavigationDiagnostics.h:26`). A tick function or string formatter does not prove frequency, cost, or Shipping inclusion. Measure per-run selector calls/traces, site/category log events and bytes, thread inclusive/exclusive scopes, attributable allocations if reliable, and frame/game/render/GPU distributions on the same selected route and package. No numerical cost estimate is supported by this source audit.

## BJ-X35 — Disposition

No active target contradiction was found in the targeted current-state documents. Dated older decisions/results remain historical context, with the superseding target identified above. The RTX 2060 Super full-fight packaged result, same-build identity, and representative profiler counters remain open. No optimization or default change follows from this audit. Continue BJ-X36–X40 without waiting for review.
