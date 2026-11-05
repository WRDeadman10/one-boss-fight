# I021 — first paired parity pilot contract

**Chosen registered driver:** `pie_a4_low_sweep` (`Scripts/RunDrivers.ps1:17-18`), registered marker kind R, minimum 14 checks. It exercises a repeatable A4 sweep and its grounded hit, jump avoidance, range/behind refusals, roll i-frames, mid-sweep reset, and boss death cleanup. This is the narrowest existing driver with several named outcome dimensions and a stable end marker; its current runs remain legacy-path evidence.

## Exact planned observables

The receipt must include the same named per-scenario outcomes for legacy and selected data runs:

- `S2_grounded_front_250`: hit count and health delta per trial (expected one hit / 20 HP);
- `S3_jump_033`: hit count, jumped count and health delta (expected no hit, jump clear);
- `S4_out_of_reach_520` and `S5_behind_250`: hit and health delta (expected no hit);
- `S6_backward_roll_050`: hit, invulnerable-contact and health delta (expected i-frame pass);
- `S7_mid_sweep_reset_062` and `S8_boss_death_062`: hit and health delta (expected cancellation/no damage);
- `S9_*` information-only probes: retain their output in raw logs, but exclude them from parity observables because they do not have pass/fail acceptance and are explicitly informational.

Each value must be captured from that run's counters/health reads; do not synthesize it from pass booleans or parse it from source. Driver marker/check totals remain independently required and must meet the registered minimum. Both run IDs are distinct; map/build/content/settings/seed/driver args/input identity must match exactly.

## Input identity

Use a canonical JSON descriptor over ordered `SCENARIOS` name/distance/angle/trial count/actions, `TRIAL_LEN`, `SETTLE`, jump/dodge key names and the driver source revision; SHA-256 of its UTF-8 canonical serialization is `input_sha256`. The driver/build identity, content snapshot, settings, seed and command arguments must come from the run harness, not constants copied from this example. If a field is unavailable or a pair differs, report INCONCLUSIVE/FAIL rather than filling a placeholder.

## Readiness limits

No v1 receipt is emitted today. The current script stores pass booleans and only logs informational S9 counters, so I022 must add per-trial measured outcome capture before emission. Selected-route pilot execution additionally needs valid typed boss/player definition assets and the approved manifest; none exists yet. The pack death/respawn lifecycle does not occur in this specific scenario, but H001's approved rebind design remains a separate requirement before broad parity. Claude owns both PIE arms and validation.
