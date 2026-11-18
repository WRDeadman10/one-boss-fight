# BT-83 Greystone visual smoke: post-BT-93 retry

Date: 2026-11-18 (Asia/Kolkata)

Authorization: Owner H-17; fresh approval envelope `Saved/GreystoneVisualSmoke/Approvals/OwnerApproval_H17_retry_8d724c2402a34a29b12b0fbd64367632.json`, run token `8d724c2402a34a29b12b0fbd64367632`. The receipt is bound to the current four source hashes, including driver `89ED8BF38C5C2A70289E71C24AB1DC6D09A10E248BE7D8266BEA0BFCE6F703F0`.

## Result

- Run: `Saved/GreystoneVisualSmoke/Run_20261117_214948_8d724c24`.
- Runner exit 1; receipt `result=FAIL`, `accepted=false`.
- BT-93 fix worked: exact `BP_GreystoneERPlayer_C` possession is true. `GetMainAnimBP` error count is 0; continuous log monitoring passed.
- Next criterion failed closed: expected `CharacterMesh0` AnimBP class path was stale. Actual: `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/ABP_CombatCharacter.ABP_CombatCharacter_C`; expected: `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/ABP_CombatCharacter.ABP_CombatCharacter_C`. Runtime visual/source mesh criteria after this assertion were not accepted.
- CVar cleanup readback is `0`; `DefaultGame.ini` remains SHA-256 `5DE691FCA4E0FA375F6F262FA6BA402FEFA7AB9A0B567AE2146E6823F69EDEC8`. Editor exited, both C-1155 locks are absent. No asset/config save, build, package or tests.

## Next step

BT-95 is assigned to Antigravity to confirm the canonical existing asset path and correct only the driver's expected path. Run 3 is preserved as failed. Any next run will use a new token and approval receipt bound to all current hashes under C-1155.
