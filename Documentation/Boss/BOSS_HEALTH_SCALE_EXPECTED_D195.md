# Opt-in boss health scaling profile expected sheet (Queue D195)

Status: protocol only. No scalar/profile or default change is implemented. Owner approves values and balance evidence before implementation. Live Editor/packaged verification remains Lead-owned.

## Claim and ownership boundary

The proposed opt-in profile applies a bounded boss-health scalar while default maximum/current health behavior remains unchanged. The scalar must be read back at the authoritative health initialization/reset point and must not change player health/stats, damage routing, phase thresholds, attack selection, resistance, or encounter restart semantics outside the approved specification. No scalar, balance intent, or evidence threshold is selected here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs and hashes | **Expected:** unique ID, immutable raw logs and hash. **Observed:** pending. |
| Build/map/boss/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, boss actor/profile and generation. **Observed:** pending. |
| Default health baseline | **Expected:** configured max, runtime max/current before/after initialization, phase/reset behavior and source identity. **Observed:** pending. |
| Approved scalar | **Expected:** owner decision/reference, exact scalar, allowed range, application point and balance evidence plan. **Observed:** UNKNOWN pending decision. |
| Paired encounter inputs | **Expected:** same player build, attack sequence, seed, phase and damage sources across baseline/preset runs. **Observed:** pending. |

## Paired cases

After approval, compare default profile to the exact enabled scalar with matched encounter inputs; change only the scalar option.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default baseline | Capture configured/runtime max and current boss health before and after initialization/restart with feature off. | Existing default health behavior remains unchanged. |
| Enabled scalar readback | Capture configured scalar and actual max/current health at every initialization/phase/reset point. | Readback matches the approved scalar/application point; no double-scaling or unapproved reset behavior. |
| Damage/phase control | Record same accepted damage events, actual health deltas, phase transitions and terminal result under both runs. | Differences match the approved scalar-only specification; phase thresholds/semantics do not change unless explicitly approved. |
| Restart/default regression | Disable/restart and read max/current health and generation. | Default baseline is restored and no scaled value leaks across retries/generations. |
| Balance evidence | Run only the owner-approved sample plan with build/session identity and review results against approved target. | Report only measured outcomes; no balance claim without sufficient approved evidence. |

## Evidence interpretation and limits

- **Measured:** scalar readback, max/current health, damage event and phase/generation transitions with raw references.
- **Inferred:** scalar effect only if health initialization points and all damage sources are identified; max health alone does not prove actual time-to-kill or difficulty.
- **Manual:** perceived fight length/difficulty remains owner judgment.
- No health scalar, balance target, run count or acceptance tolerance is approved. A source constant or one fight is not balance evidence.

## Failure and stop conditions

Do not implement before owner approves the scalar, application/reset points and balance plan. Fail if default changes, health is scaled twice, current/max readback mismatches approved values, unrelated combat rules change, or scaled state leaks after restart. Stop if health initialization is not uniquely attributable or balance samples are insufficient. Missing evidence remains UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No scalar/profile/source changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before owner approval and review.
