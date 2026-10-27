# S2P-3: dual-trigger coordinator and transactional hydration design

2026-10-26 adversarial addendum: see `07_REGISTRATION_TEARDOWN_ADVERSARIAL_REVIEW.md`. The original31-check model missed mid-registration unbind falling to Legacy, reused encounter identity reviving stale keys, and cross-encounter callback mutations. The revised abstract model passes41/41 with retirement fences and a world-scoped registration guard. In the historical state-machine text below, invalidated/removal must preserve rejection for surviving explicitly claimed actors; removing records alone is insufficient. No production integration is authorized by this correction.

Design proposal, NOT authorization to wire2c–2g. Existing2a scaffold compiled by Claude is infrastructure only; this document records missing semantics and engine evidence for replacement implementation review.

## Verified engine ordering (UE5.5 installed source)

Engine/Private/World.cpp around5428 calls every UWorldSubsystem::OnWorldBeginPlay BEFORE GameMode.StartPlay; its later `OnWorldBeginPlay.Broadcast()` at5443 is AFTER StartPlay. Engine/Private/WorldSettings.cpp326–344 NotifyBeginPlay broadcasts pre-begin then DispatchBeginPlay for actors. Therefore use the SUBSYSTEM method for placed-actor coordination, never assume the similarly named WORLD delegate is early enough. Ordering between different world subsystems is not inferred from either hook: establish explicit subsystem dependency/call direction.

Current PlayerMovesSubsystem.PostInitialize installs spawned-handler; OnWorldBeginPlay enumerates APawn, both call Attach. Both must enter one idempotent decision, not independently attach. A placed binding actor's own BeginPlay is too late as a startup coordinator and cannot order another actor's BeginPlay.

Engine/Classes/Engine/World.h508 declares the exact misspelled API `FActorSpawnParameters::CustomPreSpawnInitalization`. Engine/Private/LevelActor.cpp708–710 calls it before PostSpawnInitialize733 and OnActorSpawned.Broadcast750. This is a candidate explicit native spawn-token seam, NOT executed/tested here. SpawnActorDeferred alone is insufficient if the legacy handler still attaches on spawn before caller receives actor pointer. Native factory must set reservation in pre-spawn callback or use an equally verified scoped spawn protocol, then FinishSpawning only after configuration. No global ignore-next-spawn flag.

## Single ownership / keys

World subsystem owns session GUID and encounter records; GI catalog owns immutable content epoch/leases, not actor state. Key = world-session + explicit encounter GUID + slot + generation. Each participant actor belongs to at most one live encounter; one encounter's target slot cannot resolve another encounter, even in same world. Catalog epoch may survive travel; world session and actor weak references do not. Never use player0/first iterator for a bound participant; legacy fallback only for actors NOT explicitly claimed by a binding.

Native ABI profile selects approved actor/component adapters; author config cannot select arbitrary UObject class/property paths. Source/definition schema+digest pinned; explicit content values validated. Target refs are weak actor refs, immutable key copies retained in delayed callbacks; no process static maps.

## Attach decision contract

`EAttachDisposition { Legacy, PendingBound, BoundReady, RejectBound }`.

- No applicable records / feature disabled: Legacy, unchanged AttachLegacyBossBundle. Disabled path must not create participants or suppress legacy.
- Explicit valid binding reservation, not fully registered: PendingBound. The reservation is created only after whole-batch prevalidation; never attach legacy while waiting, otherwise first reads already happened.
- Whole batch registered/current: BoundReady, suppress duplicate legacy attachment.
- Explicit invalid/poisoned binding: RejectBound, fail closed with diagnostic; NEVER quietly run legacy on half-hydrated actor. Ordinary unbound actors still legacy.

This distinguishes “empty binding suppresses nothing” from “explicit invalid binding falls back”: latter is forbidden. Do not let arbitrary actor tag claim alone suppress gameplay. Reservation requires verified whole binding plan and lifetime-owned token.

## State machine and side effects

Unseen -> Prevalidated/Reserved -> Preparing -> Prepared -> Registering -> Ready; pre-registration failure discards pending allocations, registration failure -> Poisoned. EndPlay/world teardown -> invalidated/removal. All callbacks on game thread; guard reentrancy explicitly. Repeated same trigger/key/manifest is idempotent; same encounter GUID with changed plan/live actor is rejected, not silently rebound.

1. Discover/validate ENTIRE encounter: unique IDs/slots/actors, same world, supported class/skeleton/ABI, target slots, finite typed configs, required fields/dependencies, no begun actor/preexisting consumer, no duplicate plans/names. Perform before consumer creation or legacy suppression. No synthetic flag in author assets.
2. Reserve whole batch, hold snapshots/assets/classes. Prepare ALL participants' unregistered components and Configure methods; setters must not register/tick/start montages or query unrelated world actors. Constructor default assignment is not configured behavior; side-effectful constructors need explicit review. No source-data UObject pointer retained without declared lease.
3. Before every registration and after every callback recheck actor validity/world/key/generation/session. Install explicit participant association for consumers before their OnRegister; all association lookups expose NOT READY until whole encounter complete. Configure-only failures clean pending owned objects and release reservation safely; preserve preexisting unrelated state.
4. Register in explicit legacy order, including footsteps/music, Stagger/Phases/Encounter/Wake/Posture/Death-before-Look/Bleed/Tracker/etc and Legend last. Registration may execute callbacks with irreversible effects; do NOT claim rollback after it. Poison whole encounter on callback failure or invalidation, stop registering more components, invoke reviewed owned-component cleanup and prevent gameplay activation. Never suppress/disable unrelated player/world systems as a fake rollback.
5. Publish Ready atomically for all participants only after every component registered, dependency/target association verified and callback checks passed. Then activate intended gameplay. Actual actor BeginPlay and component registration semantics require engine tests; abstract state Ready is not runtime evidence.

## Existing scaffold differences to close before product hydration

- BindEncounter records whole participant config, but CreateConfigureRegister works per actor; does NOT implement encounter-wide atomic prepare/ready publication. Calling it in a loop is not sufficient.
- Pending component registrations currently check key primarily before configure and after final registration; add per-callback invalidation checks. A registration callback may invalidate actor/session, destroy another component, reenter or advance generation.
- FRecord array lookup is linear. Existing functions are not approved per-hit hot-path APIs. Add actor-key map and (encounter,slot) map with weak refs, generation validation and teardown maintenance; never scan all bindings on each HandlePackHit.
- Existing public ResolveTarget takes arbitrary TargetSlot; production consumer API should resolve stored association/validated role, not let an author redirect cross-context targets at read time. Same encounter/world/current generation required for both ends.
- Configure setters must cover private content fields and legacy Attach assignments; no generic Fields string import. Missing concrete adapters/importer remain open.
- Missing explicit startup coordinator, reserved-deferred-spawn mechanism, effective-field fixtures and actual paired participants.2a success does not close these.

## Reset/respawn/travel

Existing encounter ResetEncounter is sole generation authority. One reset advances whole encounter generation once; never independently increment per component/world tick. Captured old keys remain old, not references to mutable record fields. Clear victim/contact sets, pending timers and observer leases according to their actual owner; no delayed hit resolves into a new generation. Actor replacement requires whole encounter invalidation/explicit rebind transaction; cannot mutate actor pointer under same identity unnoticed. Teardown one world/GI must not clear another's catalog or actor map. Releasing all actor refs is different from releasing shared immutable catalog metadata.

Two transient GIs and model tests do NOT prove two live duels or real travel. Those remain full architecture gates; no N/A waiver. Plan2g only after startup/target semantics accepted.

## Tests ready for implementation

`coordinator_contract_model.mjs` is an executable ABSTRACT model with31 independently asserted scenarios: empty/disabled fallback, invalid/duplicate slots/actors/world/target/generation, two-trigger idempotence, changed manifest refusal, preexisting/partial plan failure, prepare discard, whole-batch readiness, ordered registration, post-registration poison/no fallback, invalidation/reentrancy, associated-target isolation, world isolation, copied old-generation invalidation, unbind and teardown, no fallback after disposal, mixed-generation refusal and uint32 overflow refusal. Model passes are NOT UE automation/build/PIE or performance proof.

Translate into UE fixtures before wiring: test actual actor constructors/OnRegister/BeginPlay/deferred-spawn triggers/GC and invalidating callback components; use real transient world/GI hosts with proper outers and supported actor lifetime. Keep fixtures outside Shipping authoring bypass. Full gate and source/binary pins after stable implementation; compare actual event order, not just final component counts.
