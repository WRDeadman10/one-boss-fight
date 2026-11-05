# Opt-in strafe-stuck debug overlay expected sheet (Queue D167)

Status: protocol only. No overlay or feature is implemented/enabled. Review the overlay fields and default-off behavior before implementation. Live Editor proof is Lead-owned; this debug protocol does not authorize gameplay wiring changes.

## Claim and evidence independence

The proposed overlay exposes strafe-stuck detector state for debugging and must be hidden by default. Enabling it must not change detector input, movement, direction flips, attack selection, or recovery. Overlay text is not independent evidence that the detector is correct: a positive requires controlled blocked movement and detector telemetry derived from the actual rule/state path, correlated with separate movement measurements. The visual overlay may only be treated as a presentation of that telemetry.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/video and hashes | **Expected:** unique ID and immutable raw evidence/hash. **Observed:** pending. |
| Build/map/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, boss/player/profile identity. **Observed:** pending. |
| Geometry and movement | **Expected:** record capsule/nav/floor geometry, target, strafe start/end transforms, commanded direction and measured displacement. **Observed:** pending. |
| Detector settings | **Expected:** exact stuck threshold/window, sample counts and reset state; identify the source telemetry independent of overlay. **Observed:** pending. |
| Feature state | **Expected:** overlay toggle read back off by default and enabled only in paired run. **Observed:** pending. |

## Paired cases

Run the same controlled strafe scenarios with overlay disabled/enabled; change only the display toggle. Include one genuinely blocked interval and one unblocked movement interval.

| Row | Required evidence | Pass condition |
|---|---|---|
| Hidden control | Capture detector telemetry, movement samples and screen with overlay off. | Overlay is absent; independent telemetry still records the detector state. |
| Enabled blocked interval | Constrain movement using reviewed safe test geometry. Capture overlay, raw detector counters/state, displacement and threshold crossing timestamps. | Overlay fields match the independently logged rule/state values; blocked movement is physically established; detector event timing follows configured logic. Enabling overlay does not change movement or recovery. |
| Enabled unblocked interval | Repeat in open geometry with movement above the detector's stuck criterion. | Overlay reports the source state accurately and does not claim stuck; no spurious recovery/flip is caused by display. |
| Toggle-off regression | Disable after enabled run and repeat same scenario. | Gameplay/detector state matches the initial hidden control. |

## Evidence interpretation and limits

- **Measured:** independent movement displacement, source detector inputs/outputs/counters and timestamps; overlay screenshot/video and raw text.
- **Inferred:** detector correctness only from measured geometry/displacement and the configured rule. Overlay content alone is circular evidence and cannot pass the detector claim.
- **Manual:** overlay readability and whether it obscures gameplay.
- Editor-authored geometry and actual nav blockage require live verification. A source-level threshold or displayed `stuck=1` does not establish that movement was physically blocked.

## Failure and stop conditions

Fail if default-on, overlay disagrees with source telemetry, overlay changes gameplay, stuck is reported without independently blocked movement, or actual blocked movement is missed against the approved threshold. Stop if movement cannot be measured independently, test geometry is unsafe, or overlay fields are not specified/reviewed. Missing evidence is UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No overlay/source/UI/geometry edits, tests/build/Editor run, or runtime claims. Implementation is not authorized before review.
