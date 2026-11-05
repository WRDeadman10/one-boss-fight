# Opt-in retry summary panel expected sheet (Queue D180)

Status: protocol only. No panel, text, or feature is implemented/enabled. Review default-off behavior, fields and presentation before implementation. Live Editor/packaged verification remains Lead-owned.

## Claim and boundary

The proposed optional panel summarizes the completed attempt for win, loss and restart outcomes. It must use the correct completed run/generation and must not change result classification, health/resources, retry eligibility, restart state, input or encounter progression. Hidden/default mode must preserve current behavior and show no new panel. No summary fields or player-facing text are approved here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw logs/screens and hashes | **Expected:** unique immutable evidence per attempt and post-capture hashes. **Observed:** pending. |
| Build/map/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, profile and generation. **Observed:** pending. |
| Result source | **Expected:** authoritative win/loss/restart state and transition timestamp, independent of panel. **Observed:** pending. |
| Summary schema | **Expected:** approved field list, source for each field, units/rounding, privacy/retention policy and generation association. **Observed:** UNKNOWN pending review. |
| Feature state | **Expected:** panel toggle read back off by default; enabled only for paired run. **Observed:** pending. |

## Paired cases

For each result class, compare hidden/default and enabled runs from equivalent setup; change only the panel toggle. Capture the independent result event and underlying source values.

| Row | Required evidence | Pass condition |
|---|---|---|
| Win summary | Authoritative completed win, generation, approved source fields and panel screenshot. | Panel appears only after the win and every displayed field matches the same completed generation. |
| Loss summary | Authoritative loss/death/failure class, source fields and panel screenshot. | Correct loss result appears; it is not conflated with restart or success. |
| Restart summary | Restart path and old/new generation IDs, source fields and panel state. | Summary is associated only with the intended attempt; prior values do not leak into new generation. |
| Hidden/default control | Repeat all reachable cases with feature off/read-back off. | No new panel appears; result classification, restart and gameplay match baseline. |
| Privacy/data check | Inspect displayed/stored fields, paths and logs under approved scope. | Only reviewed fields are disclosed; no raw host/session/path details appear without approval. |

## Privacy restriction

Any retry summary data remains local to the project/repository; do not publish or transmit it. Do not include player identity or identifying host/session data. If evidence is shared for review, use a separate scrubbed copy and retain the original locally unchanged.

## Evidence interpretation and limits

- **Measured:** authoritative result/generation and each displayed data source with raw references; screenshot/video of panel state.
- **Inferred:** field correctness only when the panel value is compared to its same-generation source; visually plausible text is insufficient.
- **Manual:** clarity, readability, accessibility and whether the panel obscures action.
- No panel fields, rounding, result taxonomy, persistence, privacy retention or presentation duration is approved. Logs do not prove what was actually rendered.

## Failure and stop conditions

Fail if default-on, wrong result class, stale-generation values, unapproved data disclosure, or any gameplay/restart state changes due to display. Stop if authoritative result source or field provenance is unclear, or summary schema requires owner decisions. Missing evidence is UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No UI/source/assets changes, tests/build/Editor run, or runtime claim. Implementation is not authorized before review.
