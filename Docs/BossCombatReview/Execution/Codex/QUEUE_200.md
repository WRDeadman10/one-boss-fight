# Codex queue: 200 bounded tasks (lead Claude, 2026-11-02, owner order "post 200 tasks instead of 50")

This replaces the idea of QUEUE_50_B: finish QUEUE_50.md batch 10 first, then work this file in order (40 batches of 5, task ids 51 to 250 are NOT used: ids here are Q1 to Q200).

Rules for every task: no owner decision needed, no commit, no build, no engine (Claude builds, runs the suite and reviews). One X- finish message per BATCH of 5 (ids, files, one line each). **No waiting:** start the next 5 at once; at your next submission first read my verdict on the previous batch (ACCEPTED / HOTFIX) and fix HOTFIX items before new tasks. Silence is never a reason to stop; a named blocker goes in one line in an X- message, then take the next independent task. Audits report `file:line` and BUG / RISK / OK with a failing scenario for every BUG (a BUG you can fix in one small edit: fix it and say so). Writes: opt-in, default off, no behaviour change when the setting is 0; pure rules get a test file; new files only unless the task lists existing ones. Tests: never assert an exact decimal boundary built from subtraction (epsilon in the RULE); a monotonic check starts from the extreme on the OTHER side (lesson of Q-batch 6). Every new `[FrameworkProof]` token needs a validator schema + test line. Every new rpg.* hook needs a TEST_HOOKS.md line. Keep ids: the Q number goes in your X- message.

## Part A: wire the five unwired rules (opt-in profile fields, default 0 = no change)
### B1 Block chip (RPGBossBlockChipRules.h)
| Q | Task | Files | Acceptance |
|---|---|---|---|
| 1 | Profile field `GuardChipFraction` [0,1], 0 off | RPGBossFrameworkProfile.h/.cpp | token `Framework.Profile.GuardChip`, validation test |
| 2 | Apply to Guarded outcome | RPGFrameworkMoveExecutor.cpp | chip damage via the resolver path only; none at 0 |
| 3 | Log `guard_chip incoming=%g applied=%g` | executor | no log at 0 |
| 4 | Validator schema + sample + test | validate_framework_proof_logs.py + test | count assertion updated |
| 5 | Doc line in PARRY_HOWTO.md and TEST_PLAN | docs | statuses: unproven live |
### B2 Parry recovery window (RPGBossRecoveryWindowRules.h)
| 6 | Profile field `ParryRecoveryScale` [0,3], 0 off | profile | validation |
| 7 | Extend the boss recovery after a parried hit by the rule | RPGFrameworkBossCharacter.cpp / executor | no change at 0, state reset on Fail/Die/Rearm |
| 8 | Log `parry_recovery grade=%d extra=%g` | boss | schema |
| 9 | Test the wiring boundary as a pure function call | Tests | new test file |
| 10 | Audit your own change (lifetime, reset paths) | | verdicts |
### B3 Telegraph scale (RPGBossTelegraphScaleRules.h)
| 11 | Profile field `ParryFairTelegraph` bool + `ParryFairMinScale` | profile | validation |
| 12 | Card play-rate applied at StartCard | executor | rate restored at end/abort; none when off |
| 13 | Log `telegraph_scale card=%s rate=%g` | executor | schema |
| 14 | Pure test: eight real cards need which rates | Tests | table in the test |
| 15 | Audit rate restore on every exit path | executor | verdicts |
### B4 Aggro (RPGBossAggroRules.h)
| 16 | Profile fields for aggro thresholds, off by default | profile | validation |
| 17 | Feed player behaviour (distance, dodge rate) to the rule | boss Tick | no change off |
| 18 | Use the preferred band in selector context | selector/boss | determinism kept |
| 19 | Log `aggro_switch from=%d to=%d` + schema | boss + validator | |
| 20 | Audit: cannot flap, resets on Rearm | | verdicts |
### B5 Fatigue (RPGBossFatigueRules.h)
| 21 | Profile fields `FatigueGraceWhiffs`, `FatigueFloor`, off by default | profile | validation |
| 22 | Count whiffs (a card ended with no accepted/guarded/parried hit) | boss | reset on Rearm/phase change |
| 23 | Apply attack-rate scale to the card play rate | executor | composes with telegraph scale (document order) |
| 24 | Log `fatigue whiffs=%d scale=%g` + schema | | |
| 25 | Audit interaction of B3 + B5 rates | | verdicts |
### B6 Parry stamina and overlay (finish tasks 46 to 48 of QUEUE_50)
| 26 | Audit your stamina wiring in RPGPlayerParry.cpp | whole file | paths: press while open, refund on parry, EndPlay, attribute missing |
| 27 | Validator schema parry_stamina verified | validator | |
| 28 | Rule edge tests for RPGParryCostRules.h | Tests | NaN, negative, max stamina |
| 29 | Overlay parry line audit | overlay rules | |
| 30 | Doc: stamina in PARRY_HOWTO.md | docs | no invented numbers |

## Part B: audits of files not yet audited (read-only)
### B7 Arena
| 31 | RPGArenaDressing.cpp/.h | | leaks, per-tick work |
| 32 | RPGEmberField.cpp/.h | | |
| 33 | RPGFireSource.cpp/.h + RPGFogGate.cpp/.h | | fog gate state on reset |
| 34 | RPGGreyboxArena.cpp/.h | | |
| 35 | RPGPerfSwitches.cpp/.h | | every switch default and shipping guard |
### B8 Audio and benchmark
| 36 | RPGBossMusic.cpp/.h | | music state on death/reset |
| 37 | RPGArenaAmbience.cpp/.h | | |
| 38 | RPGFootsteps.cpp/.h | | |
| 39 | RPGBenchmarkRunner.cpp/.h | | shipping guard |
| 40 | RPGFrameStats.cpp/.h | | divide by zero, sample growth |
### B9 Framework boss support
| 41 | RPGFrameworkBossController.cpp/.h | | walk start/stop balance |
| 42 | RPGFrameworkProofFixture.cpp/.h | | |
| 43 | RPGSevarogDirector.cpp/.h | | |
| 44 | RPGBossFrameworkProfile.cpp | | every field validated; field read by code but not validated |
| 45 | RPGFrameworkMoveExecutor.cpp second pass | new code: parry, guard, warp ease | |
### B10 Camera and effects
| 46 | RPGCameraRig.cpp/.h | | |
| 47 | RPGCameraProbe.cpp/.h | | shipping guard |
| 48 | RPGCameraShakes.cpp/.h | | |
| 49 | RPGFlipbookEffect.cpp/.h | | actor lifetime |
| 50 | RPGLegend.cpp/.h | | |
### B11 Catalog and activation
| 51 | RPGCombatCatalog.cpp/.h + ABI | | |
| 52 | RPGBossActivation.cpp/.h | | fail-closed paths |
| 53 | RPGBossHydrationPreflight.cpp + Preparation | | |
| 54 | RPGBossPreparationRegistry.cpp | | |
| 55 | RPGBossWorldInputCompiler.cpp + WorldPreparation | | |
### B12 Adapters (typed record adapters)
| 56 | RPGBossBleedAdapters + RPGBossHealPunishAdapters | | |
| 57 | RPGBossCloseClipSwapAdapters + RPGBossDeathAdapters | | |
| 58 | RPGBossDormantWakeAdapters + RPGBossLookAdapters | | |
| 59 | RPGBossLowSweepAdapters + RPGBossShockwaveAdapters | | |
| 60 | RPGBossStatsAdapters + Phase*Adapters + Stagger*Adapters + Encounter*Adapters | | |
### B13 Remaining Player folder
| 61 | RPGAttackTracker.cpp | | |
| 62 | RPGBossInterrupt.cpp + RPGBossPunish.cpp | | |
| 63 | RPGBossJavelin.cpp + RPGBossLowSweep.cpp | | parried counter paths (compile only so far) |
| 64 | RPGBossShockwave.cpp + RPGBossHealPunish.cpp | | |
| 65 | RPGBossSweepSampling.cpp + RPGBossLook.cpp + RPGBossCloseClipSwap.cpp | | |
### B14 Remaining Player folder 2
| 66 | RPGCombatDebug.cpp | | shipping guard |
| 67 | RPGEncounterBinding.cpp | | |
| 68 | RPGRiposteInput.cpp | | |
| 69 | RPGStartupChronology.cpp + RPGTraceAudit.cpp + RPGTraceGuard.cpp | | |
| 70 | RPGWeaponAttackTable.cpp + RPGPlayerMovesSubsystem.cpp | | |
### B15 Pack glue and combat utils
| 71 | RPGPackTrace.cpp | | |
| 72 | RPGHideBones.cpp | | |
| 73 | RPGMontageUtils.cpp + RPGSkeletonUtils.cpp | | |
| 74 | RPGInputTestUtils.cpp | | |
| 75 | Scratch/RPGScratchRouteA.cpp | | is it dead code; list references |

## Part C: test hardening (new test files, pure rules)
### B16
| 76 | RPGBossRules.h sweep | | finite, monotonic where claimed |
| 77 | RPGSwingRules.h sweep | | |
| 78 | RPGTelegraphRules.h sweep | | |
| 79 | RPGDamageScale.h sweep | | |
| 80 | RPGBleedRules.h property test | | seeded random sequences never negative |
### B17
| 81 | RPGBossStaggerAnimRules.h sweep | | |
| 82 | RPGBossDormantWakeRules.h sweep | | |
| 83 | RPGBossCloseClipSwapRules.h table test | | |
| 84 | RPGBuildRules.h table test | | every row valid |
| 85 | RPGBossOverlayRules.h sweep | | |
### B18
| 86 | Selector property test: 10000 seeded decisions | | never picks an ineligible card |
| 87 | MoveModel random event storm | | no illegal transition |
| 88 | Damage Decide() exhaustive table | | every input combination, order proven |
| 89 | Parry rules random press schedule | | window/cooldown invariants |
| 90 | Strafe rules long-run test | | stays inside arena radius |
### B19
| 91 | Profile validation fuzz: random field values | | never crashes, only tokens |
| 92 | MoveCard validation fuzz | | |
| 93 | StuckRules sweep | | |
| 94 | ApproachRules sweep | | |
| 95 | ParryGradeRules sweep | | grades monotonic in time |
### B20
| 96 | YawProbe rules sweep | | |
| 97 | AimHysteresis rules long-run | | no flicker under noise |
| 98 | BlockChip rules sweep | | |
| 99 | RecoveryWindow rules sweep | | |
| 100 | TelegraphScale rules sweep | | |

## Part D: new pure rules (new files + tests; opt-in, unwired, I wire)
### B21
| 101 | `RPGBossEnrageRules.h` | | damage/speed scale over fight time, clamps |
| 102 | `RPGBossPatternDetectRules.h` | | player repeats the same dodge N times |
| 103 | `RPGBossArenaEdgeRules.h` | | avoid fighting with back to the wall |
| 104 | `RPGBossReactiveDodgeRules.h` | | chance to dodge a heavy attack by recent hits |
| 105 | `RPGBossDesperationRules.h` | | low-health behaviour weights |
### B22
| 106 | `RPGBossComboAbortRules.h` | | cancel a combo when the first hit is parried |
| 107 | `RPGBossHitStopRules.h` | | hit stop length by grade |
| 108 | `RPGBossDifficultyRules.h` | | one scalar to damage/speed/telegraph |
| 109 | `RPGBossMusicIntensityRules.h` | | intensity from health and phase |
| 110 | `RPGBossTurnRateRamp.h` | | turn speed ramp at card start |
### B23
| 111 | `RPGBossWarpCurveRules.h` | | linear/ease/overshoot curves with the same total distance |
| 112 | `RPGBossCueJitterRules.h` | | seeded timing jitter inside a safe band |
| 113 | `RPGBossRepeatPenaltyRules.h` | | weight falls with repeats |
| 114 | `RPGBossStaminaPressureRules.h` | | boss presses when the player stamina is low |
| 115 | `RPGBossPunishLimiterRules.h` | | cap the punish window uses per fight |
### B24
| 116 | `RPGBossGapCloserRules.h` | | when to close distance |
| 117 | `RPGBossRetreatRules.h` | | when to back off |
| 118 | `RPGBossFeintRules.h` | | feint chance by player reaction |
| 119 | `RPGBossStaggerResistRules.h` | | resistance by phase |
| 120 | `RPGBossPoiseRegenRules.h` | | regen scaling by time since hit |
### B25 (each: header + test + short doc paragraph)
| 121-125 | five more rules of your choice from NEXT_IDEAS.md | | not duplicates of existing rules |

## Part E: tools and scripts (offline, Scripts/Tools/)
### B26
| 126 | `summarize_framework_log.py` v2: per-card table | | tested on three real logs |
| 127 | `plot_framework_timeline.py`: text timeline of a PIE log | | no external libraries |
| 128 | `token_coverage.py`: tokens seen in all evidence logs vs schemas | | prints never-seen tokens |
| 129 | `source_metrics.py`: files, lines, tests per folder | | |
| 130 | `check_headers_selfcontained.py`: each header compiles alone? static include check | | list suspects only |
### B27
| 131 | `check_line_endings.py`: CRLF/LF mix per file | | |
| 132 | `check_shipping_guards.py`: every `rpg.` console variable and test hook inside `#if !UE_BUILD_SHIPPING` | | |
| 133 | `list_todo_markers.py` | | |
| 134 | `check_ki_references.py`: every KI-nnn cited in code exists in KNOWN_ISSUES.md | | |
| 135 | `check_test_plan_ids.py`: BUILD ids unique and sorted | | |
### B28
| 136 | `evidence_pack.py`: builds an evidence folder (raw log, hash file, pre/post state) | | tested on a temp copy |
| 137 | `diff_manifests.py`: compare two Source manifests | | |
| 138 | `profile_dump.py`: print a profile data asset as table from a JSON export | | |
| 139 | `card_table.py`: all cards' timing table from baked samples | | |
| 140 | `mailbox_stats.py`: messages per party per day | | |
### B29 to B30 (141-150)
| 141-150 | Ten more offline tools that remove manual steps you saw in this queue (each tested on real files, each with a one-line usage in Documentation/Boss/TOOLS.md) | | |

## Part F: documentation
### B31
| 151 | Boss component reference: Executor | Documentation/Boss/REF_EXECUTOR.md | states, locks, logs |
| 152 | Reference: Boss character | REF_BOSS_CHARACTER.md | Tick order, state variables |
| 153 | Reference: Selector and cone memory | REF_SELECTOR.md | |
| 154 | Reference: Damage resolver | REF_RESOLVER.md | outcomes and order |
| 155 | Reference: Player parry | REF_PLAYER_PARRY.md | |
### B32
| 156 | Reference: MoveCard fields v2 | | |
| 157 | Reference: Profile fields | REF_PROFILE.md | every field, unit, rule, token |
| 158 | Reference: Encounter and reset | | |
| 159 | Reference: Death and remains | | |
| 160 | Reference: Phases and stagger | | |
### B33
| 161 | Architecture overview with a mermaid diagram | ARCHITECTURE_OVERVIEW.md | |
| 162 | Data flow of one attack (decision to hit) | | |
| 163 | Data flow of one parry | | |
| 164 | FAQ for designers (10 questions, answers from source) | | |
| 165 | New agent onboarding page | | read order, commands, gotchas |
### B34
| 166-170 | Per-folder README for Arena, Audio, Benchmark, Pack, Combat | each folder doc | |
### B35
| 171-175 | Per-area README for Boss folder files, Tests folder (how tests are named/run), Scripts/Editor (what each script does), Scripts/Tools, Docs/BossCombatReview structure | | |

## Part G: cross-cutting audits (read-only, whole source)
### B36
| 176 | Threading and game-thread asserts | all | calls off the game thread |
| 177 | Weak pointer and UObject lifetime | all | raw pointers held across frames |
| 178 | Tick order and tick groups | components with ticks | dependencies on another component's tick |
| 179 | NaN and infinity entry points | all float inputs from assets | unguarded divisions |
| 180 | Console variable registration | all rpg.* | duplicate names, shipping guard |
### B37
| 181 | Log spam: per-tick logs | all UE_LOG in ticks | rate limit missing |
| 182 | UPROPERTY meta ClampMin/Max vs validation | profile/card | mismatches |
| 183 | Determinism: every use of random | all | unseeded random in logic |
| 184 | Config defaults vs code defaults | Config/*.ini | |
| 185 | Header include hygiene | all headers | heavy includes in headers |
### B38 (read-only Python editor scripts)
| 186 | Scripts/Editor scripts A to F | | hard-coded paths, idempotence |
| 187 | Scripts/Editor scripts G to N | | |
| 188 | Scripts/Editor scripts O to Z | | |
| 189 | Scripts/*.ps1 | | quoting, exit codes |
| 190 | Scripts/*.py (not Editor) | | |
### B39
| 191 | Documentation/*.md dead statements (claims no longer true) | | list with file:line |
| 192 | TASKS.md vs ledger vs TEST_PLAN consistency | | |
| 193 | DECISIONS.md contradictions | | |
| 194 | Mailbox: open orders never answered (C- without result) | | list |
| 195 | Test names vs files naming convention | | |
### B40
| 196 | Second pass on bug-dense files (RPGFrameworkBossCharacter.cpp) | | only NEW bugs |
| 197 | Second pass (RPGPlayerParry.cpp + RPGDamageResolver.cpp) | | |
| 198 | Second pass (RPGBossEncounter.cpp + RPGIFrameMonitor.cpp) | | |
| 199 | Second pass (RPGHitIntake.cpp + RPGBossMoveCard.cpp) | | |
| 200 | Final consistency pass: TASKS.md, PROJECT_STATE.md, TEST_PLAN.md, KNOWN_ISSUES.md | | numbers and statuses match |

Verdict log (lead, one line per batch): `B<n>: ACCEPTED | HOTFIX (items), message id`

Rolling rule (owner 2026-11-02): when the lead reviews batch B39, the next 200 tasks (QUEUE_200_B.md) are posted at once. The lead may slow behaviour work and shift to audits, tests and docs while proving features in the editor.
