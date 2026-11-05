# Queue J J036–J040 — selected-route cost evidence

## J036 authored timing markers

`URPGPlayerMovesSubsystem` emits `[EncounterTiming]` begin/end rows for selected startup, broadcast-driven rebind, rebind timeout/refusal, and activation release paths (startup refusal, rebind, refusal cleanup, and subsystem shutdown). Each row carries a per-world monotonically increasing operation ID, world ID, operation name, monotonic `FPlatformTime::Seconds()` timestamp, elapsed milliseconds on end, and outcome. End rows are scope-guarded for startup/rebind/refusal returns. These markers are source-authored and unbuilt; no timing measurement is claimed.

## J037–J039 sample and compare gates

No cold/warm selected-route samples exist. A valid capture must retain each sample's distinct run/sample IDs, cold/warm phase, build ID, binary/content SHA-256, raw log path and raw-log SHA-256. `Scripts/Tools/summarize_encounter_cost.py` already reports nearest-rank p50/p95/p99 separately for cold and warm, and returns INCONCLUSIVE for missing or mixed build/binary/content evidence. Its offline fixtures are authored from Queue I but remain unrun by Codex in this cycle.

J039 cannot compare selected timing/memory with a packaged baseline yet: no selected-route package, agreed matching hardware/resolution/sample method, baseline receipt or memory sample set is available. The new startup/rebind/release CPU markers do not prove memory cost.

## J040 owner decision

No numeric budget is proposed here. A budget or explicit no-budget disposition requires owner review after comparable packaged samples exist. Until that decision, performance risk stays open and these source markers are measurement instrumentation only.
