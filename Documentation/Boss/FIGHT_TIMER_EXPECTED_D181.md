# Opt-in fight timer HUD expected sheet (Queue D181)

Status: protocol only. No timer HUD is implemented/enabled. Review default-off behavior, clock basis and display format before implementation. Live Editor/packaged proof is Lead-owned.

## Claim and boundary

The proposed timer is informational only. It records a reviewed fight-start event, stops on approved terminal state, and resets under a new generation ID. It must not pause/advance gameplay, alter AI, input, damage, attack selection, speed, or terminal classification. No clock basis, start trigger, precision, or stop taxonomy is approved here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/video and hashes | **Expected:** unique immutable evidence and post-capture hash. **Observed:** pending. |
| Build/map/actors | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, boss/player and encounter identity. **Observed:** pending. |
| Generation IDs | **Expected:** record run/generation on fight start, every sample and terminal/reset; distinguish restarted attempts. **Observed:** pending. |
| Clock contract | **Expected:** approved real/game clock, pause/dilation behavior, precision and reset/start/stop events. **Observed:** UNKNOWN until reviewed. |
| Feature state | **Expected:** timer display off by default/read-back; enabled only in paired run. **Observed:** pending. |

## Paired cases

Use matched fight-start and terminal scenarios with display hidden/enabled, changing only the reviewed toggle.

| Row | Required evidence | Pass condition |
|---|---|---|
| Hidden control | Record authoritative fight start/terminal and generation IDs with timer display off. | No new timer display; gameplay baseline is unchanged. |
| Enabled fight | Capture timer samples and authoritative start/stop events on the approved clock. | Timer begins/stops at approved events, is monotonic within that clock contract, and is only informational. |
| Restart | Finish or abort an attempt, restart with a new generation and capture old/new timer values. | New generation resets per policy; old value does not leak or continue. |
| Pause/dilation | If supported, exercise known pause/time-dilation while recording both real and game clocks. | Display behavior matches the approved clock contract; no inference from a frozen clock. |
| Gameplay guard | Compare attack/state transitions and timing with display off/on. | Enabling or rendering the timer causes no gameplay mutation or scheduling effect. |

## Evidence interpretation and limits

- **Measured:** generation/start/terminal events, timestamp samples and timer display with raw references.
- **Inferred:** elapsed time only from a defined clock source and sample resolution; formatting precision cannot exceed underlying evidence.
- **Manual:** readability, placement and whether display distracts from combat.
- No clock basis, pause/dilation policy, display precision or terminal stop taxonomy is approved. A displayed number alone cannot prove correct start/stop or generation reset.

## Failure and stop conditions

Fail if default-on, timer is nonmonotonic contrary to contract, start/stop/reset mismatches authoritative events, generations leak, or gameplay changes. Stop if event identity/clock basis is unclear or paired runs differ. Missing evidence remains UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No HUD/source changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before review.
