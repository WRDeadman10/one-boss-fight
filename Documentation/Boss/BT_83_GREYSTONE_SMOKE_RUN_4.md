# BT-83 Greystone Visual Smoke Run 4

Date: 2026-11-18 (Asia/Kolkata)
Lead: Codex
Task: BT-83
Status: Automated smoke PASS; visual art inspection remains pending Owner.

## Authorization and scope

Executed one fresh, no-save C-1155 run under Owner authorization H-17 after the BT-95 driver and BT-96 receipt-validator path corrections. The fresh approval receipt is `Saved/GreystoneVisualSmoke/Approvals/OwnerApproval_H17_retry_15380a4c48de47638c29bc7aacafe7a5.json`, token `15380a4c48de47638c29bc7aacafe7a5`. It binds the current runner, driver, retarget C++, and moves C++ SHA-256 values. No build, package, tests, asset edits, config edits, or commits/pushes were performed.

## Result

Run directory: `Saved/GreystoneVisualSmoke/Run_20261117_221027_15380a4c`

The runner and receipt validator returned `PASS`, `accepted=true`. The exact `BP_GreystoneERPlayer_C` pawn was possessed in `/Game/OneBossFight/Maps/L_SevarogArena`. The canonical source mannequin AnimBP path matched, the source mesh was hidden, and `GreystoneRuntimeVisual` was visible with `ABP_Greystone_RuntimeRetarget`. Continuous log monitoring read 184,542 bytes in five reads; `GetMainAnimBP` errors were zero. CVar readback after cleanup was `0`.

`DefaultGame.ini` remained unchanged (SHA-256 `5DE691FCA4E0FA375F6F262FA6BA402FEFA7AB9A0B567AE2146E6823F69EDEC8`). Unreal Editor exited and both C-1155 lock files are absent. The receipt's automated criterion `runtime_visual_visible=true` is satisfied, but visual aesthetics, mesh deformation/clipping, and animation blending are explicitly `PENDING_OWNER_INSPECTION`; this smoke alone does not establish a complete playable build.

## Source hashes

| Input | SHA-256 |
|---|---|
| Runner | `FAB7A89AC4710F9F955F8A3E9DDA18C97F0882BC973132E210213B070B14DB1F` |
| Driver | `AD94D32121506E790C4215945320DF59A3EEFE10853E20204BF353B084EA89A0` |
| Retarget C++ | `22A04C1A5B12AAC1A045EC33AB2E346064D55FBABA83FA5E25FA2E749C5778AF` |
| Moves C++ | `60097589BA1FAF3C12827ECDF6AC0FD32651EA3AA292EF25C17AB1878D7FB838` |
| Receipt validator | `4584523C0E7B8C179E6ECCDE26382576237117AEEC829A6F85040F616F2BB708` |
