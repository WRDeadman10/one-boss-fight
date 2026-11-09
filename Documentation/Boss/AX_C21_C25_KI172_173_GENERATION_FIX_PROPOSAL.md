# AX-C21–C25 — KI-172/173 generation-guarded callback proposal

Date: 2026-11-09. Proposal only, requested by Claude in C-1153 after the C-1152 work. No production code or KI-172/173 tests are changed by this report. Both issues remain plausible stale-state hazards; neither is claimed reproduced.

## Existing pattern to reuse

`URPGPackParryContact` reads `URPGBossEncounter::GetParticipantGeneration()`, includes that generation in attack identity, and clears observer state when the observed generation changes (`RPGPackParryContact.cpp:71-100,118-132`). The proposed guards use encounter generation as a lifecycle boundary and a separate monotonically changing request token where a callback can outlive an operation inside one encounter generation.

## KI-172 — deferred hit finalization across encounter reset

### Test-first ordering

1. Build a native fixture with `URPGHitIntake`, a native-health boss carrying `URPGBossEncounter`, and observable health/posture/bleed/broadcast state. Queue one hit while the encounter is at generation G.
2. Before the next-tick finalizer runs, reset the encounter so the participant generation becomes G+1. Advance the world one tick.
3. Assert the G record has no health, posture, bleed, hit-record, or hit-broadcast effect. Then queue a fresh G+1 hit and assert its normal positive-control effect, proving that the guard did not disable intake.
4. Add a same-generation positive control: queued hit finalizes normally without reset.

The test must establish ordering in the native world, not invoke `FinalizePending` directly. If timer ordering cannot be made deterministic in the fixture, introduce the narrowest non-shipping test seam only after confirming that the real next-tick timer remains covered by a separate integration assertion.

### Candidate fix after the regression test fails on current code

Capture the target encounter generation in each `FPending` when the hit is queued. Before consuming any `FPending` record, resolve the same target/encounter and require the captured generation to equal the current generation. A stale record must be discarded before damage or any record/posture/bleed/broadcast side effect.

Prefer an explicit reset notification that clears pending records and cancels any retained finalizer handle, plus the generation comparison as a last-line defense. Do not repurpose `ResetCounters()`; it is documented as a test-driver counter/record reset and is not called by encounter reset. If a timer handle is stored, reset/EndPlay must clear it and make rescheduling safe. Batch records only when target and generation match, preserving existing same-frame merge behavior.

### Acceptance

- Old-generation hit after reset has zero gameplay and observer side effects.
- New-generation and no-reset controls still produce exactly the established behavior.
- Reset cancellation leaves no stuck `bFinalizeScheduled` state; a later fresh hit schedules and completes.
- Existing batch deduplication/merge and native-vs-pack routing tests remain green.

## KI-173 — stale next-tick riposte start after abort/reset/rearm

### Test-first ordering

1. Enter a valid Down/stagger state and request riposte A, which queues its next-tick start callback.
2. Abort or reset the stagger before dispatch, then enter a new valid Down state and request riposte B before A's callback can run.
3. Dispatch the pending callbacks in their natural next-tick order. Assert A produces no montage, player input lock, movement change, collision change, failure cleanup, or mutation of B; assert B starts once.
4. Add an encounter-reset control and a same-generation valid request control. Verify an old encounter callback is inert even if the current clip phase is again Down.

The test should observe both player and boss montage/input/collision state. A callback that routes its stale failure through `EndRiposteExecution` is not inert: it may cancel B and must fail the test.

### Candidate fix after the regression test fails on current code

Keep a riposte request serial on `URPGBossStagger`; advance it on each new request, abort, reset, and teardown. Capture the serial and the encounter participant generation in the scheduled callback. At callback entry compare both tokens before any cleanup or state mutation. A stale callback returns without calling `EndRiposteExecution`, because the cleanup could belong to a newer request. The active matching request retains the current validity and `Phase == Down` checks.

If a retained timer handle is practical for `SetTimerForNextTick`, clear it during abort/reset/EndPlay as eager cancellation; still keep the request-token guard because callback cancellation and state reuse are distinct concerns. Do not infer that a successful `SetTimerForNextTick` implies the pair clips started.

### Acceptance

- Old request cannot start clips or change state after abort/reset/rearm.
- Old callback cannot cancel, mutate, or lock out a newer request.
- Current request starts exactly once while its request token, encounter generation, player/boss, and Down phase are current.
- Abort/reset with no newer request remains safe; existing riposte and stagger lifecycle tests remain green.

## Scope and gate

This proposal does not authorize a production change by itself. First add/run the ordering tests against current code and retain the failing evidence; then implement only the smallest guard that makes those tests pass. Preserve exact generation source and reset ordering in test evidence. Update KI-172/KI-173 statuses only after the regression tests and full native suite run. No editor asset, Blueprint, or runtime-content change is proposed.

## Source basis

- `Source/OneBossFight/Player/RPGHitIntake.h:155-166` — pending record fields currently omit generation.
- `Source/OneBossFight/Player/RPGHitIntake.cpp:471-478,509-518,522-527` — queue scheduling and deferred batch consumption.
- `Source/OneBossFight/Player/RPGBossEncounter.cpp:347-365` — reset advances participant generation and aborts stagger; no intake reset call found in the audited path.
- `Source/OneBossFight/Player/RPGBossStagger.cpp:567-584,825-840` and `RPGBossStagger.h:244,250,287` — next-tick callback and abort state.
- `Source/OneBossFight/Player/RPGPackParryContact.cpp:71-100,118-132` — existing participant-generation identity/reset pattern.

