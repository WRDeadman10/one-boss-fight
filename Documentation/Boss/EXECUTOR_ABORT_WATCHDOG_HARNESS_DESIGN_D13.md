# Executor abort/watchdog and harness design (D13)

## Scope

Design-only follow-up to C-740's request for a real stateful executor regression fixture. Existing `RPGFrameworkRuntimeTests.cpp` uses a bare `NewObject<URPGFrameworkMoveExecutor>` for rejected initialization and cleanup; no existing test initializes a live executor with a boss, target, animation instance, model token, and owned montage. `RPGAutomationTests.cpp` and other adapter suites demonstrate a scoped transient game-world pattern, but not this executor's full dependency set.

Relevant paths: initialization and owner/target/AnimBP/slot checks in `RPGFrameworkMoveExecutor.cpp:69-89`; start refusal and playback setup in `:121-174`; watchdog and component tick in `:176-192`; abort/EndPlay in `:580-605`; rearm in `:96-105`; runtime-only CVar hooks `rpg.BossProofSuppressMontageEnd`, `rpg.BossProofRepeatAbort`, and `rpg.BossProofStaleCallback` in `:44-54`.

## Proposed fixture

Create `FScopedFrameworkExecutorWorld` in a dedicated Editor automation test translation unit. Follow the established `UWorld::CreateWorld(EWorldType::Game,false)`, engine world-context registration, `InitializeActorsForPlay`, and paired context/world teardown pattern in `RPGAutomationTests.cpp:64-89`. Spawn the native `ARPGFrameworkProofFixture`, `ARPGFrameworkBossCharacter`, and an explicit target pawn in that world. Load a known proof profile/card, Sevarog skeletal mesh and AnimBP, then use the real authored `FullBody` slot graph and sequence so `ValidatePlaybackCard`, animation position, and montage ownership execute through the production wrapper. Call `InitializeProof` and drive `StartCard` with deterministic same-world snapshots. Do not fake resolved assets or claim game-world animation coverage from a metadata-only card.

Asset readiness is a fixture precondition, not a behavior under test. If those proof assets or slot graph cannot be loaded in the automation target, keep the pure model tests and document that the wrapper harness is blocked; do not substitute an unresolved preview card or mock a montage pointer.

## Bounded cases

| Case | Steps | Required assertions |
|---|---|---|
| D8 failed replacement while active | Start card A. Call `StartCard(B, ...)` while A is active so state refusal is expected. Abort/recover A; submit a later neutral snapshot through convenience `Start()`. | First call refuses with `Framework.Playback.State`; original A remains the selected member and starts on retry; B never becomes active. Assert model token/state and `ActiveCard()->Spec().MoveId` at each boundary. |
| D9 rejected generation rearm | Start A and retain its token/montage state. Call `Rearm(currentGeneration)` and `Rearm(olderGeneration)`. Then call with a strictly newer generation. | Equal/older return `MoveModel.Generation`, keep `IsIdle()==false`, keep old token accepted and active card unchanged. Newer rearm stops playback, leaves model idle, and rejects old token; valid newer-generation behavior unchanged. |
| Abort and EndPlay idempotence | Start A, call `Abort` twice, then destroy/end play. Also destroy while A is active. | One model abort/close sequence, one owned-montage cleanup, tick disabled, motion unlocked, no duplicate release/cleanup; existing repeat-abort hook may support telemetry but assertions should inspect state. |
| Watchdog | Start A with `rpg.BossProofSuppressMontageEnd=1`; advance the real transient world beyond computed `CardWatchdogTimeoutSeconds`. | `WatchdogFired`, named `Framework.Playback.WatchdogTimeout`, idle model, stopped owned montage, tick disabled, and successful same-generation `RecoverAfterAbort` followed by a later start. Reset the CVar in fixture teardown. |
| Stale callback control | Abort attack A, start B, then inject A's token against the model (or enable the existing stale-callback test hook). | Old token refusal does not alter B; B remains accepted and active, no events emitted for stale callback. |
| D22 target identity / caller-owned contract | Keep an explicit current-player pawn plus separate boss/self and friendly actor candidates in the transient world. Drive the relevant trusted caller path with overlap/contact geometry that includes the extra actors. | Resolver receives only the active player target; self/friendly overlaps are ignored by the caller. Do not assert a resolver self/team predicate: C-745 directs the API to remain caller-owned. If the fixture cannot exercise a caller's real geometry, mark that case blocked rather than simulating resolver filtering. |

## Harness feasibility and limits

The test world pattern exists, so a stateful fixture is feasible in principle. The hard dependencies are a real framework AnimBP with a validated slot node, resolved authored card/skeletal assets, and a tickable world/animation instance that advances montage state. These are content-backed Editor test dependencies; a headless pure automation test cannot honestly simulate them. Start with D8/D9 state refusals and model/montage ownership assertions, then include watchdog only after a measured world tick advances the actual slot montage. Keep asset-load/setup failures explicit and never count them as behavior passes.

The two D12 pending-hit/riposte issues are recorded in KI-172/KI-173; their reset-order cases belong in the same broader fixture backlog but are separate from this executor harness. No test source was added and no build, test, Editor, PIE, or package run occurred for D13.
