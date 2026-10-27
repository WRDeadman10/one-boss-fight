# Preparation abort and owned cleanup contract

Codex lead, 2026-10-26. Source review and proposed implementation requirements only. No live edits, engine execution or new integration authorization. Complements07_REGISTRATION_TEARDOWN_ADVERSARIAL_REVIEW.md; inert2a acceptance remains infrastructure only.

## Independently inspected source

`Source/OneBossFight/Player/RPGEncounterBinding.cpp:311–335` configures participant and consumer objects, rejects registered/begun consumers after configure, destroys pending objects on preparation failure, then registers participant followed by every consumer. It checks binding identity after configure and after the registration loop, not around every registration callback. Participant `EndPlay:117–120` unbinds the encounter and releases its snapshot/context. There is no explicit pre-BeginPlay abort API in that class.

Installed UE5.5 `Engine/Source/Runtime/Engine/Private/Components/ActorComponent.cpp:1558–1609` shows DestroyComponent calls EndPlay only when `bHasBegunPlay`; uninitialization, unregistration, removal from actor ownership and OnComponentDestroyed follow separately. Therefore destroying a prepared-but-never-begun participant does not guarantee execution of its EndPlay unbind/snapshot-reset code. This is a static engine/source observation, not a measured leak or runtime reproduction. GC may later release the C++ members; deterministic abort must not rely on that latency for external ownership cleanup.

## Required abort distinctions

| Failure stage | Proposed coordinator obligation | Forbidden inference |
|---|---|---|
| Whole-plan validation | Create nothing; publish no active association | Invalid explicit binding is safe to silently route Legacy |
| Pure allocation/configure, no callbacks with effects | Explicitly release owned pending objects/leases and reconcile the reservation disposition; preserve unrelated state | DestroyComponent necessarily calls EndPlay or removes context records |
| Configure registers/ticks/plays audio or animation | Mark a contract violation and poison the encounter; run effect-aware owned cleanup | A false Configure return proves rollback or harmlessness |
| Registration begun, callback invalidates/ends actor/world | Stop before next registration; retain fail-closed routing for survivors; invoke reviewed idempotent cleanup | Final pointer/key check alone protects intermediate callbacks |
| World teardown | Invalidate keys first, then release only this world's ownership; preserve other worlds | Cancel every global/shared effect to simplify teardown |

Proposed implementation separates `AbortPreparation` (no published gameplay effects), `PoisonAndCleanupOwned` (effects may already exist), and ordinary EndPlay. Names are illustrative, not an approved public ABI. A transaction ownership ledger tracks each allocated object, registration attempt, configuration lease and acquired external effect handle. Cleanup runs at most once per owned resource, tolerates already destroyed objects, and does not acquire an active registration guard to perform invalidation. Participant destruction may reenter UnbindActor after BeginPlay; keep it idempotent. Pre-registration failure disposition must agree with the explicit-binding fence from07; do not automatically release it into Legacy.

## Consumer evidence and adapter obligations

- Encounter.cpp:66–74 captures HomeTransform and may Sleep during BeginPlay; its tick later mutates pack attributes and AI state. Configure may assign final inputs but must not invoke Sleep or seed a synthetic home state. Preserving current behavior requires actual actor/controller startup evidence.
- Phases.cpp:62–78 synchronously loads dependencies, snapshots movement speed and adds a Stagger tick prerequisite in BeginPlay. Final fields/dependencies must be ready first. Reconfiguration after this snapshot is not configure-before-register parity. Cleanup must account for any actual transition effects, not merely null the config object.
- DormantWake.cpp:37–55 loads clips, adds an Encounter prerequisite, may start the dormant montage and stops clips in EndPlay. StopClips:132–155 also calls Encounter.CancelWake; this is a gameplay side effect. Do not invoke it blindly on unrelated/preexisting components or assume it is a passive lease release.
- Music.cpp:26–37 stops owned voices in EndPlay; EnsurePlayer:54–65 creates non-auto-destroy sound components later. A component being registered successfully is not evidence that audio voices were created, stopped or destroyed. Separate pre-voice abort from active-voice cleanup and verify under an audio-capable run; `-nosound` null creation does not prove audible behavior.
- Legend.cpp:66–75 owns world teardown cancellation and a core ticker. CancelAll:193 onward restores shared hit-stop/slow motion and stops camera shake classes through the first local camera manager. A single encounter's adapter must not call world-wide CancelAll as a generic transaction rollback in a future multi-encounter world. Define scoped effect ownership/arbitration before claiming independent duels; that is a design gate, not a requested gameplay patch.

## Implementation evidence still needed

Real fixtures must inject configure failure before any registration, illegal early registration, failure/invalidation in first and later OnRegister callbacks, participant destruction before and after BeginPlay, partner survival, and repeated cleanup. Record exact callback order, remaining actor-owned components, stale key rejection, leases and unrelated encounter effects. Keep original event side effects and failures visible. No UE fixtures were run here; no leak-free, rollback-safe, two-duel or performance claim is made.

## Source pins (SHA256)

| Source relative to Source/OneBossFight | Hash |
|---|---|
|Player/RPGEncounterBinding.cpp|2fe63bcb78261b9bdd15be33607ea3c696ae33227989facc5b67e15cd91110dc|
|Player/RPGBossEncounter.cpp|dc149393f2fff1788ea22daf42db0b14f85ac36f58ad59c459b44ee94600c96d|
|Player/RPGBossPhases.cpp|c43615412e1f345d6ed75cc6d6a6b0d9ece6acaaac612e545b42cc24087f7a06|
|Player/RPGBossDormantWake.cpp|fd3df15b1530a227750548b4e7241f16d2f3e946e3b04e49bc28ce4ae9524788|
|Audio/RPGBossMusic.cpp|d69950f2f2868ac89b4b810d21fe8fbcb41790a0b5836a4e541b01a59c2c9f57|
|Player/RPGLegend.cpp|a22c13b78bb13c5fe7aa9f1d59e34d494c96725bdbc39384c1755c8154c79df3|
