# Opt-in gap-closer landing cue expected sheet (Queue D164)

Status: protocol only. No cue, asset, or feature is implemented/enabled. Review default-off behavior and the landing event source before implementation. Live Editor/packaged proof remains Lead-owned; cue asset and presentation choices remain unselected.

## Claim and event boundary

The proposed optional cue occurs when the boss gap-closer actually lands, not merely when its montage reaches an end time. Evidence must correlate movement/floor contact or the approved landing event with the cue. It must not play on a canceled move, midair montage end, blocked movement, or unrelated attack. The cue must not change the landing location, movement, collision, attack result, timing, damage, or recovery. No specific source event, montage notify, sound, or visual asset is approved here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw logs/video/audio and hashes | **Expected:** unique IDs and immutable evidence hashes. **Observed:** pending. |
| Build/map/actors/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, boss/target/profile and generation. **Observed:** pending. |
| Gap-closer identity | **Expected:** selected card/asset, montage instance and start/end timestamps, movement start/end transforms, target identity and root-motion/movement state. **Observed:** pending. |
| Ground/contact evidence | **Expected:** floor/grounded readback or reviewed landing event, contact transform and timestamp. **Observed:** pending. |
| Feature state | **Expected:** cue toggle read back default-off; enabled only in paired run. **Observed:** pending. |

## Paired cases

Repeat the same gap-closer setup with the cue disabled/enabled, changing only its toggle. Include a valid landing, then safely reachable negative cases.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default-off landing control | Capture actual grounded/contact transition, transforms, montage timeline and audio/visual output. | Establishes landing and existing cue baseline; no new optional cue. |
| Enabled actual landing | Repeat; record landing event/contact and cue timestamps independently of montage position/end. | Cue follows measured landing within a reviewed tolerance; temporal association is not based solely on montage end. Landing/movement/combat outcome matches control. |
| Montage end without landing | Use a safe blocked/midair/canceled case where montage can end without actual landing. | No landing cue plays. If this condition cannot be created safely, leave the row UNKNOWN. |
| Abort/reset | Abort or restart during gap-close before landing where supported. | No stale cue after abort/reset and no cue attributed to a later generation. |

## Evidence interpretation and limits

- **Measured:** montage start/end and movement/contact/grounded event timestamps with raw references; direct cue recording/screenshot as applicable.
- **Inferred:** landing association only when independent contact evidence precedes/correlates with the cue. Montage completion alone does not establish landing.
- **Manual:** whether the cue communicates impact and remains audible/visible without masking other cues.
- Source traces or a montage notify do not prove actual floor contact. Authored map geometry, loaded notify/event wiring, and packaged playback remain UNKNOWN until live inspection.

## Failure and stop conditions

Fail if default-on, cue plays at montage end without landing, cue plays after abort/reset, or cue changes movement/collision/combat outcomes. Stop if independent landing evidence is unavailable, a reliable negative case cannot be produced safely, or the cue requires an unreviewed event/asset choice. Missing/invalid setup is inconclusive.

## Verification boundary

Expected protocol only. No cue asset, source/UI change, tests/build/Editor execution, or runtime claim. Implementation is not authorized before review.
