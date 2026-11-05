# How to write a pure boss rule and its tests

Keep a reusable rule deterministic and independent of actors, world state, and engine services. The header is the single implementation used by production callers and automation tests. These steps and checks are based on the project's compiled pure rules and the build fixes recorded in `TEST_PLAN.md`.

## Implementation and test path

1. **Define one small contract.** State the inputs, units, valid domain, defaults, and invalid-input output in a short header comment. Prefer explicit configuration structs when several settings change together; keep state explicit in caller-owned structs.
2. **Validate before calculating.** Reject non-finite inputs and invalid ranges before division, square roots, interpolation, or state mutation. Choose one documented fallback (false, zero, or neutral multiplier) and return it consistently.
3. **Keep the rule pure and testable.** Put a small deterministic helper in a `*Rules.h` header, use `inline` where appropriate, and avoid UObjects, globals, timers, random global state, and hidden writes. If randomization is part of the behavior, accept a seed or roll as an argument.
4. **Prove the formula by hand first.** Evaluate at least one interior point and both endpoints before writing the assertion. For example, smoothstep at `t=0.5` is `0.5`; an ease-out-back curve must exceed 1 at some interior point if it is named overshoot. Clamp behavior and units should also be hand-checked.
5. **Test boundaries with declared types.** Cover valid baseline, exact boundary, immediately adjacent representable values, invalid/non-finite values, and relevant monotonicity/determinism. Use `std::nextafter` with the field's actual type; choose arithmetic whose difference is exactly representable when asserting exact equality.
6. **Test state transitions separately.** For stateful helpers, cover first event, repeated event, reset, invalid input, and cap/exhaustion. Reset the fixture before each independent case so one branch cannot contaminate another.
7. **Register and locate the test.** Add a unique automation test name under the project's `OneBossFight.Framework.*` or specific subsystem namespace. Use `EditorContext` when it touches engine services/assets; a pure inline rule can still use the established project test target. No test result is a pass until the suite actually ran.

To create an initial three-file skeleton without overwriting existing files, run `python -I Scripts/Tools/new_rule_scaffold.py --name <PascalCaseName> --requirement-id <BOSS-AREA-NNN> --slug <lowercase-topic> --output-root .`. It writes the `RPGBoss<Name>Rules.h`, matching `*RulesTests.cpp`, and a designer-reference Markdown file. The generated test is an empty registration placeholder, not evidence; replace all TODOs before treating the rule as implemented.

## Six project build lessons

| Build lesson | Concrete project evidence | Check before delivery |
|---|---|---|
| A similarly named helper may be a free function, not a member | `BUILD-159`: `IsValid` was a free function; the first build failed until the call site was corrected (`TEST_PLAN.md:585`). | Search the declaration and existing call sites before writing `Object.IsValid(...)` or `Type::IsValid(...)`. |
| Static utility APIs may not match instance-style intuition | `BUILD-149`: `FVector2D::Distance` is static; the first test compile failed and the rule/test was corrected (`TEST_PLAN.md:507`). | Read the exact signature and include the owning header. |
| Float fields need float-adjacent boundary inputs | C-707 found `TimeSeconds` is float; `nextafter(float, double)` rounded back to the same float, so the purported adjacent-value test did not perturb it. Use float infinity (`TEAM_MAILBOX.md`, C-707). | Check the declared property type; use `std::nextafter` with that type and verify the value changed. |
| Fixture setup must be repeatable across each case | `BUILD-158` fixed three F5 test fixtures whose setup lambda left profile state from a previous case (`TEST_PLAN.md:584`). | Reinitialize the full fixture before each independent validation assertion. |
| A named numeric property must be true at an interior point | `BUILD-162/163`: the first warp-curve formula never exceeded 1 despite claiming overshoot; the lead replaced it with ease-out-back (`TEST_PLAN.md:588–589`). | Substitute a hand-computable input before posting and assert the property itself, not only endpoints. |
| Match both `nextafter` operands to the stored field type | `C-709`: `FRPGBakedBladeSample::TimeSeconds` is `float`; passing a `double` negative infinity selected double precision, and assignment rounded the adjacent value back to the same float. The corrected boundary uses `std::numeric_limits<float>::infinity()` (`RPGBossBakedSampleLastEndpointBoundaryTests.cpp:43–44`; declaration `RPGBossMoveCard.h:51`). | Check the field declaration and use the matching `nextafter` overload and infinity type. Assert the stored value differs from the endpoint before relying on the boundary test. |

Also keep the queue-wide preflight in mind: inspect helper declarations before calls, use the correct automation macros/includes, avoid shadowed locals, and keep a failing first-run log for the lead to diagnose. The examples above are observed fixes, not a substitute for a fresh compile.

Source evidence: [`TEST_PLAN.md`](../TEST_PLAN.md:507), [`RPGFrameworkRuntimeTests.cpp`](../../Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp:157), [`RPGBossWarpCurveRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossWarpCurveRulesTests.cpp:6), the C-707 review in [`TEAM_MAILBOX.md`](../TEAM_MAILBOX.md), and [`RPGBossBakedSampleLastEndpointBoundaryTests.cpp`](../../Source/OneBossFight/Tests/RPGBossBakedSampleLastEndpointBoundaryTests.cpp:43).
