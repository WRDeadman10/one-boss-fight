# Aggro band transition boundary audit (Queue D96)

**Scope:** source/test comparison for the opt-in pure aggro-band stepper. Static only; no tests run. The helper's header describes it as opt-in; caller/runtime evidence is not established here.

## Source thresholds

`Source/OneBossFight/Player/RPGBossAggroRules.h:15-28` validates finite, ordered thresholds. Close enters strictly below `EnterCloseCm` (default 250) and a current Close band persists strictly below `ExitCloseCm` (300), unless kiting takes priority. Far enters strictly above `EnterFarCm` (700) and a current Far band persists strictly above `ExitFarCm` (600), unless hugging takes priority. Exact threshold equality therefore exits/does not enter that range band, subject to the other rule branches. A hugging override forces Close; kiting forces Far. Contradictory behavior flags, negative/nonfinite range or dodge rate, and invalid config preserve the supplied current band.

Dodge behavior uses `EnterDodgeRate=.6` and `ExitDodgeRate=.3`: non-Far states begin kiting at rate `>= .6`; a Far state remains kiting only when rate `> .3`, so exact `.3` exits. Dodge rate is validated nonnegative and finite. Config validation requires `EnterDodgeRate > ExitDodgeRate >= 0` and a positive window duration.

## Existing test map

`Source/OneBossFight/Tests/RPGBossAggroRulesTests.cpp:11-21` proves representative close/far entry, persistence inside exit thresholds, exit beyond/below them, behavior-driven overrides, dodge-rate entry at .6, persistence at .4, exit at .3, and no balanced-band flap at .5. It checks contradictory flags and a negative range preserve state.

## Gaps

- No tests pin exact range equality at 250/300/600/700 or adjacent representable values; current samples are 200/275/310 and 750/650/550.
- No direct assertion covers close persistence at exactly 300, far persistence at exactly 600, or behavior override precedence against those boundary states.
- Dodge tests hit exact .6 and .3 but do not check adjacent representable values or invalid/nonfinite dodge input/config/window.
- Invalid config state preservation is source-visible but not asserted. Invalid enum values for `Current` are also not explicitly handled by `IsValid`; this audit does not claim a canonical recovery policy.
- The helper is opt-in and this source/test pair does not prove any production caller is wired or that an authored range preference has runtime effect.
