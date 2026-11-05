# Codex queue: 50 bounded tasks (lead Claude, 2026-11-02)

Rules for every task: no owner decision needed, no commit, no build (Claude builds, runs the suite and reviews). One X- finish message per BATCH of 5 (task ids, files, one line each); a rejected item comes back as a HOTFIX that you fix at once and resend. Audits report `file:line` and a verdict (BUG / RISK / OK) with a failing scenario for every BUG. Writes: opt-in, default off, no behaviour change when the setting is 0; pure rules get a test file; new files only unless listed. Pure-rule tests: never assert an exact decimal boundary built from subtraction, put an epsilon in the RULE (BUILD-153 lesson).

## Batch 1: finish the wiring (W2 to W5)
| # | Task | Scope / files | Acceptance |
|---|---|---|---|
| 1 | W2 `WarpEaseInOut` | RPGBossMoveCard.h/.cpp (spec bool, default false), RPGFrameworkMoveExecutor.cpp TickWarp, uses RPGBossApproach::StepCm | total warp distance unchanged, budget checks kept, log `warp_ease on=1` + validator schema + test line |
| 2 | W3 strafe stuck recovery | RPGFrameworkBossCharacter.cpp strafe block, RPGBossStuckRules.h | `strafe_stuck flipped=1 movedRatio=%g` schema + test line |
| 3 | W4 `rpg.BossProofYawProbe` | RPGFrameworkBossCharacter.cpp (#if !UE_BUILD_SHIPPING), RPGBossYawProbeRules.h | `yaw_probe sample=%d yaw=%g` schema + test line |
| 4 | W5 docs | KNOWN_ISSUES.md stale workaround texts (KI-149/153/154), TEST_PLAN.md one BUILD-155 line for W2..W4 | statuses unchanged |
| 5 | Validator completeness | validate_framework_proof_logs.py + its test | every `[FrameworkProof] <token>` UE_LOG in Source has a schema (re-run your J10 audit after W2..W4), count assertion updated |

## Batch 2: bug-hunt audits, boss core (read-only)
| # | Task | Scope / files | Acceptance |
|---|---|---|---|
| 6 | Audit RPGFrameworkMoveExecutor.cpp | whole file | every early return releases lock, montage and window state (leak list), verdicts |
| 7 | Audit RPGFrameworkBossCharacter.cpp Tick | decision, reposition, strafe, stagger, phase hold paths | state variables not reset on Fail, Die or Rearm; verdicts |
| 8 | Audit RPGBossMoveSelector.h/.cpp | selection, cooldown, repeat memory, cone memory | determinism with seed, NaN, empty candidates, memory growth |
| 9 | Audit RPGBossMoveCard.h/.cpp | validation rules vs the executor use of each field | a field the executor reads that validation does not check |
| 10 | Audit RPGBossMoveModel.cpp | state machine transitions | an illegal transition reachable from a late or duplicate event |

## Batch 3: audits, player side and resolver (read-only)
| # | Task | Scope / files | Acceptance |
|---|---|---|---|
| 11 | Audit RPGDamageResolver.cpp | every outcome path, Spent keys, generation | a path that spends a key on a rejection, or not on an accept |
| 12 | Audit RPGHitIntake.cpp | pack hit to boss path, attack row, pending hits | a hit lost or applied twice around phase change or death |
| 13 | Audit RPGSwingTracker.cpp | swing counters, stamina extra, hyperarmor | counters not reset on interrupt; ability class lookups |
| 14 | Audit RPGDodgeTiming.cpp + RPGIFrameMonitor.cpp | tag add and remove balance | a path that leaves Status.Invulnerable set |
| 15 | Audit RPGPlayerParry.cpp | tag add and remove balance, EndPlay, cooldown, input rebind | a path that leaves Status.ParryActive set; double bind |

## Batch 4: audits, encounter and old path (read-only)
| # | Task | Scope / files | Acceptance |
|---|---|---|---|
| 16 | Audit RPGBossEncounter.cpp + RPGBossDormantWake*.* | wake, reset, dormant | a restart that leaves boss or player state stale |
| 17 | Audit RPGBossPhases.cpp + RPGBossPhase*Adapters.* | phase transition, hold | a transition during stagger or death |
| 18 | Audit RPGBossStagger.cpp + RPGBossPosture.cpp | break, regen, stagger end | posture negative or above max; stagger never ends |
| 19 | Audit RPGBossBleed.cpp + RPGBleedRules.h | buildup, proc, reset | proc double fire; negative buildup |
| 20 | Audit RPGBossDeath.cpp + RPGBossRemains.cpp | death flow | double death; timers surviving a restart |

## Batch 5: audits, UI, pack glue, tests (read-only)
| # | Task | Scope / files | Acceptance |
|---|---|---|---|
| 21 | Audit RPGBossHud.cpp + RPGFlaskHud.cpp | widget lifetime, nulls | a widget used after destroy; per-tick allocation |
| 22 | Audit RPGBlueprintCall.h + RPGPackReflect.h | reflection helpers | unchecked UFunction or property null; param size mismatch |
| 23 | Audit RPGPackNotifies.cpp | ChargeToTarget and friends | division by zero; stale weak pointers |
| 24 | Audit RPGBuildLoadout.cpp | build switch, ability grants | a build switch that drops an ability or double-grants |
| 25 | Test-suite audit | Source/OneBossFight/Tests/*.cpp | tests that cannot fail (no assertion on the outcome), duplicate names, order dependence |

## Batch 6: test hardening (new test files, pure rules only)
| # | Task | Scope / files | Acceptance |
|---|---|---|---|
| 26 | RPGBossTrackRules sweep tests | Tests/RPGBossTrackRulesSweepTests.cpp | StepYaw, Warp, Grab and Ring over a 360 x range grid: no NaN, monotonic where claimed |
| 27 | RPGBossCueRules sweep | Tests/RPGBossCueSweepTests.cpp | HoldSeconds in range for 10000 seeds, DistinctChannels symmetric |
| 28 | RPGBossPunishRules sweep | Tests/RPGBossPunishSweepTests.cpp | margins monotonic in recovery and distance |
| 29 | RPGBossDefenseRules sweep | Tests/RPGBossDefenseSweepTests.cpp | boundary table with epsilon-safe values |
| 30 | RPGBossComboRules property test | Tests/RPGBossComboPropertyTests.cpp | random graphs (seeded) never loop, Step never returns an unreachable node |

## Batch 7: more pure rules (new files + tests; each opt-in and unwired, Claude wires)
| # | Task | Scope / files | Acceptance |
|---|---|---|---|
| 31 | `RPGBossRecoveryWindowRules.h` | punish window after a parried hit | window = f(grade, card recovery), clamps, tests |
| 32 | `RPGBossBlockChipRules.h` | chip damage fraction while the player blocks | Guarded hit damage scale in [0,1], fail closed |
| 33 | `RPGBossTelegraphScaleRules.h` | scale a card telegraph so ParryableOk passes, clamp to a max slowdown | returns rate or refuses, tests with the real numbers of the 8 existing cards |
| 34 | `RPGBossAggroRules.h` | switch of preferred range band by player behaviour | pure state machine, hysteresis, tests |
| 35 | `RPGBossFatigueRules.h` | boss attack rate falls after N whiffs | monotonic, bounded, tests |

## Batch 8: tools and scripts (offline)
| # | Task | Scope / files | Acceptance |
|---|---|---|---|
| 36 | Log summary tool | Scripts/Tools/summarize_framework_log.py | prints per-run counts of every token, decisions, parried, guarded and accepted hits; test with real logs |
| 37 | Evidence hash checker | Scripts/Tools/check_evidence_sha256.py | verifies every evidence_sha256.txt in Docs/BossCombatReview/Execution/Claude/B_* against the files; prints mismatches |
| 38 | Run compare helper | Scripts/Tools/compare_parry_runs.py | compares two PIE logs on RESULT, hits, parries; ignores timestamps |
| 39 | Docs link checker | Scripts/Tools/check_doc_links.py | finds broken relative links in Documentation/*.md |
| 40 | Mailbox id audit | Scripts/Tools/check_mailbox_ids.py | duplicate or skipped C-, X-, A- ids in TEAM_MAILBOX.md |

## Batch 9: documentation
| # | Task | Scope / files | Acceptance |
|---|---|---|---|
| 41 | Designer guide: new card | Documentation/Boss/NEW_CARD_HOWTO.md (facts from MoveCard fields and the C1 how-to) | every spec field with unit and rule |
| 42 | Designer guide: proof workflow | Documentation/Boss/PROOF_WORKFLOW.md (PIE driver, hooks, validator, evidence hashes) | commands copied from real runs |
| 43 | Test-hook reference | Documentation/Boss/TEST_HOOKS.md (every rpg.* console variable under !UE_BUILD_SHIPPING with meaning and default) | grep-complete |
| 44 | Log token reference | Documentation/Boss/LOG_TOKENS.md (every token, fields, where logged) | matches the validator schemas |
| 45 | KNOWN_ISSUES digest | Documentation/Boss/OPEN_ISSUES_DIGEST.md (open issues by area with the proof each needs) | no invented facts |

## Batch 10: wiring and verification helpers (existing files allowed as listed, opt-in)
| # | Task | Scope / files | Acceptance |
|---|---|---|---|
| 46 | Parry stamina wiring | RPGPlayerParry.* + RPGParryCostRules.h: player setting `StaminaCost` (0 = off, default), reads and writes the pack stamina attribute via RPGPack helpers | no change when 0; log `parry_stamina before after parried` + schema |
| 47 | Overlay line for parry | RPGBossOverlayRules.h + overlay code: add parry window state and last grade | existing overlay tests unchanged, one new test |
| 48 | Resolver audit counters for Parried | RPGDamageResolver.cpp GetOutcomeCount names list | `DAMAGE accepted ... parried N` summary line extended, existing tests unchanged |
| 49 | Combo graph Parried edges sample | a NEW JSON sample + a pure test that loads its graph and asserts the Parried branch is reachable | no engine asset needed |
| 50 | Final consistency pass | TASKS.md, PROJECT_STATE.md, TEST_PLAN.md after tasks 1 to 49 | numbers and KI statuses match, list of mismatches fixed |
