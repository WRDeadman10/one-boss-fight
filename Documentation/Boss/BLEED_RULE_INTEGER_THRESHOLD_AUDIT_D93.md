# Bleed rule integer and threshold audit (Queue D93)

**Scope:** static review of `RPGBleedRules::Apply`/`ProcDamage` and the existing pure-rule tests. No source changed during the original audit; no test was run.

## Existing coverage

- `Source/OneBossFight/Tests/RPGCodexTests.cpp:87-95` checks zero-input precedence, dead-target refusal, exact 80+20 threshold equality, reset-to-zero, one threshold increase, same-frame suppression, and the health floor.
- `Source/OneBossFight/Tests/RPGAutomationTests.cpp:605-629` checks four/five-hit boundaries, the repeated threshold sequence to the configured 200 cap, and seven total procs.
- `Source/OneBossFight/Tests/RPGAutomationTests.cpp:641-645` checks one proc with surplus buildup and no carry-over.
- `Source/OneBossFight/Tests/RPGBleedRulesPropertyTests.cpp:13-31` uses a fixed seed for 10,000 amounts in [-40, 40], checks finite/nonnegative buildup and monotonic capped thresholds, and ignores NaN amount. It does not generate extreme finite values or boundary `Procs` states.

## Findings

1. **Integer upper-bound gap (source-level, unreachable under ordinary fight duration):** `RPGBleedRules.h:56` rejects negative `State.Procs` but accepts `MAX_int32`; `:68` then increments it on a proc. Signed overflow is undefined behavior. Existing tests only reach seven procs (`RPGAutomationTests.cpp:629`). The state is runtime data; this audit found no evidence it is serialized or can naturally reach that limit. Treat as a robustness gap, not a normal-play defect. A bounded test can seed `MAX_int32` and verify the chosen refusal/saturation policy before any change is made.

2. **Extreme finite buildup boundary:** `RPGBleedRules.h:64-70` adds a finite amount to finite buildup, then resets to zero when the threshold comparison succeeds. A finite `FLT_MAX` amount with positive buildup can produce positive infinity during the addition, which compares above a finite threshold and then resets. That path appears self-recovering but has no fixture; the current seeded generator only reaches magnitude 40. Add a focused assertion for result, reset state, and proc-count policy if the behavior is intended.

3. **Threshold extrema:** `:69` caps the increasing threshold with `ThresholdMax`; finite-addition overflow is therefore capped when the max is finite. The function validates a finite positive max and `ThresholdMax >= InitialThreshold`, but does not require `State.Threshold <= Config.ThresholdMax`. Thus externally supplied state above the configured cap can persist after a proc when increase is zero; normal internally-created state follows the defaults and tests verify the normal 200 cap. No test covers `FLT_MAX` threshold/config increase or mismatched state/config.

4. **One threshold crossing per call is intentional and tested:** large surplus does not carry into a second proc (`RPGAutomationTests.cpp:641-645`). Do not interpret that contract as an untested multi-proc loop.

## Acceptance follow-up

For a future pure-rule fixture, cover `MAX_int32` proc state, a large finite buildup addition, largest finite threshold/increase values, and a state threshold above the active config cap. Decide expected behavior before adding a code guard. Adapter config validation is distinct from runtime-state validation and does not by itself close these cases.

## C-757 source disposition (2026-11-03)

The Lead-directed `Procs` overflow case is now handled by saturation at `RPGBleedRules.h:68`; a pure edge assertion was added at `RPGCodexTests.cpp:98-99`. The historical audit above describes the pre-fix code. No test was run by Codex; Lead suite validation remains pending.
