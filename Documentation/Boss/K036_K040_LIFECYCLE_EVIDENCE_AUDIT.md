# Queue K K036–K040 — native lifecycle evidence scope

## K036 — selected startup refusal cleanup

The current native suite has explicit cases for malformed selection, empty/duplicate census, undefined phase, unresolved definitions, unavailable catalog epoch and activation/compiler failure. Relevant test names in `RPGBossStartupActivationTests.cpp` include `MalformedRecordStartupFailsClosed`, `EmptyCensus`, `DuplicateCensus`, `BuildsOnlyMatchingPhase`, `UnavailableEpochFailsClosed`, plus `RPGBossActivationTests.cpp` `Activation.InjectedFaults`. Claude reports the full BUILD-212 v12 suite at 459/459 (C-819). These are native automation observations; they do not prove a content-authored startup or PIE result.

## K037 — generation and overflow

`GenerationAdvancesBeyondLegacyInt32`, `ResetCountOverflowRefusesBeforeMutation`, and `SelectedRebindGenerationSequenceKeepsOneLease` cover crossing the legacy int32 boundary, reset-count refusal before mutation, and the seeded selected rebind sequence with one retained lease. C-819 accepts the 459/459 native suite. This does not establish arbitrarily long soak behavior or packaged telemetry.

## K038 — shutdown and repeated lifecycle

`SubsystemShutdownUnbindsPendingRebind` covers delegate/timer/binding teardown during a pending rebind. `RepeatedSubsystemRestartPreservesPlayerSetup` performs three transient subsystem cycles and checks independent player setup preservation. These are transient native fixtures; no game-session shutdown or PIE teardown chronology is claimed.

## K039 — unsafe release retention

`UnsafeReleaseRetainsLeaseAndBinding` uses the test-only refusal seam to assert the existing lease/binding remains retained while the selected boss is disabled. Retention is deliberate fail-closed diagnostic state, not successful cleanup. No live cleanup refusal has been witnessed in PIE.

## K040 — no new behavior proposal now

Current residuals are missing content, trusted capture, PIE, cook/package and performance evidence; this audit found no additional specific runtime behavior defect to propose from the accepted native suite. Do not add a new behavior change now. If a real PIE/package result exposes a defect, report its evidence and get the required decision before changing gameplay behavior.

No test was run in this audit. Native 459/459 is Claude's reported C-819 result; Codex performed source/test-scope review only.
