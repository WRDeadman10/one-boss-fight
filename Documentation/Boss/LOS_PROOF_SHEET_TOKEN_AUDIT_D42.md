# LOS proof-sheet token audit (Queue D42)

Scope: compare `LOS_MEMORY_EXPECTED_S117.md` positive, timeout, and control claims with literal emitters, validator schemas, and retained evidence. Read-only; no tests/build/Editor/run.

## Claim-to-token map

| Expected claim | Token / source | Evidence boundary |
|---|---|---|
| Injected target shift and setup | `target_shift_injected` (`RPGFrameworkBossCharacter.cpp`, non-shipping proof hook) | identifies commanded displacement, not that the pillar actually occluded the target. Must retain blocker from `los_lost` and setup identity. |
| Sight lost with last-visible position/blocker | `los_lost lastKnownX/Y blocker` (`:146`; schema `validate_framework_proof_logs.py:79`) | direct event/token evidence; coordinates are last visible sample, not hidden target location. |
| Search request to last-known point | `los_search_start x/y` (`RPGFrameworkBossCharacter.cpp:381`; schema `:80`) | proves the request only; actual boss movement remains labeled manual in S117. |
| Sight regain and search duration | `los_regained lostForSeconds` (`:147`; schema `:81`) | reports event and elapsed time; does not itself prove corridor/path reachability. |
| Resume to normal behavior | `los_resume` (`:387`; empty schema `:82`), then `walk` and `playback_start` | source requests walk-back; later walk/playback tokens evidence arrival and resumed combat. S117 explicitly retains the band and playback checks. |
| Hidden timeout | `los_search_timeout seconds` (`:148`; schema `:83`) | exactly-once rule event is unit-covered and a retained no-regain log contains the timeout. No regain/resume during the bounded hidden interval is an absence claim requiring a complete run log. |
| Visible negative control | no LOS event, ordinary decision/playback | correctly specified as an absence check; S117 says no retained inside-LOS control was found, so this remains un-witnessed. |

`Documentation/Boss/LOG_TOKENS.md:23,151-155` lists the five LOS tokens and emitter links. Validator unit samples include all five (`test_validate_framework_proof_logs.py:98-102`). S117 maps each positive event to a literal token or explicitly labels movement as manual, and separates the regain and timeout runs.

## Accuracy caveat

S117 expects `los_regained lostForSeconds=<0..3>`. Under ordinary active ticks, `LosStep` normally reports timeout once at/after the configured duration before later regain; however `TickLos` is skipped during leash, and a long frame/tick gap can also deliver a visible sample before a timeout sample. `LosStep` prioritizes visible/regain before timeout (`RPGBossTrackRules.h:58-65`), so a regain can report elapsed time greater than `SearchSeconds`. The `<0..3` range is therefore conditional on a continuously serviced LOS interval; it should not be a hard failure criterion across leash pauses or skipped ticks. No retained log reviewed here demonstrates that edge.

The sheet correctly does not treat `los_search_start` as proof of movement and does not claim a visible-control pass. No positive feature claim lacks a token/manual/UNKNOWN qualifier in the reviewed rows; the duration range needs the caveat above.
