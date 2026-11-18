# BT-83 Greystone visual smoke: fresh H-17-authorized attempt

Date: 2026-11-18 (Asia/Kolkata)

Owner authorization: mailbox `[H-17]` grants Codex and Antigravity full permission to proceed without waiting. Codex issued a unique approval envelope at `Saved/GreystoneVisualSmoke/Approvals/OwnerApproval_H17_ae4289f22fec4eee90dc128fcaaff7cb.json`, bound to run token `ae4289f22fec4eee90dc128fcaaff7cb`, map `/Game/OneBossFight/Maps/L_SevarogArena`, and the four current source hashes below.

| Source | SHA-256 |
|---|---|
| runner | `FAB7A89AC4710F9F955F8A3E9DDA18C97F0882BC973132E210213B070B14DB1F` |
| driver | `68CF485F54858B943A5D7B1DE2D209768898E0F143B79E550D06B35836EB4AF1` |
| retarget C++ | `22A04C1A5B12AAC1A045EC33AB2E346064D55FBABA83FA5E25FA2E749C5778AF` |
| moves C++ | `60097589BA1FAF3C12827ECDF6AC0FD32651EA3AA292EF25C17AB1878D7FB838` |

## Result

- Run: `Saved/GreystoneVisualSmoke/Run_20261117_213058_ae4289f2`.
- Runner exit: 1. Receipt `result=FAIL`, `accepted=false`.
- Direct failure: `unhandled driver exception: 'World' object has no attribute 'get_first_player_controller'` at `Scripts/Editor/pie_greystone_visual_smoke.py:494`.
- Exact pawn possession and visual/source mesh criteria were not reached. `GetMainAnimBP` error count was 0; continuous log monitoring passed.
- CVar cleanup readback was `0`; `Config/DefaultGame.ini` SHA-256 remained `5DE691FCA4E0FA375F6F262FA6BA402FEFA7AB9A0B567AE2146E6823F69EDEC8`.
- The wrapper initially reported that the Editor did not exit within its 10-second graceful-close wait. A subsequent check confirmed the Editor process count is 0 and both exact C-1155 lock paths are absent. No config or asset save occurred.
- No build, package or tests were run. Computer Use returned `GetCursorPos access denied (0x80070005)`, so BT-71 Full-mode combat input remains unperformed.

## Follow-up

BT-93 is assigned to Antigravity, in progress, as a source-only fix to use a supported UE 5.5 PlayerController lookup with bounded retry. Existing engine header `GameplayStatics.h:192` and project PIE drivers show `unreal.GameplayStatics.get_player_controller(world, 0)` as the supported pattern. No duplicate Editor run is underway. A retry requires separate fresh C-1155 execution and approval provenance; this attempt is consumed and is not a pass.
