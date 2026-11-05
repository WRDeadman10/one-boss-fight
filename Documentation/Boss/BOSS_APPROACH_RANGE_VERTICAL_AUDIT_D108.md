# Boss approach range and vertical audit — D108

**Scope:** compare boss navigation band checks with card-selector eligibility, units, and endpoints. Static source review; no navigation/world run.

The framework boss derives `RangeCm` from `FVector::Dist2D`, records `VerticalDeltaCm` separately via `FloorSeparationCm`, and sends both to the move model (`RPGFrameworkBossCharacter.cpp:424-425`). The navigation arrival check uses the same 2D range in centimeters against the profile band `[BandMinCm, BandMaxCm]` and separately requires grounded movement (`:231-236`). It does not use a 3D distance or treat vertical separation as range.

At decision time, the move model checks a candidate's own `MinRangeCm <= RangeCm <= MaxRangeCm`; when `MaxVerticalDeltaCm > 0`, it additionally refuses if `VerticalDeltaCm > MaxVerticalDeltaCm` (`RPGBossMoveModel.cpp:28-42`). Profile resolution requires the profile walk band to fit each card's range unless F5 `bRangeBandPartition` makes the profile band a walk target and card ranges independent (`RPGBossFrameworkProfile.cpp:197-199`). Units are centimeters throughout the profile, card, observation, and distance calculations.

The comparison is therefore purposeful: 2D approach band is a navigation target gate; selector eligibility applies per-card 2D range and optional vertical limit. The profile and card range endpoints are inclusive; vertical equality is allowed because refusal is strict `>` (`MoveModel.cpp:33-42`). This does not establish that nav can reach the band on multi-level geometry or that floor separation matches authored gameplay expectations.

Existing tests for `RPGBossMoveModel` and profile validation are cited in the source index, but this audit did not find a focused selector-model fixture that combines exact band endpoints, vertical equality/adjacent values, and nonzero vertical limits in one approach/decision comparison. Exact profile/card equal-range acceptance also depends on resolution conditions.

**Acceptance result:** no unit mismatch found. The behavior separates 2D approach range from optional vertical card eligibility as implemented. Multi-level navigation and combined boundary behavior remain unproved; static only.
