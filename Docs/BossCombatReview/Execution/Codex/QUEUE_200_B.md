# Codex queue B: 200 bounded tasks R1 to R200 (lead Claude, 2026-11-03; rolling queue, owner order)

Posted at the review of batch 39 of QUEUE_200.md. Start R1 at once when QUEUE_200 batch 40 is done. Same rules as the top of QUEUE_200.md (no commit, no build, no engine; one X- finish message per 5 tasks; no waiting; read my verdict on the previous batch first and fix HOTFIX items; every OK has a file:line; opt-in default off; epsilon in the RULE; monotonic checks start from the opposite extreme; fresh profile object for F3 negative cases; grep the declaration of every helper before you call it (member vs free function), a build error costs a whole review round; evaluate a claimed rule property at one point by hand before you post it).

SLOW-DOWN PHASE (lead decision): enough behaviour exists to prove in the editor. This queue adds almost no new behaviour: proof scripts, audits, test quality, docs, tools, clean-up. I run the editor proofs; you prepare them. Do not wire any Part D rule of QUEUE_200 unless a task below says so.

## Part A: live-proof preparation (offline; you write scripts and checklists, I run the editor)
Pattern for each feature: (1) an editor Python script `Docs/BossCombatReview/Execution/Codex/Proofs/make_<feature>_profile.py` modelled on the existing create/enable scripts in Claude/B_* (look at B_CODEX_W1/enable_grade_scale.py and B_PARRY scripts), creating a profile data asset copy with ONLY that setting on and a proof map copy; (2) `<feature>_EXPECTED.md`: the exact log tokens and numeric relations a PASS must show, and what a FAIL looks like; (3) a validator invocation line.
### B1 to B4 (R1 to R20)
| R | Feature | Acceptance |
|---|---|---|
| 1-2 | WarpEaseInOut | script + EXPECTED (warp_ease on=1, total distance equals linear) |
| 3-4 | Strafe stuck recovery | script (force a blocked strafe by geometry) + EXPECTED (strafe_stuck flipped=1) |
| 5-6 | Yaw probe + cone hysteresis | script + EXPECTED (yaw_probe samples around the cone edge, zero flicker with hysteresis, flicker without) |
| 7-8 | Guard chip | script + EXPECTED (guard_chip incoming/applied relation) |
| 9-10 | Parry recovery | script + EXPECTED (parry_recovery extra by grade) |
| 11-12 | Telegraph fair scale | script + EXPECTED (telegraph_scale rate, montage rate restored) |
| 13-14 | Aggro switch | script + EXPECTED (aggro_switch after repeated dodges) |
| 15-16 | Fatigue | script + EXPECTED (fatigue whiffs/scale after N whiffs) |
| 17-18 | Parry stamina | EXPECTED only (player-side, needs the pack stamina attribute names, list the exact ones from source) |
| 19-20 | Overlay parry line | EXPECTED only (how to see it, which flag) |
### B5 to B6 (R21 to R30): one combined proof driver
| 21-25 | `Proofs/drive_opt_in_features.py` plan: a single PIE driver sequence that exercises features in an order that does not interfere (document the order and why), written against the existing drive_pie.py API | no engine run by you; I review the plan |
| 26-30 | Failure-mode catalogue | for each feature the 3 most likely live failure causes and the log line that shows each |

## Part B: test-suite quality audit (read-only, report file:line)
### B7 to B14 (R31 to R70)
| 31-35 | Tests that cannot fail | list every test in Tests/*.cpp whose only assertions are TestTrue(true-ish constants) or compare a value with itself; each with file:line |
| 36-40 | Tests with duplicate assertions or dead loops | |
| 41-45 | Tests that read global state (console variables, statics) and could be order dependent | |
| 46-50 | Tests whose boundary values are built from subtraction (epsilon lesson) | list with proposed fix |
| 51-55 | Tests that call real engine services (file system, assets) | which need the editor context |
| 56-60 | Coverage matrix: rule header -> test file -> number of assertions | table in Documentation/Boss/TEST_COVERAGE.md |
| 61-65 | Rule headers without a dedicated test | list |
| 66-70 | Mutation thought experiment: for 10 rules name one comparison operator whose flip no test would catch | file:line, propose the test |

## Part C: new tests from those findings (new files only)
### B15 to B19 (R71 to R95)
| 71-95 | One test file per finding of Part B (up to 25), each failing before the fix is imagined | fresh tests, no existing test edited |

## Part D: documentation
### B20 to B25 (R96 to R125)
| 96-100 | One-page designer reference for each of the 25 Part D rules of QUEUE_200 (5 tasks of 5 rules) | Documentation/Boss/RULES_REFERENCE_*.md with every parameter, unit, default, failure return |
| 101-105 | How-to: add a new opt-in profile field (the exact 8 steps: header, validation token, validator schema, test, doc, log token, reset paths, TEST_HOOKS) | from the guard chip / parry recovery diffs |
| 106-110 | How-to: write a new pure rule and its tests (with the 5 build mistakes of this project as a checklist) | |
| 111-115 | How-to: run the full suite, read the log, keep evidence (commands from real runs) | |
| 116-120 | Troubleshooting guide: every failure seen in this project (resolution too low, Git Bash path mangling, stale logs, editor crash on duplicated map, missing manifest hash) with the fix | from memory notes in Documentation/PROJECT_STATE.md and KNOWN_ISSUES.md |
| 121-125 | Release-readiness checklist for a boss profile (what must be proven live before shipping a card) | |

## Part E: tools and scripts (offline)
### B26 to B31 (R126 to R155)
| 126-130 | `suite_log_report.py`: summarize an automation log (pass/fail, slowest tests, duplicate names) | tested on three real logs |
| 131-135 | `diff_suite_logs.py`: two logs, new/removed/changed tests | |
| 136-140 | `check_validator_tokens.py`: every UE_LOG token in Source has a schema and a LOG_TOKENS.md row (keeps itself in sync) | |
| 141-145 | `new_rule_scaffold.py`: generates header + test + doc skeleton following the project style | tested by generating into a temp dir |
| 146-150 | `new_profile_field_scaffold.py`: prints the 8 edit sites for a profile field | |
| 151-155 | `proof_report.py`: from a PIE log and an EXPECTED.md produce PASS/FAIL per expected line | |

## Part F: cross-cutting audits (read-only)
### B32 to B36 (R156 to R180)
| 156-160 | Every `if (X>0.f)` opt-in gate in the profile: default value, validation, reset on Rearm, log, schema, doc (a matrix) | find any missing cell |
| 161-165 | Every state variable of ARPGFrameworkBossCharacter: where set, where reset (Rearm/Die/Fail/EndPlay) | matrix, list the unreset ones |
| 166-170 | Every state variable of URPGFrameworkMoveExecutor, same matrix | |
| 171-175 | Every tag add/remove pair (Status.*) across Source | which path can leave a tag set |
| 176-180 | Every timer / delegate registration and its removal | |

## Part G: clean-up proposals (read-only, no edits)
### B37 to B38 (R181 to R190)
| 181-185 | Dead code candidates with file:line and the grep proving no callers | |
| 186-190 | Naming and comment style drift across Player/ (list, no changes) | |

## Part H: closing
### B39 to B40 (R191 to R200)
| 191-195 | Documentation consistency: TASKS / PROJECT_STATE / TEST_PLAN / KNOWN_ISSUES / DECISIONS after both queues | list and fix numbers |
| 196-198 | Handover note for a fresh session (read order, commands, state of every opt-in feature: coded / unit-tested / live-proven) | one page |
| 199 | Queue C proposal: 200 tasks you think matter next, ranked, each with scope and acceptance | I choose |
| 200 | Final consistency pass | |

Verdict log (lead): `B<n>: ACCEPTED | HOTFIX (items), message id`
