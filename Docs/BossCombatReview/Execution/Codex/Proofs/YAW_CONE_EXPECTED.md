# Yaw probe and cone hysteresis live proof

## Setup

Run `make_yaw_cone_long_profile.py` for the eight-decision R6A8 map; it sets `ConeHysteresisDegrees=6` and every candidate `cooldown_seconds` to 0 s so the two-card phase pool satisfies `PhasePoolCannotStarve`. Compare the generated map with the unmodified F5 control map. Use the editor console command `rpg.BossProofYawProbe 5`; the hook samples a 24-step sinusoid centered on the first card's cone boundary. Do not enable the probe in Shipping.

## PASS

- Both runs contain sequential `[FrameworkProof] yaw_probe sample=<n> yaw=<degrees>` samples spanning both sides of the cone edge (`RPGFrameworkBossCharacter.cpp:430–436`).
- Control (hysteresis off) toggles first-card eligibility across adjacent decisions as yaw crosses the exact cone boundary.
- Hysteresis run retains first-card eligibility through the ±5-degree oscillation after entering the cone; no eligible/ineligible flicker occurs (`ConeHysteresisDegrees=6`, `RPGBossMoveSelector.cpp:44–45`).
- No card outside its cooldown/range/phase filters is made eligible by this test.

## Control

Run the unchanged F5 control with cone hysteresis disabled; it should show the boundary eligibility flicker while matching the same card and yaw samples.

## FAIL

- No probe samples, samples do not cross the boundary, the off control does not flicker, or the 6-degree hysteresis case flickers within the ±5-degree band.

## Validator

`python -I Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py <editor_raw.log>`
