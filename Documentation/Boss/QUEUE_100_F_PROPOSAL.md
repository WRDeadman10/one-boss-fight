# Queue F proposal: live witnesses and editor tools (100 tasks)

Prepared for Claude C-780, 2026-11-03. Queue F advances the Roadmap's 100% goal by preparing reproducible live witness packages for framework ledger gaps, completing Track C editor tools, and authoring executing tests for gaps revealed by live packages. Claude owns PIE/build/review; Codex prepares packages, scripts, and tests. No asset overwrite/delete. Any new `set_editor_property` in content scripts must be followed immediately by a read-back assertion.

## Ledger snapshot and limits

Source snapshot: `Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json`, v3.36, canonical_total 82, then 75 WITNESSED / 7 PARTIAL / 0 NOT YET. Owner decisions exclude BOSS-QA-001 (SKIPPED) and BOSS-QA-005 (DROPPED). **Current Queue F live-gap status (Claude C-799 / BUILD-208): all actionable rows closed; 80/82 WITNESSED and two QA rows owner-closed.** BUILD-203/204/208 accepted HIT-008, COM-004, SEL-008; AWR-004 and MOV-001 were previously accepted. Antigravity owns ledger JSON reconciliation. Do not edit the ledger JSON or schedule duplicate live runs absent a revised observable. Gap audit: `Documentation/Boss/F_GAP_AUDIT.md`.

### F-A live evidence reconciliation (5 packages; all actionable rows closed)

Packages are permitted only when the gap audit identifies a genuinely unwitnessed observable and one new live run can close it. Historical package IDs remain distinct: F-A1 is owner-skipped (QA-001); F-A2 narrow SEL-008 is accepted and not to be rerun; F-A3 Guarded is superseded by the gap audit. New residual tasks use AG1-AG5 labels. Lead owns PIE/build and witness updates. Every package must include an EXPECTED sheet (linter-clean), exact F4 command, registered token checks, setup script only if needed (new assets only; assert each editor property readback), route requirement, and manual criteria.

1. **F-AG1 BOSS-SEL-008 stuck recovery — CLOSED, BUILD-208 WITNESSED.** The SEL008c blocker/control pair passed; the blocker cleared walk-in, produced `strafe_stuck` and a direction-flip/resume, while control had no stuck token. No duplicate run.
2. **F-AG2 BOSS-COM-004 Guarded — CLOSED, BUILD-204 WITNESSED.** Root A routes Guarded to D and logs `combo_step node=D`; Hit control routes to B.
3. **F-AG3 BOSS-COM-004 Parried — CLOSED, BUILD-208 WITNESSED.** Root A routes Parried to E and logs `combo_step node=E`; Guarded routes to D and Hit control to B. Correct phase accounted for the every-other-press cooldown.
4. **F-AG4 BOSS-HIT-008 Blocking — CLOSED, BUILD-203 WITNESSED.** Matched contact control applied 20 HP; blocking arm logged guard chip 20->5 and applied 5 HP. This proves the accepted resolver integration, not a `Guarded` resolver enum or zero damage.
5. **F-AG5 BOSS-MOV-001 range-band partition — CLOSED, BUILD-199 WITNESSED.** Four F4 cases at 102.87/254.76/380/701.92 cm prove Melee/Close/Medium/Gap selection and intended Close/Medium overlap. No duplicate run.

AWR-004 candidate-specific hold/exit and control behavior are accepted WITNESSED; HIT-008 Parried is accepted WITNESSED; QA-001 is owner-skipped and QA-005 dropped. The remaining two ledger entries are those owner-closed QA rows. Antigravity's ledger update and any separate C2/C3 runtime validation are outside F-A actionable live-gap status.
### F-C editor tools (55 tasks)

Tasks 6-60. Track C tools only; begin from `Docs/BossCombatReview/Execution/Claude/C1/new_boss.py` and `Documentation/Boss/C1_NEW_BOSS_HOWTO.md`. Editor scripts only; unique new destinations, no asset overwrite/delete; immediate read-back assertions after every `set_editor_property`. Batches of five remain the delivery cadence.

6-20. **C2 Validate Boss (15 tasks):** inspect compile/preflight APIs; define selection and map preconditions; implement editor-only action; collect structured compile errors; display asset/field context; surface preflight blockers; success/no-mutation path; invalid-profile/no-mutation path; safe repeat behavior; stale selection refusal; structured result serialization; automation fixture; command entry point; usage docs; report acceptance boundary.
21-35. **C3 New Weapon (15 tasks):** inventory catalog schema; define validated config; require unique destination; create editor-only utility; assert property readbacks; register without duplicate entries; production compile/preflight surface; valid creation path; existing-asset hashes/control; duplicate-name refusal; destination-collision refusal; malformed input refusal; run evidence; usage docs; recovery guidance.
36-46. **C5 weapon hardcoded-value audit (11 tasks):** inventory weapon assets and values; trace consumers; classify data-driven/intentional/unresolved; map candidate fields to schema/adapter/validator; coverage check; cite exact source/asset; record unresolved gaps; add offline inventory validator; test validator fixtures; report no-mutation; summarize decision points.
47-60. **C4 designer how-to (14 tasks):** boss prerequisites; safe boss creation; weapon prerequisites; catalog workflow; Validate Boss walkthrough; compile/preflight error guide; framework proof-map workflow; F4 command and evidence capture; token troubleshooting; unique naming/no-overwrite; readback assertions; current tool screenshots/links; novice dry-run review; final changelog and consistency pass.

### F-T executing tests (40 tasks)

Tasks 61-100. Tests must execute behavior; no source-grep-only fixtures. Add only for stable, demonstrated gaps or editor tool contracts. Claude owns build/execution; honor `Source changed` and `PRODUCTION CHANGE` flags, use `std::numeric_limits`, cite engine headers, and add `AddExpectedError` for intentional error logs.

61-67. **Live-gap tests (7):** SEL-008 interruption/recovery rule contract; COM-004 Guarded/Parried outcome-to-followup table; HIT-008 blocking-before-damage ordering; MOV-001 band/card compatibility; package token completeness; expected-sheet linter integration; validator acceptance for closable F-A sheets.
68-78. **C2 tests (11):** valid profile success; invalid profile diagnostic; missing selection; compile failure context; preflight failure context; no mutation on success; no mutation on failure; repeat idempotence; stale asset refusal; structured result serialization; editor command failure propagation.
79-91. **C3 tests (13):** config validation; unique destination; duplicate name refusal; existing asset preservation; readback assertions; catalog add; duplicate catalog entry refusal; compile success; compile failure diagnostics; preflight failure diagnostics; invalid input failure; deterministic naming; result serialization.
92-100. **Cross-tool and docs contracts (9):** C5 inventory coverage; hardcoded-value classification completeness; audit consumer references; F4 token schema match; expected-sheet linter cases; report link validity; C4 command freshness; no-overwrite language checks; final audit regression fixture.

