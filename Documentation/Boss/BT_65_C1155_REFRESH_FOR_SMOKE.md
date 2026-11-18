# BT-65 — C-1155 Refresh for Smoke Player-Health Gate

Date: 2026-11-16 18:04 UTC
Status: passed.

The Smoke acceptance driver changed to require the observed player health current/max values to equal 800/800. A fresh approval was generated and the locked C-1155 Development build plus complete DD27j suite were run against those current hashes.

- Development build: exit 0.
- DD27j suite: 574 started / 574 passed / 0 failed; exit 0.
- Manifest: `cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`.
- Updated route driver hash: `6896C2D37AA0F7836027AE0AE02E83627BB5905DB8DB778492D2423B312917C3`.
- Locks: 2 acquired / 2 released; none retained.
- No PIE, assets, package, or cook.

Evidence is in `Saved/C1619RouteBuild/Run_20261116_180407_2f383983`; lead approval is `Saved/C1619RouteBuild/LeadApproval_BT65_20261116T1804Z.json`.

BT-63's authoring runner still requires source hotfix and lead review before profile/encounter asset writes. BT-62 Smoke still requires that asset readback and must preserve the raw BehaviorTree tick limitation as `BLOCKED_NOT_INSTRUMENTED`.
