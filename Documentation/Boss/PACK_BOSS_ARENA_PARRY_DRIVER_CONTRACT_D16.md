# Pack-boss arena parry driver contract (Queue D D16, 2026-11-03)

## Objective and proof claim

Prove the pack boss's own melee-hit decision recognizes a real player parry in `L_SevarogArena`. A passing run needs all three facts in the same contact: a real pack-boss weapon trace/contact reaches the pack's impact decision, `Status.ParryActive` is active at that contact and the pack reports its own parry response, and player health does not decrease from that contact. The framework boss's `URPGDamageResolver` outcome alone is not evidence for the pack boss's branch.

## Source and evidence boundary

- The pack's impact decision reads `Status.Blocking` and `Status.ParryActive`; `URPGPlayerParry` mirrors its timed window into the pack-owned `Status.ParryActive` tag (`RPGPlayerParry.cpp:20–58,65–109`; behavior and BUILD-152 boundary in `Documentation/TEST_PLAN.md:512`). The exact pack Blueprint branch and its reaction output must be verified by Claude from the live event/log or reflected Blueprint evidence; these are not visible in this native source audit.
- `L_SevarogArena` was loaded by the previous BUILD-152 PIE command (`Docs/BossCombatReview/Execution/Claude/B_PARRY/pie_parry5_pack_tag/editor_raw.log:1294`). That run instead switched to `L_SevarogFrameworkProofCOM` at line 1385 and its guard hook pressed `IA_Parry` against a framework proof boss; it proves the tag mechanism, not pack-boss reaction.
- Existing BUILD-152 record explicitly says the pack boss's own reaction remains unwitnessed (`Documentation/TEST_PLAN.md:512`; open KI-153). `Documentation/Boss/PARRY_HOWTO.md:36–38` describes the framework-boss hook and its limits.
- `Scripts/Editor/pie_sevarog_pack.py` is a demo-level observer/player-fight helper and its module docstring says it deletes the boss actor from the editor level at completion. Do not run/adapt it for this contract without first proving exact map/actor ownership and replacing broad cleanup with cleanup of only actors created by the driver.
- The PIE command's referenced `F4/drive_*.py` script is not present under maintained `Scripts/Editor`; prior outputs do not retain enough driver source to claim its exact input scheduling or cleanup behavior.

## Proposed driver sequence (not implemented or run)

1. **Preflight:** Claude owns the editor handoff; confirm the active project/editor PID and that `L_SevarogArena` is the loaded map. Confirm the actual `BP_SevarogBossPack` actor, player pawn/controller, Sword or Claymore style with granted `GA_PlayerParry`, bound `IA_Parry`, and `URPGPlayerParry` component/tag owner. Fail setup if any required object or reflected tag readback is absent; do not silently substitute the framework proof map/boss.
2. **Control contact:** start from a repeatable in-arena start transform and let the pack boss choose and execute a real melee attack with no parry input. Capture attacker/attack identity, contact time, `Status.ParryActive=0`, player health before/after, and the pack response. Require a genuine contact that damages the player; otherwise mark the control inconclusive and do not count it as a negative parry result.
3. **Parry contact:** repeat from the same baseline/reset procedure. Open the window through the player's real `IA_Parry` input binding, scheduled from the pack attack's observed tell/contact timing. Do not inject a damage event, call the resolver directly, or use `rpg.BossProofPlayerGuard`'s framework-executor hit-window trigger as a substitute for observing the pack swing. At contact, capture pack attack identity, parry window open/close and tag add/remove, pack impact-decision outcome/reaction, and player health/stamina before/after.
4. **Repeatability and cleanup:** collect at least three valid pack contacts, including at least one paired control and one parried contact; retain failed/inconclusive attempts separately. Use unique per-run raw logs/results and hashes. End PIE normally, remove only driver-owned spawned actors/timers/delegates, restore test-only input hooks/cvars to captured prior values, and leave map/content assets unsaved and unchanged.

## Acceptance matrix

| Claim | Required evidence | Fail/inconclusive rule |
|---|---|---|
| Correct arena and actors | Raw log records map package, player class, pack boss class, actor identities, transforms, and active combat style. | Wrong map, missing actor/style/input binding, or only framework boss present = setup failure. |
| Real pack melee source | Contact is tied to the pack boss's actual weapon/ability trace and a named attack/animation; no injected damage calls. | Framework executor hit, test damage injection, or ambiguous contact = invalid sample. |
| Control works | At least one real un-parried pack contact with tag inactive and a measured player-health decrease. | No valid damaging control = inconclusive; not a parry pass. |
| Pack's own parry branch works | At a real contact, input open succeeded, tag active at contact, pack's own branch reports a parry-specific response, and health loss for that contact is zero. | Tag add/remove without pack-branch evidence only reproves plumbing; resolver-only `Parried` is insufficient. |
| No unintended resource effects | Read player health and stamina immediately before/after contact; state any configured stamina cost/refund and compare actual deltas. | Missing attribute readback prevents a resource-conservation claim. |
| Repeatability | Per-contact rows include attack, time, window/tag state, pack outcome, health delta, and raw-log locator; paired control/parry attempts share documented reset inputs. | Do not aggregate invalid attempts into sample count or discard failures. |

## Verification boundary

This is a no-run contract derived from native source, maintained docs, and retained BUILD-152 command/log metadata. No driver was implemented or run; no Editor, map, pack asset, build, or test was changed. Lead must verify the exact pack Blueprint response telemetry and own execution in the real arena. The contract does not claim KI-153 is resolved.
