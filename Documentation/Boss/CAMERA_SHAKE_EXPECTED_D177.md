# Opt-in camera impact shake expected sheet (Queue D177)

Status: protocol only. No camera shake profile or feature is implemented/enabled. Review default-off behavior and trigger before implementation. Live Editor/packaged proof is Lead-owned; amplitude/duration/frequency and camera ownership remain unselected.

## Claim and trigger boundary

The proposed optional camera shake occurs only for the reviewed accepted-hit event. It must not occur for a refused/rejected event or mere trace/overlap candidate. Enabling shake must not change hit acceptance, damage, stamina, posture, parry/guard outcome, target, movement or encounter state. The exact camera to affect (player, boss, or both) and shake parameters require review.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/video and hashes | **Expected:** unique IDs; immutable video/log evidence and post-capture hash. **Observed:** pending. |
| Build/map/actors/camera | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, actors, controller and active camera identity. **Observed:** pending. |
| Hit event | **Expected:** attack instance, target, hit key, accepted/refused outcome and timestamps independently recorded. **Observed:** pending. |
| Feature state | **Expected:** shake toggle read back default-off; enabled run records exact reviewed trigger/parameters. **Observed:** pending. |
| Camera capture | **Expected:** fixed camera, FOV, resolution and frame capture; note any other camera effects. **Observed:** pending. |

## Paired cases

Replay the same contact scenario with shake off/on, changing only the reviewed toggle. Keep event identity and camera setup matched.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default-off accepted hit | Record accepted outcome, gameplay fields and camera video with shake off. | No new shake is visible; establishes camera and combat baseline. |
| Enabled accepted hit | Repeat same accepted hit; capture event and camera motion, plus damage/resources/outcome. | Shake follows the accepted hit within the reviewed timing; combat outcomes match control. |
| Refused/rejected event | Cause a safely controlled refused event with no accepted hit; capture trace/candidate and final outcome plus video. | No shake. A candidate overlap/trace must not be misclassified as accepted. |
| Repeated/overlapping event | If supported, exercise separate accepted hits and any duplicate callback path. | One approved shake per accepted event, no shake for duplicate/refused events; exact overlap policy must be reviewed. |

## Evidence interpretation and limits

- **Measured:** final hit outcome and combat fields with raw references; camera pose/video before, during and after event.
- **Inferred:** causality only when accepted/refused identity is correlated to camera motion and other camera modifiers are controlled.
- **Manual:** shake comfort, visibility, readability and motion-sensitivity review under recorded camera settings.
- Video motion alone cannot prove which system caused it. No accessibility guarantee, amplitude, duration, frequency or affected-camera policy is approved here.

## Failure and stop conditions

Fail if default-on, shake occurs on a refused event, accepted trigger is missed against reviewed policy, duplicate event causes extra shake, or gameplay changes. Stop if camera ownership/effects cannot be isolated, event outcome cannot be distinguished, or motion parameters require an unreviewed choice. Missing evidence remains UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No camera/assets/source changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before review.
