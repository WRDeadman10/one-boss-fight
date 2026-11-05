# Queue S35 — Antigravity ledger handover

Date: 2026-11-05. This is a handover index for evidence received from Claude; Codex did not run the editor, builds, packages, or parity pairs.

## Requested rows and evidence

| Work row | Evidence and source of result | Antigravity update requested |
|---|---|---|
| A5 selected-route parity | `Docs/BossCombatReview/Execution/Claude/B_C835_PARITY/`; final all-31-pair disposition in `Documentation/TEST_PLAN.md` (BUILD-221 parity entry) and `Documentation/Boss/P15_A7_PARITY_SUMMARY_DRAFT.md`; Lead order C-868. | Record 31/31 registered driver pairs as Lead-reported complete, with per-pair results and PASS+WARN classifications retained. Do not convert stochastic/sampled WARN rows to exact equivalence or infer release readiness. |
| D1 attach parity | BUILD-220 raw evidence under `Docs/BossCombatReview/Execution/Claude/B_C835_PARITY/`; disposition indexed in `Documentation/DECISIONS.md` C-840 and `Documentation/TEST_PLAN.md`. | Record selected-route component-attach parity and link the actual pair receipts. Keep the claim limited to the tested boss component set. |
| D5 legacy defaults | Lead-run draft/manifest evidence under `Docs/BossCombatReview/Execution/Claude/C852_D5_DEFAULTS/`; 424-leaf audit summarized in `Documentation/Boss/D5_G044_LEGACY_DEFAULT_AUDIT.md` and `Documentation/TEST_PLAN.md`; C-855. | Record 214 MATCH / 0 MISMATCH / 210 NOT-COMPARABLE. Preserve the 210 player leaves as not comparable, not passed. |
| T1 tracker tick order | BUILD-221 build/test artifacts under `Docs/BossCombatReview/Execution/Claude/B_C863_TICKORDER/`; paired A4 `_t1`/`_t1b` captures under `Docs/BossCombatReview/Execution/Claude/B_C835_PARITY/`; C-864/C-865. | Record the same-frame prerequisite test and the two-pair A4 S9 0.05 s result. Leave S9 0.40 s and P06 `world_hits` as boundary-sensitive observations. |
| G2 selection refusal and clear | BUILD-222 live result under `Docs/BossCombatReview/Execution/Claude/C872_G2_REFUSAL_v2/`; 13/13 summarized in `Documentation/TEST_PLAN.md`; C-872. | Record missing-definition and invalid-manifest refusal, no legacy bundle leak, and explicit-clear restoration of LegacyNoSelection. Owner visual review and packaged recovery proof remain open. |

## Canonical ledger mapping note

The current Antigravity canonical witness ledger is `Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json` (version 3.36; 82 requirements). Its requirement IDs do not use the project work labels A5, D1, D5, T1, or G2, and the source scan found no BUILD-218–222 or C-864–876 references in that ledger. Therefore this handover identifies the evidence and requested record updates without changing or guessing a canonical requirement status. Antigravity should map each item to a requirement only where that requirement's observable is directly supported by the cited evidence; otherwise retain it as route/parity evidence in the linked project records.

This distinction keeps the witnessed behavior ledger separate from the A5 route-comparison matrix and from pending owner release gates.
