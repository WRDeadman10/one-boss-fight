# Queue C next-queue scope delta (S199)

## Sources compared

- Current Queue C proposal: `Documentation/Boss/QUEUE_200_C_PROPOSAL.md`, tasks S1–S200.
- Prior Codex Queue B proposal and status snapshot: `Docs/BossCombatReview/Execution/Codex/QUEUE_200_B.md` and `Documentation/Boss/QUEUE_200_B_HANDOVER.md`.
- Earlier 50-task order: `Docs/BossCombatReview/Execution/Codex/QUEUE_50.md`.
- Active roadmap/current evidence boundaries: `Documentation/TASKS.md`, `PROJECT_STATE.md`, `TEST_PLAN.md`, and Claude's C-734 Queue D order.

This is a scope comparison, not a new task authorization. The previous queues and active Queue C continuation contain direct topic overlaps; each is listed with a distinct purpose or a proposed supersession so repeated work is visible.

## Direct and near overlaps with disposition

| Earlier scope | Queue C overlap | Disposition / reason |
|---|---|---|
| Queue B R199: create a ranked 200-task Queue C proposal. | Queue C S199: compare Queue C against completed queues/roadmap before preparing the next queue. | Sequential, different deliverables: R199 generated this queue; S199 audits its scope for the next one. No second Queue C proposal is intended. |
| Queue B R200: final consistency pass. | Queue C S200 has the same broad title and reconciles the same core docs. | Direct duplicate by name and purpose. Treat C S200 as the single final pass after the additional Queue C work; it supersedes the unfinished B R200 closeout for the current checkout. Do not run two separate final passes. |
| Queue B R196–R198: fresh-session handover with read order, commands, queue state, and opt-in proof status. | Queue C S193: validate the active fresh-checkout handover and current task pointer. | Successor, not a second historical handover: C validates and refreshes the current state after later receipts and Lead changes. The B handover is retained as a historical snapshot. |
| Queue B R121–R125 proposal table says “Release-readiness checklist for a boss profile.” | Queue C S188 defines a feature/profile proof release gate. | Similar release-evidence purpose, but the recorded R121–R125 implementation in TASKS/TEST_PLAN is an eight-step profile-field authoring workflow, not a release checklist. Keep S188 as the release evidence gate; reconcile the stale/mismatched R121–R125 proposal label before declaring the old checklist delivered. |
| Queue B R191–R195: documentation consistency after both queues. | Queue C S195/S198/S200: findings dispositions, queue counts, final doc reconciliation. | Distinct intermediate outputs: S195 assigns action/status to open findings, S198 counts active continuation states, and S200 is the final reconciliation. The older consistency sweep is not a substitute for current counts or Lead verdicts. |
| Queue B R126–R160 and Queue 50 Batch 8: create/extend log, evidence, compare, scaffold, and link tools. | Queue C S170–S180: path/atomicity/cleanup/input/network/import/determinism/redaction/header/usage/index audits. | Complementary safety/maintenance audits, not duplicate tool implementations. Keep each only where its acceptance checks a distinct failure class; do not recreate already-listed tools. |
| Queue 50 Batch 1 W2–W5 wiring and Batch 2–5 C++/player/encounter audits. | Queue C S161–S169 editor-script and offline wrapper audits. | Different file surfaces and failure modes: Queue 50 concerns runtime C++/wiring; C161–C169 inspect Python/PowerShell editor and wrapper tooling. |
| Queue 50 Batch 10 parry stamina wiring and overlay parry line; Queue C S108–S111 parry/overlay checklists. | C-734 Queue D asks for parry visuals/sound specification and pack-boss melee parry driver. | The new D themes must remain scoped: the old checklist covers player stamina cost and overlay state visibility; it does not specify authored VFX/SFX timing/assets or prove the pack boss's melee reaction in an arena. Do not repeat the player-side checks. |
| Queue 50 task 2 W3 stuck recovery; Queue C S16/S112/S113/S151 and KI-149 track stuck recovery. | C-734 asks for a strafe-stuck proof that does not use cage-wall scripts. | Existing work is implementation, status audit, alternate-setup survey, telemetry expectation, and failure catalogue; the live `strafe_stuck` event remains unproven. A new proof task is justified only as an alternate geometry/driver experiment with measured setup and normal-end control; no cage-wall script reuse. |
| Queue B R191–R195 and Queue C S11/S195 both touch open issues. | S11 compares the open-issue digest to the full issue register; S195 maps unresolved Codex findings to Lead/owner actions or limits. | Different completeness criteria: one checks digest parity, the other assigns dispositions. S195 must not duplicate the entire digest. |
| Queue C S3 and S6 both address restart/result-counter scope. | S3 requests a recommendation separating lifetime and generation totals; S6 requests a source/log matrix for the same counters. | Related tasks are nonduplicate only if S6's matrix is the evidence input to S3's recommendation. Keep their outputs cross-linked; avoid commissioning a second independent counter audit. |
| Queue C S1/S5 both cover selection/start parity. | C-734 Queue D also names selection-vs-start parity tests. | C S1 is the all-path audit and S5 the exact missing regression proposals. Queue D should carry forward only uncovered paths/test gaps identified by their verdicts, not repeat the broad audit. |
| Queue C S8/S9 both compare proof status and terminology. | Queue D evidence-focused work may revisit proof labels. | S8 flags mismatched proof claims; S9 standardizes vocabulary. Future work should test the vocabulary against new evidence only, not redo either survey. |
| Queue C S14/S15 and S196/S197/S198 all touch queue receipts/status. | The midpoint/final packages and dashboard are current review artifacts. | Different layers: S14 audits receipt completeness, S15 reconciles Queue B records, S196 presents first-ten evidence, S197 requests per-task Lead verdicts, and S198 counts the active S163–S200 slice. Use the existing audit result as input; do not run another receipt census without new messages. |

## Queue D themes from C-734

1. Selection/start parity is already an explicit Queue C audit/test pair (S1/S5); carry forward only verdict-identified uncovered start paths.
2. Pack-boss melee parry requires a new arena driver and Lead-owned live run; existing player-side parry wiring/proof and old-move KI-154 do not establish this behavior.
3. Parry visuals/sound should be an authored presentation specification with setup/asset/timing and a control. Existing parry overlay/state checklists are not a substitute.
4. Gap-closer animation is not covered by the compared queue titles; treat it as a specification/measurement task until an owner/Lead selects an asset.
5. Strafe-stuck live proof has a clear gap (KI-149; S16/S112/S113/S151); a new task is justified only with a non-cage setup and explicit event plus normal-end criteria.

Per C-734, any future opt-in feature proposals belong in a separate section and each needs an `EXPECTED` sheet plan. Audits, tests, and proof scripts should precede those opt-in proposals. No product choice, asset selection, or live Editor run is authorized by this delta audit.

## Queue source discrepancy

The Queue B proposal's R121–R125 acceptance text and the recorded R121–R125 deliverable disagree: the proposal says release-readiness checklist, while TASKS/TEST_PLAN say the eight-step opt-in profile-field workflow and list the resulting `PROFILE_FIELD_HOWTO.md`. S199 does not rewrite that historical proposal. Reconcile the title/status in the final consistency pass or a Lead disposition; until then the workflow can be treated as delivered, but the separate broad checklist cannot be claimed from that receipt.

## Result

No undocumented same-deliverable duplication is recommended for the next queue. The explicit same-title R200 pass is superseded by the final C S200 pass; S188/R121–R125 remains a documented source discrepancy requiring reconciliation. The C-734 candidate themes above have distinct evidence boundaries and named overlap rules for Queue D planning.
