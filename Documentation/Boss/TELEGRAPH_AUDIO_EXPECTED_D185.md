# Opt-in attack telegraph accessibility audio expected sheet (Queue D185)

Status: protocol only. No cue, sound asset, or feature is implemented/enabled. Review default-off behavior, cue mapping and timing before implementation. Live Editor/packaged audio verification remains Lead-owned; no pack sound is to be replaced by this protocol.

## Claim and event boundary

The proposed optional audio cue supplements the existing attack telegraph for accessibility. It must associate with the exact attack event that started the warning, and must not play for a refused/unstarted attack or a different attack. It must not change attack selection, warning duration, parry/hit windows, movement, damage or existing pack sounds. No cue mapping, sound asset, repetition policy or mixing value is approved here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw logs/audio/video and hashes | **Expected:** unique ID and immutable captures hashed after run. **Observed:** pending. |
| Build/map/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, profile and generation. **Observed:** pending. |
| Attack identity | **Expected:** exact selected card/MoveId, attack instance/sequence, telegraph start/end, phase and target. **Observed:** pending. |
| Cue mapping/state | **Expected:** approved mapping from attack event to cue identity, toggle off by default/read-back and enabled config. **Observed:** UNKNOWN pending review. |
| Audio environment | **Expected:** fixed output device, volume, capture route and relevant pack sounds identified. **Observed:** pending. |

## Paired cases

Replay the same attack/event sequence with audio cue disabled/enabled; change only the reviewed toggle. Include a separate attack identity and a safely reachable refusal/no-start case.

| Row | Required evidence | Pass condition |
|---|---|---|
| Disabled paired control | Capture attack identity, existing telegraph/sounds, event timings and gameplay state with feature off. | No new accessibility cue; establishes event and audio baseline. |
| Enabled attack event | Repeat same event; capture cue identity/audio onset and attack instance, with telegraph/window times. | Cue is heard once at the reviewed event timing and is associated with the exact active attack; attack timing/gameplay matches control. |
| Different attack identity | Run a second approved attack whose cue mapping is reviewed. | Cue matches that attack's approved mapping, not the previous/next MoveId or stale instance. |
| Refusal/no-start/abort | Capture selection refusal or canceled attack and audio output. | No telegraph cue plays for an attack that never started; cue state clears on abort. |
| Existing sound preservation | Compare pack cue/audio events off/on. | Pack sounds remain intact and are not replaced, muted or delayed outside approved behavior. |

## Evidence interpretation and limits

- **Measured:** selected attack identity, instance, telegraph timestamps and cue/audio event with raw references/audio capture.
- **Inferred:** event association only when the cue's timestamp and attack instance uniquely match; proximity in time alone is insufficient if multiple attacks overlap.
- **Manual:** audibility, distinguishability, accessibility, mixing and whether the cue masks other sounds.
- No standard, cue/attack mapping, volume, timing tolerance or simultaneous-attack policy is approved. Audio capture does not prove all users perceive the cue.

## Failure and stop conditions

Fail if default-on, cue is missing/misassociated/duplicated, cue plays on refusal, existing pack audio is replaced/suppressed, or attack timing/combat behavior changes. Stop if overlapping attacks cannot be disambiguated, event identity is not observable, or cue mapping/mix requires an unreviewed choice. Missing evidence stays UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No sound selection, asset/source changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before review.
