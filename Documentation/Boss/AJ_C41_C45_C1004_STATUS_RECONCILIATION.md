# AJ-C41–C45 — C-1004 status reconciliation

Date: 2026-11-07  
Authority: Claude C-1004, Antigravity A-607, and the mailbox-derived latest status.  
Status: Documentation correction only.

## Drift found and corrected

Several current-status paragraphs still said the AirHeavy hit was -16 HP and the post-A-607 rerun was pending. C-1004 supersedes that snapshot: Lead PIE r5 on both routes reports AirLight -16.0 HP / JumpLight / DefaultMeleeAttackData and AirHeavy -22.4 HP / JumpHeavy / StrongMeleeAttackData, matching pack controls. The ER air-hit runtime check is therefore closed at that recorded scope.

Updated current status in `AA_A08_NOTIFY_FRAMES_TABLE.md`, `GATE07_ANIMATION_REVIEW.md`, `ER_PLAYER_CONTROLS_SPEC.md`, `KNOWN_ISSUES.md` KI-193, `PROJECT_STATE.md`, and `TEST_PLAN.md`. The older C-995 paragraph in AA-A08 is retained as a dated historical snapshot and explicitly marked superseded. KI-193 now remains open for owner review, any approved saved-field assignment, and separate cook/package proof; it no longer lists the completed air-hit rerun as pending.

## Validation boundary

This was a source-document/mailbox reconciliation. No new PIE, build, test, asset edit, or package operation was performed. C-1004 is reported Lead evidence; Codex did not independently rerun the routes. The guard-counter live hit is a separate open test in C-1004 and remains pending.
