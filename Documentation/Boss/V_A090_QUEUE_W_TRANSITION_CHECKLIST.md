# V-A090: Queue W Transition Checklist & 50-Task Ledger

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** Complete  
**Scope:** Formal ratification of the 50 tasks allocated to Lane A (`W-A001..W-A050`) in [`Documentation/Boss/QUEUE_W.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_W.md), structured into 10 executable batches.

---

## 1. Context & Authority

Per Lead Claude directives [`[C-930]`](file:///c:/UnrealProject/OneBossFight/Documentation/TEAM_MAILBOX.md#L23950) and [`[C-932]`](file:///c:/UnrealProject/OneBossFight/Documentation/TEAM_MAILBOX.md#L23970), Queue W was authored by the Lead to govern operations post-BUILD-232/234. This checklist formally integrates the 50 Antigravity lane task IDs (`W-A001..W-A050`) and establishes the execution prerequisites for transitioning from Queue V to Queue W upon completion of `V-A100`.

---

## 2. 50-Task Master Roster (`W-A001..W-A050`)

### Batch 1: Evidence Rule Enforcement & Citation Repair
* [ ] **W-A001:** Re-check `V-A032`, `V-A033`, and `V-A077` figures against raw sources; replace unsupported claims with citations or `PROPOSAL` tags.
* [ ] **W-A002:** Add an explicit "Sources" line to every `V-A` document that contains an empirical measurement.
* [ ] **W-A003:** Author automated scanner (`Scripts/Tools/scan_doc_citations.py` + tests) detecting uncited numbers.
* [ ] **W-A004:** Execute scanner and eliminate 100% of uncited claims across documentation.
* [ ] **W-A005:** Submit Batch 1 receipt.

### Batch 2: Second Review of Codex Source & Lifetime Symmetry
* [ ] **W-A006:** Review BUILD-233 Source diff (startup route logs, dead helper removal, config key) against inclusion and default rules.
* [ ] **W-A007:** Audit Tier 2 presentation hooks for lifetime symmetry (Director, Legend, Parry: every Push has matching Pop on reset/death/teardown).
* [ ] **W-A008:** Audit `AM_Boss01_A2` preview clip override logic (`rpg.AttackTracker.A2PreviewClip`).
* [ ] **W-A009:** Verify CVar compilation guards across Development and Shipping configurations.
* [ ] **W-A010:** Submit Batch 2 receipt.

### Batch 3: Verification of Queue W Test Hardening
* [ ] **W-A011:** Second review of Codex test additions in `RPGPresentationRulesTests.cpp`.
* [ ] **W-A012:** Validate Editor timing range AST guard and transitive alias tracing (`test_timing_range_independence.py`).
* [ ] **W-A013:** Audit comparator regression fixtures using BUILD-231 retained observables.
* [ ] **W-A014:** Verify static symbol guards in `Scripts/CheckShippingFeatureSymbols.py`.
* [ ] **W-A015:** Submit Batch 3 receipt.

### Batch 4: Stage Footprint & Cook Manifest Review
* [ ] **W-A016:** Review Codex Shipping binary symbol check results.
* [ ] **W-A017:** Validate staged folder cook manifest schema against H2 closure paths.
* [ ] **W-A018:** Formulate texture LOD group clamping configuration patch for `DefaultEngine.ini`.
* [ ] **W-A019:** Review unreferenced asset retention/deletion list (`V_A039`) with Asset Registry.
* [ ] **W-A020:** Submit Batch 4 receipt.

### Batch 5: Documentation Archiving & Rebuild Verification
* [ ] **W-A021:** Run doc link checker; ensure `broken_links=0`.
* [ ] **W-A022:** Run line count guard on modified files.
* [ ] **W-A023:** Execute approved `git mv` migration of 694 historical docs to `Documentation/Boss/Archive/`.
* [ ] **W-A024:** Audit living `PROJECT_STATE.md` structure against recovery copies.
* [ ] **W-A025:** Submit Batch 5 receipt.

### Batch 6: Owner Performance Intake & Preset Formulation
* [ ] **W-A026:** Review Round 6 owner benchmark results (upon owner delivery).
* [ ] **W-A027:** Evaluate measured DLSS 4.5 frame pacing vs TSR baseline.
* [ ] **W-A028:** Formulate final 1080p / 60 FPS performance preset.
* [ ] **W-A029:** Review owner feedback on brazier shadow selection (L1/L2 profiles).
* [ ] **W-A030:** Submit Batch 6 receipt.

### Batch 7: Visual & Combat Polish Verification
* [ ] **W-A031:** Validate ribbon emitter implementation for scythe swing trails.
* [ ] **W-A032:** Inspect sub-bass acoustic thump sample for successful parries.
* [ ] **W-A033:** Review camera shake decay curve damping during boss impacts.
* [ ] **W-A034:** Verify footstep dust puff particle emitter bounds (`< 0.02 ms`).
* [ ] **W-A035:** Submit Batch 7 receipt.

### Batch 8: Packaging Verification & Binary Stripping
* [ ] **W-A036:** Dry-run `Scripts/ShippingSmoke.ps1` with symbol verification.
* [ ] **W-A037:** Confirm removal of PDBs and debug libraries from staged Shipping payload.
* [ ] **W-A038:** Verify package size delta against 4.35 GB baseline.
* [ ] **W-A039:** Validate IoStore container integrity.
* [ ] **W-A040:** Submit Batch 8 receipt.

### Batch 9: Release Candidate Audit & Gate Certification
* [ ] **W-A041:** Execute full Track B witness status ledger census.
* [ ] **W-A042:** Validate requirements automation coverage matrix across all 82 canonical IDs.
* [ ] **W-A043:** Review all 9 formal release gates from `V_A048`.
* [ ] **W-A044:** Draft Release Candidate certification note (`rc-v0.9.0`).
* [ ] **W-A045:** Submit Batch 9 receipt.

### Batch 10: Queue W Close-Out & Tag Preparation
* [ ] **W-A046:** Final repository clean-up and untracked file sweep.
* [ ] **W-A047:** Confirm commit hygiene across all Queue W commits.
* [ ] **W-A048:** Run full offline test suite and ensure 100% green status.
* [ ] **W-A049:** Prepare release tag commit request for Lead Claude.
* [ ] **W-A050:** Submit final Queue W close-out receipt.

---

## 3. Transition Prerequisites
Prior to launching task `W-A001`:
1. Queue V Lane A must reach task `V-A100` with all intermediate receipts posted.
2. Fast offline verification suite must remain 100% green (369/369 PASS).
3. Track B ledger must remain 100% green (80 WITNESSED / 2 PARTIAL / 0 NOT YET, 4/4 PASS).
4. Repository formatting and line-count guards must pass without warnings.
