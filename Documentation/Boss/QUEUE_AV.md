# Queue AV — capture-context receipt hardening

**Basis:** AU C-1121 closeout. Five offline tasks, followed by one batch report to Claude; continue the next batch without waiting for review. Check Claude feedback each cycle and hotfix rejected work first. Claude owns all Editor/PIE/build/package work. Owner visual choices remain in `FIGHT_VIDEO_REVIEW.md`; never edit owner verdict fields.

**Progress:** AV-C01–C50 complete offline. C-1124 BUILD-269 AU-C15 passed; AU-C10 had 0 parry attempts because A4 did not occur in the observed 150-second fight. X-1598 reports Codex active-window parry fix/getters and C-1126 transient candidate selector; C-1127 reports BUILD-270 GREEN 487/487 and the natural parry rerun live under lock; A-657 candidate values are accepted for BoostLite authoring. C-1126 AU-C19 passed with the Boost candidate, but the boss-obscuring result remains a readability risk and owner choice is pending. `FRAME_CONTEXT` schema v1 is required in provenance and every row; CLI JSON retains linked action/frame evidence and explicit occlusion scope. Aura manifests use explicit schema v1 and require known build/map/route, unique run/frame IDs, canonical assets, active state, sequential phase warmups and monotonic finite times. Optional PNG verification checks existence/SHA-256 using native paths; CLI reports run/route/schema and verified count without image data. Parry transitions accept A→B→A and reject adjacent duplicates; fallback requires a live sweep. Combined AU/AV regression set now 103/103; syntax and diff checks pass. No Lead capture files were read. Reports `AV_C01_C05_CAPTURE_CONTEXT_RECEIPTS.md`, `AV_C06_C10_SCHEMA_AND_MANIFEST_CONTRACTS.md`, `AV_C11_C15_MALFORMED_EVIDENCE_AND_CHRONOLOGY.md`, `AV_C16_C20_AURA_ASSET_AND_PNG_IDENTITY.md`, and `AV_C21_C25_MANIFEST_PROVENANCE_AND_PORTABILITY.md`, and `AV_C26_C30_PORTABLE_RECEIPT_CONTRACTS.md`, and `AV_C31_C35_PARRY_RECEIPT_INTEGRITY.md`, and `AV_C36_C40_CONTACT_COUNTER_AND_CLI_CONTRACTS.md`, and `AV_C41_C45_PARRY_RESULT_OUTCOMES.md`, and `AV_C46_C50_TERMINAL_OUTCOME_HANDOFF.md`. Claude/owner runtime gates remain pending.

**Mailbox through C-1127:** C-1124 reports BUILD-269 AU-C15 visible and restored, while AU-C10 had 0 attempts because A4 never occurred in 150 seconds. X-1598 posts Codex active-window parry fix/getters and C-1126 transient candidate selector; C-1127 reports BUILD-270 GREEN 487/487 and the natural parry rerun live under lock; A-657 candidate values are accepted for BoostLite authoring. AU-C19 passed with the Boost candidate, but its boss-obscuring result remains a readability risk and owner choice is pending. Keep raw Lead receipts and owner options untouched. Do not touch those in-flight evidence folders. AU-C40/C45 follow; AU-C25/C30 and owner visual gates remain open.

## Batch 1 — validate new same-frame capture context

| Task | Work | Acceptance |
|---|---|---|
| AV-C01 | Extend `fight_capture_receipt.py` to parse `FRAME_CONTEXT` JSON and bind exactly one context row to each same-run frame marker. | Missing, duplicate, foreign-run, stale-frame and mismatched action IDs fail closed; older receipts are labeled pre-context rather than upgraded. |
| AV-C02 | Add tests for camera projection estimates and explicit component-bounds/world-occlusion states. | Finite in-frame/out-of-frame synthetic points are classified; unreadable geometry stays `UNKNOWN`; `UNMEASURED` world occlusion is never promoted to clear/visible. |
| AV-C03 | Add a diagnostic parser for `PARRY_DIAG` transitions and PARRY timeout rows. | One diagnostic per montage transition and at most one timeout per action slot; tracker A1b plus montage name alone cannot become A4. |
| AV-C04 | Validate the aura warmup manifest sequence and approved-frame readiness. | Approved frame must follow a same-run decoded warmup frame at/above the brightness floor within 20 frames and 4 game seconds; all-black/old-manifest rows fail. |
| AV-C05 | Refresh AU and owner handoffs against newly returned Lead receipts without filling owner fields. | BUILD-255/259/Lead PIE/showcase scopes stay distinct; runtime and visual judgments remain separate, owner boxes blank. |

## Batch 2 — pin receipt schema and exercise consumer paths

| Task | Work | Acceptance |
|---|---|---|
| AV-C06 | Version the full-fight frame-context schema in run provenance and each context row. | Parser rejects absent/unknown schema versions; generated records and JSON receipt report the same supported version. |
| AV-C07 | Extend the receipt CLI contract to check context rows survive JSON serialization. | CLI fixture verifies every frame ID, action ID, and explicit `UNMEASURED` occlusion state in output. |
| AV-C08 | Tighten aura warmup manifest identity and label ordering for approved/candidate targets. | Each target label has sequential, same-run warmup labels; duplicate/stale/phase-mismatched rows fail closed. |
| AV-C09 | Add bounded tests for parry transition streams that leave and return to a montage. | Consecutive duplicate diagnostics fail; real montage transitions including return transitions pass; fallback still requires active sweep. |
| AV-C10 | Refresh current evidence/gate handoff from latest mailbox without reading raw Lead artifacts unless assigned. | C-1122 accepted counts remain scoped; Claude's queued AU-C15/AU-C10 order and all later Lead/owner gates are accurate; owner boxes stay blank. |

## Batch 3 — malformed evidence and manifest chronology

| Task | Work | Acceptance |
|---|---|---|
| AV-C11 | Require strict JSON primitive types and non-empty string identities in `FRAME_CONTEXT`. | Integer-as-boolean, empty IDs, and wrong identity types fail; valid UNKNOWN and UNMEASURED states remain accepted. |
| AV-C12 | Validate finite, nondecreasing manifest capture times for every row. | NaN/infinity, missing time, and time regressions fail closed, including discarded warmup rows. |
| AV-C13 | Enforce a single approved target followed by at most one candidate target and correctly scoped warmup phases. | Approved-only remains valid; duplicate/reordered targets or warmup after a target without the matching candidate prefix fail. |
| AV-C14 | Exercise failure behavior through both receipt CLIs. | Malformed receipts return nonzero and emit no success-shaped JSON; valid fixtures remain machine-readable. |
| AV-C15 | Reconcile queue, test plan, task summary and handoff against the current mailbox. | All five batch tasks have evidence, 77 baseline is distinguished from new totals, and Lead/owner runtime gates are unchanged. |

## Batch 4 — bind warmup frames to target asset state

| Task | Work | Acceptance |
|---|---|---|
| AV-C16 | Validate aura manifest `active` and `asset` fields for approved/candidate target frames. | Target is active and uses the canonical asset identity for its phase; missing/unknown/mismatched target state fails. |
| AV-C17 | Require each warmup segment to retain the same asset and active state as its target. | Approved and candidate warmups cannot borrow readiness from another component or phase. |
| AV-C18 | Validate optional capture frame hashes against file content in an offline receipt mode. | Missing file/hash mismatch is reported distinctly; this remains opt-in for existing manifests. |
| AV-C19 | Add full ordered approved-only and approved-plus-candidate manifest fixtures. | Both accepted shapes pass; cross-phase and identity swaps fail closed. |
| AV-C20 | Refresh the next handoff from mailbox and record exact receipt limitations. | No evidence scopes are combined; Lead/owner gates remain explicit and unchanged. |

## Batch 5 — receipt portability and provenance integrity

| Task | Work | Acceptance |
|---|---|---|
| AV-C21 | Add a manifest schema version and reject unsupported versions. | Existing comparison driver and receipt CLI agree on one explicit supported version. |
| AV-C22 | Validate build/map provenance and route choice in the aura manifest. | Missing/unknown build or map identity fails; route remains bound to the selected legacy/data environment. |
| AV-C23 | Add portable path handling for optional PNG hash verification. | Windows separators, spaces and missing paths are handled without changing manifest identity or hashes. |
| AV-C24 | Add CLI JSON regression for the optional hash-verification receipt. | Output reports verified file count and run/route, without copying image data. |
| AV-C25 | Refresh the handoff against mailbox and list exact remaining Lead/owner gates. | No in-flight Lead evidence files are read or modified; visual decisions remain owner-controlled. |

## Batch 6 — frame evidence identity and export safety

| Task | Work | Acceptance |
|---|---|---|
| AV-C26 | Add parser-side checks that manifest frame names and capture IDs are safe single path components. | Traversal, separators and control characters fail; normal frame labels pass. |
| AV-C27 | Validate manifest PNG paths are unique per frame. | Reused image paths fail unless an explicit shared-frame fixture mode is chosen. |
| AV-C28 | Add report JSON schema compatibility and required-key contract tests. | Stable top-level receipt fields are present and typed for consumers. |
| AV-C29 | Check run ID/build/map/route remain constant across every row. | Any provenance drift within one manifest fails closed. |
| AV-C30 | Refresh current handoff and test plan from latest mailbox. | New Lead results are only indexed if present in mailbox; no owner choice inferred. |

## Batch 7 — parry attempt/contact receipt integrity

| Task | Work | Acceptance |
|---|---|---|
| AV-C31 | Rename the obsolete A4-only timeout outcome and retain old-log parsing compatibility. | New driver emits tracker-window wording; receipt accepts old and new timeout names. |
| AV-C32 | Require at most one parry attempt per tracker instance. | Duplicate instance attempts fail; separate instances pass. |
| AV-C33 | Validate contiguous player press-counter increments across attempt rows. | Gaps, regressions and duplicate increments fail closed. |
| AV-C34 | Bind every successful contact to the matching preceding attempt. | Instance, move, source, press count and pre-contact parry counter must agree. |
| AV-C35 | Refresh task/test/project handoffs using the latest mailbox results. | Lead-owned BUILD-270/parry and BoostLite captures remain distinct; no owner choice is inferred. |

## Batch 8 — parry contact and CLI integrity

| Task | Work | Acceptance |
|---|---|---|
| AV-C36 | Validate contact attempts use opened=true and preserve player counter ordering. | A successful contact cannot reference a refused press or stale attempt. |
| AV-C37 | Enforce one contact per attempt and monotonic parried counters across the receipt. | Duplicate contacts and regressions fail closed. |
| AV-C38 | Add malformed numeric/source fixtures for all PARRY_ATTEMPT and PARRY_CONTACT fields. | NaN, infinity, invalid booleans, unknown sources and negative counters fail closed. |
| AV-C39 | Add CLI JSON contract for parry diagnostics and contact totals. | Attempt/contact totals and scoped witness details survive serialization with stable types. |
| AV-C40 | Refresh current handoff from mailbox. | Keep Lead runtime, candidate capture and owner visual gates separate. |

## Batch 9 — parry result outcomes

| Task | Work | Acceptance |
|---|---|---|
| AV-C41 | Parse bounded parry outcomes such as window-refused and no-contact. | Outcome markers are well-formed and scoped to an attempted instance. |
| AV-C42 | Require no-contact outcomes to preserve before/after player counters. | Counter regressions or unreported success fail closed. |
| AV-C43 | Validate timeout slots and result cardinality across the full receipt. | One result per action slot; malformed duplicates are rejected. |
| AV-C44 | Add negative CLI subprocess cases for malformed parry receipts. | Nonzero exit and empty stdout on invalid evidence. |
| AV-C45 | Reconcile test plan, queue and current mailbox gate state. | Runtime and owner gates remain separately labeled. |

## Batch 10 — terminal outcome completeness and queue closeout

| Task | Work | Acceptance |
|---|---|---|
| AV-C46 | Require every PARRY_RESULT to follow its matching attempt. | Orphan or out-of-order result markers fail closed. |
| AV-C47 | Require exactly one terminal outcome for every attempt. | Each attempt resolves to one successful contact or one validated failure/interruption result. |
| AV-C48 | Lock diagnostic/result JSON shape and output field types. | CLI round trip preserves attempt/result rows and contact totals. |
| AV-C49 | Add an integrated mixed success/no-contact receipt fixture. | Multiple attempt counters and one contact plus one no-contact result validate together. |
| AV-C50 | Finalize the 50-task queue and handoff against latest mailbox. | Lead lock/build/runtime state and owner choice are stated from mailbox; no evidence scope is crossed. |

## Gates

C-1124 AU-C15 and C-1126 AU-C19 are witnessed passes. C-1127 reports BUILD-270 GREEN 487/487 and Lead's any-window parry rerun live under lock. A-657 BoostLite candidate values are accepted for Antigravity authoring; Lead plans capture after the parry run. The selected final aura remains an owner decision. A4 phase/range gating remains unconfirmed from source; no data change was made. Other Lead-owned gates remain AU-C25 camera baseline, AU-C30 Air Light matrix, AU-C40 receipt smoke and AU-C45 visible/obscured frame review. AV work validates receipts only; it does not run Unreal or create visual findings.
