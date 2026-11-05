# Opt-in boss difficulty preset expected sheet (Queue D172)

Status: protocol only. No preset values, rule deltas, or default change are authorized. Owner chooses values and Lead reviews the exact preset before implementation. Live Editor/packaged proof remains Lead-owned.

## Claim and boundary

The proposed opt-in preset applies only an explicit, bounded list of approved rule-parameter changes. Baseline values and behavior remain unchanged when the feature is off. Every enabled delta must be read back and attributed to one named rule; no undocumented side effect, content edit, or broad difficulty label is sufficient. This sheet selects no health/damage/speed/timing values and makes no claim that a difficulty preset already exists.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw logs and hashes | **Expected:** unique IDs and immutable evidence hashed after capture. **Observed:** pending. |
| Build/map/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarovArena`, profile and configuration identity. **Observed:** pending. |
| Baseline readback | **Expected:** all relevant rule inputs, defaults, selected cards, phase, target and runtime state captured with preset off. **Observed:** pending. |
| Preset identity and values | **Expected:** owner-approved name/version, every explicit value/delta, allowed range, rule target and readback with preset on. **Observed:** UNKNOWN pending decision. |
| Pair identity | **Expected:** same build/profile/seed/encounter setup; only preset setting differs. **Observed:** pending. |

## Paired cases

After the owner supplies a concrete preset, run baseline-off and preset-on from matched conditions. Verify each configured rule independently before any aggregate balance interpretation.

| Row | Required evidence | Pass condition |
|---|---|---|
| Unchanged baseline | Preset off/read-back; capture all relevant rule inputs and representative outputs. | Values and behavior match the current baseline; no hidden preset default. |
| Enabled preset readback | Enable approved preset; read back each field and compare against the approved delta table. | Every changed value matches the authorized value and stays within its approved bound; no unlisted field changes. |
| Per-rule behavior | Exercise the relevant bounded cases for each changed rule and capture its input/output plus invariant attack/terminal behavior. | Observed deltas match the approved specification; unrelated rules remain at baseline. |
| Reset/off regression | Disable or restart to baseline using the reviewed route; capture all fields again. | Preset values do not leak into default or next-generation state. |

## Evidence interpretation and limits

- **Measured:** readback of each value, rule input/output, build/profile and transition identity with raw references.
- **Inferred:** causal effect only when one approved delta is isolated or its combined interaction is explicitly tested.
- **Manual:** perceived challenge and fairness remain owner/Lead judgment; numeric rule checks do not establish product balance.
- Until owner selects values, ranges, rule scope and reset behavior, there is no valid enabled preset acceptance. A preset label alone is not evidence of its contents.

## Failure and stop conditions

Do not implement before the owner approves a complete value/delta table and bounds. Fail if defaults change, an unlisted parameter changes, readback differs, a bound is exceeded, or preset state leaks across reset. Stop if rule ownership, readback or matched setup is ambiguous. Missing evidence stays UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No difficulty value selected, source/profile changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before owner choice and review.
