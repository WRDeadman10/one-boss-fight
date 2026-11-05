# Player Parry: Designer How-To

**Audience:** Combat and technical designers  
**Scope:** BUILD-147, BUILD-147b, and BUILD-150 behavior recorded in `Documentation/TEST_PLAN.md`.

## What the parry does

`URPGPlayerParry` opens a 0.25 second window when the player presses IA_Parry. The current proposed cooldown is 0.7 seconds, measured from the press. At a valid contact, `URPGDamageResolver` checks dodge invulnerability first, then the parry window, then ordinary damage. A parried contact applies no health damage and spends that swing's hit; it is not counted as an accepted hit. The combo gate receives the `Parried` outcome.

BUILD-147 added the parry ability to the Sword and Claymore combat styles by copying each style's existing block entry. DualSwords and Polearm styles had no block entry and were left unchanged. The style edits and their before/after hashes are recorded under `Docs/BossCombatReview/Execution/Claude/B_PARRY/`.

BUILD-150 added `ParryPostureAmount` to the framework boss profile. Zero disables the reaction. A positive amount requires a positive `PostureMax` and cannot exceed that maximum. When a parry is recorded, the boss applies that posture amount at the start of its next tick, outside the hit sweep. If posture breaks, the usual stagger path follows. The BUILD-150 proof profile uses 100 posture against a 100 `PostureMax`; it is a proof value. The real boss profile leaves the field at zero pending a design value.

The optional `GuardChipFraction` profile field applies to ordinary `Guarded` contacts handled by the framework move executor: when positive, it is the fraction of normal health damage that still passes through a guard. Zero is off and preserves the current guarded-contact damage. Parried contacts remain damage-free. This wiring has not been proven in a live editor run.

The optional `ParryRecoveryScale` profile field extends the neutral wait after a card finishes when its contact was parried. Zero is off; positive values [0,3] scale the card's authored recovery duration before the pure grade rule calculates the extra time. The largest same-card parry result wins, and the extension clears on restart, death, or failure. `[FrameworkProof] parry_recovery grade=%d extra=%g` records it. This wiring is not live-proven.

The optional `ParryFairTelegraph` profile switch slows an attack only enough for its opening tell to meet the pure parry reaction-window rule. `ParryFairMinScale` defaults to 0.4 and is the minimum allowed playback-rate fraction in `(0,1]`; if a card needs a slower rate than that floor permits, playback fails closed. The executor restores the card's original rate at finish or abort. `[FrameworkProof] telegraph_scale card=%s rate=%g` records the selected rate, and `telegraph_restore card=%s rate=%g` records the active montage's rate after restoration. These runtime tokens are not yet live-proven.

If the F5 profile also enables fatigue, the fatigue multiplier is applied to the authored card rate first; the fair-telegraph rule then slows that result as needed. The final rate is used for montage playback, timing/watchdog calculations, and hold release; card completion and abort restore the authored rate.

`URPGPlayerParry.StaminaCost` is optional and defaults to zero. A charged press requires a readable stamina value at least as large as the cost; the cost is rolled back if cooldown prevents opening the window. If that parry lands, half the cost is refunded when its window closes, capped at the readable maximum stamina. Failed refund/rollback calls retry for up to five attempts; a missing stamina attribute cannot create a free parry. `[FrameworkProof] parry_stamina` reports the before/after values when readable. This is not live-proven.

## Authoring and tuning

1. Ensure the player combat style grants the parry ability. In the BUILD-147 content change, this was done for Sword and Claymore only.
2. Treat the 0.25 second parry window and 0.7 second cooldown as proposed design values, not final balance decisions.
3. For framework boss reaction proofs, set `ParryPostureAmount` to a value in `(0, PostureMax]`. Keep it at zero to disable the reaction.
4. A parried hit does not automatically play a player-facing parry animation or sound. BUILD-150 added boss posture/stagger behavior; the documented proof has no parry animation or sound.
5. Leave `GuardChipFraction` at zero for the existing behavior; positive values are in [0,1] and apply only to guarded contacts. Live behavior remains unproven.
6. Leave `ParryRecoveryScale` at zero to disable the extra recovery. Positive values are opt-in and require the F5 selector profile lane. Live behavior remains unproven.
7. Enable `ParryFairTelegraph` only in an F5 profile; lower `ParryFairMinScale` to permit more slowdown. A card that cannot meet the rule above that floor is rejected. Live behavior remains unproven.

## Live proof

Use a development PIE run with the framework proof boss and the real pack player input. The `rpg.BossProofPlayerGuard` hook is a development test aid and is not compiled into Shipping builds. Mode 6 toggles combat at the start and presses IA_Parry when a boss hit window is open; `rpg.BossProofPlayerGuardSeconds` sets how long the hook runs. The BUILD-147 timing proof used `pie_parry3_perfect` and logged `parry_press ... opened=1`, `guard_state ... guard=Parried outcome=ERPGDamageOutcome::Parried`, and `combo_gate ... outcome=Parried`. The target health invariant showed that only the earlier hit, whose parry press came after contact, dealt damage.

For the boss reaction, use the BUILD-150 PARRY proof map and `DA_Sevarog_ParryReaction_PARRY`. Confirm `guard_state ... guard=Parried`, `parry_reaction posture=100`, `posture_drain`, and `stagger_recovery` in `Claude/B_PARRY/pie_reaction2/editor_raw.log`.

## Completion reporting and limits

BUILD-147b corrected the clean-completion RESULT label: if `acceptedHits` is zero and at least one hit was parried, the outcome is `CompletedAllParried`. RESULT lines include a trailing `parriedHits=N`. The all-parried outcome branch had no live run in the evidence recorded for BUILD-147b; its example RESULT line was `CompletedWithDamage acceptedHits=1 attacks=3 parriedHits=1`.

The BUILD-150 proof profile can fail closed with `NoCandidate` after the parry stagger because its card cooldowns starve the selector; that profile does not set `NeutralStrafeSeconds`. The actual boss profile still has `ParryPostureAmount=0`. The BUILD-150 proof did not include a parry animation or sound.
