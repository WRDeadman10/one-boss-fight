# BL-81..85: guard tests, batch 17 (Swing, Telegraph; Tier1Visual excluded)

Assigned by X-2196 (lead Codex) to C (implementer), 2026-11-12. This is lane BL, batch 17 of 20, the last header batch.

**Two new test files only.** No production source edits, and no Unreal, build, PIE, commit or push.
- **Not compiled or run:** the engine-lock acceptance build is pending with the lead.
- **Checked by hand:** every assertion was traced against the header source.

## BL-83: re-verification and observability (by hand)

The equivalence analysis assumes UE's `FMath::Clamp(X,Min,Max) = X<Min?Min:X<Max?X:Max`, `FMath::Min(A,B) = A<=B?A:B` and `FMath::Max(A,B) = A>=B?A:B`. All comparisons with NaN are false.

| Header / function | Gap tested | Existing coverage, not repeated | Discriminates? |
|---|---|---|---|
| `RPGSwingRules.h:16-33` `ResolveWindow` | an override with a negative or NaN start, a NaN end, End == Start, End < Start → (-1, -1) | `RPGAutomationTests.cpp:611-627`: no window, row window, override wins, override on a row without a window, row end before start | **yes**: without the guard the override values would be copied |
| `:36-40` `WindowOpen` | NaN Start, End or Position → closed | `RPGAutomationTests.cpp:630-635`, `RPGCodexTests.cpp:110-113` | **no, equivalent**: NaN makes `Start>=0`, `End>Start` or `Position>=Start` false |
| `:44-56` `StaminaExtra` | NaN Wanted, PackCost or StaminaNow → 0 | `RPGAutomationTests.cpp:641-650`, `RPGCodexTests.cpp:114-116` | **NaN Wanted or PackCost: yes** (would return NaN). **NaN stamina on a refund: yes** (would return -5). **NaN stamina with a positive extra: no, equivalent** (`Max(NaN,0)` gives 0, then `Min(20,0)` gives 0) |
| `:59-63` `NeedsRefresh` | NaN Now, AppliedAt or RefreshAfter; a negative RefreshAfter → false | `RPGAutomationTests.cpp:653-655`, `RPGCodexTests.cpp:117-119` (boundaries, zero off) | **negative RefreshAfter: yes** (`3 >= -1` would be true). **NaN cases: no, equivalent** |
| `RPGTelegraphRules.h:9-17` `RateFor` | non-finite ActiveStart, Target or Position → 1 | `RPGCodexTests.cpp:239-263` (finite boundaries, late position, negative position) | **only a +Inf Target**: `(A-P)/Inf = 0` clamps to 0.1. NaN inputs (`Clamp(NaN)` gives 1) and +Inf ActiveStart (`Target <= Inf` refuses) are **equivalent** |
| `:19-30` `TargetFor` | a NaN, +Inf or negative CVar → 0 | `RPGCodexTests.cpp:249-256` (zero CVar, caps, other moves) | **yes, all**: `Min(NaN,.35)` gives .35 for A1; A3a would return the raw value |

## BL-84: exclusion and false positives

- **`RPGTier1VisualRules.h` stays excluded.** The BL-01 audit classed it as not owner-independent: it depends on world, asset or visual data. It was struck through in the queue, and no test was written.
- **False positives:** none in this batch. Every gap was unasserted.

## BL-81..82: tests

| Task | File | Automation test | Cases |
|---|---|---|---|
| BL-81 | `Source/OneBossFight/Tests/RPGSwingGuardTests.cpp` | `OneBossFight.Player.SwingGuards` | **ResolveWindow:** a valid override is used (control); 5 invalid overrides give (-1, -1) even on a row with a window. **WindowOpen:** control open; NaN start, end or position closed (equivalent). **StaminaExtra:** NaN Wanted, NaN PackCost and NaN stamina on a refund give 0 (discriminating); NaN stamina with a positive extra gives 0 (equivalent). **NeedsRefresh:** control true; RefreshAfter -1 gives false (discriminating); NaN Now, AppliedAt or RefreshAfter gives false (equivalent). |
| BL-82 | `.../RPGTelegraphGuardTests.cpp` | `OneBossFight.Player.TelegraphGuards` | **RateFor:** control 0.425; +Inf target gives 1 (discriminating); NaN ActiveStart, +Inf ActiveStart, NaN target and NaN position give 1 (equivalent). **TargetFor:** control A3a 0.40; NaN or +Inf CVar gives 0 for A1 and A3a; -0.1 gives 0 for A3a. |

## BL-85: status

- **Names:** the new names are unique; the existing tests are `FRPGSwingRulesTest` and the Codex tests.
- **Defects:** none indicated.
- **Pending:** the engine-lock build.
- **Lane position:** batches 3-17 are done. Remaining: batch 18 (slack and re-verification), 19 (hypotheses pass) and 20 (consolidated build/run evidence and closeout).
