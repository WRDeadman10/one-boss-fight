# BL-86..90: re-verification of BL batches 3-17 (slack pass)

Assigned by X-2198 (lead Codex) to C (implementer), 2026-11-12. This is lane BL, batch 18 of 20.

**Method:** 3 read-only reviewers (a workflow fan-out, inside the 3-agent cap) traced every assertion in the 44 guard-test files of batches 3-17 against their headers, the existing tests and the BL-01 audit. I then **re-checked every finding by hand against the header source before acting**. One reviewer claim was wrong (Enrage, below) and was corrected rather than applied.

**Not done:** no production source edits, and no Unreal, build, PIE, commit or push. The engine-lock acceptance build is still pending with the lead.

## Result summary

- **Wrong expected values: none found.** Every asserted value matches the source.
- **Hotfixes, tests and comments only, in 13 existing guard-test files:**

| Finding | File(s) | Fix |
|---|---|---|
| Equivalence misclassified ("discriminates" or "fair without guard" claimed, but the result is the same without the guard) | ParryFair (+Inf ActiveStart / Reaction: `IsFinite(ReactionGap)` and `gap >= Inf` already refuse), StaminaPressure (+Inf threshold: `> 1` refuses), Desperation (health 1.1: the ramp clamps to 0), ChannelDrain (`MaxHealth <= 0` is implied by `Health >= Max`; +Inf fraction is caught by `> 1`), ArenaEdge (NaN Boss/Center: `IsFinite(Distance)` refuses), Cue (+Inf max: `> 3` refuses), Combo (+Inf MinRange/Yaw/Tempo are caught by the ordering checks), PatternDetect (clamp upper bound: `Min(…,100)` caps it anyway), RecoveryWindow (Scale<0: `Seconds` refuses the negative recovery), RepeatPenalty (negative base: `Clamp` gives the 0 lower bound) | relabelled `(equivalent)` with the reason; the header comments were corrected |
| Non-discriminating clamp asserts | GuardGuard (phase ±1e300 / ±FLT_MAX give the same result unclamped) | added a **discriminating** case: `IsProofParryPulse(1.7e308, 1.7e308)` is true with the clamp, while the unclamped sum overflows to +Inf (false) |
| **Missed discriminating gaps** (untested anywhere) | Desperation `StartFraction > 1`: `(0, 1.1, 1.5)` would be 1.5 without the guard | added → 1 |
| | ArenaEdge `IsFinite(Margin)`: a +Inf margin would give `Clamp(NaN) = 1` pressure | added → empty result |
| | Cue `IsFinite(MaxSeconds)`: a NaN max would give a NaN hold | added → -1 |
| | Combo `IsFinite(MinRange)` and `IsFinite(Yaw)`: NaN passes every ordering check | added NaN MinRange and NaN Yaw → EdgeDomain |
| | StaminaPressure `IsFinite(LowThreshold)`: `(NaN-.2)/NaN` would clamp to pressure 1 | added a NaN threshold → 0 |
| Wrong reason text | YawProbe (at sample 1, `Inf·sin(π/2)` is +Inf, not NaN; the verdict was right) | comment corrected |

## Reviewer claim rejected after hand-check

The reviewers suggested NaN `RampSeconds` and `MaxSpeedScale` "pin" Enrage's `IsFinite` clauses. **That is false.** NaN already fails `RampSeconds > 0` and `MaxSpeedScale >= 1`; a +Inf ramp gives progress 0 (scale 1); and +Inf speed fails `<= 2`. Both clauses are **unobservable**. The added NaN asserts are labelled as documenting behavior.

## Documented, not changed

- **Duplicated positive controls** (harmless; each repeats an existing call only as a control):

| Guard file | Existing test |
|---|---|
| ChannelDrain `CappedHeal(30, .5, 93, 100)` | `MoveCardTests:169` |
| Feint `Chance(.15)` | `FeintRulesTests:10` |
| ComboAbort | `ComboAbortRulesTests:10` |
| Defense `CooldownOk(3)` | `DefenseTests:19` |
| BakeFreshness | `BakeFreshnessRulesTests:9` |
| Track watchdog | `Runtime:517` |
| Telegraph `TargetFor(A3a)` | `Codex:252` |
| ParryCost `StaminaAfter(10, 4, false)` | `ParryCostTests:22` |
| Swing `NeedsRefresh(13, 10, 3)` | `Automation:654` |
| DLSS | `DLSSRulesTests:22` |
| StrafeHold `HoldSeconds(19, 3)` | `StrafeTests:51-53` |
| GuardGuard pulse 0.05 | `GuardTests:25` |
| PoiseRegen 15 | `QueueE:24` |

- **Already-documented equivalents confirmed:** GapCloser negative range; StuckRecovery `MaxAttempts <= 0`; NextPosition angle overflow (unreachable).
- **Unobservable guards (no test can discriminate them), recorded:**
  - Punish `IsFinite(cone)`: NaN fails `>= 0`, and +Inf fails `< 180`.
  - Punish `IsValid`'s `IsFinite(RunSpeed / Reach)` for NaN.
  - The Enrage clauses above.

## BL-89/90: status

- All 13 edited files pass the trailing-whitespace check.
- No new files were added, so the test names are unchanged.
- **Not compiled or run:** pending the engine-lock build.
- Next: batch 19, the hypotheses pass.
