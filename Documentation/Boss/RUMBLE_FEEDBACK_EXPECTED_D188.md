# Opt-in controller rumble feedback expected sheet (Queue D188)

Status: protocol only. No rumble effect or feature is implemented/enabled. Review default-off behavior, pattern and user-setting policy before implementation. Live Editor/packaged/platform proof is Lead-owned.

## Claim and platform boundary

The proposed optional rumble feedback is triggered only by the reviewed accepted-parry event and respects the platform/controller's rumble support and user settings. It must not alter hit/parry semantics, damage, stamina, posture, timing, input, or existing sound/visual behavior. No motor pattern, strength, duration, platform matrix or settings override is approved here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/video and hashes | **Expected:** unique ID and immutable evidence/hash. **Observed:** pending. |
| Build/map/player/controller | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, platform, controller model/connection and player identity. **Observed:** pending. |
| Platform support/settings | **Expected:** device support readback, operating-system/game rumble setting and user opt-in state. **Observed:** pending. |
| Trigger identity | **Expected:** accepted-parry event, attack instance, target, grade and timestamp independent of haptics. **Observed:** pending. |
| Feature/pattern | **Expected:** feature off by default; approved event mapping, motor pattern/strength/duration recorded when enabled. **Observed:** UNKNOWN pending review. |

## Paired cases

On a supported controller with user rumble enabled, compare off/on for the same accepted-parry scenario. Keep the user/platform settings and game state fixed. Include negative and unsupported/disabled settings cases.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default-off accepted parry | Capture accepted event, platform settings and controller output with feature off. | No new rumble occurs; baseline behavior captured. |
| Enabled accepted parry | Repeat with feature enabled and user rumble enabled; capture event/output timing. | Approved rumble occurs once after the accepted event; gameplay state/outcomes match control. |
| No-event control | Press without accepted parry and exercise a refused/non-parried event. | No rumble. A press or candidate overlap alone is not a trigger. |
| User setting disabled | With feature enabled but platform/user rumble disabled, exercise accepted parry. | No rumble override; setting remains disabled and game behavior stays unchanged. |
| Unsupported/disconnected device | If safely testable, use unsupported/disconnected controller and record capability handling. | Graceful no-op with no crash, hidden fallback or gameplay mutation. |

## Evidence interpretation and limits

- **Measured:** accepted/refused event identity, platform/controller/settings readback and any available haptic event telemetry; log raw references.
- **Inferred:** output occurred only when support and user settings allow it; controller telemetry may not prove physical motor perception.
- **Manual:** perceived strength, comfort, accessibility, and whether rumble is distinguishable from other effects.
- No platform capability, strength/duration, user-setting override or accessibility guarantee is approved. A log that requests rumble does not establish that hardware produced it.

## Failure and stop conditions

Fail if default-on, rumble occurs without accepted parry, user-disabled settings are overridden, unsupported devices crash, or gameplay changes. Stop if platform support/settings cannot be read, accepted event is ambiguous, or pattern values require an unreviewed choice. Missing evidence remains UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No haptics/assets/source changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before review.
