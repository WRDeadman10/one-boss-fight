# BQ-36..40: Queue BQ batch 8, Sevarog S1/S2 reach and the S4 to S5 boundary

C (implementer), 2026-11-13. Queue: `QUEUE_BQ.md`.

**Analysis only.** No asset, card, script or source was changed. The data diff below is a proposal and is **not applied** (unsaved). No engine, editor, PIE or commit. Raw trace logs were not re-read; the trace numbers are cited from the existing reports.

| Task | Result |
|---|---|
| **BQ-36** S1/S2 140 cm miss | **reconciled, already analysed** (C1269 X03, BJ X07). At 140 cm, isolated S1 and S2 both finished with 0 card hits. In the active window, S1's `root_weapon_end_r` was 106.1 cm from the player capsule and S2's closest point (`weapon_r`) 37.0 cm, against a 15 cm trace radius. The miss is geometric (out of reach), not a selection or navigation fault. The only positive point is the S4 to S5 combo hit at 120 cm (25 damage), which is not an isolated S1 result |
| **BQ-37** S4 to S5 boundary | **root cause, new analysis**, see below |
| **BQ-38** C-1274 card range as a data diff | **reconciled, source already carries it.** `author_sevarog_draft_cards.py:463-464` sets `Swing1_Medium` and `Swing2_Medium` to (90, 120), with an inclusive gate (`:469-474`) and the baseline print (`:541`, margin 0.352996 s against 0.300 required). BE-X26..30 validated the transient dry run (509/509). Still open (ENG): saving the authored card assets, reading back the saved rows, and an isolated live S2 hit at 120 cm |
| **BQ-39** the boundary fix proposal | **data diff proposed, unsaved**, see below. Needs a Lead decision and ENG to apply |
| **BQ-40** | this report |

## BQ-37: why S4 to S5 sometimes refuses with `MoveModel.Range`

- **S4 (Speedburst)** is a defensive gap closer. Its warp closes on the target down to `WarpStandoffCm`. The executor computes `Needed = max(0, Dist - WarpStandoffCm)` (`Boss/RPGFrameworkMoveExecutor.cpp:645`), so the warp is designed to end at **exactly 120 cm** (`author_sevarog_draft_cards.py:365`).
- **S5 (Swing1_Medium)** is reached by the WHIFF combo edge. The edge's own range is 0 to 1e6, but S5 still has to pass the card eligibility check `RangeCm < Min || RangeCm > Max`, which refuses (`Player/RPGBossMoveModel.cpp:33-34`). Since C-1274, S5's maximum is **120 cm inclusive**.
- **Conflict:** the warp target equals the inclusive upper bound. The measured distance at S5's decision includes float residue from the warp interpolation, capsule correction and any player movement between frames. So it is 120 plus a small epsilon about as often as it is 120 minus one, and the refusal is intermittent, as Arm A shows (`BK_06_10_X26_DRIVER_SUPPORT.md:37`).
- **Not a model bug.** The inclusive comparison is pinned on purpose (`OneBossFight.Framework.MoveModel.RangeBandPartition` and the 19/401 boundary tests). The fault is the data: two authored values with zero margin between them.

## BQ-39: proposed data diff (unsaved, Lead decision)

**Recommended:** give the S4 warp a 10 cm margin inside S5's band.

```diff
--- Scripts/Editor/author_sevarog_draft_cards.py  (proposal only, not applied)
+++ Scripts/Editor/author_sevarog_draft_cards.py
@@ index == 3  (S4 Move_Sevarog_Speedburst, C-1250)
-                "warp_standoff_cm": 120.0,
+                "warp_standoff_cm": 110.0,  # BQ-39: 10 cm inside S5's inclusive 90-120 band (C-1274), so float residue cannot exceed S5's max
```

**Effect check (static):**
- S5 starts at about 110 cm instead of exactly 120 cm. That is still inside 90-120 with a 10 cm margin on either side, and well clear of the 90 cm floor.
- **Punish margin is unchanged.** With the player's 150 cm reach, the walk-in is `max(0, 110 - 150) = 0` at both 110 and 120, so the light margin stays at 0.703333 - 0.350337 - 0 = **+0.353 s** (required 0.300).
- S4 itself is defensive and does zero damage, and its own range (300-650 cm) is untouched. The only gameplay change is that S5's swing begins 10 cm closer, which, if anything, helps the recorded combo hit (25 damage at 120 cm).
- The S1/S2 C-1274 approval (90-120) is not touched.

**Alternatives (not recommended):**
- **(b)** Raise S5's max above 120. This reopens the C-1274 approval and the 140 cm miss evidence.
- **(c)** Add an opt-in range epsilon to `FRPGBossMoveModel::IsEligible` (source). This changes a pinned inclusive contract for every card to fix a single data pair.

## Gates

1. **Lead:** accept or reject the 110 cm standoff (BQ-39). Then ENG: apply it in the authoring script, run the transient dry run under C-1155, save the asset, and run Arm A again to confirm S4 to S5 no longer refuses.
2. **ENG (existing):** C-1274 saved-row readback and the isolated live S2 hit at 120 cm.
3. **O1 (X-1991):** Sevarog values remain owner-gated. This proposal changes no owner-decided value, but it does touch authored Sevarog data, so the Lead should confirm it is inside the delegated scope.

## Lead disposition (X-2350)

Accepted the 110 cm S4 `warp_standoff_cm` as the candidate for a bounded ENG trial: it puts the S4 landing 10 cm inside S5's inclusive upper range and leaves the measured light-punish margin unchanged. This is not a final authored value or a live acceptance. The C-1250 value remains provisional until the Lead applies the candidate under the C-1155 lock, reads back the saved data, and repeats the S4→S5 arm. No script or asset was changed in this analysis batch.
