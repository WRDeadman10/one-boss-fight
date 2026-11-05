# Queue X X-C036–X-C039 — selected-route release-gate audit

Date: 2026-11-06. Read-only reconciliation of available package receipts, source, and release-policy documents. No package, build, game, Editor, PIE, or asset operation was run.

## X-C036 — packaged selector / first-caller evidence

**WAITING ON LEAD/owner package evidence.** Current policy authorizes the Blueprint `SetSelectedDefinition` route in Shipping (J049=A), but the last documented caller scan found no Content call sites and defers packaged setter proof until a real caller exists (`L026_L030_SHIPPING_SELECTOR_AUDIT.md`; `DECISIONS.md` C-876). No new packaged selector/first-caller receipt, build identity, raw log, or caller inventory was present in the mailbox tail or saved run artifacts. The command-line benchmark/CVar selector remains non-Shipping; that path is not proof of the approved Blueprint setter.

## X-C037 — cooked content manifest and selected-definition closure

**PARTIAL — R6 transfer-kit staged manifests found; identity-bound package proof remains open.** The R6 transfer kit includes Shipping and Development `Manifest_UFSFiles_Win64.txt` files. Shipping contains the three expected H2 roots; comparison against the 156-path `/Game` closure finds 78 present and 78 absent. The missing paths match C-878's previously classified editor-only skeleton-reference categories. BUILD_INFO has no package ID or executable SHA-256, and no UAT log or normalized schema manifest was found, so the staged manifest cannot be bound to the staged executable or used alone to close cook proof. The earlier statement that no manifest was present under `Saved` was too broad because it missed `C:/BenchTransfer/R6/OneBossFight_BenchKit/Saved/StagedBuilds/Windows`. Details and hashes: `Y016_Y020_A7_COOK_MANIFEST_RECONCILIATION.md`. Configured cook roots and historical census remain insufficient substitutes for identity-bound package evidence.

## X-C038 — refusal and visual recovery receipts

**WAITING ON LEAD/owner packaged receipts and owner-visible visuals.** The release packet records Lead G2 v2 PIE refusal results (13/13) for missing and invalid definitions and restoration for an explicit empty selector; screenshots were black in the agent session. The same packet explicitly leaves packaged recovery proof open. The runbook requires fresh-process package identity, raw log, structured snapshot, component inventory, and visible refusal/recovery capture. No new package logs or visual captures were available; PIE results are not promoted to packaged proof.

## X-C039 — fallback and retirement wording

The current release decision is internally aligned in the checked sources: `DECISIONS.md` owner entries J049=A and A7=B; `KNOWN_ISSUES.md` KI-183; `A7_RELEASE_GATE_CHECKLIST.json`; `L026_L030_SHIPPING_SELECTOR_AUDIT.md`; and `P15_A7_PARITY_SUMMARY_DRAFT.md` all retain legacy startup as fallback/parity control until the gates close, permit the Shipping Blueprint setter, and keep CVar/benchmark selectors non-Shipping. The checklist keeps its four gates OPEN. Historical entries documenting earlier gate states are not current policy updates.

## Disposition

No release gate is closed by this audit. The selected path and configured cook root are source/config facts; current packaged closure, selector behavior, and visible recovery remain unproven. Continue X-C041–X-C045 without waiting for Lead review.
