# BQ-61..65: Queue BQ batch 13, QUEUE_50 / QUEUE_200 Q21–Q30 build-and-suite checklists

C (implementer), 2026-11-13. Queue: `QUEUE_BQ.md`.

**The C++ is written but NOT compiled or run.** The checklists are for the Lead's C-1155 build and suite. Every test name below was confirmed by grep to be registered in `Source/OneBossFight/Tests`.

## BQ-61: QUEUE_200 Q21–Q25 (fatigue and fair telegraph, Codex 2026-11-03)

These are still open in TASKS ("Awaiting Claude build/suite review").
- **Source:** `RPGBossFatigueRules.h` (`RateScale`); profile validation at `RPGBossFrameworkProfile.cpp:172-174`; the executor composes fatigue **before** the fair-telegraph slowdown (`RPGFrameworkMoveExecutor.cpp:165-178`).
- **Suite filter:**
  - `OneBossFight.Framework.Fatigue` (Rules, Guards, ExactRuleBoundaries, MaximumWhiffCount)
  - `OneBossFight.Framework.Runtime.FatigueProfile`
  - **new** `OneBossFight.Framework.Runtime.FatigueProfileBoundaries` (BQ-64)
  - the rate-composition case in `RPGBossTelegraphScaleRulesTests.cpp`
- **Accept when:** all pass, and the live `[FrameworkProof] fatigue whiffs=... scale=...` and `telegraph_scale` lines appear only on a profile with fatigue enabled (ENG).

## BQ-62: QUEUE_200 Q26–Q30 (stamina refund, tag cleanup retries, Codex 2026-11-03)

Also still open in TASKS.
- **Suite filter:**
  - `OneBossFight.Framework.ParryCost` (Rules, including the `ParryRefund` cap, half-cost and NaN cases; Guards)
  - `OneBossFight.Player.OwnedTagCleanup` (RetryPolicy, GenerationFence, PriorGenerationCannotRemoveCurrentTag)
  - `OneBossFight.Framework.StaminaPressure`
- **Accept when:** all pass. The live parry stamina debit and refund on the overlay stay ENG.

## BQ-63: QUEUE_50 tasks 21–30

- **Tasks 26–30 (Batch 6, 2026-11-10), the seeded sweep and property tests.**
  - Suite filter: `OneBossFight.Framework.Track` (Guards, Sweep, TurnLatch.*), `OneBossFight.Framework.Cue` (Rules, Guards, Sweep), `OneBossFight.Framework.Punish` (Rules, Guards, Sweep, PackMontages), `OneBossFight.Framework.Defense` (Rules, Guards, Sweep, CooldownAdjacentBoundary), `OneBossFight.Framework.Combo.Property`.
  - Note: the batch fixed the Track sweep's tautological self-comparison. Check that `Track.Sweep` still passes; a newly failing case is a real finding, not a regression.
- **Tasks 21–25:** the missing TASKS ledger row is now reconciled from the historical Queue_50 receipt X-1786 (2026-11-10 07:08, `Documentation/TEAM_MAILBOX.md`). It records all five read-only audits, including two risks: negative serialized/runtime `StopDistance` can divide by zero at coincident XY in `RPGPackNotifies.cpp`, and `RPGBuildLoadout.cpp` checks reflected parameter names but not `SetIntParam` types. No implementation or validation is claimed; the ledger now records provenance and the open risks. This closes BQ-63's documentation-gap finding without conflating the separate Queue Q D3 row.

## BQ-64: missing native test (new)

`Tests/RPGFatigueProfileBoundaryTests.cpp` adds `OneBossFight.Framework.Runtime.FatigueProfileBoundaries`. The existing `FatigueProfile` test covered negative grace, a zero floor while enabled, floor 1.01 and the F5 requirement. It did **not** cover these rule boundaries, which this test adds:
- grace 100 accepted and 101 refused;
- NaN and infinite floors refused;
- floor exactly 1.0 accepted (enabled but never slows);
- grace 0 with a floor accepted;
- a negative floor refused.

Each refusal also asserts the `Framework.Profile.Fatigue` token. It reuses `FrameworkRuntimeFixture::Fill` through an external declaration; it has external linkage in `RPGFrameworkRuntimeTests.cpp` under the same `WITH_DEV_AUTOMATION_TESTS` guard.

## BQ-65: this report

## Lead run (C-1155)

1. Build Development Editor Win64.
2. Run the filters above, plus the full pinned suite.
3. Record counts in `TEST_PLAN.md`, then tick the two QUEUE_200 Q21–Q30 lines in TASKS only on a pass.

## Risks

- **Linkage:** if the Lead's build uses unity or adaptive-unity grouping, `Fill` still links (it is not `static`). If the fixture is ever made `static` or moved into an anonymous namespace, this test breaks at link time. That is a deliberate tripwire, documented here.
- **Fixture validity:** the boundary cases assume the F5 fixture is otherwise valid. The existing test's "enabled fatigue on valid F5 profile" case shows it is.
