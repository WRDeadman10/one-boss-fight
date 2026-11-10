# C-1262a: Sevarog trace, attribution, and combo diagnosis

**Status:** Codex implementation and PIE self-test complete; Lead review of the S1/S2 contact marks remains open. No card windows, asset values, or map data were changed.

## S1/S2 at 140 cm

PIE geometry receipts are in `Docs/BossCombatReview/Execution/Codex/C1262A_SEVAROG_DIAG/pie_live.log` (`sweep_geometry`, instances 1 and 2). The player capsule was centered at X=-1780 with radius 42 cm and half-height 96 cm; both setup receipts show a 140 cm in-band target and actor yaw 180°, with player relative to boss at X=-140. `heading_commit` reports yaw 180°, `turnedDegrees=0`, and decision/live yaw 0. The actor's facing decision was therefore already toward the player; the missing hit is not caused by a failed turn.

- **S1 / Swing1_Medium:** the active interval is 0.267–0.400 s (C-1242 frames 4–6). The weapon sweep comes closest at the start of the window and then moves away from the target. It does not intersect the target capsule; no accepted hit is logged.
- **S2 / Swing2_Medium:** the active interval is 0.200–0.400 s (C-1242 frames 3–6). Its logged sweep points stay on the far side of the target: during the first sampled substep the closest weapon point is around X=-1604 while the player capsule is X=-1780; the sweep subsequently moves farther toward positive X. The sweep cannot intersect the capsule during this window.

The live evidence identifies a weapon-path/clip-to-target alignment problem, with S1 a near miss and S2 far outside the target envelope. C-1242 explicitly labels its 15 Hz contact marks as visual candidates, not measured traces. The marks visually cover the striking motion, but this PIE run cannot prove whether their boundaries need re-marking or the weapon alignment/range is wrong. No speculative timing or radius edits were made; Lead should re-mark the clips if the intended contact frames differ.

## S4 attribution, health abort, and S5

The old S4 `hitsAccepted=1 appliedDamage=55` was executor lifetime totals carried from S3's one hit, not S4 contact. `RPGFrameworkMoveExecutor` now records per-card start baselines and emits per-card deltas separately from lifetime totals. `FRPGBossCardTelemetryDeltaTest` covers the prior-hit/defensive-card case.

An initial diagnostic attempt showed `actual=100 expected=800` exactly as the PIE viewport acquired gameplay focus and initialized the player's combat style. Destroying the map-owned boss actor inside transient PIE did not prevent the reset. The runner now warms the viewport to two consecutive bright frames before initializing the test target, and removes the ambient actor only in PIE; the successful run had no target-health abort. This isolates the test lifecycle and preserves the health invariant.

The test driver had already run three standalone cards before starting the S4 combo on the same test actor, exhausting the profile's three-attack budget. `StartComboForTest` now resets that test-only budget when it initializes an isolated combo. In the successful run, S4 logged `cardHitsAccepted=0 cardAppliedDamage=0`, `totalHitsAccepted=1 totalAppliedDamage=55`; `combo_gate ... outcome=Whiff result=Continue next=S5` followed by `combo_step node=S5`, and S5 finished. S5 then connected for 25, confirming the whiff edge works after the test-only budget reset.

## Capture and verification

The driver serializes each card's screenshot warmup/final capture before requesting the next card. PIE produced four bright retained card images (each >300,000 bytes), and all four primary cards finished; no map save occurred. The Dev editor build passed and the full automation suite passed **501/501**. Evidence and lock receipts are under `Docs/BossCombatReview/Execution/Codex/C1262A_SEVAROG_DIAG/`; the PIE runner reports all locks released.
