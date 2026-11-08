# Queue AP-C01–C05 — BossBlocks switch

**Assignment:** Claude C-1078. **State:** offline implementation complete; Lead build and live probe pending.

## Scope

This slice implements only camera option A from C-1051: make the live pack boss capsule block `ECC_Camera`, shortening the existing spring arm instead of letting its camera enter the boss mesh. The new `rpg.Camera.BossBlocks` console variable is compiled only outside Shipping and defaults to `0`. The existing spring-arm sweep and its 34 cm probe are unchanged. No owner choice or shipped default is implied.

When enabled, `URPGCameraRig` finds the pack boss through `URPGPlayerMovesSubsystem::IsPackBoss`, saves the capsule's authored `ECC_Camera` response, and sets that response to Block. Disabling the switch, replacing/removing the target, or ending the rig restores the saved response when the component still has the switch's Block value. If another system has since changed that response, cleanup leaves that newer value intact. The off path restores any prior experiment state and returns before actor iteration or collision writes.

## Offline evidence

`Scripts/Editor/test_camera_boss_blocks_contract.py` was extended before the source fix. Its first run had one failure for null-safe component-owner logging (the other four checks passed); the implementation was then guarded and the focused suite rerun. The contract checks Development-only/default-off declaration, pack-boss capsule selection, authored-response capture/restore, tick and EndPlay cleanup, and that the disabled branch returns before iteration and collision writes. These are source contracts, not native compilation or runtime proof.

## Lead acceptance still required

Build the project and run `Scripts/Editor/probe_camera_inside_boss.py` on both legacy and data routes. Capture baseline (`rpg.Camera.BossBlocks 0`), enabled (`1`), then disabled (`0`) in one identified build. Circle both directions at 150–250 cm and cover 105 cm, wall/floor, attacks, dodge, recovery, and aura. Record per-tick camera-in-boss state, arm length, blocking component, saved/restored collision response, and safety samples in `Documentation/Boss/CAMERA_DYNAMIC_BASELINE_RECEIPT_TEMPLATE.md`. Confirm baseline is unchanged at zero and disabling restores the response. Lead build/PIE evidence is pending; do not close KI-037/KI-066 or claim the owner has selected an option based on this code alone.
