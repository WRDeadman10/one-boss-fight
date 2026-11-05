# Queue X X-C031–X-C034 — combat timing evidence audit

Date: 2026-11-06. Read-only evidence intake and source/instrumentation review. No Editor, PIE, build, game, package, or asset operation was run.

## X-C031 — six input-to-montage latency sessions

**WAITING ON LEAD/owner for runtime evidence.** The six requested sessions are Legacy and selected-data routes at 30, 60, and 120 FPS. No six-session output/log set was present in `Saved/bench_return` or named in the mailbox tail. Existing R1/R2/R4/R5 benchmark returns are unrelated and were not used as latency evidence. The run sheet requires per-sample route, requested cap, measured `tick_s`, action, baseline/observed montage, `observed_ms`, log path/hash, and a corroborated route-selection line (`W_C036_C039_FEEL_MEASUREMENT_SHEETS.md`, W-C036). No route/FPS comparison or average is supportable yet.

## X-C032 — montage observation delay versus game-tick cadence

The driver `Scripts/Editor/pie_input_montage_latency.py` samples montage state from a Slate post-tick callback (`:34-41, 54-55, 106-125`). It sets `press_real` while arming, injects the action on a later callback, then records the first sampled montage change. Each sample writes the current callback `dt` as `tick_s` (`:110-125`). Thus `observed_ms` includes at least the arm-to-first-injection callback gap, input injection/simulation timing, and polling until the first observed montage change; it is not pure input latency. If the transition falls between observations, polling quantization is bounded approximately by one observed callback interval, whose per-sample value is `tick_s`; the additional arm-to-injection interval also needs the preceding cadence sample, which the current record does not save. At nominal 30/60/120 Hz, one frame is approximately 33.3/16.7/8.3 ms, respectively, but these are requested-rate illustrations only—not measurements. No raw latency log was available to compute actual cadence or quantify actual delay. **Instrumentation limitation confirmed; empirical quantification remains WAITING ON LEAD/owner.**

## X-C033 — paired A1–A6 telegraph captures

**WAITING ON LEAD/owner for synchronized response captures.** Correction after broader Docs search: historical paired driver receipts exist under `Docs/BossCombatReview/Execution/Claude/B_C835_PARITY/`. BUILD-220 `pie_telegraph` pairs exercise A1, A1b, A2, and A3a timing/rate checks but their parity reports have observable mismatches; BUILD-221 A4 `t1b` is a passing automation pair; A5 heal-punish pairs show observable mismatches; BUILD-220/231 Legend pairs include A6-related checks. These are historical test logs, not synchronized tell/input/contact video or reaction-window measurements. A3b has no paired trial receipt identified. Configured tracker/Freeze timings remain targets; no player reaction or readability claim is inferred. Full coverage distinction: `Y006_Y009_LATENCY_TELEGRAPH_INTAKE.md`.

## X-C034 — hit-stop, shake, and audio source/capture reconciliation

Correction after intake of Lead BUILD-231 `pie_legend_t2` pair: both routes report 25/25 checks and the comparator reports MATCH with zero issues. Raw logs include A2/A6/roar shake behavior checks, L4 measured riposte hit-stop durations, L8 perfect-parry slow-motion and gate-off control, and L6 restoration. Exact per-check values and limits are in `Y011_Y014_HIT_FEEDBACK_RUNTIME_RECONCILIATION.md`. Active serialized Blueprint shake properties, per-hit audio playback, and audio/video capture are still unverified; the M0 check only confirms Phase 2 track import/assignment.

## X-C035 — batch receipt

No reaction-time, responsiveness, readability, or feel claim is made from configured timing or source alone. X-C031 and X-C033 remain evidence-gated; X-C032 polling analysis is instrumentation-only pending raw latency sessions. X-C034 now has historical BUILD-231 instrumented shake/hit-stop/parry runtime evidence, but serialized Blueprint values and event-linked audio remain unknown. No gameplay/source change was made.
