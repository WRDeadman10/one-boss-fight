# Queue I — actionable data route and lifecycle preparation

**Owner:** Codex owns source, tests, documentation and offline tools; Claude owns Unreal builds, native automation execution, Editor/PIE and live/package evidence. **Cadence:** ten batches of five, one X report per batch, continue without waiting for review. Owner gates remain production defaults, Shipping selection policy, main-map changes and product scope. Never commit or push.

**Entry state (C-805–C-809):** C-804 Step A is implemented and accepted (X-1114); it adds reset notification/log tokens without rebind. BUILD-211 measured the legacy order and C-809 approved Step B: selected-route respawn is pending on spawn, then reset-broadcast-triggered release/census/compile/activate with a 5 s timeout and uint64 generation guards. Typed boss/player definition assets and canonical manifest receipt are still absent; they remain prerequisites for Claude's selected-mode PIE run.

**How to use this queue:** execute in five-task reports and continue without waiting for Lead review; Claude reviews/builds while Codex advances. Newer approvals supersede earlier prerequisites. Mark genuine asset/runtime/owner dependencies as blocked or Lead-run, author honest automation where native execution is unavailable, and keep those runtime results separate from source completion.

## Batch 1 — definition authoring inputs (I001–I005)

| ID | Task | Acceptance |
|---|---|---|
| I001 | Map existing pack boss/player roots and available typed-definition source values. | **Done:** `I001_TYPED_DEFINITION_SOURCE_MAP.md` records exact class/package paths, historic mesh/skeleton/capsule facts, named boss animations, typed schema, and still-unread fields. No fabricated phase or Greystone subclass; no asset write. |
| I002 | Add a read-only Editor CDO snapshot exporter for the boss and player Blueprints. | **Prepared:** `Scripts/Editor/export_encounter_definition_sources.py` captures reflected class/component properties to a new timestamped JSON; labels values as CDO defaults, refuses timestamp collision, never saves a package. Claude owns execution/readback review. |
| I003 | Add refusal-safe Editor authoring for the two typed definition assets. | **Prepared:** `Scripts/Editor/create_g044_typed_definitions.py` refuses overwrites and requires both complete explicit source specs, all soft refs and every nested leaf citation before creating either asset. Full readback assertions precede both saves. Runtime asset creation remains LEAD-RUN. |
| I004 | Define canonical membership-manifest generation from the two typed definitions. | **Prepared:** `Scripts/Editor/write_g044_manifest_receipt.py` snapshots exact reflected authored values, sorts canonical JSON, refuses receipt overwrite, and hashes selection identity plus both definitions. G044 selection creation now recomputes and checks the digest. |
| I005 | Add an offline validator for generated definitions/manifest receipts. | **Done:** `Scripts/Tools/validate_encounter_manifest.py` checks schema, paths, required fields and canonical digest; `test_validate_encounter_manifest.py` contains six isolated fixtures (6/6 reported in the prior run). |

## Batch 2 — data-route automation hardening (I006–I010)

| ID | Task | Acceptance |
|---|---|---|
| I006 | Reconcile G010/G013/G014 test declarations with C-806 hotfix. | **Reconciled:** selected success/refusal and teardown cases match C-806's token correction and fixture limitation; current native run remains Lead-owned. |
| I007 | Add direct selection-record validation tests for malformed GUID, empty slots, duplicate slots and invalid manifest shape. | **Authored, unrun:** production record validator now asserts GUID, empty/duplicate slots, phase, malformed manifest and role-definition collision tokens. |
| I008 | Add direct selection-store lifecycle tests for replacement, clear, reinitialize and per-GameInstance isolation. | **Partial, unrun:** replacement/clear and per-GameInstance isolation are asserted. Explicit subsystem reinitialize lifecycle is not covered. |
| I009 | Add binding-census tests for wrong-world, already-begun actor, duplicate actor identity and missing target. | **Authored, unrun:** cross-world binding, begun-actor refusal, duplicate boss/player census and empty census are covered without publishing a partial binding. |
| I010 | Add activation rollback tests for binding destruction and owned-component cleanup failures. | **Partial, unrun:** selected startup compiler refusal destroys binding and generic activation registration faults clean owned components. Combined selected-route cleanup-failure injection is still open. |

## Batch 3 — generation and rebind Step B preparation (I011–I015)

| ID | Task | Acceptance |
|---|---|---|
| I011 | Specify participant-generation ownership and initial-value semantics. | **Done:** `I011_PARTICIPANT_GENERATION_CONTRACT.md` defines per-world uint64 ownership, actor identity, initial nonzero generation, no wrap and the current int32 widening gate. |
| I012 | Add a pure generation-advance rule with MAX refusal. | **Done:** `RPGEncounterGenerationRules::CanAdvance` rejects zero, non-increasing values and MAX_uint64 with stable refusal tokens. |
| I013 | Add tests for generation advance, duplicate reset notification and overflow preservation. | **Authored:** direct automation covers valid, duplicate, late, zero and exhausted values; Lead build/run remains pending. |
| I014 | Draft the narrow `CompileWorldInputForRebind` API contract. | **Done:** `I014_REBIND_COMPILER_CONTRACT.md`; original compiler API remains strict pre-BeginPlay; same selection and explicit generation are required. |
| I015 | Draft the rebind transaction/rollback state machine against Step A log tokens. | **Done:** `I015_REBIND_TRANSACTION.md` records the C-809 5 s pending timeout, release-before-census order, duplicate idempotence and fail-closed paths. |

## Batch 4 — selected-route correctness tests (I016–I020)

| ID | Task | Acceptance |
|---|---|---|
| I016 | Add selected-route test for missing GameInstance catalog epoch. | **Existing coverage retained:** `UnavailableCatalogEpochFailsClosed` expects `WorldInput.NoContent`, checks inactive boss/no binding and retained player setup. |
| I017 | Add selected-route test for malformed and unresolved typed definitions. | **Existing coverage retained:** startup tests distinguish malformed manifest, undefined phase and unresolved typed-definition refusal before activation; fail-closed cases register expected log tokens. |
| I018 | Add selected-route test for two GameInstances with distinct catalog epochs. | **Authored:** `GameInstancesCannotShareBindings` asserts distinct epoch identities and rejects world A's binding when compiled against world B. |
| I019 | Add idempotence tests for reset multicast subscriber removal. | **Authored:** `ResetBroadcastRebindsAndDeduplicates` validates the bound reset callback, same-generation duplicate no-op and stale-generation fail-closed; subsystem teardown removes the delegate and lease. |
| I020 | Add reset event payload tests for generation/count update order. | **Existing coverage retained:** `ResetBroadcastAfterStateUpdate` checks the event fires once with both state fields already incremented; pure generation tests cover zero, duplicate and exhausted sources. |

## Batch 5 — parity receipt tooling (I021–I025)

| ID | Task | Acceptance |
|---|---|---|
| I021 | Extend the H006–H010 receipt schema with selected-definition and participant-generation identity. | **Done:** v2 schema adds route/selection/manifest, ordered boss/player identities and generation, full run identity and terminal result; v1 remains readable. |
| I022 | Add a pure receipt builder used by one eligible PIE driver. | **Partial:** encounter_parity_receipt.py builds and atomically writes from explicit captured facts without touching logs; no current PIE driver can yet supply the full envelope. |
| I023 | Add data-route receipt emission to the same driver behind an explicit opt-in argument. | **Blocked on runtime capture source:** the driver API does not expose selected definition, manifest, activation/component census, or generation. No fabricated receipt or driver behavior change. |
| I024 | Add receipt verifier fixtures for identity drift, malformed digest and missing participants. | **Authored, unrun:** isolated unit fixtures cover selected identity, malformed SHA-256, missing boss/player, and unchanged raw-log bytes. |
| I025 | Add paired-report output that references source logs and receipt hashes. | **Implemented, unrun:** report includes both receipt paths/hashes and per-observable log citations; v2 unmatched/missing trial correspondence is INCONCLUSIVE; atomic JSON output. |

## Batch 6 — authored content graph, downstream (I026–I030)

| ID | Task | Acceptance |
|---|---|---|
| I026 | Validate the generated boss definition against the reference boss asset. | **Blocked:** no authored definition asset or CDO export/readback exists; refusal-safe exporter/creator are prepared under I002–I003. |
| I027 | Validate the generated player definition against the pack player asset. | **Blocked:** same missing authoring/readback prerequisite; do not fill unknown fields from defaults. |
| I028 | Generate the canonical manifest receipt from validated assets. | **Blocked:** canonical writer/validator exist, but validated saved boss/player assets are unavailable. |
| I029 | Generate the G044 encounter selection asset from validated definitions. | **Blocked:** script is prepared and refuses overwrite; prerequisites are absent, so it has not been run. |
| I030 | Validate the full soft-reference graph and expected cook roots. | **Partial:** normalized graph verifier is authored; no authoritative graph export or UE cook manifest exists for this selection. |

## Batch 7 — measured-order rebind implementation (I031–I035)

| ID | Task | Acceptance |
|---|---|---|
| I031 | Convert Claude's H019 raw run into an event-order table. | **Done:** `I031_BUILD211_EVENT_ORDER.md` records raw hash, timestamps, generation/count, actor IDs and absent selected-route tokens without extending the legacy evidence claim. |
| I032 | Reconcile the measured order with H001 transaction design. | **Done:** I015 transaction follows the measured spawn → detection → broadcast order; C-809 approved broadcast as the Step B trigger. |
| I033 | Implement the narrow begun-world compiler entry point after approval. | **Implemented, unbuilt:** `CompileWorldInputForRebind` carries the same selection and explicit generation; strict existing preflight remains for the original API. |
| I034 | Implement generation-keyed rebind transaction after approval. | **Implemented, unbuilt:** reset subscription/removal, release-before-activate, duplicate/stale guards and MAX refusal are in the selected-route subsystem. |
| I035 | Implement fail-closed rollback for any rebind stage. | **Implemented, unbuilt:** cleanup failure retains unsafe binding/lease; other failures disable the selected boss, avoid legacy fallback and preserve independent player setup. Claude owns build/runtime proof. |

## Batch 8 — rebind automation (I036–I040)

| ID | Task | Acceptance |
|---|---|---|
| I036 | Test successful new-pawn re-census under the measured event order. | **Authored, unrun:** success test checks replacement actor identity, original selection GUID, generation 2, and exactly one active binding. |
| I037 | Test missing/duplicate pawn after reset. | **Authored, unrun:** missing pending player and duplicate live players each expect a stable HardError, no active binding, disabled boss; player-only setup is asserted for census refusal. |
| I038 | Test duplicate reset notification and stale generation callbacks. | **Existing, unrun:** success lifecycle test verifies duplicate no-op and stale-generation HardError; no double registration is checked. |
| I039 | Test compiler, activation and cleanup failure rollback at each rebind stage. | **Partial, unrun:** compiler/no-catalog failure checks no binding, inactive boss and retained independent player setup. Activation-stage and cleanup-failure injection remain unavailable. |
| I040 | Add reset/rebind lifecycle property test over repeated generation sequences. | **Partial, unrun:** seeded 256-step generation monotonicity property authored; runtime active-lease-count/release property remains unproved. |

## Batch 9 — parity, cook, performance (I041–I045)

| ID | Task | Acceptance |
|---|---|---|
| I041 | Add receipt support for the next five eligible standard drivers. | **Blocked:** runtime capture seam is absent (I023); driver IDs/markers are inventoried, but truthful receipts need active selection/generation/census exposure. |
| I042 | Add independent negative-control receipt cases. | **Authored, unrun:** v2 paired fixtures accept matching identity/value, flag input-hash drift, and classify unmatched trial IDs as INCONCLUSIVE; no source-text gameplay inference. |
| I043 | Add package-manifest verifier for the authored selection graph. | **Implemented, unrun:** normalized graph/cook-manifest verifier prints a reachable root-to-package chain; unrelated staged entries are ignored. No UE cook inputs exist yet. |
| I044 | Add a deterministic local cost-report parser for Lead run receipts. | **Implemented, unrun:** cold/warm receipt parser preserves sample identities, calculates nearest-rank p50/p95/p99 and returns INCONCLUSIVE for missing or mixed identities. No measured selected-route samples exist. |
| I045 | Reconcile source, tests and offline reports into Queue J. | **Done:** `QUEUE_J_TRACK_A.md` contains 50 unique ranked items across ten batches, with runtime/cook/performance evidence boundaries and owner gates explicit. |

## Batch 10 — blocked gates and handover artifacts (I046–I050)

| ID | Task | Acceptance |
|---|---|---|
| I046 | Refresh designer workflow after Step B acceptance. | **Done:** workflow reflects C-809-approved broadcast rebind and timeout while clearly marking implementation unbuilt/unwitnessed. |
| I047 | Audit Queue I task receipts and hotfix outcomes. | **Done:** this table records Done/Partial/Blocked/Authored-unrun/Lead-run for I001–I050; no unreviewed receipt is called accepted. |
| I048 | Refresh milestone, TASKS and TEST_PLAN status. | **Done:** current authored automation/tooling is distinguished from Claude-run build, PIE, cook and cost proof. |
| I049 | Prepare scoped release-readiness decision packet. | **Done:** `I049_OWNER_DECISION_PACKET.md` separates opt-in data route, Shipping selector, production default and legacy retirement; owner gates remain explicit. |
| I050 | Close Queue I with scoped handover to Queue J. | **Done with residuals:** `I050_QUEUE_HANDOVER.md` transfers I partials, blockers and Lead-run evidence to Queue J without claiming feature completion. |

## LEAD-RUN list (outside the 50)

- **LR-01 — post-C-809 native suite:** Claude builds current source and runs the full suite, reporting exact totals and failures after X-1121/X-1124.
- **LR-02 — definition authoring/readback:** after source validation, run refusal-safe boss/player scripts and G044 preflights; retain asset readbacks and canonical manifest proof.
- **LR-03 — selected data-route PIE:** after LR-02, exercise startup, successful rebind and refusal in the approved pack arena; retain activation/census/terminal receipts.
- **LR-04 — paired parity and capture:** after I023 capture integration, run legacy and selected-data A4 arms and retain exact logs, command inputs and v2 receipts.
- **LR-05 — cook/package:** after authored roots exist, retain the authoritative cook manifest and target-binary load proof.
- **LR-06 — performance/soak:** after packaged activation works, capture identified cold/warm samples and lifecycle soak; owner decides budget/Shipping/default/retirement.

## Sequencing and authority

Queue I completion and handover are recorded in `I050_QUEUE_HANDOVER.md`; Queue J is the continuation. BUILD-211 and C-809 supply the approved Step B trigger, but selected-route implementation remains unbuilt/unwitnessed until LR-01/LR-03. Claude owns engine execution and native suite results. Definition values must come from exact source readback, never guessed. Shipping selection, production defaults, main-map changes and legacy retirement remain owner-only decisions.
