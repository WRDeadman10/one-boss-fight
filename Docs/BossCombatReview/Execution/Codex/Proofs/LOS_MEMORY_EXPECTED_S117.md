# S117 — LOS memory proof checklist

## Setup and evidence inputs

Use the AWR007 fixture with `LosSearchSeconds=3.0` (authoring/readback `Claude/B_AWR007/create_los_content.py:102–105`; retained content readback `content_run3/editor_raw.log:1373`). The target starts at `(0,0)`, the boss starts at `(500,0)`, and the pillar is centered at `(128,100,250)` with a 100×100×600 cm box (`create_los_content.py:146–163`). The retained trace logs the blocker as `StaticMeshActor_1`; do not infer a successful occlusion from target coordinates alone.

## Occluded and regain pass

After the current card finishes, shift the target by `(200,500,0)` while the pillar blocks the boss-to-target visibility trace. Required order:

1. `target_shift_injected n=1 dx=200 dy=500 dz=0`.
2. `los_lost lastKnownX=0 lastKnownY=0 blocker=<pillar>`; the last-known point is the target's last visible position (`RPGBossTrackRules.h:54–68`).
3. `los_search_start x=0 y=0`; source must request movement to that last-known point and return before selector decisions (`RPGFrameworkBossCharacter.cpp:376–385`). Add a labeled manual observation/video that the boss actually moves toward `(0,0)` while sight remains blocked and starts no blind card. This token reports the request; it does not prove movement reached the point.
4. When the target becomes visible, `los_regained lostForSeconds=<0..3>` then `los_resume`; the actor stops search movement and requests a normal walk back to its authored band (`RPGFrameworkBossCharacter.cpp:386–394`). Confirm the subsequent `walk start` is within the band, then a later `playback_start` follows regain.

Existing `pie_hide/editor_raw.log:1662–1663,1708–1712,1758` shows loss with last-known `(0,0)`, search request, regain at 0.916667 s, resume, a band arrival at range 128.132 cm, and later playback. The retained log lacks a labeled movement observation for step 3; keep that criterion manual.

## No-regain timeout pass

Use the same fixture with an occluded target point that remains hidden beyond three seconds. Expect `los_lost`, then `los_search_start x=0 y=0`, then exactly one `los_search_timeout seconds=3`; no `los_regained` or `los_resume` may appear in that hidden interval (`RPGBossTrackRules.h:58–68`). Existing `pie_hide_no_regain_target_x128/editor_raw.log:1662,1707–1708` shows the timeout line. Keep this as a separate run from the regain pass.

## Negative control

Keep the target visible in the same fixture (do not inject a shift behind the pillar), with the same 3 s profile. Expect normal decisions/playback and no `los_lost`, `los_search_start`, `los_regained`, `los_resume`, or `los_search_timeout`. No retained inside-LOS control was found in the AWR007 evidence folder; capture this before claiming a paired proof.

The early active card may finish after LOS is lost; LOS handling begins at a neutral decision gate. Do not require an in-progress card to abort on LOS loss. `pie_hide_resume_walk_failed_pillar_in_the_corridor` is a failed navigation setup and must not be used as a regain pass. No new runtime run was performed for this checklist.

## Setup
## Control
## PASS
## FAIL
