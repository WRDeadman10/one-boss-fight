# Opt-in hold-to-parry input mode expected sheet (Queue D187)

Status: protocol only. No hold mode or default input change is implemented/enabled. Review press/hold/release semantics and default-off behavior before implementation. Live Editor/packaged proof is Lead-owned.

## Claim and input boundary

The proposed opt-in mode changes how a held input requests parry while preserving the existing default press behavior when disabled. It must not alter the parry window's configured duration, cooldown, grade thresholds, stamina cost/refund, hit acceptance, or unrelated input. No hold duration, repeat behavior, release-to-close rule or input threshold is approved here. Use ordinary manual input; no automated-input or usability claim is included.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/video and hashes | **Expected:** unique IDs and immutable evidence/hash. **Observed:** pending. |
| Build/map/player/controller | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarovArena`, player/controller/device and real parry binding. **Observed:** pending. |
| Input semantics | **Expected:** approved definition of press, hold, release, repeat and cancellation behavior. **Observed:** UNKNOWN pending review. |
| Parry configuration | **Expected:** same window, cooldown, grade, cost/refund values read back in both modes. **Observed:** pending. |
| Timing capture | **Expected:** input down/up, parry open/close, contact and grade timestamps on a defined clock. **Observed:** pending. |

## Paired cases

Use matched attacks and input timing with mode disabled/enabled; change only the reviewed hold-mode toggle. Record the physical/manual input edge events.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default tap control | One manual press/release with mode off; capture down/up, window, grade, cooldown and resource outcome. | Existing default press route is unchanged. |
| Enabled tap | Same press/release under enabled mode. | Tap behavior matches the approved mode design and does not change window/cooldown/grade/resource rules. |
| Enabled hold | Hold across the approved interval and release; capture edge events, window and any repeat/close behavior. | Behavior matches the reviewed hold contract; no unbounded open window or repeated costs/callbacks. |
| Timing equivalence | Use matched contact offsets relative to parry-window opening under both modes. | For the same accepted input timing, window duration and grade boundaries remain identical to baseline. |
| Cancel/focus loss | If supported, cancel/lose input focus while held and record cleanup. | Input and parry state close/reset according to approved policy; no stuck input/window. |

## Evidence interpretation and limits

- **Measured:** physical input edges, parry state/open-close, contact offset, grade, cooldown and resource values with raw references.
- **Inferred:** timing equivalence only when input edge and window timestamps share a defined clock and controlled contact timing.
- **Manual:** ease, fatigue, discoverability, and whether hold interaction feels responsive.
- No hold threshold, repeat cadence or release behavior is approved. Similar grade outcomes alone do not prove identical timing windows.

## Failure and stop conditions

Fail if default input changes, window/cooldown/grade/cost semantics differ, hold causes repeated spend or stuck state, or unrelated input changes. Stop if hold/release contract is undefined, manual edge timing cannot be recorded, or controller/input context differs between pairs. Missing evidence is UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No input/UI/source changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before review.
