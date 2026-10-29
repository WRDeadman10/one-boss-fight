# DD15 actual unregistered batch preparation

Claude SOURCE ONLY:3 NEW files Player/RPGBossHydrationPreparation.h/.cpp and Tests/RPGBossHydrationPreparationTests.cpp. No existing Source/Binding/preflight/adapter/native edits. Save full178-file manifest and exact dependencies before work; new181 manifest must preserve all178 original files. Deliver actual code/tests/diff before any build. No separate prose design round.

This implements the next runtime integration primitive: prepare ALL accepted subset components for the whole explicit batch without registering or beginning ANY managed component. It is explicitly callable but not wired to any startup/spawn hook. No context binding, reservation, participant component or Ready publication. An incomplete prepared subset never authorizes suppressing legacy attachment.

## API and ownership

Namespace RPGBossHydrationPreparation, public PrepareBatch taking the existing FRPGHydrationPreflightInput. Return a move-only result containing errors and a unique owned prepared-batch object on success, null on failure. Use Succeeded/IsPrepared wording, not gameplay IsReady. A return-value result avoids leaving a caller's prior output silently usable after failure; no caller-supplied arbitrary plan/callback array accepted.

Game-thread-only preparation and destruction. Refuse off-thread calls before touching UObjects. Make ownership/lifetime explicit, noncopyable and privately constructed; callers must keep and release the artifact on the game thread. No process-static maps/subsystems or automatic destruction from a background thread. A different necessary seam/lifetime design must be presented as an exact proposed delta, not broadened into startup wiring.

Run the accepted CompilePreflight over the ENTIRE input first and retain its validated world/encounter/slots/targets/config/content/class leases. Any rejection returns no prepared artifact and creates no managed component for any actor. Do not accept a manufactured preflight-plan struct as authority. The source's caller/GI, manifest and mutable-alias limitations remain; input DTOs may not be mutated concurrently or during the call. Retained const leases alone do not prove deep immutable authoring data.

Only after whole-batch preflight success, allocate exactly the5 trusted native consumer classes per BossCore using reviewed factory class/name pairs and owner actors. TargetOnly gets none. Keep strong component/class leases from creation onward. All components remain unregistered, not begun, unticked. Constructors may set native defaults but must not load/play/attach other consumers; read/pin each actual constructor. No arbitrary classes, generic reflected assignment, mutable callback overrides, attributes or ability side effects.

Configure every pending component with its accepted plan callback and validated config. Recheck weak actor/world/role/encounter identities and component owner/class/lifecycle before and immediately after each allocation/configure; revalidate appropriate preconditions on failures/invalidation. Retain the exact selected-phase binding and the already-compiled participant associations; do not look up player0 or infer a target. Existing callbacks operate before registration and have their own whole-record guards. Never call the old per-actor CreateConfigureRegister loop.

Return a prepared artifact ONLY after every member/component configured successfully. Expose no Register/Commit/Activate/Ready or legacy-suppression API. Production components remain privately owned by the artifact; limited read-only inspection or dev-test access may be defined explicitly for tests. There is no claimed concurrent reservation: second PrepareBatch on actors already holding these components must fail via preflight and must not destroy the first artifact's components.

## Abort and cleanup

Artifact Abort/destruction must explicitly DestroyComponent on precisely its owned unregistered allocations, not merely drop TStrongObjectPtr roots (the owner component set also holds them). Cleanup also covers components created before the last configure failed. Destroy each owned component at most once, tolerate already-destroyed component/owner/world teardown without dereferencing stale pointers, release all leases, and leave unrelated preexisting components untouched. Abort is idempotent. Partial failure cleans every earlier participant too, not just the failing member.

No registration ever occurs here, so cleanup may claim only pre-registration owned-resource cleanup. If any caller externally registered/began an artifact-owned component, fail closed/report that contract violation; never pretend an irreversible registration callback was rolled back or destroy unrelated gameplay systems. No cleanup delegate framework or EndPlay-only assumption: an unregistered component may never have begun play.

## Actual tests and failure injection

Isolated UE-world/native-owner fixtures using accepted valid configs. Success: two BossCore members+TargetOnly,10 actual owned/unregistered components, exact classes/names/owners/configured representative fields, no participant/bound/Ready context, no BeginPlay/tick/load, retained config/content/phase identities. Explicit and scope-exit abort restore each actor's prior unrelated component set and public state, all owned objects reported destroyed/unregistered; repeat Abort harmless. Second prepare rejects without damaging the first; preparation succeeds again only after the first has aborted.

Whole-batch invalid late member must allocate nothing for earlier members. For actual mid-preparation cleanup, allow a narrowly scoped WITH_DEV_AUTOMATION_TESTS-only failure ordinal after a real allocation or configure operation in these NEW files. Production PrepareBatch has no author/cvar/control for it and no arbitrary injected executable callback. Tests label it injected, never an organically reproduced native failure. Fail after early and late allocations/configurations spanning multiple participants; check no artifact/managed component survives, unrelated components retained, context untouched. Capture pointer identities/counts after fixture setup, not before adding fixture objects.

Actor/world lifetime failure and destruction of an owned unregistered component before abort must be handled without double destroy, stale lookup or global cleanup. Include wrong-thread refusal only if safely exercisable without UObject work on the worker. Report any unexercised lifetime branch explicitly. Do not loosen accepted validators or register components to make tests easier. Positive real-asset fixture need not be repeated wholesale; DD14 remains its separate evidence.

## Delivery/gates

Actual3-file diff/Review/source181 manifest/source+native constructor+adapter pins/SHA receipts, exact test names and lifetime assumptions. All178 old Source unchanged. No UHT/build/automation until independent source review. Any failure/drift later stops for preserved first-source/raw-log evidence and exact proposed delta before fix/retry.

No UCLASS/world hook, Binding/context mutation, reservation/disposition, target/reset rewiring, BeginPlay/registration, activation, legacy suppression, asset edits, PIE/full driver gate/package/noneditor, config/scripts/pack/git. All83/networking required,A5 parked. Future reservation/full-cluster/registration atomicity and authority remain concrete separate packages; this step advances actual owned preparation without claiming a playable data-defined boss.
