# H001 — selected-route same-world respawn rebind design (proposal)

**State:** design decision accepted by C-804, but Step B implementation is gated on Claude's live PIE order measurement. C-803's fail-closed behavior remains interim and cannot be the production default because the pack respawns the player and resets the encounter in the same world.

## Current evidence and seam

- `URPGPlayerMovesSubsystem::OnActorSpawned` is registered in `PostInitialize` and receives new actors. In selected mode, a late pack boss/player spawn currently releases the activation lease, destroys its transient binding, disables the boss, and reports `EncounterActivation.LateSpawnUnsupported` (`RPGPlayerMovesSubsystem.cpp:35-53,155-179`).
- The existing startup builder requires a game world that has **not** begun play, plus exactly one unbegun pack boss and one unbegun pack player (`RPGEncounterSelectionSubsystem.cpp:72-119`). `RPGBossWorldInputCompiler::CompileWorldInput` also rejects a begun world (`RPGBossWorldInputCompiler.h:17-21`). Reusing this path after same-world respawn cannot work as written.
- `URPGBossEncounter::TickComponent` detects that `UGameplayStatics::GetPlayerPawn(this, 0)` changed and invokes private `ResetEncounter` (`RPGBossEncounter.cpp:115-141`). That reset increments `ResetCount` and `Generation` (`:303-323`). The component exposes getters for both but no reset delegate/event (`RPGBossEncounter.h:48-62`). The reset is therefore a proven pack/project seam, but its exact ordering relative to the player's spawn callback and safe binding teardown has not been measured.

## Accepted seam and ordering plan (C-804)

1. Treat the new recognized player pawn observed by the existing world spawn handler as the candidate identity change; do not infer readiness from spawn alone.
2. C-804 approves a native multicast owned by `URPGBossEncounter`, broadcast at the end of a successful `ResetEncounter` after generation/reset count increment, with `(NewGeneration, ResetCount)` payload. Subscribers use `AddUObject` and unbind on subsystem `Deinitialize`. Step A adds the delegate and logging only. Do not poll or guess a delay.
3. On that notification, perform a fresh exact one-boss/one-player census in the same world. Require the new player and boss to be valid and in the expected reset generation; reject duplicate, absent, dying, begun-state-incompatible, or cross-world participants.
4. Reuse the same selected `URPGBossEncounterDefinition` record and its encounter identity/hash/slots/phase. Capture a monotonically increasing participant generation in the new binding/keys; no pawn pointer is retained by the GameInstance selection store.
5. Release old activation/registrations first on the game thread; only after successful cleanup compile and activate the fresh binding. If release, census, compile, or activation fails, keep the interim fail-closed policy: release any partial lease, destroy only the owned binding, disable the framework boss, and report a stable HardError plus onscreen refusal. Never fall back to the legacy boss bundle.

## Required Lead evidence / unresolved facts

- Measure the real order of player spawn callback, reset detection, reset completion/broadcast, and current binding release in live pack PIE. C-804 requires this before Step B.
- Keep `CompileWorldInput` unchanged. C-804 permits a separate narrow `CompileWorldInputForRebind`-style entry point only if needed; it may accept a begun world only with an explicit participant generation and the exact same selection record, while preserving all other checks.
- Establish measured order for: new pawn spawn callback, reset detection, reset completion, binding release, fresh census, and new activation. No live/runtime order is claimed here.
- Decide whether stale activation components may be removed after BeginPlay; existing cleanup refusal behavior means begun components may remain present but inactive (KI-182).
- Step B participant generation is monotonic `uint64`; at `MAX_uint64`, refuse with HardError and never wrap. Components that have begun play may remain in place but inactive if cleanup refuses (KI-182).

## Focused test plan (after decision)

Native automation should establish first-generation success; same-world player replacement and reset notification; exact new actor identity/generation and unchanged selection record; release-before-new-register order; stale old-generation lookup refusal; missing/duplicate participant refusal; reset/notification duplication idempotence; teardown during pending rebind; and failure injection at release, compile, and activation with no legacy fallback. Every expected refusal uses `AddExpectedError`. Lead owns build and suite run. A live pack PIE run must separately establish that the approved reset signal actually fires after the ~4 s respawn and that the fight resumes; no source test alone proves pack timing.

## Gate

No rebind code until Claude completes and accepts the live ordering measurement. Until then selected-mode late respawn stays fail-closed and continues to block production-default A5/A7.
