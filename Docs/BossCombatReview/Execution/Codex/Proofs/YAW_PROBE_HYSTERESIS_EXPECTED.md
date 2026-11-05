# Yaw probe with cone hysteresis: expected trace

Use the same bounded 26-sample yaw probe and environment as `YAW_PROBE_NO_HYSTERESIS_EXPECTED.md`, changing only `ConeHysteresisDegrees` from 0 to 6.0. The field is a full-cone-width slack: `RPGBossMoveModel.cpp:35–39` adds half of it to the normal half-cone. For a 90° full cone (45° normal half-angle), the tolerated exit boundary is therefore 48°, not 51°.

For one named candidate with half-cone 45°:

- Enter normally at `abs(yaw) <= 45°`; the exact boundary is included.
- Once remembered inside, retain it for `45° < abs(yaw) <= 48°`.
- Leave only when `abs(yaw) > 48°`; after leaving, the candidate needs to return to `<=45°` before memory is set inside again.
- With the 5° probe amplitude, exact center-relative samples 0–3 are 45°, 46.2941°, 47.5°, and 48.5355°. Starting inside at sample 0, the same candidate should remain held at samples 1–2 and be refused at sample 3. On the descending half-cycle, it should not re-enter until the signal is back at or below 45° (sample 13).

Required paired evidence: same candidate identity, profile/card cone width, range, target, phase, seed, and probe amplitude; `cone_hysteresis degrees=6`; per-sample yaw; candidate/refusal outcomes. The control should refuse that same candidate immediately above 45°; the enabled arm should hold it through 48° and exit only above 48°. Current R6A8 logs show eight samples with yaw 45°→50°, but logged candidate selection/other gates do not establish that a specific candidate was inside at sample 0 and held through 48°. Current evidence does not prove the hysteresis exit/return relation; require a candidate-specific A/B trace.

## Setup
## Control
## PASS
## FAIL
