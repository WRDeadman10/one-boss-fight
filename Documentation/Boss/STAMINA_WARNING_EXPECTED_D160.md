# Opt-in stamina warning cue expected sheet (Queue D160)

Status: protocol only. No warning cue, threshold, or feature is implemented/enabled. Review the protocol and default-off behavior before implementation. Live Editor/packaged proof is Lead-owned. The exact trigger, modality, presentation and threshold need review; this sheet does not choose them.

## Claim and invariant

The proposed optional cue signals the reviewed low-stamina condition. It must only observe stamina and must not spend, restore, clamp, reserve, or otherwise mutate `Attribute.Stamina`; it also must not change parry/attack input, acceptance, timing, damage, posture or recovery. `RPGParryCostRules.h` describes parry spend/refund rules but is not a warning threshold or approval for a product cue.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw logs/screens/audio and hashes | **Expected:** unique IDs and immutable evidence with post-capture hashes. **Observed:** pending. |
| Build/map/player | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, player/controller and stamina component identity. **Observed:** pending. |
| Approved trigger | **Expected:** owner/Lead-approved threshold and basis, trigger edge/repeat/reset policy, and modality. **Observed:** UNKNOWN until decided. |
| Feature state | **Expected:** toggle read back default-off; record enabled value and all related configuration. **Observed:** pending. |
| Resource state | **Expected:** exact current/max `Attribute.Stamina` before/after, all spend/refund events, and unrelated stamina consumers. **Observed:** pending. |

## Paired cases

After trigger policy is approved, use the same player, resource values, action/event sequence and build for disabled/enabled comparisons; change only the cue toggle.

| Row | Required evidence | Pass condition |
|---|---|---|
| Disabled low-stamina control | Reach the approved low-stamina condition with cue off; capture before/after stamina, maximum, resource mutations and screen/audio. | No new cue is emitted; establishes resource and gameplay baseline. |
| Enabled low-stamina condition | Repeat same sequence with cue enabled; capture condition, cue timing, resource values and parry/attack outcomes. | Cue matches the reviewed trigger; stamina and all gameplay outcomes match control exactly, accounting for only independently measured game actions. |
| Above/clear boundary | If the approved policy defines boundaries or recovery, test above threshold and recovery/rearm with both states. | Cue appears/clears/rearms only as approved; no resource mutation or gameplay change. |
| No-resource-event interval | Hold low stamina with no spend/refund while the warning is active. | Cue itself produces no `Attribute.Stamina` change, repeated spend, refund, input change or gameplay transition. |

## Evidence interpretation and limits

- **Measured:** stamina current/max readbacks and spend/refund events with raw file/line references; cue timing and direct screenshot/audio recording.
- **Inferred:** resource equivalence only if all other stamina sources are accounted for and paired actions match.
- **Manual:** cue audibility/legibility, timing clarity, accessibility and whether it masks combat sounds or visuals.
- Until trigger value/basis and reset semantics are approved, low/above/boundary cases remain UNKNOWN. A cue log or source condition cannot prove perceived output or unchanged resources by itself.

## Failure and stop conditions

Fail if enabled cue changes stamina or gameplay, fires outside the approved trigger, is on by default, or cannot clear/rearm as reviewed. Stop if trigger policy is missing, unrelated resource consumers cannot be isolated, or cue output cannot be directly observed. Missing or invalid evidence is inconclusive, not a pass.

## Verification boundary

Expected protocol only. No threshold/modality choice, UI/audio/assets/source changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before review.
