# C-1157 — KI-172/173 reset-order regressions and generation guards

Date: 2026-11-09. Status: local implementation complete; Lead acceptance build/review pending. No commit or push.

## Red evidence against the pre-fix code

`targeted_red_final.log` records both requested orderings failing on the original implementation:

- KI-172: the no-reset next-tick control records and broadcasts once. A second hit queued before `ResetForTest()` then finalized after reset; hit/broadcast totals advanced to 2 instead of remaining at 1. A fresh-generation control also finalized, showing the intake path remained active.
- KI-173: request A was accepted, encounter reset advanced generation, and request B was accepted before the queued callbacks ran. The test-only dispatch witness counted 2 starts instead of the expected 1.

The first KI-172 draft had a transient-world timer-pumping issue. The final regression keeps the real `SetTimerForNextTick` no-reset positive control and directly invokes the private finalizer for the reset ordering, so the reset-before-finalize condition is deterministic. `targeted_red_retry.log` is retained as an invalid fixture iteration; it is not the red evidence used for the finding.

## Guards added

- Each `URPGHitIntake::FPending` captures the target encounter and participant generation. Finalization drops records whose encounter is gone or generation changed.
- `URPGHitIntake` binds to the encounter reset broadcast, removes that encounter's queued records, cancels its pending finalizer when the queue is empty, and unbinds/cancels on EndPlay. The generation check remains the final guard if reset notification is missed.
- `URPGBossStagger` retains the next-tick timer and captures a request serial plus encounter generation. Abort, reset/end of stagger, and teardown invalidate/cancel the request. The callback checks both identities before any cleanup, so an old callback cannot affect a newer request.

## Green verification

- Development editor build succeeded: `build_after_guards.log` (UE 5.5.4; 39 actions).
- Focused automation succeeded: `targeted_green.log`, both KI tests passed, editor command exit 0.
- Full native automation succeeded: `full_suite_with_manifest.log`, 494 finished / 494 passed / 0 failed, terminal marker `TEST COMPLETE. EXIT CODE: 0`.
- The full-suite run supplied the operator-pinned `DD27jManifestHash` from `DD27j/run_C339/EmberWarden_PhaseTwo_fields_manifest.json`; path and SHA-256 are recorded in `dd27j_manifest_hash_source.txt`. The earlier `full_suite.log` omitted that required argument and failed only `SavedProductionPreflight`; it is retained as an invalid invocation, not the final suite result.
- Lock used: `ENGINE_LOCK.json`, owner X. Builds/suites only; no PIE, capture, or editor launch.

## Gate

Both regressions now pass and the full suite is green locally. Claude/Antigravity review and the Lead acceptance build remain pending. KI-172/173 are therefore locally fixed, not Lead-accepted or committed.
