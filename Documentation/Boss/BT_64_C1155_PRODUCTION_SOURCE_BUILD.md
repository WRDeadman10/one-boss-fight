# BT-64 — C-1155 Production Source Build and DD27j Suite

Date: 2026-11-16 17:54 UTC
Status: passed; source and build validation only.

## Result

- Unreal Development build: exit 0.
- DD27j-pinned `OneBossFight` automation suite: 574 started, 574 passed, 0 failed; suite exit 0.
- Manifest SHA256: `cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`.
- All nine source/runner hashes bound in the lead approval matched after build and suite.
- C-1155 locks: 2 created, 2 released, none retained.
- Scope remained pre-authoring: no PIE, asset write/rebind, package, or cook.

## Evidence

Run directory: `Saved/C1619RouteBuild/Run_20261116_175430_dcc1dd6e`

The runner emitted `status.json` and `route_lead_approval.json`. The fresh lead input receipt is `Saved/C1619RouteBuild/LeadApproval_BT64_20261116T1754Z.json`.

## Next Gates

Antigravity's BT-63 source runner is not yet accepted. It currently reads build-gate fields that BT-64 does not emit, allows `-SkipBuildGate` beyond dry-run, and does not verify restored profile bytes after rollback. After source-only hotfix and lead review, execute locked profile authoring/rebind; then run BT-62 fresh route Smoke. Raw BehaviorTree attack-task tick instrumentation remains `BLOCKED_NOT_INSTRUMENTED`, so the build/suite pass alone is not gameplay acceptance or a playable-build claim.
