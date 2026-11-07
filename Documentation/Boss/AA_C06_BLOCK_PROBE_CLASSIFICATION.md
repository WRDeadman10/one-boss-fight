# AA-C06 — Block probe classification

## Finding

The prior probes do not demonstrate that the guard input failed in a valid player state. Probe 1 began its guard window with health and stamina both `0.0` (`Docs/BossCombatReview/Execution/Claude/ER_INPUT_DUMP/probe1/editor_raw.log:1872-1875`). Probe 2 began at health `-36.0` and stamina `0.0` (`probe2/editor_raw.log:1883-1886`). Those samples cannot establish an Enhanced Input or guard-ability failure. Probe 3 was alive at `1000000.0` health/stamina, but its “weapon drawn” claim was paired with `montage seen: None`; its later `GS_EquipWeapon_Montage` line is explicitly the boss montage, not the player's (`probe3/editor_raw.log:1877-1887`). The old observer therefore did not prove player weapon state.

The input dump shows the intended mapping `IA_Block <- Gamepad_LeftShoulder` (`ER_INPUT_DUMP/run1/editor_raw.log:1290-1297`), but a mapping dump and a synthetic key setter are not evidence that the player's Enhanced Input action activated. The old logs contain no `[FrameworkProof] guard_tags` samples and no `Status.Blocking` result.

The authoritative source observer is `RPGBossDamage::HasTag`, which calls the target actor's `HasMatchingGameplayTag` (`Source/OneBossFight/Player/RPGBossDamage.h:18-33`). `RPGFrameworkBossCharacter.cpp:270-282` drives `IA_Block` through the test hook and logs `Status.Blocking`, `State.Blocking`, ability tags, and guard ability presence. The current Python v4 reads `GetOwnedGameplayTags` from the pawn and logs montages, but does not capture the action activation callback or the framework observer values.

## Classification

The demonstrated defects are probe validity and attribution: two runs tested a dead player, and the third confused the boss equip montage with evidence of player weapon draw. The exact reason v4's gamepad arm may fail remains unproven until a live run records a valid player, actual player equip state, and guard-state observations. No gameplay defect is established; the owner reports that L1 blocking works in normal play (C-953).

## Evidence boundary

This is a static classification of retained logs and source. The revised v4 has not been run live in this report; do not infer that the C++ hook or the Python tag reader has been validated in PIE.
