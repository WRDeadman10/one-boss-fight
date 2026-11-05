# Opt-in boss attack-name prompt expected sheet (Queue D153)

Status: protocol only; no prompt is implemented or enabled. Review this sheet and default-off behavior before any implementation. Live Editor and packaged proof remain Lead-owned.

## Claim and source identity boundary

The proposed prompt displays the identity of the boss move actually selected for execution, and clears when selection is refused or the move ends. The stable source identity available to this protocol is `FRPGBossMoveCard::Spec().MoveId`; candidate/refusal telemetry and active executor state are emitted in `RPGFrameworkBossCharacter.cpp` (for example candidate/refusal around lines 463-464 and active-card overlay around 741). This does not prove a human-facing attack name exists or that the profile's `MoveId` is suitable player-facing copy. No name mapping, localization, placement, duration, or presentation choice is approved here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw log path, hash | **Expected:** unique run ID, immutable raw logs, SHA-256 after capture. **Observed:** pending. |
| Build/map/profile | **Expected:** exact executable/build, `/Game/OneBossFight/Levels/L_SevarogArena`, profile asset and profile identity. **Observed:** pending. |
| Boss and execution identity | **Expected:** actual boss actor, selected candidate, `MoveId`, card/profile identity, execution generation/sequence, and timestamps. **Observed:** pending. |
| Prompt state | **Expected:** explicit toggle read back off by default and on only for the paired run. **Observed:** pending. |
| Refusal/end triggers | **Expected:** a deterministic eligible card, a distinct refusal path, and a move end/abort path exercised through real execution. **Observed:** pending. |

## Paired rows

For each row, reset from the same recorded baseline and compare hidden default-off control to enabled prompt with only the reviewed toggle changed. Keep profile, candidate set, seed, and encounter conditions fixed.

| Row | Required evidence | Pass condition |
|---|---|---|
| Selected move | Candidate decision and prompt text are time-correlated with the execution start; capture source `MoveId`, profile/card identity, generation/sequence and direct screen evidence. | Prompt identifies the same card that the executor actually starts. A merely eligible candidate or rejected combo branch must not be shown as active. |
| Selection refusal | Cause a controlled refusal with no active card; capture refusal token/reason, active-card state and screen. | No new attack name appears for a refused selection. If a prior prompt is visible, it clears according to the reviewed rule. |
| Move end or abort | End a started move normally and separately exercise an existing abort/refusal terminal route. Capture terminal event, active-card state and screen timestamps. | Prompt clears on the approved terminal event and does not persist into idle, next generation, or next move. |
| Hidden control | Repeat all reachable rows with the feature default-off/read-back off. | No prompt is visible; combat selection, execution and terminal behavior match the enabled pair. |

## Evidence interpretation and limits

- **Measured:** candidate, refusal, start, active-card and terminal log events with raw file/line and sequence; prompt text and visibility from screenshot or direct Lead observation.
- **Inferred:** prompt-to-move association only when identities and generation/sequence match. Do not equate the last candidate line with the card that started.
- **Manual:** readability, display duration, placement, whether labels are understandable, and whether text obscures gameplay.
- Logs do not prove the player saw the prompt. `MoveId` does not by itself establish a designer-approved display name. No asset, widget, editor, or package behavior is evidenced by this protocol.

## Failure and stop conditions

Fail if prompt identity differs from the executor's active card, appears for a refusal, or remains after the approved end/abort event. Stop if source/log identities cannot correlate candidates to execution, if an ambiguous duplicate identity is encountered, if no deterministic refusal can be exercised safely, or if readable labels require an unreviewed product choice. Treat missing telemetry or invalid setup as UNKNOWN/inconclusive, not as pass.

## Verification boundary

Expected protocol only. No source/UI changes, tests/build/Editor run, screenshots, or runtime claims. This task does not authorize prompt implementation before review.
