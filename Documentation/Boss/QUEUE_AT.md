# Queue AT — DATA-default package-readiness and evidence-tooling tasks

Prepared at AS-C45 under Claude C-1104. Ten batches of five tasks, with an update to Lead after each batch. Codex works offline while Lead handles package/build reviews; rejected work is hotfixed immediately. Owner commits. Do not commit/push, launch Unreal/PIE, build, cook, package, mutate raw Lead evidence, or modify art assets in this queue. DATA-default is acceptance scope for first-dodge, camera and parry; legacy remains a parity control only, and no true-legacy rerun is queued to restore wording. Preserve all owner choices and package gates. Do not delete or clean stage/kit evidence; `MakeBenchKit.ps1` removes an existing target kit and zip, so any later Lead run must use a fresh isolated output directory.

## Progress

- **AT-C01–C05 complete:** all eight required paths match current C++ defaults; checker audit added explicit duplicate-required-list coverage; intake captures separate Development/Shipping identities, hashes, route witnesses and smoke outcomes; TEST_PLAN audited without edits; fail-closed stops made explicit. Focused tests 10/10, links 0, diff-check pass. No package/build/UE activity.
- **AT-C06–C10 complete:** validated stage stamp/file/root semantics and kit remapping, added two temp-fixture fail-closed tests, and documented separate stage/kit identity returns plus MakeBenchKit deletion risk. Focused stage suite 14/14, links 0, diff-check pass. No stage outputs inspected.
- **AT-C11–C15 complete:** kept C-1100’s PIE receipts separate from the fixed 5x2 wrapper; added route/trial mismatch coverage and a Lead-selected-count packaged R2 intake. Charge contracts 28/28, links 0, diff-check pass; no raw logs/package evidence accessed.

## Batch 1 — KI-193 cook and package intake

| ID | Files | Task and acceptance | External gate |
|---|---|---|---|
| AT-C01 | `AR_C21_C25_KI193_COOK_GATE.md` | Reconcile the eight required package paths against current source defaults; distinguish source existence from cooked manifest and runtime proof. | None |
| AT-C02 | `Scripts/Tools/ar_er_cook_manifest.py`, tests | Audit malformed, duplicate, configuration-mismatched and missing-path synthetic inputs; add only a demonstrated offline contract gap. | None |
| AT-C03 | KI-193 intake template | Add exact Development/Shipping Build ID, manifest hash, executable hash, required-path result, packaged-smoke and route-witness fields. | Lead package artifacts |
| AT-C04 | `Documentation/TEST_PLAN.md` | Audit existing KI-193 rows for claim boundaries; propose edits outside TEST_PLAN and do not edit without renewed Lead authorization. | Lead authorization required for edits |
| AT-C05 | `QUEUE_AT.md`, KI-193 handoff | Define fail-closed stops for absent/mismatched build identity, missing package path, missing route witness or incomplete smoke log. | None |

## Batch 2 — KI-197 stage identity and bench kit

| ID | Files | Task and acceptance | External gate |
|---|---|---|---|
| AT-C06 | `Scripts/Tools/check_stage_identity.py`, tests | Re-audit exact stamp, required-file, root-collision and shared-build-ID semantics; maintain synthetic no-write coverage. | None |
| AT-C07 | `Scripts/MakeBenchKit.ps1`, `check_bench_kit.py` | Reconcile project roots with intentional kit remapping; flag any default mismatch without opening staged outputs. | None |
| AT-C08 | `AR_C16_C20_KI197_STAGE_ROOT_FIX.md` | Keep Lead dual-package commands and returned identity fields separate from source-level acceptance. | None |
| AT-C09 | `Scripts/Tools/test_package_stage_roots.py` | Add only justified fixture checks for config-specific roots and caller overrides; no UAT or staged-folder access. | None |
| AT-C10 | `QUEUE_AT.md`, KI-197 handoff | Preserve no-cleanup/no-delete policy and list exact separate Development/Shipping verification artifacts. | Lead package run |

## Batch 3 — KI-192 packaged receipt interoperability

| ID | Files | Task and acceptance | External gate |
|---|---|---|---|
| AT-C11 | `AR_C31_C35_KI192_RERUN.md` | Audit the DATA-default package gate against C-1100 and ensure the four established hold cases are named without changing threshold or inventing repetitions. | None |
| AT-C12 | `Scripts/Tools/ar_charge_receipt.py`, tests | Ensure package receipt identity remains same-run activation-witness based and filtered inputs require the matching raw witness file. | None |
| AT-C13 | `Scripts/Tools/ar_charge_repeat_receipt.py`, tests | Ensure a repeated package aggregate cannot mix Build IDs, route witnesses, trial IDs or absent sample rows. | None |
| AT-C14 | KI-192 package intake | Define exact packaged executable/stage/manifest hashes, smoke status, activation witness and per-hold selected action/tick fields. | Lead package run |
| AT-C15 | `KNOWN_ISSUES.md`, AR handoff | Keep KI-192 PIE-closed and package-open; no threshold or device-latency claim. | None |

## Batch 4 — DATA-default first-dodge and guard acceptance

| ID | Files | Task and acceptance | External gate |
|---|---|---|---|
| AT-C16 | `AN_C11_C15_MOVING_DODGE_GATE.md` | Reconcile first-dodge acceptance with C-1104: DATA-default witness only; no parity-only legacy rerun. | None |
| AT-C17 | `AM_C26_C30_DODGE_GATE.md` | Reconcile KI-196/KI-198 package evidence to the documented DATA-default scope and separate their actions. | None |
| AT-C18 | `Scripts/Editor/test_probe_first_dodge_after_draw_contract.py` | Audit snapshot ordering and mutator exclusions; add only synthetic AST coverage for a demonstrated gap. | None |
| AT-C19 | First-dodge/guard package return sheet | Require stage/build identity, same-run `route=data` witness, first input, action/montage, outcome, raw-log hash and process completion. | Lead package run |
| AT-C20 | `KNOWN_ISSUES.md`, `QUEUE_AT.md` | Preserve KI-199 root-cause uncertainty and KI-196/KI-198 package-open status; do not change disposition from a checklist. | None |

- **AT-C16–C20 complete:** applied C-1104 DATA-default scope to first-dodge/guard gates, audited snapshot contracts, added a same-run witnessed package return sheet, and removed stale KI-199 parity-rerun wording. Dodge contracts 12/12, links 0, diff-check pass.
- **AT-C21–C25 complete:** reconciled the owner brief, DATA-default matrix, package gate, receipt template and KI-037/KI-066 text with C-1105; corrected stale two-route/24-run test expectations. Camera/package contracts 18/18, links 0, diff-check pass. No Source or runtime changes.

## Batch 5 — Camera package readiness after owner choice

| ID | Files | Task and acceptance | External gate |
|---|---|---|---|
| AT-C21 | `CAMERA_MELEE_OCCLUSION_PROPOSAL.md` | Keep A/B/C/B+C evidence bounds current; preserve no-selection state until owner choice. | Owner choice |
| AT-C22 | `AQ_C11_C15_BC_MATRIX.md` | Audit DATA-default cells, C-1090 limits and C-1105 look-input result; preserve owner-choice/package-only open gates and do not queue legacy parity work. | None |
| AT-C23 | `AQ_C21_C25_PACKAGE_GATES.md` | Reconcile selected-option package steps with same-run route, config readback, hashes, cleanup and default-off baseline. | Owner choice |
| AT-C24 | Camera receipt template | Verify exact scenario, CVar request/readback, route witness, build/stage, raw log/video hashes and cleanup fields. | None |
| AT-C25 | `KNOWN_ISSUES.md` KI-037/KI-066 | Per C-1105, keep open only for owner option choice and package proof; do not add broader parity-only reruns. | Owner choice / Lead package |

## Batch 6 — KI-191 Tier 2 package and visual evidence

| ID | Files | Task and acceptance | External gate |
|---|---|---|---|
| AT-C26 | `AT_C26_C30_OWNER_GATED_PATCH_READINESS.md` | Confirm B/C/B+C remains unselected and map the existing component/config shape without touching camera Source or config. | Owner choice |
| AT-C27 | `plan_camera_default.py`, tests, patch-readiness doc | Produce an accurate B+C config/Shipping-guard/test plan that remains dry-run-only and fail-closed. | Owner choice |
| AT-C28 | `create_phase_two_aura_boost.py`, launcher | Audit authoring behavior and harden exclusive engine-lock acquisition; do not run Unreal or touch the candidate asset. | Owner approval |
| AT-C29 | Aura static contract, patch-readiness doc | Verify duplicate/source/save/readback boundaries and prove launcher only removes a lock it acquired. | None |
| AT-C30 | `QUEUE_AT.md`, handoff status | Record no camera/aura selection, no runtime application, and remaining owner/Lead gates. | Owner/Lead evidence |

- **AT-C26–C30 complete (offline readiness; C-1108 refinement):** planner proposes two `URPGCameraRig` config booleans (`bDefaultHideBossInside`, `bDefaultLockOnFraming`) with false/false fallback, selected config plus Development-only test CVar behavior, guard move, native tests and DATA-default package evidence. Hardened aura launcher lock acquisition against a check/write race; static contracts pass. Camera Source/config and aura asset untouched; no Unreal run. See `AT_C26_C30_OWNER_GATED_PATCH_READINESS.md`.

## Batch 7 — Shared offline intake and identity validators

| ID | Files | Task and acceptance | External gate |
|---|---|---|---|
| AT-C31 | package receipt schema | Define common Build ID/configuration/stage-root/manifest/executable identity fields without collapsing feature-specific evidence. | None |
| AT-C32 | route witness contracts | Audit all maintained package acceptance scripts for `route=data` same-run activation witness; do not execute UE scripts. | None |
| AT-C33 | hash manifest tooling | Add synthetic corruption/missing-file checks only where current offline validators lack them; no raw artifact writes. | None |
| AT-C34 | packaged smoke intake | Define exact process exit, smoke summary, runtime log and retained-failure paths. | Lead package run |
| AT-C35 | package intake tests | Run the exact scoped pure-Python contracts and verify no files outside temporary fixtures are written. | None |

- **AT-C31–C35 complete:** added a shared per-configuration identity/smoke/route/failure-retention intake; audited route receipts, hash manifests and smoke token validation. Fixed two proven fail-closed gaps: evidence SHA manifests now reject correctly hashed paths escaping the evidence root and report unreadable manifests; smoke receipts reject zero-second survival. Focused identity/route/smoke/hash suite 36/36, Python syntax pass. No package/stage artifacts accessed or modified. See `AT_C31_C35_SHARED_PACKAGE_INTAKE.md`.

## Batch 8 — Documentation and source contract consistency

| ID | Files | Task and acceptance | External gate |
|---|---|---|---|
| AT-C36 | `Documentation/PROJECT_STATE.md`, `TASKS.md` | Reconcile only current queue status to latest mailbox verdicts; demote superseded progress to historical. | None |
| AT-C37 | `Documentation/KNOWN_ISSUES.md` | Check KI-191/192/193/196/197/198/199 and KI-037/066 against accepted evidence boundaries. | None |
| AT-C38 | `Documentation/TEST_PLAN.md` | Read-only audit of any remaining post-C-1099 route wording; submit proposed diff separately and do not edit without explicit renewed authorization. | Lead authorization required for edits |
| AT-C39 | source contracts | Confirm offline tests guard acceptance claims and test fixtures remain synthetic/read-only; no game run. | None |
| AT-C40 | `QUEUE_AT.md` | Record only evidence supported by the mailbox or local test outputs; attach source paths for every status. | None |

- **AT-C36–C40 complete:** reconciled current queue status to C-1107/C-1108 and updated the camera default plan to C-1108's two-boolean shape. Audited the KI-037/066 and KI-191/192/193/196/197/198/199 dispositions against current issue rows, mailbox verdicts, and the latest TEST_PLAN receipts; no unsupported closure or route-parity claim found. TEST_PLAN was read-only per its authorization gate. Source/package contracts 17/17, links 0, diff-check clean. See `KNOWN_ISSUES.md`, `TEST_PLAN.md`, `PROJECT_STATE.md`, and `TASKS.md`.

## Batch 9 — Final scoped validation and handoff

| ID | Files | Task and acceptance | External gate |
|---|---|---|---|
| AT-C41 | offline test inventory | Run the enumerated route/stage/cook/camera/aura/test contracts exactly; report actual counts. | None |
| AT-C42 | changed Python/PowerShell sources | Run Python syntax checks and PowerShell parser AST only; do not execute runners. | None |
| AT-C43 | `Documentation/Boss` | Run link checker, task-ID/order validator and `git diff --check`; list any failures. | None |
| AT-C44 | `AT_C41_C45_HANDOFF.md` | Build task-to-file/gate index with open Lead/owner actions and exact evidence paths. | None |
| AT-C45 | `QUEUE_AT.md`, `PROJECT_STATE.md`, `TASKS.md` | Close 50 ordered unique IDs in ten five-task batches; name next queue and state no commit/push. | None |

- **AT-C41–C45 complete:** selected route/stage/cook/camera/aura/smoke/hash/source-reference contracts pass 76/76; changed Python syntax and PowerShell AST pass. Queue validator now checks AT as ten groups of five (AA/AB/AT all pass at 50 rows). Documentation links 0; diff check pass. TEST_PLAN read-only; no Unreal/build/cook/package/stage/raw-evidence access. Handoff: `AT_C41_C45_HANDOFF.md`.

## Batch 10 — External evidence intake maintenance

| ID | Files | Task and acceptance | External gate |
|---|---|---|---|
| AT-C46 | Lead package returns | When received, audit their stated identity/summary against submitted receipts without editing raw package artifacts. | Lead artifacts |
| AT-C47 | rejected source/docs items | If Claude rejects any offline row, patch that bounded defect immediately and add a regression contract. | Claude verdict |
| AT-C48 | accepted package gate docs | Record package results only from a Lead verdict and exact referenced evidence; keep evidence provenance explicit. | Lead verdict |
| AT-C49 | current queue and issue docs | Reconcile statuses after evidence intake; preserve owner choice and DATA-default policy. | Lead/owner evidence |
| AT-C50 | `QUEUE_AT.md`, next handoff | Close the final five-task batch, list remaining gates and prepare the next queue without committing. | None |

- **AT-C46–C50 complete:** mailbox review found no post-C-1108 Lead package result or new owner disposition. C-1108's two-boolean planner refinement was applied and verified in X-1572; no hotfix/rejection remains outstanding. KI-191/192/193/196/197/198/199 and camera KI-037/066 gates remain as listed in `AT_C41_C45_HANDOFF.md`. Queue AT is complete: 50 ordered tasks in ten batches, all offline work recorded. The next batch of work needs a fresh bounded scope; no commits/pushes.

## Queue acceptance boundary

AT is offline-first. Lead-owned package artifacts can be reviewed when delivered, but Codex does not create them by running Unreal, UAT, cook or package commands. No owner camera/stamina choice, no art change, no TEST_PLAN edit without renewed Lead authorization, no raw-log edits, and no commit/push.
