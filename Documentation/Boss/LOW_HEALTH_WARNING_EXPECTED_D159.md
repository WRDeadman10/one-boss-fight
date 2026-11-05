# Opt-in low-health warning expected sheet (Queue D159)

Status: protocol only. No warning, threshold, or feature is implemented/enabled. The owner must approve the health threshold and policy before implementation; this sheet intentionally assigns no number. Lead owns live Editor/packaged verification.

## Claim and decision boundary

The proposed warning is opt-in, one-shot per approved low-health crossing/reset interval, and has no gameplay effect. It may not change health, damage, healing, invulnerability, attacks, input, phase, or death. Threshold value, max-health basis (absolute vs fraction), recovery/hysteresis behavior, display/cue, and reset policy require explicit owner/Lead decision; do not infer them from a test boundary.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw logs/screens/audio and hashes | **Expected:** unique ID and immutable evidence hashed after capture. **Observed:** pending. |
| Build/map/actor/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, boss/player identity and health configuration. **Observed:** pending. |
| Approved threshold | **Expected:** owner-approved value and basis with decision reference. **Observed:** **UNKNOWN / decision required**; no boundary run is valid until this is supplied. |
| Feature/reset state | **Expected:** warning toggle read back default-off; record encounter generation, warning latch and approved reset route. **Observed:** pending. |
| Health source | **Expected:** exact health and maximum-health readback at each observation; record unrelated damage/heal sources. **Observed:** pending. |

## Paired cases (only after threshold approval)

Let `T` denote the approved threshold and use a fixed, recorded health basis. Compare default-off control and enabled behavior from matching baselines; change only the reviewed warning toggle.

| Case | Required observation | Pass condition |
|---|---|---|
| Above threshold | Health just above `T`, with exact readback and no crossing event. | No warning before the approved crossing condition. |
| Equal threshold | Health exactly `T`; record whether the approved policy uses inclusive or exclusive comparison. | Behavior matches that explicit decision; no inferred inequality. |
| Below threshold | Cross below `T` once; capture health, timestamp, generation, and visible/audible warning. | Enabled warning appears once at the approved crossing; default-off has no new warning. No health/gameplay mutation from warning. |
| One-shot | Remain below `T` and generate additional health updates/damage events. | No duplicate warning within the approved latch interval. |
| Recovery and recross | Recover above the approved reset/rearm point, then cross again. | Rearm behavior matches the approved policy; no assumption about hysteresis is made here. |
| Encounter restart | After warning fires, restart into a new generation and repeat the crossing. | Old warning/latch clears; new-generation behavior matches explicit reset policy. |

## Evidence interpretation and limits

- **Measured:** health/max health, generation and event timestamps with raw line references; warning visibility/audio from screenshot/video or direct observation.
- **Inferred:** threshold crossing and one-shot behavior only when the approved health basis, comparison operator and event sequence are known.
- **Manual:** warning clarity, placement, duration, audibility/accessibility and whether it obscures combat.
- Until the owner approves `T` and comparison/reset policy, all above/equal/below results are blocked/UNKNOWN. A source constant or pack default is not owner approval.

## Failure and stop conditions

Do not implement or run threshold acceptance until an owner decision supplies the threshold basis/value and equality/reset policy. After approval, fail if default-on, warning fires outside policy, duplicates before rearm, fails to reset by policy, or changes gameplay/health. Stop on ambiguous health basis, unrelated mutations, unrecorded generation, or missing direct warning evidence. Invalid setup is inconclusive.

## Verification boundary

Expected protocol only. No threshold chosen, UI/audio/assets/source changes, tests/build/Editor execution, or runtime claims. The feature remains unapproved pending owner decision and review.
