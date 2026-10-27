# DD4 package 01: typed phase adapter, source and test delivery for review (NOT built, NOT run)

Order: X-244 / `Codex/DD4_PHASE_ADAPTER_PACKAGE_01.md`. Claim: C-194. Three NEW files, no existing live file changed (whole-Source manifest: exactly 3 added lines, 0 removed or changed; the 11 dependency pins in `pre_dependency_pins.txt` all verify).

| file | lines | sha256 (CRLF, 0 bare LF, 0 bare CR) |
|---|---|---|
| `Source/OneBossFight/Player/RPGBossPhaseAdapters.h` | 64 | `fab105d67f8d99c891e30b72a04a3404b2488c1d766efd148510037eff0cf4a6` |
| `Source/OneBossFight/Player/RPGBossPhaseAdapters.cpp` | 195 | `8140cd203feff0c3c72a3b0c3672c9d19761d9b3b88e617dd6949f75978edacf` |
| `Source/OneBossFight/Tests/RPGBossPhaseAdaptersTests.cpp` | 574 | `5099aa04ea22d28f11eb8eb05abc07c46a2a02a124f51339747661ffa8b0432a` |

Review copies of exactly these bytes: `Review/`. Nothing was compiled; engine APIs were checked against the engine headers and source (or were already compiled in the accepted stats package).

## What it does

Namespace `RPGBossPhaseAdapters`:

| function | job |
|---|---|
| `PhaseFieldPath(FName, Field)` | `Phases[<id>].<Field>` manifest path of one typed input |
| `ValidatePhases(const TArray<FRPGPhaseConfig>&, FName SelectedPhaseId, FString&)` | selection by id + the whole selected record, no component touched |
| `ConfigurePhases(UActorComponent&, const FRPGParticipantConfig&, FName SelectedPhaseId, FString&)` | the accepted lifecycle checks, then validation, then the write of four fields |
| `MakePhasePlan(FName SelectedPhaseId)` | `FRPGComponentPlan`, class `URPGBossPhases`, instance name `RPGBossPhases`, id captured BY VALUE (lambda), `RequiredFields` = the four `Phases[<id>].*` paths (empty when no id is selected, the callback then fails by name) |

Mapping: `EntryHealthFraction` -> `PhaseTwoHealthFraction`, `SpeedMultiplier` -> `MovementScale`, `RateMultiplier` -> `AttackRateScale`, `AttackMultiplier` -> `DamageScale`. Typed record only, never `FRPGParityField.Value`. Writes only those four public fields; transition seconds, clips and roar, immunity effect, leap lock, fireball settings (disabled default), ability prefix and every runtime cache/state untouched (the state struct in the tests covers all of them, including the three soft asset paths). Creates, registers, begins and triggers nothing; no pack attribute, timer or phase trigger. An isolated phase plan is stated in the header to be NOT a valid complete cluster.

## Check order (all before the single write block), named by leading token

| # | check | token |
|---|---|---|
| 1 | component alive and not being destroyed (accepted `InvalidComponent` rule) | `InvalidComponent` |
| 2 | exact class `URPGBossPhases` | `WrongComponentClass` |
| 3 | component not begun | `ComponentBegunPlay` |
| 4 | component not registered | `ComponentAlreadyRegistered` |
| 5 | owner valid, not being destroyed | `InvalidOwner` |
| 6 | owner not begun / beginning | `OwnerBegunPlay` |
| 7 | an id was selected | `InvalidPhase.NoSelection` |
| 8 | the config has at least one record | `InvalidPhase.NoRecords` |
| 9 | exactly one record carries the id (none) | `InvalidPhase.NotFound` |
| 10 | one transition only: no extra record, no duplicate id | `UnsupportedNativePhaseSet` |
| 11 | all four finite | `InvalidPhase.NotFinite` |
| 12 | threshold > 0 and <= 1 | `InvalidPhase.ThresholdOutOfRange` |
| 13 | speed, rate, attack > 0 (no rule that a multiplier is >= 1) | `InvalidPhase.NotPositive` |
| 14 | float inverse of speed and of rate finite (native reset divides by them) | `UnsupportedNativeInverse` |
| 15 | attack multiplier >= `NativeDamageScaleFloor` (1) | `UnsupportedNativeDamageScale` |

Generic validity (11 to 13) precedes the native capability checks (14, 15), so an invalid record is reported as invalid and not as unsupported. Selection is by id only: a single record with another id is `NotFound`, never "the first", so first/last/index 0 cannot be selected by accident. A longer set is refused by name even when the selected id is in it.

## Judgement calls I made (please confirm or change)

1. **DAMAGE FACTOR BELOW 1 (the one that needs your decision).** I refuse `AttackMultiplier < 1` as `UnsupportedNativeDamageScale`. Reason, from the code (RPGBossPhases.cpp 368 and 390) and Step2Preparation/14: apply writes `AppliedAttack = Attack*(DamageScale-1)` (negative below 1) and the native reset subtracts it only `if (AppliedAttack > 0)`, so a factor below 1 is applied and never reversed; exactly 1 changes nothing and is valid. Your order says fractional factors are valid "where the native arithmetic supports them", and doc 14 asked for an explicit decision; I read the reset guard as the arithmetic not supporting it. If you want it accepted (a scalar-only domain, documenting the asymmetry), it is one constant (`NativeDamageScaleFloor`, header) and two test rows (the `0.5` and the first-float-below-1 rows in `Validation`). Fractional SPEED and RATE factors below 1 are valid when the inverse is finite, as ordered.
2. **Inverse check** is `IsFinite(1.f / x)` on the typed float, for speed and rate. It does not prove the real ability or movement round trip and does not rule out downstream overflow (your wording); it only refuses a value whose reversal arithmetic is already non-finite.
3. **Order of selection checks:** not-found before the set-capability check, so "this id is not in the config" is never reported as "unsupported set".
4. **Plan with no selected id** has empty `RequiredFields` and its callback fails by name (`InvalidPhase.NoSelection`), instead of the factory asserting or inventing an id.
5. **The lifecycle check is duplicated privately** in this cpp (same tokens, same order as the accepted stats adapters) because the stats adapter files must not change. A later shared helper is possible and is not part of this package.
6. **Not exercised:** an owner that is being destroyed (in the code, no test builds that state). The finite-inverse tests use the float `denorm_min` (inverse overflows) and the smallest normal float (inverse finite); both outcomes are deterministic on x64 whether or not denormals are flushed (a flushed denormal gives an infinite inverse too).

## Tests (5 new automation tests, expected discovered count 52 -> 57 once built)

| test | covers |
|---|---|
| `OneBossFight.Binding.PhaseAdapters.Assign` | non-default values (0.35, 1.5, 1.75, 2.0) through the plan callback; plan class/name/RequiredFields with the selected id; id captured by value (the caller's variable is changed after the plan is made); no-id plan has no required fields; only the four fields changed, all other configuration (incl. soft asset paths, fireball default off) and runtime state equal; unregistered, owner not begun, owner gained no component; direct helper with another id and fractional speed/rate |
| `...Selection` | no id, zero records, mismatched id with one record (not "the first"), extra transition selecting first and selecting last, duplicate id, id missing from a longer set; each via `ValidatePhases`, `ConfigurePhases` and the plan callback, same token each time, state unchanged; a control record then works on the same component |
| `...Validation` | 33-row table: valid rows incl. threshold exactly 1, damage exactly 1, fractional speed/rate, large finite values, smallest-normal inverse; NaN / +Inf / -Inf per field; threshold 0, negative, above 1, first float above 1; zero and negative multipliers; denormal speed and rate; damage 0.5 and the first float below 1; four precedence rows; every invalid row also run through `ConfigurePhases` with a full before/after state comparison; a valid record still configures afterwards |
| `...Isolation` | two owners, two ids, two plans: configuring B leaves A equal, a plan is bound to its id (the other config is `NotFound`), later config change changes nothing, a refused third component and the CDO keep 0.6 / 1.2 / 1.2 / 1.25 |
| `...Rejections` | wrong class with concrete classes (a posture component, a scene component; no abstract class), registered, component begun (real `DispatchBeginPlay`, three soft asset references cleared first so nothing loads), owner begun, orphan without an actor owner, destroyed (and destroyed wrong-class: `InvalidComponent` outranks the class check); each asserts the token and unchanged state; unreachable preconditions are `AddError` |

Retained allocated objects, no GC, no freed-memory assertion. Same headless world set-up the stats and witness tests already ran.

## What this does NOT prove

A phase transition, the effective movement speed, attack rate or damage, a reset, a duel, the real ability-rate or attribute round trip, nor any wiring (coordinator, association, reset, legacy suppression). It proves typed assignment of one selected phase and the rejection paths on isolated native components. No tuning, no default substitution, no pack readback.

## Next, when you release it

Build (no new UCLASS/USTRUCT), run only `OneBossFight.Binding.PhaseAdapters`, then the full suite (expect 57 found, the prior 52 present), with raw logs, hashes and manifests, as for the stats package. No build or automation has been run for this package.
