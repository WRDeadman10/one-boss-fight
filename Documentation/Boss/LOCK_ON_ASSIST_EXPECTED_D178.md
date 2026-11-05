# Opt-in camera lock-on assist expected sheet (Queue D178)

Status: protocol only. No assist behavior, strength, or default change is implemented/enabled. Owner approves assist strength and allowed targeting behavior before implementation. Live Editor/packaged verification is Lead-owned.

## Claim and boundary

The proposed opt-in assist adjusts camera tracking toward an explicitly selected target along a fixed path. Default camera/target behavior remains unchanged when off. Assist strength must not silently change target identity, attack selection, player input acceptance, damage or movement. No strength, angular rate, target-switch rule or camera ownership is selected here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/video and hashes | **Expected:** unique ID and immutable capture/hash. **Observed:** pending. |
| Build/map/actors/camera | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, player/controller, active camera and target identity. **Observed:** pending. |
| Fixed target path | **Expected:** same recorded target trajectory, distance/height, occlusion and encounter state across pairs. **Observed:** pending. |
| Feature state/strength | **Expected:** default off/read-back; exact owner-approved enabled strength and any rate/limits. **Observed:** UNKNOWN until approved. |
| Tracking samples | **Expected:** target bearing, camera yaw/pitch, angular error, input and target changes with synchronized timestamps. **Observed:** pending. |

## Paired cases

Replay the identical target path with assist disabled/enabled, changing only the reviewed assist toggle/strength. Include target motion across center and a controlled occlusion only if safe and supported.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default tracking control | Capture target bearing, camera orientation/error and user input with assist off. | Establishes baseline target tracking and camera behavior. |
| Enabled fixed-path tracking | Repeat path with approved assist; record same fields and strength. | Assist response follows approved bounded strength; target identity stays the same and unrelated gameplay is unchanged. |
| User input interaction | Apply a repeatable camera input during tracking in both modes. | Input semantics match reviewed policy; assist does not override or invert input unexpectedly. |
| Occlusion/target-loss case | If supported safely, record target visibility, selected target and camera behavior on loss/reacquisition. | No hidden target switch or camera snap outside approved policy. If policy is unspecified, stop and leave UNKNOWN. |
| Toggle-off regression | Disable after enabled run and repeat path. | Camera returns to original default behavior. |

## Evidence interpretation and limits

- **Measured:** target identity/bearing, camera orientation/angular error, input, assist setting and timestamps from raw logs/video.
- **Inferred:** assist effect only from paired fixed-path samples; reduced angular error alone does not prove good control feel.
- **Manual:** comfort, agency, target visibility, occlusion response and whether tracking feels intrusive.
- No strength/rate, supported target class, input priority or target-loss policy is approved here. A visually centered target does not prove the system selected the intended target.

## Failure and stop conditions

Do not implement before owner approves strength and behavior boundaries. Fail if default behavior changes, target identity changes without explicit policy, camera snaps/oscillates beyond approved bounds, user input is unexpectedly suppressed, or gameplay outcomes change. Stop if fixed path/camera samples or target identity cannot be read back. Missing evidence is UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No strength chosen, camera/source changes, tests/build/Editor execution, or runtime claims. Implementation is not authorized before review.
