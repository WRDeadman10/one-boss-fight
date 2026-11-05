# Opt-in boss combo-depth display expected sheet (Queue D184)

Status: protocol only. No display or feature is implemented/enabled. Review default-off behavior, text and depth definition before implementation. Live Editor/packaged proof is Lead-owned. No combo balance or graph changes are authorized.

## Claim and graph boundary

The proposed optional display shows current combo depth derived from the active combo graph state. It must match the authoritative node/depth transition and must not change graph traversal, branch choice, attack budget, candidate eligibility, hit acceptance, damage, timing or reset behavior. The display is informational; it cannot be treated as proof of underlying graph state without independent node/depth telemetry. No depth-label wording or graph semantics are selected here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/screens and hashes | **Expected:** unique ID, immutable evidence/hash. **Observed:** pending. |
| Build/map/profile/graph | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, profile, graph identity/root/version and resolved node MoveIds. **Observed:** pending. |
| Depth contract | **Expected:** authoritative depth variable, root counting convention, maximum depth and transition events read back. **Observed:** UNKNOWN pending review. |
| Feature state | **Expected:** display off by default/read-back; enabled only in paired run. **Observed:** pending. |
| Event sequence | **Expected:** accepted combo transitions, branch, refusal, abort and restart identities/timestamps. **Observed:** pending. |

## Paired cases

Replay identical combo graph inputs and seed with display hidden/enabled. Change only the reviewed display toggle and compare displayed text to independent graph node/depth evidence after every transition.

| Row | Required evidence | Pass condition |
|---|---|---|
| Root/start | Record graph root, active node and depth convention before/after first accepted transition. | Display equals the reviewed root/depth rule and matches source node state. |
| Branch/deeper node | Capture selected branch MoveId, graph node/depth before/after and text. | Text follows actual active node/depth, not merely selected candidate or intended branch. |
| Refusal/abort/end | Capture node/depth and visible text after refusal, canceled transition and normal completion. | Text clears or holds only as the reviewed state contract defines; no stale depth is shown as active. |
| Restart/new generation | Record old/new graph identity, generation and displayed value. | Old depth clears and new generation begins at reviewed root depth. |
| No-balance-change guard | Compare selected branch, attacks, budget, depth transitions and combat results off/on. | Display-only feature produces identical graph and combat behavior. |

## Evidence interpretation and limits

- **Measured:** graph/node/MoveId, independent depth value, generation, event and display text with raw references/screenshots.
- **Inferred:** display correctness only from same-event node/depth correlation. A candidate decision does not prove a node transition occurred.
- **Manual:** readability and whether the text aids understanding without obscuring combat.
- No root counting, max-depth or reset convention is approved here. Logs showing depth text alone cannot prove graph traversal or absence of balance change.

## Failure and stop conditions

Fail if default-on, displayed depth disagrees with active graph state, candidate is shown as active before transition, stale depth survives reset, or enabling display changes branch/budget/combat outcomes. Stop if graph/depth contract cannot be independently read back. Missing evidence remains UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No graph/profile/source/UI changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before review.
