# Queue O — independent encounter source and tool assurance

**Purpose:** continue Codex-owned static/source/offline assurance while Claude handles live Editor/PIE/build/cook/package work and the owner retains product decisions. This queue ranks the next audits from the unresolved release gates and recent tool hardening. Dynamic claims require retained artifacts; no tests, Unreal execution, commit or push are assigned to Codex here.

## Batch 1 — G044 source contract (O001–O005)

| ID | Task | Owner / acceptance |
|---|---|---|
| O001 | Audit exporter role-to-Blueprint roots and snapshot identity labels. | **Codex:** source paths/schema/scope agree; no CDO values inferred. |
| O002 | Audit snapshot serialization stability for arrays, structs and object references. | **Codex:** document exact canonicalization limits and ordering. |
| O003 | Crosswalk current typed-definition field consumers to `URPGBossDefinition`. | **Codex:** every runtime-consumed value has a source location; no authored asset assumed. |
| O004 | Reconcile nested config struct fields with typed-spec encoding requirements. | **Codex:** field/type gaps listed; current Editor reflection still required for runtime names. |
| O005 | Maintain explicit unknown/historical-value discrepancy inventory. | **Codex + Claude:** only current snapshot can resolve a value; no default promotion. |

## Batch 2 — asset authoring safety (O006–O010)

| ID | Task | Owner / acceptance |
|---|---|---|
| O006 | Audit dual-definition creation order and partial-failure residue behavior. | **Codex:** no destructive cleanup; exact existing/new asset outcome documented. |
| O007 | Audit all pre-save validation paths in typed-definition creation. | **Codex:** failures precede first package save. |
| O008 | Audit recursive readback equivalence for each tagged UE value. | **Codex:** unsupported/unknown encodings refuse before writes. |
| O009 | Reconcile manifest receipt fields with definition readbacks and snapshot hash. | **Codex:** fields and digest contract agree; no receipt invented. |
| O010 | Audit selection creation and validator no-write guarantees. | **Codex:** explicit destinations, read-only validation and current path contract. |

## Batch 3 — selected startup source assurance (O011–O015)

| ID | Task | Owner / acceptance |
|---|---|---|
| O011 | Trace selected startup from subsystem discovery through activation. | **Codex:** exact call order and state owners cited in source. |
| O012 | Crosswalk census refusal predicates to stable diagnostic tokens. | **Codex:** missing/duplicate/invalid state boundaries and native tests cited. |
| O013 | Audit selected activation failure cleanup and legacy-fallback suppression. | **Codex:** retained versus released resources stated exactly. |
| O014 | Audit selection manifest/phase drift checks at startup. | **Codex:** validation order and rejection reason map; no PIE claim. |
| O015 | Record startup source/native/PIE evidence limits. | **Codex:** claim-level readiness stays separate. |

## Batch 4 — rebind and lifecycle source assurance (O016–O020)

| ID | Task | Owner / acceptance |
|---|---|---|
| O016 | Trace reset generation and count ownership through the rebind path. | **Codex:** uint64 authority and broadcast updates cited. |
| O017 | Audit pending-candidate chronology and ambiguity refusal. | **Codex:** candidate identity and reset-order predicates cited. |
| O018 | Audit rebind timeout and cancellation cleanup. | **Codex:** timer/delegate state transition documented. |
| O019 | Audit unsafe-release retention and successful release cleanup. | **Codex:** exact lease/binding ownership; no injected result presented as PIE. |
| O020 | Crosswalk lifecycle source tests to live-session gaps. | **Codex:** transient fixture and PIE scope remain distinct. |

## Batch 5 — parity receipt assurance (O021–O025)

| ID | Task | Owner / acceptance |
|---|---|---|
| O021 | Crosswalk v2 receipt required fields to actual driver observations. | **Codex:** unsupported fields/claims listed; no synthetic run. |
| O022 | Audit paired identity and selected-route identity comparison. | **Codex:** exact comparable keys and exclusions documented. |
| O023 | Audit raw source-log resolution/hash behavior across receipts. | **Codex:** path escape/mutation outcomes explicit. |
| O024 | Crosswalk A4 scenario IDs/ordinals to comparator trial behavior. | **Codex:** missing/extra trials inconclusive; deterministic deltas retained. |
| O025 | Audit exit/status precedence for incomplete and mismatched pairs. | **Codex:** every result class maps to evidence, no false PASS. |

## Batch 6 — graph and cook assurance (O026–O030)

| ID | Task | Owner / acceptance |
|---|---|---|
| O026 | Audit reachable-package traversal for cycles and missing graph nodes. | **Codex:** root-to-edge chain and malformed input behavior documented. |
| O027 | Audit graph/cook build and configuration identity requirements. | **Codex:** v1/v2 compatibility and limits stated. |
| O028 | Audit mount-root preservation and package-name validation. | **Codex:** object/package paths not conflated. |
| O029 | Audit normalizer source/output alias and overwrite safeguards. | **Codex:** raw input preservation and destination behavior confirmed. |
| O030 | Reconcile package-tool claims with target-binary proof requirements. | **Codex + Claude:** graph/cook PASS is not packaged activation. |

## Batch 7 — performance receipt assurance (O031–O035)

| ID | Task | Owner / acceptance |
|---|---|---|
| O031 | Audit packaged metric identity completeness and same-session matching. | **Codex:** all run identity fields and limits documented. |
| O032 | Audit cold/warm phase/sample uniqueness behavior. | **Codex:** absent protocol/counts remain owner/Lead decisions. |
| O033 | Audit raw-log hash and report-destination alias safeguards. | **Codex:** path, symlink and hard-link outcomes documented. |
| O034 | Audit nearest-rank summary edge cases and metric scope separation. | **Codex:** no mixed units/scopes or inferred thresholds. |
| O035 | Audit evidence limits for supplied metric values. | **Codex:** tool output cannot claim a metric was read from its log. |

## Batch 8 — evidence pack verifier assurance (O036–O040)

| ID | Task | Owner / acceptance |
|---|---|---|
| O036 | Audit strict membership enumeration including symlink refusal. | **Codex:** unlisted paths cannot hide behind directory links. |
| O037 | Audit absolute, traversal and resolved-outside manifest paths. | **Codex:** all failure paths return diagnostics. |
| O038 | Audit duplicate lexical/canonical paths and hard-link treatment. | **Codex:** alias limits and exact verifier guarantees documented. |
| O039 | Audit byte-count/hash requirements and source-reference membership. | **Codex:** each claim ties to bytes in the same pack. |
| O040 | Audit manifest/companion exemptions and evidence retention contract. | **Codex:** exempt files are explicit; no empty-pack success inferred. |

## Batch 9 — product decision and release gates (O041–O045)

| ID | Task | Owner / acceptance |
|---|---|---|
| O041 | Refresh J049's current evidence inventory from new artifacts. | **Codex:** only dated/source-backed changes; owner choices remain explicit. |
| O042 | Incorporate the Editor Blueprint caller inventory when supplied. | **Codex + Claude:** exact callsites and migration impacts retained. |
| O043 | Reassess production-default prerequisites. | **Codex + Owner:** no default change without accepted selected and control evidence. |
| O044 | Reassess Shipping selector prerequisites and approved route. | **Codex + Owner:** no binary readiness claim without choice and package proof. |
| O045 | Reassess performance budget and legacy-retirement prerequisites. | **Codex + Owner:** comparable measures and dated decisions only. |

## Batch 10 — status and handover (O046–O050)

| ID | Task | Owner / acceptance |
|---|---|---|
| O046 | Refresh claim-level readiness matrix from current retained evidence. | **Codex:** claims stay scoped to their actual evidence. |
| O047 | Update recovery instructions only from observed run outcomes. | **Codex + Claude:** preserve failure attempts and exact tokens. |
| O048 | Reconcile TASKS, PROJECT_STATE, KNOWN_ISSUES and TEST_PLAN. | **Codex:** all statuses and evidence limits agree. |
| O049 | Validate the next queue's IDs, owners, ranking and acceptance. | **Codex:** exactly 50 unique sequential task IDs. |
| O050 | Close Queue O as a work cycle only if evidence/status reconcile. | **Codex:** no feature/release completion inferred. |
