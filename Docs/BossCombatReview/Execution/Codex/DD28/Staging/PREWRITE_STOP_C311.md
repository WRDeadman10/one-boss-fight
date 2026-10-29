# DD28 C-311 pre-write stop — 2026-10-29

No staged C++ implementation, Source edit, build or engine run has been made. The accepted preparation interface triggers the explicit C-311 stop condition before implementing registration.

## Frozen interface cannot expose the required ownership/state

- The actual artifact type is `FRPGPreparedBatch`, not the illustrative `FRPGPreparationBatch` (RPGBossHydrationPreparation.h:75).
- `IsPrepared()` checks only `bPrepared && !bAborted` (:86). Both flags and Members are private (:124-126), and the only friend is the existing `FRPGBatchPreparer` (:103-104). There is no production registered-state getter/setter or registration transition.
- Production public access returns the plan, counts and participant summaries (:92-96). Owned component pointers are accessible only through `OwnedComponentsForTest()` behind `WITH_DEV_AUTOMATION_TESTS`, and those are const pointers (:98-100). Its own comment explicitly says production code has no component access.
- A report-side registered flag could describe one call's result, as C-311 permits, but does not expose the artifact's exact owned leases or provide a persistent batch-owned transition. Do not solve ownership by looking up objects by actor/class/name, casting away const on the test-only accessor, editing private access with a macro, redefining the existing friend class, or introducing a process-static registry. None is authorized and each bypasses the accepted boundary.

Therefore the frozen class cannot represent a registered transition itself, and the new production library cannot enumerate/mutate precisely its owned components through the accepted interface. C-311 explicitly requires stopping if the batch cannot represent the state without accepted preparation edits; those edits are also explicitly excluded. A concrete lead disposition of both ownership access and state/lifetime is required.

## Abort contract confirmed

RPGBossHydrationPreparation.cpp:319-361: Abort refuses off-thread; the first call sets `bAborted=true` (:332), then walks members/components in reverse. Registered, begun or reparented components cause `Preparation.ContractViolation` and are left alive (:347-352). All leases are then released (:359). The next Abort returns an empty report because the batch is already aborted (:328-330).

Consequences: failure rollback must unregister this registration attempt's successful registrations in reverse BEFORE Abort, and it needs exact owned handles to do so. An immediate first Abort after successful registration would report violations and leave the registered components alive; a second Abort would be idempotently clean, not report those violations again. A success lifetime contract must address artifact destruction too, since its destructor calls Abort (:298-309). No such behaviour was changed here.

## Seven-class registration side-effect source check

Inspected both headers and implementations for Look, Death, Bleed, LowSweep, Shockwave, HealPunish and CloseClipSwap. Each derives directly from UActorComponent. None declares/defines an OnRegister or InitializeComponent override. This is a source check, not an engine observation that RegisterComponent has no engine-side effects.

- Look's explicit next-tick Apply scheduling is in BeginPlay only (RPGBossLook.cpp:26-32); its loads are in Apply, not a project OnRegister override.
- Death's setup is in BeginPlay (RPGBossDeath.cpp:97 onward); death asset loads and remains spawning occur in its other runtime paths, not a project OnRegister override.
- Bleed's synchronous asset loads are in BeginPlay (RPGBossBleed.cpp:31-40). CloseClipSwap's preload is reached from BeginPlay/runtime code. HealPunish's asset/projectile operations are in runtime paths. No custom registration/initialization load/timer/spawn override was found in these seven classes.
- This does not authorize registration on a begun actor/world, BeginPlay, ticking, asset loads, readiness, context binding, reservations or legacy suppression.

## Intended bounded design, pending interface decision

The future entry point would run on the game thread, reject stale/aborted/already registered artifacts and begun owners/worlds before mutation, validate the entire owned set, then register each boss's components in plan order, checking registered and not begun after each step. Failure would unregister the attempt's successful registrations in reverse, then Abort and report member/plan/reason plus cleanup errors. Success would report per-member ordered classes. Exact lease access and a durable registration/cleanup state are unresolved; no declaration pretending those are solved is staged.

No authored arithmetic or numeric policy is proposed; ordinal loops/counts still require bounded index checks. No new test code exists, so there are no new array mutations to audit and no tests to claim. Registration, failure injection and success/destructor tests remain unimplemented until the stop is resolved.

Requested lead decision: release a specific minimal preparation-interface/state delta in staged copies, or specify an alternative ownership/lifetime protocol supported by the frozen API. Do not promote or change the 212 Source pins during DD27 authoring qualification.
