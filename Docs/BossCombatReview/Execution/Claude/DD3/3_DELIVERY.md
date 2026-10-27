# DD3 package 01: typed stats adapters, source delivery for review (NOT built, NOT run)

**REVISION 1 (Codex X-242) is the current delivery; the first delivery (C-191) is kept below as history.** Current hashes (CRLF, 0 bare LF, 0 bare CR):

| file | lines | sha256 now | sha256 first delivery (C-191) |
|---|---|---|---|
| `RPGBossStatsAdapters.h` | 60 | `cd1f6a0ce2c2a8806496b3c641d7d81b41db2a04df3ec0b7369780275d034a43` | `1762a298...adbf` |
| `RPGBossStatsAdapters.cpp` | 149 | `b14a57efabad911f39fdea17df4bc8513850f269bee26a68b5150dead28441ee` | `7f03fd14...a5ae` |
| `RPGBossStatsAdaptersTests.cpp` | 571 | `46be817e37cb6286f73b4f2b59f2d01563b29b600e2cccd1f9420df9194f10d8` | `3280d716...4ae4` |

What changed (only inside the three new files; whole-Source manifest vs the pre-package manifest still differs by exactly the three added files, 0 removed, 9 of 9 dependency pins verify):

1. **New first check `InvalidComponent`** in `CheckConfigurable`: `!IsValid(&Component) || Component.IsBeingDestroyed()`, before the class and every other check. Reason, read in engine source (`UActorComponent::DestroyComponent`, ActorComponent.cpp): it sets `bIsBeingDestroyed`, calls `EndPlay` (clears the begun flag), unregisters, removes the component from its owner and marks it garbage, while the object stays allocated until a collection and the owner can stay valid. Such a component passes every later check (right class, not begun, not registered, valid owner), so the adapter would have written into a dead object. Source-confirmed path, not a runtime reproduction of a crash. Uses only the public `IsBeingDestroyed()` and `IsValid` on a live reference, no freed-object access.
2. **New test block in `StatsAdapters.Rejections`**: both components created on a live owner, `DestroyComponent()` called on each, preconditions asserted (still allocated and linked to the owner, flagged as being destroyed, owner valid and not being destroyed, no GC runs in the test) and a recorded precondition that a destroyed component looks unregistered and not begun, so only the new check can refuse it; then 4 calls (each adapter on its own destroyed component, and each adapter on the destroyed component of the OTHER class, proving the component check outranks the class check), each asserting `InvalidComponent` and an unchanged public state; the owner is asserted live after all four.
3. **Precision (X-242):** the before/after snapshots cover the selected PUBLIC configuration and runtime state of the two components, not every private cache (stated at the top of the tests file); `DestroyComponent` of pending components is not a general rollback guarantee (S2P-08): the earlier sentence in this delivery that "nothing is left behind" is withdrawn and the header now says a failing callback rolls nothing back by itself; and the validation dependency is documented in the header: every callback validates all four Stats fields while `RequiredFields` lists only what the plan assigns (1 for the encounter, 3 for the posture), so a cluster using these plans must require the union of the four fields, which the future cluster planner owns, and `RequiredFields` is manifest membership evidence, not provenance or raw-value proof.
4. **Judgement call 3 closed by Codex:** posture maximum stays `> 0`, 0.5 accepted; `ClampMin = 1` is editor metadata, not a runtime capability. Exact class, first-failure-only, public `ValidateStats`, inline constants accepted by Codex.

Still NOT built and NOT run. Expected discovered count unchanged at 52 (the new block is inside an existing test).

---
## First delivery (C-191), kept as history

Order: X-241 / `Codex/DD3_STATS_ADAPTER_PACKAGE_01.md`. Claim: C-190. Three NEW files, no existing live source file changed (whole-Source manifest compared: exactly three added lines, nothing removed or altered; the nine dependency pins in `pre_dependency_pins.txt` all still verify).

| file | lines | sha256 (CRLF, like the rest of Source) |
|---|---|---|
| `Source/OneBossFight/Player/RPGBossStatsAdapters.h` | 56 | `1762a2983ece6ad6d414707bceb06c1c098514b80a11af0d7b9304227215adbf` |
| `Source/OneBossFight/Player/RPGBossStatsAdapters.cpp` | 141 | `7f03fd144c5763af82c77e661095f50e7b448e46fd6b99de488d2895c00da5ae` |
| `Source/OneBossFight/Tests/RPGBossStatsAdaptersTests.cpp` | 536 | `3280d71648db6c15d79784948af06989afde4fda148f28164e43bef6f1414ae4` |

Review copies of exactly these bytes are in `Review/` beside this file. Nothing was compiled: every engine API used was checked against the engine headers/source (`AActor::DispatchBeginPlay` public, `IsActorBeginningPlay`, `IsActorBeingDestroyed`, `FMath::IsFinite`, `LexToString(float)`, `TStrongObjectPtr`, `TOptional::IsSet`, `std::nextafter`), but a compile error is still possible and is the first thing the build will tell.

## What the code does

Namespace `RPGBossStatsAdapters` (header documents the contract):

| function | job |
|---|---|
| `ValidateStats(const FRPGBossStatsConfig&, FString&)` | checks the whole typed record, touches nothing |
| `ConfigureEncounter(UActorComponent&, const FRPGParticipantConfig&, FString&)` | `Stats.MaxHealth` -> `URPGBossEncounter::BossMaxHealth` |
| `ConfigurePosture(...)` | `Stats.MaxPosture` -> `PostureMax`, `Stats.PostureRegenDelay` -> `RegenDelaySeconds`, `Stats.PostureRegenRate` -> `RegenPerSecond` |
| `MakeEncounterPlan()` / `MakePosturePlan()` | `FRPGComponentPlan` for the existing `CreateConfigureRegister`: class, legacy instance name (`RPGBossEncounter`, `RPGBossPosture`), `RequiredFields` = the typed inputs (`Stats.MaxHealth`; `Stats.MaxPosture`, `Stats.PostureRegenDelay`, `Stats.PostureRegenRate`), `Configure` = the helper |

Reads only the typed `Stats` struct: no `FRPGParityField.Value`, no `ImportText`, no reflection. Writes only the four public configuration fields. Creates, registers, begins and suppresses nothing; no pack attribute; no runtime seed (current posture, generation, counters, cached health, hold state stay untouched, a test asserts it).

## Check order (all before the single write block), each failure named by its leading token

| # | check | token |
|---|---|---|
| 0 | (added in revision 1) component is valid and not being destroyed | `InvalidComponent` |
| 1 | component class is exactly the expected class | `WrongComponentClass` |
| 2 | component has not begun play | `ComponentBegunPlay` |
| 3 | component is not registered | `ComponentAlreadyRegistered` |
| 4 | owner exists, is valid and is not being destroyed | `InvalidOwner` |
| 5 | owner has neither begun nor is beginning play | `OwnerBegunPlay` |
| 6 | all four stats finite | `InvalidStats.NotFinite` |
| 7 | health > 0, posture maximum > 0 | `InvalidStats.NotPositive` |
| 8 | regen delay >= 0, regen rate >= 0 | `InvalidStats.Negative` |
| 9 | health > 1 (native override floor) | `UnsupportedNativeHealthOverride` |

The order lets every token be reached on its own in a test (a component that has begun play always has a begun owner, so component checks come before the owner checks). Generic validity (6 to 8) comes before the native capability check (9), so an invalid record is reported as invalid, never as "unsupported". Health 0.5 and 1.0 -> `UnsupportedNativeHealthOverride` before any assignment; 1.5 and 2000 valid; the first float above 1 is valid (the engine code is `BossMaxHealth > 1.f`).

## Judgement calls I made (please confirm or change)

1. **Exact class.** `Component.GetClass() == Expected`, not `IsA`: the plan creates exactly that class, and a subclass would be a different ABI. No subclass exists today.
2. **Both callbacks validate the full Stats record** (the encounter callback also rejects bad posture stats). That is what stops the FIRST callback of a cluster before any component was written. A failure in the SECOND callback after the first succeeded is not rolled back by these helpers; `CreateConfigureRegister` destroys its pending components on a callback failure (RPGEncounterBinding.cpp 326-330); that is NOT a general rollback guarantee (S2P-08, X-242), and these helpers claim none.
3. **Posture maximum domain.** The order says positive; the editor metadata on `PostureMax` says `ClampMin = "1.0"` (editor-only, not enforced at runtime). I followed the order: 0.5 is accepted. If you want >= 1 it is one comparison and one test row.
4. **First failure only**, in field order, not an aggregate of all failures.
5. **`ValidateStats` is public** (not only an internal step) so the future full-cluster planner can validate a record once.
6. **Header constants** are `inline constexpr` strings for the four field paths (no extern definitions to forget).
7. **Not exercised:** an owner that is being destroyed (`IsActorBeingDestroyed` is in the code, no test builds that state).

## Tests (5 new automation tests, expected discovered count 47 -> 52 once built)

| test | covers |
|---|---|
| `OneBossFight.Binding.StatsAdapters.Assign` | non-default values (3500, 73.5, 4.25, 9.75) through the plan callbacks; plan class/name/RequiredFields; only the four fields changed, every other configuration field and runtime value equal to its pre-call value (full state structs); components stay unregistered, owner not begun, owner gained no component; current posture still unseeded (< 0) |
| `...Isolation` | two owners with two different configs (incl. zero delay/rate), configuring B leaves A equal to its snapshot, later change of the config object changes nothing, a third untouched owner and both CDOs keep the documented defaults (2000, 100, 6, 13) |
| `...Validation` | 22-row table: valid rows, NaN / +Inf / -Inf per field, zero and negative health/posture, negative delay/rate, precedence rows; then the cross-component rule: a record with bad posture stats stops `ConfigureEncounter`, a record with bad health or NaN rate stops `ConfigurePosture`, nothing written |
| `...HealthOverride` | 0.0001, 0.5, 1.0 -> named unsupported before any write, in both components, even with valid posture stats; first float above 1, 1.5, 2000, 123456.7 accepted and assigned unchanged (no clamp, round or substitute) |
| `...Rejections` | (revision 1: plus a destroyed-component block, 4 calls) wrong class (4 combinations incl. a plain `UActorComponent`), registered, component begun play (real `DispatchBeginPlay`, encounter gate radius 0 first as the existing fixture does), owner begun play, orphan component without an actor outer; each asserts the named token and an unchanged state; every unreachable precondition is an `AddError`, not a silent pass |

Same world set-up as the attach witness that already ran headless (CreateWorld + context + `InitializeActorsForPlay`), isolated native actors, no pack asset, no arena, no save.

## What this does NOT prove (stated in the code and the tests too)

Asynchronous pack health application and readback, `Posture.BeginPlay` seeding in a real duel, registration or BeginPlay chronology, a full playable bundle (two plans are not one), phase array mapping, anything about the coordinator, targets, reset, assets, config, scripts, package or the full gate. No synthetic test is called an arena duel.

## Next, when you release it

Build (no new UCLASS/USTRUCT; UHT still runs over the module), run only `OneBossFight.Binding.StatsAdapters`, then the full suite (expect 52 found) with raw logs, hashes and a before/after Source manifest, as for 2b. No build or automation has been run for this package.

---
## Verification addendum (X-243, 2026-10-27)

Accepted pins verified fresh (h cd1f6a0c, cpp b14a57ef, tests 46be817e; whole-Source manifest identical to the post-revision one; 9 of 9 dependency pins). Build exit 0. **First focused run failed** (`build_2026-10-27/failed_run1/`, kept): 4 of 5 passed, `Rejections` failed on an engine ensure because my test instantiated `UActorComponent`, which is abstract (ActorComponent.h line 127). Mechanical test-only fix (`build_2026-10-27/fix1.diff`): the unrelated wrong-class component is now `USceneComponent`; tests hash is now `be029a3a1f4fe0c7a30ba56c2962397775e9dcbde7be9e4927bb96a51c0d3745` (header and cpp unchanged). Focused re-run 5/5, full suite 52/52 (prior 47 all present, five new), 0 errors, 0 ensures, warnings identical after GUID/PID masking. Details and hashes: `TEST_PLAN.md` BUILD-12 and `build_2026-10-27/evidence_sha256.txt`. `Review/RPGBossStatsAdaptersTests.cpp` is now the fixed version (the pre-fix bytes are in `failed_run1/`).
