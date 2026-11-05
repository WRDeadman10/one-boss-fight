# Opt-in boss turn smoothing expected sheet (Queue D162)

Status: protocol only; no smoothing behavior or default change is authorized. Review the smoothing method, bounds and default-off control before implementation. Live Editor/packaged verification remains Lead-owned.

## Claim and invariant

The proposed opt-in smoothing reduces abrupt boss facing changes while following the current target direction. Default behavior remains unchanged and the feature is off unless explicitly enabled. Smoothing must not change target selection, attack/card choice, attack eligibility, hit timing, damage, range, movement destination, or terminal behavior. This sheet does not choose a smoothing rate, angular cap, interpolation method, or acceptable error threshold.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw logs/video and hashes | **Expected:** unique IDs and immutable capture hashes. **Observed:** pending. |
| Build/map/profile/actors | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, boss/player/profile identities. **Observed:** pending. |
| Target trajectory | **Expected:** repeatable recorded target path, distance/height and encounter generation; same input/seed in each pair. **Observed:** pending. |
| Feature state | **Expected:** off by default/read-back off; enabled only in paired test. Record exact parameters. **Observed:** pending. |
| Sampling | **Expected:** synchronized target heading, boss yaw, angular velocity, attack/move state and timestamps at a documented sample interval. **Observed:** pending. |

## Paired cases

Repeat the same target direction changes with smoothing disabled/enabled from matched state; change only the reviewed toggle. Include a small turn, a large direction reversal, and a target direction change during an active attack only if the existing behavior safely supports it.

| Row | Required evidence | Pass condition |
|---|---|---|
| Disabled control | Record target yaw, boss yaw, angular error over time, movement and attack decisions. | Establishes current behavior; default remains unchanged. |
| Enabled turn | Repeat identical trajectory and capture the same values, plus smoothing parameters and start/settle times. | Angular change is smoother according to a reviewed metric, remains bounded, and converges within a reviewed error/time bound. No attack/movement semantics change. |
| Target reversal | Repeat a direction reversal; record peak angular rate, peak/settled error and direction overshoot. | No unbounded spin, wrong-way turn or persistent target-facing error under the approved bounds. |
| Gameplay guard | Compare selected card, attack start/active windows, hit outcomes, range and destination for each pair. | Any difference outside the specifically reviewed rotation presentation is a failure. |

## Evidence interpretation and limits

- **Measured:** timestamped target/boss headings, angular error/rate, movement/attack state and outcomes, with log/video references.
- **Inferred:** smoothing benefit only from a specified metric compared on equivalent trajectories; a single visual example does not establish general stability.
- **Manual:** animation quality, perceived responsiveness, clipping and whether the boss appears to track unnaturally.
- No interpolation model, rate, cap, settle time, angular error tolerance, or product feel target is approved here. Numerical thresholds must be specified before a pass can be issued.

## Failure and stop conditions

Fail if default changes, rotation becomes unbounded/unstable, approved error bounds are exceeded, target/attack/movement semantics change, or a stale target is followed after reset. Stop if the target trajectory cannot be replayed, angle conventions/sampling are not established, or an acceptable smoothing bound has not been reviewed. Missing telemetry is UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No parameter choice, source/asset changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before review.
