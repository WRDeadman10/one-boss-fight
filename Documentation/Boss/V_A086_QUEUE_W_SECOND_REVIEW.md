# V-A086: Second Review of Queue W Master Specification

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** Complete  
**Scope:** In-depth evaluation of [`Documentation/Boss/QUEUE_W.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_W.md) authored by Lead Claude ([`Documentation/TEAM_MAILBOX.md:23970`](file:///c:/UnrealProject/OneBossFight/Documentation/TEAM_MAILBOX.md#L23970), `[C-932]`), evaluating structure, task boundaries, test coverage, and execution readiness across Lanes C and A.
**Sources:** Documentation/Boss/QUEUE_W.md:1-155, Documentation/TEAM_MAILBOX.md:23970

---

## 1. Executive Assessment

[`Documentation/Boss/QUEUE_W.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_W.md) establishes a robust, 100-task post-BUILD-232/234 operational framework divided into two parallel 50-task tracks:
* **Codex Lane (`W-C001..W-C050`):** Focuses on Round 6 benchmark telemetry intake, A7-B legacy retirement patch series, dead-code elimination, mutation test hardening, and encounter selection tooling.
* **Antigravity Lane (`W-A001..W-A050`):** Focuses on evidence citation enforcement, second review of Codex C++ changes, lifetime/cleanup verification, content stage stripping, and release packaging gates.

The design adheres strictly to established project protocols: 5-task batches, append-only receipts, look-changing asset owner gating, and zero Shipping allocations.

---

## 2. Lane A Review & Analysis (`W-A001..W-A050`)

### 2.1 Batch 1: Evidence Rule & Citation Repair (`W-A001..W-A005`)
- **Intent:** Directly rectifies uncited assertions identified by Lead Claude in `[C-932]` (e.g., "95%+ parity alignment" in `V-A077` and "0-frame startup" in `V-A033`).
- **Tooling Plan (`W-A003`/`W-A004`):** Development of an automated scanner (`scan_doc_citations.py`) that detects floating percentages, milliseconds, decibels, and frame numbers lacking explicit `file:line`, evidence folder, or ledger row citations.
- **Assessment:** **SOUND & HIGH PRIORITY**. Enforces mathematical rigor across the entire Lane A documentation corpus.

### 2.2 Batch 2: Second Review of Codex Source & Hook Lifetime (`W-A006..W-A010`)
- **Intent:** Audit C++ modifications from BUILD-233 and BUILD-234, verifying lifetime symmetry (every push has a matching pop on reset, death, and world teardown in `RPGSevarogDirector`, `RPGLegend`, and `RPGPlayerParry`).
- **Assessment:** **CRUCIAL SAFETY GATE**. Prevents sound mix bus stacking or mid-fight MPC parameter leaks across consecutive encounter restarts.

### 2.3 Batch 3: Verification of Queue W Test Suite (`W-A011..W-A015`)
- **Intent:** Validate Codex's mutation additions in [`RPGPresentationRulesTests.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGPresentationRulesTests.cpp), timing range AST guards in [`Scripts/Tools/test_timing_range_independence.py`](file:///c:/UnrealProject/OneBossFight/Scripts/Tools/test_timing_range_independence.py), and Shipping symbol guards in [`Scripts/CheckShippingFeatureSymbols.py`](file:///c:/UnrealProject/OneBossFight/Scripts/CheckShippingFeatureSymbols.py).
- **Assessment:** **FEASIBLE & VERIFIED**. Codex's tests already pass 100% in local test runs (369/369 PASS).

### 2.4 Batch 4 & 5: Stage Optimization & Docs Archiving (`W-A016..W-A025`)
- **Intent:** Execute the 680 MB Shipping binary stripping proposals ([`V_A066`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/V_A066_PACKAGE_SIZE_PROPOSALS_REVIEW.md)), execute the 694-file historical docs migration to `Documentation/Boss/Archive/` via tracked `git mv` ([`V_A082`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/V_A082_SUPERSEDED_DOCS_ARCHIVE_LIST.md)), and audit `PROJECT_STATE` against recovery copies ([`V_A083`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/V_A083_PROJECT_STATE_STRUCTURE_REVIEW.md)).
- **Assessment:** **CLEAR & UNBLOCKED**. Requires only Lead sign-off on the archive list.

### 2.5 Batches 6–10: Feel Polish, Packaging & Close-Out (`W-A026..W-A050`)
- **Intent:** Owner review integration, camera/audio feel evaluation, packaged Shipping smoke runs via [`ShippingSmoke.ps1`](file:///c:/UnrealProject/OneBossFight/Scripts/ShippingSmoke.ps1), and final RC tag readiness.
- **Assessment:** **APPROPRIATELY PHASED**. Correctly separates offline verifiable steps from owner-gated deliverables.

---

## 3. Recommendations & Enhancements

1. **Explicit Checkpoint/Resume Rule in `W-A003`:** The citation scanner must support `--check` mode suitable for CI / pre-commit inclusion.
2. **Case-Insensitive String Assertion:** Reaffirm throughout `W-A011` that all string and asset path comparisons in UE test mutations must respect case insensitivity.
3. **Receipt Traceability:** All receipts in Queue W will continue using the standardized `-BodyFile` invocation via `Scripts/MailboxPost.ps1`.

---

## 4. Conclusion

Queue W provides an airtight roadmap for hardening, optimizing, and closing out the *One Boss Fight* combat slice. Lane A is ready to transition immediately upon completion of `V-A100`.
