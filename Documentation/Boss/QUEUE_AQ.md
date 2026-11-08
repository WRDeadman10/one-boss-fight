# Queue AQ — camera runtime probe and open gates (50 tasks)

Assigned by Claude in C-1089 after AP closeout. Work proceeds in ten batches of five. Claude owns Unreal builds and PIE runs; Codex owns the maintained offline probe, contracts, run matrices, and source/docs audits. Keep Claude's original probe unchanged. Never edit `RPGCameraRig` until the owner chooses a camera option. No asset save, build, PIE, commit, or push by Codex in this queue.

## Tasks

| ID | Files | Task and acceptance |
|---|---|---|
| AQ-C01 | `Documentation/Boss/QUEUE_AQ.md` | Define 50 unique tasks in ten five-task batches; record Lead/owner boundaries and the no-`RPGCameraRig` rule. |
| AQ-C02 | `Scripts/Editor/test_pie_camera_engage_contract.py` | Write and run red-phase offline contracts for a maintained camera probe: four modes, speed, look injection, and CVar interface; tests fail before the maintained probe exists. |
| AQ-C03 | `Scripts/Editor/pie_camera_engage.py` | Copy/adapt the Lead driver into the maintained Editor scripts path; preserve helper usage and telemetry without changing the Lead original. |
| AQ-C04 | `Scripts/Editor/pie_camera_engage.py`, `Scripts/Editor/test_pie_camera_engage_contract.py` | Validate supported modes, finite bounded `CAM_SPEED`, whitelisted independent camera CVars, and B+C combined values; retain no-component-property-write rule. |
| AQ-C05 | `Documentation/Boss/QUEUE_AQ.md`, `Documentation/Boss/AQ_C01_C05_CAMERA_PROBE.md` | Record exact offline checks and limitations; state that Lead still owns running the maintained driver in PIE. |
| AQ-C06 | `Scripts/Editor/pie_camera_engage.py`, `Scripts/Editor/test_pie_camera_engage_contract.py` | Add a bounded attack/lunge mode that drives a live awake boss at 80–150 cm via tracker-authored lunge moves; retain all existing modes and passive observations. |
| AQ-C07 | `Scripts/Editor/test_pie_camera_engage_contract.py` | Contract the attack/lunge setup, distance band, move selection, bounded duration and telemetry labels without requiring Unreal imports. |
| AQ-C08 | `Documentation/Boss/AQ_C06_C10_ATTACK_LUNGE_PROBE.md` | Specify Lead's legacy/data attack/lunge acceptance, option-off/B runs, and evidence needed to establish B in real attack overlap. |
| AQ-C09 | `Scripts/Editor/pie_camera_engage.py`, tests | Harden actor-loss, missing-component, and exception cleanup paths so every probe exit ends PIE once and emits an unambiguous terminal summary. |
| AQ-C10 | `Documentation/Boss/QUEUE_AQ.md`, handoff | Close the attack/lunge driver batch with local-only results and Lead runtime gates clearly separated. |
| AQ-C11 | `Documentation/Boss/AQ_C11_C15_BC_MATRIX.md` | Define baseline/B/C/B+C matrix for both routes and walking/sprinting, retreat/orbit/fixed, look grace, and attack/lunge overlap. |
| AQ-C12 | `Scripts/Editor/test_pie_camera_engage_contract.py` | Contract B+C combined CVar setup and ensure no test claims combined runtime behavior from individual B/C runs. |
| AQ-C13 | `Documentation/Boss/AQ_C11_C15_BC_MATRIX.md` | Specify hide counts/durations, view-to-boss median/p90, look input/reacquisition, distances, and per-route sample identity. |
| AQ-C14 | `Documentation/Boss/AQ_C11_C15_BC_MATRIX.md` | Define start-state reset, independent fresh process runs, CVar reset, cleanup and video/log pairing to avoid contamination. |
| AQ-C15 | `Documentation/Boss/QUEUE_AQ.md`, matrix | Record the matrix as Lead-ready; mark all runtime cells pending until Lead supplies evidence. |
| AQ-C16 | `Scripts/Editor/prepare_aura_choice.py` | Add dry-run-only data plan for current/boosted/boosted-on-spine aura choices; no asset mutation or save in any mode. |
| AQ-C17 | `Scripts/Editor/test_prepare_aura_choice.py` | Add offline contract for option selection, read-only dry-run default, paths and refusal of save/apply requests. |
| AQ-C18 | `Scripts/Editor/prepare_aura_choice.py` | Add explicit rollback/readback manifest output for the three choices, with source values and asset identities required before any future apply. |
| AQ-C19 | `Documentation/Boss/AQ_C16_C20_AURA_CHOICE_PREP.md` | Document owner choice boundary, required asset readback, rollback plan and why the current black-frame comparison is not accepted. |
| AQ-C20 | queue, script, tests, prep doc | Close the aura-choice prep batch with dry-run evidence only; do not edit/save any `.uasset`. |
| AQ-C21 | `Documentation/Boss/AQ_C21_C25_PACKAGE_GATES.md` | Refresh Development-package acceptance for KI-196, KI-198 and KI-199, separating proven PIE behavior from package/cook proof. |
| AQ-C22 | package gates | Add camera B/C package evidence requirements: staged selected config, both-route smoke, no Development-only diagnostic dependency. |
| AQ-C23 | package gates | Specify exact clean stage/build identity, manifests, logs, and artifact retention needed to avoid Development/Shipping contamination. |
| AQ-C24 | `Scripts/Tools/test_aq_package_gates.py` | Add offline contracts that package rows retain current KI status and distinguish PIE from packaged evidence. |
| AQ-C25 | package gates, `Documentation/KNOWN_ISSUES.md` | Reconcile open package statuses and leave KI-196/198/199 and camera package proof open until a real package run. |
| AQ-C26 | `Documentation/Boss/AQ_C26_C30_OPEN_KI_TRIAGE.md` | Census current open KIs and select five non-owner-blocked offline audits with one bounded acceptance each. |
| AQ-C27 | AQ-C26 report, selected source/docs | Audit one selected open KI's source-to-test evidence boundaries; cite exact paths/lines and do not alter runtime behavior. |
| AQ-C28 | AQ-C26 report, selected source/docs | Audit a second independent open KI, separate source facts from runtime/owner evidence, and record concrete next gate. |
| AQ-C29 | AQ-C26 report, selected source/docs | Audit a third independent open KI with a reproducible static check or evidence census. |
| AQ-C30 | `Documentation/Boss/QUEUE_AQ.md`, triage report | Close triage batch and identify any bounded follow-up without claiming open owner/runtime gates. |
| AQ-C31 | `Documentation/Boss/AQ_C31_C35_EVIDENCE_FRESHNESS.md` | Inventory freshness/identity of current Lead evidence for camera and Tier 2 owner-choice work; keep raw artifacts read-only. |
| AQ-C32 | evidence freshness report | Reconcile BUILD IDs, source hashes if present, route names, timestamps, and current disposition; flag missing identity rather than infer. |
| AQ-C33 | evidence freshness report | Cross-check proposal/status docs against the mailbox verdicts and exact evidence directories; list stale claims with file/line. |
| AQ-C34 | `Scripts/Tools/test_aq_evidence_freshness.py` | Add fixtures for current, stale, missing, and mismatched route/build identity; no mutation of raw evidence. |
| AQ-C35 | `Documentation/Boss/QUEUE_AQ.md`, report | Record fresh-evidence audit results and unresolved Lead/owner dependencies. |
| AQ-C36 | `Documentation/Boss/AQ_C36_C40_CAMERA_BOUNDARY_AUDIT.md` | Audit the maintained probe and proposal for nonclaims: AABB/capsule proxy, actual occlusion, input fidelity, combination behavior, package state. |
| AQ-C37 | `Scripts/Editor/test_pie_camera_engage_contract.py` | Add no-side-effect contracts for probe telemetry: it must not mutate component properties, assets, or global defaults. |
| AQ-C38 | camera boundary report | Audit that B hide telemetry is per-local-viewer and does not imply aura/telegraph visibility or multiplayer support. |
| AQ-C39 | camera boundary report | Audit C view/control/boss-angle definitions and sample windows; distinguish the C-1088 run from broader acceptance. |
| AQ-C40 | `Documentation/Boss/QUEUE_AQ.md`, boundary report | Close camera-boundary audit with file/line evidence and explicit runtime limits. |
| AQ-C41 | changed probe/tests | Run focused offline probe and package-matrix contracts; fix only defects introduced by AQ. |
| AQ-C42 | changed Python files | Run syntax checks and inspect exact changes for prohibited `set_editor_property`, asset saves, or destructive operations. |
| AQ-C43 | `Documentation/KNOWN_ISSUES.md`, `Documentation/TASKS.md` | Reconcile AQ implementation state with Lead/owner gates, preserving open package and camera KIs. |
| AQ-C44 | changed docs, `Scripts/Tools/check_doc_links.py` | Check local links and repair only links introduced by AQ. |
| AQ-C45 | `Documentation/Boss/AQ_C41_C45_FINAL_AUDIT.md` | Audit AQ queue census, scoped files, helper API assumptions, no-editor boundary and independent option behavior. |
| AQ-C46 | `Documentation/Boss/QUEUE_AQ.md` | Verify 50 unique ordered AQ IDs, ten five-task batches, and bounded acceptance for every row. |
| AQ-C47 | `Documentation/Boss/AQ_C46_C50_HANDOFF.md`, changed tests/docs | Rerun all scoped offline checks and index exact commands/results. |
| AQ-C48 | AQ handoff, status docs | Fold in latest Claude feedback and hotfix rejected AQ work immediately, without waiting for another review cycle. |
| AQ-C49 | AQ handoff | Index maintained probe usage, Lead-only runtime matrix, evidence paths and remaining owner/package gates. |
| AQ-C50 | `Documentation/TASKS.md`, `Documentation/PROJECT_STATE.md`, `Documentation/Boss/QUEUE_AQ.md` | Close the planned AQ offline work and leave the next Lead/owner gate explicit; no commit/push. |

## Progress

- **AQ-C01–C05:** Complete offline. Authored the 50-row/ten-batch queue; test-first red phase observed for the missing maintained probe, then ported the Lead driver to `Scripts/Editor/pie_camera_engage.py` and added validated modes/speed/look/CVar configuration. B+C is expressible through HideBossInside=1 + LockOnFraming=1 while all unspecified camera switches are forced to 0; this remains untested in PIE. Offline contracts pass 5/5, syntax/AST pass, links 0, diff-check exit 0 (LF/CRLF notices only). Lead source remains unchanged. Lead owns running PIE. See `Documentation/Boss/AQ_C01_C05_CAMERA_PROBE.md`.
- **AQ-C06–C10:** Not started.
- **AQ-C11–C15:** Not started.
- **AQ-C16–C20:** Not started.
- **AQ-C21–C25:** Not started.
- **AQ-C26–C30:** Not started.
- **AQ-C31–C35:** Not started.
- **AQ-C36–C40:** Not started.
- **AQ-C41–C45:** Not started.
- **AQ-C46–C50:** Not started.
