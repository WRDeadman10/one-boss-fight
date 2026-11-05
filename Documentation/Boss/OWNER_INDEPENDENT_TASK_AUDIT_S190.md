# Owner-independent task audit (S190)

Reviewed the remaining Queue C items and the candidate themes in Claude's C-734 instruction. This audit checks whether the work can be prepared from checked-in source/docs and Lead-owned tools without asking the owner to make a new decision, provide assets, or grant account access.

## Remaining Queue C tasks

| Task | Owner intervention needed? | Bounded execution rule |
|---|---|---|
| S191 review-receipt template | No | Draft the five-task report format from existing mailbox receipts and queue rules. |
| S192 Lead hotfix intake guide | No | Document how to capture a rejection and isolate the exact follow-up diff/evidence; no edits to rejected work. |
| S193 fresh-checkout handover validation | No | Walk only existing docs/source paths; record missing dependencies instead of assuming a user-local file. |
| S194 current artifact inventory | No | Inventory repository artifacts and state unknown external ownership as unknown. |
| S195 open-findings disposition table | No | Classify each finding from existing Lead/owner messages; if none exists, record “decision pending” or retained limit rather than deciding for the owner. |
| S196 midpoint review package | No | Assemble already-retained reports, suite receipts, and evidence links; Lead remains the reviewer. |
| S197 final review package | No | Map each assigned item to its existing Lead verdict; do not infer acceptance from a posted completion. |
| S198 Queue C status dashboard | No | Count directly from the task list and receipts; represent missing verdicts as in-review. |
| S199 next-queue proposal delta | No | Compare existing queues and roadmap; duplicate/overlap findings are written as reasons, not silently removed. |
| S200 final consistency pass | No | Reconcile current source authorities and report conflicts; do not resolve product decisions or rewrite historical results. |

These items remain owner-independent when kept inside the listed boundaries. Work that requires a product choice or unavailable artifact is reported as a dependency, not guessed or performed.

## C-734 candidate themes for Queue D

- **Selection/start parity tests:** source/test work can proceed without owner input. Keep tests engine-free when possible; Lead owns the Unreal build/suite run.
- **Parry against the pack boss melee arena driver:** script and expected-sheet preparation are owner-independent. Live Editor execution and build verification are Lead-owned and must be separate tasks/acceptance evidence.
- **Parry visual/sound specification:** source/asset survey and an evidence-backed options spec can proceed. Final asset selection, licensing, or approval is an owner decision; the proposal must stop at alternatives and acceptance criteria until authorized.
- **Gap-closer animation specification:** source/profile/MoveCard feasibility and timing criteria can be prepared. Creating/importing/replacing art or selecting an unapproved clip is out of scope without the asset owner/Lead disposition.
- **Strafe-stuck proof without cage-wall scripts:** an expected sheet, safe setup survey, and telemetry checklist can proceed. Do not run cage-wall authoring/deletion scripts; live setup changes belong to Lead or the content owner.

## Intake rules for Queue D

1. Rank bounded tests, proof scripts/sheets, source audits, and documentation first. No task may depend on owner availability for its stated acceptance.
2. Place new opt-in ideas in a separate section. Give each idea an `EXPECTED` sheet plan with setup, enabled path, default-off/negative control, measurable criteria, required artifacts, and an honest manual-evidence limit. A proposal is not approval to enable or ship it; S188's release gate still applies.
3. If a task needs an owner choice, new licensed/authored asset, external account, or access not in the workspace, scope it to a preparatory survey/spec that records alternatives and the pending decision. Exclude execution that would cross that boundary.
4. Require explicit source/file scope, output artifact, acceptance evidence, and a no-side-effect constraint for every audit/tool task. Lead-owned build/Editor/PIE steps must be listed as verification dependencies rather than performed by Codex.

Result: the remaining Queue C closeout tasks and bounded preparatory versions of every C-734 theme can be performed without owner intervention. Final art/product choices and live Editor verification stay explicit external dispositions; no queue item should assume them.
