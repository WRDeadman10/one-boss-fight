# Queue H — data-driven activation, parity, and release evidence

**Owner:** Codex for source/docs/offline tools; Claude for build, Unreal/PIE and review. **Cadence:** ten batches of five; report after each batch and continue without waiting. Rejected items are immediate hotfixes; re-run the relevant Lead-owned validation on the next cycle. Never commit/push. Owner-only choices remain production boss/hero defaults, main-map/binary edits, or product-scope changes.

**Basis:** Queue G G001–G045 status in `QUEUE_G_TRACK_A.md`; C-800 accepted the additive typed encounter definition, GameInstance selection store, and transient binding architecture. The opt-in startup route is implemented, but source boss/player assets, same-world respawn rebind, and paired data-path evidence remain open. A7 legacy retirement and production default remain owner-gated. Every task below must preserve those boundaries and mark decision-dependent work BLOCKED while taking independent tasks next.

**H019 status (C-808):** Revised F4 live-order driver, runner and expected sheet are prepared in `Docs/BossCombatReview/Execution/Codex/H019_ORDER/`. The earlier run was inconclusive: health was written to zero at 10.02 s, but no death/respawn occurred. The revision wakes the boss, enters player combat, starts A4, writes health zero during the active action, enables the diagnostic overlay, and records health/death-tag changes. Claude owns the rerun; Step B still depends on measured event order.

## Batch 1 — decisions and source contract (H001–H005)

**Status (2026-11-04):** H001 design, H002 source/API map, H003 lifecycle receipt proposal, H004 sequencing audit, and H005 scope plan are documented in `H001_RESPAWN_REBIND_DESIGN.md` and `H002_H004_SELECTION_CONTRACT_MAP.md`. C-804 accepted the reset multicast and Step A instrumentation; live pack PIE must measure ordering before Step B rebind. No post-BeginPlay epoch behavior is claimed.

| ID | Task | Acceptance |
|---|---|---|
| H001 | Design same-world respawn rebinding for selected encounter data. | Identify the pack respawn/reset signal, exact re-census point, new participant generation, same selection-record reuse, safe release/reactivation order, failure policy, and a focused test plan; no code until Claude decides. |
| H002 | Reconcile DD30 selection, manifest, epoch and phase contracts against current compiler and catalog APIs. | Updated source map with file/line citations and explicit unproved runtime claims. |
| H003 | Freeze the minimal versioned selection receipt contract for the approved design. | Typed fields, stable refusal tokens, identity/freshness rules, no ambiguous fallback. |
| H004 | Audit world-start/late-spawn sequencing constraints for the proposed resolver. | Exact BeginPlay boundary and supported respawn path, or explicit fail-closed block. |
| H005 | Publish the accepted additive source/API plan. | One Lead-facing report separates released code scope from owner-gated product/default/map decisions. |

## Batch 2 — offline evidence tooling (H006–H010)

**Status (2026-11-04):** H006–H007 examples, H008 isolated temporary-root fixtures, H009 deterministic atomic JSON report option, and H010 maintainer guide are complete. `python Scripts/Tools/test_compare_encounter_parity.py` passes 8/8. Fixtures are expressly synthetic; no driver emits them yet.

| ID | Task | Acceptance |
|---|---|---|
| H006 | Define a machine-readable receipt example for a legacy driver. | Complete v1 JSON fixture bound to build/content/settings/input identity and registered marker. |
| H007 | Define the paired data-route receipt example. | Same identity tuple, fresh run ID, explicit selection/activation result and component census. |
| H008 | Add isolated fixtures for the parity comparator's PASS, mismatch, and inconclusive outcomes. | Temporary-root fixtures; missing/extra observable and identity drift fail closed; no engine launch. |
| H009 | Add comparator output serialization for CI/evidence bundles. | Deterministic JSON report, stable status codes, atomic output; no input mutation. |
| H010 | Document receipt capture and comparator invocation. | Maintainer guide links exact command, schema, exit codes and known no-data-route limitation. |

## Batch 3 — activation implementation after decision (H011–H015)

| ID | Task | Acceptance |
|---|---|---|
| H011 | Implement approved selection-store lifetime and reset semantics. | GameInstance/world boundary follows approved G1 choice; no raw pawn survives respawn. |
| H012 | Implement exact pre-BeginPlay actor census and typed definition resolution. | Missing/duplicate/ambiguous actor or definition refuses before registration. |
| H013 | Create a transient encounter binding from the accepted exact census. | Existing compiler/activation APIs remain source-compatible unless Lead explicitly approves. |
| H014 | Integrate activation lease ownership into world subsystem teardown. | Game-thread/idempotent release, only owned registrations removed. |
| H015 | Suppress legacy boss Attach side effects only after successful data-path decision. | No fallback on refusal; unrelated player-only setup remains intact. |

## Batch 4 — activation refusal and cleanup automation (H016–H020)

| ID | Task | Acceptance |
|---|---|---|
| H016 | Add native automation for empty and duplicate actor census. | Real subsystem route returns stable refusal and no legacy boss bundle. |
| H017 | Add mismatch tests for selected definition, phase and manifest. | No partial component registration; original actor state preserved. |
| H018 | Add success/repeated teardown tests for the activation lease. | Owned objects are removed exactly once; unrelated pre-existing components survive. |
| H019 | Add a supported respawn/new-generation test. | New pawn identity is recensused; stale pawn cannot retain the new binding. |
| H020 | Run the focused activation suite after implementation. | Claude records exact build identity, test IDs/counts and logs; Codex does not run Unreal. |

## Batch 5 — parity driver migration (H021–H025)

| ID | Task | Acceptance |
|---|---|---|
| H021 | Add receipt emission to the first eligible registered driver. | Driver declares gameplay observables and exact activation fields; legacy behavior unchanged. |
| H022 | Add receipt emission to eligible drivers 2–10. | No source-grep substitute; outputs satisfy schema and preserve marker minima. |
| H023 | Add receipt emission to eligible drivers 11–20. | Each migrated driver identified by registered script and has a paired-input contract. |
| H024 | Add receipt emission to eligible drivers 21–30. | Noneligible cases are named and excluded explicitly. |
| H025 | Add receipt emission to eligible drivers 31–40. | Full current standard registry accounted for; optional `-Full`/balance excluded separately. |

## Batch 6 — paired runtime parity (H026–H030)

| ID | Task | Acceptance |
|---|---|---|
| H026 | Run paired legacy/data parity on first five eligible drivers. | Fresh raw outputs, identical build/content/settings/seed/input, comparator report per pair. |
| H027 | Run pairs for the next five eligible drivers. | Every pass/failure/inconclusive has a source receipt and named observable. |
| H028 | Run pairs for eligible drivers 11–20. | No aggregate percentage hides skipped or partial drivers. |
| H029 | Run pairs for eligible drivers 21–40. | Report each driver separately; optional modes remain outside denominator. |
| H030 | Triage and resolve parity deltas. | Each delta is fixed, explicitly accepted by the right authority, or remains blocked with reproduction. |

## Batch 7 — data schema and behavior (H031–H035)

**Status (2026-11-04):** H031 re-audit complete; H032–H035 are BLOCKED because activation integration revealed no confirmed literal-only gameplay field with an unchanged formula/default to migrate. See the H031 addendum in `G4_A6_ROWS_1_10_REFRESH.md`. Do not create a placeholder schema field; resume only if a qualifying live consumer/value is found.

| ID | Task | Acceptance |
|---|---|---|
| H031 | Re-audit active gameplay-number candidates after activation exists. | Exact live consumers/defaults; separate tuning from invariant, diagnostics and schema limits. |
| H032 | Propose one confirmed profile field with bit-identical default. | Units/range/default/adapter/consumer and compatibility proof before source change. |
| H033 | Implement the approved first field and adapter. | Invalid values fail closed; ordinary default preserves prior behavior. |
| H034 | Add direct executing automation for default, boundaries and invalid inputs. | Tests reach helper/consumer behavior, not text search. |
| H035 | Reconcile authoring/manifest/compiler/adapter/runtime parity. | Exact types, names, units, defaults and validation match end to end. |

## Batch 8 — lifecycle and requirement evidence (H036–H040)

**Status (2026-11-04):** H036 read-only ledger reconciliation is complete in `H036_LEDGER_RECONCILIATION.md`. The current JSON remains v3.36 at 75/7/0; later Claude disposition is 80/82 witnessed with QA-001/005 owner-closed, pending Antigravity's JSON reconciliation. H037–H040 are BLOCKED: no currently open gameplay requirement is supported by an existing registered driver; the five actionable rows are Lead-accepted closed and the two QA rows require owner actions. Do not invent a new runtime requirement or rerun closed proofs.

| ID | Task | Acceptance |
|---|---|---|
| H036 | Reconcile current framework witness ledger after G/H activation work. | Antigravity-owned JSON stays untouched; report exact status/source evidence and gaps. |
| H037 | Select the highest-ranked unresolved runtime requirement supported by a driver. | One-row packet states actor/content prerequisites, control, tokens and owner of each run. |
| H038 | Add the narrowest supported actor-level lifecycle automation for that row. | Native supported setup, no production-only hook or synthetic pack-health workaround. |
| H039 | Add terminal cleanup assertions for the selected requirement. | Owned windows/components cleaned once; unrelated state preserved where reachable. |
| H040 | Run the focused requirement suite and live proof. | Claude records exact test and raw run IDs; no witness promotion without source evidence. |

## Batch 9 — cooking, packaging and performance (H041–H045)

**Status (2026-11-04):** Static audit and measurement protocol are in `H041_H044_COOK_PACKAGE_PERF_AUDIT.md`. H041 is BLOCKED on authored definition assets and actual cook-manifest/package evidence; directory cook rules alone are insufficient. H042 is BLOCKED because no verified cook-plan defect exists to fixture. H043 protocol is prepared, but Shipping execution is blocked: selection is currently via nonshipping CVar or unapproved production default, with no approved Shipping selector. H044 source cost/ownership map and measurement plan are complete, with no numeric budget claim. H045 is Lead-run and blocked on approved selector plus prerequisites.

| ID | Task | Acceptance |
|---|---|---|
| H041 | Reconcile typed definition soft references with cook/staging rules. | Every required dependency has explicit cook evidence; editor-only success is excluded. |
| H042 | Add an isolated offline fixture for a verified manifest/cook-plan gap. | Fixture catches the specific defect in a temporary root without Unreal or content writes. |
| H043 | Prepare a fresh packaged data-path smoke protocol. | Shipping binary identity, default selection, no debug CVar, exact refusal and success evidence. |
| H044 | Audit packaged data-path startup cost and memory ownership. | Source-derived budgets plus a Claude-run measurement plan; no unsupported performance claim. |
| H045 | Run the first approved packaged smoke and profile. | Claude captures exact binary/content identity, logs and measured result; no map/default change without owner approval. |

## Batch 10 — handover and next queue (H046–H050)

**Status (2026-11-04):** H046 designer workflow, H047 decision register, H048 evidence/status audit, H049 `QUEUE_I_TRACK_A.md`, and H050 scoped handover are complete. Queue I contains exactly 50 ranked tasks. H019, H021–H030, H032–H035, H037–H042 and H045 remain blocked; H020 is Lead-run; H043 has a completed protocol but blocked execution. No release-readiness or feature-complete claim is made.

| ID | Task | Acceptance |
|---|---|---|
| H046 | Refresh the designer workflow for typed encounter definitions. | Safe create/validate/select steps, no overwrite, error routing and evidence limits. |
| H047 | Reconcile unresolved Lead/owner decisions for the next milestone. | Only actual owner-boundary decisions remain; each has a cited safe default and impact. |
| H048 | Audit queue status/evidence links against current source and mailbox. | Complete/blocked/Lead-run counts reconcile; no stale task claims. |
| H049 | Prepare Queue I with exactly 50 ranked tasks from verified residual gaps. | Unique IDs, files and measurable acceptance; before H050. |
| H050 | Close Queue H evidence and hand over. | Every task has receipt/status/dependency; no runtime or release claim exceeds evidence. |

## Gate and sequencing rules

Under C-804, H011–H018 are delivered by the accepted G implementation/tests; H019 rebind automation and H020 Lead run await the measured live order. While awaiting that run, continue independent offline tools, audit, docs, cook and performance tasks. Do not retire legacy attach, change production default definitions, edit the main binary map, or change product scope without owner authorization. Do not report parity until both routes have matching run identity and emitted receipts.
