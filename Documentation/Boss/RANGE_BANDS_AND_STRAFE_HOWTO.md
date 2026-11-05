# Range Bands, Warp, Cone Hysteresis, and Neutral Strafe

**Audience:** Combat and technical designers  
**Scope:** BUILD-146, BUILD-148, and BUILD-149 behavior recorded in `Documentation/TEST_PLAN.md`.

## Range-band authoring

The profile's `BandMinCm` and `BandMaxCm` describe where the boss walks before choosing an attack. `bRangeBandPartition` is an F5-only opt-in and defaults to `false`. With it off, the profile band must fit inside every card's range, preserving the prior rule. With it on in F5, the profile band is only the walk target; each card's own minimum and maximum range decide whether that card may be selected. The validator refuses this option in F3/F4 (`Framework.Profile.Domain`).

BUILD-148 added two cards based on the baked HeavySlam_F7 blade window:

| Card | Card range | Maximum warp distance | Standoff |
|---|---:|---:|---:|
| `Move_Sevarog_BandMedium_MOV001` | 200–400 cm | 330 cm | — |
| `Move_Sevarog_BandGap_MOV001` | 400–950 cm | 880 cm | 80 cm |

Both cards use a 0.05 s commit and warp from 0.05 to 0.533 s. The warp rule requires `commit <= warpStart`. Existing `SwingSlow` (100–200 cm) and `HeavySlam` (90–180 cm) serve the Melee and Close ranges; both ranges are served by the same two cards. The proof saw SwingSlow and HeavySlam eligible at 152 cm, only the Medium card at 302 cm, and only the Gap card at 702 cm.

## Cone hysteresis

`ConeHysteresisDegrees` is an opt-in profile value in the F5 lane, constrained to 0–40 degrees. Zero preserves the original cone check. When enabled, the boss enters the facing cone at the normal cone boundary and, once inside, remains inside up to the normal boundary plus the configured slack. The selector keeps per-card cone memory and clears it on reset. BUILD-146 verified the live wiring with `DA_Sevarog_ConeHysteresis_AWR004` at 6 degrees. The flicker reduction itself was demonstrated by a selector unit test; the live proof did not use a yaw oscillation driver.

## Neutral strafe

`NeutralStrafeSeconds` is another opt-in F5 profile property: zero disables it; the allowed range is 0–20 seconds and walk speed must be positive. If no card is eligible while the boss is in its band, and the old turn-in-place branch does not apply (`RepositionMax` is zero), the boss walks a circle around the target at its walk speed and retries card selection each tick. Direction holds are seeded using `NeutralStrafeMinHoldSeconds` (default 0.8 s) and `NeutralStrafeMaxHoldSeconds` (default 1.6 s); the window must be finite, positive, and ordered. The budget ends when a card becomes eligible or the configured time expires.

The BUILD-149 live proof used one card with a 4-second cooldown and a 4-second strafe budget. It kept the same 128.467 cm range, changed direction, then ended at 2.28333 seconds when the card became eligible. This strafe has no animation, so the boss slides; the only obstacle handling is the movement sweep.

## Proof references

- BUILD-146: `L_SevarogFrameworkProofAWR004`, `DA_Sevarog_ConeHysteresis_AWR004`, and `Claude/B_AWR004/pie_run1/editor_raw.log`.
- BUILD-148: `Claude/B_MOV001/pie_R150`, `pie_R300`, and `pie_R700` editor logs.
- BUILD-149: `DA_Sevarog_NeutralStrafe_SEL008` and `Claude/B_SEL008/pie_run2/editor_raw.log`.
