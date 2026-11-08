# Queue AS — bounded offline handoff tasks (45-task outline)

Prepared after C-1101 in five-task batches. This outline prioritizes work that Codex can complete without an owner decision or Unreal access. Claude owns builds, PIE, cooking and packaging; Antigravity owns art assets; the owner commits and makes product choices. Every runtime/package row is a Lead gate, and every design/default row is an owner gate. Do not read, edit, move, or regenerate raw Lead artifacts unless a later mailbox order explicitly assigns that evidence.

## Batch 1 — C-1101 route-receipt hotfix closeout

| ID | Files | Task and acceptance | External gate |
|---|---|---|---|
| AS-C01 | `Scripts/Tools/ar_charge_receipt.py`, tests | Verify activation route is authoritative; conflicting probe labels fail with both route values; filtered inputs require a witness file. | Lead review |
| AS-C02 | receipt tests | Keep path contracts for mislabelled C-1095, truelegacy, and data logs read-only; assert no artifact writes. | None |
| AS-C03 | `AR_C06_C10_KI192_RECEIPT_TOOL.md` | Document raw/full versus filtered/witness-file CLI, mismatch behavior, and C-971 historical limits. | None |
| AS-C04 | `AR_C31_C35_KI192_RERUN.md`, `QUEUE_AR.md` | Make repeat-receipt stamping use activation-witness semantics and distinguish historical C-971 from confirmed C-1100 identities. | None |
| AS-C05 | `AR_C46_C50_HANDOFF.md`, TASKS/PROJECT_STATE | Close AR-C46–C50 with validation and C-1101 verdict state; keep Lead countersign explicitly pending until received. | Lead review |

## Batch 2 — KI-193 source/cook evidence readiness

| ID | Files | Task and acceptance | External gate |
|---|---|---|---|
| AS-C06 | `Documentation/Boss/AR_C21_C25_KI193_COOK_GATE.md` | Reconcile the eight required ER/Tier 2 package paths against current Source defaults and owner-approved assets; no presence claim without a manifest. | None |
| AS-C07 | `Scripts/Tools/ar_er_cook_manifest.py`, tests | Audit malformed manifests, duplicate normalized paths, configuration identity and output no-write behavior; add only missing synthetic contracts. | None |
| AS-C08 | cook-gate report | Add an explicit Development/Shipping evidence intake template with build ID, manifest hash and executable hash fields. | None |
| AS-C09 | `Documentation/TEST_PLAN.md` only if authorized | Draft a proposed KI-193 package acceptance row outside TEST_PLAN first; keep runtime, cook and source evidence separate. | Ask Lead before TEST_PLAN edit |
| AS-C10 | `QUEUE_AS.md`, KI-193 handoff | Close the evidence intake increment with exact Lead return artifacts and fail-closed stop conditions for missing identity, path, or packaged smoke evidence. | Lead supplies packages |

## Batch 3 — KI-197 stage identity and bench-kit evidence

| ID | Files | Task and acceptance | External gate |
|---|---|---|---|
| AS-C11 | `AR_C16_C20_KI197_STAGE_ROOT_FIX.md` | Re-audit every default stage-root consumer against config selection; report any stale Development/Shipping fallback with file:line evidence. | None |
| AS-C12 | `Scripts/Tools/test_package_stage_roots.py` | Expand synthetic cases for relative/absolute overrides and configuration mismatch, without invoking UAT or touching staged folders. | None |
| AS-C13 | `Scripts/Tools/check_stage_identity.py`, tests | Audit BuildStamp, configuration, manifest and executable identity comparison; add fixtures only for a demonstrated gap. | None |
| AS-C14 | `AR_C16_C20_KI197_STAGE_ROOT_FIX.md` | Provide a Lead checklist for separate Development and Shipping roots plus bench-kit provenance. | Lead package run |
| AS-C15 | `QUEUE_AS.md`, KI-197 handoff | Close source-level acceptance separately from dual-package verification; no cleanup, contamination or package claim. | Lead returns identity evidence |

## Batch 4 — KI-192 package scope and receipt interoperability

| ID | Files | Task and acceptance | External gate |
|---|---|---|---|
| AS-C16 | `AR_C31_C35_KI192_RERUN.md` | Audit C-1100 summary counts and pie/package boundary against C-1100 mailbox text; avoid opening raw receipts. | None |
| AS-C17 | `Scripts/Tools/ar_charge_repeat_receipt.py`, tests | Verify stamp rejects absent activation witness and probe disagreement; aggregate accepts only exact route/trial cardinality. | None |
| AS-C18 | `AR_C06_C10_KI192_RECEIPT_TOOL.md` | Document witness-file pairing rules so filtered rows cannot be paired with a different run. | None |
| AS-C19 | KI-192 package gate | Draft a same-build packaged-run evidence schema with activation route, stage identity and four hold cases. | Lead package run |
| AS-C20 | `KNOWN_ISSUES.md`, `AR_C46_C50_HANDOFF.md` | Keep KI-192 CLOSED for PIE and package-open status consistent after Lead review; no threshold changes. | Lead review |

## Batch 5 — KI-199 first-dodge evidence boundaries

| ID | Files | Task and acceptance | External gate |
|---|---|---|---|
| AS-C21 | `AN_C11_C15_MOVING_DODGE_GATE.md`, `AN_C1065_FIRST_DODGE_RETRY_HOTFIX.md` | Reconcile the C-1099 route correction and C-1067 scope; legacy must remain unmeasured unless an activation witness proves it. | None |
| AS-C22 | `Scripts/Editor/probe_first_dodge_after_draw.py` | Static audit that the observation snapshot is after existing input edges and does not alter dispatch; no probe execution. | None |
| AS-C23 | `Scripts/Editor/test_probe_first_dodge_after_draw_contract.py` | Add only a missing AST contract for the diagnostic helper boundary; preserve state-changing outer-driver warning. | None |
| AS-C24 | KI-199 diagnostic handoff | Define the minimal Lead capture return fields for route witness, first attempt, repeat, activation, consumption and travel. | Lead PIE run |
| AS-C25 | `KNOWN_ISSUES.md`, `QUEUE_AS.md` | Separate workaround proof, root-cause attribution and package status; do not assign a root cause from current logs. | Lead review |

## Batch 6 — KI-196 / KI-198 scoped gates

| ID | Files | Task and acceptance | External gate |
|---|---|---|---|
| AS-C26 | `AM_C26_C30_DODGE_GATE.md`, KI-196 | Ensure C-1076 is labeled DATA-default for both nominal arms and package proof remains open. | None |
| AS-C27 | `C1043_PROBE_API_HOTFIX.md`, `C1044_PROJECT_GUARD_HOTFIX.md` | Ensure C-1047 guard-counter observations are DATA-default only and preserve package-open state. | None |
| AS-C28 | guard-counter tests/source docs | Audit that test claims distinguish synthetic arm, real blocked contact and damaging counter; no runtime changes absent an assigned defect. | None |
| AS-C29 | Lead gate templates | Specify activation-witness fields for any future legacy guard/dodge run and reject label-only route identity. | Lead run |
| AS-C30 | `KNOWN_ISSUES.md`, `QUEUE_AS.md` | Close only stale route wording; do not promote PIE success to packaged acceptance. | Lead review |

## Batch 7 — Camera matrix readiness without selecting an option

| ID | Files | Task and acceptance | External gate |
|---|---|---|---|
| AS-C31 | `CAMERA_MELEE_OCCLUSION_PROPOSAL.md` | Reconcile C-1081–C-1090 DATA-default labels and keep A/B/C/B+C scenario bounds visible. | None |
| AS-C32 | `AP_C31_C35_OPTION_MATRIX.md`, `AQ_C11_C15_BC_MATRIX.md` | Audit scenario and option-cell identity; identify missing results without inferring absent cells. | None |
| AS-C33 | `AQ_C21_C25_PACKAGE_GATES.md` | Specify package checks for a future selected option while preserving default-off/no-option baseline. | Owner choice before implementation |
| AS-C34 | camera receipt template | Require actual activation witness, config/CVar readback, scenario label, route, build and cleanup evidence. | None |
| AS-C35 | `KNOWN_ISSUES.md` KI-037/KI-066 | Reconcile current open coverage and owner-choice gates; no `RPGCameraRig` or config changes. | Owner selects B/C/B+C |

## Batch 8 — KI-191 Tier 2 and full-fight evidence boundaries

| ID | Files | Task and acceptance | External gate |
|---|---|---|---|
| AS-C36 | `AN_C26_C30_TIER2_EVIDENCE.md`, `FIGHT_VIDEO_REVIEW2_AG.md` | Reconcile C-1075/C-1077 black paired capture with the separate owner showcase options; preserve no-disposition status. | Owner visual review |
| AS-C37 | `AO_C16_C20_AURA_COMPARISON_AUDIT.md` | Separate authoring readback, PIE lifecycle, comparison capture and full-fight visibility claims. | None |
| AS-C38 | aura capture contracts | Static audit of frame selection, image validation and receipt identity; no image generation or Unreal run. | None |
| AS-C39 | KI-191 follow-up sheet | List remaining first-use, cooked-content and full-fight visual evidence without upgrading the failed comparison. | Lead/owner review |
| AS-C40 | `KNOWN_ISSUES.md`, `QUEUE_AS.md` | Keep KI-191 PARTIAL until a reviewed visible result plus separate package proof exists. | Lead and owner evidence |

## Batch 9 — Cross-queue consistency and next handoff

| ID | Files | Task and acceptance | External gate |
|---|---|---|---|
| AS-C41 | `Documentation/PROJECT_STATE.md`, `Documentation/TASKS.md` | Reconcile current AR/AS queue state to mailbox verdicts; demote old snapshots to historical. | None |
| AS-C42 | `Documentation/TEST_PLAN.md`, `KNOWN_ISSUES.md` | Cross-check only explicitly authorized evidence rows against source mailbox entries; no new run claims. | Lead review |
| AS-C43 | AS offline test inventory | Run the exact scoped offline test list, py_compile, PowerShell parse where applicable, link checker and diff check; record actual outputs. | None |
| AS-C44 | `Documentation/Boss/AS_C41_C45_HANDOFF.md` | Build a concise task-to-file/gate index with unresolved owner/Lead actions and exact evidence paths. | None |
| AS-C45 | `QUEUE_AS.md`, `PROJECT_STATE.md`, `TASKS.md` | Close the outline at 45 ordered unique tasks in nine five-task batches; state the next action and prohibit Codex commit/push. | Lead reviews next batch |

## Acceptance boundary

This is an offline work outline. It does not authorize opening Unreal, starting PIE, building/cooking/packaging, selecting a camera or stamina policy, modifying art assets, or editing raw Lead evidence. Execute offline batches in order while Lead review proceeds asynchronously; check each cycle for feedback and hotfix rejected items immediately before continuing.

## Progress

- **AS-C01–C05:** C-1101 receipt hotfix implemented, fixture-path contracts cover mislabelled/truelegacy/data logs, AR handoff refreshed; focused receipt/runner/rerun suite 31/31 at first closeout. Claude accepted the hotfix in C-1103 after checking the three fixture paths and filtered-input refusal; Lead reports 10/10 P_C1095 receipts regenerated with activation-witnessed routes. No raw log edits by Codex.
- **AS-C06–C10:** Audited the canonical eight-path list, checker identity/no-write behavior and existing synthetic contracts; added `AR_C21_C25_KI193_PACKAGE_INTAKE.md` with separate Development/Shipping intake fields and claim boundaries. No package or stage evidence changed.
- **AS-C11–C15:** Audited project and bench-kit stage mappings, corrected the remaining Shipping symbol-scan default and clarified the benchmark runner's context-dependent stage label. Added synthetic stage-identity fixtures for valid split stamps, same-root/config mismatch and missing-file rejection. This is source-level coverage only; Lead dual-package verification remains open.
- **AS-C16–C20:** Cross-checked C-1100's 15-run counts and PIE/package boundary against mailbox C-1100 and current handoffs without opening raw receipts. Repeat stamping now has direct tests for activation-witness absence and probe disagreement; docs state raw same-run witness requirements. Added a prospective packaged KI-192 receipt checklist with Lead-controlled repetitions and no threshold change. KI-192 remains CLOSED for PIE and OPEN for package. Combined focused AS/AR route and stage-root suite: 44/44; py_compile and diff-check pass.
- **AS-C21–C25:** Reconciled KI-199's nominal route labels to C-1099 (former “legacy” arms are DATA-default; no legacy parity claim), confirmed the post-press snapshot contract preserves input edge order and calls no dispatch mutators, and added minimum Lead return fields requiring route witness, build/log identity, first input, activation observables, movement, repeats and completion. Focused observation contract 4/4; py_compile and diff-check pass. Root cause and package status stay open.
- **AS-C26–C30:** Corrected KI-196 and KI-198 summaries so C-1076/C-1047 nominal route pairs are scoped to DATA-default PIE observations per C-1099; added a shared package-return contract requiring build/stage identity, action/scenario, per-process activation witness, raw-log identity and packaged smoke. Both package gates remain Lead-owned/open; focused suite 48/48, doc links 0, diff-check pass. No raw artifacts inspected or runtime claim added.
- **AS-C31–C35:** Reconciled the owner camera brief and corrected the C-1090 matrix: two nominal arms are DATA-default, not legacy/data parity; the B+C cell also lacked the specified look-input injection, so that acceptance remains pending. Updated the post-owner-choice package gate and camera receipt template with route witness, config/CVar readback, stage/build identity, hashes, cleanup and log/video fields. KNOWN_ISSUES continues to keep KI-037/KI-066 open pending owner choice, broader scenarios and package proof. Doc links 0; diff-check pass; no camera option/default selected.
