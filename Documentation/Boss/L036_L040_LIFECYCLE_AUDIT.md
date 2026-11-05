# Queue L Batch 8 — lifecycle and recovery evidence audit

## Native automation mapping (source only)

Claude reported BUILD-212 v12 at 459/459 in C-819; Codex did not run that suite.
The following source cases map to L036–L039:

| Task | Existing automation | What it supports | What it does not support |
|---|---|---|---|
| L036 | `RPGBossStartupActivationTests.cpp`: `MalformedRecordStartupFailsClosed`, `EmptyCensusFailsClosed`, `DuplicateCensusFailsClosed`, `UnavailableEpochFailsClosed`, and injected activation failures. | Selected startup refusal states, cleanup/fallback assertions in transient worlds. | Authored G044 content, PIE refusal UX, packaged behavior. |
| L037 | `GenerationAdvancesBeyondLegacyInt32`, `ResetCountOverflowRefusesBeforeMutation`, `SelectedRebindGenerationSequenceKeepsOneLease`. | Exact generation crossing, refuse-before-mutation at reset-count exhaustion, seeded rebind sequence/one-lease invariant. | Arbitrarily long soak or packaged telemetry. |
| L038 | `SubsystemShutdownUnbindsPendingRebind`, `RepeatedSubsystemRestartPreservesPlayerSetup`. | Pending timer/delegate/binding shutdown in a transient fixture and three subsystem restart cycles. | Real game-session shutdown ordering or PIE teardown chronology. |
| L039 | `UnsafeReleaseRetainsLeaseAndBinding`. | Intentional lease/binding retention after unsafe cleanup refusal while disabling the selected boss. | Successful release/cleanup or a live PIE failure. |

## L040 — new behavior proposal

No new gameplay behavior proposal is justified by the current accepted native
automation report. The remaining known gaps are G044 content, capture bridge,
PIE, cook/package, and comparable performance evidence. If a witnessed run
reveals a specific defect, retain its evidence and route the fix through the
existing review/approval process.

No tests or builds were run and no lifecycle behavior was changed in this audit.
