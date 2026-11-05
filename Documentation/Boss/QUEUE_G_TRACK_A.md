# Queue G — Track A data-driven platform, then verified gaps

**Owner:** Codex implementation/docs; Claude owns builds, Unreal/PIE, and review. **Delivery:** five-task batches; one X- report per batch, or per task when Source changes. Continue without waiting for review. When starting G045, prepare the next 50-task queue. Never commit or push.

Queue order starts with Track A from `Docs/BossCombatReview/Execution/Claude/ROADMAP_AND_BACKLOG_2026-10-30.md`. A7 remains owner-gated; no retirement work is authorized. C-800 accepted the G1 architecture and the selected startup route is implemented as an opt-in path. Claude owns build/Unreal/PIE and reviews; the owner alone decides production default and binary/content scope.

## Execution status (2026-11-04)

- **G001–G006: DONE.** G006's startup ordering and legacy side-effect map is in `G2_STARTUP_ACTIVATION_SOURCE_MAP.md`.
- **G007–G009: IMPLEMENTED** under C-800/C-801. G010 startup tests now cover selected-mode success, no-selection legacy behavior, empty/duplicate census, undefined phase, unresolved definition, malformed manifest, and unavailable catalog epoch. Claude built the earlier snapshot (BUILD-209, 433/433); the latest added cases await Lead rerun.
- **G012–G015: PARTIAL.** G012 tests selected-phase/definition mismatch; G013 adds unresolved definition and selected-route missing epoch; G014 adds subsystem teardown/repeat teardown coverage; latest cases await Lead rerun. C-803 accepts G015 fail-closed same-world respawn as interim only. Its transient-world test was dropped in C-806 because `UWorld::BeginPlay()` did not put the GameInstance-owned fixture into begun play; the test could not reach the late-spawn branch without fabricating world state. The F4-compatible live order driver is the evidence path. Under C-804 Step A, a native post-reset multicast notification and `[EncounterLifecycle]` spawn/reset/broadcast/release timestamp tokens are added, with no rebind behavior. Claude's live PIE order measurement is pending; implement rebind only after that measured order. This blocks a production default. G016–G018 remain complete; comparator tests pass 8/8.
- **G028–G030: NO SOURCE CHANGE.** C-801 released literal-only migration with unchanged formula/evaluation order. A6 rows 3–4 are formulas, not literals; they are recorded as `kept in code: formula`. No authorable field or matching old literal exists to test, so no promotion is warranted.
- **G031–G035: DISPOSITION COMPLETE / PREFLIGHT LEAD-RUN.** No remaining confirmed literal-only fields exist in rows 1–10, so no schema or boundary test was added. G033 requires Editor asset identity/readback on the reference boss draft and is handed to Claude; G035's hardcoded-value disposition is recorded in `G4_A6_ROWS_1_10_REFRESH.md`.
- **G016–G018: DONE.** The live registry has 40 standard drivers, not the roadmap's stale 31; see `G3_PARITY_DRIVER_INVENTORY.md` and `Scripts/Tools/compare_encounter_parity.py`.
- **G019–G023: LEAD-RUN / PREREQUISITE-BLOCKED.** The opt-in data activation route exists, but no typed boss/player assets or canonical manifest receipt exist; Claude must create/validate content and run paired Editor/PIE evidence. No parity is claimed.
- **G024–G027: DONE.** `G4_A6_ROWS_1_10_REFRESH.md` rechecks all ten active audit rows, corrects stale citations/unsupported symbols, classifies values, and applies C-801's compatibility rule.
- **G028–G030: NO SOURCE CHANGE.** A6 rows 3–4 are formulas, not literals; disposition is `kept in code: formula` under C-801. No data field qualifies for bit-identical migration.
- **G041/G043: DONE.** `G5_D108_D110_LIFECYCLE_RECONCILIATION.md` reconciles current model/actor tests and retained BUILD-65/66 live results. G043 is met by existing model window cleanup assertions.
- **G042: BLOCKED** because current supported public setup does not initialize the native boss actor for a success/death restart matrix; no production hook or synthetic pack-health workaround is authorized.
- **G044 PACKAGE: DONE / LIVE RUN: LEAD-RUN.** `G044_ENCOUNTER_SELECTION_PIE_EXPECTED.md` has Setup/Control/PASS/FAIL sections and passes `Scripts/Tools/lint_expected_sheets.py`; `Scripts/Editor/create_g044_encounter_definition.py` passes Python AST parsing and refuses overwrite. Claude's Editor/PIE run still needs typed boss/player definitions and a canonical manifest receipt.
- **G045: DONE.** Prepared `QUEUE_H_TRACK_A.md` with exactly 50 ranked tasks and per-task acceptance; it preserves owner gates and requires no waiting between batches.
- Continue with unblocked Queue H audit/offline-tool work; do not wait between batches.

## Batch 1 — A3 binding and selection decision (G001–G005)

| ID | Bounded task | Acceptance |
|---|---|---|
| G001 | Write the one-page binding-source and boss-selection-store decision brief from DD30 options and current source. | Select an in-plan architecture, cite current source/chronology, distinguish Lead decision from owner scope, name touched files and tests. **Done:** `Documentation/Boss/G1_BINDING_SELECTION_DECISION.md`. |
| G002 | Reconcile DD30's manifest/epoch claims with the production compiler and catalog APIs. | Record the actual authority for content epoch, manifest hash, phase, and definitions with source lines; list mismatches in G1 brief without claiming runtime provenance. |
| G003 | Specify encounter-selection record fields and deterministic resolution/refusal order. | Contract covers exact boss/player definitions, slots, selected phase, encounter identity, manifest string, missing/duplicate/ambiguous cases, and no implicit first-phase fallback. |
| G004 | Specify selection-store lifetime and world/respawn behavior. | State GameInstance/world ownership, reset boundary, stale actor handling, and how a new pawn is recensed; no raw pawn pointer persists across respawn. |
| G005 | Send the G1 recommendation and the single product/scope decision, if any, to Claude. | One X- message identifies the chosen additive design and leaves only the production definition/default-content choice owner-gated. |

## Batch 2 — A4 fail-closed activation design and implementation (G006–G010)

| ID | Bounded task | Acceptance |
|---|---|---|
| G006 | Map `OnWorldBeginPlay` ordering, census, current `Attach` side effects, and the activation seam. | A source map lists exact call order and which legacy components must not attach to the framework boss after data-path selection. |
| G007 | Implement the approved selection resolver and transient binding input. | **Implemented under C-800.** Exact one boss/player census and matching typed definitions/selections; no level-map edit. |
| G008 | Implement fail-closed activation in the subsystem. | **Implemented under C-800.** Selected-mode failures report, disable/hide the framework boss and its component ticks/collision, and do not invoke legacy boss attachment; player-only setup (including footsteps) remains independent. Runtime verification is Lead-owned. |
| G009 | Implement user-visible refusal reporting and owned activation cleanup. | **Implemented under C-800.** Actionable on-screen message, structured error token, teardown release, and transient binding cleanup. Runtime verification is Lead-owned. |
| G010 | Add startup integration checks for success and each fail-closed branch. | **Authored; Lead rerun pending.** Startup tests cover record validation, no-selection legacy startup, selected-mode successful activation, empty/duplicate census, undefined phase, unresolved definition, invalid manifest and missing catalog epoch. Intended hard-error logs use `AddExpectedError`. |

## Batch 3 — A4 lifecycle and failure tests (G011–G015)

| ID | Bounded task | Acceptance |
|---|---|---|
| G011 | Test empty and duplicate boss/player census. | **Authored.** Real subsystem-path automation checks empty and duplicate boss/player census, no binding, no legacy bundle, and the stable refusal token; Lead must execute it. |
| G012 | Test definition/selection mismatch and invalid phase. | **Authored:** record collisions and a selected phase missing from the boss definition are refused with stable tokens before a binding is spawned. Lead execution pending. |
| G013 | Test missing/invalid manifest and unavailable catalog epoch. | **Authored; Lead rerun pending:** malformed hash shape/alphabet, unresolved boss definition and selected-route missing catalog epoch refuse before/during activation without legacy fallback. |
| G014 | Test successful lease release and repeated teardown. | **Authored; Lead rerun pending:** subsystem `Deinitialize` releases owned activation/binding, preserves player-only components, and tolerates repeated teardown; existing API test also covers idempotent release. |
| G015 | Test respawn/restart generation boundaries. | **Interim policy accepted (C-803):** fail closed on same-world late respawn, release the activation lease, and disable/hide the framework boss; this blocks a production default. Transient startup automation was removed in C-806 because the GameInstance-owned transient world did not enter begun play, so it could not reach the runtime-spawn branch honestly. C-807 supplies a Lead-run F4 driver to measure the real pack order. Rebinding design/test plan is H001; Step B awaits that measurement. |

## Batch 4 — A5 parity packet and driver coverage (G016–G020)

| ID | Bounded task | Acceptance |
|---|---|---|
| G016 | Inventory all current standard PIE drivers and classify activation dependencies. | Each of the 40 registered standard drivers is mapped to data activation, legacy control, or not applicable with exact script and expected activation tokens. |
| G017 | Prepare paired data-path/legacy-control run protocol. | Same map, seed, assets, timing and driver args; capture build identity, raw logs, activation result, gameplay outcome and component census. |
| G018 | Implement offline comparison of paired driver receipts. | Compares only declared parity fields; missing run identity/tokens fails closed; does not parse source to pretend behavior was tested. |
| G019 | Run data-path parity on the first five eligible drivers. | Claude-owned raw run evidence records each pass/failure/inconclusive and mismatched observable; no aggregate claim from skipped drivers. |
| G020 | Run parity on the next five eligible drivers and triage differences. | Evidence references G018 report and includes a bounded reproduction for every mismatch. |

## Batch 5 — A5 remaining parity and A6 audit refresh (G021–G025)

| ID | Bounded task | Acceptance |
|---|---|---|
| G021 | Run parity on eligible drivers 11–20. | Same paired protocol; report every run, skip, and inconclusive with evidence path. |
| G022 | Run parity on eligible drivers 21–30, then 31–40. | Same paired protocol; do not claim 40/40 if any driver is ineligible or incomplete. |
| G023 | Reconcile all parity deltas against owner/Lead-approved behavior. | Each difference is fixed, explicitly accepted, or marked unresolved; no silent normalization of the control. |
| G024 | Recheck A6 audit rows 1–5 against current active Source. | Correct file/line/value/consumer and default behavior; exclude retired classes from active counts. |
| G025 | Recheck A6 audit rows 6–10 and identify missing current values. | Every active finding has verified consumer, current default, existing profile/card alternative, and test gap. |

## Batch 6 — A6 migration decisions and first promotions (G026–G030)

| ID | Bounded task | Acceptance |
|---|---|---|
| G026 | Classify each audited number as gameplay tuning, safety invariant, diagnostic, or schema bound. | A6 refresh explains why only gameplay tuning belongs in authorable data; no mechanical constant is exposed without need. |
| G027 | Propose bit-identical profile fields for confirmed gameplay-tuning gaps. | For every proposed field, include current default, units, validation range, adapter, consumer and focused test before source edits. |
| G028 | Implement the first approved profile field and adapter. | **No candidate:** A6 rows 3–4 contain formulas, not literals. C-801 requires same formula/order; disposition is `kept in code: formula`. |
| G029 | Add direct automation for the first field's default, boundary, invalid and caller behavior. | **Not applicable:** no field is promoted, so no artificial default-profile test is added. |
| G030 | Implement and test the next approved profile field as a separate Source change. | **No candidate:** preserve formula in code; no profile field is justified by the audited rows. |

## Batch 7 — A6 remaining confirmed data seams (G031–G035)

| ID | Bounded task | Acceptance |
|---|---|---|
| G031 | Add remaining confirmed gameplay fields in a bounded schema/adapter increment. | **No candidate:** no remaining literal-only gameplay fields are confirmed by A6 rows 1–10. |
| G032 | Add boundary and default automation for that increment. | **Not applicable:** no field is promoted; no synthetic schema/test is added. |
| G033 | Run profile asset preflight on the reference boss draft. | **Lead-run:** Claude must inspect/execute the Editor asset preflight and record asset identity/readback; Codex does not run Unreal. |
| G034 | Verify authoring/manifest/adapter parity for the new fields. | **Not applicable:** no new fields exist under the C-801 compatibility rule. |
| G035 | Update the hardcoded-value audit disposition. | **Done:** each retained value is classified; rows 3–4 say `kept in code: formula`, other rows identify invariant/diagnostic/schema disposition. |

## Batch 8 — verified runtime requirement gaps (G036–G040)

| ID | Bounded task | Acceptance |
|---|---|---|
| G036 | Reconcile the 83-row ledger and partial plan after A4/A5. | Current row IDs, witnessed status, raw evidence and remaining data-path blockers agree; do not alter external ledger ownership. |
| G037 | Select the highest-ranked unresolved runtime requirement with an existing deterministic driver. | One-row packet states prerequisites, actor/content evidence, exact tokens, control, and what Codex versus Claude runs. |
| G038 | Fill a confirmed pure-rule coverage gap for that requirement. | A named executing C++ automation case covers a meaningful boundary/invalid transition and preserves current defaults. |
| G039 | Add or tighten its observable runtime telemetry only if required by the row. | Schema is strict, backward compatibility is tested, and every token maps to a source emission and driver assertion. |
| G040 | Prepare the paired live proof for the selected requirement. | Fresh unique evidence paths, declared control, acceptance/refusal rules, and no unsupported status promotion. |

## Batch 9 — actor/lifecycle gaps with scoped claims (G041–G045)

| ID | Bounded task | Acceptance |
|---|---|---|
| G041 | Reconcile D108/D110 lifecycle findings with current automation and live evidence. | Remaining gaps distinguish actor behavior from pure/model evidence and cite exact tests/logs. |
| G042 | Add the narrowest feasible native actor lifecycle test for a confirmed gap. | Test uses supported native actors/world setup; no synthetic pack-health workaround and no production-only hook. |
| G043 | Add terminal cleanup assertions for owned windows/components where reachable. | Normal finish, death and failure cases assert idempotent cleanup and preserved unrelated state. |
| G044 | Run the selected encounter-definition PIE route (`rpg.EncounterDefinition`). | **Package complete for Claude:** new asset path, refusal-safe script and expected sheet are ready; live run is Lead-owned and blocked until typed boss/player definitions and the manifest receipt exist. |
| G045 | Package the first 44-task outcomes and prepare Queue H. | Queue H contains exactly 50 ranked tasks, cites current remaining gaps, and is posted before G050. |

## Batch 10 — content, cook and release evidence gaps (G046–G050)

| ID | Bounded task | Acceptance |
|---|---|---|
| G046 | Reconcile required runtime soft references against cook/staging rules. | Every required definition dependency has explicit cook evidence; editor-only success is not packaged proof. |
| G047 | Add a focused offline manifest/cook-plan fixture for a verified missing dependency. | Fixture catches the specific gap, is temporary-root isolated, and does not launch Unreal or mutate project content. |
| G048 | Prepare a fresh packaged data-path smoke protocol. | Claude-owned steps specify Shipping binary identity, default selection, no debug CVar, failure output, and exact runtime evidence. |
| G049 | Reconcile owner decisions needed for the next data-driven milestone. | Only product defaults, irreversible binary/content edits, or feature-scope choices remain; each has a safe default and cited source. |
| G050 | Close Queue G evidence and publish the next-batch status. | Counts include completed, blocked, skipped, and Lead-run tasks; every claim links its receipt/log/test and states runtime limits. |

## Owner-gated boundary

Retiring the legacy attach path (roadmap A7), choosing the production boss/hero definition and authorizing edits to `L_SevarogArena.umap` are not part of Queue G execution without owner approval. For an unanswered product choice, leave selection unset and fail closed. Claude's written in-plan design decisions release additive code tasks; they do not authorize binary map edits or changing product scope.
