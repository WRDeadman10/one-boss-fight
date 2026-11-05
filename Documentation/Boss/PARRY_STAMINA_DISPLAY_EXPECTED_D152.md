# Opt-in parry stamina cost display expected sheet (Queue D152)

Status: protocol only. This sheet does not implement or enable a display. Feature implementation requires review of this protocol and the default-off behavior; live Editor/packaged proof is Lead-owned.

## Claim and source boundary

The proposed readout shows the configured cost of a parry press and must not alter parry input, resource values, refunds, or combat outcomes. The source rule permits a press only for finite, nonnegative values with `Stamina >= Cost`; `RPGPlayerParry::Press` logs before/after on success and refusal, and on an accepted parry can refund half the paid cost. See `Source/OneBossFight/Player/RPGParryCostRules.h` and `RPGPlayerParry.cpp:75-100,157-178`.

Do not infer a product cost or label for the readout from this protocol. Capture the actual configured value and the displayed unit/rounding; any new threshold, placement, or presentation choice remains pending review.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw log path and SHA-256 | **Expected:** unique paired IDs, immutable raw evidence and post-capture hash. **Observed:** pending. |
| Build and map | **Expected:** exact executable/build and `/Game/OneBossFight/Levels/L_SevarogArena`. **Observed:** pending. |
| Player/input/component | **Expected:** possessed player, real parry action binding and receiving component recorded. **Observed:** pending. |
| Cost and display state | **Expected:** read back actual configured stamina cost and display toggle; prove display defaults off before enabling. **Observed:** pending. |
| Stamina state | **Expected:** record current and maximum `Attribute.Stamina` immediately before each press; define sufficient as `Before >= Cost`, insufficient as `Before < Cost`. Avoid unrelated stamina consumers. **Observed:** pending. |

## Paired cases

For each case, start from matched identity/state and repeat with the display off and on, changing only the reviewed display toggle. Capture `parry_stamina`, `parry_press`, stamina attribute reads, tag/window result, and direct screen evidence. Never edit evidence in place.

| Case | Required setup and evidence | Pass condition |
|---|---|---|
| Sufficient stamina | Finite nonnegative `Before >= Cost`; capture exact cost, before/after attribute, `opened`, tag/window, and displayed value. Repeat a no-contact press and a real accepted parry as separate subcases if both are in scope. | Display matches the actual configured cost and is visible only when the reviewed UI policy says it should be. Toggle does not change press acceptance, paid amount, or the half-cost accepted-parry refund. |
| Insufficient stamina | Finite nonnegative `Before < Cost`; record values, refusal, `opened=0`, tag/window and screen state. | Both toggle states refuse the press; stamina remains unchanged; readout does not imply a paid or accepted parry. Any shown cost must be clearly a configured cost, not a deduction. |
| Invalid or unavailable input | Where reachable without modifying gameplay, exercise unavailable attribute or invalid configured value and capture the component refusal. | Display cannot turn a refusal into an accepted press or mutate stamina. If a condition is not safely reachable, leave it untested rather than injecting runtime state. |

## Evidence interpretation and limits

- **Measured:** configured cost and resource values from source-tokenized logs/readback; text, unit, rounding, and visibility from screenshot or direct Lead observation with run/time reference.
- **Inferred:** paired equivalence only when both starts match and other resource consumers are excluded. State timing and any unavoidable confounders.
- **Manual:** legibility, placement, whether the wording communicates cost rather than a deduction, and whether it obscures combat.
- Log rows do not establish that the player saw the text. The existing debug overlay and `parry_stamina` telemetry are not a player-facing display witness.
- No exact cost, unit formatting, visual placement, hide interval, insufficient-stamina messaging, or shipping policy is approved by this sheet.

## Failure and stop conditions

Fail if the display is on by default, the value disagrees with the configured cost, any display state changes gameplay/resource results, insufficient stamina is accepted, or a refusal is presented as a successful spend. Stop if the toggle or cost cannot be read back, paired baseline cannot be reproduced, resource sources cannot be isolated, or implementation needs an unreviewed product choice. Missing evidence remains UNKNOWN; invalid setup is inconclusive.

## Verification boundary

Expected protocol only. No code/UI/test changes, tests/build/Editor execution, screenshots, or runtime claims. No implementation is authorized before review of the sheet and default-off behavior.
