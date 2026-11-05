# Selector zero-weight candidate audit (Queue D105)

**Scope:** static review of candidate initialization, score eligibility, and fallback behavior. No tests run.

`Source/OneBossFight/Player/RPGBossMoveSelector.cpp:19-24` refuses any candidate whose base weight or context multipliers are nonfinite, <=0, or above 1e6, with `Selector.Domain`. Thus authored zero-weight candidates are invalid and cannot enter selection. For valid candidates, eligible score at `:60-67` multiplies strictly positive base weight, range factor (documented code keeps it >=0.5), repeat penalty (config >0), and positive pattern multipliers; score is positive. Zero does not represent a supported “eligible but never choose” candidate.

`Source/OneBossFight/Tests/RPGBossMoveSelectorTests.cpp:46-48` includes `Cand(... Weight=0)` and expects `Selector.Domain`. The named no-candidate fallback at `:92-97` sets `ChosenIndex == INDEX_NONE` when candidates fail model eligibility; there is no zero-score eligible trace path under validated inputs. Tie-band tests exercise ranking among positive scores.

Conclusion: zero-weight candidates are rejected at initialization by contract; fallback is “no eligible candidate,” not a zero-weight fallback tier. No code change indicated. Runtime profile adaptation/wiring is outside this selector unit test.
