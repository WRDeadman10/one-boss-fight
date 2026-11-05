# Player parry stamina live proof

This proof is player-side and does not use a framework boss profile copy. The exact pack attribute name in source is `Attribute.Stamina`: current value is read with `ReadAttribute(..., false, ...)` and maximum with `ReadAttribute(..., true, ...)` (`RPGPlayerParry.cpp:74`, `:154–158`).

## Setup

Record current and maximum `Attribute.Stamina`, then test a valid parry press that does not contact an attack, a successful parry, and (when a low-stamina setup is available) an insufficient-stamina refusal. Keep other stamina consumers idle during each measurement. For the recorded run, `rpg.ParryStaminaCost 20` supplied the cost through the non-shipping hook; see `Documentation/Boss/TEST_HOOKS.md`.

## Control

Use `rpg.ParryStaminaCost 0` as the baseline control. A paid press whose parry window opens but contacts no attack is a whiff, not a refusal: its opening cost remains spent. An insufficient-stamina refusal must not spend stamina; this refusal has not yet been exercised live. Do not treat `parried=0` alone as proof of rollback.

## PASS

- A valid press with positive `StaminaCost` spends that cost immediately; insufficient stamina refuses the press without a write (`RPGPlayerParry.cpp:68–83`).
- If the player parries, half the paid cost is refunded, capped at max stamina (`RPGParryCostRules.h:22–27`). A whiff retains the opening cost; a refused press spends none.
- Live evidence (C-715; `Docs/BossCombatReview/Execution/Claude/B_PARRY_STAMINA`): with cost 20, a window opening without contact logged `before=100 after=80 parried=0`; a Perfect parry logged `before=80 after=70 parried=1` (cost 20 less half refund 10). Overlay values were `Parry=Closed Grade=None` before, `Parry=Open` at press, and `Grade=Perfect` afterwards.
- `[FrameworkProof] parry_stamina before=<x> after=<y> parried=1` records a parry; `parried=0` can record a paid whiff and does not imply refusal or rollback. Compare logged values with the pack's current `Attribute.Stamina` before/after. Validate tag cleanup separately with `parry_tag` lines.
- Insufficient-stamina refusal remains unproven live; use a low-stamina setup before claiming this branch.
- If current or max stamina reads/writes fail transiently, the pending retry stays visible in state until it succeeds or the documented retry bound is reached; report persistent API failures separately.

## FAIL

- An insufficient-stamina refusal spends stamina, a valid parry fails to refund, refund exceeds max stamina, or the log reports different values from the attribute.

## Validator

`python -I Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py <editor_raw.log>`
