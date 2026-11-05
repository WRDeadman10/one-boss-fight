# Opt-in line-of-sight debug overlay expected sheet (Queue D169)

Status: protocol only. No overlay or feature is implemented/enabled. Review default-off behavior and displayed fields before implementation. Live Editor proof is Lead-owned; this sheet does not authorize changes to LOS gameplay.

## Claim and evidence independence

The proposed overlay displays the LOS result used by the source rule. It must be hidden by default and display-only. Enabling it must not change trace channel, trace endpoints, target/actor positions, attack eligibility, selection, movement, or damage. The overlay is not its own proof: each row must independently record source actor positions and the actual trace inputs/result, including blocker identity where available.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw logs/video and hashes | **Expected:** unique ID and immutable evidence hashes. **Observed:** pending. |
| Build/map/actors/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, source/target actor identity and generation. **Observed:** pending. |
| Positions and trace | **Expected:** world-space start/end positions, trace channel, collision params, result and hit actor/component recorded independently of overlay. **Observed:** pending. |
| Feature state | **Expected:** overlay read back off by default; enabled only in paired run. **Observed:** pending. |
| LOS scenarios | **Expected:** one clear path and one safely controlled obstructed path using known geometry. **Observed:** pending. |

## Paired cases

Repeat each scenario with overlay disabled/enabled from the same actor transforms and configuration; change only the display toggle.

| Row | Required evidence | Pass condition |
|---|---|---|
| Clear path | Record source actor positions, trace start/end/channel/result and screen with overlay off and on. | Overlay matches the independently measured clear trace result; trace and gameplay behavior are unchanged. |
| Obstructed path | Repeat with a known blocker; record blocker actor/component and hit point. | Overlay matches the actual trace obstruction and actor positions; gameplay behavior is unchanged. |
| Position/target movement | Move target or source through a controlled sequence; capture every sample and overlay update. | Display follows current source positions/results and does not retain stale LOS after movement or generation reset. |
| Toggle-off regression | Disable after overlay run and repeat a baseline scenario. | Original trace/result and gameplay behavior remain unchanged; overlay is absent. |

## Evidence interpretation and limits

- **Measured:** source and target world positions, trace inputs/result/blocker and timestamps with raw file/line references; overlay screenshot/video.
- **Inferred:** overlay correctness only by comparing displayed values with independent trace evidence for the same sample/time.
- **Manual:** overlay readability and whether it obscures aim/telegraph/combat view.
- A line drawn on screen does not establish the actual trace channel or gameplay LOS decision. A source actor label alone does not identify the hit component. Loaded Blueprint/geometry behavior remains UNKNOWN until live observation.

## Failure and stop conditions

Fail if default-on, display disagrees with trace inputs/result, overlay changes LOS or gameplay behavior, or stale result persists after position change/reset. Stop if trace endpoints/channel are not independently available, blocker geometry cannot be identified, or overlay sample timing cannot be aligned. Missing evidence is UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No overlay/trace/source/geometry changes, tests/build/Editor run, or runtime claims. Implementation is not authorized before review.
