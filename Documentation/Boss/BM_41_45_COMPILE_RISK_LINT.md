# BM-41..45: pre-compile risk lint of the lane-BL and lane-BM native tests (lane BM, batch 9 of 10)

C (implementer), 2026-11-12.

New file: `Scripts/Tools/test_bl_bm_compile_risk_lint.py`. **Source-only heuristics; nothing is compiled.** It complements `test_bl_lane_static_checks.py` (from BL-99: names, guards and includes) and is **not a substitute** for the lead's engine-lock build.

## Checks (over the 51 lane native test files: 50 BL + 1 BM)

| # | Risk pattern | Why it matters | Result |
|---|---|---|---|
| 1 | `TestEqual` with a bool operand (`==`, `!=`, `.IsEmpty()`, `IsNearlyEqual`) or `uint64(...)` | `FAutomationTestBase::TestEqual` lacks or makes ambiguous these overloads; `TestTrue(a == b)` is the safe form | **0 hits** |
| 2 | string overload mismatch: `FString(...)` against a bare `TEXT("...")` | mixed `FString` / `TCHAR*` overload resolution | **0 hits** |
| 3 | `std::numeric_limits` without `#include <limits>` | it compiles only through an incidental transitive include | **0 hits** |
| 4 | an integer literal compared with a floating literal in `TestEqual` | ambiguous between the float and double overloads | **0 hits** |

**The lint is not vacuous.** A synthetic file containing each pattern (`X == 1`, `uint64(7)`, `TEXT` against `FString`, `1` against `1.0`, `numeric_limits` without the include) triggered all four detectors.

## Earlier hand fixes this lint now pins

During BL I replaced a bool `TestEqual` (Guard clamp equivalence) and a `uint64` `TestEqual` (Combo `LastGateId`) with `TestTrue(==)`. Codex's BL hotfixes kept the same forms. The lint guards against regressions of those patterns.

## Tests

`python -m unittest discover -s Scripts/Tools -p test_bl_bm_compile_risk_lint.py -v` → **`Ran 5 tests ... OK`**: the file count is at least 51, plus the 4 checks above.

## Limits (honest)

- **These are heuristics, not a C++ front end.** The lint cannot see an operand's type when it is an expression, for example a function returning `float` compared with a double literal. Mixed float and double operands resolve to the double overload by promotion, so they are low risk, but they were not proven.
- **Not checked:**
  - missing `#include`s for engine types other than `<limits>`;
  - template deduction failures on custom types;
  - deprecated APIs;
  - warnings treated as errors.
- **Only the engine-lock build can confirm compilation.** The run filter for that build is in `BL_96_100_LANE_CLOSEOUT.md` and BM-50.
