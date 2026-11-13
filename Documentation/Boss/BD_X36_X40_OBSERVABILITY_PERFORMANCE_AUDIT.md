# Queue BD X36–X40 — Observability and Performance Evidence

**Scope:** source/log/driver audit and a proposed Lead-owned profiling receipt schema. No profiling, benchmark, Unreal, package, editor, build, PIE, or test was run.

## BD-X36 — combat log and allocation candidates

Source candidates for later profiling, not measured costs:

- `RPGDamageResolver.cpp:39,101–104,217–229` formats string keys from `MoveId` / hit key / outcome and formats a human-readable history row; event logging also converts `FName`s and may format a reason string.
- `RPGFrameworkMoveExecutor.cpp:195,218,276,305–410` emits watchdog/card/playback/hit/sweep/area-effect telemetry. `ToString()` and socket `ToString()` appear on several proof/diagnostic paths. The volume depends on event frequency and enabled route; source alone does not establish frame cost.
- `RPGFrameworkProofFixture.cpp:60–109` logs initialization, nav readiness, and reset state. These are lifecycle events rather than per-frame logs.

No allocation or performance conclusion is drawn. Capture call counts, allocation counts/bytes, and sampled CPU time in the same measured configuration before proposing a change.

## BD-X37 — per-card versus lifetime deltas

`RPGFrameworkMoveExecutor.cpp:134` snapshots hit and damage totals at card start; line 218 computes `cardHitsAccepted` / `cardAppliedDamage` as deltas and emits them beside `totalHitsAccepted` / `totalAppliedDamage`. The counters are intentionally different scopes. The C-1262a receipt checks S4's per-card zero delta separately from accumulated total damage, preventing S3's hit from being attributed to S4. This is source semantics plus documented run evidence, not a fresh runtime check.

## BD-X38 — watchdog outcome observability

The executor emits `watchdog_timeout` at `RPGFrameworkMoveExecutor.cpp:193–195`, then its model-abort path emits card-abort and cleanup reasons. The C-1262a runner requires four expected card starts, four `reason=Finished` card ends, a final driver-complete marker, S4 zero delta, Whiff→S5 combo markers, four bright shots, and no target-health abort.

The generated `pie_live_status.txt` does not report a per-card terminal-reason table or explicit watchdog/abort counts. The current completion criteria fail if an expected Finished row is missing, but the receipt has limited diagnostics when a run fails. Proposed schema below adds terminal reason/counts without treating missing data as success.

## BD-X39 — target reconciliation

The current release target remains packaged 1920x1080, average >=60 FPS and p99 <=16.67 ms on RTX 2060 Super (`AGENTS.md`, `Documentation/PERFORMANCE_LOG.md`, `Documentation/GATE4_RUNBOOK.md`). DECISIONS.md's 2026-10-24 entry saying RTX 3060 could replace the target is now explicitly labeled historical and superseded for final selected-route acceptance by the owner's 2026-11-05 decision requiring performance on RTX 2060 Super. Valid RTX 3060 console runs remain proxy evidence. The latest valid Round 6 Phase 1 proxy modes all missed the absolute target; Phase 2 is recorded parked/not run in `PERFORMANCE_LOG.md`.

## BD-X40 — proposed Lead performance receipt schema

One immutable receipt per measured run, plus a parent comparison manifest:

| Field group | Required values |
|---|---|
| Run identity | unique run ID, UTC start/end, runner and revision, task/approval reference, raw-log/receipt SHA-256 |
| Build/package | configuration, build ID, source commit/tree identity, packaged binary hash, cook/package manifest hash, engine version |
| Scenario | map package, encounter route and route witness, full-fight/empty mode, phase, exact launch cvars, resolution/window mode, VSync and dynamic-resolution settings |
| Hardware/session | GPU model/device identity and driver, CPU, RAM, OS, monitor mode, active Windows session type (`console`), and whether target or proxy hardware |
| Capture method | runner/script version and hash, warmup seconds/frames, measured seconds/frame count, frame CSV and summary JSON paths/hashes |
| Results | average FPS, p95/p99/max frame time, game/render/GPU p99, frames above 16.67 ms, fight_started, terminal outcome, validity verdict and reason |
| Comparison set | baseline/variant ID, same-hardware/config checks, run inclusion/exclusion reason, aggregate method and per-run raw receipt references |

The Lead owns collection and acceptance. The schema records evidence identity and context; it does not itself establish a passing result or permit a proxy to replace target hardware.

## Verification and handoff

- Source and document review only; no profiling/benchmark/test/engine operation.
- `python Scripts/Tools/check_doc_links.py` and scoped `git diff --check` are run after final status sync; results are in the mailbox handoff.
