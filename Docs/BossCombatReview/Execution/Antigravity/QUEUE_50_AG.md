# Antigravity queue: 50 bounded offline tasks (lead Claude, 2026-11-02)

Rules for every task: offline lane only (no engine, no build, no Source/ edits unless a task says so). **NO commit and NO push**: the owner said on 2026-11-02 "Leave it uncommitted for now"; that stands until the owner or I say otherwise in a C- message. One A- finish message per BATCH of 5 (task ids, files, one line each, sha256 of every new file). **Do not wait for my review:** after a batch start the next 5 at once; at your next submission first read my verdict on the previous batch (ACCEPTED / HOTFIX) and fix HOTFIX items first. Silence is never a reason to stop; a named blocker goes in one line in an A- message, then take the next independent task. Audits report `file:line` and BUG / RISK / OK with a failing scenario for every BUG. Evidence rule: no pass without raw log or hash.

## Batch 1: ledger and status (evidence already exists, uncommitted tree stays as is)
| # | Task | Scope / files | Acceptance |
|---|---|---|---|
| 1 | Graduate AWR-004 | the 82-row ledger | PASS with evidence folder B_AWR004 and its sha256 file, cite the PIE log lines |
| 2 | Graduate COM-004 and HIT-008 | ledger | use Codex/COM004_HIT008_LEDGER_DRAFT.md, evidence B_GUARD and B_PARRY, say what stays PARTIAL |
| 3 | Graduate SEL-008 | ledger | evidence B_SEL008 (neutral strafe live, range constant, direction flip) |
| 4 | Graduate MOV-001 | ledger | evidence B_MOV001 (range bands live at 152/302/702 cm) |
| 5 | Recount the dashboard | TASKS.md dashboard numbers | 80 of 82 expected, QA-001 skipped and QA-005 dropped by owner decision, numbers recomputed from the ledger |

## Batch 2: validator and tools
| 6 | Run the validator over every B_* PIE log | validate_framework_proof_logs.py | table of log, verdict, first schema error; no change to Source |
| 7 | Evidence manifest audit | every evidence_sha256.txt in Claude/B_* | recompute hashes, list mismatches and missing files |
| 8 | Validator negative tests | test_validate_framework_proof_logs.py | one malformed line per schema family is rejected (new tests only) |
| 9 | Log diff helper review | Scripts/Tools/*.py written by Codex | verdicts BUG/RISK/OK per script, run each once |
| 10 | Mailbox id gaps | Scripts/Tools/check_mailbox_ids.py output | explain each skipped id or mark unknown, no edits to the mailbox |

## Batch 3: audits of existing offline material (read-only)
| 11 | Audit Documentation/TEST_PLAN.md | BUILD-145 to BUILD-156 | every line matches an evidence folder; list mismatches |
| 12 | Audit Documentation/DECISIONS.md new entries | guard, hysteresis, parry, range bands, strafe | each decision has a reason and an owner decision cite |
| 13 | Audit KNOWN_ISSUES.md | open KIs | status vs evidence, list stale ones |
| 14 | Audit Documentation/Boss/*.md written by Codex | NEW_CARD_HOWTO, PROOF_WORKFLOW, TEST_HOOKS, LOG_TOKENS, OPEN_ISSUES_DIGEST | every command and field checked against source, list errors |
| 15 | Audit PARRY_HOWTO.md and RANGE_BANDS_AND_STRAFE_HOWTO.md | | commands and numbers checked against evidence |

## Batch 4: content audits (Content/ read via existing Python audit scripts, no editor launch)
| 16 | Inventory FrameworkProof profiles and maps | Content/OneBossFight/FrameworkProof | table asset, referenced by, purpose; unreferenced assets listed |
| 17 | Card audit | the 8 Sevarog cards and 2 new MOV001 cards | field table with units, flag values that look off |
| 18 | Pack asset edit register | the two combat styles changed for parry | before/after hashes from B_PARRY, document the edit and how to undo it |
| 19 | Reference mapping | Documentation/Boss Morgott 82 rows | which rows the framework now covers, from the ledger |
| 20 | Gap list | rows still PARTIAL | one line per row: what proof is missing |

## Batch 5: designer documentation
| 21 | Quickstart: make a new card in 10 steps | Documentation/Boss/ | based on NEW_CARD_HOWTO and a real card, commands verified |
| 22 | Quickstart: make a new boss profile | Documentation/Boss/ | from DA_Sevarog_* assets |
| 23 | Parry tuning guide | from PARRY_HOWTO and J6 fairness numbers | designer knobs, safe ranges, what each log line means |
| 24 | Range band tuning guide | MOV-001 | worked example with the three arenas |
| 25 | Glossary | all log tokens and ids used in the mailbox | one page |

## Batch 6 to 10: reserve (I will refine with you as batches complete)
| 26-30 | More audits of docs vs source (second pass) | | same acceptance as batch 3 |
| 31-35 | Blender / art tasks: only on owner H-13 permission (art via Blender MCP is authorised): player parry visual sketch, boss telegraph decal sketch | content only, no import without my order | preview images, no engine import |
| 36-40 | Validator v2 (D1 protocol v2): schema versioning, field types, strict unknown-token mode | validate_framework_proof_logs.py | backwards compatible, tests |
| 41-45 | D2: evidence packager | script that builds an evidence folder with raw log, hash file, pre/post state from a run | tested on B_SEL008 |
| 46-49 | Final consistency passes of TASKS.md, PROJECT_STATE.md, TEST_PLAN.md after batches 1 to 45 | | numbers and statuses match |
| 50 | Handover note | one page for a new session | state, commands, gotchas |

Notes: Codex works in parallel on a separate queue; do not edit files she is writing (Source/, Scripts/Tools/). Tell me in the A- message if two tasks touch the same file.
