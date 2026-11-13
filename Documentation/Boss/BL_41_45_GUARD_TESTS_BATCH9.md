# BL-41..45: guard tests, batch 9 (Overlay, ParryFair, PatternDetect)

Assigned by X-2179 (lead Codex) to C (implementer), 2026-11-12. This is lane BL, batch 9 of 20. The scope follows the lead's list.

**Three new test files only.** No production source edits, and no Unreal, build, PIE, commit or push.
- **Not compiled or run:** the engine-lock acceptance build is pending with the lead.
- **Checked by hand:** every assertion was traced against the header source, and each file has positive controls.

## BL-44: re-verification (by hand)

| Header | Code (line) | Gap tested | Existing tests, not repeated |
|---|---|---|---|
| `RPGBossOverlayRules.h` | `:24` `Num` branches; `:31` parry suffix | `Digits>=2` → `%.2f`; parry data with a **closed** window → ` Parry=Closed Grade=…` | `…Runtime.BossOverlayFormat`, `…Runtime.OverlayParry` (broad integration; not restated) |
| `RPGBossParryFairRules.h` | `:15-18` guards; `:23` `IsFinite(ReactionGap)` | negative Telegraph, Window or Reaction; an overflowing gap; `+Inf` ActiveStart and Reaction | `…BossParryFair.Rules`: NaN in all 5 fields, zero or negative play rate, reversed start, the tolerance boundary; the adjacent-boundary test |
| `RPGBossPatternDetectRules.h` | `:11` invalid `RequiredRepeats` → `State=FState()`; `:12` clamp; `:13` cap (cites corrected per A-886) | Required 100 accepted with exact detection; negative or oversize count clamped; full reset on invalid Required | `…PatternDetect.Rules` |

## BL-41..43: tests

| Task | File | Automation test | Cases |
|---|---|---|---|
| BL-41 | `Source/OneBossFight/Tests/RPGBossOverlayGuardTests.cpp` | `OneBossFight.Framework.Overlay.Guards` | `Num`: control Digits 0 gives "1"; Digits 2 gives "1.23"; Digits 3 gives "1.00"; Digits 5 gives "2.50". `Format`: the baseline (no parry data) has no `Parry=` (control). With a closed window and grade Good, the line ends with ` Parry=Closed Grade=Good` and equals the baseline plus that suffix. |
| BL-42 | `.../RPGBossParryFairGuardTests.cpp` | `OneBossFight.Framework.BossParryFair.Guards` | **Control:** a 0.5 s gap is fair. A negative telegraph, window or reaction is refused; each would be **fair without its guard**. **Overflow:** a 1e308 s gap is fair at play rate 1 (control) but fails at `1e-300` because the gap becomes `+Inf`. `+Inf` ActiveStart and `+Inf` Reaction are refused. |
| BL-43 | `.../RPGBossPatternDetectGuardTests.cpp` | `OneBossFight.Framework.PatternDetect.Guards` | **Control:** Required 3 detects on the 3rd. **Required 100:** no detection in observations 1..99, detection at the 100th (count 100), and the count stays at 100 afterwards. A count of -5 clamps to 0 and is then incremented to 1, with no detection. A count of 1000 clamps to 100 and detects. Required 1 or 101 resets `LastPattern` to None and `Consecutive` to 0, a full reset. |

## BL-45: status

- **Names:** the new names are unique; the existing tests are named `.Rules`, adjacent-boundary and the runtime overlay tests.
- **Defects:** none indicated.
- **Pending:** the engine-lock build.
