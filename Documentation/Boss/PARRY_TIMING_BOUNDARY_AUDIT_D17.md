# Parry timing boundary audit (Queue D D17, 2026-11-03)

## Source contract

`RPGParry::IsOpen` accepts the half-open interval `[OpenedAt, OpenedAt + WindowSeconds)`: the opening instant is inside; the exact close instant is out (`Player/RPGParryRules.h`). `RPGParryGrade::Grade` rejects negative offsets and offsets `>= WindowSeconds`; valid offsets are Perfect when `offset/window < 0.4`, Good when `< 0.8`, otherwise Late (`Player/RPGParryGradeRules.h`). With the current proposed `.25 s` window, these boundaries are `.10 s` and `.20 s`; they are mechanics/config defaults, not a claim that final balance is approved. The input component computes grade from game-time offset (`RPGPlayerParry.cpp:101–119`), and contact routing gives dead/stale/duplicate/dodge rejection precedence before Parried (`RPGDamageResolver` pure rules; `Tests/RPGParryTests.cpp`).

## Boundary coverage

| Edge | Expected source result | Existing coverage inspected | Gap |
|---|---|---|---|
| Before press | `IsOpen` false; grade None for negative offset. | `RPGParryTests.cpp` checks `9.99` against a `10.0` opening; `RPGParryGradeTests.cpp` checks `-0.001`. | No combined contact/result row, but both pure predicates cover the side. |
| Exact open | Window is open; offset zero is Perfect. | `RPGParryTests.cpp` checks `IsOpen(10.0)`; `RPGParryGradeTests.cpp` checks `Grade(0,.25)`. | Covered in separate rule tests, not through `URPGPlayerParry`/contact integration. |
| Exact 40% | `.10/.25` is exactly the threshold; `< .4` is false, so Good. | `RPGParryGradeTests.cpp` asserts `.1` is Good and `.099` is Perfect. | No representable adjacent-before/after threshold checks. |
| Exact 80% | `.20/.25` is exactly the threshold; `< .8` is false, so Late. | `RPGParryGradeTests.cpp` asserts `.2` is Late and `.199` is Good. | No representable adjacent-before/after threshold checks. |
| Last valid time | Any representable offset below `.25` is in-window; within final interval grade Late. | Grade test uses `.249999`; adjacent-window test checks `nextafter(close, open)` is in-window. | Stronger to use the same adjacent value for both `IsOpen` and `Grade`. |
| Exact close | `IsOpen` false and Grade None at `.25`. | `RPGParryTests.cpp`, `RPGParryAdjacentWindowBoundaryTests.cpp`, and `RPGParryGradeTests.cpp` cover exact close independently. | No combined exact-close assertion at the component/contact boundary. |
| Exact cooldown ready time | A press at `ReadyAt` succeeds; just-before is refused without changing state. | `RPGParryCooldownAdjacentBoundaryTests.cpp` covers both. | No timing-boundary gap in the pure press rule. |

`Tests/RPGParryTests.cpp` also checks Parried decision and that dodge invulnerability, duplicate, dead, and stale inputs take precedence. The existing source does not demonstrate that a pack boss uses this resolver; that separate live-evidence gap remains KI-153/D16.

## Bounded follow-up

Add adjacent representable samples around the `.4` and `.8` grade thresholds, preserving exact-equality assertions. Use `std::nextafter` toward both infinities and assert the expected neighboring grade on each side. In the existing adjacent-window test, feed the exact last-in-window representable `Now` into both `IsOpen` and `Grade`; retain exact close and cooldown checks. If an integration harness is available later, add a single contact matrix confirming the component's `GradeNow` agrees with the pure offset rule and that invalid/dead/duplicate/dodge outcomes still precede Parried. No runtime change is indicated by this audit.

## Verification boundary

Static source/test inspection only. Existing tests were read but not run; no code, test, build, or Editor changes/execution were made for D17. `git diff --check` is required on the documentation update.
