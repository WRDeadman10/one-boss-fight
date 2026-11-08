# Queue AG — ER montage hotfix follow-through

Scope: independently advance documentation and evidence audits for the failed C-994 saved-property check. Antigravity owns asset re-authoring under ENGINE_LOCK; Lead owns the asset readback and PIE hit-test. Codex does not edit assets or operate Unreal/build/cook/package/PIE/benchmark in this lane.

## Batch 1 — five tasks

| ID | Task | Acceptance |
|---|---|---|
| AG-C01 | Reconcile any corrected three-montage t3d/readback against AA-A08 | Check every CollisionTrace instance for template parity and AttackData absence; record file/line evidence for all three. If absent, mark the saved-property gate only, not runtime. |
| AG-C02 | Audit the Lead rerun of P_C992_AIRHITS | Compare both control attacks and both ER air attacks on both routes; require route/build, health deltas, hit logs and attack-data attribution; classify any missing route as incomplete. |
| AG-C03 | Audit evidence chain consistency | Compare Antigravity authoring evidence, Lead asset readback, t3d exports and Lead PIE timing/results; flag stale timestamps, mismatched asset versions or claims that overstate proof. |
| AG-C04 | Refresh GATE-07/KI-193/TEST_PLAN/PROJECT_STATE | Record only evidenced saved properties and runtime results; keep owner review/assignment and cook/package gates distinct. |
| AG-C05 | Close lane and stage the next five-task queue | Include per-task completion/dependency status, identify exact external artifacts still needed, validate five unique IDs, and do not infer a release pass. |

## Progress note — 2026-11-07

Queue AG closes locally. The evidence-chain audit is in `AG_C01_C05_EVIDENCE_CHAIN_AUDIT.md`: AG-C01 has full AttackData-unset exports for GuardCounter/AirLight but lacks the AirHeavy full t3d; AG-C02 found 0 air damage on both routes after re-authoring; AG-C03/C04 refreshed the chain and registries. External dependencies remain open; Queue AH is staged for a source-level diagnosis, without waiting for Lead review.
