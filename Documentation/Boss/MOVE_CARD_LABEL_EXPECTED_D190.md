# Opt-in boss move-card debug label expected sheet (Queue D190)

Status: protocol only. No label or feature is implemented/enabled. Review default-off behavior, label fields and shipping policy before implementation. Live Editor/packaged proof remains Lead-owned.

## Claim and shipping boundary

The proposed debug label displays the currently selected/active move-card identity only when explicitly enabled; it is hidden by default. It must distinguish selected candidate from actually active card and must not change selection, execution, attack budget, timing, or combat. This sheet makes no claim that debug text or feature code is absent from Shipping: that requires inspection of the exact packaged binary/configuration, not source guards or Development observations alone. No player-facing display or shipping exposure policy is approved here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/screens and hashes | **Expected:** unique ID and immutable evidence/hash. **Observed:** pending. |
| Build/map/profile | **Expected:** exact build configuration, `/Game/OneBossFight/Levels/L_SevarogArena`, profile and generation. **Observed:** pending. |
| Card identity | **Expected:** candidate list/selected MoveId, executor active-card MoveId, card/profile identity and timestamps independently recorded. **Observed:** pending. |
| Feature state | **Expected:** label toggle off by default/read-back; enabled only in paired Development proof. **Observed:** pending. |
| Shipping evidence | **Expected:** exact Shipping package hash, config and binary-level string/code inspection if making absence/exposure claim. **Observed:** UNKNOWN until reviewed. |

## Paired cases

Replay the same card-selection/execution scenario with label disabled/enabled, changing only the reviewed debug toggle.

| Row | Required evidence | Pass condition |
|---|---|---|
| Hidden/default control | Capture candidate, selection, active card and screen with label off. | No label is visible; combat establishes baseline. |
| Enabled selected/active | Capture candidate decision and subsequent active executor card with exact MoveIds and screen. | Label matches the intended state: if selected, it is explicitly marked candidate; if active, it matches the executor's actual active card. It cannot imply a move started before execution. |
| Refusal/end/reset | Capture refusal, normal end, abort and generation reset where reachable. | Label clears or updates according to the reviewed state policy; no stale candidate/active ID. |
| Gameplay guard | Compare selected/active card, budget, timing and outcomes off/on. | Debug display has no gameplay effect. |
| Shipping claim | Inspect the exact Shipping binary/package hash, not only source/build scripts. | Any statement about exposure/absence is limited to the inspected artifact/config; without binary evidence, mark UNKNOWN and make no shipping claim. |

## Evidence interpretation and limits

- **Measured:** candidate/active MoveId, executor state, generation and label text with raw references/screens.
- **Inferred:** label state only when matched to the corresponding candidate or active executor event; `MoveId` in a selector log alone does not prove execution.
- **Manual:** readability and whether internal IDs are unsuitable or confusing to a player.
- Development observations, `#if` guards, config defaults or source inspection do not prove Shipping binary exposure/absence. A binary-level result applies only to the recorded package hash/configuration.

## Failure and stop conditions

Fail if default-on, label confuses candidate with active, mismatches MoveId, persists stale state, or affects combat. Stop before any Shipping exposure claim if exact package and binary inspection are unavailable. Do not expose player identity or unrelated internal data. Missing evidence is UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No label/source changes, tests/build/Editor execution, package inspection, or runtime claim. Implementation and any Shipping claim require review.
