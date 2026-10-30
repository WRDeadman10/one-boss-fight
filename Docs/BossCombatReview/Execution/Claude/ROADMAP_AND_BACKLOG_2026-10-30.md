# Roadmap and backlog (lead, 2026-10-30)

Owner goal (2026-10-30): at 100 %, a designer creates a NEW BOSS and a NEW WEAPON from an Unreal Editor Utility, with all
boss data in assets (data-driven), and the 83 requirements closed. Reference for comparison: a reference boss profile built
from observed gameplay of the owner's chosen reference boss (a humanoid two-phase king) and one reference great sword.

Counting rule: a task is DONE only with evidence (receipt, log, test or recorded run) accepted by the lead. A requirement row
(track B) is DONE only when its observable_result is witnessed. Progress = DONE tasks / 100.

Foundation already done before this backlog (not counted): typed records, validators, adapters, preflight, preparation,
registry, activation facade (DD19-DD29, 182/182 tests), authoring toolkit, 3 saved draft assets, Ember Warden passes the
production compile (DD27j), startup chronology measured (DD30 probe).

## Track A: data-driven boss platform (7)
| ID | Task | Depends on | State |
|---|---|---|---|
| A1 | Save Hero V2 draft (DD27m) | owner yes (given) | released |
| A2 | 12-plan preflight on the SAVED Ember Warden (DD27k) | A1 | staged |
| A3 | Binding source + boss selection store (DD30 design and code) | A2 | options doc in progress |
| A4 | Fail-closed activation at OnWorldBeginPlay: on-screen error + error log, boss inactive | A3 | owner policy given |
| A5 | Parity: data path vs legacy on the 31 PIE drivers | A4 | todo |
| A6 | Hardcoded-value audit: every boss number lives in data | A4 | todo |
| A7 | Retire the legacy attach path (owner approval) | A5, A6 | todo |

## Track B: the 83 requirements (83)
Rows of `Codex/ALL83_EXECUTION_LEDGER_2026-10-27.json`. Groups from `Antigravity/Ledger/DATA_DRIVEN_LEDGER_GAPS.md`:
13 with typed fields (need a witness after A4), 11 missing fields (measure the current value in PIE first, then
record + validator + adapter + authoring field + manifest row + test), 59 runtime systems (mostly verification, plus moving
hardcoded numbers to data). State today: 0 of 83 closed.

## Track C: editor tools (5)
| ID | Task | Depends on |
|---|---|---|
| C1 | Editor Utility "New Boss": create a boss definition from a template, fill fields, save | A2 |
| C2 | "Validate Boss" in the editor: runs the production compile and preflight, shows errors | A2 |
| C3 | Editor Utility "New Weapon": create a weapon definition, register in the catalog, validate | C5 |
| C4 | Designer how-to (create, validate, test a boss and a weapon) | C1-C3 |
| C5 | Weapon data audit: which weapon values are still hardcoded (catalog, DA_WeaponAttacks) | none |

## Track D: reference boss and weapon (5)
| ID | Task | Depends on |
|---|---|---|
| D1 | Reference capture: owner-recorded gameplay of the reference boss and weapon; frame-timing method | owner footage |
| D2 | Reference profile: the 83 rows filled from measured footage (UNMEASURED where not measured) | D1 |
| D3 | Author the reference-inspired boss with C1 (original names and art) | C1, D2, animation source |
| D4 | Reference-inspired weapon with C3 | C3, D1 |
| D5 | Comparison report: 83 rows, reference vs ours; match target defined by the owner | D2, D3, track B |

## Rules for the reference work
- Behaviour is matched by OBSERVATION of footage the owner records from their own copy (timings, ranges, phase rules).
- No extraction of the reference game's files (models, animations, sounds, parameter data), no datamined tables.
- Original names, models and animations in the project; the reference names stay out of shipped content.

Total: 7 + 83 + 5 + 5 = 100 tasks. DONE today: 0 (A1 released, A2 staged, A3 in progress).
