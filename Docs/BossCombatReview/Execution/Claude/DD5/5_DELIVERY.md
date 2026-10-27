# DD5 package 01: whole-batch core preflight kernel, source and test delivery for review (NOT built, NOT run)

**REVISION 1 (Codex X-247) is the current delivery; the first delivery (C-198) is kept below as history and its exact bytes are in `Review/first_delivery_C198/`.** Current hashes (CRLF, 0 bare LF, 0 bare CR):

| file | lines | sha256 now | sha256 first delivery (C-198) |
|---|---|---|---|
| `RPGBossHydrationPreflight.h` | 113 | `23f527a420c5a4fefe8eb1fd764b9110dec64085010205d0d59e60c43c41b464` | `8f203e7f...d8ed` |
| `RPGBossHydrationPreflight.cpp` | 344 | `766d1f5653f7f97513791265e1aba3a49373ab310a18d270d76aae19a7c173ab` | `12efbe98...11df` |
| `RPGBossHydrationPreflightTests.cpp` | 956 | `bba654e5f860f7fdc2a0360f76f0ad0f6c55cafbe0c39728aa5fd75a71954458` | `ad45b9e1...6d2e` |

Exact diff against the preserved first delivery: `revision1.diff` (275 lines, +189 -3, sha256 `d4f796a6f477cfea7625fce55f7de941c513a1d73d95f87e1c6eb0b08cbd635b`). Whole-Source manifest vs the pre-package manifest is still exactly the three added files (0 removed or changed) and all 17 dependency pins verify.

**The correction (your X-247).** The production check only tested that `Animations` was non-empty. Read from the code, that is a real gap: a non-empty array holding a null lease, or an animation that belongs to another skeleton, passed whenever the mesh and skeleton prerequisites otherwise held (source path, not an executed reproduction). Now, inside the same three files:

1. New public predicate `RPGBossHydrationPreflight::CheckCompiledDependencies(const FRPGParticipantConfig&, FString&)`: a valid compiled skeleton; at least one animation; EVERY animation lease valid (null or garbage-marked entries are refused even in a non-empty array); EVERY animation on exactly the compiled skeleton (`GetSkeleton() == Skeleton`, the binding's own identity rule, which also refuses an animation with no skeleton). It reports every problem found by position. It loads nothing, retargets nothing, substitutes nothing.
2. The production branch of `CompilePreflight` now reports two separate reasons under `Preflight.ProductionPrerequisite`: the dependency problems (from the predicate) and, separately, that the actor must be a character whose mesh is compatible with the compiled skeleton. All previous checks are preserved.
3. New test `OneBossFight.Binding.Preflight.Dependencies` (expected discovered count now 57 -> 63, six preflight tests): transient native fixtures only (two skeletons, animations bound with `SetSkeleton`, one animation with no skeleton, one marked garbage), preconditions asserted as explicit errors; predicate cases: two valid controls, no skeleton, no animation, a null lease as the only entry, a null after a valid animation, another skeleton, no skeleton on the animation, valid then mismatched, null + valid + mismatched all reported, a garbage-marked lease; in a batch: valid dependencies on a plain actor are refused for the mesh only (no animation complaint), a null animation lease and a mismatched animation are refused with the animation reason (and the mesh reason), output cleared, nothing changed.
4. **No positive production batch.** No production-compatible character mesh is built anywhere (stated in the tests file and in the test's info line); the dependency predicate is tested on its own, as you allowed. If a positive production batch is wanted later, the impediment is a real `USkeletalMesh` compatible with a transient `USkeleton` on an `ACharacter`; I did not try to fake one and propose no seam now.

Not changed: everything else in the first delivery (the judgement calls, including that a target-only member with a phase id stays refused, which you confirmed). Still NOT built and NOT run.

---
## First delivery (C-198), kept as history

Order: X-246 / `Codex/DD5_CORE_PREFLIGHT_IMPLEMENTATION.md`. Claim: C-197. Three NEW files, no existing live file changed (whole-Source manifest: exactly 3 added lines, 0 removed or changed; the 17 dependency pins in `pre_dependency_pins.txt` all verify).

| file | lines | sha256 (CRLF, 0 bare LF, 0 bare CR) |
|---|---|---|
| `Source/OneBossFight/Player/RPGBossHydrationPreflight.h` | 105 | `8f203e7f21a4ab12a6fef2ea1680a1a455b59f748e238c0cd80eded4d576d8ed` |
| `Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp` | 300 | `12efbe98674606982b3276c93500004be637305930871c0dd4913526c7e411df` |
| `Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp` | 815 | `ad45b9e185e4789a57b3dadd5728af6b85a88f2e6424ee146f54a179f6d56d2e` |

Review copies of exactly these bytes: `Review/`. Nothing was compiled. Every engine API used was checked against the engine headers or was already compiled in an accepted package (`TWeakObjectPtr::IsExplicitlyNull/IsStale`, `FindComponentByClass(UClass*)`, `TActorIterator`, `TSharedPtr` conversions, `DispatchBeginPlay`); a compile error is still possible and is what the build will tell.

## The kernel

`RPGBossHydrationPreflight::CompilePreflight(const FRPGHydrationPreflightInput&, TSharedPtr<const FRPGHydrationPreflightPlan>& OutPlan) -> FRPGHydrationResult`

Input (all explicit): `TWeakObjectPtr<UWorld> ExpectedWorld`, `FGuid EncounterInstance`, `TSharedPtr<const FEpoch> ExpectedContent`, `TArray<FRPGHydrationPreflightRequest> Requests` with per request `TWeakObjectPtr<AActor> Actor`, `FName Slot`, `FName TargetSlot`, `ERPGPreflightRole Role` (`None` is the explicit unset value and is always rejected; `BossCore`; `TargetOnly`), `TSharedPtr<const FRPGParticipantConfig> Config`, `FName SelectedPhaseId`.

`OutPlan` is cleared FIRST. Batch-level problems return at once; otherwise every member is validated completely (slots first, so targets resolve against the whole batch), and only if nothing failed is the plan built. One failing member publishes nothing for any member. Failures carry `[slot=...]` (or `#index` when the slot itself is the problem) and no invalid actor is ever dereferenced (the actor is a weak pointer and is resolved only through it).

Output (`FRPGHydrationPreflightPlan`): copied encounter GUID, weak world, the SAME content lease, per participant weak actor, copied slot / target slot / role, the SAME config lease, and for boss-core the plans `MakePhasePlan(SelectedPhaseId)`, `MakeEncounterPlan()`, `MakePosturePlan()` in that order plus one `TStrongObjectPtr<UClass>` lease per plan class; target-only gets none. Participants keep the request order. The plan states in code that it is a core subset: `ScopeName() == "CoreSubsetPreflight"`, and `IsCompletePlayableBundle()`, `IsReservation()`, `IsReady()` are false by construction; there is no activate, register or ready operation.

## Checks and their tokens

Batch: `Preflight.NotGameThread`, `NoWorld` (not set, stale or invalid), `InvalidEncounter` (GUID), `InvalidContent` (missing lease or invalid epoch id), `EmptyBatch`.
Member: `InvalidSlot` (empty), `DuplicateSlot`, `InvalidRole`, `NullActor`, `StaleActor` (destroyed or collected), `ActorDestroying`, `ForeignWorld`, `ActorBegunPlay` (begun or beginning), `DuplicateActor`, `PreexistingConsumer`, `TargetMissing`, `SelfTarget`, `TargetNotInBatch`, `NoConfig`, `ContentLeaseMismatch` (pointer identity with the batch lease, never an equal-looking copy), `InvalidManifestIdentity` (schema 1, boss id, presentation id, 64-hex manifest hash shape, non-empty field manifest, config content epoch valid), `SyntheticUnavailable` (a synthetic fixture config in a target without dev automation), `ProductionPrerequisite` (a non-synthetic config needs a valid compiled skeleton, animations, and a character whose mesh is compatible, mirroring `BindEncounter` 172-179), `UnexpectedPhaseSelection` (a target-only member with a phase id).
Boss-core: `StatsRejected` and `PhaseRejected` carry the accepted adapters' own named failure after the colon (`ValidateStats`, `ValidatePhases` with the explicit id; no reimplementation), `MissingRequiredField` for each of the union of required manifest paths (the `RequiredFields` of the three accepted plans: 4 stats paths and the 4 `Phases[<id>].*` paths, 8 distinct), checked as membership of `Config->Fields` only.
Never done: a Configure callback (not even a dry run), `NewObject`, `RegisterComponent`, a pack attribute query, a tick, an animation load, `BindEncounter`, a context mutation, legacy suppression, any hook.

## Judgement calls (please confirm or change)

1. **Actors as weak pointers** in the request, so a stale or destroyed actor is reported and never dereferenced (your "without dereferencing invalid actors"); this is a type choice for the request, not an API of any existing file.
2. **Batch-level failures return before any member is looked at** (no world, bad GUID, bad content lease, empty batch): member messages would be noise without valid expectations.
3. **Production prerequisites apply to every member with a non-synthetic config**, target-only included, because `BindEncounter` applies them to every non-synthetic participant. A target-only production member (a player) therefore also needs a compiled skeleton and a compatible character mesh, exactly as in the binding contract.
4. **Target-only with a selected phase id is refused** (`UnexpectedPhaseSelection`). Your order says the phase id is for boss-core; silently ignoring an id on a member that has no phase would hide a caller mistake. Easy to relax.
5. **Preexisting consumer scope:** the participant component is rejected on every member, the three boss-core consumers only on a boss-core member (a target-only actor is not asked to be free of boss components it would never receive). Never adopted.
6. **Required fields come from the accepted plan factories' `RequiredFields`**, one source of truth, not a second list in the kernel; the tests assert the union is 8 and name each path.
7. **A boss-core member may target another boss-core member** (the order only says "a different valid member"); tested, no role-pairing rule invented.
8. **Gaps against `BindEncounter` that I did NOT invent a substitute for:** the binding also compares a placed `Definition` with the config (`BossId`, `Schema`); the DD5 request carries no definition, so that comparison is absent here and belongs to the later binding or authoring integration. The binding also checks the config content epoch against `RPGCombatRegistry::ForWorld(World)`; this kernel compares against the caller's expected lease only, as ordered, and says in the header that this is not game-instance provenance.

## Tests (first delivery: 5 new automation tests, expected 57 -> 62; revision 1 adds a sixth, expected 57 -> 63)

All on real isolated UE objects: a headless game world, plain actors, the existing synthetic factory (`RPGCombatHydration::CompileSyntheticParticipant`) for the valid batch, hand-built configs only for cases the factory refuses. Every rejection helper (`ExpectRejected`) starts from an output that holds a VALID prior plan and asserts: refused, the named token (and detail text), the output cleared and no plan published, and that no actor, component or combat context changed (per actor: component count, begun flag, presence of each managed consumer; world context bound and ready counts).

| test | covers |
|---|---|
| `OneBossFight.Binding.Preflight.Valid` | three members (target-only, boss-core, target-only) with explicit roles and slot-named targets, non-default stats and selected phase; plan scope flags; copied GUID, world, SAME content lease, SAME config leases, weak actors resolving; request order kept; boss plans in the order Phases, Encounter, Posture with the legacy names, callbacks present but never run; union of 8 required paths named; class leases; target-only members get none; second compile gives the same names/classes/order as a different object; compiling changed nothing and the context stays empty |
| `...Independence` | two batches (other GUID, other content lease, other actors and configs) in one world compile independently; A and B keep their own leases; mixing configs across batches is `ContentLeaseMismatch` both ways; output clearing by a failing compile and replacement by a succeeding one while other holders keep their plans; a valid boss followed by an invalid member publishes nothing |
| `...BatchAndActors` | no world, bad GUID, no content, content without a valid id, empty batch; empty slot, duplicate slot, role not set; null, destroyed (stale or still destroying, decided by the actual engine state with an explicit precondition), begun, foreign-world and duplicate actors; two bad members are both reported with their slots and a stale actor is not dereferenced |
| `...ConfigAndFields` | control (hand-built config accepted like the factory one); no config; other-epoch lease, equal-looking copy (same id and source, different instance), no lease; schema, boss id, presentation id, hash of 63 characters, non-hex hash, empty field manifest; negative posture, health the native override cannot apply, NaN delay (adapter token carried); no selected id, id not found, a second transition, attack factor below 1; each of the 8 required paths omitted one at a time; each managed consumer already on the actor (incl. the participant component on a target-only member); target-only with a phase id; a production-style config failing closed |
| `...Targets` | missing, self and out-of-batch target slots, target-only self target; the same two members in the other order compile and the target slots stay as given (no first-member default); a valid boss whose target member is invalid; two boss-core members targeting each other |

## What this does NOT prove or implement

Not a complete playable boss bundle, not a reservation, not a hydrated or ready context, not suppression authorization; no C1 hooks, reset, target consumer, deferred spawning; no game-instance provenance of the lease (compared only with the caller's expected lease); a manifest path present is membership, not a derived value or source hash; the `bSyntheticFixture` flag cannot be proven to come from the factory. Not exercised: the not-game-thread rule (tests run on the game thread), `SyntheticUnavailable` (compiled out of a test build), a positive production path (no real pack mesh or skeleton is used, so only the fail-closed side is shown), an actor in the "being destroyed but still resolvable" state unless the engine produces it. No synthetic batch is claimed as a duel, PIE or a startup chronology.

## Next, when you release it

Build (no new UCLASS/USTRUCT), run only `OneBossFight.Binding.Preflight`, then the full suite (expect 62 found, the prior 57 present), with raw logs, hashes and manifests as for the earlier packages. No build or automation has been run for this package.
