# Queue P — data-route parity, hardening and reference work (50 tasks)

Written by the lead (Claude), 2026-11-05, after BUILD-217 (first live data-route startup + respawn rebind, suite 460/460).
Rules: C-797 (50 tasks, 5-task batches, one X- per batch or per Source change, rolling: at P45 write QUEUE_Q), C-820 (no re-check
queues; "WAITING ON LEAD: <item>" then backlog), C-829 (a lead HOTFIX outranks everything), C-819 build lessons, C-791 UE Python lessons.
A task is DONE only with an executing test, a tool run with counts, a lead-run live result, or a measured artifact. "LEAD-RUN" tasks
are prepared by Codex (script + EXPECTED sheet + exact command) and run by the lead.

## P01–P15 A5 parity: legacy route vs selected data route (same fights both ways)
| ID | Task | Acceptance |
|---|---|---|
| P01 | Parity driver plan: list registered drivers that can take the optional `H019_ENCOUNTER_DEFINITION` env switch (unset = unchanged) | table: driver, map, compared observables, expected identical/differing fields |
| P02 | Capture bridge: smallest supported Python path to call `URPGPlayerMovesSubsystem::BuildEncounterParitySnapshot()` in PIE (get_game_world + subsystem class); one read-only probe script | LEAD-RUN probe prints the snapshot JSON line in a selected run |
| P03 | Add the env switch to `pie_a4_low_sweep.py` (A4 low sweep) | AST ok; unset path byte-identical behaviour; LEAD-RUN both arms |
| P04 | Add the env switch to `pie_dormant_wake.py` | same |
| P05 | Add the env switch to `pie_damage_path.py` | same |
| P06 | Add the env switch to `pie_player_death_reset.py` | same |
| P07 | Add the env switch to `pie_telegraph.py` | same |
| P08 | Add the env switch to `pie_boss_hud.py` | same |
| P09 | Receipt writer: driver emits a v2 parity receipt (route, selection, identities, terminal outcome, observables) from the P02 snapshot + its own checks | `compare_encounter_parity.py` accepts a real pair from P03 |
| P10 | LEAD-RUN package: P03 pair (legacy + selected) with EXPECTED sheet | comparator PASS or a listed mismatch |
| P11 | LEAD-RUN package: P04 + P05 pairs | same |
| P12 | LEAD-RUN package: P06 + P07 + P08 pairs | same |
| P13 | Mismatch triage doc for every parity difference found (cause: data value, missing component, timing, expected difference) | each mismatch has a cause + proposed fix or "intended" |
| P14 | Fixes for real parity mismatches (one PRODUCTION CHANGE per root cause, test first) | test shows the defect, then passes; suite green |
| P15 | Parity summary for the owner decision on A7 (retire legacy): what is identical, what differs, residual risk | one page, no owner email (lead presents it) |

## P16–P25 A6 hardcoded boss values into data (bit-identical defaults, C-801 rule)
| ID | Task | Acceptance |
|---|---|---|
| P16 | Fresh inventory of literal boss numbers still in Source outside typed records (grep + classify gameplay / safety / schema) | table with file:line; diff vs the A6 audit |
| P17 | Batch 1: move up to 5 gameplay literals into existing typed records, defaults equal to the literal, same formula | default-equals-literal test per value; suite green |
| P18 | Batch 2 (next 5) | same |
| P19 | Batch 3 (next 5) | same |
| P20 | Receipt/readback: G044 receipt lists the new fields with native-default provenance | validator PASS on a rewritten receipt (LEAD-RUN step 2/3) |
| P21 | Designer guide update for the new fields | doc links resolve |
| P22 | Validator rules for the new fields (domain, finiteness, ordering) | executing tests incl. NaN/inf/adjacent values |
| P23 | Record what stays in code (formulas, safety, CPU bounds) with reasons | KI/decision rows |
| P24 | C1 New Boss tool: emits the new fields (default values) | C1 dry-run output contains them (offline test) |
| P25 | A6 status line in TASKS (count moved / kept / remaining) | numbers match P16–P19 |

## P26–P35 Tools and pipeline hardening (real defects only)
| ID | Task | Acceptance |
|---|---|---|
| P26 | Shared UE Python helper module for editor scripts (ue_path, struct to JSON via export_text names, Array handling, GUID text, class compare) from the BUILD-214 fixes | used by the 4 G044 scripts; offline mocks updated to the real API shapes |
| P27 | Replace the per-script copies with the helper; rerun G044 step 1 + 5 (LEAD-RUN, read-only) | both PASS, no Content change |
| P28 | Mock fidelity: every mock of an engine type in Scripts/Tools tests mirrors only API seen live; list and fix divergences (SoftObjectPath, Array, Guid, UClass) | tests updated; list in the doc |
| P29 | C2 Validate Boss: AnimBlueprint compile receipt verified live with `C2_EDITOR_LOG_PATH` set to the abslog (LEAD-RUN) | receipt shows the new [Compiler] lines or none |
| P30 | C3 New Weapon: second weapon dry-run with a fresh config (no apply) to prove the fail-closed checks on a non-Polearm style | dry-run PASS, written=[] |
| P31 | run_editor_script.ps1: refuse when an evidence folder already exists (prevents the overwritten-evidence case of 2026-11-04) | parse ok + offline test |
| P32 | Evidence hashing helper used by all lead run scripts (one function, relative paths) | used in a new run; hashes verify |
| P33 | TEST_PLAN: collapse BUILD-183..217 notes into a short index table (keep the details below) | links resolve |
| P34 | KNOWN_ISSUES sweep: close rows fixed by BUILD-183..217 with evidence links | each closed row cites a BUILD id |
| P35 | Owner cleanup list (no deletion): the unreferenced leftovers (DA_Sevarog_ComboOutcome_FAG23/_FAG23b, L_...ComboOutcomeFAG23/_FAG23b, L_...StrafeBlockerSEL008, superseded FAG23c) with referencer check output (read-only LEAD-RUN) | list + referencer counts |

## P36–P42 Reference study (Track D)
| ID | Task | Acceptance |
|---|---|---|
| P36 | D3 clip 7 | ledger row + evidence in repo + hash |
| P37 | D3 clip 8 | same |
| P38 | D3 clip 9 | same |
| P39 | D3 clip 10 | same; D3 = 10/10 |
| P40 | D5 fill_ledger run over all 10 clips; consistency report | tool run counts |
| P41 | Comparison draft (D5 track): reference timings vs our Ember Warden card timings for the measured moves | table; differences with confidence |
| P42 | Feel-like tuning proposals from P41 (proposals only, owner/lead decide) | list, each with the source frames |

## P43–P50 Close-out
| ID | Task | Acceptance |
|---|---|---|
| P43 | Shipping selector policy brief (J049 A/B) refreshed with the live G044 facts | one page for the owner packet |
| P44 | Update OWNER_DECISIONS_PENDING.md with A7 (retire legacy) and the cleanup list | under 40 lines |
| P45 | Write QUEUE_Q (50 tasks) from what P01–P44 left open; post one X- line with section counts | 50 unique IDs |
| P46 | PROJECT_STATE / TASKS dashboard refresh with percentages per track | numbers match TEST_PLAN and the ledger |
| P47 | Handover note for Antigravity (ledger rows the lead witnessed: AWR-004, MOV-001, HIT-008, COM-004, SEL-008, with BUILD ids) | one file, paths verified |
| P48 | DECISIONS.md entries for C-800..C-832 (data route, rebind, tracker, G044 source/phase) | one line each with the C id |
| P49 | Final consistency pass (TASKS, PROJECT_STATE, TEST_PLAN, KNOWN_ISSUES, DECISIONS) | no contradictions |
| P50 | Queue P closed; continue at Q001 | X- line |
