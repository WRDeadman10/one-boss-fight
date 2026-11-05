# Opt-in high-contrast parry flash expected sheet (Queue D155)

Status: protocol only; no flash, palette, or feature is implemented/enabled here. Review the sheet and default-off behavior before implementation. Live Editor/packaged proof remains Lead-owned. Any flash color, shape, duration, location, or contrast target remains unselected pending the appropriate review.

## Claim and trigger boundary

The proposed flash is displayed only after an actually accepted parry. Pressing parry, opening a window, seeing a boss telegraph, or merely calculating a timing grade is not sufficient. `URPGPlayerParry::NotifyParried` records the grade on the receiving player component (`RPGPlayerParry.cpp:138-145`); the exact integration point for a visual cue is not authorized by this protocol. The flash must not affect parry acceptance, grade, damage, stamina/refund, posture, recovery, input, or existing sounds.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw logs/screenshots and hashes | **Expected:** unique IDs, immutable evidence and post-capture hashes. **Observed:** pending. |
| Build/map/actors | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, actual player/controller and pack boss identities. **Observed:** pending. |
| Feature state | **Expected:** display toggle read back off by default; enabled only for paired run. Record all hooks/CVars. **Observed:** pending. |
| Parry route and contact | **Expected:** real input binding, parry component, attack identity, contact result and computed grade. **Observed:** pending. |
| Visual/sound setup | **Expected:** fixed display settings and capture method; record existing sound/cue configuration so it can be compared. **Observed:** pending. |

## Paired cases

Reset the encounter and compare default-off and enabled runs with the same attack, input timing, actor/profile identities and seed. Change only the reviewed flash toggle.

| Row | Required evidence | Pass condition |
|---|---|---|
| Accepted parry | Real attack contact is positively identified as parried; capture parry window, accepted outcome, grade, health/stamina/posture/recovery and direct flash evidence with timestamp. | Enabled run shows the approved high-contrast flash after accepted parry; default-off control shows none. All measured gameplay results match the paired control. |
| Parry press without accepted contact | Press within a valid window but provide no accepted boss contact; capture press/window and outcome. | No flash: input alone is not acceptance. No change in input/window behavior. |
| Non-parried contact / refusal | Exercise a real non-parried hit or a no-grade/refusal case where safely reachable. Record actual outcome, resources and screen. | No flash unless the recorded result explicitly establishes an accepted parry. A failed setup or missing contact is inconclusive. |
| Existing sound behavior | Capture the same accepted-parry and negative cases with sound enabled under both feature states. | Existing sound cues remain present and their triggering/selection is unchanged; the visual feature does not replace or suppress pack sounds. |

## Evidence interpretation and limits

- **Measured:** parry outcome/grade and resource/combat logs with file/line references; screen capture and timestamps for flash visibility; recorded sound/cue identity or manual audio capture.
- **Inferred:** flash causality only when the accepted-parry event is present and negative controls are valid. Correlation with a press or grade calculation alone is insufficient.
- **Manual:** contrast/legibility, flash comfort, accessibility, occlusion, and sound audibility. These require direct review under recorded display/audio conditions.
- Do not claim a contrast standard or accessibility guarantee without separately approved measurement. Logs cannot establish that a player perceived the visual or audio cue.

## Failure and stop conditions

Fail if the default is enabled, flash appears without an accepted parry, an accepted parry lacks the enabled flash, any gameplay/resource result changes, or sound behavior is replaced/suppressed. Stop if accepted outcomes cannot be distinguished from presses, display conditions differ, the approved visual specification is absent, or a proposed cue requires an unreviewed product choice. Missing or invalid evidence stays UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No code/UI/assets, palette decision, tests/build/Editor execution, screenshots, or runtime claims. Implementation is not authorized before review.
