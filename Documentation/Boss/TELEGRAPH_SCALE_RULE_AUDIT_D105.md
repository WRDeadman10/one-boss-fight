# Telegraph scale rule audit — D105

**Scope:** map profile opt-in, scale inputs, refusal behavior, and endpoint tests. Static source review only; no suite or runtime test run.

`RPGBossTelegraphScale::Rate` accepts the clip's active-start time, current play rate, required real tell, and a minimum fraction of the current rate. It rejects nonfinite or nonpositive values and a floor outside `(0,1]`; computes `min(CurrentRate, ActiveStartSeconds / RequiredRealSeconds)`; and refuses if that result is below `CurrentRate * MinRateScale` (`RPGBossTelegraphScaleRules.h:9-17`). Thus the returned rate cannot accelerate the current rate; the floor is relative to the incoming rate, not a global absolute rate.

The framework executor only uses this helper when profile `ParryFairTelegraph` is enabled. It derives the required real tell from `RPGBossParryFair`, applies the scale to the card rate, and fails closed if the helper refuses (`RPGFrameworkMoveExecutor.cpp:136-143`). Profile validation limits the minimum scale to `(0,1]` and requires the opt-in lane to be F5 (`RPGBossFrameworkProfile.cpp:139-140`). This is playback timing behavior; it does not change authored sequence timing or guarantee a live parry outcome.

The tests cite active-start values for eight current attack rows and check expected scale, fairness, no acceleration, cap refusal, invalid rate, and composition with fatigue. The 100x50 sweep checks no acceleration and refusal below the floor; explicit equality at the floor, `MinRateScale == 1`, and adjacent representable values around the refusal boundary are not directly asserted (`RPGBossTelegraphScaleRulesTests.cpp:10-45`). Nonfinite required time and NaN floor are covered; positive/negative infinity in each other input is not exhaustively enumerated.

**Acceptance result:** the helper and executor agree on the relative floor and fail-closed contract. Existing coverage supports the main range/composition claims; exact floor-boundary adjacency remains a targeted test gap. Helper/profile opt-in remains unproven in a live fixture.
