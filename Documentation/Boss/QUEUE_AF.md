# Queue AF — next five-task lane

Scope: audit the C-992 montage hotfix return and update release evidence. No Codex asset edit, Editor, build, cook, package, PIE, or benchmark run without a specific later order.

## Batch 1 — post-hotfix verification handoff

| ID | Task | Acceptance |
|---|---|---|
| AF-C01 | Reconcile Antigravity's post-C-992 montage readback and t3d exports against AA-A08 | CollisionTrace properties (AttackData unset), timings, MovementCancel ordering, and 0.100 s ER blend-in checked by file/line |
| AF-C02 | Audit Lead's rerun of P_C992_AIRHITS when it arrives | Compare control and ER results on both routes; require damage and attack-data evidence; classify any missing arm as incomplete |
| AF-C03 | Reconcile corrected montage timing behavior with the Lead PIE matrix | Blend-in/trace/cancel ordering claims separated from saved-asset values and actual runtime observations |
| AF-C04 | Refresh GATE-07, KI-193 and TEST_PLAN from the new receipts | Update only from Lead readback/PIE artifacts; keep owner review/assignment and cook gates separate |
| AF-C05 | Prepare the next five-task lane and owner/Lead handoff | Current evidence, exact remaining dependencies, and validated unique IDs; no release decision inferred |

One batch of five tasks; no waiting for review is required to continue independent documentation work.

## Progress note — 2026-11-07

`Documentation/Boss/AF_C01_C05_HOTFIX_PROGRESS_AUDIT.md` records the new Lead evidence: the four 0.100 s blend-ins and corrected air timings are present, but all three attack t3d exports still report AttackData present. AF-C01 reconciled with a failed saved-property criterion; AF-C02 classifies the dependent Lead hit-test as externally pending/incomplete. AF-C03 timing audit, AF-C04 evidence refresh and AF-C05 next-lane staging are complete. Queue AG is active; no Lead review wait is needed for independent documentation work.
