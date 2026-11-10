# C-1258a Sevarog in-band PIE retry and nav diagnosis

Date: 2026-11-10  
Owner: Codex  
Scope: transient Sevarog framework driver and test-only initialization; no map or asset save.

## Result

The driver now places the player 140 cm in front of S1/S2/S3 and 450 cm for S4 before each request, reads back horizontal distance, reads each card's `MinRangeCm` / `MaxRangeCm`, and refuses to start outside that card band. C-1258a's self-test reached S1, S2, and S3; each logged `CARD_START` and `CARD_END reason=Finished`. It stopped before S4.

The test bridge skips its initial `WalkToBand` request only when the non-Shipping, default-off `rpg.BossProofSkipInitialWalk` hook is explicitly enabled, the target is test-authorized and already in the profile walk band, and the boss is grounded. The regular encounter path still uses navigation. PIE evidence confirms the in-band test starts no longer emit `Framework.Nav.MoveFailed`.

## Navigation findings

- PIE found one `RecastNavMesh` actor. A direct navigation projection of the spawned boss location succeeded, but projected from Z=227.28 cm to Z=10 cm, a 217.275 cm vertical delta.
- `InitializeProofInternal` explicitly calls `SpawnDefaultController`; the spawned controller was `RPGFrameworkBossController` and successfully issued `WalkToBand`. The prior run logged `nav request=1 ... fullPath=1`, then the path-follow callback failed with `Framework.Nav.MoveFailed` while the target had already been positioned at 140 cm.
- These observations rule out a missing navigation system or missing controller. They point to a spawn point substantially above the projected navigation surface as the likely reason the approach path fails. The exact path-follow failure mechanism remains unisolated. In-band test starts avoid that unnecessary approach; this does not claim general navigation movement is fixed.

## Playback fix found during the required self-test

S1/S2/S3 montage playback reached natural end, but the executor watchdog fired before `CARD_END`. The watchdog now derives its deadline from the card's natural clip end and authored blend-out, or recovery end plus blend-out when that is later, scaled by play rate with the existing scheduling tolerance. It advances the model to at least RecoveryEnd at natural montage end, and stops an inert montage after the model is idle and its slot weight is zero. Native rule tests cover clip-tail and recovery-dominant budgets.

## Validation

- C-1155 locked Development editor build: exit 0.
- Full `Automation RunTests OneBossFight`: 500 started, 500 passed, 0 failed; DD27j manifest `cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`.
- PIE self-test: S1/S2/S3 each started and ended `Finished`; distances read back as 140 cm and all three bands were 90–180 cm. S3 recorded one accepted hit. No S4 start, no map save.
- C-1260 follow-up rerun: `TEST_ONLY_SKIP_WALK_HOOK_ENABLED=True`; the hook is default-off in source and explicitly enabled by the test driver. Build and 500/500 suite passed; S1–S3 start/end remained `Finished`; no S4, map save or MoveFailed in the rerun.
- Navigation probe, controller diagnostic, and the prior failing path request are retained in `Docs/BossCombatReview/Execution/Codex/C1258A_RANGE_RETRY/` (`nav_failure_baseline.log`, `pie_self_test.log`, `pie_self_test_status.txt`). Both C-1155 locks are released; UnrealEditor is closed.
### C-1260 follow-up

The initial walk skip is guarded by `rpg.BossProofSkipInitialWalk`, a non-Shipping console test hook that defaults to `0`; the C-1258a PIE driver explicitly enables it only for the transient standalone test. Normal encounter initialization and live behavior retain the approach request. The watchdog now computes its allowance from `max(clip length - authored blend-out, recovery end) + authored blend-out`, scaled by play rate, with the existing 0.5 s scheduling tolerance. Native rule tests cover clip-tail and recovery-dominant cases. The out-of-band `Framework.Nav.MoveFailed` remains a live approach/navigation follow-up and is tracked in `KNOWN_ISSUES.md`.
