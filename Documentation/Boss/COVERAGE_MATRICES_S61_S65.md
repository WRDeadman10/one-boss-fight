# Queue C coverage matrices (S61–S65)

Read-only mapping of existing tests and proof artifacts. Presence of a unit test is not evidence of live actor integration. No test or engine execution in this audit.

## S62 — opt-in feature behavior coverage

| Profile group | Validation coverage | Pure/runtime-rule coverage | Behavior or live-evidence status |
|---|---|---|---|
| Selector tie, repeat penalty, combo graph | `RPGFrameworkRuntimeTests.cpp`: `SelectorProfile`, `SelectorTieProfile`, `ComboProfile` | `RPGBossMoveSelectorTests.cpp`; combo graph tests | Selector behavior has pure tests; framework selection is not proven by these profile-validation tests. |
| Guard chip, parry recovery/fair telegraph, parry posture/grade | `GuardChipProfile`, `ParryRecoveryProfile`, `ParryFairTelegraphProfile`, `PhaseSupersedesProfile` | `RPGBossBlockChipRulesTests.cpp`, parry/recovery rule tests | Live parry/stamina and overlay evidence is limited to C-715; insufficient-stamina refusal and boss reaction remain unproven. |
| Aggro/dodge history, fatigue, reaction delay, LOS | `AggroProfile`, `FatigueProfile`, `DodgeHistory`, `ReactionDelay`, `LosMemory` | `RPGBossAggroRulesTests.cpp`, `RPGBossFatigueRulesTests.cpp`, `RPGBossTrackRulesSweepTests.cpp` | C-715 proves fatigue to three whiffs and contact reset only; W3 stuck recovery remains live-unproven. Actor-level flask/LOS/dodge integration requires the dedicated proof lane. |
| Posture, phase, bleed, phase-pool starvation | `PostureProfile`, `PhaseProfile`, `BleedProfile`, `PhasePoolStarvation` | No dedicated posture-rule test file found in this scan; bleed property tests are `RPGBleedRulesPropertyTests.cpp` | Profile validation and bleed pure rules are covered; live transition, posture break, and bleed proc witnesses are separately tracked in KI/proof records. |
| Arena, center bias, reposition/turn latch, warp | `ArenaProfile`, `CenterBias`, `RepositionProfile`, `TurnLatch`, `BoundedWarp` | `RPGBossArenaEdgeRulesTests.cpp`, `RPGBossTrackRulesSweepTests.cpp`, `RPGBossWarpCurveRulesTests.cpp` | Pure math coverage does not prove nav projection/path behavior. Center-bias live proof is in its feature sheet; warp boundary concerns remain in S50 audit. |
| Anti-cheese, phase supersedes stagger, hyperarmor | `AntiCheeseProfile`, `PhaseSupersedesProfile`, `HyperArmor` | `RPGBossAggroRulesTests.cpp` and their dedicated policy headers/tests | Profile acceptance is distinct from actor decision/use coverage; no blanket live proof implied. |
| Required assets and core movement/damage | `ProfileDomains`, `ProfileValidationFuzz`, `ResolvedDependencies`, `PlaybackGuards`, `DamageProfile`, `BakedSamplesValidation` | framework resolver/executor and card tests | Validation/resolution tests exist; actual animation/nav/damage playback evidence is the separate BUILD/PIE lane. |

**Coverage conclusion:** profile tests frequently assert acceptance/refusal, while paired pure-rule tests cover deterministic policy. They do not establish runtime wiring for every opt-in field. Validation-only or partially integrated groups include feature-specific profile switch fields with no matching dedicated `*Profile` test (for example `ConeHysteresisDegrees`, `NeutralStrafeSeconds`, `bRangeBandPartition`, and several authored geometry/animation options); behavior-level evidence must be checked in the relevant live proof sheet or remains a gap. This matrix is a source/test-name inventory, not a claim that every test asserts all boundaries.

## S61 — Q101–Q125 rule/test mapping

The header-only rules and corresponding tests are inventoried in `TASKS.md` Q101–Q125 and registered in `RPGFrameworkRuntimeTests.cpp` or dedicated `RPGBoss*RulesTests.cpp` files. Detailed assertion-to-boundary mapping is in progress; do not infer the existence of a rule test means its claimed property is fully covered.

## S63 — restart behavior coverage

| State category | Reset/lifetime behavior | Existing test evidence | Coverage result |
|---|---|---|---|
| Move model generation and open windows | `ResetGeneration(2)` closes an open window then aborts; old generation tokens reject; generation two can complete another loop. | `Tests/RPGBossEncounterLoopTests.cpp:80–125`; `Tests/RPGBossMoveModelTests.cpp:148–152` | Pure model reset ordering and stale-token path are asserted. |
| Selector repeat memory | `Selector.Reset()` is called before generation-two selection in the encounter-loop fixture. | `Tests/RPGBossEncounterLoopTests.cpp` | Reset is exercised, but per-field memory contents are not independently observed by that restart assertion. |
| Framework actor gameplay state | `RestartEncounter` clears terminal/move/selector/phase/posture/bleed and perception state; executor `Rearm` resets per-card state, but lifetime hit/damage counters remain lifetime totals. | Source crosswalk `Boss/REF_ENCOUNTER_RESET.md`; counter and field inventory `Boss/LIFECYCLE_AND_RESTART_AUDIT_S41_S45.md` | No actor-level `RestartEncounter` test found in the searched test tree; reset inventory is source reviewed, not behavior-tested as a whole. |
| Proof-hook sentinels | `ProofGStart`/`ProofIFStart` are not reset across generations despite per-encounter descriptions. | `Boss/LIFECYCLE_AND_RESTART_AUDIT_S41_S45.md` | Explicit regression-test candidate; test-only hook state does not affect gameplay. |
| Immutable/session fields and inactive transient caches | Profile dependencies remain session immutable; inactive combo/F11 state is overwritten or cleared on next use; `bFailed` is sticky and restart disallowed. | `Boss/LIFECYCLE_AND_RESTART_AUDIT_S41_S45.md` | Source-backed reason they do not need generation reset under current use; not every member has a direct reset test. |

**Conclusion:** current restart tests prove model-level window closure, abort ordering, generation monotonicity, stale-token refusal, and a new generation loop. They do not prove the full native actor reset path or every member disposition. The proof-hook sentinel and `CARD_END` lifetime-scope caveats remain explicit.

## S64 — opt-in disabled-gate negative controls

| Feature gate | Existing disabled/off control | What it proves | Gap |
|---|---|---|---|
| Posture | `RPGFrameworkRuntimeTests.cpp:274–283` accepts all-zero posture and rejects partial configs | Profile validator preserves explicit off contract | Does not compare actor behavior with enabled vs disabled posture. |
| Bleed | `RPGFrameworkRuntimeTests.cpp:293–306` accepts all-zero bleed and rejects partial configs | Profile validator preserves explicit off contract | Pure bleed rule tests cover invalid/no-op input; no live boss comparison here. |
| Center bias | `RPGBossTrackRulesSweepTests.cpp` and `RPGFrameworkRuntimeTests.cpp:478–503` exercise bias parameter/control values; test hook documents 0 as control (`rpg.BossProofCenterBias`) | Pure geometry control path is available | No paired nav-path test proving zero bias reproduces baseline. |
| Guard chip | `RPGBossBlockChipRulesTests.cpp:21–23` checks zero chip yields zero guarded damage across sampled inputs | Rule-level disabled endpoint is stable | Does not prove profile wiring/attribute side effects are absent in PIE. |
| Fatigue | `RPGBossFatigueRulesTests.cpp:20+` validates an invalid zero floor; `RPGFrameworkRuntimeTests.cpp:216–230` covers profile setup | Validator rejects malformed configuration | Zero/off behavior needs a direct baseline equivalence assertion; C-715 only proves enabled behavior. |
| Aggro/dodge, selector tie, reaction, LOS, reposition | Dedicated rule tests cover neutral/default inputs (`RPGBossAggroRulesTests.cpp`, `RPGBossMoveSelectorTests.cpp`, `RPGBossTrackRulesSweepTests.cpp`); profile tests cover zero/off encodings | Some pure policy defaults have negative controls | No single integration control suite pairs each opt-in profile with its feature disabled. |

**Conclusion:** validator-off tests and pure-rule baseline inputs exist for several groups, but they are not equivalent to behavior-level negative controls. No all-groups paired control suite was found; retain a documented gap rather than treating default values or successful validation as proof of unchanged gameplay.

## S65

Scanned all `*.cpp` under `Source/OneBossFight` using the registration macro plus quoted canonical-name pattern. The test-folder README identifies `OneBossFight.*` as the usual project prefix.

| Result | Count |
|---|---:|
| Registrations parsed | 328 |
| Unique canonical names | 328 |
| Duplicate canonical names | 0 |
| Names outside `OneBossFight.*` | 0 |

This is a source registration scan, not proof that Unreal discovers or executes every registration. Regex extraction can miss macro forms with nonliteral/dynamically assembled names; no such form was identified by the scan.

## S66 — test isolation and cleanup

World-based tests commonly own their temporary `UWorld`, context, and actors in fixture/scope cleanup: examples include `RPGAutomationTests.cpp:73–83`, `RPGBossActivationTests.cpp:65–76`, and `RPGBossWorldInputCompilerTests.cpp:133–164`. Actor-spawn listeners and subsystem ticker cleanup are primarily production lifecycle responsibilities, audited in S41–S56; no test fixture registration leak was confirmed in this sampled scan. `RPGCombatCatalogTests.cpp:341–348` saves and restores console-variable values, including `ECVF_SetByCode` provenance. This is a sample-based audit, not a verified exhaustive fixture-by-fixture inventory; static/global hooks and early-return paths remain a review limit.

## S67 — CVar mutation provenance

`RPGCombatCatalogTests.cpp:332–350` is the only mutating CVar fixture found by searching test code for `Set`, `SetByCode`, and saved CVar values. Its scope restores the prior string value on destruction, including early returns, but restores with `ECVF_SetByCode` rather than the original priority/source. Thus value restoration is explicit; priority/provenance restoration is not. No priority mutation was identified in the remaining matches, which read registered values or check startup defaults. Candidate is isolated to this fixture and is documented, not changed in this audit.

## S68 — asset-backed test context

Asset/file-dependent registrations found in this scan use `EditorContext`: e.g. `RPGBuildTests.cpp` `Build.Assets` (`:387`), `RPGBossPunishTests.cpp` `PackMontages`, `RPGBossAuthoredDraftPreflightTests.cpp` (`:94`), registry/preparation tests (`RPGBossPreparationRegistryTests.cpp`, `RPGBossProductionPreparationTests.cpp`), and world input/preparation tests. Their service use includes `LoadClass`, `FPackageName::DoesPackageExist`, and object lookup. No asset-backed registration flagged only for `EngineFilter` or a non-editor application context was found in the searched files. This is a repository-source scan; execution in a packaged target was not evaluated.

## S69 — asynchronous test completion

No latent automation commands or latent enqueue APIs were found in `Source/OneBossFight/Tests`. Thread-pool concurrency tests use `Async(...).Get()` and therefore join before leaving the test, including activation, preparation abort, registry reservation/release, and world-input compilation (`RPGBossActivationTests.cpp:336`; `RPGBossHydrationPreparationTests.cpp:783–797`; `RPGBossPreparationRegistryTests.cpp:1025–1040`; `RPGBossWorldInputCompilerTests.cpp:1091`). This avoids dangling latent commands but `Get()` has no finite timeout: a deadlock could hang the automation worker indefinitely. Treat bounded-wait coverage as a test robustness gap, not as a known deadlock.

## S70 — property-test seed replay

Property/randomized tests found use fixed `FRandomStream` seeds, making failures replayable from source, e.g. bleed `0xB1EED`, automation policy sequence `7`, approach `0x94A11`, combo graph `0x51A7`, aim `0x97A11`, strafe `0x90A11`, yaw probe `0x96A11`, and framework profile fuzz `0x91A11`. Failures generally do not print the seed in the assertion text; reproduction requires locating the hard-coded seed or rerunning the same test revision. No unseeded `FMath::Rand*` use was found in property tests. Improvement candidate: include seed and case index in fuzz/property failure diagnostics.

## S71 — strict-comparison adjacent values

Typed adjacent-value fixtures exist for several sensitive strict gates: parry window/cooldown and damage-scaler window edges use `std::nextafter` (`RPGParryAdjacentWindowBoundaryTests.cpp`, `RPGParryCooldownAdjacentBoundaryTests.cpp`, `RPGDamageScalerWindowBoundaryMutationTests.cpp`, `RPGDamageScalerReciprocalBoundaryTests.cpp`, `RPGDamageScalerLowerWindowBoundaryTests.cpp`). Gap-closer strict exit uses exact equality and decimal `+0.001` (`RPGBossGapCloserExitBoundaryMutationTests.cpp:11–15`), not adjacent representable values. No exhaustive inventory proves every strict float comparison has an independent adjacent-value fixture; coverage is targeted.

## S72 — interval endpoint coverage

- Parry active interval is explicitly half-open: test asserts just-before-close and exact close plus just-after-close (`RPGParryAdjacentWindowBoundaryTests.cpp:15–24`); cooldown rejection immediately before ready time is separately covered (`RPGParryCooldownAdjacentBoundaryTests.cpp`).
- Cue hold tests assert sampled values remain in closed `[min,max]`, fixed `min=max`, and reject inverted/out-of-domain/non-finite windows (`RPGBossCueTests.cpp:18–33`). This is sampled seeded coverage plus a degenerate equality case, not exact generated min/max attainment.
- Some move-card/profile ranges use open or closed endpoints with individual tests, but the audit did not find one common interval fixture for every authored field. The S51 inventory already records equality coverage as incomplete; keep per-feature proof limits explicit.

## S73 — monotonic property assertion ordering

`RPGBossEnrageRulesTests.cpp` previously compared the damage scale with its prior sample but checked speed only against its fixed `[1, max]` range, despite the assertion claiming both are monotone. Updated the fixture to track `PreviousSpeed` and assert `S >= PreviousSpeed`; this makes a decreasing-speed counterexample fail the named assertion. Difficulty and repeat-penalty tests already compare each sample to the previous sample. No test was run; Lead owns suite execution.

## S74 — saturation/floor/cap cases

Tests explicitly check representative endpoints/caps: desperation at zero health reaches configured max (`RPGBossDesperationRulesTests.cpp:12`); arena-edge pressure saturates at wall and remains clamped outside (`RPGBossArenaEdgeRulesTests.cpp:13–14`); reactive dodge and recovery clamp to configured maxima (`RPGBossReactiveDodgeRulesTests.cpp:12`, `RPGBossRecoveryWindowRulesTests.cpp:13`); stamina pressure caps at empty stamina (`RPGBossStaminaPressureRulesTests.cpp:10`); punish-use and stuck-recovery caps refuse further use (`RPGBossPunishLimiterRulesTests.cpp:11`, `RPGBossStuckRecoveryRulesTests.cpp:11`). The S73 enrage sweep checks bounded range and monotonic steps, but only asserts exact configured saturation for damage, not speed. General below/at/above coverage is not complete across all clamp functions; treat missing exact endpoint assertions as targeted gaps, not evidence of wrong clamp behavior.

## S75 — arithmetic overflow paths

The new bounded policy rules commonly cap inputs before arithmetic: `RPGBossPoiseRegen::Rate` limits base/delay/ramp to 1e6 and scale to 3, while `RPGBossDifficulty::Evaluate` caps output scales via config validation. Their tests cover non-finite values and configured caps, but not largest finite representable operands.

Concrete source risk: `RPGBleedRules::Apply` accepts any finite nonnegative `State.Procs` up to `INT32_MAX`, then performs `++State.Procs` on a proc (`RPGBleedRules.h:68`); signed overflow can wrap negative, after which later calls fail the `State.Procs < 0` validation. No test initializes `Procs` near `INT32_MAX`. Amount addition can overflow to +Inf for very large finite buildup/amount, but the immediate threshold-crossing path resets buildup to zero; no non-finite residual was demonstrated. This is an extreme-state counter risk, not a normal combat reachability claim. Existing test only checks NaN amount (`RPGBleedRulesPropertyTests.cpp:29–30`).

### S61 detailed rule/test matrix

| Queue rule | Test file | Assertions inspected (scope, not exhaustive claim) |
|---|---|---|
| Q101 Enrage | `RPGBossEnrageRulesTests.cpp` | pre-fight baseline, midpoint, configured cap, bounded monotonic sweep (speed comparison corrected under S73). |
| Q102 Pattern detect | `RPGBossPatternDetectRulesTests.cpp` | sequence progression/reset and bounded consecutive count. |
| Q103 Arena edge | `RPGBossArenaEdgeRulesTests.cpp` | interior zero, half-margin midpoint, wall maximum, outside clamp, inward vector. |
| Q104 Reactive dodge | `RPGBossReactiveDodgeRulesTests.cpp` | increase with recent hits, configured chance cap, invalid roll/config refusal. |
| Q105 Desperation | `RPGBossDesperationRulesTests.cpp` | above/at threshold baseline, midpoint ramp, zero-health cap, invalid inputs; separate full-threshold mutation fixture. |
| Q106 Combo abort | `RPGBossComboAbortRulesTests.cpp` | active first-hit parry aborts; no-active/already-hit/non-parry controls. |
| Q107 Hit stop | `RPGBossHitStopRulesTests.cpp` | grade scaling and configured duration bounds. |
| Q108 Difficulty | `RPGBossDifficultyRulesTests.cpp` | normalized endpoints, per-step monotonic scales, invalid input neutral; equal-endpoint mutation fixture. |
| Q109 Music intensity | `RPGBossMusicIntensityRulesTests.cpp` | health/phase intensity mapping and bounds. |
| Q110 Turn ramp | `RPGBossApproachTests.cpp` | ramp start/end, clamp, partition/sweep behavior. |
| Q111 Warp curves | `RPGBossWarpCurveRulesTests.cpp` | endpoints for each curve, midpoint, overshoot above 1 then return. |
| Q112 Cue jitter | `RPGBossCueJitterRulesTests.cpp` | 1000 seeded samples within safe interval, exact repeatability for seed/index, invalid interval refusal. |
| Q113 Repeat decay | `RPGBossRepeatPenaltyRulesTests.cpp` | bounded non-increasing weights, zero-repeat baseline, zero-factor and invalid controls. |
| Q114 Stamina pressure | `RPGBossStaminaPressureRulesTests.cpp` | full/threshold/half/empty endpoints, monotonic sweep as stamina falls, invalid controls. |
| Q115 Punish budget | `RPGBossPunishLimiterRulesTests.cpp` | use reaches cap, next use and over-cap record refuse, reset/availability policy. |
| Q116 Gap closer | `RPGBossGapCloserRulesTests.cpp` | hysteresis enter/exit, invalid range; separate strict-exit boundary mutation fixture. |
| Q117 Threat retreat | `RPGBossRetreatRulesTests.cpp` | range/threat gates and inclusive threat threshold; separate strict-close boundary fixture. |
| Q118 Feint | `RPGBossFeintRulesTests.cpp` | reaction-to-chance endpoints, direction, out-of-band clamp, invalid config; separate max-chance boundary fixture. |
| Q119 Stagger resistance | `RPGBossStaggerResistRulesTests.cpp` | phase defaults, explicit values, unknown-phase neutral and invalid-scale fallback. |
| Q120 Poise regeneration | `RPGBossPoiseRegenRulesTests.cpp` | pre-delay zero, ramp and cap, invalid elapsed/config; separate zero-ramp mutation fixture. |
| Q121 Parry feedback | `RPGBossParryFeedbackRulesTests.cpp` | only first parry emits; already-emitted and non-parry controls; false/already mutation fixture. |
| Q122 Strafe resume | `RPGBossStrafeResumeRulesTests.cpp` | one restart only, interruption required, exhausted/non-finite budget; negative-budget mutation fixture. |
| Q123 Bake freshness | `RPGBossBakeFreshnessRulesTests.cpp` | matching nonzero fingerprints fresh; changed/missing fingerprints stale/unknown. |
| Q124 Presentation | `RPGBossPresentationRulesTests.cpp` | one-shot death/phase presentation gating and repeat suppression. |
| Q125 Stuck recovery | `RPGBossStuckRecoveryRulesTests.cpp` | blocked-only, one-time, bounded attempt; cap-eight mutation fixture. |

All 25 tasks have a dedicated registered rule test or directly named companion fixture in the test tree. This links each claim to tests but does not prove compilation on current HEAD (Lead owns suite execution). Boundary variants are called out where found; general property labels should not be read as exhaustive proof of every branch.

## S76 — assertion tautology/duplicate scan

Static regex scan of automation assertions found no literal same-variable `TestEqual(x,x)` or direct self-equality assertion. Repeated pure-rule calls are generally controls with changed inputs; e.g. the enrage midpoint/control and gap-closer boundary pairs have different times/ranges, and the cue-jitter identical-input pair intentionally verifies deterministic replay. No confirmed tautology was found in the scanned assertion forms. Macro-generated assertions and semantically equivalent-but-different expressions remain outside regex proof.

## S77 — test loop bounds

The test-tree `while` loops found are bounded by explicit limits or finite inputs: bleed threshold simulation uses `Hits < 50` (`RPGAutomationTests.cpp:621`); regex enumeration advances over loaded file contents (`:1285`); exact-duration warp advances by a positive member of a fixed `Dt` set toward `.4` seconds (`RPGBossWarpExactDurationBoundaryTests.cpp:12–25`). Other data-sized loops use arrays/strings built by bounded fixtures, and randomized sweeps use literal maxima (e.g. 1000/10000). No empty/constant condition or unbounded test loop was found in this scan; the warp loop relies on positive-step arithmetic rather than an explicit iteration cap.

## S78 — test name/outcome parity

In the Q101–Q125 sample, no registration name asserts runtime wiring or broader integration than the helper-level assertions. Two generic names obscure their actual coverage: `OneBossFight.Framework.Enrage.Rules` could be `...Enrage.BoundedMonotonicScales`; `...Difficulty.Rules` could be `...Difficulty.NormalizedScales`. Assertion text is more precise than those canonical names. These are naming suggestions only; registrations were not renamed because names are external automation identifiers.

## S79 — assertion diagnostic quality

Two high-sample property assertions have accurate relations but generic messages that omit the failing input/sample: `RPGBossEnrageRulesTests.cpp:13` checks `T`, damage, speed, and previous values but emits only “damage and speed stay bounded and monotone”; `RPGBossDifficultyRulesTests.cpp:13` checks the normalized difficulty index and three scales but emits only “three difficulty scales are monotonic and bounded.” A failure would not print the index or current/previous values. Proposed improvement: use `FString::Printf` to include T/I and values. Boundary fixtures generally have more specific labels such as “exact close instant is excluded.” No diagnostic edits made in S79.

## S80 — test file organization

Dedicated Q101–Q125 rule headers generally have paired `RPGBoss*RulesTests.cpp` files in `Tests/`, matching feature ownership. Two established files are overloaded relative to that pattern: `RPGFrameworkRuntimeTests.cpp` has 41 registrations across 842 lines (profile validation plus many unrelated helper/runtime contracts); `RPGAutomationTests.cpp` has 19 registrations across 1208 lines (broad historical gameplay/pack checks). Keep as organization candidates; no tests were moved or split. Large asset/preflight suites (`RPGBossHydrationPreflightTests.cpp`, 9 registrations/1274 lines; `RPGBossWorldPreparationTests.cpp`, 4/894) are cohesive around their subject and not necessarily misgrouped.

## S81–S85 — restart and attachment follow-up tests

- **S81 counter scope:** added `counter_delta()` to `Scripts/Tools/framework_results.py` and a pure fixture in `Scripts/Tools/test_queue_c_tools.py` showing lifetime totals (3→5 accepted hits, 4→6 attacks) produce per-interval deltas (2,2); first RESULT has no prior delta. Not run.
- **S82 proof-hook restart boundary:** no focused native actor fixture for private `ProofGStart`/`ProofIFStart` persistence found. The code/audit confirms these test-only sentinels persist across generations; recreating actor lifecycle in a helper test would only test a duplicate model, so this remains an explicit test gap rather than adding a disconnected helper.
- **S83 stale generation callback:** existing `RPGBossMoveModelTests.cpp:147–151` already verifies an old callback cannot abort the new attack, reset rejects the old generation token, delayed old tick emits no event, and current token remains live. No redundant test added.
- **S84 failed tag removal retry:** `URPGIFrameMonitor::OnEncounterReset` retains `bTag`/`bOwnedNow` when `RemoveTag` fails (`Player/RPGIFrameMonitor.cpp:146–155`), and stale-tag tick path documents retry (`:268–280`). No narrow fake-removal seam/test found; EndPlay still drops local ownership after failed removal (S41). Add a test only with an injectable reflected-call seam, not a detached state-only mirror.
- **S85 duplicate component attachment:** existing `RPGPlayerMovesAttachWitnessTests.cpp` W1/W2 observes spawn attachment followed by world-begin on the same pawn and asserts no new objects/component identity changes (`:388–407`). This already exercises duplicate prevention for spawn-then-world-begin; no second test added.

## S86–S90 — callback, restart, selector, and combo test review

- **S86 timer owner teardown:** director's delayed Niagara lambda captures only `TWeakObjectPtr<UNiagaraSystem>`, `TWeakObjectPtr<UWorld>`, and a copied location, then checks effect/world validity before spawn (`Boss/RPGSevarogDirector.cpp:78–88`). Owner invalidation cannot be tested from a pure unit without a world/timer fixture; no callback-lifetime test found. This delayed VFX is cosmetic and does not dereference the director.
- **S87 delayed VFX schedule:** no pure scheduling policy abstraction exists. Current expected rule is explicit in the callback: spawn if weak effect and world remain valid, independent of director lifetime; cancel-by-owner is not implemented. No new helper test added because it would duplicate the lambda predicate without exercising the timer.
- **S88 restart partition:** S63 crosswalk identifies immutable profile/session dependencies, reset generation/card state, and actor-lifetime counters; `RPGBossEncounterLoopTests.cpp` covers model generation reset and monotonic instance IDs, but no test asserts one representative from every actor partition together. Existing source crosswalk remains the evidence; no extra model-only duplicate test added.
- **S89 selector start snapshot:** existing `RPGBossEncounterLoopTests.cpp:68,111` starts generation-one and generation-two selected cards using the same snapshot passed to Select; selector and model paths remain aligned in this fixture. It does not vary cone/range after selection, so cone/range mutation parity remains a gap.
- **S90 combo fresh-snapshot fallback:** added `Source/OneBossFight/Tests/RPGBossComboFallbackTests.cpp` as an engine-free model/selector test. On a fresh gate snapshot outside the combo card's cone, `Model.Start` refuses with `MoveModel.Cone`; the ordinary selector then chooses and starts a different eligible card using that same snapshot. This exercises the pure fallback decision, not the actor/executor integration path. Not run by Codex.

## S91–S100 — follow-up tests and source audit

- **S91 cooldown starvation:** `RPGFrameworkRuntimeTests.cpp:261–281` covers a small 1–8 attack/card matrix; positive cooldown pools starve iff cards are fewer than attacks, and a zero-cooldown filler prevents starvation. Not run.
- **S92 CVar restoration:** `RPGCombatCatalogTests.cpp:332–357,378–403` captures/restores both string and set-by flags and checks success and early-return scope exits. Lead's explicit `uint32` cast is present. Not run.
- **S93 profile isolation:** `RPGFrameworkRuntimeTests.cpp:77–87` mutates one profile and verifies a second new instance remains at defaults. This is not asset serialization coverage. Not run.
- **S94 MoveCard defaults:** `RPGBossMoveCardTests.cpp:208–220` checks zero/default construction for opt-in fields; it does not deserialize an old asset with absent fields. Not run.
- **S95 malformed telemetry:** `test_validate_framework_proof_logs.py` rejects NaN, positive/negative Infinity, `inf`, and text in numeric guard-chip/fatigue fields, plus existing malformed integer cases. Not run.
- **S96 parser event order:** `test_validate_framework_proof_logs.py` asserts source-order semantic findings for duplicate playback instance IDs and backward timestamp lines, retaining line numbers and raw lines. Current validator has no explicit start/end lifecycle state machine; this is not full lifecycle validation. Not run.
- **S97 expected-sheet control:** `Scripts/Tools/test_queue_c_tools.py` adds an enabled `los_resume` report pass and a control `combo_start` leak failure with diagnostic assertion. Not run.
- **S98 evidence manifest mutation:** the same tool test verifies a valid fixture manifest, mutates `run.log`, then checks size/hash mismatches name the original relative file. Not run.
- **S99 coupled profile groups:** source/test review found representative accepted off/coherent states and refused partial states for phase, posture, bleed, fatigue, reaction delay, reposition, stagger clips, and punish settings. No missing group case identified in this scope; no test added.
- **S100 Shipping guard:** `Scripts/Tools/test_queue_c_tools.py` statically checks all discovered `rpg.BossProof*` C++ console registrations are enclosed by a non-Shipping guard. This does not inspect a Shipping binary. Not run.

## S113–S117 and C-727 follow-ups

- **S113 strafe-stuck telemetry:** `STRAFE_STUCK_EXPECTED.md` now requires a `strafe_stuck flipped=1` event only after at least 0.3 s with `movedRatio < 0.5`, exactly one flip per uninterrupted window, and a later `strafe_step dir` opposite the seeded unflipped `DirectionAt` value at that logged elapsed time. The interior control must end through `strafe_end reason=CandidateEligible` with no stuck token. This remains an expected-sheet requirement; no live witness was run.
- **C-727 combo fallback follow-up:** `RPGBossComboFallbackTests.cpp` adds pure model/selector coverage for a fresh-snapshot combo-card refusal and a different eligible ordinary fallback. It does not exercise the boss actor/executor integration. Not run by Codex.
- **S114 reposition proof audit:** `REPOSITION_PROOF_AUDIT_S114.md` ties the MOV profile's band/speed/timeout and turn-rate settings to retained readback, then separates successful walk-to-band evidence from the incomplete in-band turn trace. The run has `reposition_turn start` and a subsequent eligible candidate but no source-emitted `reposition_turn_end`; its archived command relies on mutable `F4/current_map.txt`. No new runtime run.
- **S115 arena leash controls:** `ARENA_LEASH_EXPECTED_S115.md` fixes the baseline `(0,0)`, radius 250 cm, outside point `(0,500)`, and return point `(0,100)` with exact abort/center/resume/playback signals. Existing evidence covers outside-to-inside recovery; it lacks a separate inside-only control and 250 cm boundary check. No new runtime run.
- **S116 center-bias feasibility:** `CENTER_BIAS_FEASIBILITY_AUDIT_S116.md` hand-calculates the 125 cm requested band-midpoint destinations: bias 1 points `(125,0)`, bias 0 points `(-75,100)`, a +200 cm center-axis difference. Existing A/B endpoints align with that geometry within nav projection and arrival tolerance; no new runtime run.
- **S117 LOS memory:** `LOS_MEMORY_EXPECTED_S117.md` defines the blocked/lost/search/regain/resume sequence, separate 3 s timeout run, and visible negative control. Retained runs cover loss, regain, and timeout; actual movement toward the last-known point needs a labeled manual observation, and no visible control is retained.
- **S119 anti-cheese proof:** `ANTICHEESE_PROOF_EXPECTED_S119.md` specifies the kite threshold/streak controls and identifies the retained PHS005 log's score crossover. The retained profile proves kite only; hug remains unconfigured, and a strict same-snapshot A/B plus hug proof are specified. Static review only.
- **S120 tie-band proof:** `TIE_BAND_SEED_PROOF_EXPECTED_S120.md` specifies paired 12345/54321 seeds, the exact top-tier threshold and exclusions, reproducibility, and TieBand=0/narrow-band controls. Existing engine-free test covers the selector sequence; no retained PIE tie-band run was found.
- **S121 RESULT grader review:** `RESULT_GENERATION_GRADER_REVIEW_S121.md` documents current parser/delta semantics and proposes a separate opt-in generation segment checker with unknown legacy attribution, explicit boundary checks, and fixture matrix. No authoritative parser change.
- **S126 proof-report paired control:** `proof_report.py --control-log` evaluates required tokens against the enabled log and checklist `no TOKEN` assertions against the paired control log; absent flag preserves old single-log behavior. Added a fixture for clean control PASS and a control-only token leak FAIL. Not run by Codex.
- **S127 proof-report citations:** PASS/FAIL/MANUAL now print the supplied expected-sheet path and checklist line, replacing the generic `expected.md` label. Fixture asserts the failing control check points to the exact sheet and line; not run by Codex.
- **S128 proof-report artifact identity:** output now prints the resolved input log path, UTC mtime, and streamed SHA-256. Fixture checks timestamp and exact digest; not run by Codex.
- **S129 PIE identity check:** optional expected map/profile/run ID compares against recognized identity fields in the log, reports absent values as UNKNOWN, and prints mismatches before checklist rows; a mismatched profile fixture fails despite passing telemetry. Existing retained PIE logs often omit those fields, so this is opt-in and does not infer identity from a command manifest.
- **S130 PIE completeness:** opt-in `--require-complete-run` requires a FrameworkProof RESULT before `LogExit: Exiting.`; missing result/shutdown marker or reversed ordering returns INCOMPLETE (2), distinct from gameplay checklist FAIL. Added fixtures for absent RESULT and truncated shutdown. Log closure is only a process-log marker, not a substitute for the launcher's OS exit code. Not run by Codex.
- **S131 decision/candidate trace relations:** existing validator tests already include valid trace-before-decision pairs, mismatched seq, unselected cycles, and intervening unselected cycle followed by mismatch (`test_validate_framework_proof_logs.py:365–447`). This validates ordering/seq consistency only, not whether a candidate should win. Existing coverage satisfies the fixture request; no code change or test run.
- **S132 telemetry relation format:** `TELEMETRY_RELATION_FORMAT_S132.md` proposes strict JSON relations for equality, closed range, ratio, and monotonic checks, with pass/fail/error fixtures and fail-closed rules for unsupported syntax, missing/nonfinite samples, and invalid denominators. Proposal only; no evaluator implemented.
- **S133 schema sample bundle:** extended `token_coverage.py --samples-output` and generated `FRAMEWORK_SCHEMA_SAMPLE_BUNDLE_S133.json` from 995 retained logs. Current validator has 138 schemas: 133 have first real sample path/line; five (`attack_row_refused`, `pending_hit_refused`, `strafe_budget_exhausted`, `strafe_budget_restarted`, `strafe_stuck`) are explicitly `no_real_sample`. No synthetic sample was substituted.
- **S134 failure catalogue cross-check:** verified listed telemetry tokens are registered and emitted by the cited paths. Corrected the WarpEaseInOut diagnostic: `playback_start` has no card/map/profile identity, so an authoring readback or manifest is needed; `telegraph_scale` identifies card only under its separate opt-in. Finding and correction in `FAILURE_CATALOGUE_TELEMETRY_AUDIT_S134.md`.
- **S135 profile refusal audit:** added exact `[FrameworkProof] ERROR token=...` and fixture-profile refusal mappings with source-backed setup corrections to `FAILURE_MODE_CATALOGUE.md`. Notes that `Framework.Profile.Domain` is shared/ambiguous and that ValidateProfile may return before actor ERROR telemetry; absence of ERROR is not a pass.
- **S136 RESULT vocabulary:** current source emits four outcomes (`CompletedWithDamage`, `CompletedAllParried`, `CompletedTelemetryOnly`, `BossDefeated`), all observed in retained logs. Schema/parser require nonempty strings but accept unknowns as opaque data; this is forward-compatible parsing, not a semantic pass. See `RESULT_OUTCOME_VOCABULARY_AUDIT_S136.md`.
- **S137 duplicate PIE chunks:** added `detect_duplicate_pie_runs.py`; it splits on Unreal engine-start markers, hashes each raw chunk, and reports repeated identical chunks with original line ranges. Fixture verifies duplicate-boundary detection and preserved line numbers. No test run by Codex.
- **S138 evidence summary table:** added `evidence_summary.py` and generated `FRAMEWORK_EVIDENCE_SUMMARY_S138.csv`, one row per 581 retained `editor_raw.log` files with path, map/profile (unknown when absent), first timestamp, last RESULT, schema/semantic status, and digest. Counts: 564 validator PASS, 17 semantic warnings; 222 logs lack a RESULT. Inventory generation only; no tests.
- **S139 PIE command manifest audit:** added `audit_pie_command.py` to compare `command.json` against a structured `command-requirements` block in the expected sheet; reports missing args/inline CVars and unlisted executable/mutation arguments. Explicitly does not claim CVars applied inside referenced Python drivers are captured by command.json. No test run.
- **S140 asset provenance check:** added `asset_provenance.py` and reviewed PHS005 authoring/evidence. It identifies generated profile `/Game/OneBossFight/FrameworkProof/DA_Sevarog_AntiCheese_PHS005` and map `/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofPHS005`; no source profile/map is declared (reported unknown), while content readback and save lines corroborate destinations. Report is read-only.
